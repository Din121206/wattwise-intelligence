import pytest
from pydantic import ValidationError

from app.raw_models import RawIoTData


VALID_DATA = {
    "installation_id": "INST-001",
    "timestamp": "2026-09-04T08:45:00Z",
    "solar": {
        "voltage": 231.4,
        "current": 18.1
    },
    "environment": {
        "irradiance": 742,
        "panel_temperature": 46.8,
        "ambient_temperature": 31.2
    },
    "grid": {
        "voltage": 230.8,
        "current": 8.4
    },
    "load": {
        "voltage": 230.5,
        "current": 13.9
    },
    "battery": {
        "voltage": 51.6,
        "current": 4.7,
        "temperature": 34.2
    },
    "inverter": {
        "voltage": 231.1,
        "current": 17.9,
        "temperature": 52.3,
        "status_code": 0
    }
}


def test_valid_raw_iot_data():
    data = RawIoTData(**VALID_DATA)

    assert data.installation_id == "INST-001"
    assert data.solar.voltage == 231.4
    assert data.solar.current == 18.1
    assert data.environment.irradiance == 742


def test_nested_fields_are_accessible():
    data = RawIoTData(**VALID_DATA)

    assert data.battery.voltage == 51.6
    assert data.battery.current == 4.7
    assert data.inverter.status_code == 0


def test_negative_solar_voltage_is_rejected():
    invalid_data = VALID_DATA.copy()
    invalid_data["solar"] = {
        "voltage": -231.4,
        "current": 18.1
    }

    with pytest.raises(ValidationError):
        RawIoTData(**invalid_data)


def test_missing_installation_id_is_rejected():
    invalid_data = VALID_DATA.copy()
    invalid_data.pop("installation_id")

    with pytest.raises(ValidationError):
        RawIoTData(**invalid_data)