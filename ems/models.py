"""
EMS Data Models & Contracts for WattWise AI Platform.
"""

from enum import Enum
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ApprovalState(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class EMSAction(str, Enum):
    BATTERY_CHARGE = "BATTERY_CHARGE"
    BATTERY_DISCHARGE = "BATTERY_DISCHARGE"
    GRID_EXPORT = "GRID_EXPORT"
    GRID_IMPORT = "GRID_IMPORT"
    CRITICAL_LOAD_PROTECTION = "CRITICAL_LOAD_PROTECTION"
    OPTIMIZE_LOAD = "OPTIMIZE_LOAD"
    LOAD_SHIFT = "LOAD_SHIFT"
    LOAD_REDUCE = "LOAD_REDUCE"
    MAINTAIN = "MAINTAIN"



class HardwareStatus(str, Enum):
    EXECUTED = "EXECUTED"
    BLOCKED = "BLOCKED"
    ERROR = "ERROR"


class EnergyState(BaseModel):
    installation_id: str = Field(..., json_schema_extra={"example": "INST-001"})

    solar_generation_kw: float = Field(..., ge=0.0, description="Current solar output in kW")
    battery_soc: float = Field(..., ge=0.0, le=100.0, description="Battery state of charge percentage")
    grid_import_kw: float = Field(..., ge=0.0, description="Current power imported from grid in kW")
    load_consumption_kw: float = Field(..., ge=0.0, description="Total building load consumption in kW")
    critical_load_kw: float = Field(default=0.2, ge=0.0, description="Essential load requirement in kW")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO formatted UTC timestamp"
    )


class EMSDecision(BaseModel):
    decision_id: str = Field(..., description="Unique decision ID e.g. DEC-1001")
    installation_id: str = Field(..., description="Target installation ID")
    recommended_action: EMSAction = Field(..., description="Recommended control action")
    target_device: str = Field(..., description="Target device (e.g. Battery Inverter, HVAC Load Controller)")
    reason: str = Field(..., description="Detailed explanation of the rule-based recommendation")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence rating between 0.0 and 1.0")
    approval_status: ApprovalState = Field(default=ApprovalState.PENDING, description="User confirmation state")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class UserConfirmation(BaseModel):
    decision_id: str = Field(..., description="ID of decision to confirm or reject")
    approved: bool = Field(..., description="True to approve, False to reject")
    user_notes: Optional[str] = Field(default=None, description="Optional user comments")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class SafetyResult(BaseModel):
    decision_id: str = Field(..., description="Target decision ID")
    is_safe: bool = Field(..., description="Whether command passed all safety constraints")
    reason: str = Field(..., description="Safety evaluation summary")
    violations: List[str] = Field(default_factory=list, description="List of safety rule violations if any")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class ControlCommand(BaseModel):
    command_id: str = Field(..., description="Unique command ID")
    decision_id: str = Field(..., description="Origin decision ID")
    device_name: str = Field(..., description="Device targeted for actuation")
    command_type: EMSAction = Field(..., description="Command type")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Command payload parameters")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class HardwareResponse(BaseModel):
    device_name: str = Field(..., description="Name of executed device")
    command_type: str = Field(..., description="Executed command action")
    status: HardwareStatus = Field(..., description="Execution status")
    is_simulated: bool = Field(default=True, description="Always True for ESP32 hardware simulator")
    message: str = Field(..., description="Hardware output log or message")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
