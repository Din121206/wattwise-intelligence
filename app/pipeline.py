"""
WattWise Module 2
AI/ML processing pipeline.

This module provides the common processing flow that will
connect forecasting, digital twin, anomaly detection and
recommendation components.
"""

from typing import Any

import pandas as pd

from app.models import InstallationData


class IntelligencePipeline:
    """
    Central pipeline for WattWise Module 2.

    Day 1:
        - Validate input data
        - Convert input into a DataFrame
        - Perform basic preprocessing

    Later:
        - Forecasting
        - Digital Twin
        - Anomaly detection
        - Recommendations
    """

    def validate_input(self, data: InstallationData) -> bool:
        """
        Validate a single installation record.

        Pydantic performs the primary validation through
        InstallationData. This method provides a simple
        pipeline-level validation interface.
        """

        if not isinstance(data, InstallationData):
            raise TypeError(
                "Input must be an InstallationData object."
            )

        return True

    def preprocess(self, data: InstallationData) -> pd.DataFrame:
        """
        Convert validated installation data into a
        DataFrame suitable for future ML processing.
        """

        self.validate_input(data)

        # Convert the Pydantic model into a dictionary.
        record: dict[str, Any] = data.model_dump()

        # Create a one-row DataFrame.
        dataframe = pd.DataFrame([record])

        # Ensure timestamp is represented as a datetime.
        dataframe["timestamp"] = pd.to_datetime(
            dataframe["timestamp"],
            errors="coerce",
        )

        # Reject invalid timestamps.
        if dataframe["timestamp"].isna().any():
            raise ValueError("Invalid timestamp detected.")

        # Ensure numerical values are actually numeric.
        numeric_columns = [
            "capacity",
            "solar_generation",
            "energy_consumption",
            "grid_import",
            "grid_export",
            "system_efficiency",
        ]

        for column in numeric_columns:
            dataframe[column] = pd.to_numeric(
                dataframe[column],
                errors="coerce",
            )

        # Reject missing numerical values.
        if dataframe[numeric_columns].isna().any().any():
            raise ValueError(
                "Invalid or missing numerical values detected."
            )

        return dataframe

    def process(self, data: InstallationData) -> pd.DataFrame:
        """
        Execute the Day 1 intelligence pipeline.

        Forecasting, Digital Twin, anomaly detection and
        recommendations will be attached here in later phases.
        """

        return self.preprocess(data)