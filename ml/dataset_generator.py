"""
WattWise ML Training Dataset Generator.

Generates 150 realistic raw IoT telemetry samples
for six WattWise operating scenarios.

The production input schema remains unchanged.
The "scenario" field is used ONLY as the ML training label.
"""

from datetime import datetime, timedelta, timezone
import json
import random
from pathlib import Path


TOTAL_SAMPLES = 150
SAMPLES_PER_SCENARIO = 25

SCENARIOS = [
    "normal_sunny",
    "cloudy_weather",
    "panel_soiling",
    "partial_shading",
    "inverter_inefficiency",
    "high_energy_consumption",
]


def generate_sample(
    installation_id: str,
    timestamp: datetime,
    scenario: str,
) -> dict:

    # ---------------------------------------------------------
    # Base environmental conditions
    # ---------------------------------------------------------

    ambient_temperature = random.uniform(
        28.0,
        35.0,
    )

    # ---------------------------------------------------------
    # Scenario-specific solar/environment behaviour
    # ---------------------------------------------------------

    if scenario == "normal_sunny":

        irradiance = random.uniform(
            750,
            1000,
        )

        solar_voltage = random.uniform(
            17.5,
            19.0,
        )

        solar_current = random.uniform(
            0.85,
            1.05,
        )

        inverter_current_factor = random.uniform(
            0.95,
            1.00,
        )

        load_current = random.uniform(
            0.25,
            0.50,
        )

    elif scenario == "cloudy_weather":

        # Main distinguishing feature:
        # low irradiance.
        irradiance = random.uniform(
            180,
            550,
        )

        solar_voltage = random.uniform(
            15.5,
            18.0,
        )

        solar_current = random.uniform(
            0.20,
            0.60,
        )

        inverter_current_factor = random.uniform(
            0.92,
            1.00,
        )

        load_current = random.uniform(
            0.25,
            0.60,
        )

    elif scenario == "panel_soiling":

        # High irradiance but reduced current.
        irradiance = random.uniform(
            750,
            1000,
        )

        solar_voltage = random.uniform(
            17.0,
            18.8,
        )

        solar_current = random.uniform(
            0.30,
            0.58,
        )

        inverter_current_factor = random.uniform(
            0.94,
            1.00,
        )

        load_current = random.uniform(
            0.25,
            0.55,
        )

    elif scenario == "partial_shading":

        # High/moderate irradiance.
        # Shading causes a stronger voltage variation
        # and reduced solar current.
        irradiance = random.uniform(
            650,
            950,
        )

        solar_voltage = random.uniform(
            11.5,
            16.0,
        )

        solar_current = random.uniform(
            0.25,
            0.55,
        )

        inverter_current_factor = random.uniform(
            0.90,
            0.98,
        )

        load_current = random.uniform(
            0.25,
            0.55,
        )

    elif scenario == "inverter_inefficiency":

        # Solar input remains healthy.
        irradiance = random.uniform(
            700,
            1000,
        )

        solar_voltage = random.uniform(
            17.5,
            19.0,
        )

        solar_current = random.uniform(
            0.80,
            1.05,
        )

        # Inverter receives healthy solar power but
        # operates inefficiently.
        inverter_current_factor = random.uniform(
            0.55,
            0.75,
        )

        load_current = random.uniform(
            0.30,
            0.60,
        )

    elif scenario == "high_energy_consumption":

        # Solar generation remains relatively normal.
        irradiance = random.uniform(
            700,
            1000,
        )

        solar_voltage = random.uniform(
            17.5,
            19.0,
        )

        solar_current = random.uniform(
            0.80,
            1.05,
        )

        inverter_current_factor = random.uniform(
            0.94,
            1.00,
        )

        # Main distinguishing feature:
        # unusually high load.
        load_current = random.uniform(
            0.85,
            1.20,
        )

    else:
        raise ValueError(
            f"Unknown scenario: {scenario}"
        )

    # ---------------------------------------------------------
    # Panel temperature
    # ---------------------------------------------------------

    panel_temperature = (
        ambient_temperature
        + (irradiance / 1000.0) * 15.0
        + random.uniform(
            -1.5,
            1.5,
        )
    )

    # ---------------------------------------------------------
    # Inverter
    # ---------------------------------------------------------

    inverter_voltage = random.uniform(
        11.8,
        12.2,
    )

    inverter_current = (
        solar_current
        * inverter_current_factor
    )

    if scenario == "inverter_inefficiency":
        inverter_temperature = random.uniform(
            50.0,
            65.0,
        )
    else:
        inverter_temperature = random.uniform(
            35.0,
            48.0,
        )

    inverter_status_code = 0

    # ---------------------------------------------------------
    # Battery behaviour
    # ---------------------------------------------------------

    net_current = (
        solar_current
        - load_current
    )

    if net_current >= 0:

        battery_current = net_current

        battery_voltage = random.uniform(
            12.6,
            14.2,
        )

    else:

        battery_current = net_current

        battery_voltage = random.uniform(
            11.8,
            12.8,
        )

    battery_temperature = random.uniform(
        30.0,
        42.0,
    )

    # ---------------------------------------------------------
    # Small sensor noise
    # ---------------------------------------------------------

    solar_voltage += random.uniform(
        -0.20,
        0.20,
    )

    inverter_voltage += random.uniform(
        -0.10,
        0.10,
    )

    battery_temperature += random.uniform(
        -1.0,
        1.0,
    )

    # ---------------------------------------------------------
    # Return exact production-style telemetry
    # ---------------------------------------------------------

    return {
        "installation_id": installation_id,

        "timestamp": timestamp.isoformat().replace(
            "+00:00",
            "Z",
        ),

        "solar": {
            "voltage": round(
                max(solar_voltage, 0),
                2,
            ),
            "current": round(
                max(solar_current, 0),
                2,
            ),
        },

        "environment": {
            "irradiance": round(
                max(irradiance, 0),
                2,
            ),
            "panel_temperature": round(
                panel_temperature,
                2,
            ),
            "ambient_temperature": round(
                ambient_temperature,
                2,
            ),
        },

        # Current prototype is 12 V DC off-grid.
        "grid": {
            "voltage": 0.0,
            "current": 0.0,
        },

        "load": {
            "voltage": 12.0,
            "current": round(
                max(load_current, 0),
                2,
            ),
        },

        "battery": {
            "voltage": round(
                battery_voltage,
                2,
            ),
            "current": round(
                battery_current,
                2,
            ),
            "temperature": round(
                battery_temperature,
                2,
            ),
        },

        "inverter": {
            "voltage": round(
                inverter_voltage,
                2,
            ),
            "current": round(
                max(inverter_current, 0),
                2,
            ),
            "temperature": round(
                inverter_temperature,
                2,
            ),
            "status_code": inverter_status_code,
        },

        # Training label only.
        # Production API will NOT receive this field.
        "scenario": scenario,
    }


def generate_dataset(
    total_samples: int = TOTAL_SAMPLES,
) -> list[dict]:

    if total_samples <= 0:
        raise ValueError(
            "total_samples must be greater than zero."
        )

    random.seed(42)

    samples = []

    start_time = datetime(
        2026,
        9,
        1,
        6,
        0,
        0,
        tzinfo=timezone.utc,
    )

    for index in range(total_samples):

        scenario = SCENARIOS[
            index % len(SCENARIOS)
        ]

        timestamp = (
            start_time
            + timedelta(
                hours=index,
            )
        )

        installation_id = (
            f"INST-{(index % 10) + 1:03d}"
        )

        sample = generate_sample(
            installation_id=installation_id,
            timestamp=timestamp,
            scenario=scenario,
        )

        samples.append(sample)

    return samples


def save_dataset(
    samples: list[dict],
    output_path: str = (
        "data/ml_training_dataset.json"
    ),
) -> None:

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            samples,
            file,
            indent=2,
        )


if __name__ == "__main__":

    dataset = generate_dataset(
        TOTAL_SAMPLES,
    )

    save_dataset(
        dataset,
    )

    print(
        f"Generated {len(dataset)} samples."
    )

    print(
        "Scenarios:"
    )

    for scenario in SCENARIOS:

        count = sum(
            sample["scenario"] == scenario
            for sample in dataset
        )

        print(
            f"  {scenario}: {count}"
        )

    print(
        "Dataset saved to "
        "data/ml_training_dataset.json"
    )