import pytest

from app.scenarios import Scenario, ScenarioSimulator


def test_all_scenarios_generate_data():

    simulator = ScenarioSimulator()

    for scenario in Scenario:

        result = simulator.generate(scenario)

        assert not result.empty
        assert "timestamp" in result.columns
        assert "solar_generation" in result.columns


def test_normal_sunny_data():

    simulator = ScenarioSimulator()

    result = simulator.generate(
        Scenario.NORMAL_SUNNY
    )

    assert result["solar_generation"].max() == 4.6


def test_cloudy_weather_reduces_generation():

    simulator = ScenarioSimulator()

    normal = simulator.generate(
        Scenario.NORMAL_SUNNY
    )

    cloudy = simulator.generate(
        Scenario.CLOUDY_WEATHER
    )

    assert cloudy["solar_generation"].max() < \
           normal["solar_generation"].max()


def test_soiling_reduces_generation():

    simulator = ScenarioSimulator()

    normal = simulator.generate(
        Scenario.NORMAL_SUNNY
    )

    soiling = simulator.generate(
        Scenario.PANEL_SOILING
    )

    assert soiling["solar_generation"].max() < \
           normal["solar_generation"].max()


def test_shading_reduces_generation():

    simulator = ScenarioSimulator()

    normal = simulator.generate(
        Scenario.NORMAL_SUNNY
    )

    shading = simulator.generate(
        Scenario.PARTIAL_SHADING
    )

    assert shading["solar_generation"].max() < \
           normal["solar_generation"].max()


def test_inverter_inefficiency_reduces_generation():

    simulator = ScenarioSimulator()

    normal = simulator.generate(
        Scenario.NORMAL_SUNNY
    )

    inverter = simulator.generate(
        Scenario.INVERTER_INEFFICIENCY
    )

    assert inverter["solar_generation"].max() < \
           normal["solar_generation"].max()


def test_high_consumption_preserves_generation():

    simulator = ScenarioSimulator()

    normal = simulator.generate(
        Scenario.NORMAL_SUNNY
    )

    high_consumption = simulator.generate(
        Scenario.HIGH_ENERGY_CONSUMPTION
    )

    assert high_consumption["solar_generation"].equals(
        normal["solar_generation"]
    )

def test_scenarios_provide_additional_signals():
    simulator = ScenarioSimulator()

    result = simulator.generate(
        Scenario.NORMAL_SUNNY
    )

    assert "energy_consumption" in result.columns
    assert "weather" in result.columns
    assert "system_efficiency" in result.columns


def test_cloudy_weather_signal():
    simulator = ScenarioSimulator()

    result = simulator.generate(
        Scenario.CLOUDY_WEATHER
    )

    assert (result["weather"] == "cloudy").all()


def test_inverter_efficiency_signal():
    simulator = ScenarioSimulator()

    result = simulator.generate(
        Scenario.INVERTER_INEFFICIENCY
    )

    assert (result["system_efficiency"] == 65.0).all()


def test_high_consumption_signal():
    simulator = ScenarioSimulator()

    normal = simulator.generate(
        Scenario.NORMAL_SUNNY
    )

    high_consumption = simulator.generate(
        Scenario.HIGH_ENERGY_CONSUMPTION
    )

    assert (
        high_consumption["energy_consumption"].mean()
        > normal["energy_consumption"].mean()
    )