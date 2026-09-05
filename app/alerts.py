"""
WattWise Module 2
Alert generation for detected system anomalies.
"""

from datetime import datetime, timezone
import uuid
import pandas as pd


class AlertGenerator:

    def generate(
        self,
        dataframe: pd.DataFrame,
        installation_id: str
    ) -> list[dict]:

        required = {
            "anomaly",
            "likely_cause",
            "recommendation",
            "health_score"
        }

        if not required.issubset(dataframe.columns):
            raise ValueError(
                "Dataset is missing required alert columns."
            )

        alerts = []

        for _, row in dataframe.iterrows():

            if not bool(row["anomaly"]):
                continue

            health_score = float(row["health_score"])

            if health_score < 60:
                severity = "critical"
            elif health_score < 80:
                severity = "warning"
            else:
                severity = "low"

            alert = {
                "alert_id": f"ALT-{uuid.uuid4().hex[:8].upper()}",
                "installation_id": installation_id,
                "severity": severity,
                "status": "active",
                "likely_cause": str(row["likely_cause"]),
                "recommendation": str(row["recommendation"]),
                "created_at": datetime.now(timezone.utc).isoformat()
            }

            alerts.append(alert)

        return alerts