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


def test_final_output_structure():
    engine = IntelligenceEngine()

    output = engine.run_raw(
        create_raw_data(),
        capacity=0.020
    )

    assert output.energy_readings is not None
    assert output.intelligence_output is not None
    assert isinstance(
        output.hardware_anomalies,
        list
    )


def test_energy_readings_are_calculated():
    engine = IntelligenceEngine()

    output = engine.run_raw(
        create_raw_data(),
        capacity=0.020
    )

    energy = output.energy_readings

    assert energy.solar_generation == 0.018
    assert energy.energy_consumption == 0.012
    assert energy.battery_charge == 0.0064
    assert energy.battery_discharge == 0.0
    assert energy.grid_import == 0.0
    assert energy.grid_export == 0.0


def test_inverter_status_is_normal():
    engine = IntelligenceEngine()

    output = engine.run_raw(
        create_raw_data(),
        capacity=0.020
    )

    assert (
        output.energy_readings.inverter_status
        == "normal"
    )


def test_final_intelligence_values_exist():
    engine = IntelligenceEngine()

    output = engine.run_raw(
        create_raw_data(),
        capacity=0.020
    )

    intelligence = output.intelligence_output

    assert intelligence.predicted_generation >= 0
    assert intelligence.expected_generation >= 0
    assert intelligence.actual_generation >= 0
    assert 0 <= intelligence.performance_loss <= 100
    assert 0 <= intelligence.health_score <= 100
    assert isinstance(intelligence.status, str)
    assert isinstance(intelligence.anomaly, bool)
    assert isinstance(intelligence.recommendation, str)


def test_faulty_inverter_reaches_final_output():
    data = create_raw_data()

    data.inverter.status_code = 1

    engine = IntelligenceEngine()

    output = engine.run_raw(
        data,
        capacity=0.020
    )

    assert (
        output.energy_readings.inverter_status
        == "fault"
    )

    assert len(
        output.hardware_anomalies
    ) == 1

    assert (
        output.hardware_anomalies[0]["type"]
        == "inverter_fault"
    )

    assert (
        output.hardware_anomalies[0]["severity"]
        == "critical"
    )


def test_overvoltage_reaches_final_output():
    data = create_raw_data()

    data.battery.voltage = 15.2

    engine = IntelligenceEngine()

    output = engine.run_raw(
        data,
        capacity=0.020
    )

    assert len(
        output.hardware_anomalies
    ) == 1

    assert (
        output.hardware_anomalies[0]["type"]
        == "battery_overvoltage"
    )

    assert (
        output.intelligence_output.anomaly
        is True
    )


def test_shading_reaches_final_output():
    data = create_raw_data()

    engine = IntelligenceEngine()

    output = engine.run_raw(
        data,
        capacity=0.020
    )

    assert output.intelligence_output is not None
    assert output.energy_readings is not None