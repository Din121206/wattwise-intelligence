import json
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
import joblib

DATA_PATH = Path("data/control_training_dataset.json")
MODEL_PATH = Path("ml/models/control_action_classifier.joblib")
FEATURE_NAMES = [
    "solar_voltage", "solar_current", "irradiance", "panel_temperature", "ambient_temperature",
    "grid_voltage", "grid_current", "load_voltage", "load_current", "battery_voltage", "battery_current",
    "battery_temperature", "inverter_voltage", "inverter_current", "inverter_temperature",
    "inverter_status_code", "hour", "predicted_generation",
]
CONTROL_ACTIONS = {
    "GRID_EXPORT": 0, "GRID_IMPORT": 1, "CRITICAL_LOAD_PROTECTION": 2,
    "OPTIMIZE_LOAD": 3, "LOAD_SHIFT": 4, "LOAD_REDUCE": 5, "MAINTAIN": 6,
}

def load_dataset():
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    rows = []
    for item in data:
        rows.append({
            "solar_voltage": item["solar"]["voltage"], "solar_current": item["solar"]["current"],
            "irradiance": item["environment"]["irradiance"], "panel_temperature": item["environment"]["panel_temperature"],
            "ambient_temperature": item["environment"]["ambient_temperature"], "grid_voltage": item["grid"]["voltage"],
            "grid_current": item["grid"]["current"], "load_voltage": item["load"]["voltage"], "load_current": item["load"]["current"],
            "battery_voltage": item["battery"]["voltage"], "battery_current": item["battery"]["current"],
            "battery_temperature": item["battery"]["temperature"], "inverter_voltage": item["inverter"]["voltage"],
            "inverter_current": item["inverter"]["current"], "inverter_temperature": item["inverter"]["temperature"],
            "inverter_status_code": item["inverter"]["status_code"], "hour": pd.to_datetime(item["timestamp"]).hour,
            "predicted_generation": item["predicted_generation"], "control_action": item["control_action"],
        })
    return pd.DataFrame(rows)

def train():
    df = load_dataset()
    X, y = df[FEATURE_NAMES], df["control_action"].map(CONTROL_ACTIONS)
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.30, random_state=42, stratify=y)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)
    model = RandomForestClassifier(n_estimators=300, max_depth=12, min_samples_leaf=1, random_state=42, class_weight="balanced")
    model.fit(X_train, y_train)
    for name, truth, pred in [("Validation", y_val, model.predict(X_val)), ("Test", y_test, model.predict(X_test))]:
        print(f"{name} accuracy: {accuracy_score(truth, pred):.4f}")
    print(classification_report(y_test, model.predict(X_test), labels=list(CONTROL_ACTIONS.values()), target_names=list(CONTROL_ACTIONS.keys()), zero_division=0))
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "feature_names": FEATURE_NAMES, "control_actions": CONTROL_ACTIONS}, MODEL_PATH)
    print(f"Model saved to: {MODEL_PATH}")

if __name__ == "__main__":
    train()
