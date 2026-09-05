import pandas as pd
import pytest

from anomaly.detector import AnomalyDetector


def sample_data():
    return pd.DataFrame({
        "performance_loss": [
            2.0,
            10.0,
            15.0,
            25.0
        ]
    })


def test_anomaly_column_created():
    detector = AnomalyDetector()
    result = detector.detect(sample_data())

    assert "anomaly" in result.columns


def test_normal_performance_is_not_anomaly():
    detector = AnomalyDetector()
    result = detector.detect(sample_data())

    assert not result.loc[0, "anomaly"]


def test_loss_below_threshold_is_not_anomaly():
    detector = AnomalyDetector()
    result = detector.detect(sample_data())

    assert not result.loc[1, "anomaly"]


def test_threshold_loss_is_anomaly():
    detector = AnomalyDetector()
    result = detector.detect(sample_data())

    assert result.loc[2, "anomaly"]


def test_high_loss_is_anomaly():
    detector = AnomalyDetector()
    result = detector.detect(sample_data())

    assert result.loc[3, "anomaly"]


def test_custom_threshold():
    detector = AnomalyDetector(loss_threshold=30.0)
    result = detector.detect(sample_data())

    assert not result.loc[3, "anomaly"]