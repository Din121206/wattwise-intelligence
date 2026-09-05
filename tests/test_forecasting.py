import pandas as pd
import pytest

from forecasting.solar_forecast import SolarForecaster


def sample_data():
    return pd.DataFrame({
        "timestamp": [
            "2026-09-01 08:00",
            "2026-09-01 10:00",
            "2026-09-01 12:00",
            "2026-09-01 14:00",
            "2026-09-01 16:00",
        ],
        "solar_generation": [1.2, 3.5, 4.6, 4.1, 2.5]
    })


def test_forecast_generation():
    model = SolarForecaster(5.0)
    result = model.predict(sample_data())

    assert "predicted_generation" in result.columns
    assert len(result) == 5


def test_prediction_not_negative():
    model = SolarForecaster(5.0)
    result = model.predict(sample_data())

    assert (result["predicted_generation"] >= 0).all()


def test_prediction_does_not_exceed_capacity():
    model = SolarForecaster(5.0)
    result = model.predict(sample_data())

    assert (result["predicted_generation"] <= 5.0).all()


def test_peak_generation():
    model = SolarForecaster(5.0)
    result = model.predict(sample_data())

    peak = model.peak_generation_period(result)

    assert peak == 12


def test_invalid_capacity():
    with pytest.raises(ValueError):
        SolarForecaster(0)


def test_next_day_forecast():
    model = SolarForecaster(5.0)

    result = model.next_day_forecast(sample_data())

    assert len(result) == 24
    assert "timestamp" in result.columns
    assert "predicted_generation" in result.columns


def test_next_day_predictions_not_negative():
    model = SolarForecaster(5.0)

    result = model.next_day_forecast(sample_data())

    assert (result["predicted_generation"] >= 0).all()


def test_next_day_predictions_within_capacity():
    model = SolarForecaster(5.0)

    result = model.next_day_forecast(sample_data())

    assert (result["predicted_generation"] <= 5.0).all()


def test_next_day_starts_after_historical_data():
    model = SolarForecaster(5.0)

    result = model.next_day_forecast(sample_data())

    assert result["timestamp"].min() > pd.to_datetime(
        sample_data()["timestamp"]
    ).max()


def test_next_day_contains_all_hours():
    model = SolarForecaster(5.0)

    result = model.next_day_forecast(sample_data())

    assert result["timestamp"].dt.hour.tolist() == list(range(24))

def test_predict_from_healthy_baseline():
    import pandas as pd

    baseline = pd.DataFrame({
        "timestamp": [
            "2026-09-01 10:00",
            "2026-09-01 12:00",
            "2026-09-01 14:00"
        ],
        "solar_generation": [
            3.0,
            4.5,
            4.0
        ]
    })

    actual = pd.DataFrame({
        "timestamp": [
            "2026-09-02 10:00",
            "2026-09-02 12:00",
            "2026-09-02 14:00"
        ],
        "solar_generation": [
            2.0,
            2.5,
            2.0
        ]
    })

    forecaster = SolarForecaster(capacity=5.0)

    result = forecaster.predict_from_baseline(
        baseline,
        actual
    )

    assert "predicted_generation" in result.columns
    assert result.loc[1, "predicted_generation"] == 4.5
    assert result.loc[1, "solar_generation"] == 2.5