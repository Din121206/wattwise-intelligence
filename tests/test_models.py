"""
Tests for WattWise Module 2 shared data models.
"""

from datetime import datetime

import pytest

from app.models import InstallationData, IntelligenceOutput


def test_valid_installation_data():
    """
    Verify that valid installation data is accepted.
    """

    installation = InstallationData(
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

    assert installation.installation_id == "INS-001"
    assert installation.capacity == 5.0
    assert installation.solar_generation == 4.2


def test_valid_intelligence_output():
    """
    Verify that a valid intelligence result is accepted.
    """

    result = IntelligenceOutput(
        predicted_generation=4.8,
        expected_generation=4.8,
        actual_generation=4.2,
        performance_loss=12.5,
        health_score=87.5,
        status="healthy",
        anomaly=False,
        likely_cause=None,
        recommendation="Continue regular monitoring.",
    )

    assert result.health_score == 87.5
    assert result.anomaly is False


def test_negative_generation_is_rejected():
    """
    Generation cannot be negative.
    """

    with pytest.raises(ValueError):
        InstallationData(
            installation_id="INS-001",
            location="Chennai",
            capacity=5.0,
            timestamp=datetime(2026, 9, 1, 12, 0),
            solar_generation=-1.0,
            energy_consumption=3.0,
            grid_import=0.0,
            grid_export=0.0,
            weather="sunny",
            system_efficiency=85.0,
        )


def test_zero_capacity_is_rejected():
    """
    A renewable installation must have positive capacity.
    """

    with pytest.raises(ValueError):
        InstallationData(
            installation_id="INS-001",
            location="Chennai",
            capacity=0,
            timestamp=datetime(2026, 9, 1, 12, 0),
            solar_generation=1.0,
            energy_consumption=2.0,
            grid_import=1.0,
            grid_export=0.0,
            weather="sunny",
            system_efficiency=85.0,
        )


def test_invalid_efficiency_is_rejected():
    """
    Efficiency cannot exceed 100%.
    """

    with pytest.raises(ValueError):
        InstallationData(
            installation_id="INS-001",
            location="Chennai",
            capacity=5.0,
            timestamp=datetime(2026, 9, 1, 12, 0),
            solar_generation=4.0,
            energy_consumption=3.0,
            grid_import=0.0,
            grid_export=1.0,
            weather="sunny",
            system_efficiency=105.0,
        )