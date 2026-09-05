"""
WattWise Module 2
Anomaly detection for solar generation performance.
"""

import pandas as pd


class AnomalyDetector:

    def __init__(self, loss_threshold: float = 15.0):
        if loss_threshold < 0 or loss_threshold > 100:
            raise ValueError("Loss threshold must be between 0 and 100.")

        self.loss_threshold = loss_threshold

    def detect(self, dataframe: pd.DataFrame) -> pd.DataFrame:

        if "performance_loss" not in dataframe.columns:
            raise ValueError(
                "Dataset must contain performance_loss."
            )

        df = dataframe.copy()

        df["anomaly"] = (
            df["performance_loss"] >= self.loss_threshold
        )

        return df