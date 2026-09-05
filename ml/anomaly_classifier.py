from pathlib import Path

import joblib
import pandas as pd

from app.raw_models import RawIoTData


MODEL_PATH = Path("ml/models/anomaly_classifier.joblib")


class MLAnomalyClassifier:
    """Loads the trained anomaly model and predicts the operating scenario."""

    def __init__(self, model_path: Path = MODEL_PATH):
        if not model_path.exists():
            raise FileNotFoundError(
                f"Anomaly model not found: {model_path}"
            )

        package = joblib.load(model_path)

        if not isinstance(package, dict):
            raise ValueError("Invalid anomaly model package.")

        if "model" not in package:
            raise ValueError("Model package does not contain a model.")

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

    def _extract_features(self, data: RawIoTData) -> list[float]:
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

    def predict(self, data: RawIoTData) -> dict:
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
            "confidence": round(confidence, 4),
        }