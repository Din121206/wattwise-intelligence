import pandas as pd

from app.intelligence import IntelligenceEngine


def create_data(
    solar_generation,
    predicted_generation,
    expected_generation,
    energy_consumption
):
    return pd.DataFrame([{
        "timestamp": "2026-09-04 12:00:00",
        "solar_generation": solar_generation,
        "predicted_generation": predicted_generation,
        "expected_generation": expected_generation,
        "actual_generation": solar_generation,
        "energy_consumption": energy_consumption,
        "grid_import": 0.0,
        "grid_export": 0.0,
        "battery_charge": 0.0,
        "battery_discharge": 0.0,
        "weather": "sunny",
        "system_efficiency": 100.0
    }])


def test_normal_sunny():
    engine = IntelligenceEngine()

    data = create_data(
        solar_generation=4.8,
        predicted_generation=4.8,
        expected_generation=4.8,
        energy_consumption=2.0
    )

    result = engine.analyze(
        data,
        capacity=5.0
    )

    row = result.iloc[0]

    assert row["performance_loss"] == 0
    assert row["health_score"] == 100
    assert bool(row["anomaly"]) is False


def test_cloudy_weather():
    engine = IntelligenceEngine()

    data = create_data(
        solar_generation=2.5,
        predicted_generation=4.8,
        expected_generation=3.0,
        energy_consumption=2.0
    )

    result = engine.analyze(
        data,
        capacity=5.0
    )

    row = result.iloc[0]

    assert row["actual_generation"] == 2.5
    assert row["expected_generation"] == 3.0
    assert row["performance_loss"] > 0


def test_panel_soiling():
    engine = IntelligenceEngine()

    data = create_data(
        solar_generation=2.0,
        predicted_generation=5.0,
        expected_generation=5.0,
        energy_consumption=2.0
    )

    result = engine.analyze(
        data,
        capacity=5.0
    )

    row = result.iloc[0]

    assert row["performance_loss"] == 60.0
    assert bool(row["anomaly"]) is True


def test_partial_shading():
    engine = IntelligenceEngine()

    data = create_data(
        solar_generation=2.4,
        predicted_generation=4.8,
        expected_generation=4.8,
        energy_consumption=2.0
    )

    result = engine.analyze(
        data,
        capacity=5.0
    )

    row = result.iloc[0]

    assert row["performance_loss"] == 50.0
    assert bool(row["anomaly"]) is True


def test_inverter_inefficiency():
    engine = IntelligenceEngine()

    data = create_data(
        solar_generation=3.2,
        predicted_generation=4.8,
        expected_generation=4.8,
        energy_consumption=2.0
    )

    result = engine.analyze(
        data,
        capacity=5.0
    )

    row = result.iloc[0]

    assert row["performance_loss"] > 0
    assert bool(row["anomaly"]) is True


def test_high_energy_consumption():
    engine = IntelligenceEngine()

    data = create_data(
        solar_generation=4.5,
        predicted_generation=4.8,
        expected_generation=4.8,
        energy_consumption=5.5
    )

    result = engine.analyze(
        data,
        capacity=5.0
    )

    row = result.iloc[0]

    assert row["energy_consumption"] == 5.5
    assert row["actual_generation"] == 4.5