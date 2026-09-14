from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# FACILITYOPS AI
# MILESTONE 3 - OCCUPANCY ANALYTICS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "milestone3_occupancy_dataset.csv"
)


# ============================================================
# BASIC HELPERS
# ============================================================

def safe_float(value, default=0.0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value, default=0):
    try:
        if pd.isna(value):
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


# ============================================================
# LOAD OCCUPANCY DATA
# ============================================================

def load_occupancy_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Occupancy dataset not found: {DATA_FILE}"
        )

    dataframe = pd.read_csv(DATA_FILE)

    dataframe["timestamp"] = pd.to_datetime(
        dataframe["timestamp"],
        errors="coerce",
    )

    dataframe = dataframe.dropna(
        subset=["timestamp"]
    )

    dataframe = dataframe.sort_values(
        "timestamp"
    ).reset_index(drop=True)

    return dataframe


# ============================================================
# FILTER OCCUPANCY DATA
# ============================================================

def filter_occupancy_data(
    dataframe,
    facility_id=None,
    building_name=None,
    block_name=None,
    space_id=None,
    start_time=None,
    end_time=None,
):
    filtered = dataframe.copy()

    if facility_id:
        filtered = filtered[
            filtered["facility_id"] == facility_id
        ]

    if building_name:
        filtered = filtered[
            filtered["building_name"] == building_name
        ]

    if block_name:
        filtered = filtered[
            filtered["block_name"] == block_name
        ]

    if space_id:
        filtered = filtered[
            filtered["space_id"] == space_id
        ]

    if start_time is not None:
        start_time = pd.to_datetime(start_time)

        filtered = filtered[
            filtered["timestamp"] >= start_time
        ]

    if end_time is not None:
        end_time = pd.to_datetime(end_time)

        filtered = filtered[
            filtered["timestamp"] <= end_time
        ]

    return filtered.reset_index(drop=True)


# ============================================================
# GET LATEST READING FOR EACH SPACE
# ============================================================

def get_latest_space_readings(dataframe):
    if dataframe.empty:
        return dataframe.copy()

    latest = (
        dataframe
        .sort_values("timestamp")
        .groupby(
            "space_id",
            as_index=False,
        )
        .tail(1)
        .sort_values(
            [
                "building_name",
                "block_name",
                "space_name",
            ]
        )
        .reset_index(drop=True)
    )

    return latest


# ============================================================
# OVERALL OCCUPANCY SUMMARY
# ============================================================

def calculate_occupancy_summary(dataframe):
    if dataframe.empty:
        return {
            "spaces_monitored": 0,
            "total_capacity": 0,
            "current_occupancy": 0,
            "available_capacity": 0,
            "current_utilization_percent": 0.0,
            "average_utilization_percent": 0.0,
            "peak_occupancy": 0,
            "overcrowded_spaces": 0,
            "underused_spaces": 0,
            "high_utilization_spaces": 0,
        }

    latest = get_latest_space_readings(
        dataframe
    )

    total_capacity = int(
        latest["capacity"].sum()
    )

    current_occupancy = int(
        latest["occupancy_count"].sum()
    )

    available_capacity = int(
        latest["available_capacity"].sum()
    )

    if total_capacity > 0:
        current_utilization = (
            current_occupancy
            / total_capacity
            * 100
        )
    else:
        current_utilization = 0.0

    average_utilization = safe_float(
        dataframe[
            "utilization_percent"
        ].mean()
    )

    peak_occupancy = safe_int(
        dataframe[
            "occupancy_count"
        ].max()
    )

    overcrowded_spaces = int(
        (
            latest["occupancy_count"]
            > latest["capacity"]
        ).sum()
    )

    underused_spaces = int(
        (
            latest["utilization_percent"]
            < 15
        ).sum()
    )

    high_utilization_spaces = int(
        (
            latest["utilization_percent"]
            >= 75
        ).sum()
    )

    return {
        "spaces_monitored": int(
            latest["space_id"].nunique()
        ),
        "total_capacity": total_capacity,
        "current_occupancy": current_occupancy,
        "available_capacity": available_capacity,
        "current_utilization_percent": round(
            current_utilization,
            2,
        ),
        "average_utilization_percent": round(
            average_utilization,
            2,
        ),
        "peak_occupancy": peak_occupancy,
        "overcrowded_spaces": overcrowded_spaces,
        "underused_spaces": underused_spaces,
        "high_utilization_spaces": (
            high_utilization_spaces
        ),
    }


# ============================================================
# SPACE UTILIZATION TABLE
# ============================================================

def get_space_utilization_table(dataframe):
    latest = get_latest_space_readings(
        dataframe
    )

    if latest.empty:
        return []

    records = []

    for _, row in latest.iterrows():

        utilization = safe_float(
            row.get("utilization_percent")
        )

        if utilization >= 100:
            status = "OVERCROWDED"

        elif utilization >= 75:
            status = "HIGH"

        elif utilization >= 40:
            status = "OPTIMAL"

        elif utilization >= 15:
            status = "LOW"

        else:
            status = "UNDERUSED"

        records.append(
            {
                "facility_id": row[
                    "facility_id"
                ],
                "building_id": row[
                    "building_id"
                ],
                "building_name": row[
                    "building_name"
                ],
                "block_id": row[
                    "block_id"
                ],
                "block_name": row[
                    "block_name"
                ],
                "space_id": row[
                    "space_id"
                ],
                "space_name": row[
                    "space_name"
                ],
                "space_type": row[
                    "space_type"
                ],
                "timestamp": (
                    row["timestamp"]
                    .strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                ),
                "capacity": safe_int(
                    row["capacity"]
                ),
                "occupancy_count": safe_int(
                    row["occupancy_count"]
                ),
                "available_capacity": safe_int(
                    row[
                        "available_capacity"
                    ]
                ),
                "utilization_percent": round(
                    utilization,
                    2,
                ),
                "utilization_status": status,
                "overcrowded": bool(
                    safe_int(
                        row["overcrowded"]
                    )
                ),
            }
        )

    return records


# ============================================================
# BUILDING OCCUPANCY COMPARISON
# ============================================================

def get_building_occupancy_comparison(
    dataframe,
):
    latest = get_latest_space_readings(
        dataframe
    )

    if latest.empty:
        return []

    records = []

    for building_name, group in latest.groupby(
        "building_name"
    ):
        total_capacity = int(
            group["capacity"].sum()
        )

        occupancy = int(
            group["occupancy_count"].sum()
        )

        available = max(
            0,
            total_capacity - occupancy,
        )

        if total_capacity > 0:
            utilization = (
                occupancy
                / total_capacity
                * 100
            )
        else:
            utilization = 0.0

        records.append(
            {
                "building_name": building_name,
                "spaces": int(
                    group[
                        "space_id"
                    ].nunique()
                ),
                "total_capacity": (
                    total_capacity
                ),
                "occupancy_count": occupancy,
                "available_capacity": available,
                "utilization_percent": round(
                    utilization,
                    2,
                ),
                "overcrowded_spaces": int(
                    (
                        group[
                            "occupancy_count"
                        ]
                        > group["capacity"]
                    ).sum()
                ),
            }
        )

    records.sort(
        key=lambda item: item[
            "utilization_percent"
        ],
        reverse=True,
    )

    return records


# ============================================================
# OCCUPANCY BY HOUR
# ============================================================

def get_hourly_occupancy_pattern(dataframe):
    if dataframe.empty:
        return []

    working = dataframe.copy()

    working["hour"] = (
        working["timestamp"].dt.hour
    )

    hourly = (
        working
        .groupby("hour")
        .agg(
            average_occupancy=(
                "occupancy_count",
                "mean",
            ),
            average_utilization=(
                "utilization_percent",
                "mean",
            ),
            peak_occupancy=(
                "occupancy_count",
                "max",
            ),
        )
        .reset_index()
    )

    records = []

    for _, row in hourly.iterrows():
        records.append(
            {
                "hour": safe_int(
                    row["hour"]
                ),
                "average_occupancy": round(
                    safe_float(
                        row[
                            "average_occupancy"
                        ]
                    ),
                    2,
                ),
                "average_utilization_percent":
                    round(
                        safe_float(
                            row[
                                "average_utilization"
                            ]
                        ),
                        2,
                    ),
                "peak_occupancy": safe_int(
                    row[
                        "peak_occupancy"
                    ]
                ),
            }
        )

    return records


# ============================================================
# PEAK USAGE HOURS
# ============================================================

def get_peak_usage_hours(
    dataframe,
    top_n=5,
):
    hourly = get_hourly_occupancy_pattern(
        dataframe
    )

    hourly.sort(
        key=lambda item: item[
            "average_utilization_percent"
        ],
        reverse=True,
    )

    return hourly[:top_n]


# ============================================================
# OCCUPANCY HEATMAP DATA
# ============================================================

def get_occupancy_heatmap(dataframe):
    if dataframe.empty:
        return []

    working = dataframe.copy()

    working["hour"] = (
        working["timestamp"].dt.hour
    )

    heatmap = (
        working
        .groupby(
            [
                "space_id",
                "space_name",
                "building_name",
                "hour",
            ]
        )
        .agg(
            average_utilization=(
                "utilization_percent",
                "mean",
            ),
            average_occupancy=(
                "occupancy_count",
                "mean",
            ),
        )
        .reset_index()
    )

    records = []

    for _, row in heatmap.iterrows():
        records.append(
            {
                "space_id": row[
                    "space_id"
                ],
                "space_name": row[
                    "space_name"
                ],
                "building_name": row[
                    "building_name"
                ],
                "hour": safe_int(
                    row["hour"]
                ),
                "average_utilization_percent":
                    round(
                        safe_float(
                            row[
                                "average_utilization"
                            ]
                        ),
                        2,
                    ),
                "average_occupancy": round(
                    safe_float(
                        row[
                            "average_occupancy"
                        ]
                    ),
                    2,
                ),
            }
        )

    return records


# ============================================================
# OVERCROWDING EVENTS
# ============================================================

def get_overcrowding_events(
    dataframe,
    limit=100,
):
    if dataframe.empty:
        return []

    events = dataframe[
        (
            dataframe["overcrowded"] == 1
        )
        |
        (
            dataframe[
                "occupancy_count"
            ]
            > dataframe["capacity"]
        )
    ].copy()

    events = events.sort_values(
        "timestamp",
        ascending=False,
    ).head(limit)

    records = []

    for _, row in events.iterrows():

        records.append(
            {
                "space_id": row[
                    "space_id"
                ],
                "space_name": row[
                    "space_name"
                ],
                "space_type": row[
                    "space_type"
                ],
                "building_name": row[
                    "building_name"
                ],
                "block_name": row[
                    "block_name"
                ],
                "timestamp": (
                    row["timestamp"]
                    .strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                ),
                "capacity": safe_int(
                    row["capacity"]
                ),
                "occupancy_count": safe_int(
                    row[
                        "occupancy_count"
                    ]
                ),
                "utilization_percent": round(
                    safe_float(
                        row[
                            "utilization_percent"
                        ]
                    ),
                    2,
                ),
                "severity": (
                    "CRITICAL"
                    if safe_float(
                        row[
                            "utilization_percent"
                        ]
                    ) >= 110
                    else "HIGH"
                ),
            }
        )

    return records


# ============================================================
# UNDERUSED SPACES
# ============================================================

def get_underused_spaces(
    dataframe,
    threshold=25.0,
):
    if dataframe.empty:
        return []

    average_usage = (
        dataframe
        .groupby(
            [
                "space_id",
                "space_name",
                "space_type",
                "building_name",
                "block_name",
                "capacity",
            ]
        )
        .agg(
            average_occupancy=(
                "occupancy_count",
                "mean",
            ),
            average_utilization=(
                "utilization_percent",
                "mean",
            ),
        )
        .reset_index()
    )

    average_usage = average_usage[
        average_usage[
            "average_utilization"
        ] < threshold
    ]

    average_usage = average_usage.sort_values(
        "average_utilization"
    )

    records = []

    for _, row in average_usage.iterrows():

        records.append(
            {
                "space_id": row[
                    "space_id"
                ],
                "space_name": row[
                    "space_name"
                ],
                "space_type": row[
                    "space_type"
                ],
                "building_name": row[
                    "building_name"
                ],
                "block_name": row[
                    "block_name"
                ],
                "capacity": safe_int(
                    row["capacity"]
                ),
                "average_occupancy": round(
                    safe_float(
                        row[
                            "average_occupancy"
                        ]
                    ),
                    2,
                ),
                "average_utilization_percent":
                    round(
                        safe_float(
                            row[
                                "average_utilization"
                            ]
                        ),
                        2,
                    ),
                "recommendation":
                    "Review workspace allocation "
                    "or shared-space usage.",
            }
        )

    return records


# ============================================================
# SPACE UTILIZATION INSIGHTS
# ============================================================

def generate_occupancy_insights(dataframe):
    summary = calculate_occupancy_summary(
        dataframe
    )

    peak_hours = get_peak_usage_hours(
        dataframe,
        top_n=3,
    )

    underused = get_underused_spaces(
        dataframe
    )

    overcrowding = get_overcrowding_events(
        dataframe,
        limit=20,
    )

    insights = []

    if peak_hours:
        best = peak_hours[0]

        insights.append(
            {
                "type": "PEAK_USAGE",
                "severity": "INFO",
                "title": "Peak Facility Usage",
                "message": (
                    f"Hour {best['hour']:02d}:00 "
                    f"has the highest average "
                    f"utilization at "
                    f"{best['average_utilization_percent']:.1f}%."
                ),
            }
        )

    if underused:
        insights.append(
            {
                "type": "UNDERUSED_SPACE",
                "severity": "INFO",
                "title": "Underused Spaces Detected",
                "message": (
                    f"{len(underused)} spaces "
                    f"have average utilization "
                    f"below 25%."
                ),
            }
        )

    if overcrowding:
        insights.append(
            {
                "type": "OVERCROWDING",
                "severity": "HIGH",
                "title": "Overcrowding Detected",
                "message": (
                    f"{len(overcrowding)} recent "
                    f"overcrowding events were "
                    f"identified."
                ),
            }
        )

    if (
        summary[
            "current_utilization_percent"
        ]
        < 20
    ):
        insights.append(
            {
                "type": "LOW_UTILIZATION",
                "severity": "INFO",
                "title": "Low Current Utilization",
                "message": (
                    "Current facility utilization "
                    "is below 20%. Space allocation "
                    "can be reviewed."
                ),
            }
        )

    return insights


# ============================================================
# COMMAND-LINE TEST
# ============================================================

def main():
    print()
    print("=" * 60)
    print("FACILITYOPS AI - MILESTONE 3")
    print("OCCUPANCY ANALYTICS")
    print("=" * 60)

    dataframe = load_occupancy_data()

    print()
    print(f"Dataset rows: {len(dataframe)}")

    print(
        "Spaces monitored:",
        dataframe["space_id"].nunique(),
    )

    summary = calculate_occupancy_summary(
        dataframe
    )

    print()
    print("Occupancy Summary")
    print("-" * 60)

    for key, value in summary.items():
        print(f"{key}: {value}")

    print()
    print("Latest Space Utilization")
    print("-" * 60)

    spaces = get_space_utilization_table(
        dataframe
    )

    for space in spaces:
        print(
            f"{space['space_id']} | "
            f"{space['space_name']} | "
            f"Occupancy: "
            f"{space['occupancy_count']}/"
            f"{space['capacity']} | "
            f"Utilization: "
            f"{space['utilization_percent']:.2f}% | "
            f"{space['utilization_status']}"
        )

    print()
    print("Building Occupancy")
    print("-" * 60)

    buildings = (
        get_building_occupancy_comparison(
            dataframe
        )
    )

    for building in buildings:
        print(
            f"{building['building_name']} | "
            f"Occupancy: "
            f"{building['occupancy_count']}/"
            f"{building['total_capacity']} | "
            f"Utilization: "
            f"{building['utilization_percent']:.2f}%"
        )

    print()
    print("Peak Usage Hours")
    print("-" * 60)

    peak_hours = get_peak_usage_hours(
        dataframe
    )

    for item in peak_hours:
        print(
            f"{item['hour']:02d}:00 | "
            f"Average Utilization: "
            f"{item['average_utilization_percent']:.2f}%"
        )

    print()
    print("Underused Spaces")
    print("-" * 60)

    underused = get_underused_spaces(
        dataframe
    )

    if not underused:
        print("No underused spaces detected.")

    for item in underused:
        print(
            f"{item['space_id']} | "
            f"{item['space_name']} | "
            f"Average Utilization: "
            f"{item['average_utilization_percent']:.2f}%"
        )

    print()
    print("Occupancy Insights")
    print("-" * 60)

    insights = generate_occupancy_insights(
        dataframe
    )

    for insight in insights:
        print(
            f"[{insight['severity']}] "
            f"{insight['title']} - "
            f"{insight['message']}"
        )

    print()
    print("=" * 60)
    print(
        "Occupancy analytics completed successfully."
    )
    print("=" * 60)


if __name__ == "__main__":
    main()