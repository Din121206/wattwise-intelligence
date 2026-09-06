from pathlib import Path

import joblib
import pandas as pd

from app.raw_models import RawIoTData

MODEL_PATH = Path("ml/models/control_action_classifier.joblib")

CONTROL_ACTIONS = {
    "GRID_EXPORT": 0,
    "GRID_IMPORT": 1,
    "CRITICAL_LOAD_PROTECTION": 2,
    "OPTIMIZE_LOAD": 3,
    "LOAD_SHIFT": 4,
    "LOAD_REDUCE": 5,
    "MAINTAIN": 6,
}

FEATURE_NAMES = [
    "solar_voltage", "solar_current", "irradiance",
    "panel_temperature", "ambient_temperature",
    "grid_voltage", "grid_current", "load_voltage", "load_current",
    "battery_voltage", "battery_current", "battery_temperature",
    "inverter_voltage", "inverter_current", "inverter_temperature",
    "inverter_status_code", "hour", "predicted_generation",
]

class MLControlActionClassifier:
    def __init__(self, model_path: Path = MODEL_PATH):
        if not model_path.exists():
            raise FileNotFoundError(f"Control action model not found: {model_path}")
        package = joblib.load(model_path)
        if not isinstance(package, dict):
            raise ValueError("Invalid control action model package.")
        for key in ("model", "feature_names", "control_actions"):
            if key not in package:
                raise ValueError(f"Model package does not contain {key}.")
        self.model = package["model"]
        self.feature_names = package["feature_names"]
        self.control_actions = package["control_actions"]
        self.reverse_labels = {v: k for k, v in self.control_actions.items()}

    def _extract_features(self, data: RawIoTData, predicted_generation: float) -> list[float]:
        if not isinstance(data, RawIoTData):
            raise TypeError("data must be a RawIoTData object.")
        return [
            data.solar.voltage, data.solar.current,
            data.environment.irradiance, data.environment.panel_temperature,
            data.environment.ambient_temperature, data.grid.voltage, data.grid.current,
            data.load.voltage, data.load.current, data.battery.voltage,
            data.battery.current, data.battery.temperature, data.inverter.voltage,
            data.inverter.current, data.inverter.temperature, data.inverter.status_code,
            data.timestamp.hour, predicted_generation,
        ]

    def predict(self, data: RawIoTData, predicted_generation: float) -> dict:
        features = self._extract_features(data, predicted_generation)
        frame = pd.DataFrame([features], columns=self.feature_names)
        prediction = int(self.model.predict(frame)[0])
        probabilities = self.model.predict_proba(frame)[0]
        return {
            "control_action": self.reverse_labels[prediction],
            "confidence": round(float(max(probabilities)), 4),
        }
