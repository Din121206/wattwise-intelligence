"""
Tests for WattWise scenario definitions.
"""

from app.scenarios import Scenario


def test_all_required_scenarios_exist():
    """All six SIH demonstration scenarios must exist."""

    assert len(Scenario) == 6


def test_normal_sunny_scenario():
    assert Scenario.NORMAL_SUNNY.value == "normal_sunny"


def test_cloudy_scenario():
    assert Scenario.CLOUDY_WEATHER.value == "cloudy_weather"


def test_panel_soiling_scenario():
    assert Scenario.PANEL_SOILING.value == "panel_soiling"


def test_partial_shading_scenario():
    assert Scenario.PARTIAL_SHADING.value == "partial_shading"


def test_inverter_scenario():
    assert Scenario.INVERTER_INEFFICIENCY.value == (
        "inverter_inefficiency"
    )


def test_high_consumption_scenario():
    assert Scenario.HIGH_ENERGY_CONSUMPTION.value == (
        "high_energy_consumption"
    )
    