"""
WattWise Module 2
Performance Digital Twin.

Compares expected solar generation with actual
solar generation and calculates performance loss.
"""

import pandas as pd


class PerformanceAnalyzer:

    def compare(
        self,
        dataframe: pd.DataFrame
    ) -> pd.DataFrame:

        df = dataframe.copy()

        # Support the new architecture
        # expected_generation + actual_generation
        if {
            "expected_generation",
            "actual_generation"
        }.issubset(df.columns):

            expected = df["expected_generation"]
            actual = df["actual_generation"]

        # Backward compatibility with the existing
        # simulation/test pipeline
        elif {
            "predicted_generation",
            "solar_generation"
        }.issubset(df.columns):

            expected = df["predicted_generation"]
            actual = df["solar_generation"]

            df["expected_generation"] = expected
            df["actual_generation"] = actual

        else:
            raise ValueError(
                "Dataset must contain either "
                "expected_generation and actual_generation "
                "or predicted_generation and solar_generation."
            )

        df["performance_loss"] = 0.0

        valid = expected > 0

        df.loc[valid, "performance_loss"] = (
            (
                expected[valid] - actual[valid]
            )
            / expected[valid]
        ) * 100

        df["performance_loss"] = (
            df["performance_loss"]
            .clip(lower=0, upper=100)
            .round(2)
        )

        return df