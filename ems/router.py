"""
FastAPI APIRouter for WattWise Energy Management System (EMS).
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from ems.models import (
    EnergyState,
    EMSDecision,
    UserConfirmation,
    SafetyResult,
    ControlCommand,
    HardwareResponse,
    ApprovalState,
    HardwareStatus
)
from ems.ems_engine import EMSEngine
from ems.safety_engine import EMSSafetyEngine
from ems.hardware_simulator import ESP32HardwareSimulator
from ems.scenarios import DEMO_SCENARIOS


router = APIRouter(
    prefix="/api/ems",
    tags=["EMS (Energy Management System)"]
)

STATIC_DIR = Path(__file__).parent / "static"


@router.get("/ui", response_class=HTMLResponse, summary="EMS Control Center UI Dashboard")
@router.get("/control-center", response_class=HTMLResponse, summary="EMS Control Center UI Dashboard")
def get_control_center_ui():
    """Serves the interactive EMS Control Center dashboard."""
    html_path = STATIC_DIR / "index.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
    raise HTTPException(status_code=404, detail="EMS Control Center UI template not found.")

# Global in-memory storage for demo state
engine = EMSEngine()
safety_engine = EMSSafetyEngine()
hardware_simulator = ESP32HardwareSimulator()

decisions_store: Dict[str, EMSDecision] = {}
states_store: Dict[str, EnergyState] = {}
safety_log: List[SafetyResult] = []
execution_history: List[HardwareResponse] = []


class ExecuteRequest(BaseModel):
    decision_id: str = Field(..., description="ID of the approved decision to execute")


class ExecuteResponse(BaseModel):
    decision: EMSDecision
    safety_result: SafetyResult
    hardware_response: Optional[HardwareResponse] = None


@router.get("/health", summary="EMS Service Health Check")
def ems_health():
    """Returns operational health status for EMS module."""
    return {
        "status": "healthy",
        "service": "EMS",
        "simulation": True
    }


@router.get("/scenarios", summary="List pre-packaged demo energy scenarios")
def get_scenarios():
    """Returns realistic pre-packaged energy states for testing the EMS decision flow."""
    return {
        "scenarios": DEMO_SCENARIOS
    }


@router.post("/scenarios/{scenario_key}/decision", response_model=EMSDecision, summary="Evaluate a pre-packaged scenario with dynamic AI engine")
@router.get("/scenarios/{scenario_key}/decision", response_model=EMSDecision, summary="Evaluate a pre-packaged scenario with dynamic AI engine")
def evaluate_scenario_decision(scenario_key: str):
    """Passes a pre-packaged demo scenario telemetry state through the REAL dynamic AI decision engine."""
    if scenario_key not in DEMO_SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_key}' not found.")
    state = DEMO_SCENARIOS[scenario_key]
    decision = engine.analyze(state)
    decisions_store[decision.decision_id] = decision
    states_store[decision.decision_id] = state
    return decision


@router.post("/decision", response_model=EMSDecision, summary="Generate EMS AI Decision")
def create_decision(state: EnergyState):
    """
    Evaluates current energy telemetry state and produces a rule-based EMS recommendation (status = PENDING).
    """
    try:
        decision = engine.analyze(state)
        decisions_store[decision.decision_id] = decision
        states_store[decision.decision_id] = state
        return decision
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"EMS engine decision failed: {exc}")


@router.post("/confirm", response_model=EMSDecision, summary="User confirmation of EMS decision")
def confirm_decision(confirmation: UserConfirmation):
    """
    Transition a decision status from PENDING to APPROVED or REJECTED based on user confirmation.
    """
    if confirmation.decision_id not in decisions_store:
        raise HTTPException(
            status_code=404,
            detail=f"Decision ID '{confirmation.decision_id}' not found."
        )

    decision = decisions_store[confirmation.decision_id]
    if confirmation.approved:
        decision.approval_status = ApprovalState.APPROVED
    else:
        decision.approval_status = ApprovalState.REJECTED

    decisions_store[decision.decision_id] = decision
    return decision


@router.post("/execute", response_model=ExecuteResponse, summary="Execute approved EMS decision")
def execute_decision(request: ExecuteRequest):
    """
    Passes an approved decision through safety validation and executes it on the ESP32 hardware simulator.
    Unapproved or unsafe commands are blocked before hitting hardware.
    """
    decision_id = request.decision_id
    if decision_id not in decisions_store:
        raise HTTPException(
            status_code=404,
            detail=f"Decision ID '{decision_id}' not found."
        )

    decision = decisions_store[decision_id]
    energy_state = states_store.get(
        decision_id,
        EnergyState(
            installation_id=decision.installation_id,
            solar_generation_kw=1.0,
            grid_import_kw=0.5,
            load_consumption_kw=1.5
        )
    )

    # 1. Perform Safety Check
    safety_result = safety_engine.validate(decision, energy_state)
    safety_log.append(safety_result)

    # 2. If Unsafe or Not Approved, Block Execution
    if not safety_result.is_safe:
        hw_blocked = HardwareResponse(
            device_name=decision.target_device,
            command_type=decision.recommended_action.value,
            status=HardwareStatus.BLOCKED,
            is_simulated=True,
            message=f"[SIMULATED HARDWARE] Command blocked by Safety Engine: {safety_result.reason}",
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        return ExecuteResponse(
            decision=decision,
            safety_result=safety_result,
            hardware_response=hw_blocked
        )

    # 3. Create Control Command payload
    command = ControlCommand(
        command_id=f"CMD-{uuid.uuid4().hex[:6].upper()}",
        decision_id=decision.decision_id,
        device_name=decision.target_device,
        command_type=decision.recommended_action,
        parameters={
            "installation_id": decision.installation_id,
            "target_device": decision.target_device,
            "confidence": decision.confidence
        }
    )

    # 4. Dispatch to Virtual ESP32 Hardware Simulator
    hw_response = hardware_simulator.execute_command(command, safety_result)
    execution_history.append(hw_response)

    return ExecuteResponse(
        decision=decision,
        safety_result=safety_result,
        hardware_response=hw_response
    )


@router.get("/status", summary="Get EMS status and execution logs")
def get_ems_status():
    """
    Returns current status overview of EMS decisions, safety evaluations, and hardware execution log.
    """
    return {
        "status": "online",
        "total_decisions": len(decisions_store),
        "pending_decisions": sum(1 for d in decisions_store.values() if d.approval_status == ApprovalState.PENDING),
        "approved_decisions": sum(1 for d in decisions_store.values() if d.approval_status == ApprovalState.APPROVED),
        "rejected_decisions": sum(1 for d in decisions_store.values() if d.approval_status == ApprovalState.REJECTED),
        "safety_evaluations": len(safety_log),
        "hardware_executions": len(execution_history),
        "recent_executions": execution_history[-5:]
    }
