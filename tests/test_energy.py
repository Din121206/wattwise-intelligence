from app.raw_models import RawIoTData
from app.energy import EnergyCalculator


def create_data(solar_current=18.1, load_current=13.9):
    return RawIoTData(
        installation_id="INST-001",
        timestamp="2026-09-04T08:45:00Z",
        solar={
            "voltage": 231.4,
            "current": solar_current
        },
        environment={
            "irradiance": 742,
            "panel_temperature": 46.8,
            "ambient_temperature": 31.2
        },
        grid={
            "voltage": 230.8,
            "current": 8.4
        },
        load={
            "voltage": 230.5,
            "current": load_current
        },
        battery={
            "voltage": 51.6,
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


def test_solar_generation():
    calculator = EnergyCalculator()
    data = create_data()

    assert calculator.solar_generation(data) == 4.1883


def test_energy_consumption():
    calculator = EnergyCalculator()
    data = create_data()

    assert calculator.energy_consumption(data) == 3.204


def test_battery_charge():
    calculator = EnergyCalculator()
    data = create_data()

    assert calculator.battery_charge(data) == 0.2167
    assert calculator.battery_discharge(data) == 0.0


def test_battery_discharge():
    calculator = EnergyCalculator()
    data = create_data(
        solar_current=10.0,
        load_current=15.0
    )

    assert calculator.battery_charge(data) == 0.0
    assert calculator.battery_discharge(data) == 0.258


def test_grid_values_are_zero_for_off_grid_prototype():
    calculator = EnergyCalculator()
    data = create_data()

    result = calculator.calculate(data)

    assert result["grid_import"] == 0.0
    assert result["grid_export"] == 0.0


def test_calculate_returns_required_fields():
    calculator = EnergyCalculator()
    data = create_data()

    result = calculator.calculate(data)

    expected_fields = {
        "solar_generation",
        "energy_consumption",
        "grid_import",
        "grid_export",
        "battery_charge",
        "battery_discharge",
    }

    assert set(result.keys()) == expected_fields