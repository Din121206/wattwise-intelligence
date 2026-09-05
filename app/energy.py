"""
WattWise Module 2
Energy and power calculations from raw IoT data.
"""

from app.raw_models import RawIoTData


class EnergyCalculator:

    def solar_generation(self, data: RawIoTData) -> float:
        """Solar power in kW."""
        return round(
            data.solar.voltage * data.solar.current / 1000,
            4
        )

    def energy_consumption(self, data: RawIoTData) -> float:
        """Load power in kW."""
        return round(
            data.load.voltage * data.load.current / 1000,
            4
        )

    def battery_charge(self, data: RawIoTData) -> float:
        """
        Battery charging power in kW.

        Uses the hardware team's current-source formula.
        """
        net_current = data.solar.current - data.load.current

        if net_current > 0:
            return round(
                net_current * data.battery.voltage / 1000,
                4
            )

        return 0.0

    def battery_discharge(self, data: RawIoTData) -> float:
        """
        Battery discharging power in kW.

        Uses the hardware team's current-flow concept.
        """
        net_current = data.solar.current - data.load.current

        if net_current < 0:
            return round(
                abs(net_current) * data.battery.voltage / 1000,
                4
            )

        return 0.0

    def calculate(self, data: RawIoTData) -> dict:
        """Calculate all derived energy values."""

        return {
            "solar_generation": self.solar_generation(data),
            "energy_consumption": self.energy_consumption(data),

            # Current prototype is off-grid.
            "grid_import": 0.0,
            "grid_export": 0.0,

            "battery_charge": self.battery_charge(data),
            "battery_discharge": self.battery_discharge(data),
        }