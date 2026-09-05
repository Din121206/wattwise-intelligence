"""
WattWise EMS AI Module API Service.
"""

from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from ems.router import router as ems_router


app = FastAPI(
    title="WattWise EMS AI Module",
    description="Energy Management System AI API & Dashboard",
    version="1.0.0"
)

# Include EMS Module Endpoints
app.include_router(ems_router)


@app.get("/")
def root():
    return {
        "service": "WattWise EMS AI Module",
        "status": "online",
        "ems_control_center": "/ems"
    }


@app.get("/ems", response_class=HTMLResponse, summary="EMS Control Center UI Dashboard")
def ems_dashboard():
    """Serves the interactive EMS Control Center UI Dashboard."""
    html_path = Path(__file__).parent.parent / "ems" / "static" / "index.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
    raise HTTPException(status_code=404, detail="EMS Control Center UI template not found.")


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }