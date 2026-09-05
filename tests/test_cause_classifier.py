import pandas as pd
import pytest

from anomaly.cause_classifier import CauseClassifier


def test_cause_column_created():
    classifier = CauseClassifier()

    data = pd.DataFrame({
        "performance_loss": [20.0],
        "anomaly": [True]
    })

    result = classifier.classify(data)

    assert "likely_cause" in result.columns


def test_normal_system_has_no_cause():
    classifier = CauseClassifier()

    data = pd.DataFrame({
        "performance_loss": [5.0],
        "anomaly": [False]
    })

    result = classifier.classify(data)

    assert pd.isna(result.loc[0, "likely_cause"])


def test_cloudy_weather_cause():
    classifier = CauseClassifier()

    data = pd.DataFrame({
        "performance_loss": [30.0],
        "anomaly": [True],
        "weather": ["cloudy"],
        "system_efficiency": [95.0]
    })

    result = classifier.classify(data)

    assert result.loc[0, "likely_cause"] == (
        "Possible cloudy weather"
    )


def test_inverter_inefficiency_cause():
    classifier = CauseClassifier()

    data = pd.DataFrame({
        "performance_loss": [30.0],
        "anomaly": [True],
        "weather": ["sunny"],
        "system_efficiency": [65.0]
    })

    result = classifier.classify(data)

    assert result.loc[0, "likely_cause"] == (
        "Possible inverter inefficiency"
    )


def test_panel_soiling_cause():
    classifier = CauseClassifier()

    data = pd.DataFrame({
        "performance_loss": [30.0],
        "anomaly": [True],
        "weather": ["sunny"],
        "system_efficiency": [70.0]
    })

    result = classifier.classify(data)

    assert result.loc[0, "likely_cause"] == (
        "Possible panel soiling"
    )


def test_partial_shading_cause():
    classifier = CauseClassifier()

    data = pd.DataFrame({
        "performance_loss": [30.0],
        "anomaly": [True],
        "weather": ["sunny"],
        "system_efficiency": [80.0]
    })

    result = classifier.classify(data)

    assert result.loc[0, "likely_cause"] == (
        "Possible partial shading"
    )


def test_unknown_issue_without_extra_signals():
    classifier = CauseClassifier()

    data = pd.DataFrame({
        "performance_loss": [30.0],
        "anomaly": [True]
    })

    result = classifier.classify(data)

    assert result.loc[0, "likely_cause"] == (
        "Unknown performance issue"
    )


def test_missing_required_columns():
    classifier = CauseClassifier()

    with pytest.raises(ValueError):
        classifier.classify(
            pd.DataFrame({
                "performance_loss": [20.0]
            })
        )