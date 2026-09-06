import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

CONTROL_ACTIONS = [
    "GRID_EXPORT", "GRID_IMPORT", "CRITICAL_LOAD_PROTECTION",
    "OPTIMIZE_LOAD", "LOAD_SHIFT", "LOAD_REDUCE", "MAINTAIN",
]
TOTAL_PER_ACTION = 60

def sample_for_action(action, index):
    random.seed(1000 + index)
    solar_v = random.uniform(17.5, 19.0)
    irradiance = random.uniform(750, 1000)
    load_v = 12.0
    grid_v = 230.0
    grid_c = random.uniform(2.0, 8.0)
    battery_v = random.uniform(12.6, 14.2)
    battery_c = random.uniform(0.2, 1.0)
    predicted = random.uniform(0.012, 0.019)

    if action == "GRID_EXPORT":
        solar_c, load_c = random.uniform(1.05, 1.20), random.uniform(0.20, 0.35)
        battery_c = random.uniform(-0.05, 0.20)
    elif action == "GRID_IMPORT":
        solar_c, load_c = random.uniform(0.25, 0.50), random.uniform(0.90, 1.20)
    elif action == "CRITICAL_LOAD_PROTECTION":
        solar_c, load_c = random.uniform(0.15, 0.30), random.uniform(1.10, 1.40)
        battery_v = random.uniform(11.3, 11.7)
        grid_c = 0.0
    elif action == "OPTIMIZE_LOAD":
        solar_c, load_c = random.uniform(0.75, 1.00), random.uniform(0.60, 0.80)
        predicted = random.uniform(0.010, 0.015)
        grid_c = 0.0
    elif action == "LOAD_SHIFT":
        solar_c, load_c = random.uniform(0.25, 0.55), random.uniform(0.55, 0.80)
        predicted = random.uniform(0.014, 0.019)
        irradiance = random.uniform(300, 650)
        grid_c = 0.0
    elif action == "LOAD_REDUCE":
        solar_c, load_c = random.uniform(0.75, 1.00), random.uniform(0.95, 1.25)
        predicted = random.uniform(0.008, 0.013)
        grid_c = 0.0
    else:
        solar_c, load_c = random.uniform(0.80, 1.00), random.uniform(0.25, 0.50)
        predicted = random.uniform(0.012, 0.018)
        grid_c = 0.0

    timestamp = datetime(2026, 9, 1, 8, 0, tzinfo=timezone.utc) + timedelta(hours=index)
    return {
        "installation_id": f"INST-{index % 10 + 1:03d}",
        "timestamp": timestamp.isoformat().replace("+00:00", "Z"),
        "solar": {"voltage": round(solar_v, 2), "current": round(solar_c, 3)},
        "environment": {"irradiance": round(irradiance, 1), "panel_temperature": round(random.uniform(30, 48), 1), "ambient_temperature": round(random.uniform(25, 35), 1)},
        "grid": {"voltage": grid_v if grid_c > 0 else 0.0, "current": round(grid_c, 3)},
        "load": {"voltage": load_v, "current": round(load_c, 3)},
        "battery": {"voltage": round(battery_v, 2), "current": round(battery_c, 3), "temperature": round(random.uniform(30, 42), 1)},
        "inverter": {"voltage": 12.0, "current": round(solar_c, 3), "temperature": round(random.uniform(35, 50), 1), "status_code": 0},
        "predicted_generation": round(predicted, 6),
        "control_action": action,
    }

def generate_dataset():
    rows = []
    index = 0
    for action in CONTROL_ACTIONS:
        for _ in range(TOTAL_PER_ACTION):
            rows.append(sample_for_action(action, index))
            index += 1
    return rows

def save_dataset(rows, path="data/control_training_dataset.json"):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(rows, indent=2), encoding="utf-8")

if __name__ == "__main__":
    rows = generate_dataset()
    save_dataset(rows)
    print(f"Generated {len(rows)} control-action samples.")
    print("Dataset saved to data/control_training_dataset.json")
