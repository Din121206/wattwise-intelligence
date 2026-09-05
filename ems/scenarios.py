"""
Pre-packaged demo energy scenarios for WattWise EMS.
Provides ready-to-use telemetry states to test dynamic EMS AI decision flows.
"""

from typing import Dict
from ems.models import EnergyState


DEMO_SCENARIOS: Dict[str, EnergyState] = {
    "excess_solar": EnergyState(
        installation_id="INST-DEMO-001",
        solar_generation_kw=8.5,
        grid_import_kw=0.0,
        load_consumption_kw=4.0,
        critical_load_kw=0.5
    ),
    "grid_import_required": EnergyState(
        installation_id="INST-DEMO-002",
        solar_generation_kw=2.0,
        grid_import_kw=5.0,
        load_consumption_kw=8.0,
        critical_load_kw=2.0
    ),
    "load_reduction": EnergyState(
        installation_id="INST-DEMO-003",
        solar_generation_kw=1.0,
        grid_import_kw=0.1,
        load_consumption_kw=6.0,
        critical_load_kw=1.0
    ),
    "critical_load_protection": EnergyState(
        installation_id="INST-DEMO-004",
        solar_generation_kw=0.2,
        grid_import_kw=0.1,
        load_consumption_kw=1.8,
        critical_load_kw=0.5
    ),
    "normal_operation": EnergyState(
        installation_id="INST-DEMO-005",
        solar_generation_kw=1.5,
        grid_import_kw=0.0,
        load_consumption_kw=1.5,
        critical_load_kw=0.3
    )
}
