import pytest

from app.raw_models import (
    RawIoTData,
    SolarData,
    EnvironmentData,
    GridData,
    LoadData,
    BatteryData,
    InverterData,
)
from anomaly.hardware_detector import HardwareAnomalyDetector


def create_data(
    battery_voltage=13.0,
    panel_temperature=30.0,
    battery_temperature=30.0,
    inverter_status=0,
):
    return RawIoTData(
        installation_id="INST-001",
        timestamp="2026-09-04T08:45:00Z",
        solar=SolarData(
            voltage=12.0,
            current=1.5,
        ),
        environment=EnvironmentData(
            irradiance=742,
            panel_temperature=panel_temperature,
            ambient_temperature=31.2,
        ),
        grid=GridData(
            voltage=0.0,
            current=0.0,
        ),
        load=LoadData(
            voltage=12.0,
            current=1.0,
        ),
        battery=BatteryData(
            voltage=battery_voltage,
            current=1.0,
            temperature=battery_temperature,
        ),
        inverter=InverterData(
            voltage=12.0,
            current=1.5,
            temperature=40.0,
            status_code=inverter_status,
        ),
    )


def test_normal_condition_has_no_anomaly():
    detector = HardwareAnomalyDetector()
    data = create_data()

    result = detector.detect(
        data,
        expected_generation=0.018,
        actual_generation=0.018,
    )

    assert result == []


def test_solar_performance_anomaly():
    detector = HardwareAnomalyDetector()
    data = create_data()

    result = detector.detect(
        data,
        expected_generation=0.020,
        actual_generation=0.009,
    )

    assert len(result) == 1
    assert result[0]["type"] == "solar_performance"
    assert result[0]["severity"] == "warning"
    assert result[0]["likely_cause"] == "Panel shaded or dirty"


def test_battery_overvoltage():
    detector = HardwareAnomalyDetector()
    data = create_data(battery_voltage=15.0)

    result = detector.detect(
        data,
        expected_generation=0.018,
        actual_generation=0.018,
    )

    assert any(
        anomaly["type"] == "battery_overvoltage"
        for anomaly in result
    )


def test_battery_deep_discharge():
    detector = HardwareAnomalyDetector()
    data = create_data(battery_voltage=11.0)

    result = detector.detect(
        data,
        expected_generation=0.018,
        actual_generation=0.018,
    )

    assert any(
        anomaly["type"] == "battery_deep_discharge"
        for anomaly in result
    )


def test_high_panel_temperature():
    detector = HardwareAnomalyDetector()
    data = create_data(panel_temperature=50.0)

    result = detector.detect(
        data,
        expected_generation=0.018,
        actual_generation=0.018,
    )

    assert any(
        anomaly["type"] == "panel_temperature"
        and anomaly["severity"] == "warning"
        for anomaly in result
    )


def test_critical_panel_temperature():
    detector = HardwareAnomalyDetector()
    data = create_data(panel_temperature=65.0)

    result = detector.detect(
        data,
        expected_generation=0.018,
        actual_generation=0.018,
    )

    assert any(
        anomaly["type"] == "panel_temperature"
        and anomaly["severity"] == "critical"
        for anomaly in result
    )


def test_high_battery_temperature():
    detector = HardwareAnomalyDetector()
    data = create_data(battery_temperature=50.0)

    result = detector.detect(
        data,
        expected_generation=0.018,
        actual_generation=0.018,
    )

    assert any(
        anomaly["type"] == "battery_temperature"
        and anomaly["severity"] == "warning"
        for anomaly in result
    )


def test_critical_battery_temperature():
    detector = HardwareAnomalyDetector()
    data = create_data(battery_temperature=65.0)

    result = detector.detect(
        data,
        expected_generation=0.018,
        actual_generation=0.018,
    )

    assert any(
        anomaly["type"] == "battery_temperature"
        and anomaly["severity"] == "critical"
        for anomaly in result
    )


def test_inverter_fault():
    detector = HardwareAnomalyDetector()
    data = create_data(inverter_status=1)

    result = detector.detect(
        data,
        expected_generation=0.018,
        actual_generation=0.018,
    )

    assert any(
        anomaly["type"] == "inverter_fault"
        and anomaly["severity"] == "critical"
        for anomaly in result
    )


def test_invalid_input_type():
    detector = HardwareAnomalyDetector()

    with pytest.raises(TypeError):
        detector.detect(
            "invalid",
            expected_generation=0.018,
            actual_generation=0.018,
        )


def test_negative_expected_generation():
    detector = HardwareAnomalyDetector()
    data = create_data()

    with pytest.raises(ValueError):
        detector.detect(
            data,
            expected_generation=-1,
            actual_generation=0.018,
        )


def test_negative_actual_generation():
    detector = HardwareAnomalyDetector()
    data = create_data()

    with pytest.raises(ValueError):
        detector.detect(
            data,
            expected_generation=0.018,
            actual_generation=-1,
        )


def test_battery_status():
    detector = HardwareAnomalyDetector()

    assert detector.battery_status(13.0) == "healthy"
    assert detector.battery_status(12.0) == "warning"
    assert detector.battery_status(11.0) == "critical"
    assert detector.battery_status(15.0) == "critical"


def test_inverter_status():
    detector = HardwareAnomalyDetector()

    assert detector.inverter_status(0) == "normal"
    assert detector.inverter_status(1) == "fault"