"""
WattWise Module 2
Hardware safety anomaly detection.
"""

from app.raw_models import RawIoTData


class HardwareAnomalyDetector:

    MIN_SOLAR_RATIO = 0.50

    BATTERY_OVERVOLTAGE = 14.8
    BATTERY_DEEP_DISCHARGE = 11.5

    PANEL_TEMPERATURE_WARNING = 45.0
    PANEL_TEMPERATURE_CRITICAL = 60.0

    BATTERY_TEMPERATURE_WARNING = 45.0
    BATTERY_TEMPERATURE_CRITICAL = 60.0

    def battery_status(self, voltage: float) -> str:
        if voltage < self.BATTERY_DEEP_DISCHARGE:
            return "critical"

        if voltage > self.BATTERY_OVERVOLTAGE:
            return "critical"

        if 12.2 <= voltage <= 14.4:
            return "healthy"

        return "warning"

    def inverter_status(self, status_code: int) -> str:
        if status_code == 0:
            return "normal"

        return "fault"

    def detect(
        self,
        data: RawIoTData,
        expected_generation: float,
        actual_generation: float
    ) -> list[dict]:

        if not isinstance(data, RawIoTData):
            raise TypeError(
                "data must be a RawIoTData object."
            )

        if expected_generation < 0:
            raise ValueError(
                "Expected generation cannot be negative."
            )

        if actual_generation < 0:
            raise ValueError(
                "Actual generation cannot be negative."
            )

        anomalies = []

        if (
            expected_generation > 0
            and actual_generation
            < expected_generation * self.MIN_SOLAR_RATIO
        ):
            anomalies.append({
                "type": "solar_performance",
                "severity": "warning",
                "status": "active",
                "likely_cause": "Panel shaded or dirty",
                "recommendation":
                    "Inspect and clean the solar panels."
            })

        if data.battery.voltage > self.BATTERY_OVERVOLTAGE:
            anomalies.append({
                "type": "battery_overvoltage",
                "severity": "critical",
                "status": "active",
                "likely_cause": "Battery overvoltage",
                "recommendation":
                    "Turn off the solar charging relay and inspect the battery system."
            })

        if data.battery.voltage < self.BATTERY_DEEP_DISCHARGE:
            anomalies.append({
                "type": "battery_deep_discharge",
                "severity": "critical",
                "status": "active",
                "likely_cause": "Battery deep discharge",
                "recommendation":
                    "Turn off the load relay and inspect or recharge the battery."
            })

        if (
            data.environment.panel_temperature
            >= self.PANEL_TEMPERATURE_WARNING
            and data.environment.panel_temperature
            <= self.PANEL_TEMPERATURE_CRITICAL
        ):
            anomalies.append({
                "type": "panel_temperature",
                "severity": "warning",
                "status": "active",
                "likely_cause": "High panel temperature",
                "recommendation":
                    "Monitor panel temperature and ensure adequate ventilation."
            })

        if (
            data.environment.panel_temperature
            > self.PANEL_TEMPERATURE_CRITICAL
        ):
            anomalies.append({
                "type": "panel_temperature",
                "severity": "critical",
                "status": "active",
                "likely_cause": "Critical panel temperature",
                "recommendation":
                    "Reduce solar load and inspect the panel cooling conditions."
            })

        if (
            data.battery.temperature
            >= self.BATTERY_TEMPERATURE_WARNING
            and data.battery.temperature
            <= self.BATTERY_TEMPERATURE_CRITICAL
        ):
            anomalies.append({
                "type": "battery_temperature",
                "severity": "warning",
                "status": "active",
                "likely_cause": "High battery temperature",
                "recommendation":
                    "Monitor battery temperature and ensure adequate cooling."
            })

        if (
            data.battery.temperature
            > self.BATTERY_TEMPERATURE_CRITICAL
        ):
            anomalies.append({
                "type": "battery_temperature",
                "severity": "critical",
                "status": "active",
                "likely_cause": "Critical battery temperature",
                "recommendation":
                    "Stop battery operation and inspect the battery cooling system."
            })

        if data.inverter.status_code != 0:
            anomalies.append({
                "type": "inverter_fault",
                "severity": "critical",
                "status": "active",
                "likely_cause": "Inverter fault",
                "recommendation":
                    "Inspect the inverter and verify its electrical connections."
            })

        return anomalies