from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = PROJECT_ROOT / "data" / "milestone1_energy_dataset.csv"

MODEL_DIR = PROJECT_ROOT / "models"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

MODEL_FILE = MODEL_DIR / "energy_anomaly_model.joblib"
METRICS_FILE = PROCESSED_DIR / "anomaly_metrics.json"


FEATURE_COLUMNS = [
    "electricity_kwh",
    "water_liters",
    "hvac_kwh",
    "lighting_kwh",
    "temperature_c",
    "occupancy",
]


def prepare_directories():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_training_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Energy dataset not found: {DATA_FILE}"
        )

    df = pd.read_csv(DATA_FILE)

    missing_columns = [
        column
        for column in FEATURE_COLUMNS + ["is_anomaly"]
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Dataset missing required columns: {missing_columns}"
        )

    return df


def train_anomaly_model():
    """
    Train a supervised anomaly detector.

    Important:
    is_anomaly is the simulated ground-truth label in the
    Milestone 1 dataset.

    The model does NOT use is_anomaly as an input feature.
    It only uses it as the target during training.
    """

    prepare_directories()

    df = load_training_data()

    X = df[FEATURE_COLUMNS].copy()

    y = (
        df["is_anomaly"]
        .astype(str)
        .str.lower()
        .isin(["true", "1", "yes"])
        .astype(int)
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced",
        min_samples_leaf=2,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(
        y_test,
        predictions,
        zero_division=0,
    )
    recall = recall_score(
        y_test,
        predictions,
        zero_division=0,
    )
    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0,
    )

    matrix = confusion_matrix(
        y_test,
        predictions,
        labels=[0, 1],
    ).tolist()

    metrics = {
        "accuracy": round(float(accuracy), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1_score": round(float(f1), 4),
        "confusion_matrix": matrix,
        "training_rows": int(len(X_train)),
        "testing_rows": int(len(X_test)),
        "features": FEATURE_COLUMNS,
    }

    joblib.dump(model, MODEL_FILE)

    with open(
        METRICS_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metrics,
            file,
            indent=4,
        )

    return metrics


def load_anomaly_model():
    if not MODEL_FILE.exists():
        return None

    return joblib.load(MODEL_FILE)


def predict_anomaly(reading):
    """
    Predict anomaly probability for one reading.

    reading can be:
    - dict
    - pandas Series
    """

    model = load_anomaly_model()

    if model is None:
        return {
            "model_available": False,
            "is_anomaly": False,
            "probability": 0.0,
        }

    row = {
        feature: float(reading[feature])
        for feature in FEATURE_COLUMNS
    }

    data = pd.DataFrame([row])

    prediction = int(model.predict(data)[0])

    probability = float(
        model.predict_proba(data)[0][1]
    )

    return {
        "model_available": True,
        "is_anomaly": bool(prediction),
        "probability": round(probability, 4),
    }


def get_model_metrics():
    if not METRICS_FILE.exists():
        return None

    with open(
        METRICS_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


if __name__ == "__main__":

    metrics = train_anomaly_model()

    print("\nEnergy anomaly model trained successfully.\n")

    print(f"Accuracy : {metrics['accuracy'] * 100:.2f}%")
    print(f"Precision: {metrics['precision'] * 100:.2f}%")
    print(f"Recall   : {metrics['recall'] * 100:.2f}%")
    print(f"F1 Score : {metrics['f1_score'] * 100:.2f}%")

    print("\nModel saved to:")
    print(MODEL_FILE)

    print("\nMetrics saved to:")
    print(METRICS_FILE)