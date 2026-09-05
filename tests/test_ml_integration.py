from datetime import datetime, timezone

from app.intelligence import IntelligenceEngine
from app.raw_models import (
    BatteryData,
    EnvironmentData,
    GridData,
    InverterData,
    LoadData,
    RawIoTData,
    SolarData,
)


def create_raw_data(
    solar_current: float = 1.0,
    load_current: float = 0.5,
    irradiance: float = 850.0,
) -> RawIoTData:
    return RawIoTData(
        installation_id="INST-001",
        timestamp=datetime(
            2026,
            9,
            5,
            10,
            0,
            tzinfo=timezone.utc,
        ),
        solar=SolarData(
            voltage=18.0,
            current=solar_current,
        ),
        environment=EnvironmentData(
            irradiance=irradiance,
            panel_temperature=40.0,
            ambient_temperature=30.0,
        ),
        grid=GridData(
            voltage=0.0,
            current=0.0,
        ),
        load=LoadData(
            voltage=12.0,
            current=load_current,
        ),
        battery=BatteryData(
            voltage=13.2,
            current=0.5,
            temperature=35.0,
        ),
        inverter=InverterData(
            voltage=12.0,
            current=1.0,
            temperature=40.0,
            status_code=0,
        ),
    )


def test_raw_iot_runs_complete_ml_pipeline():
    engine = IntelligenceEngine()

    raw_data = create_raw_data()

    output = engine.run_raw(
        raw_data=raw_data,
        capacity=0.020,
    )

    intelligence = output.intelligence_output

    assert intelligence is not None

    assert intelligence.predicted_generation >= 0
    assert intelligence.predicted_generation <= 0.020

    assert intelligence.expected_generation >= 0
    assert intelligence.actual_generation >= 0

    assert 0 <= intelligence.performance_loss <= 100
    assert 0 <= intelligence.health_score <= 100

    assert isinstance(intelligence.status, str)
    assert isinstance(intelligence.anomaly, bool)
    assert isinstance(intelligence.recommendation, str)


def test_ml_forecast_is_used_for_raw_iot_prediction():
    engine = IntelligenceEngine()

    raw_data = create_raw_data()

    output = engine.run_raw(
        raw_data=raw_data,
        capacity=0.020,
    )

    predicted = output.intelligence_output.predicted_generation

    assert predicted >= 0
    assert predicted <= 0.020

    # The raw IoT path must produce a forecast through the ML forecaster.
    ml_prediction = engine.ml_forecaster.predict(raw_data)

    assert predicted == ml_prediction


def test_ml_anomaly_classifier_is_used():
    engine = IntelligenceEngine()

    raw_data = create_raw_data(
        solar_current=0.45,
        load_current=0.40,
        irradiance=900.0,
    )

    ml_result = engine.ml_anomaly_classifier.predict(raw_data)

    assert "scenario" in ml_result
    assert "confidence" in ml_result

    assert isinstance(ml_result["scenario"], str)
    assert 0 <= ml_result["confidence"] <= 1


def test_complete_output_contains_energy_and_intelligence():
    engine = IntelligenceEngine()

    raw_data = create_raw_data()

    output = engine.run_raw(
        raw_data=raw_data,
        capacity=0.020,
    )

    assert output.energy_readings is not None
    assert output.intelligence_output is not None

    assert output.energy_readings.solar_generation >= 0
    assert output.energy_readings.energy_consumption >= 0

    intelligence = output.intelligence_output

    required_fields = [
        "predicted_generation",
        "expected_generation",
        "actual_generation",
        "performance_loss",
        "health_score",
        "status",
        "anomaly",
        "likely_cause",
        "recommendation",
    ]

    result = intelligence.model_dump()

    for field in required_fields:
        assert field in result