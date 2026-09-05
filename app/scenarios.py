"""
WattWise Module 2
Scenario definitions and simulation data.
"""

import pandas as pd

from enum import Enum


class Scenario(str, Enum):
    NORMAL_SUNNY = "normal_sunny"
    CLOUDY_WEATHER = "cloudy_weather"
    PANEL_SOILING = "panel_soiling"
    PARTIAL_SHADING = "partial_shading"
    INVERTER_INEFFICIENCY = "inverter_inefficiency"
    HIGH_ENERGY_CONSUMPTION = "high_energy_consumption"


class ScenarioSimulator:

    def generate(self, scenario: Scenario) -> pd.DataFrame:

        base = {
            "timestamp": pd.date_range(
                "2026-09-01 08:00",
                periods=6,
                freq="2h"
            ),
            "solar_generation": [
                1.2,
                3.5,
                4.6,
                4.1,
                2.5,
                1.0
            ],
            "energy_consumption": [
                2.0,
                2.5,
                3.0,
                2.8,
                2.2,
                1.8
            ],
            "weather": ["sunny"] * 6,
            "system_efficiency": [95.0] * 6
        }

        df = pd.DataFrame(base)

        # Normal sunny day
        if scenario == Scenario.NORMAL_SUNNY:
            return df

        # Cloudy weather
        if scenario == Scenario.CLOUDY_WEATHER:
            df["solar_generation"] *= 0.65
            df["weather"] = "cloudy"
            return df

        # Panel soiling
        if scenario == Scenario.PANEL_SOILING:
            df["solar_generation"] *= 0.70
            df["system_efficiency"] = 70.0
            return df

        # Partial shading
        if scenario == Scenario.PARTIAL_SHADING:
            df["solar_generation"] *= 0.55
            df["system_efficiency"] = 80.0
            return df

        # Inverter inefficiency
        if scenario == Scenario.INVERTER_INEFFICIENCY:
            df["solar_generation"] *= 0.75
            df["system_efficiency"] = 65.0
            return df

        # High energy consumption
        if scenario == Scenario.HIGH_ENERGY_CONSUMPTION:
            df["energy_consumption"] *= 2.0
            return df

        raise ValueError("Unsupported scenario.")