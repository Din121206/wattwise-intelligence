"""
WattWise Module 2
Raw IoT input models.

Represents the data received from the hardware/backend
before any calculations or AI processing.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class SolarData(BaseModel):
    voltage: float = Field(..., ge=0)
    current: float = Field(..., ge=0)


class EnvironmentData(BaseModel):
    irradiance: float = Field(..., ge=0)
    panel_temperature: float
    ambient_temperature: float


class GridData(BaseModel):
    voltage: float = Field(..., ge=0)
    current: float = Field(..., ge=0)


class LoadData(BaseModel):
    voltage: float = Field(..., ge=0)
    current: float = Field(..., ge=0)


class BatteryData(BaseModel):
    voltage: float = Field(..., ge=0)
    current: float
    temperature: float


class InverterData(BaseModel):
    voltage: float = Field(..., ge=0)
    current: float
    temperature: float
    status_code: int


class RawIoTData(BaseModel):
    installation_id: str = Field(..., min_length=1)
    timestamp: datetime

    solar: SolarData
    environment: EnvironmentData
    grid: GridData
    load: LoadData
    battery: BatteryData
    inverter: InverterData