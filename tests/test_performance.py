import pandas as pd
import pytest

from digital_twin.performance import PerformanceAnalyzer


def test_performance_loss():
    analyzer = PerformanceAnalyzer()

    dataframe = pd.DataFrame({
        "expected_generation": [4.8],
        "actual_generation": [4.19],
    })

    result = analyzer.compare(dataframe)

    assert result.loc[0, "performance_loss"] == 12.71


def test_no_performance_loss():
    analyzer = PerformanceAnalyzer()

    dataframe = pd.DataFrame({
        "expected_generation": [5.0],
        "actual_generation": [5.0],
    })

    result = analyzer.compare(dataframe)

    assert result.loc[0, "performance_loss"] == 0.0


def test_actual_above_expected_has_zero_loss():
    analyzer = PerformanceAnalyzer()

    dataframe = pd.DataFrame({
        "expected_generation": [4.0],
        "actual_generation": [5.0],
    })

    result = analyzer.compare(dataframe)

    assert result.loc[0, "performance_loss"] == 0.0


def test_loss_is_limited_to_100():
    analyzer = PerformanceAnalyzer()

    dataframe = pd.DataFrame({
        "expected_generation": [2.0],
        "actual_generation": [0.0],
    })

    result = analyzer.compare(dataframe)

    assert result.loc[0, "performance_loss"] == 100.0


def test_zero_expected_generation():
    analyzer = PerformanceAnalyzer()

    dataframe = pd.DataFrame({
        "expected_generation": [0.0],
        "actual_generation": [0.0],
    })

    result = analyzer.compare(dataframe)

    assert result.loc[0, "performance_loss"] == 0.0


def test_missing_columns():
    analyzer = PerformanceAnalyzer()

    dataframe = pd.DataFrame({
        "actual_generation": [4.0]
    })

    with pytest.raises(ValueError):
        analyzer.compare(dataframe)