import pandas as pd

from app.alerts import AlertGenerator


def test_anomaly_creates_alert():

    data = pd.DataFrame([
        {
            "anomaly": True,
            "likely_cause": "Possible panel soiling",
            "recommendation": "Inspect and clean the solar panels.",
            "health_score": 72.0
        }
    ])

    generator = AlertGenerator()

    alerts = generator.generate(
        data,
        "INST-001"
    )

    assert len(alerts) == 1

    alert = alerts[0]

    assert alert["installation_id"] == "INST-001"
    assert alert["severity"] == "warning"
    assert alert["status"] == "active"
    assert alert["likely_cause"] == "Possible panel soiling"
    assert alert["recommendation"] == (
        "Inspect and clean the solar panels."
    )
    assert alert["alert_id"].startswith("ALT-")
    assert "created_at" in alert


def test_healthy_system_creates_no_alert():

    data = pd.DataFrame([
        {
            "anomaly": False,
            "likely_cause": None,
            "recommendation": "Continue regular monitoring.",
            "health_score": 100.0
        }
    ])

    generator = AlertGenerator()

    alerts = generator.generate(
        data,
        "INST-001"
    )

    assert alerts == []


def test_critical_health_creates_critical_alert():

    data = pd.DataFrame([
        {
            "anomaly": True,
            "likely_cause": "Possible inverter inefficiency",
            "recommendation": (
                "Inspect inverter performance and schedule maintenance."
            ),
            "health_score": 45.0
        }
    ])

    generator = AlertGenerator()

    alerts = generator.generate(
        data,
        "INST-001"
    )

    assert len(alerts) == 1
    assert alerts[0]["severity"] == "critical"