from app.raw_models import RawIoTData
from recommendations.control_engine import ControlRecommendationEngine


def raw(**overrides):
    data = RawIoTData(
        installation_id="INST-001",
        timestamp="2026-09-05T12:00:00Z",
        solar={"voltage": 18.0, "current": 0.8},
        environment={"irradiance": 850, "panel_temperature": 40, "ambient_temperature": 30},
        grid={"voltage": 0, "current": 0},
        load={"voltage": 12, "current": 0.4},
        battery={"voltage": 13.2, "current": 0.2, "temperature": 35},
        inverter={"voltage": 12, "current": 0.8, "temperature": 42, "status_code": 0},
    )
    for group, values in overrides.items():
        for key, value in values.items():
            setattr(getattr(data, group), key, value)
    return data


def rec(data, predicted=0.014, scenario=None):
    return ControlRecommendationEngine().recommend(data, predicted, scenario)


def test_grid_export():
    result = rec(raw(grid={"voltage": 230, "current": 2}, load={"current": 0.25}), scenario="normal_sunny")
    assert result["control_action"] == "GRID_EXPORT"
    assert result["recommendation"] == "Export surplus solar power to the grid."


def test_grid_import():
    result = rec(raw(grid={"voltage": 230, "current": 5}, solar={"current": 0.3}, load={"current": 1.0}), scenario="cloudy_weather")
    assert result["control_action"] == "GRID_IMPORT"
    assert result["recommendation"] == "Import power from the grid to meet the current load demand."


def test_critical_load_protection():
    result = rec(raw(solar={"current": 0.15}, load={"current": 1.2}, battery={"voltage": 11.5}), scenario="high_energy_consumption")
    assert result["control_action"] == "CRITICAL_LOAD_PROTECTION"


def test_optimize_load():
    result = rec(raw(solar={"current": 0.8}, load={"current": 0.5}), scenario="normal_sunny")
    assert result["control_action"] == "OPTIMIZE_LOAD"


def test_load_shift():
    result = rec(raw(solar={"current": 0.35}, load={"current": 0.65}), predicted=0.018, scenario="high_energy_consumption")
    assert result["control_action"] == "LOAD_SHIFT"


def test_load_reduce():
    result = rec(raw(solar={"current": 0.75}, load={"current": 1.1}), predicted=0.009, scenario="high_energy_consumption")
    assert result["control_action"] == "LOAD_REDUCE"


def test_maintain():
    result = rec(raw(solar={"current": 0.8}, load={"current": 0.2}), scenario="normal_sunny")
    assert result["control_action"] == "MAINTAIN"
    assert result["recommendation"] == "Maintain the current system operating state."


def test_hardware_anomaly_does_not_become_ems_action():
    result = ControlRecommendationEngine().recommend(
        raw(), 0.014, "normal_sunny", hardware_anomalies=[{"severity": "critical"}]
    )
    assert result["control_action"] is None
    assert result["recommendation"] is None
