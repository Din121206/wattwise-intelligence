from __future__ import annotations

from app.raw_models import RawIoTData
from ml.control_action_classifier import MLControlActionClassifier


class ControlRecommendationEngine:
    """Selects one safe, condition-based EMS recommendation."""

    RECOMMENDATIONS = {
        "GRID_EXPORT": "Export surplus solar power to the grid.",
        "GRID_IMPORT": "Import power from the grid to meet the current load demand.",
        "CRITICAL_LOAD_PROTECTION": "Protect critical loads by reducing non-critical loads.",
        "OPTIMIZE_LOAD": "Optimize flexible loads to better match available solar generation.",
        "LOAD_SHIFT": "Shift flexible loads to the period of higher solar generation.",
        "LOAD_REDUCE": "Reduce non-critical energy consumption to lower grid dependency.",
        "MAINTAIN": "Maintain the current system operating state.",
    }

    def __init__(self):
        self.classifier = MLControlActionClassifier()

    def _condition_action(
        self,
        data: RawIoTData,
        predicted_generation: float,
        scenario: str | None,
    ) -> str | None:
        solar_power = data.solar.voltage * data.solar.current / 1000
        load_power = data.load.voltage * data.load.current / 1000
        battery_discharge = max(
            (data.solar.current - data.load.current) * data.battery.voltage / 1000,
            0.0,
        )
        available_generation = solar_power + battery_discharge

        # Grid actions require an actually connected/available grid.
        grid_available = data.grid.voltage > 0 and data.grid.current >= 0
        if grid_available and solar_power > load_power * 1.25:
            return "GRID_EXPORT"

        if grid_available and load_power > solar_power * 1.15:
            if data.battery.voltage < 11.8 or available_generation < load_power * 0.40:
                return "CRITICAL_LOAD_PROTECTION"
            return "GRID_IMPORT"

        # Severe shortage takes priority over optimization.
        if available_generation < load_power * 0.40 or data.battery.voltage < 11.8:
            return "CRITICAL_LOAD_PROTECTION"

        # High consumption is handled by reduction or shifting.
        if scenario == "high_energy_consumption" or load_power > solar_power * 1.15:
            if predicted_generation > solar_power * 1.25:
                return "LOAD_SHIFT"
            return "LOAD_REDUCE"

        # If solar is available and the load can be better matched without
        # a major shortage, optimize flexible loads.
        if solar_power > 0 and load_power <= solar_power * 1.05 and load_power > solar_power * 0.40:
            return "OPTIMIZE_LOAD"

        return "MAINTAIN"

    def recommend(
        self,
        data: RawIoTData,
        predicted_generation: float,
        scenario: str | None,
        hardware_anomalies: list[dict] | None = None,
    ) -> dict:
        # Hardware/safety findings remain separate from EMS control actions.
        if hardware_anomalies:
            return {
                "control_action": None,
                "recommendation": None,
                "confidence": 0.0,
            }

        allowed_action = self._condition_action(
            data,
            predicted_generation,
            scenario,
        )

        if allowed_action is None:
            return {
                "control_action": None,
                "recommendation": None,
                "confidence": 0.0,
            }

        # Use the trained classifier as a second decision signal, but never
        # allow it to override the telemetry condition gate.
        prediction = self.classifier.predict(data, predicted_generation)
        if prediction["control_action"] == allowed_action:
            action = prediction["control_action"]
            confidence = prediction["confidence"]
        else:
            action = allowed_action
            confidence = 1.0

        return {
            "control_action": action,
            "recommendation": self.RECOMMENDATIONS[action],
            "confidence": confidence,
        }
