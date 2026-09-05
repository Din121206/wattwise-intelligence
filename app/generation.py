"""
WattWise Module 2
Solar generation estimation and prediction.
"""

import pandas as pd

from app.raw_models import RawIoTData


class GenerationAnalyzer:

    TEMPERATURE_COEFFICIENT = -0.004

    DEFAULT_SYSTEM_EFFICIENCY = 0.90

    def __init__(
        self,
        capacity: float,
        system_efficiency: float = DEFAULT_SYSTEM_EFFICIENCY
    ):

        if capacity <= 0:
            raise ValueError(
                "Solar capacity must be greater than zero."
            )

        if not 0 < system_efficiency <= 1:
            raise ValueError(
                "System efficiency must be between 0 and 1."
            )

        self.capacity = capacity
        self.system_efficiency = system_efficiency

    def expected_generation(
        self,
        data: RawIoTData
    ) -> float:
        """
        Calculate expected solar generation in kW.

        Formula:

        Expected =
        Capacity × (Irradiance / 1000)
        × Temperature Factor
        × System Efficiency
        """

        irradiance = (
            data.environment.irradiance
        )

        panel_temperature = (
            data.environment.panel_temperature
        )

        temperature_factor = (
            1
            + self.TEMPERATURE_COEFFICIENT
            * (panel_temperature - 25)
        )

        expected = (
            self.capacity
            * (irradiance / 1000)
            * temperature_factor
            * self.system_efficiency
        )

        return round(
            max(expected, 0),
            4
        )

    def predicted_generation(
        self,
        dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Create a historical generation forecast.

        Uses average generation for each hour
        from historical data.
        """

        required = {
            "timestamp",
            "solar_generation"
        }

        if not required.issubset(
            dataframe.columns
        ):
            raise ValueError(
                "Dataset must contain timestamp "
                "and solar_generation."
            )

        df = dataframe.copy()

        df["timestamp"] = pd.to_datetime(
            df["timestamp"]
        )

        df["hour"] = (
            df["timestamp"].dt.hour
        )

        hourly_average = (
            df.groupby("hour")[
                "solar_generation"
            ].mean()
        )

        df["predicted_generation"] = (
            df["hour"]
            .map(hourly_average)
            .fillna(0)
            .clip(
                lower=0,
                upper=self.capacity
            )
        )

        return df

    def next_hour_prediction(
        self,
        dataframe: pd.DataFrame,
        timestamp
    ) -> float:
        """
        Predict solar generation for the next hour.

        Uses historical generation averages
        for the target hour.

        This baseline can later be replaced
        by an ML forecasting model.
        """

        required = {
            "timestamp",
            "solar_generation"
        }

        if not required.issubset(
            dataframe.columns
        ):
            raise ValueError(
                "Dataset must contain timestamp "
                "and solar_generation."
            )

        df = dataframe.copy()

        df["timestamp"] = pd.to_datetime(
            df["timestamp"]
        )

        timestamp = pd.to_datetime(
            timestamp
        )

        next_hour = (
            timestamp + pd.Timedelta(hours=1)
        ).hour

        df["hour"] = (
            df["timestamp"].dt.hour
        )

        hourly_average = (
            df.groupby("hour")[
                "solar_generation"
            ].mean()
        )

        prediction = hourly_average.get(
            next_hour,
            0.0
        )

        return round(
            max(
                min(
                    float(prediction),
                    self.capacity
                ),
                0.0
            ),
            4
        )