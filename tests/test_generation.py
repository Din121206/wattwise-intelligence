import pandas as pd
import pytest

from app.raw_models import RawIoTData
from app.generation import GenerationAnalyzer


def create_data():
    return RawIoTData(
        installation_id="INST-001",
        timestamp="2026-09-04T08:45:00Z",
        solar={
            "voltage": 231.4,
            "current": 18.1
        },
        environment={
            "irradiance": 742,
            "panel_temperature": 46.8,
            "ambient_temperature": 31.2
        },
        grid={
            "voltage": 230.8,
            "current": 8.4
        },
        load={
            "voltage": 230.5,
            "current": 13.9
        },
        battery={
            "voltage": 51.6,
            "current": 4.7,
            "temperature": 34.2
        },
        inverter={
            "voltage": 231.1,
            "current": 17.9,
            "temperature": 52.3,
            "status_code": 0
        }
    )


def test_expected_generation():
    analyzer = GenerationAnalyzer(capacity=5.0)

    data = create_data()

    result = analyzer.expected_generation(data)

    assert result > 0
    assert result < 5.0


def test_expected_generation_uses_irradiance():
    analyzer = GenerationAnalyzer(capacity=5.0)

    data = create_data()

    normal = analyzer.expected_generation(data)

    data.environment.irradiance = 300

    lower = analyzer.expected_generation(data)

    assert lower < normal


def test_expected_generation_temperature_effect():
    analyzer = GenerationAnalyzer(capacity=5.0)

    data = create_data()

    normal = analyzer.expected_generation(data)

    data.environment.panel_temperature = 70

    hotter = analyzer.expected_generation(data)

    assert hotter < normal


def test_predicted_generation():
    analyzer = GenerationAnalyzer(capacity=5.0)

    dataframe = pd.DataFrame({
        "timestamp": [
            "2026-09-01 08:00",
            "2026-09-02 08:00",
            "2026-09-03 08:00",
            "2026-09-01 10:00",
            "2026-09-02 10:00",
            "2026-09-03 10:00",
        ],
        "solar_generation": [
            1.0,
            1.2,
            1.1,
            3.0,
            3.2,
            3.1,
        ]
    })

    result = analyzer.predicted_generation(dataframe)

    assert "predicted_generation" in result.columns
    assert result.loc[0, "predicted_generation"] == pytest.approx(1.1)
    assert result.loc[3, "predicted_generation"] == pytest.approx(3.1)


def test_prediction_is_limited_by_capacity():
    analyzer = GenerationAnalyzer(capacity=2.0)

    dataframe = pd.DataFrame({
        "timestamp": [
            "2026-09-01 10:00",
            "2026-09-02 10:00",
        ],
        "solar_generation": [
            3.0,
            4.0,
        ]
    })

    result = analyzer.predicted_generation(dataframe)

    assert result["predicted_generation"].max() <= 2.0


def test_invalid_capacity():
    with pytest.raises(ValueError):
        GenerationAnalyzer(capacity=0)


def test_missing_prediction_columns():
    analyzer = GenerationAnalyzer(capacity=5.0)

    dataframe = pd.DataFrame({
        "solar_generation": [1.0]
    })

    with pytest.raises(ValueError):
        analyzer.predicted_generation(dataframe)

def test_expected_generation_accepts_custom_efficiency():

    from app.generation import GenerationAnalyzer
    from tests.test_raw_intelligence import create_raw_data

    raw_data = create_raw_data()

    analyzer = GenerationAnalyzer(
        capacity=0.02,
        system_efficiency=0.80
    )

    result = analyzer.expected_generation(
        raw_data
    )

    assert result >= 0


def test_invalid_system_efficiency_rejected():

    from app.generation import GenerationAnalyzer

    try:
        GenerationAnalyzer(
            capacity=0.02,
            system_efficiency=1.5
        )

        assert False

    except ValueError:
        assert True

def test_next_hour_prediction():

    from app.generation import GenerationAnalyzer

    import pandas as pd

    dataframe = pd.DataFrame({
        "timestamp": [
            "2026-09-01 09:00:00",
            "2026-09-02 09:00:00",
            "2026-09-01 10:00:00",
            "2026-09-02 10:00:00",
        ],
        "solar_generation": [
            1.0,
            1.2,
            2.0,
            2.2,
        ],
    })

    analyzer = GenerationAnalyzer(
        capacity=5.0
    )

    prediction = analyzer.next_hour_prediction(
        dataframe,
        "2026-09-03 09:30:00"
    )

    assert prediction == 2.1


def test_next_hour_prediction_respects_capacity():

    from app.generation import GenerationAnalyzer

    import pandas as pd

    dataframe = pd.DataFrame({
        "timestamp": [
            "2026-09-01 10:00:00",
            "2026-09-02 10:00:00",
        ],
        "solar_generation": [
            8.0,
            9.0,
        ],
    })

    analyzer = GenerationAnalyzer(
        capacity=5.0
    )

    prediction = analyzer.next_hour_prediction(
        dataframe,
        "2026-09-03 09:30:00"
    )

    assert prediction == 5.0