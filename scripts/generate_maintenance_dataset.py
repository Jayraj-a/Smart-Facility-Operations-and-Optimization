"""
FacilityOps AI
Milestone 2 - Predictive Maintenance System

Generates a simulated asset-monitoring dataset for facility equipment.

The dataset is used for:
- Asset health monitoring
- Equipment health scoring
- Abnormal equipment behaviour detection
- Maintenance prediction
- Maintenance scheduling
- Maintenance alerts
"""

from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_SEED = 42
DAYS = 30
READINGS_PER_DAY = 24

np.random.seed(RANDOM_SEED)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "milestone2_asset_dataset.csv"
)


# ============================================================
# FACILITY ASSETS
# ============================================================

ASSETS = [
    {
        "asset_id": "AST-001",
        "asset_name": "HVAC Unit 1",
        "asset_type": "HVAC",
        "building_name": "Building A",
        "block_name": "Block A1",
        "age_years": 4,
    },
    {
        "asset_id": "AST-002",
        "asset_name": "Chiller 1",
        "asset_type": "Chiller",
        "building_name": "Building A",
        "block_name": "Block A2",
        "age_years": 6,
    },
    {
        "asset_id": "AST-003",
        "asset_name": "Water Pump 1",
        "asset_type": "Pump",
        "building_name": "Building B",
        "block_name": "Block B1",
        "age_years": 3,
    },
    {
        "asset_id": "AST-004",
        "asset_name": "HVAC Unit 2",
        "asset_type": "HVAC",
        "building_name": "Building B",
        "block_name": "Block B2",
        "age_years": 5,
    },
    {
        "asset_id": "AST-005",
        "asset_name": "Generator 1",
        "asset_type": "Generator",
        "building_name": "Building C",
        "block_name": "Block C1",
        "age_years": 7,
    },
    {
        "asset_id": "AST-006",
        "asset_name": "Air Handling Unit 1",
        "asset_type": "AHU",
        "building_name": "Building C",
        "block_name": "Block C2",
        "age_years": 4,
    },
    {
        "asset_id": "AST-007",
        "asset_name": "Elevator Motor 1",
        "asset_type": "Elevator",
        "building_name": "Building A",
        "block_name": "Block A1",
        "age_years": 8,
    },
    {
        "asset_id": "AST-008",
        "asset_name": "Water Pump 2",
        "asset_type": "Pump",
        "building_name": "Building B",
        "block_name": "Block B1",
        "age_years": 2,
    },
]


# ============================================================
# ASSET BASELINES
# ============================================================

ASSET_BASELINES = {
    "HVAC": {
        "temperature": 58.0,
        "vibration": 2.2,
        "pressure": 5.5,
        "power": 42.0,
    },
    "Chiller": {
        "temperature": 52.0,
        "vibration": 2.0,
        "pressure": 6.2,
        "power": 58.0,
    },
    "Pump": {
        "temperature": 48.0,
        "vibration": 2.5,
        "pressure": 5.8,
        "power": 24.0,
    },
    "Generator": {
        "temperature": 62.0,
        "vibration": 3.0,
        "pressure": 5.0,
        "power": 65.0,
    },
    "AHU": {
        "temperature": 50.0,
        "vibration": 2.1,
        "pressure": 5.4,
        "power": 30.0,
    },
    "Elevator": {
        "temperature": 55.0,
        "vibration": 2.8,
        "pressure": 5.1,
        "power": 35.0,
    },
}


# ============================================================
# HEALTH SCORE
# ============================================================

def calculate_health_score(
    temperature_c,
    vibration_mm_s,
    pressure_bar,
    power_kw,
    baseline,
    age_years,
    days_since_service,
):
    """
    Calculate a simulated equipment health score from 0 to 100.

    Higher score = healthier equipment.
    """

    score = 100.0

    temperature_ratio = (
        temperature_c / baseline["temperature"]
    )

    vibration_ratio = (
        vibration_mm_s / baseline["vibration"]
    )

    pressure_difference = abs(
        pressure_bar - baseline["pressure"]
    )

    power_ratio = (
        power_kw / baseline["power"]
    )

    # Temperature penalty
    if temperature_ratio > 1.10:
        score -= (
            temperature_ratio - 1.10
        ) * 100

    # Vibration penalty
    if vibration_ratio > 1.15:
        score -= (
            vibration_ratio - 1.15
        ) * 45

    # Pressure penalty
    score -= pressure_difference * 4

    # Power-consumption penalty
    if power_ratio > 1.15:
        score -= (
            power_ratio - 1.15
        ) * 35

    # Asset age penalty
    score -= max(
        age_years - 3,
        0,
    ) * 1.2

    # Service overdue penalty
    if days_since_service > 120:
        score -= (
            days_since_service - 120
        ) * 0.05

    return float(
        np.clip(
            score,
            0,
            100,
        )
    )


# ============================================================
# HEALTH CATEGORY
# ============================================================

def get_health_status(score):
    if score >= 85:
        return "EXCELLENT"

    if score >= 70:
        return "GOOD"

    if score >= 50:
        return "WARNING"

    return "CRITICAL"


# ============================================================
# MAINTENANCE REQUIREMENT
# ============================================================

def get_maintenance_requirement(
    health_score,
    vibration,
    temperature,
    baseline,
):
    """
    Produce a simulated maintenance target.

    1 = maintenance required
    0 = normal operation
    """

    if health_score < 55:
        return 1

    if vibration > baseline["vibration"] * 1.80:
        return 1

    if temperature > baseline["temperature"] * 1.35:
        return 1

    return 0


# ============================================================
# DATASET GENERATOR
# ============================================================

def generate_dataset():
    records = []

    timestamps = pd.date_range(
        start="2026-01-01 00:00:00",
        periods=DAYS * READINGS_PER_DAY,
        freq="h",
    )

    for asset in ASSETS:
        baseline = ASSET_BASELINES[
            asset["asset_type"]
        ]

        operating_hours = np.random.randint(
            1000,
            6000,
        )

        initial_service_days = np.random.randint(
            10,
            100,
        )

        for index, timestamp in enumerate(
            timestamps
        ):
            hour = timestamp.hour

            # ------------------------------------------------
            # OPERATING LOAD
            # ------------------------------------------------

            if 8 <= hour <= 18:
                load_factor = np.random.uniform(
                    0.75,
                    1.10,
                )
            else:
                load_factor = np.random.uniform(
                    0.35,
                    0.70,
                )

            # ------------------------------------------------
            # NORMAL SENSOR VALUES
            # ------------------------------------------------

            temperature = np.random.normal(
                baseline["temperature"],
                2.5,
            )

            vibration = np.random.normal(
                baseline["vibration"],
                0.25,
            )

            pressure = np.random.normal(
                baseline["pressure"],
                0.30,
            )

            power = np.random.normal(
                baseline["power"] * load_factor,
                baseline["power"] * 0.06,
            )

            runtime_hours = np.random.uniform(
                0.4,
                1.0,
            )

            operating_hours += runtime_hours

            days_since_service = (
                initial_service_days
                + index / 24
            )

            # ------------------------------------------------
            # SIMULATED EQUIPMENT DEGRADATION
            # ------------------------------------------------

            degradation_probability = (
                0.025
                + asset["age_years"] * 0.003
            )

            abnormal_behavior = 0

            if (
                np.random.random()
                < degradation_probability
            ):
                abnormal_behavior = 1

                degradation_strength = (
                    np.random.uniform(
                        1.30,
                        2.00,
                    )
                )

                temperature *= np.random.uniform(
                    1.15,
                    degradation_strength,
                )

                vibration *= np.random.uniform(
                    1.35,
                    degradation_strength,
                )

                power *= np.random.uniform(
                    1.10,
                    1.45,
                )

                pressure += np.random.normal(
                    0,
                    1.0,
                )

            # ------------------------------------------------
            # CLEAN VALUES
            # ------------------------------------------------

            temperature = max(
                temperature,
                1.0,
            )

            vibration = max(
                vibration,
                0.1,
            )

            pressure = max(
                pressure,
                0.5,
            )

            power = max(
                power,
                1.0,
            )

            # ------------------------------------------------
            # HEALTH SCORE
            # ------------------------------------------------

            health_score = calculate_health_score(
                temperature,
                vibration,
                pressure,
                power,
                baseline,
                asset["age_years"],
                days_since_service,
            )

            health_status = get_health_status(
                health_score
            )

            # ------------------------------------------------
            # MAINTENANCE TARGET
            # ------------------------------------------------

            maintenance_required = (
                get_maintenance_requirement(
                    health_score,
                    vibration,
                    temperature,
                    baseline,
                )
            )

            # ------------------------------------------------
            # ESTIMATED DAYS TO MAINTENANCE
            # ------------------------------------------------

            if health_score >= 85:
                days_to_maintenance = np.random.randint(
                    90,
                    181,
                )

            elif health_score >= 70:
                days_to_maintenance = np.random.randint(
                    45,
                    91,
                )

            elif health_score >= 50:
                days_to_maintenance = np.random.randint(
                    7,
                    31,
                )

            else:
                days_to_maintenance = np.random.randint(
                    0,
                    7,
                )

            # ------------------------------------------------
            # RECORD
            # ------------------------------------------------

            records.append(
                {
                    "facility_id": "FAC-001",
                    "facility_name": "FacilityOps Campus",
                    "asset_id": asset["asset_id"],
                    "asset_name": asset["asset_name"],
                    "asset_type": asset["asset_type"],
                    "building_name": asset["building_name"],
                    "block_name": asset["block_name"],
                    "timestamp": timestamp,
                    "temperature_c": round(
                        temperature,
                        2,
                    ),
                    "vibration_mm_s": round(
                        vibration,
                        2,
                    ),
                    "pressure_bar": round(
                        pressure,
                        2,
                    ),
                    "power_kw": round(
                        power,
                        2,
                    ),
                    "runtime_hours": round(
                        runtime_hours,
                        2,
                    ),
                    "operating_hours": round(
                        operating_hours,
                        2,
                    ),
                    "age_years": asset["age_years"],
                    "days_since_service": round(
                        days_since_service,
                        2,
                    ),
                    "health_score": round(
                        health_score,
                        2,
                    ),
                    "health_status": health_status,
                    "abnormal_behavior": abnormal_behavior,
                    "maintenance_required": maintenance_required,
                    "days_to_maintenance": int(
                        days_to_maintenance
                    ),
                }
            )

    return pd.DataFrame(
        records
    )


# ============================================================
# MAIN
# ============================================================

def main():
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe = generate_dataset()

    dataframe.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print()
    print(
        "FacilityOps AI - Milestone 2"
    )
    print(
        "Asset monitoring dataset generated successfully."
    )
    print()

    print(
        f"Dataset path: {OUTPUT_FILE}"
    )

    print(
        f"Rows: {len(dataframe)}"
    )

    print(
        f"Columns: {len(dataframe.columns)}"
    )

    print(
        f"Assets: {dataframe['asset_id'].nunique()}"
    )

    print()

    print(
        "Health Status Distribution:"
    )

    print(
        dataframe[
            "health_status"
        ].value_counts()
    )

    print()

    print(
        "Maintenance Required Distribution:"
    )

    print(
        dataframe[
            "maintenance_required"
        ].value_counts()
    )

    print()

    print(
        "Abnormal Behaviour Distribution:"
    )

    print(
        dataframe[
            "abnormal_behavior"
        ].value_counts()
    )

    print()


if __name__ == "__main__":
    main()