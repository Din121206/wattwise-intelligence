"""
Tests for the WattWise dataset loader.
"""

from pathlib import Path

import pytest

from app.data_loader import load_installation_data


DATASET = (
    Path(__file__).parent.parent
    / "data"
    / "sample_installations.csv"
)


def test_dataset_exists():
    """The development dataset should exist."""

    assert DATASET.exists()


def test_dataset_loads():
    """The dataset should load successfully."""

    dataframe = load_installation_data(DATASET)

    assert not dataframe.empty


def test_required_columns_exist():
    """All shared installation columns should exist."""

    dataframe = load_installation_data(DATASET)

    required = {
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

    assert required.issubset(dataframe.columns)


def test_timestamp_is_datetime():
    """Timestamp should be converted to datetime."""

    dataframe = load_installation_data(DATASET)

    assert str(dataframe["timestamp"].dtype).startswith(
        "datetime64"
    )


def test_missing_file_is_rejected():
    """A nonexistent dataset should raise an error."""

    with pytest.raises(FileNotFoundError):
        load_installation_data(
            "data/does_not_exist.csv"
        )