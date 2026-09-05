from app.intelligence import IntelligenceEngine
from app.raw_models import (
    RawIoTData,
    SolarData,
    EnvironmentData,
    GridData,
    LoadData,
    BatteryData,
    InverterData,
)


def create_raw_data():
    return RawIoTData(
        installation_id="INST-001",
        timestamp="2026-09-04T08:45:00Z",
        solar=SolarData(
            voltage=12.0,
            current=1.5
        ),
        environment=EnvironmentData(
            irradiance=742,
            panel_temperature=40.0,
            ambient_temperature=31.2
        ),
        grid=GridData(
            voltage=0,
            current=0
        ),
        load=LoadData(
            voltage=12.0,
            current=1.0
        ),
        battery=BatteryData(
            voltage=12.8,
            current=0.5,
            temperature=34.2
        ),
        inverter=InverterData(
            voltage=12.0,
            current=1.4,
            temperature=40.0,
            status_code=0
        ),
    )


def test_raw_output_contains_required_sections():
    engine = IntelligenceEngine()

    output = engine.run_raw(
        create_raw_data(),
        capacity=0.020
    )

    data = output.model_dump()

    assert "energy_readings" in data
    assert "intelligence_output" in data
    assert "hardware_anomalies" in data


def test_energy_output_matches_contract():
    engine = IntelligenceEngine()

    output = engine.run_raw(
        create_raw_data(),
        capacity=0.020
    )

    energy = output.energy_readings

    assert energy.solar_generation == 0.018
    assert energy.energy_consumption == 0.012
    assert energy.grid_import == 0.0
    assert energy.grid_export == 0.0
    assert energy.battery_charge == 0.0064
    assert energy.battery_discharge == 0.0
    assert energy.inverter_status == "normal"


def test_intelligence_output_matches_contract():
    engine = IntelligenceEngine()

    output = engine.run_raw(
        create_raw_data(),
        capacity=0.020
    )

    intelligence = output.intelligence_output

    assert intelligence.predicted_generation >= 0
    assert intelligence.expected_generation >= 0
    assert intelligence.actual_generation == 0.018
    assert 0 <= intelligence.performance_loss <= 100
    assert 0 <= intelligence.health_score <= 100
    assert isinstance(intelligence.status, str)
    assert isinstance(intelligence.anomaly, bool)
    assert isinstance(intelligence.recommendation, str)


def test_normal_system_has_no_hardware_anomalies():
    engine = IntelligenceEngine()

    output = engine.run_raw(
        create_raw_data(),
        capacity=0.020
    )

    assert output.hardware_anomalies == []


def test_inverter_fault_appears_in_api_output():
    data = create_raw_data()
    data.inverter.status_code = 1

    engine = IntelligenceEngine()

    output = engine.run_raw(
        data,
        capacity=0.020
    )

    assert output.energy_readings.inverter_status == "fault"

    assert len(output.hardware_anomalies) == 1

    anomaly = output.hardware_anomalies[0]

    assert anomaly["type"] == "inverter_fault"
    assert anomaly["severity"] == "critical"
    assert anomaly["status"] == "active"


def test_battery_overvoltage_appears_in_api_output():
    data = create_raw_data()
    data.battery.voltage = 15.2

    engine = IntelligenceEngine()

    output = engine.run_raw(
        data,
        capacity=0.020
    )

    assert len(output.hardware_anomalies) == 1

    anomaly = output.hardware_anomalies[0]

    assert anomaly["type"] == "battery_overvoltage"
    assert anomaly["severity"] == "critical"


def test_output_can_be_serialized_to_json():
    engine = IntelligenceEngine()

    output = engine.run_raw(
        create_raw_data(),
        capacity=0.020
    )

    json_data = output.model_dump_json()

    assert isinstance(json_data, str)
    assert "energy_readings" in json_data
    assert "intelligence_output" in json_data
    assert "solar_generation" in json_data