"""
WattWise Module 2
Dataset loading utilities.
"""

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "installation_id",
    "location",
    "capacity",
    "timestamp",
    "solar_generation",
    "energy_consumption",
    "grid_import",
    "grid_export",
    "weather",
    "system_efficiency",
}


def load_installation_data(file_path: str | Path) -> pd.DataFrame:
    """
    Load and validate a WattWise installation CSV file.

    Raises:
        FileNotFoundError: If the dataset does not exist.
        ValueError: If required columns are missing.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    dataframe = pd.read_csv(path)

    missing_columns = REQUIRED_COLUMNS - set(dataframe.columns)

    if missing_columns:
        raise ValueError(
            "Dataset is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    if dataframe.empty:
        raise ValueError("Dataset is empty.")

    dataframe["timestamp"] = pd.to_datetime(
        dataframe["timestamp"],
        errors="coerce",
    )

    if dataframe["timestamp"].isna().any():
        raise ValueError(
            "Dataset contains invalid timestamps."
        )

    return dataframe