from app.intelligence import IntelligenceEngine
from app.raw_models import RawIoTData


def create_raw_data():
    return RawIoTData(
        installation_id="INST-001",
        timestamp="2026-09-04T08:45:00Z",
        solar={
            "voltage": 231.4,
            "current": 18.1
        },
        environment={
            "irradiance": 742,
            "panel_temperature": 46.8,
            "ambient_temperature": 31.2
        },
        grid={
            "voltage": 0,
            "current": 0
        },
        load={
            "voltage": 230.5,
            "current": 13.9
        },
        battery={
            "voltage": 12.8,
            "current": 4.7,
            "temperature": 34.2
        },
        inverter={
            "voltage": 231.1,
            "current": 17.9,
            "temperature": 52.3,
            "status_code": 0
        }
    )


def test_raw_iot_pipeline_runs():
    engine = IntelligenceEngine()

    output = engine.run_raw(
        create_raw_data(),
        capacity=0.020
    )

    assert output is not None


def test_installation_id_is_processed():
    engine = IntelligenceEngine()

    result = engine.analyze_raw(
        create_raw_data(),
        capacity=0.020
    )

    assert result.iloc[0]["installation_id"] == "INST-001"


def test_solar_generation_is_calculated():
    engine = IntelligenceEngine()

    result = engine.analyze_raw(
        create_raw_data(),
        capacity=0.020
    )

    expected = round(231.4 * 18.1 / 1000, 4)

    assert result.iloc[0]["solar_generation"] == expected


def test_energy_consumption_is_calculated():
    engine = IntelligenceEngine()

    result = engine.analyze_raw(
        create_raw_data(),
        capacity=0.020
    )

    expected = round(230.5 * 13.9 / 1000, 4)

    assert result.iloc[0]["energy_consumption"] == expected


def test_expected_generation_is_calculated():
    engine = IntelligenceEngine()

    result = engine.analyze_raw(
        create_raw_data(),
        capacity=0.020
    )

    expected = result.iloc[0]["expected_generation"]

    assert expected > 0


def test_actual_generation_matches_solar_generation():
    engine = IntelligenceEngine()

    result = engine.analyze_raw(
        create_raw_data(),
        capacity=0.020
    )

    assert (
        result.iloc[0]["actual_generation"]
        == result.iloc[0]["solar_generation"]
    )


def test_performance_loss_is_valid():
    engine = IntelligenceEngine()

    result = engine.analyze_raw(
        create_raw_data(),
        capacity=0.020
    )

    loss = result.iloc[0]["performance_loss"]

    assert 0 <= loss <= 100


def test_health_score_is_valid():
    engine = IntelligenceEngine()

    result = engine.analyze_raw(
        create_raw_data(),
        capacity=0.020
    )

    health = result.iloc[0]["health_score"]

    assert 0 <= health <= 100


def test_inverter_status_is_normal():
    engine = IntelligenceEngine()

    result = engine.analyze_raw(
        create_raw_data(),
        capacity=0.020
    )

    assert result.iloc[0]["inverter_status"] == "normal"


def test_hardware_anomalies_are_list():
    engine = IntelligenceEngine()

    output = engine.run_raw(
        create_raw_data(),
        capacity=0.020
    )

    assert isinstance(
        output.hardware_anomalies,
        list
    )


def test_final_output_contains_intelligence():
    engine = IntelligenceEngine()

    output = engine.run_raw(
        create_raw_data(),
        capacity=0.020
    )

    intelligence = output.intelligence_output

    assert intelligence.predicted_generation >= 0
    assert intelligence.expected_generation >= 0
    assert intelligence.actual_generation >= 0


def test_final_output_contains_energy_readings():
    engine = IntelligenceEngine()

    output = engine.run_raw(
        create_raw_data(),
        capacity=0.020
    )

    energy = output.energy_readings

    assert energy.solar_generation > 0
    assert energy.energy_consumption > 0


def test_final_output_can_be_serialized():
    engine = IntelligenceEngine()

    output = engine.run_raw(
        create_raw_data(),
        capacity=0.020
    )

    data = output.model_dump()

    assert isinstance(data, dict)
    assert "energy_readings" in data
    assert "intelligence_output" in data
    assert "hardware_anomalies" in data       

def test_battery_overvoltage_reaches_final_output():
    engine = IntelligenceEngine()

    data = create_raw_data()

    data.battery.voltage = 15.0

    output = engine.run_raw(
        data,
        capacity=0.020
    )

    assert output.intelligence_output.anomaly is True

    assert output.intelligence_output.status == "critical"

    assert (
        output.intelligence_output.likely_cause
        == "Battery overvoltage"
    )

    assert (
        "solar charging relay"
        in output.intelligence_output.recommendation
    )

    assert len(output.hardware_anomalies) >= 1

    assert any(
        anomaly["type"] == "battery_overvoltage"
        for anomaly in output.hardware_anomalies
    )     

def test_nonzero_inverter_status_becomes_fault():
    data = create_raw_data()
    data.inverter.status_code = 1

    engine = IntelligenceEngine()

    result = engine.analyze_raw(
        data,
        capacity=0.020
    )

    assert result.iloc[0]["inverter_status"] == "fault"