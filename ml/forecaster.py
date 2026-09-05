from pathlib import Path

import joblib
import pandas as pd

from app.raw_models import RawIoTData


MODEL_PATH = Path("ml/models/solar_forecaster.joblib")


class MLSolarForecaster:
    """Loads the trained ML model and predicts next-hour solar generation."""

    def __init__(self, model_path: Path = MODEL_PATH):
        if not model_path.exists():
            raise FileNotFoundError(
                f"Solar forecasting model not found: {model_path}"
            )

        package = joblib.load(model_path)

        if not isinstance(package, dict):
            raise ValueError("Invalid solar forecasting model package.")

        if "model" not in package:
            raise ValueError("Model package does not contain a model.")

        if "feature_names" not in package:
            raise ValueError("Model package does not contain feature names.")

        self.model = package["model"]
        self.feature_names = package["feature_names"]

    def _extract_features(self, data: RawIoTData) -> dict:
        if not isinstance(data, RawIoTData):
            raise TypeError("data must be a RawIoTData object.")

        return {
            "solar_voltage": data.solar.voltage,
            "solar_current": data.solar.current,
            "irradiance": data.environment.irradiance,
            "panel_temperature": data.environment.panel_temperature,
            "ambient_temperature": data.environment.ambient_temperature,
            "load_voltage": data.load.voltage,
            "load_current": data.load.current,
            "battery_voltage": data.battery.voltage,
            "battery_current": data.battery.current,
            "battery_temperature": data.battery.temperature,
            "inverter_voltage": data.inverter.voltage,
            "inverter_current": data.inverter.current,
            "inverter_temperature": data.inverter.temperature,
            "inverter_status_code": data.inverter.status_code,
            "hour": data.timestamp.hour,
        }

    def predict(self, data: RawIoTData) -> float:
        features = self._extract_features(data)

        frame = pd.DataFrame(
            [features],
            columns=self.feature_names,
        )

        prediction = float(self.model.predict(frame)[0])

        return round(max(prediction, 0.0), 6)

    def predict_batch(self, data_list: list[RawIoTData]) -> list[float]:
        if not isinstance(data_list, list):
            raise TypeError("data_list must be a list of RawIoTData objects.")

        if not data_list:
            return []

        rows = [
            self._extract_features(data)
            for data in data_list
        ]

        frame = pd.DataFrame(
            rows,
            columns=self.feature_names,
        )

        predictions = self.model.predict(frame)

        return [
            round(max(float(prediction), 0.0), 6)
            for prediction in predictions
        ]