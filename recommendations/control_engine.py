from __future__ import annotations

from app.raw_models import RawIoTData


class ControlRecommendationEngine:
    """
    Generates an operating recommendation after performance/anomaly analysis.

    The AI module ends after producing the recommendation.
    It does not send control commands to hardware.
    """

    RECOMMENDATIONS = {
        "GRID_EXPORT": "Export surplus solar power to the grid.",
        "GRID_IMPORT": "Import power from the grid to meet the current load demand.",
        "CRITICAL_LOAD_PROTECTION": "Reduce non-critical loads to protect the battery.",
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

    def _calculate_powers(self, data: RawIoTData) -> tuple[float, float]:
        solar_power = data.solar.voltage * data.solar.current / 1000
        load_power = data.load.voltage * data.load.current / 1000

        return solar_power, load_power

    def recommend(
        self,
        data: RawIoTData,
        predicted_generation: float,
        scenario: str | None = None,
        hardware_anomalies: list[dict] | None = None,
    ) -> dict:

        solar_power, load_power = self._calculate_powers(data)

        # Hardware anomalies are handled by the safety/backend layer.
        if hardware_anomalies:
            return {
                "control_action": None,
                "recommendation": None,
                "confidence": 0.0,
            }

        # Maintenance-related anomalies should receive their
        # maintenance recommendation from the anomaly pipeline.
        if scenario in self.MAINTENANCE_SCENARIOS:
            return {
                "control_action": None,
                "recommendation": None,
                "confidence": 0.0,
            }

        # Battery warning / protection condition.
        if data.battery.voltage < 11.8:
            return {
                "control_action": "CRITICAL_LOAD_PROTECTION",
                "recommendation": self.RECOMMENDATIONS[
                    "CRITICAL_LOAD_PROTECTION"
                ],
                "confidence": 1.0,
            }

        # High consumption scenario.
        if scenario == "high_energy_consumption":

            if predicted_generation > solar_power * 1.25:
                return {
                    "control_action": "LOAD_SHIFT",
                    "recommendation": self.RECOMMENDATIONS["LOAD_SHIFT"],
                    "confidence": 1.0,
                }

            return {
                "control_action": "LOAD_REDUCE",
                "recommendation": self.RECOMMENDATIONS["LOAD_REDUCE"],
                "confidence": 1.0,
            }

        # Load is significantly higher than solar generation.
        if load_power > solar_power * 1.15:

            grid_available = (
                data.grid.voltage > 0
                and data.grid.current >= 0
            )

            if grid_available:
                return {
                    "control_action": "GRID_IMPORT",
                    "recommendation": self.RECOMMENDATIONS["GRID_IMPORT"],
                    "confidence": 1.0,
                }

            if predicted_generation > solar_power * 1.25:
                return {
                    "control_action": "LOAD_SHIFT",
                    "recommendation": self.RECOMMENDATIONS["LOAD_SHIFT"],
                    "confidence": 1.0,
                }

            return {
                "control_action": "LOAD_REDUCE",
                "recommendation": self.RECOMMENDATIONS["LOAD_REDUCE"],
                "confidence": 1.0,
            }

        # Grid export:
        # Only recommend export when the grid is actually available.
        if (
            data.grid.voltage > 0
            and data.grid.current >= 0
            and solar_power > load_power * 1.25
        ):
            return {
                "control_action": "GRID_EXPORT",
                "recommendation": self.RECOMMENDATIONS["GRID_EXPORT"],
                "confidence": 1.0,
            }

        # Normal sunny operation with a moderate amount of
        # available solar surplus.
        #
        # This preserves the existing OPTIMIZE_LOAD behaviour.
        if (
            scenario == "normal_sunny"
            and solar_power > 0
            and load_power <= solar_power * 1.05
            and load_power > solar_power * 0.40
        ):
            return {
                "control_action": "OPTIMIZE_LOAD",
                "recommendation": self.RECOMMENDATIONS["OPTIMIZE_LOAD"],
                "confidence": 1.0,
            }

        # Normal operation with very low load and no grid connection.
        return {
            "control_action": "MAINTAIN",
            "recommendation": self.RECOMMENDATIONS["MAINTAIN"],
            "confidence": 1.0,
        }