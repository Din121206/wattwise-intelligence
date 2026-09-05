"""
WattWise Module 2
Solar generation forecasting.
"""

import pandas as pd


class SolarForecaster:

    def __init__(self, capacity: float):
        if capacity <= 0:
            raise ValueError("Capacity must be greater than zero.")
        self.capacity = capacity

    def predict(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        required = {"timestamp", "solar_generation"}

        if not required.issubset(dataframe.columns):
            raise ValueError("Dataset is missing required columns.")

        df = dataframe.copy()

        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["hour"] = df["timestamp"].dt.hour

        hourly_average = (
            df.groupby("hour")["solar_generation"]
            .mean()
            .to_dict()
        )

        df["predicted_generation"] = (
            df["hour"]
            .map(hourly_average)
            .fillna(0)
            .clip(lower=0, upper=self.capacity)
        )

        return df

    def predict_from_baseline(
        self,
        baseline_dataframe: pd.DataFrame,
        actual_dataframe: pd.DataFrame
    ) -> pd.DataFrame:

        required = {"timestamp", "solar_generation"}

        if not required.issubset(baseline_dataframe.columns):
            raise ValueError(
                "Baseline dataset is missing required columns."
            )

        if not required.issubset(actual_dataframe.columns):
            raise ValueError(
                "Actual dataset is missing required columns."
            )

        baseline = baseline_dataframe.copy()
        actual = actual_dataframe.copy()

        baseline["timestamp"] = pd.to_datetime(
            baseline["timestamp"]
        )

        actual["timestamp"] = pd.to_datetime(
            actual["timestamp"]
        )

        baseline["hour"] = baseline["timestamp"].dt.hour
        actual["hour"] = actual["timestamp"].dt.hour

        hourly_average = (
            baseline.groupby("hour")["solar_generation"]
            .mean()
            .to_dict()
        )

        actual["predicted_generation"] = (
            actual["hour"]
            .map(hourly_average)
            .fillna(0)
            .clip(lower=0, upper=self.capacity)
        )

        return actual

    def next_day_forecast(
        self,
        dataframe: pd.DataFrame
    ) -> pd.DataFrame:

        required = {"timestamp", "solar_generation"}

        if not required.issubset(dataframe.columns):
            raise ValueError("Dataset is missing required columns.")

        df = dataframe.copy()

        df["timestamp"] = pd.to_datetime(df["timestamp"])

        hourly_average = (
            df.assign(hour=df["timestamp"].dt.hour)
            .groupby("hour")["solar_generation"]
            .mean()
        )

        last_date = df["timestamp"].max().normalize()
        next_day = last_date + pd.Timedelta(days=1)

        future_times = pd.date_range(
            start=next_day,
            periods=24,
            freq="h"
        )

        forecast = pd.DataFrame({
            "timestamp": future_times
        })

        forecast["hour"] = forecast["timestamp"].dt.hour

        forecast["predicted_generation"] = (
            forecast["hour"]
            .map(hourly_average)
            .fillna(0)
            .clip(lower=0, upper=self.capacity)
        )

        return forecast

    def peak_generation_period(
        self,
        dataframe: pd.DataFrame
    ) -> int:

        if "predicted_generation" not in dataframe.columns:
            raise ValueError(
                "Run predict() before finding peak."
            )

        peak_index = dataframe["predicted_generation"].idxmax()

        return int(dataframe.loc[peak_index, "hour"])