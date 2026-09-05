"""
WattWise Module 2
Likely cause classification for solar anomalies.

This is a rule-based prototype. Final fault classification
will use actual IoT sensor features when the sensor schema
is finalized.
"""

import pandas as pd


class CauseClassifier:

    def classify(self, dataframe: pd.DataFrame) -> pd.DataFrame:

        required = {
            "anomaly",
            "performance_loss"
        }

        if not required.issubset(dataframe.columns):
            raise ValueError(
                "Dataset must contain anomaly and performance_loss."
            )

        df = dataframe.copy()

        df["likely_cause"] = None

        # -------------------------------------------------
        # Rule 1: Cloudy weather
        # -------------------------------------------------
        if "weather" in df.columns:
            cloudy = (
                df["anomaly"]
                & df["weather"].astype(str).str.lower().eq("cloudy")
            )

            df.loc[
                cloudy,
                "likely_cause"
            ] = "Possible cloudy weather"

        # -------------------------------------------------
        # Rule 2: Inverter inefficiency
        # -------------------------------------------------
        if "system_efficiency" in df.columns:
            inverter = (
                df["anomaly"]
                & (df["system_efficiency"] < 70)
                & df["likely_cause"].isna()
            )

            df.loc[
                inverter,
                "likely_cause"
            ] = "Possible inverter inefficiency"

        # -------------------------------------------------
        # Rule 3: Panel soiling
        # -------------------------------------------------
        if "system_efficiency" in df.columns:
            soiling = (
                df["anomaly"]
                & (df["system_efficiency"] < 75)
                & (df["system_efficiency"] >= 70)
                & df["likely_cause"].isna()
            )

            df.loc[
                soiling,
                "likely_cause"
            ] = "Possible panel soiling"

        # -------------------------------------------------
        # Rule 4: Partial shading
        # -------------------------------------------------
        if "system_efficiency" in df.columns:
            shading = (
                df["anomaly"]
                & (df["system_efficiency"] >= 75)
                & df["likely_cause"].isna()
            )

            df.loc[
                shading,
                "likely_cause"
            ] = "Possible partial shading"

        # -------------------------------------------------
        # Fallback rule
        # -------------------------------------------------
        unknown = (
            df["anomaly"]
            & df["likely_cause"].isna()
        )

        df.loc[
            unknown,
            "likely_cause"
        ] = "Unknown performance issue"

        return df