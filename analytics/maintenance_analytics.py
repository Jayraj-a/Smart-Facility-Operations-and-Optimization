"""
FacilityOps AI
Milestone 2 - Maintenance Analytics

Provides:
- Asset monitoring analytics
- Equipment health scoring
- Health classification
- Asset-level summaries
- Maintenance statistics
- Building-level maintenance analytics
"""

from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "milestone2_asset_dataset.csv"
)


# ============================================================
# CONSTANTS
# ============================================================

HEALTH_EXCELLENT = 85
HEALTH_GOOD = 70
HEALTH_WARNING = 50


# ============================================================
# DATA LOADING
# ============================================================

def load_maintenance_data():
    """
    Load the Milestone 2 asset-monitoring dataset.
    """

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Maintenance dataset not found: {DATA_FILE}"
        )

    dataframe = pd.read_csv(DATA_FILE)

    if "timestamp" in dataframe.columns:
        dataframe["timestamp"] = pd.to_datetime(
            dataframe["timestamp"],
            errors="coerce",
        )

    return dataframe


# ============================================================
# SAFE NUMBER
# ============================================================

def safe_float(value, default=0.0):
    """
    Safely convert a value to float.
    """

    try:
        number = float(value)

        if np.isnan(number):
            return default

        return number

    except (TypeError, ValueError):
        return default


# ============================================================
# HEALTH STATUS
# ============================================================

def health_status_from_score(score):
    """
    Convert a 0-100 equipment health score into a status.
    """

    score = safe_float(score)

    if score >= HEALTH_EXCELLENT:
        return "EXCELLENT"

    if score >= HEALTH_GOOD:
        return "GOOD"

    if score >= HEALTH_WARNING:
        return "WARNING"

    return "CRITICAL"


# ============================================================
# SENSOR RISK
# ============================================================

def calculate_sensor_risk(
    temperature_c,
    vibration_mm_s,
    pressure_bar,
    power_kw,
):
    """
    Produce a simple condition-risk score based on
    equipment sensor measurements.

    Higher risk means poorer equipment condition.
    """

    risk = 0.0

    temperature = safe_float(
        temperature_c
    )

    vibration = safe_float(
        vibration_mm_s
    )

    pressure = safe_float(
        pressure_bar
    )

    power = safe_float(
        power_kw
    )

    # Temperature risk
    if temperature > 80:
        risk += 25

    elif temperature > 70:
        risk += 15

    elif temperature > 60:
        risk += 5

    # Vibration risk
    if vibration > 5.0:
        risk += 35

    elif vibration > 4.0:
        risk += 25

    elif vibration > 3.0:
        risk += 10

    # Pressure risk
    if pressure < 3.0 or pressure > 8.0:
        risk += 20

    elif pressure < 4.0 or pressure > 7.0:
        risk += 10

    # Power risk
    if power > 90:
        risk += 20

    elif power > 70:
        risk += 10

    return float(
        np.clip(
            risk,
            0,
            100,
        )
    )


# ============================================================
# EQUIPMENT HEALTH SCORE
# ============================================================

def calculate_equipment_health_score(record):
    """
    Calculate an equipment health score from asset-monitoring
    information.

    The result is between 0 and 100.

    Higher score = healthier asset.
    """

    sensor_risk = calculate_sensor_risk(
        record.get(
            "temperature_c",
            0,
        ),
        record.get(
            "vibration_mm_s",
            0,
        ),
        record.get(
            "pressure_bar",
            0,
        ),
        record.get(
            "power_kw",
            0,
        ),
    )

    age_years = safe_float(
        record.get(
            "age_years",
            0,
        )
    )

    operating_hours = safe_float(
        record.get(
            "operating_hours",
            0,
        )
    )

    days_since_service = safe_float(
        record.get(
            "days_since_service",
            0,
        )
    )

    abnormal_behavior = int(
        safe_float(
            record.get(
                "abnormal_behavior",
                0,
            )
        )
    )

    score = 100.0

    # --------------------------------------------------------
    # SENSOR CONDITION
    # --------------------------------------------------------

    score -= sensor_risk * 0.55

    # --------------------------------------------------------
    # AGE
    # --------------------------------------------------------

    if age_years > 3:
        score -= min(
            (age_years - 3) * 1.5,
            12,
        )

    # --------------------------------------------------------
    # OPERATING HOURS
    # --------------------------------------------------------

    if operating_hours > 5000:
        score -= 8

    elif operating_hours > 3500:
        score -= 4

    # --------------------------------------------------------
    # SERVICE HISTORY
    # --------------------------------------------------------

    if days_since_service > 180:
        score -= 15

    elif days_since_service > 120:
        score -= 8

    elif days_since_service > 90:
        score -= 3

    # --------------------------------------------------------
    # ABNORMAL BEHAVIOUR
    # --------------------------------------------------------

    if abnormal_behavior == 1:
        score -= 18

    return round(
        float(
            np.clip(
                score,
                0,
                100,
            )
        ),
        2,
    )


# ============================================================
# ENRICH HEALTH DATA
# ============================================================

def add_health_scores(dataframe):
    """
    Calculate operational health scores for every reading.

    Existing generated health scores are preserved under
    generated_health_score for comparison.
    """

    df = dataframe.copy()

    if "health_score" in df.columns:
        df["generated_health_score"] = (
            df["health_score"]
        )

    df["equipment_health_score"] = df.apply(
        lambda row:
            calculate_equipment_health_score(
                row.to_dict()
            ),
        axis=1,
    )

    df["equipment_health_status"] = (
        df[
            "equipment_health_score"
        ].apply(
            health_status_from_score
        )
    )

    return df


# ============================================================
# FILTER DATA
# ============================================================

def filter_maintenance_data(
    dataframe,
    building=None,
    block=None,
    asset_id=None,
    asset_type=None,
):
    """
    Filter maintenance data by facility location or asset.
    """

    df = dataframe.copy()

    if building:
        df = df[
            df["building_name"]
            == building
        ]

    if block:
        df = df[
            df["block_name"]
            == block
        ]

    if asset_id:
        df = df[
            df["asset_id"]
            == asset_id
        ]

    if asset_type:
        df = df[
            df["asset_type"]
            == asset_type
        ]

    return df


# ============================================================
# LATEST ASSET READINGS
# ============================================================

def get_latest_asset_readings(dataframe):
    """
    Return the latest monitoring record for every asset.
    """

    if dataframe.empty:
        return dataframe.copy()

    df = dataframe.copy()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
    )

    df = df.sort_values(
        "timestamp"
    )

    latest = (
        df.groupby(
            "asset_id",
            as_index=False,
        )
        .tail(1)
        .copy()
    )

    latest = latest.sort_values(
        "asset_id"
    )

    return latest


# ============================================================
# ASSET SUMMARY
# ============================================================

def calculate_asset_summary(dataframe):
    """
    Calculate high-level asset monitoring KPIs.
    """

    if dataframe.empty:
        return {
            "assets_monitored": 0,
            "average_health_score": 0.0,
            "excellent_assets": 0,
            "good_assets": 0,
            "warning_assets": 0,
            "critical_assets": 0,
            "maintenance_required": 0,
            "abnormal_assets": 0,
        }

    scored = add_health_scores(
        dataframe
    )

    latest = get_latest_asset_readings(
        scored
    )

    health_counts = (
        latest[
            "equipment_health_status"
        ]
        .value_counts()
        .to_dict()
    )

    return {
        "assets_monitored":
            int(
                latest[
                    "asset_id"
                ].nunique()
            ),

        "average_health_score":
            round(
                safe_float(
                    latest[
                        "equipment_health_score"
                    ].mean()
                ),
                2,
            ),

        "excellent_assets":
            int(
                health_counts.get(
                    "EXCELLENT",
                    0,
                )
            ),

        "good_assets":
            int(
                health_counts.get(
                    "GOOD",
                    0,
                )
            ),

        "warning_assets":
            int(
                health_counts.get(
                    "WARNING",
                    0,
                )
            ),

        "critical_assets":
            int(
                health_counts.get(
                    "CRITICAL",
                    0,
                )
            ),

        "maintenance_required":
            int(
                (
                    latest[
                        "maintenance_required"
                    ]
                    == 1
                ).sum()
            ),

        "abnormal_assets":
            int(
                (
                    latest[
                        "abnormal_behavior"
                    ]
                    == 1
                ).sum()
            ),
    }


# ============================================================
# ASSET HEALTH TABLE
# ============================================================

def get_asset_health_table(dataframe):
    """
    Return latest health information for all assets.
    """

    if dataframe.empty:
        return []

    scored = add_health_scores(
        dataframe
    )

    latest = get_latest_asset_readings(
        scored
    )

    results = []

    for _, row in latest.iterrows():

        results.append(
            {
                "asset_id":
                    row.get(
                        "asset_id"
                    ),

                "asset_name":
                    row.get(
                        "asset_name"
                    ),

                "asset_type":
                    row.get(
                        "asset_type"
                    ),

                "building_name":
                    row.get(
                        "building_name"
                    ),

                "block_name":
                    row.get(
                        "block_name"
                    ),

                "timestamp":
                    (
                        row["timestamp"].isoformat()
                        if pd.notna(
                            row["timestamp"]
                        )
                        else None
                    ),

                "temperature_c":
                    round(
                        safe_float(
                            row.get(
                                "temperature_c"
                            )
                        ),
                        2,
                    ),

                "vibration_mm_s":
                    round(
                        safe_float(
                            row.get(
                                "vibration_mm_s"
                            )
                        ),
                        2,
                    ),

                "pressure_bar":
                    round(
                        safe_float(
                            row.get(
                                "pressure_bar"
                            )
                        ),
                        2,
                    ),

                "power_kw":
                    round(
                        safe_float(
                            row.get(
                                "power_kw"
                            )
                        ),
                        2,
                    ),

                "operating_hours":
                    round(
                        safe_float(
                            row.get(
                                "operating_hours"
                            )
                        ),
                        2,
                    ),

                "days_since_service":
                    round(
                        safe_float(
                            row.get(
                                "days_since_service"
                            )
                        ),
                        2,
                    ),

                "health_score":
                    round(
                        safe_float(
                            row.get(
                                "equipment_health_score"
                            )
                        ),
                        2,
                    ),

                "health_status":
                    row.get(
                        "equipment_health_status"
                    ),

                "maintenance_required":
                    int(
                        safe_float(
                            row.get(
                                "maintenance_required"
                            )
                        )
                    ),

                "days_to_maintenance":
                    int(
                        safe_float(
                            row.get(
                                "days_to_maintenance"
                            )
                        )
                    ),
            }
        )

    return results


# ============================================================
# BUILDING HEALTH COMPARISON
# ============================================================

def get_building_health_comparison(
    dataframe
):
    """
    Calculate average equipment health by building.
    """

    if dataframe.empty:
        return []

    scored = add_health_scores(
        dataframe
    )

    latest = get_latest_asset_readings(
        scored
    )

    grouped = (
        latest.groupby(
            "building_name",
            as_index=False,
        )
        .agg(
            assets_monitored=(
                "asset_id",
                "nunique",
            ),
            average_health_score=(
                "equipment_health_score",
                "mean",
            ),
            average_temperature=(
                "temperature_c",
                "mean",
            ),
            average_vibration=(
                "vibration_mm_s",
                "mean",
            ),
        )
    )

    results = []

    for _, row in grouped.iterrows():

        average_health = round(
            safe_float(
                row[
                    "average_health_score"
                ]
            ),
            2,
        )

        results.append(
            {
                "building_name":
                    row[
                        "building_name"
                    ],

                "assets_monitored":
                    int(
                        row[
                            "assets_monitored"
                        ]
                    ),

                "average_health_score":
                    average_health,

                "health_status":
                    health_status_from_score(
                        average_health
                    ),

                "average_temperature":
                    round(
                        safe_float(
                            row[
                                "average_temperature"
                            ]
                        ),
                        2,
                    ),

                "average_vibration":
                    round(
                        safe_float(
                            row[
                                "average_vibration"
                            ]
                        ),
                        2,
                    ),
            }
        )

    return results


# ============================================================
# MAINTENANCE PRIORITY
# ============================================================

def maintenance_priority(
    health_score,
    maintenance_required=0,
):
    """
    Determine maintenance priority from equipment condition.
    """

    score = safe_float(
        health_score
    )

    required = int(
        safe_float(
            maintenance_required
        )
    )

    if score < 50:
        return "CRITICAL"

    if required == 1:
        return "HIGH"

    if score < 70:
        return "HIGH"

    if score < 85:
        return "MEDIUM"

    return "LOW"


# ============================================================
# MAINTENANCE SCHEDULE
# ============================================================

def get_maintenance_schedule(
    dataframe
):
    """
    Generate a maintenance schedule from latest asset condition.
    """

    if dataframe.empty:
        return []

    scored = add_health_scores(
        dataframe
    )

    latest = get_latest_asset_readings(
        scored
    )

    schedule = []

    for _, row in latest.iterrows():

        health_score = safe_float(
            row.get(
                "equipment_health_score"
            )
        )

        required = int(
            safe_float(
                row.get(
                    "maintenance_required"
                )
            )
        )

        priority = maintenance_priority(
            health_score,
            required,
        )

        # --------------------------------------------
        # Recommended maintenance interval
        # --------------------------------------------

        if priority == "CRITICAL":
            days_until_service = 1

        elif priority == "HIGH":
            days_until_service = 7

        elif priority == "MEDIUM":
            days_until_service = 30

        else:
            days_until_service = 90

        timestamp = pd.to_datetime(
            row.get(
                "timestamp"
            ),
            errors="coerce",
        )

        if pd.notna(timestamp):
            recommended_date = (
                timestamp
                + pd.Timedelta(
                    days=days_until_service
                )
            )

            recommended_date = (
                recommended_date
                .date()
                .isoformat()
            )

        else:
            recommended_date = None

        schedule.append(
            {
                "asset_id":
                    row.get(
                        "asset_id"
                    ),

                "asset_name":
                    row.get(
                        "asset_name"
                    ),

                "asset_type":
                    row.get(
                        "asset_type"
                    ),

                "building_name":
                    row.get(
                        "building_name"
                    ),

                "block_name":
                    row.get(
                        "block_name"
                    ),

                "health_score":
                    round(
                        health_score,
                        2,
                    ),

                "health_status":
                    health_status_from_score(
                        health_score
                    ),

                "priority":
                    priority,

                "recommended_maintenance_date":
                    recommended_date,

                "days_until_service":
                    days_until_service,

                "maintenance_required":
                    required,
            }
        )

    priority_order = {
        "CRITICAL": 0,
        "HIGH": 1,
        "MEDIUM": 2,
        "LOW": 3,
    }

    schedule.sort(
        key=lambda item: (
            priority_order.get(
                item["priority"],
                99,
            ),
            item["health_score"],
        )
    )

    return schedule


# ============================================================
# COMMAND-LINE TEST
# ============================================================

def main():
    dataframe = load_maintenance_data()

    print()
    print(
        "FacilityOps AI - Milestone 2"
    )
    print(
        "Maintenance Analytics"
    )
    print()

    print(
        f"Dataset rows: {len(dataframe)}"
    )

    print(
        f"Assets monitored: "
        f"{dataframe['asset_id'].nunique()}"
    )

    print()

    summary = calculate_asset_summary(
        dataframe
    )

    print(
        "Equipment Health Summary"
    )

    print(
        "------------------------"
    )

    for key, value in summary.items():
        print(
            f"{key}: {value}"
        )

    print()

    print(
        "Asset Health"
    )

    print(
        "------------"
    )

    health_table = (
        get_asset_health_table(
            dataframe
        )
    )

    for asset in health_table:
        print(
            f"{asset['asset_id']} | "
            f"{asset['asset_name']} | "
            f"Health: {asset['health_score']} | "
            f"{asset['health_status']}"
        )

    print()

    print(
        "Maintenance Schedule"
    )

    print(
        "--------------------"
    )

    schedule = (
        get_maintenance_schedule(
            dataframe
        )
    )

    for item in schedule:
        print(
            f"{item['asset_id']} | "
            f"{item['asset_name']} | "
            f"{item['priority']} | "
            f"{item['recommended_maintenance_date']}"
        )

    print()


if __name__ == "__main__":
    main()