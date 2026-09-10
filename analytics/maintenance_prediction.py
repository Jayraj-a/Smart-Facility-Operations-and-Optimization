"""
FacilityOps AI
Milestone 2 - Predictive Maintenance Model

Purpose:
- Train a machine-learning model using asset-monitoring data
- Predict whether equipment requires maintenance
- Return maintenance risk probability
- Save model and evaluation metrics

The dataset used for Milestone 2 is simulated.
Therefore, evaluation results represent performance on the
simulated held-out dataset and should not be interpreted as
real-world equipment reliability.
"""

from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)
from sklearn.model_selection import train_test_split


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "milestone2_asset_dataset.csv"
)

MODEL_FILE = (
    PROJECT_ROOT
    / "models"
    / "maintenance_model.joblib"
)

METRICS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "maintenance_metrics.json"
)


# ============================================================
# MODEL CONFIGURATION
# ============================================================

FEATURES = [
    "temperature_c",
    "vibration_mm_s",
    "pressure_bar",
    "power_kw",
    "runtime_hours",
    "operating_hours",
    "age_years",
    "days_since_service",
]

TARGET = "maintenance_required"

RANDOM_STATE = 42


# ============================================================
# DATA LOADING
# ============================================================

def load_training_data():
    """
    Load and validate the Milestone 2 asset-monitoring dataset.
    """

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Maintenance dataset not found: {DATA_FILE}"
        )

    dataframe = pd.read_csv(DATA_FILE)

    required_columns = FEATURES + [TARGET]

    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            "Maintenance dataset is missing required columns: "
            + ", ".join(missing_columns)
        )

    dataframe = dataframe.dropna(
        subset=required_columns
    ).copy()

    for column in FEATURES:
        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

    dataframe[TARGET] = pd.to_numeric(
        dataframe[TARGET],
        errors="coerce",
    )

    dataframe = dataframe.dropna(
        subset=required_columns
    )

    dataframe[TARGET] = (
        dataframe[TARGET]
        .astype(int)
    )

    return dataframe


# ============================================================
# CREATE MODEL
# ============================================================

def create_model():
    """
    Create the Random Forest maintenance classifier.
    """

    return RandomForestClassifier(
        n_estimators=300,
        random_state=RANDOM_STATE,
        class_weight="balanced",
        min_samples_leaf=2,
        n_jobs=-1,
    )


# ============================================================
# TRAIN MODEL
# ============================================================

def train_model():
    """
    Train and evaluate the predictive maintenance model.
    """

    dataframe = load_training_data()

    X = dataframe[FEATURES]
    y = dataframe[TARGET]

    class_counts = (
        y.value_counts()
        .sort_index()
        .to_dict()
    )

    if y.nunique() < 2:
        raise ValueError(
            "The maintenance target contains only one class. "
            "Both normal and maintenance-required records "
            "are required for training."
        )

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.25,
            random_state=RANDOM_STATE,
            stratify=y,
        )
    )

    model = create_model()

    model.fit(
        X_train,
        y_train,
    )

    predictions = model.predict(
        X_test
    )

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

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
    )

    report = classification_report(
        y_test,
        predictions,
        labels=[0, 1],
        target_names=[
            "Normal",
            "Maintenance Required",
        ],
        output_dict=True,
        zero_division=0,
    )

    feature_importance = {
        feature: round(
            float(importance),
            6,
        )
        for feature, importance in zip(
            FEATURES,
            model.feature_importances_,
        )
    }

    metrics = {
        "model": "RandomForestClassifier",
        "dataset": "Simulated Milestone 2 asset monitoring dataset",
        "records": int(
            len(dataframe)
        ),
        "training_records": int(
            len(X_train)
        ),
        "testing_records": int(
            len(X_test)
        ),
        "normal_records": int(
            class_counts.get(
                0,
                0,
            )
        ),
        "maintenance_required_records": int(
            class_counts.get(
                1,
                0,
            )
        ),
        "accuracy": round(
            float(accuracy),
            6,
        ),
        "precision": round(
            float(precision),
            6,
        ),
        "recall": round(
            float(recall),
            6,
        ),
        "f1_score": round(
            float(f1),
            6,
        ),
        "confusion_matrix": (
            matrix.tolist()
        ),
        "feature_importance": (
            feature_importance
        ),
        "classification_report": (
            report
        ),
        "evaluation_note": (
            "Metrics are measured on a held-out portion "
            "of the simulated Milestone 2 dataset."
        ),
    }

    return (
        model,
        metrics,
        X_test,
        y_test,
        predictions,
        probabilities,
    )


# ============================================================
# SAVE MODEL
# ============================================================

def save_model(
    model,
    metrics,
):
    """
    Save trained model and evaluation metrics.
    """

    MODEL_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    METRICS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_package = {
        "model": model,
        "features": FEATURES,
        "target": TARGET,
        "model_name": (
            "FacilityOps AI "
            "Predictive Maintenance Model"
        ),
    }

    joblib.dump(
        model_package,
        MODEL_FILE,
    )

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


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():
    """
    Load the saved maintenance model package.
    """

    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            "Maintenance prediction model has not "
            f"been trained yet: {MODEL_FILE}"
        )

    package = joblib.load(
        MODEL_FILE
    )

    if isinstance(package, dict):
        return package

    # Compatibility fallback
    return {
        "model": package,
        "features": FEATURES,
        "target": TARGET,
    }


# ============================================================
# PREPARE SINGLE RECORD
# ============================================================

def prepare_record(record):
    """
    Convert one asset-monitoring record into the model's
    required feature format.
    """

    values = {}

    for feature in FEATURES:

        value = record.get(
            feature,
            0,
        )

        try:
            value = float(
                value
            )

            if not np.isfinite(
                value
            ):
                value = 0.0

        except (
            TypeError,
            ValueError,
        ):
            value = 0.0

        values[feature] = value

    return pd.DataFrame(
        [values],
        columns=FEATURES,
    )


# ============================================================
# MAINTENANCE PREDICTION
# ============================================================

def predict_maintenance(record):
    """
    Predict whether a single asset reading requires
    maintenance.

    Returns:
    - maintenance_required
    - maintenance_probability
    - normal_probability
    - risk_level
    """

    package = load_model()

    model = package["model"]

    features = package.get(
        "features",
        FEATURES,
    )

    prepared = prepare_record(
        record
    )

    prepared = prepared[
        features
    ]

    prediction = int(
        model.predict(
            prepared
        )[0]
    )

    probabilities = (
        model.predict_proba(
            prepared
        )[0]
    )

    class_probability = {
        int(class_name): float(
            probability
        )
        for class_name, probability
        in zip(
            model.classes_,
            probabilities,
        )
    }

    maintenance_probability = (
        class_probability.get(
            1,
            0.0,
        )
    )

    normal_probability = (
        class_probability.get(
            0,
            0.0,
        )
    )

    if maintenance_probability >= 0.80:
        risk_level = "CRITICAL"

    elif maintenance_probability >= 0.60:
        risk_level = "HIGH"

    elif maintenance_probability >= 0.35:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"

    return {
        "maintenance_required":
            prediction,

        "maintenance_probability":
            round(
                maintenance_probability,
                4,
            ),

        "maintenance_probability_percent":
            round(
                maintenance_probability
                * 100,
                2,
            ),

        "normal_probability":
            round(
                normal_probability,
                4,
            ),

        "risk_level":
            risk_level,
    }


# ============================================================
# PREDICT DATAFRAME
# ============================================================

def predict_dataframe(
    dataframe
):
    """
    Add maintenance predictions to a DataFrame.
    """

    if dataframe.empty:
        return dataframe.copy()

    package = load_model()

    model = package["model"]

    features = package.get(
        "features",
        FEATURES,
    )

    df = dataframe.copy()

    X = df[
        features
    ].copy()

    for column in features:
        X[column] = pd.to_numeric(
            X[column],
            errors="coerce",
        ).fillna(0.0)

    predictions = model.predict(
        X
    )

    probabilities = model.predict_proba(
        X
    )

    class_indexes = {
        int(class_name): index
        for index, class_name
        in enumerate(
            model.classes_
        )
    }

    maintenance_index = (
        class_indexes.get(
            1
        )
    )

    if maintenance_index is None:
        maintenance_probabilities = (
            np.zeros(
                len(df)
            )
        )

    else:
        maintenance_probabilities = (
            probabilities[
                :,
                maintenance_index
            ]
        )

    df[
        "predicted_maintenance_required"
    ] = predictions.astype(int)

    df[
        "maintenance_probability"
    ] = maintenance_probabilities

    df[
        "maintenance_probability_percent"
    ] = (
        maintenance_probabilities
        * 100
    ).round(2)

    def probability_to_risk(
        probability
    ):
        if probability >= 0.80:
            return "CRITICAL"

        if probability >= 0.60:
            return "HIGH"

        if probability >= 0.35:
            return "MEDIUM"

        return "LOW"

    df[
        "maintenance_risk_level"
    ] = [
        probability_to_risk(
            probability
        )
        for probability
        in maintenance_probabilities
    ]

    return df


# ============================================================
# GET METRICS
# ============================================================

def get_model_metrics():
    """
    Return saved maintenance-model evaluation metrics.
    """

    if not METRICS_FILE.exists():
        return {
            "model_ready": False,
            "message": (
                "Maintenance model metrics "
                "are not available."
            ),
        }

    with open(
        METRICS_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        metrics = json.load(
            file
        )

    metrics[
        "model_ready"
    ] = MODEL_FILE.exists()

    return metrics


# ============================================================
# COMMAND-LINE TRAINING
# ============================================================

def main():
    print()
    print(
        "FacilityOps AI - Milestone 2"
    )
    print(
        "Predictive Maintenance Model"
    )
    print()

    (
        model,
        metrics,
        X_test,
        y_test,
        predictions,
        probabilities,
    ) = train_model()

    save_model(
        model,
        metrics,
    )

    print(
        "Maintenance prediction model "
        "trained successfully."
    )

    print()

    print(
        f"Dataset Records : "
        f"{metrics['records']}"
    )

    print(
        f"Training Records: "
        f"{metrics['training_records']}"
    )

    print(
        f"Testing Records : "
        f"{metrics['testing_records']}"
    )

    print()

    print(
        "Class Distribution"
    )

    print(
        "------------------"
    )

    print(
        f"Normal               : "
        f"{metrics['normal_records']}"
    )

    print(
        f"Maintenance Required : "
        f"{metrics['maintenance_required_records']}"
    )

    print()

    print(
        "Model Evaluation"
    )

    print(
        "----------------"
    )

    print(
        f"Accuracy : "
        f"{metrics['accuracy'] * 100:.2f}%"
    )

    print(
        f"Precision: "
        f"{metrics['precision'] * 100:.2f}%"
    )

    print(
        f"Recall   : "
        f"{metrics['recall'] * 100:.2f}%"
    )

    print(
        f"F1 Score : "
        f"{metrics['f1_score'] * 100:.2f}%"
    )

    print()

    print(
        "Confusion Matrix"
    )

    print(
        "----------------"
    )

    print(
        np.array(
            metrics[
                "confusion_matrix"
            ]
        )
    )

    print()

    print(
        "Feature Importance"
    )

    print(
        "------------------"
    )

    sorted_features = sorted(
        metrics[
            "feature_importance"
        ].items(),
        key=lambda item:
            item[1],
        reverse=True,
    )

    for feature, importance in sorted_features:
        print(
            f"{feature:22s}: "
            f"{importance:.4f}"
        )

    print()

    print(
        "Model saved to:"
    )

    print(
        MODEL_FILE
    )

    print()

    print(
        "Metrics saved to:"
    )

    print(
        METRICS_FILE
    )

    print()

    print(
        "Note: Evaluation is based on "
        "held-out simulated asset-monitoring data."
    )

    print()


if __name__ == "__main__":
    main()