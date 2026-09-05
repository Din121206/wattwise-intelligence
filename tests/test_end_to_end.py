import pytest

from app.scenarios import Scenario, ScenarioSimulator
from app.intelligence import IntelligenceEngine


def test_all_scenarios_produce_api_output():

    simulator = ScenarioSimulator()
    engine = IntelligenceEngine()

    baseline = simulator.generate(
        Scenario.NORMAL_SUNNY
    )

    scenarios = list(Scenario)

    for scenario in scenarios:

        actual = simulator.generate(scenario)

        result = engine.analyze(
            actual,
            capacity=5.0,
            baseline_dataframe=baseline
        )

        output = engine.api_output(result)

        assert output.predicted_generation >= 0
        assert output.expected_generation >= 0
        assert output.actual_generation >= 0

        assert 0 <= output.performance_loss <= 100
        assert 0 <= output.health_score <= 100

        assert output.status in [
            "healthy",
            "warning",
            "critical"
        ]

        assert isinstance(output.anomaly, bool)

        assert output.recommendation is not None
        assert len(output.recommendation) > 0


def test_normal_sunny_scenario_is_healthy():

    simulator = ScenarioSimulator()
    engine = IntelligenceEngine()

    baseline = simulator.generate(
        Scenario.NORMAL_SUNNY
    )

    actual = simulator.generate(
        Scenario.NORMAL_SUNNY
    )

    result = engine.analyze(
        actual,
        capacity=5.0,
        baseline_dataframe=baseline
    )

    output = engine.api_output(result)

    assert output.performance_loss == 0
    assert output.health_score == 100
    assert output.status == "healthy"
    assert output.anomaly is False


def test_fault_scenario_detected():

    simulator = ScenarioSimulator()
    engine = IntelligenceEngine()

    baseline = simulator.generate(
        Scenario.NORMAL_SUNNY
    )

    actual = simulator.generate(
        Scenario.PARTIAL_SHADING
    )

    result = engine.analyze(
        actual,
        capacity=5.0,
        baseline_dataframe=baseline
    )

    output = engine.api_output(result)

    assert output.performance_loss > 0
    assert output.health_score < 100
    assert output.anomaly is True
    assert output.likely_cause is not None
    assert output.recommendation != (
        "Continue regular monitoring."
    )


def test_high_consumption_scenario():

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

def test_panel_soiling_api_output():

    simulator = ScenarioSimulator()
    engine = IntelligenceEngine()

    baseline = simulator.generate(
        Scenario.NORMAL_SUNNY
    )

    actual = simulator.generate(
        Scenario.PANEL_SOILING
    )

    result = engine.analyze(
        actual,
        capacity=5.0,
        baseline_dataframe=baseline
    )

    output = engine.api_output(result)

    assert output.anomaly is True
    assert output.likely_cause == (
        "Possible panel soiling"
    )
    assert "clean" in output.recommendation.lower()
    assert output.health_score < 100


def test_partial_shading_api_output():

    simulator = ScenarioSimulator()
    engine = IntelligenceEngine()

    baseline = simulator.generate(
        Scenario.NORMAL_SUNNY
    )

    actual = simulator.generate(
        Scenario.PARTIAL_SHADING
    )

    result = engine.analyze(
        actual,
        capacity=5.0,
        baseline_dataframe=baseline
    )

    output = engine.api_output(result)

    assert output.anomaly is True
    assert output.likely_cause == (
        "Possible partial shading"
    )
    assert "shading" in output.recommendation.lower()


def test_inverter_api_output():

    simulator = ScenarioSimulator()
    engine = IntelligenceEngine()

    baseline = simulator.generate(
        Scenario.NORMAL_SUNNY
    )

    actual = simulator.generate(
        Scenario.INVERTER_INEFFICIENCY
    )

    result = engine.analyze(
        actual,
        capacity=5.0,
        baseline_dataframe=baseline
    )

    output = engine.api_output(result)

    assert output.anomaly is True
    assert output.likely_cause == (
        "Possible inverter inefficiency"
    )
    assert "inverter" in output.recommendation.lower()


def test_high_consumption_api_output():

    simulator = ScenarioSimulator()
    engine = IntelligenceEngine()

    baseline = simulator.generate(
        Scenario.NORMAL_SUNNY
    )

    actual = simulator.generate(
        Scenario.HIGH_ENERGY_CONSUMPTION
    )

    result = engine.analyze(
        actual,
        capacity=5.0,
        baseline_dataframe=baseline
    )

    output = engine.api_output(result)

    assert "energy consumption" in (
        output.recommendation.lower()
    )

def test_complete_scenario_intelligence_and_alerts():

    simulator = ScenarioSimulator()
    engine = IntelligenceEngine()

    baseline = simulator.generate(
        Scenario.NORMAL_SUNNY
    )

    scenarios_with_expected_causes = {
        Scenario.NORMAL_SUNNY: None,
        Scenario.CLOUDY_WEATHER: "Possible cloudy weather",
        Scenario.PANEL_SOILING: "Possible panel soiling",
        Scenario.PARTIAL_SHADING: "Possible partial shading",
        Scenario.INVERTER_INEFFICIENCY: (
            "Possible inverter inefficiency"
        ),
        Scenario.HIGH_ENERGY_CONSUMPTION: None,
    }

    for scenario, expected_cause in (
        scenarios_with_expected_causes.items()
    ):

        actual = simulator.generate(scenario)

        result = engine.analyze(
            actual,
            capacity=5.0,
            baseline_dataframe=baseline
        )

        output = engine.api_output(result)

        alerts = engine.generate_alerts(
            result,
            "INST-001"
        )

        # Every scenario must produce valid intelligence
        assert output.predicted_generation >= 0
        assert output.expected_generation >= 0
        assert output.actual_generation >= 0

        assert 0 <= output.performance_loss <= 100
        assert 0 <= output.health_score <= 100

        assert output.status in [
            "healthy",
            "warning",
            "critical"
        ]

        assert isinstance(output.anomaly, bool)

        assert output.recommendation is not None
        assert len(output.recommendation) > 0

        # Fault scenarios must identify their expected cause
        if expected_cause is not None:

            assert output.anomaly is True

            assert output.likely_cause == (
                expected_cause
            )

            assert len(alerts) > 0

            assert alerts[0]["installation_id"] == (
                "INST-001"
            )

            assert alerts[0]["status"] == "active"

            assert alerts[0]["likely_cause"] == (
                expected_cause
            )

        # Normal scenario must remain healthy
        if scenario == Scenario.NORMAL_SUNNY:

            assert output.anomaly is False
            assert output.health_score == 100
            assert output.status == "healthy"
            assert alerts == []

        # High consumption must produce optimization advice
        if scenario == Scenario.HIGH_ENERGY_CONSUMPTION:

            assert "energy consumption" in (
                output.recommendation.lower()
            )