"""
Comprehensive Unit & Integration Test Suite for WattWise EMS Module (No Battery Dependencies).
"""

from fastapi.testclient import TestClient
from app.main import app

from ems.models import (
    EnergyState,
    EMSDecision,
    UserConfirmation,
    ApprovalState,
    EMSAction,
    HardwareStatus,
    ControlCommand
)
from ems.ems_engine import EMSEngine
from ems.safety_engine import EMSSafetyEngine
from ems.hardware_simulator import ESP32HardwareSimulator
from ems.scenarios import DEMO_SCENARIOS


client = TestClient(app)


# ---------------------------------------------------------------------------
# 1. Dynamic AI Decision Engine Tests
# ---------------------------------------------------------------------------

def test_case1_critical_load_protection():
    engine = EMSEngine()
    state = DEMO_SCENARIOS["critical_load_protection"]
    decision = engine.analyze(state)

    assert decision.recommended_action == EMSAction.CRITICAL_LOAD_PROTECTION
    assert decision.approval_status == ApprovalState.PENDING
    assert decision.confidence == 0.96
    assert "critical load" in decision.reason.lower()


def test_case2_excess_solar_exports_to_grid():
    engine = EMSEngine()
    state = DEMO_SCENARIOS["excess_solar"]
    decision = engine.analyze(state)

    assert decision.recommended_action == EMSAction.GRID_EXPORT
    assert decision.approval_status == ApprovalState.PENDING
    assert 0.0 <= decision.confidence <= 1.0
    assert "8.50 kW" in decision.reason
    assert "4.00 kW" in decision.reason


def test_case3_grid_import_required():
    engine = EMSEngine()
    state = DEMO_SCENARIOS["grid_import_required"]
    decision = engine.analyze(state)

    assert decision.recommended_action == EMSAction.GRID_IMPORT
    assert decision.approval_status == ApprovalState.PENDING
    assert 0.0 <= decision.confidence <= 1.0
    assert "5.00 kW" in decision.reason


def test_case4_load_reduction():
    engine = EMSEngine()
    state = DEMO_SCENARIOS["load_reduction"]
    decision = engine.analyze(state)

    assert decision.recommended_action == EMSAction.LOAD_REDUCE
    assert decision.approval_status == ApprovalState.PENDING
    assert decision.confidence == 0.88


def test_case5_normal_operation_optimizes_load():
    engine = EMSEngine()
    state = DEMO_SCENARIOS["normal_operation"]
    decision = engine.analyze(state)

    assert decision.recommended_action == EMSAction.OPTIMIZE_LOAD
    assert decision.approval_status == ApprovalState.PENDING
    assert decision.confidence == 0.85


# ---------------------------------------------------------------------------
# 2. Safety Engine & Hardware Simulator Tests
# ---------------------------------------------------------------------------

def test_safety_engine_blocks_unapproved_decision():
    safety_engine = EMSSafetyEngine()
    state = DEMO_SCENARIOS["excess_solar"]

    unapproved_decision = EMSDecision(
        decision_id="DEC-TEST-01",
        installation_id=state.installation_id,
        recommended_action=EMSAction.GRID_EXPORT,
        target_device="Grid Tie Inverter",
        reason="Test unapproved decision",
        confidence=0.9,
        approval_status=ApprovalState.PENDING
    )

    safety_result = safety_engine.validate(unapproved_decision, state)

    assert not safety_result.is_safe
    assert len(safety_result.violations) > 0
    assert "approval check failed" in safety_result.violations[0].lower()


def test_hardware_simulator_executes_approved_safe_command():
    simulator = ESP32HardwareSimulator(device_id="ESP32-TEST")
    state = DEMO_SCENARIOS["excess_solar"]
    safety_engine = EMSSafetyEngine()

    approved_decision = EMSDecision(
        decision_id="DEC-TEST-03",
        installation_id=state.installation_id,
        recommended_action=EMSAction.GRID_EXPORT,
        target_device="Grid Tie Inverter",
        reason="Test grid export",
        confidence=0.95,
        approval_status=ApprovalState.APPROVED
    )

    safety_result = safety_engine.validate(approved_decision, state)
    assert safety_result.is_safe

    command = ControlCommand(
        command_id="CMD-TEST-01",
        decision_id=approved_decision.decision_id,
        device_name=approved_decision.target_device,
        command_type=approved_decision.recommended_action
    )

    response = simulator.execute_command(command, safety_result)

    assert response.status == HardwareStatus.EXECUTED
    assert response.is_simulated is True
    assert "ESP32-TEST" in response.message


def test_hardware_simulator_blocks_rejected_user_decision():
    simulator = ESP32HardwareSimulator(device_id="ESP32-TEST")
    state = DEMO_SCENARIOS["excess_solar"]
    safety_engine = EMSSafetyEngine()

    rejected_decision = EMSDecision(
        decision_id="DEC-TEST-04",
        installation_id=state.installation_id,
        recommended_action=EMSAction.GRID_EXPORT,
        target_device="Grid Tie Inverter",
        reason="Test export rejected",
        confidence=0.95,
        approval_status=ApprovalState.REJECTED
    )

    safety_result = safety_engine.validate(rejected_decision, state)
    assert not safety_result.is_safe

    command = ControlCommand(
        command_id="CMD-TEST-02",
        decision_id=rejected_decision.decision_id,
        device_name=rejected_decision.target_device,
        command_type=rejected_decision.recommended_action
    )

    response = simulator.execute_command(command, safety_result)

    assert response.status == HardwareStatus.BLOCKED
    assert response.is_simulated is True
    assert "Safety check failed" in response.message


# ---------------------------------------------------------------------------
# 3. Dynamic API Verification Tests
# ---------------------------------------------------------------------------

def test_api_health_endpoint():
    res = client.get("/api/ems/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "EMS"
    assert data["simulation"] is True


def test_api_dynamic_decision_different_inputs():
    # Request A: High solar, low load -> GRID_EXPORT
    req_a = {
        "installation_id": "INST-001",
        "solar_generation_kw": 8.5,
        "grid_import_kw": 1.2,
        "load_consumption_kw": 4.0,
        "critical_load_kw": 0.5
    }
    res_a = client.post("/api/ems/decision", json=req_a)
    assert res_a.status_code == 200
    data_a = res_a.json()
    assert data_a["recommended_action"] == "GRID_EXPORT"

    # Request B: Low solar, high load -> GRID_IMPORT
    req_b = {
        "installation_id": "INST-001",
        "solar_generation_kw": 2.0,
        "grid_import_kw": 5.0,
        "load_consumption_kw": 8.0,
        "critical_load_kw": 2.0
    }
    res_b = client.post("/api/ems/decision", json=req_b)
    assert res_b.status_code == 200
    data_b = res_b.json()
    assert data_b["recommended_action"] == "GRID_IMPORT"

    # Verify recommendations are DIFFERENT based on dynamic inputs
    assert data_a["recommended_action"] != data_b["recommended_action"]


def test_api_full_flow_approval_safety_execution():
    # 1. Create Decision
    req = {
        "installation_id": "INST-001",
        "solar_generation_kw": 8.5,
        "grid_import_kw": 1.2,
        "load_consumption_kw": 4.0,
        "critical_load_kw": 0.5
    }
    res_dec = client.post("/api/ems/decision", json=req)
    assert res_dec.status_code == 200
    dec = res_dec.json()
    dec_id = dec["decision_id"]
    assert dec["approval_status"] == "PENDING"

    # 2. Confirm Approval (APPROVE)
    res_conf = client.post("/api/ems/confirm", json={"decision_id": dec_id, "approved": True})
    assert res_conf.status_code == 200
    assert res_conf.json()["approval_status"] == "APPROVED"

    # 3. Execute approved & safe decision -> EXECUTED
    res_exec_approved = client.post("/api/ems/execute", json={"decision_id": dec_id})
    assert res_exec_approved.status_code == 200
    data_approved = res_exec_approved.json()
    assert data_approved["safety_result"]["is_safe"] is True
    assert data_approved["hardware_response"]["status"] == "EXECUTED"


def test_api_full_flow_rejection_blocked():
    # 1. Create Decision
    req = {
        "installation_id": "INST-002",
        "solar_generation_kw": 8.5,
        "grid_import_kw": 1.2,
        "load_consumption_kw": 4.0,
        "critical_load_kw": 0.5
    }
    res_dec = client.post("/api/ems/decision", json=req)
    dec_id = res_dec.json()["decision_id"]

    # 2. User Rejects Decision
    res_conf = client.post("/api/ems/confirm", json={"decision_id": dec_id, "approved": False})
    assert res_conf.status_code == 200
    assert res_conf.json()["approval_status"] == "REJECTED"

    # 3. Execute rejected decision -> BLOCKED
    res_exec = client.post("/api/ems/execute", json={"decision_id": dec_id})
    assert res_exec.status_code == 200
    data_exec = res_exec.json()
    assert data_exec["safety_result"]["is_safe"] is False
    assert data_exec["hardware_response"]["status"] == "BLOCKED"


def test_ems_ui_endpoint():
    res = client.get("/ems")
    assert res.status_code == 200
    assert "WattWise EMS" in res.text
