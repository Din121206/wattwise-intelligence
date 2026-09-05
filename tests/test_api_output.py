import pandas as pd

from app.intelligence import IntelligenceEngine
from app.models import IntelligenceOutput


def sample_data():
    return pd.DataFrame({
        "timestamp": [
            "2026-09-01 08:00",
            "2026-09-01 10:00",
            "2026-09-01 12:00",
        ],
        "solar_generation": [
            1.2,
            3.0,
            4.0,
        ]
    })


def test_api_output_type():
    engine = IntelligenceEngine()

    result = engine.analyze(sample_data(), 5.0)
    output = engine.api_output(result)

    assert isinstance(output, IntelligenceOutput)


def test_api_output_fields():
    engine = IntelligenceEngine()

    result = engine.analyze(sample_data(), 5.0)
    output = engine.api_output(result)

    data = output.model_dump()

    required = {
        "predicted_generation",
        "expected_generation",
        "actual_generation",
        "performance_loss",
        "health_score",
        "status",
        "anomaly",
        "likely_cause",
        "recommendation"
    }

    assert required.issubset(data.keys())


def test_api_output_values():
    engine = IntelligenceEngine()

    result = engine.analyze(sample_data(), 5.0)
    output = engine.api_output(result)

    assert output.actual_generation == 4.0
    assert output.expected_generation == 4.0
    assert output.performance_loss == 0
    assert output.health_score == 100
    assert output.status == "healthy"


def test_api_output_anomaly_default():
    engine = IntelligenceEngine()

    result = engine.analyze(sample_data(), 5.0)
    output = engine.api_output(result)

    assert output.anomaly is False
    assert output.likely_cause is None


def test_api_output_recommendation():
    engine = IntelligenceEngine()

    result = engine.analyze(sample_data(), 5.0)
    output = engine.api_output(result)

    assert output.recommendation == "Continue regular monitoring."

def test_api_output_detects_anomaly():
    engine = IntelligenceEngine()

    data = pd.DataFrame({
        "timestamp": [
            "2026-09-01 10:00",
            "2026-09-01 12:00",
            "2026-09-02 10:00",
            "2026-09-02 12:00"
        ],
        "solar_generation": [
            3.0,
            4.0,
            1.5,
            2.0
        ]
    })

    result = engine.analyze(data, 5.0)
    output = engine.api_output(result)

    assert output.anomaly is True
    assert output.likely_cause is not None
    assert output.recommendation != "Continue regular monitoring."