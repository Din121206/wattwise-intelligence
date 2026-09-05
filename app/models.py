"""
WattWise Module 2
Shared data models.

These models define the data contract used by the
AI / Renewable Energy Intelligence module.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class InstallationData(BaseModel):
    """
    Represents the data received for one renewable-energy
    installation.

    This follows the shared Installation Data structure
    defined by the WattWise team.
    """

    # Unique installation identifier shared across modules.
    installation_id: str = Field(..., min_length=1)

    # Installation location.
    location: str = Field(..., min_length=1)

    # Solar installation capacity in kW.
    capacity: float = Field(..., gt=0)

    # Timestamp of the measurement.
    timestamp: datetime

    # Actual solar energy generated.
    solar_generation: float = Field(..., ge=0)

    # Energy consumed by the user/system.
    energy_consumption: float = Field(..., ge=0)

    # Energy imported from the electrical grid.
    grid_import: float = Field(..., ge=0)

    # Energy exported to the electrical grid.
    grid_export: float = Field(..., ge=0)

    # Weather condition.
    # Example: sunny, cloudy, rainy.
    weather: str = Field(..., min_length=1)

    # System efficiency represented as a percentage.
    # Valid range: 0 to 100.
    system_efficiency: float = Field(..., ge=0, le=100)


class IntelligenceOutput(BaseModel):
    """
    Standard output produced by Module 2.

    Module 1 can later expose these values through
    the main WattWise backend API.
    """

    # Predicted generation produced by the forecasting model.
    predicted_generation: float = Field(..., ge=0)

    # Expected generation from the Performance Digital Twin.
    expected_generation: float = Field(..., ge=0)

    # Actual generation received from the installation.
    actual_generation: float = Field(..., ge=0)

    # Percentage of generation lost compared with expected output.
    performance_loss: float = Field(..., ge=0, le=100)

    # Overall system health score from 0 to 100.
    health_score: float = Field(..., ge=0, le=100)

    # System condition.
    # Expected values: healthy, warning, critical.
    status: str

    # Whether an abnormal performance condition was detected.
    anomaly: bool

    # Possible cause of the anomaly.
    likely_cause: str | None = None

    # Recommended action for the user/maintenance team.
    recommendation: str