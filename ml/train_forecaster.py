import json
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split


DATA_PATH = Path("data/ml_forecast_dataset.json")
MODEL_PATH = Path("ml/models/solar_forecaster.joblib")


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


def load_dataset():
    with open(
        DATA_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    rows = []

    for item in data:
        timestamp = pd.to_datetime(
            item["timestamp"]
        )

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
                "hour": timestamp.hour,
                "target_next_hour_generation": item[
                    "target_next_hour_generation"
                ],
            }
        )

    return pd.DataFrame(rows)


def train():
    df = load_dataset()

    X = df[FEATURE_NAMES]
    y = df["target_next_hour_generation"]

    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=42,
    )

    X_validation, X_test, y_validation, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=23 / 45,
        random_state=42,
    )

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=1,
        random_state=42,
    )

    model.fit(
        X_train,
        y_train
    )

    validation_predictions = model.predict(
        X_validation
    )

    test_predictions = model.predict(
        X_test
    )

    validation_mae = mean_absolute_error(
        y_validation,
        validation_predictions
    )

    validation_r2 = r2_score(
        y_validation,
        validation_predictions
    )

    test_mae = mean_absolute_error(
        y_test,
        test_predictions
    )

    test_r2 = r2_score(
        y_test,
        test_predictions
    )

    print("\n=== Dataset Split ===")
    print(
        f"Training samples:   {len(X_train)}"
    )
    print(
        f"Validation samples: {len(X_validation)}"
    )
    print(
        f"Test samples:       {len(X_test)}"
    )

    print("\n=== Validation Metrics ===")
    print(
        f"MAE: {validation_mae:.6f} kW"
    )
    print(
        f"R2:  {validation_r2:.4f}"
    )

    print("\n=== Test Metrics ===")
    print(
        f"MAE: {test_mae:.6f} kW"
    )
    print(
        f"R2:  {test_r2:.4f}"
    )

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    import joblib

    package = {
        "model": model,
        "feature_names": FEATURE_NAMES,
        "target": "next_hour_generation",
    }

    joblib.dump(
        package,
        MODEL_PATH
    )

    print(
        f"\nModel saved to: {MODEL_PATH}"
    )


if __name__ == "__main__":
    train()