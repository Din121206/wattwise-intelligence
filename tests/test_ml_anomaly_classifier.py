from datetime import datetime, timezone

from app.raw_models import (
    RawIoTData,
    SolarData,
    EnvironmentData,
    GridData,
    LoadData,
    BatteryData,
    InverterData,
)

from ml.anomaly_classifier import MLAnomalyClassifier


def create_sample_data():
    return RawIoTData(
        installation_id="INST-001",
        timestamp=datetime.now(timezone.utc),
        solar=SolarData(
            voltage=18.5,
            current=0.95,
        ),
        environment=EnvironmentData(
            irradiance=900,
            panel_temperature=40,
            ambient_temperature=30,
        ),
        grid=GridData(
            voltage=0,
            current=0,
        ),
        load=LoadData(
            voltage=12,
            current=0.4,
        ),
        battery=BatteryData(
            voltage=13.2,
            current=0.5,
            temperature=35,
        ),
        inverter=InverterData(
            voltage=12,
            current=0.9,
            temperature=42,
            status_code=0,
        ),
    )


def test_model_loads():
    classifier = MLAnomalyClassifier()

    assert classifier.model is not None
    assert len(classifier.feature_names) == 15


def test_prediction_contains_scenario():
    classifier = MLAnomalyClassifier()

    result = classifier.predict(create_sample_data())

    assert "scenario" in result
    assert "confidence" in result


def test_prediction_scenario_is_valid():
    classifier = MLAnomalyClassifier()

    result = classifier.predict(create_sample_data())

    valid_scenarios = {
        "normal_sunny",
        "cloudy_weather",
        "panel_soiling",
        "partial_shading",
        "inverter_inefficiency",
        "high_energy_consumption",
    }

    assert result["scenario"] in valid_scenarios


def test_prediction_confidence_is_valid():
    classifier = MLAnomalyClassifier()

    result = classifier.predict(create_sample_data())

    assert 0.0 <= result["confidence"] <= 1.0