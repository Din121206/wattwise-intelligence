"""
WattWise Module 2
Backend API client.

Sends Module 2 intelligence output
to the WattWise backend.
"""

import requests


class IntelligenceAPIClient:

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def send_intelligence(
        self,
        installation_id: str,
        intelligence_output
    ):

        url = (
            f"{self.base_url}/api/installations/"
            f"{installation_id}/intelligence"
        )

        payload = intelligence_output.model_dump()

        response = requests.post(
            url,
            json=payload,
            timeout=10
        )

        response.raise_for_status()

        return response