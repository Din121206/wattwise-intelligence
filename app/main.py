"""
WattWise Module 2
AI API service.

Receives raw IoT telemetry from the WattWise backend,
runs the intelligence engine, and returns the
nested energy readings + intelligence output contract.
"""

from fastapi import FastAPI, HTTPException

from app.raw_models import RawIoTData
from app.intelligence import IntelligenceEngine


app = FastAPI(
    title="WattWise AI Module",
    description="Renewable Energy Intelligence API",
    version="1.0.0"
)


# 20 W solar panel = 0.020 kW
SOLAR_CAPACITY_KW = 0.020


@app.get("/")
def root():
    return {
        "service": "WattWise AI Module",
        "status": "online"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post(
    "/api/installations/{installation_id}/intelligence"
)
def analyze_intelligence(
    installation_id: str,
    raw_data: RawIoTData
):
    if installation_id != raw_data.installation_id:
        raise HTTPException(
            status_code=400,
            detail="Installation ID does not match raw data."
        )

    try:
        engine = IntelligenceEngine()

        output = engine.run_raw(
            raw_data=raw_data,
            capacity=SOLAR_CAPACITY_KW
        )

        return {
            "energy_readings": (
                output.energy_readings.model_dump()
            ),
            "intelligence_output": (
                output.intelligence_output.model_dump()
            )
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Intelligence processing failed: {exc}"
        )