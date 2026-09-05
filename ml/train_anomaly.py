import json
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split


DATA_PATH = Path("data/ml_training_dataset.json")
MODEL_PATH = Path("ml/models/anomaly_classifier.joblib")

FEATURE_NAMES = [
    "solar_voltage",
    "solar_current",
    "irradiance",
    "panel_temperature",
    "ambient_temperature",
    "load_voltage",
    "load_current",
    "battery_voltage",
    "battery_current",
    "battery_temperature",
    "inverter_voltage",
    "inverter_current",
    "inverter_temperature",
    "inverter_status_code",
    "hour",
]

SCENARIO_LABELS = {
    "normal_sunny": 0,
    "cloudy_weather": 1,
    "panel_soiling": 2,
    "partial_shading": 3,
    "inverter_inefficiency": 4,
    "high_energy_consumption": 5,
}


def load_dataset():
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    rows = []

    for item in data:
        rows.append(
            {
                "solar_voltage": item["solar"]["voltage"],
                "solar_current": item["solar"]["current"],
                "irradiance": item["environment"]["irradiance"],
                "panel_temperature": item["environment"]["panel_temperature"],
                "ambient_temperature": item["environment"]["ambient_temperature"],
                "load_voltage": item["load"]["voltage"],
                "load_current": item["load"]["current"],
                "battery_voltage": item["battery"]["voltage"],
                "battery_current": item["battery"]["current"],
                "battery_temperature": item["battery"]["temperature"],
                "inverter_voltage": item["inverter"]["voltage"],
                "inverter_current": item["inverter"]["current"],
                "inverter_temperature": item["inverter"]["temperature"],
                "inverter_status_code": item["inverter"]["status_code"],
                "hour": pd.to_datetime(item["timestamp"]).hour,
                "scenario": item["scenario"],
            }
        )

    return pd.DataFrame(rows)


def train():
    df = load_dataset()

    X = df[FEATURE_NAMES]
    y = df["scenario"].map(SCENARIO_LABELS)

    if y.isna().any():
        raise ValueError("Unknown scenario found in dataset.")

    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=42,
        stratify=y,
    )

    X_validation, X_test, y_validation, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=23 / 45,
        random_state=42,
        stratify=y_temp,
    )

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=1,
        random_state=42,
        class_weight="balanced",
    )

    model.fit(X_train, y_train)

    validation_predictions = model.predict(X_validation)
    test_predictions = model.predict(X_test)

    validation_accuracy = accuracy_score(
        y_validation,
        validation_predictions,
    )

    test_accuracy = accuracy_score(
        y_test,
        test_predictions,
    )

    print("\n=== Dataset Split ===")
    print(f"Training samples:   {len(X_train)}")
    print(f"Validation samples: {len(X_validation)}")
    print(f"Test samples:       {len(X_test)}")

    print("\n=== Validation Accuracy ===")
    print(f"{validation_accuracy:.4f}")

    print("\n=== Test Accuracy ===")
    print(f"{test_accuracy:.4f}")

    print("\n=== Test Classification Report ===")
    print(
        classification_report(
            y_test,
            test_predictions,
            labels=list(SCENARIO_LABELS.values()),
            target_names=list(SCENARIO_LABELS.keys()),
            zero_division=0,
        )
    )

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    import joblib

    package = {
        "model": model,
        "feature_names": FEATURE_NAMES,
        "scenario_labels": SCENARIO_LABELS,
    }

    joblib.dump(package, MODEL_PATH)

    print(f"Model saved to: {MODEL_PATH}")


if __name__ == "__main__":
    train()