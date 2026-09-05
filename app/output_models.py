"""
WattWise Module 2
Final API output models.
"""

from typing import Any

from pydantic import BaseModel, Field


class EnergyReadings(BaseModel):

    solar_generation: float = Field(..., ge=0)

    energy_consumption: float = Field(..., ge=0)

    grid_import: float = Field(..., ge=0)

    grid_export: float = Field(..., ge=0)

    battery_charge: float = Field(..., ge=0)

    battery_discharge: float = Field(..., ge=0)

    inverter_status: str


class IntelligenceResult(BaseModel):

    predicted_generation: float = Field(..., ge=0)

    expected_generation: float = Field(..., ge=0)

    actual_generation: float = Field(..., ge=0)

    performance_loss: float = Field(..., ge=0, le=100)

    health_score: float = Field(..., ge=0, le=100)

    status: str

    anomaly: bool

    likely_cause: str | None = None

    recommendation: str


class FinalOutput(BaseModel):

    energy_readings: EnergyReadings

    intelligence_output: IntelligenceResult

    hardware_anomalies: list[dict[str, Any]] = Field(
        default_factory=list
    )