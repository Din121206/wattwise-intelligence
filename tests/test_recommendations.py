import pandas as pd
import pytest

from recommendations.engine import RecommendationEngine


def sample_data():
    return pd.DataFrame({
        "anomaly": [
            False,
            True,
            True,
            True
        ],
        "likely_cause": [
            None,
            "Possible panel soiling",
            "Possible partial shading",
            "Possible inverter inefficiency"
        ],
        "health_score": [
            100,
            85,
            75,
            90
        ]
    })


def test_recommendation_column_created():
    engine = RecommendationEngine()
    result = engine.generate(sample_data())

    assert "recommendation" in result.columns


def test_normal_system_recommendation():
    engine = RecommendationEngine()
    result = engine.generate(sample_data())

    assert result.loc[0, "recommendation"] == \
        "Continue regular monitoring."


def test_soiling_recommendation():
    engine = RecommendationEngine()
    result = engine.generate(sample_data())

    assert result.loc[1, "recommendation"] == \
        "Inspect and clean the solar panels."


def test_shading_recommendation():
    engine = RecommendationEngine()
    result = engine.generate(sample_data())

    assert result.loc[2, "recommendation"] == \
        "Inspect the installation for partial shading."


def test_inverter_recommendation():
    engine = RecommendationEngine()
    result = engine.generate(sample_data())

    assert result.loc[3, "recommendation"] == \
        "Inspect inverter performance and schedule maintenance."


def test_critical_health_overrides_recommendation():
    engine = RecommendationEngine()

    data = pd.DataFrame({
        "anomaly": [True],
        "likely_cause": ["Possible panel soiling"],
        "health_score": [50]
    })

    result = engine.generate(data)

    assert result.loc[0, "recommendation"] == \
        "Immediate system inspection and maintenance recommended."


def test_missing_columns():
    engine = RecommendationEngine()

    with pytest.raises(ValueError):
        engine.generate(
            pd.DataFrame({
                "anomaly": [True]
            })
        )

def test_unknown_anomaly_gets_investigation_recommendation():
    engine = RecommendationEngine()

    data = pd.DataFrame({
        "anomaly": [True],
        "likely_cause": ["Unknown performance issue"],
        "health_score": [70]
    })

    result = engine.generate(data)

    assert result.loc[0, "recommendation"] == (
        "Investigate the system for the source of abnormal performance."
    )


def test_cloudy_weather_recommendation():
    engine = RecommendationEngine()

    data = pd.DataFrame({
        "anomaly": [True],
        "likely_cause": ["Possible cloudy weather"],
        "health_score": [75]
    })

    result = engine.generate(data)

    assert result.loc[0, "recommendation"] == (
        "Monitor generation during changing weather conditions."
    )

def test_high_energy_consumption_recommendation():

    normal = pd.DataFrame([
        {"energy_consumption": 2.0},
        {"energy_consumption": 2.5},
        {"energy_consumption": 3.0}
    ])

    actual = pd.DataFrame([
        {
            "anomaly": False,
            "likely_cause": None,
            "health_score": 100.0,
            "energy_consumption": 5.0
        }
    ])

    engine = RecommendationEngine()

    result = engine.generate(
        actual,
        baseline_dataframe=normal
    )

    assert "High energy consumption" in result.iloc[0]["recommendation"]