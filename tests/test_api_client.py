from unittest.mock import patch

from app.api_client import IntelligenceAPIClient
from app.models import IntelligenceOutput


def test_send_intelligence():

    client = IntelligenceAPIClient(
        "http://localhost:8080"
    )

    output = IntelligenceOutput(
        predicted_generation=4.8,
        expected_generation=4.8,
        actual_generation=4.19,
        performance_loss=12.71,
        health_score=87.29,
        status="healthy",
        anomaly=True,
        likely_cause="Possible panel soiling",
        recommendation="Inspect and clean the solar panels."
    )

    with patch("requests.post") as mock_post:

        mock_post.return_value.raise_for_status.return_value = None

        client.send_intelligence(
            "INST-001",
            output
        )

        mock_post.assert_called_once()

        call = mock_post.call_args

        assert call.args[0] == (
            "http://localhost:8080/"
            "api/installations/INST-001/intelligence"
        )

        payload = call.kwargs["json"]

        assert len(payload) == 9

        assert payload["predicted_generation"] == 4.8
        assert payload["expected_generation"] == 4.8
        assert payload["actual_generation"] == 4.19
        assert payload["performance_loss"] == 12.71
        assert payload["health_score"] == 87.29
        assert payload["status"] == "healthy"
        assert payload["anomaly"] is True
        assert payload["likely_cause"] == (
            "Possible panel soiling"
        )
        assert payload["recommendation"] == (
            "Inspect and clean the solar panels."
        )