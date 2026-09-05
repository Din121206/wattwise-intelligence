"""
WattWise Module 2
Intelligent recommendation engine.
"""

import pandas as pd


class RecommendationEngine:

    def generate(
        self,
        dataframe: pd.DataFrame,
        baseline_dataframe: pd.DataFrame | None = None
    ) -> pd.DataFrame:

        required = {
            "anomaly",
            "likely_cause",
            "health_score"
        }

        if not required.issubset(dataframe.columns):
            raise ValueError(
                "Dataset must contain anomaly, likely_cause and health_score."
            )

        df = dataframe.copy()

        # Default recommendation
        df["recommendation"] = (
            "Continue regular monitoring."
        )

        # Cloudy weather
        df.loc[
            df["likely_cause"] == "Possible cloudy weather",
            "recommendation"
        ] = (
            "Monitor generation during changing weather conditions."
        )

        # Panel soiling
        df.loc[
            df["likely_cause"] == "Possible panel soiling",
            "recommendation"
        ] = (
            "Inspect and clean the solar panels."
        )

        # Partial shading
        df.loc[
            df["likely_cause"] == "Possible partial shading",
            "recommendation"
        ] = (
            "Inspect the installation for partial shading."
        )

        # Inverter inefficiency
        df.loc[
            df["likely_cause"] == "Possible inverter inefficiency",
            "recommendation"
        ] = (
            "Inspect inverter performance and schedule maintenance."
        )

        # Unknown anomaly
        df.loc[
            (df["anomaly"] == True)
            & (
                df["likely_cause"]
                == "Unknown performance issue"
            ),
            "recommendation"
        ] = (
            "Investigate the system for the source of abnormal performance."
        )

        # High energy consumption
        if (
            baseline_dataframe is not None
            and "energy_consumption" in df.columns
            and "energy_consumption" in baseline_dataframe.columns
        ):

            baseline_mean = (
                baseline_dataframe["energy_consumption"].mean()
            )

            if baseline_mean > 0:

                high_consumption = (
                    df["energy_consumption"]
                    > baseline_mean * 1.5
                )

                df.loc[
                    high_consumption,
                    "recommendation"
                ] = (
                    "High energy consumption detected. "
                    "Optimize energy usage and reduce unnecessary loads."
                )

        # Critical health
        critical = df["health_score"] < 60

        df.loc[
            critical,
            "recommendation"
        ] = (
            "Immediate system inspection and maintenance recommended."
        )

        # Preserve specific information for critical partial shading
        df.loc[
            critical
            & (
                df["likely_cause"]
                == "Possible partial shading"
            ),
            "recommendation"
        ] = (
            "Immediate system inspection and maintenance recommended. "
            "Possible partial shading detected."
        )

        return df