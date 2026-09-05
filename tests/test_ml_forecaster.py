"""
Tests for the WattWise ML solar forecaster.
"""

from datetime import datetime, timezone

import pytest

from app.raw_models import RawIoTData
from ml.forecaster import MLSolarForecaster


def create_test_data() -> RawIoTData:

    return RawIoTData(
        installation_id="INST-001",
        timestamp=datetime(
            2026,
            9,
            5,
            10,
            0,
            tzinfo=timezone.utc,
        ),
        solar={
            "voltage": 18.0,
            "current": 0.9,
        },
        environment={
            "irradiance": 800.0,
            "panel_temperature": 40.0,
            "ambient_temperature": 31.0,
        },
        grid={
            "voltage": 0.0,
            "current": 0.0,
        },
        load={
            "voltage": 12.0,
            "current": 0.4,
        },
        battery={
            "voltage": 12.8,
            "current": 0.5,
            "temperature": 34.0,
        },
        inverter={
            "voltage": 12.0,
            "current": 0.9,
            "temperature": 40.0,
            "status_code": 0,
        },
    )


def test_model_loads():

    forecaster = MLSolarForecaster()

    assert forecaster.model is not None
    assert len(
        forecaster.feature_names
    ) == 15


def test_prediction_returns_number():

    forecaster = MLSolarForecaster()

    data = create_test_data()

    prediction = forecaster.predict(data)

    assert isinstance(
        prediction,
        float,
    )


def test_prediction_is_non_negative():

    forecaster = MLSolarForecaster()

    data = create_test_data()

    prediction = forecaster.predict(data)

    assert prediction >= 0


def test_prediction_is_within_panel_capacity():

    forecaster = MLSolarForecaster()

    data = create_test_data()

    prediction = forecaster.predict(data)

    # 20 W panel = 0.020 kW
    assert prediction <= 0.020


def test_batch_prediction():

    forecaster = MLSolarForecaster()

    data = create_test_data()

    predictions = forecaster.predict_batch(
        [data, data, data]
    )

    assert len(predictions) == 3

    assert all(
        isinstance(value, float)
        for value in predictions
    )


def test_empty_batch():

    forecaster = MLSolarForecaster()

    assert forecaster.predict_batch([]) == []


def test_invalid_input():

    forecaster = MLSolarForecaster()

    with pytest.raises(TypeError):
        forecaster.predict(
            {"invalid": "data"}
        )