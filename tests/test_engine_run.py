from app.scenarios import Scenario, ScenarioSimulator
from app.intelligence import IntelligenceEngine


def test_engine_run_complete_flow():

    simulator = ScenarioSimulator()
    engine = IntelligenceEngine()

    baseline = simulator.generate(
        Scenario.NORMAL_SUNNY
    )

    actual = simulator.generate(
        Scenario.PANEL_SOILING
    )

    response = engine.run(
        actual,
        capacity=5.0,
        installation_id="INST-001",
        baseline_dataframe=baseline
    )

    assert "intelligence" in response
    assert "alerts" in response

    intelligence = response["intelligence"]

    assert len(intelligence) == 9

    assert intelligence["anomaly"] is True

    assert intelligence["likely_cause"] == (
        "Possible panel soiling"
    )

    assert len(response["alerts"]) > 0

    assert response["alerts"][0]["installation_id"] == (
        "INST-001"
    )


def test_engine_run_normal_scenario():

    simulator = ScenarioSimulator()
    engine = IntelligenceEngine()

    baseline = simulator.generate(
        Scenario.NORMAL_SUNNY
    )

    actual = simulator.generate(
        Scenario.NORMAL_SUNNY
    )

    response = engine.run(
        actual,
        capacity=5.0,
        installation_id="INST-001",
        baseline_dataframe=baseline
    )

    intelligence = response["intelligence"]

    assert intelligence["health_score"] == 100
    assert intelligence["status"] == "healthy"
    assert intelligence["anomaly"] is False

    assert response["alerts"] == []