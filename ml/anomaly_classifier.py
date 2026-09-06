from pathlib import Path

import joblib
import pandas as pd

from app.raw_models import RawIoTData


MODEL_PATH = Path("ml/models/anomaly_classifier.joblib")


class MLAnomalyClassifier:
    """
    Loads the trained anomaly model and predicts the operating scenario.

    The classifier uses a hybrid approach:
    1. Strong telemetry rules handle highly obvious operating conditions.
    2. The trained ML model handles the remaining scenarios.

    This prevents a clearly high-load condition from being incorrectly
    classified as a solar-side fault such as panel soiling.
    """

    HIGH_LOAD_MIN_POWER_KW = 0.010
    HIGH_LOAD_TO_SOLAR_RATIO = 2.0

    def __init__(self, model_path: Path = MODEL_PATH):
        if not model_path.exists():
            raise FileNotFoundError(
                f"Anomaly model not found: {model_path}"
            )

        package = joblib.load(model_path)

        if not isinstance(package, dict):
            raise ValueError("Invalid anomaly model package.")

        if "model" not in package:
            raise ValueError(
                "Model package does not contain a model."
            )

        if "feature_names" not in package:
            raise ValueError(
                "Model package does not contain feature names."
            )

        if "scenario_labels" not in package:
            raise ValueError(
                "Model package does not contain scenario labels."
            )

        self.model = package["model"]
        self.feature_names = package["feature_names"]
        self.scenario_labels = package["scenario_labels"]

        self.reverse_labels = {
            value: key
            for key, value in self.scenario_labels.items()
        }

    def _extract_features(
        self,
        data: RawIoTData,
    ) -> list[float]:

        if not isinstance(data, RawIoTData):
            raise TypeError(
                "data must be a RawIoTData object."
            )

        return [
            data.solar.voltage,
            data.solar.current,
            data.environment.irradiance,
            data.environment.panel_temperature,
            data.environment.ambient_temperature,
            data.load.voltage,
            data.load.current,
            data.battery.voltage,
            data.battery.current,
            data.battery.temperature,
            data.inverter.voltage,
            data.inverter.current,
            data.inverter.temperature,
            data.inverter.status_code,
            data.timestamp.hour,
        ]

    def _detect_high_energy_consumption(
        self,
        data: RawIoTData,
    ) -> bool:
        """
        Detect an unmistakable high-energy-consumption condition.

        This is intentionally conservative.

        A condition is classified as high energy consumption when:
        - load power is at least 0.010 kW, and
        - load power is at least twice the current solar generation.

        Example:
            Solar = 18 V × 0.30 A = 0.0054 kW
            Load  = 12 V × 1.20 A = 0.0144 kW

        The load is both substantial and more than twice the available
        solar generation, so the operating condition is clearly
        high-energy consumption.
        """

        solar_power_kw = (
            data.solar.voltage
            * data.solar.current
            / 1000
        )

        load_power_kw = (
            data.load.voltage
            * data.load.current
            / 1000
        )

        if load_power_kw < self.HIGH_LOAD_MIN_POWER_KW:
            return False

        if solar_power_kw <= 0:
            return True

        return (
            load_power_kw
            >= solar_power_kw
            * self.HIGH_LOAD_TO_SOLAR_RATIO
        )

    def predict(
        self,
        data: RawIoTData,
    ) -> dict:

        if not isinstance(data, RawIoTData):
            raise TypeError(
                "data must be a RawIoTData object."
            )

        # ---------------------------------------------------------
        # 1. Strong telemetry-based classification
        # ---------------------------------------------------------
        #
        # This condition is much more reliable than asking the ML
        # model to distinguish high load from low solar generation.
        #
        if self._detect_high_energy_consumption(data):

            return {
                "scenario": "high_energy_consumption",
                "confidence": 1.0,
            }

        # ---------------------------------------------------------
        # 2. Trained ML classification
        # ---------------------------------------------------------

        features = self._extract_features(data)

        frame = pd.DataFrame(
            [features],
            columns=self.feature_names,
        )

        prediction = self.model.predict(frame)[0]

        probabilities = self.model.predict_proba(frame)[0]

        confidence = float(max(probabilities))

        scenario = self.reverse_labels[int(prediction)]

        return {
            "scenario": scenario,
            "confidence": round(
                confidence,
                4,
            ),
        }