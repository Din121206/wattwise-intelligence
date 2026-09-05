from app.scenarios import Scenario, ScenarioSimulator
from app.intelligence import IntelligenceEngine


def test_fault_scenario_generates_alert():

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

    alerts = engine.generate_alerts(
        result,
        "INST-001"
    )

    assert len(alerts) > 0

    alert = alerts[0]

    assert alert["installation_id"] == "INST-001"
    assert alert["status"] == "active"
    assert alert["likely_cause"] == (
        "Possible panel soiling"
    )


def test_healthy_scenario_generates_no_alert():

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

    alerts = engine.generate_alerts(
        result,
        "INST-001"
    )

    assert alerts == []