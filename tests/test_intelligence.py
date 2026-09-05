import pandas as pd

from app.intelligence import IntelligenceEngine


def sample_data():
    return pd.DataFrame({
        "timestamp": [
            "2026-09-01 08:00",
            "2026-09-01 10:00",
            "2026-09-01 12:00",
            "2026-09-01 14:00",
        ],
        "solar_generation": [
            1.2,
            3.0,
            4.0,
            3.5,
        ]
    })


def test_engine_output_columns():
    engine = IntelligenceEngine()

    result = engine.analyze(sample_data(), 5.0)

    assert "predicted_generation" in result.columns
    assert "expected_generation" in result.columns
    assert "actual_generation" in result.columns
    assert "performance_loss" in result.columns
    assert "health_score" in result.columns
    assert "status" in result.columns


def test_health_score_exists():
    engine = IntelligenceEngine()

    result = engine.analyze(sample_data(), 5.0)

    assert (result["health_score"] >= 0).all()
    assert (result["health_score"] <= 100).all()


def test_status_exists():
    engine = IntelligenceEngine()

    result = engine.analyze(sample_data(), 5.0)

    valid_statuses = {"healthy", "warning", "critical"}

    assert set(result["status"]).issubset(valid_statuses)


def test_actual_generation_matches_input():
    engine = IntelligenceEngine()

    result = engine.analyze(sample_data(), 5.0)

    assert result["actual_generation"].tolist() == [
        1.2, 3.0, 4.0, 3.5
    ]


def test_engine_returns_same_number_of_rows():
    engine = IntelligenceEngine()

    result = engine.analyze(sample_data(), 5.0)

    assert len(result) == len(sample_data())

def test_intelligence_engine_uses_healthy_baseline():
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

    engine = IntelligenceEngine()

    result = engine.analyze(
        actual,
        capacity=5.0,
        baseline_dataframe=baseline
    )

    assert result.loc[1, "expected_generation"] == 4.5
    assert result.loc[1, "actual_generation"] == 2.5
    assert result.loc[1, "performance_loss"] > 0