"""
Tests for the WattWise AI processing pipeline.
"""

from datetime import datetime

import pytest

from app.models import InstallationData
from app.pipeline import IntelligencePipeline


def create_test_data() -> InstallationData:
    """Create a valid installation record for testing."""

    return InstallationData(
        installation_id="INS-001",
        location="Chennai",
        capacity=5.0,
        timestamp=datetime(2026, 9, 1, 12, 0),
        solar_generation=4.2,
        energy_consumption=3.1,
        grid_import=0.0,
        grid_export=1.1,
        weather="sunny",
        system_efficiency=85.0,
    )


def test_pipeline_accepts_valid_data():
    """Valid installation data should pass validation."""

    pipeline = IntelligencePipeline()

    data = create_test_data()

    assert pipeline.validate_input(data) is True


def test_pipeline_preprocesses_data():
    """Valid data should become a one-row DataFrame."""

    pipeline = IntelligencePipeline()

    result = pipeline.process(create_test_data())

    assert len(result) == 1
    assert result.iloc[0]["installation_id"] == "INS-001"
    assert result.iloc[0]["location"] == "Chennai"


def test_pipeline_preserves_generation():
    """Solar generation must not change during preprocessing."""

    pipeline = IntelligencePipeline()

    result = pipeline.process(create_test_data())

    assert result.iloc[0]["solar_generation"] == 4.2


def test_pipeline_rejects_wrong_input_type():
    """The pipeline should reject non-InstallationData input."""

    pipeline = IntelligencePipeline()

    with pytest.raises(TypeError):
        pipeline.process({"installation_id": "INS-001"})


def test_pipeline_handles_timestamp():
    """Timestamp should be converted to a datetime."""

    pipeline = IntelligencePipeline()

    result = pipeline.process(create_test_data())

    assert str(result["timestamp"].dtype).startswith("datetime64")