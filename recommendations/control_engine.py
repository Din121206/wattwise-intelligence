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

    MAINTENANCE_SCENARIOS = {
        "panel_soiling",
        "partial_shading",
        "inverter_inefficiency",
    }

    def __init__(self):
        self.classifier = MLControlActionClassifier()

    def _condition_action(
        self,
        data: RawIoTData,
        predicted_generation: float,
        scenario: str | None,
    ) -> str | None:

        if scenario in self.MAINTENANCE_SCENARIOS:
            return None

        solar_power = (
            data.solar.voltage * data.solar.current / 1000
        )

        load_power = (
            data.load.voltage * data.load.current / 1000
        )

        grid_available = (
            data.grid.voltage > 0
            and data.grid.current >= 0
        )

        if data.battery.voltage < 11.8:
            return "CRITICAL_LOAD_PROTECTION"

        if scenario == "high_energy_consumption":
            if predicted_generation > solar_power * 1.25:
                return "LOAD_SHIFT"
            return "LOAD_REDUCE"

        if load_power > solar_power * 1.15:
            if grid_available:
                return "GRID_IMPORT"

            if predicted_generation > solar_power * 1.25:
                return "LOAD_SHIFT"

            return "LOAD_REDUCE"

        if (
            grid_available
            and solar_power > load_power * 1.25
        ):
            return "GRID_EXPORT"

        # Explicit normal_sunny scenario:
        # retain the existing OPTIMIZE_LOAD behaviour used by
        # the control recommendation tests.
        if (
            scenario == "normal_sunny"
            and solar_power > 0
            and load_power <= solar_power * 1.05
            and load_power > solar_power * 0.40
        ):
            return "OPTIMIZE_LOAD"

        # When no ML scenario is confidently available, avoid
        # unnecessarily issuing an EMS optimization command.
        return "MAINTAIN"

    def recommend(
        self,
        data: RawIoTData,
        predicted_generation: float,
        scenario: str | None,
        hardware_anomalies: list[dict] | None = None,
    ) -> dict:

        if hardware_anomalies:
            return {
                "control_action": None,
                "recommendation": None,
                "confidence": 0.0,
            }

        allowed_action = self._condition_action(
            data=data,
            predicted_generation=predicted_generation,
            scenario=scenario,
        )

        if allowed_action is None:
            return {
                "control_action": None,
                "recommendation": None,
                "confidence": 0.0,
            }

        prediction = self.classifier.predict(
            data,
            predicted_generation,
        )

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