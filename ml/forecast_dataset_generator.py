import json
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


OUTPUT_PATH = Path("data/ml_forecast_dataset.json")

SAMPLES = 150
DAYS = 10
RANDOM_SEED = 42


def solar_irradiance(hour: int, day: int) -> float:
    """
    Generate realistic daylight irradiance for a prototype dataset.

    Peak irradiance occurs around midday and changes slightly by day.
    """

    if hour < 6 or hour > 20:
        return 0.0

    daylight_position = (hour - 6) / 14

    curve = math.sin(math.pi * daylight_position)

    daily_factor = 0.90 + (day % 5) * 0.025

    noise = random.uniform(-25, 25)

    return max(
        0.0,
        min(
            1000.0,
            1000.0 * curve * daily_factor + noise
        )
    )


def solar_power_from_irradiance(
    irradiance: float,
    panel_temperature: float
) -> float:
    """
    Calculate approximate solar generation in kW.

    Prototype panel capacity:
    20 W = 0.020 kW
    """

    capacity_kw = 0.020

    temperature_coefficient = -0.004

    temperature_factor = (
        1
        + temperature_coefficient
        * (panel_temperature - 25)
    )

    efficiency = 0.90

    return max(
        0.0,
        capacity_kw
        * (irradiance / 1000.0)
        * temperature_factor
        * efficiency
    )


def generate_sample(day: int, hour: int) -> dict:
    current_irradiance = solar_irradiance(
        hour,
        day
    )

    next_hour = hour + 1

    next_irradiance = solar_irradiance(
        next_hour,
        day
    )

    ambient_temperature = (
        28
        + 5 * math.sin(
            math.pi
            * max(0, hour - 6)
            / 14
        )
        + random.uniform(-1.5, 1.5)
    )

    panel_temperature = (
        ambient_temperature
        + current_irradiance / 1000.0 * 15
        + random.uniform(-1.0, 1.0)
    )

    next_panel_temperature = (
        ambient_temperature
        + next_irradiance / 1000.0 * 15
    )

    current_power = solar_power_from_irradiance(
        current_irradiance,
        panel_temperature
    )

    next_hour_power = solar_power_from_irradiance(
        next_irradiance,
        next_panel_temperature
    )

    solar_voltage = (
        16.5
        + 2.0 * (current_irradiance / 1000.0)
        + random.uniform(-0.3, 0.3)
    )

    solar_voltage = max(
        0.0,
        solar_voltage
    )

    if solar_voltage > 0:
        solar_current = (
            current_power
            * 1000
            / solar_voltage
        )
    else:
        solar_current = 0.0

    solar_current += random.uniform(
        -0.02,
        0.02
    )

    solar_current = max(
        0.0,
        solar_current
    )

    load_voltage = 12.0

    load_current = random.uniform(
        0.20,
        0.60
    )

    battery_voltage = random.uniform(
        12.4,
        14.2
    )

    battery_current = (
        solar_current
        - load_current
    )

    inverter_temperature = (
        35
        + current_irradiance / 1000.0 * 15
        + random.uniform(-2, 2)
    )

    timestamp = datetime(
        2026,
        1,
        1,
        hour,
        0,
        0,
        tzinfo=timezone.utc
    ) + timedelta(days=day)

    return {
        "installation_id": "INST-001",
        "timestamp": timestamp.isoformat(),
        "solar": {
            "voltage": round(
                solar_voltage,
                3
            ),
            "current": round(
                solar_current,
                3
            )
        },
        "environment": {
            "irradiance": round(
                current_irradiance,
                2
            ),
            "panel_temperature": round(
                panel_temperature,
                2
            ),
            "ambient_temperature": round(
                ambient_temperature,
                2
            )
        },
        "grid": {
            "voltage": 0.0,
            "current": 0.0
        },
        "load": {
            "voltage": load_voltage,
            "current": round(
                load_current,
                3
            )
        },
        "battery": {
            "voltage": round(
                battery_voltage,
                3
            ),
            "current": round(
                battery_current,
                3
            ),
            "temperature": round(
                32 + random.uniform(-2, 4),
                2
            )
        },
        "inverter": {
            "voltage": round(
                solar_voltage,
                3
            ),
            "current": round(
                solar_current,
                3
            ),
            "temperature": round(
                inverter_temperature,
                2
            ),
            "status_code": 0
        },
        "target_next_hour_generation": round(
            next_hour_power,
            6
        )
    }


def generate_dataset():
    random.seed(RANDOM_SEED)

    samples = []

    for day in range(DAYS):
        for hour in range(6, 21):
            samples.append(
                generate_sample(
                    day,
                    hour
                )
            )

    samples = samples[:SAMPLES]

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            samples,
            file,
            indent=2
        )

    print(
        f"Generated {len(samples)} forecasting samples."
    )

    print(
        "Target: next-hour solar generation"
    )

    print(
        f"Dataset saved to {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    generate_dataset()