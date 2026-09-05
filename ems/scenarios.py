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
        battery_soc=72.0,
        grid_import_kw=1.2,
        load_consumption_kw=4.0,
        critical_load_kw=0.5
    ),
    "battery_full": EnergyState(
        installation_id="INST-DEMO-002",
        solar_generation_kw=8.5,
        battery_soc=92.0,
        grid_import_kw=0.0,
        load_consumption_kw=4.0,
        critical_load_kw=0.5
    ),
    "peak_consumption": EnergyState(
        installation_id="INST-DEMO-003",
        solar_generation_kw=2.0,
        battery_soc=65.0,
        grid_import_kw=5.0,
        load_consumption_kw=8.0,
        critical_load_kw=2.0
    ),
    "low_battery": EnergyState(
        installation_id="INST-DEMO-004",
        solar_generation_kw=0.1,
        battery_soc=18.0,
        grid_import_kw=2.7,
        load_consumption_kw=2.8,
        critical_load_kw=0.4
    ),
    "critical_load_protection": EnergyState(
        installation_id="INST-DEMO-005",
        solar_generation_kw=0.0,
        battery_soc=12.0,
        grid_import_kw=0.1,
        load_consumption_kw=1.8,
        critical_load_kw=0.5
    ),
    "normal_operation": EnergyState(
        installation_id="INST-DEMO-006",
        solar_generation_kw=1.5,
        battery_soc=60.0,
        grid_import_kw=0.0,
        load_consumption_kw=1.5,
        critical_load_kw=0.3
    )
}
