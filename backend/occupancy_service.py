import math

import numpy as np
import pandas as pd

from agents.occupancy_agent import occupancy_agent

from analytics.occupancy_analytics import (
    load_occupancy_data,
    calculate_occupancy_summary,
    get_latest_space_readings,
    get_space_utilization_table,
    get_building_occupancy_comparison,
    get_hourly_occupancy_pattern,
    get_peak_usage_hours,
    get_occupancy_heatmap,
    get_overcrowding_events,
    get_underused_spaces,
    generate_occupancy_insights,
)

from backend.monitoring_db import (
    initialise_monitoring_database,
    save_occupancy_records_batch,
    get_occupancy_records,
    create_occupancy_alert,
    get_occupancy_alerts,
    update_occupancy_alert_status,
)


# ============================================================
# JSON SAFE CONVERSION
# ============================================================

def _json_safe(value):
    """
    Convert pandas / NumPy values into normal Python values
    that FastAPI can safely serialize to JSON.
    """

    if value is None:
        return None

    # NumPy integer -> Python int
    if isinstance(value, np.integer):
        return int(value)

    # NumPy float -> Python float
    if isinstance(value, np.floating):
        number = float(value)

        if math.isnan(number) or math.isinf(number):
            return None

        return number

    # NumPy boolean -> Python bool
    if isinstance(value, np.bool_):
        return bool(value)

    # NumPy datetime -> string
    if isinstance(value, np.datetime64):
        return str(value)

    # Pandas timestamp -> ISO string
    if isinstance(value, pd.Timestamp):
        if pd.isna(value):
            return None

        return value.isoformat()

    # Pandas / Python missing values
    try:
        missing = pd.isna(value)

        if isinstance(missing, (bool, np.bool_)) and missing:
            return None

    except (TypeError, ValueError):
        pass

    # Dictionary
    if isinstance(value, dict):
        return {
            str(key): _json_safe(item)
            for key, item in value.items()
        }

    # List / tuple / set
    if isinstance(value, (list, tuple, set)):
        return [
            _json_safe(item)
            for item in value
        ]

    # NumPy array
    if isinstance(value, np.ndarray):
        return [
            _json_safe(item)
            for item in value.tolist()
        ]

    # Pandas DataFrame
    if isinstance(value, pd.DataFrame):
        return _records_from_dataframe(value)

    # Pandas Series
    if isinstance(value, pd.Series):
        return [
            _json_safe(item)
            for item in value.tolist()
        ]

    # Standard JSON-compatible values
    if isinstance(
        value,
        (
            str,
            int,
            float,
            bool,
        ),
    ):
        return value

    # Final safe fallback
    return str(value)


# ============================================================
# DATA HELPERS
# ============================================================

def _records_from_dataframe(dataframe):
    if dataframe is None or dataframe.empty:
        return []

    clean_df = dataframe.copy()

    # Convert datetime columns to strings
    for column in clean_df.columns:
        if pd.api.types.is_datetime64_any_dtype(
            clean_df[column]
        ):
            clean_df[column] = (
                clean_df[column]
                .astype(str)
            )

    clean_df = clean_df.where(
        clean_df.notna(),
        None,
    )

    records = clean_df.to_dict(
        orient="records"
    )

    return _json_safe(records)


# ============================================================
# LOAD OCCUPANCY DATASET
# ============================================================

def load_occupancy_dataset():
    return load_occupancy_data()


# ============================================================
# SYNCHRONISE OCCUPANCY DATA WITH SQLITE
# ============================================================

def sync_occupancy_data():
    initialise_monitoring_database()

    dataframe = load_occupancy_dataset()

    records = _records_from_dataframe(
        dataframe
    )

    inserted = save_occupancy_records_batch(
        records
    )

    database_records = get_occupancy_records(
        limit=max(
            len(records),
            1,
        )
    )

    return _json_safe(
        {
            "dataset_rows": len(records),
            "inserted_rows": inserted,
            "database_rows": len(database_records),
            "data_source": "SIMULATED DATA",
        }
    )


# ============================================================
# SYNCHRONISE OCCUPANCY ALERTS
# ============================================================

def sync_occupancy_alerts():
    initialise_monitoring_database()

    dataframe = load_occupancy_dataset()

    agent_result = occupancy_agent.run(
        dataframe
    )

    alerts = agent_result.get(
        "alerts",
        [],
    )

    inserted = 0

    for alert in alerts:
        safe_alert = _json_safe(
            alert
        )

        alert_id = create_occupancy_alert(
            safe_alert
        )

        if alert_id is not None:
            inserted += 1

    return _json_safe(
        {
            "agent_alerts": len(alerts),
            "inserted_alerts": inserted,
            "data_source": "SIMULATED DATA",
        }
    )


# ============================================================
# OCCUPANCY DASHBOARD DATA
# ============================================================

def get_occupancy_dashboard():
    dataframe = load_occupancy_dataset()

    summary = calculate_occupancy_summary(
        dataframe
    )

    current_spaces = get_latest_space_readings(
        dataframe
    )

    space_utilization = get_space_utilization_table(
        dataframe
    )

    building_comparison = get_building_occupancy_comparison(
        dataframe
    )

    hourly_pattern = get_hourly_occupancy_pattern(
        dataframe
    )

    peak_usage = get_peak_usage_hours(
        dataframe
    )

    heatmap = get_occupancy_heatmap(
        dataframe
    )

    overcrowding_events = get_overcrowding_events(
        dataframe,
        limit=20,
    )

    underused_spaces = get_underused_spaces(
        dataframe
    )

    insights = generate_occupancy_insights(
        dataframe
    )

    agent_result = occupancy_agent.run(
        dataframe
    )

    result = {
        "summary": summary,
        "current_spaces": current_spaces,
        "space_utilization": space_utilization,
        "building_comparison": building_comparison,
        "hourly_pattern": hourly_pattern,
        "peak_usage": peak_usage,
        "heatmap": heatmap,
        "overcrowding_events": overcrowding_events,
        "underused_spaces": underused_spaces,
        "insights": insights,
        "agent": agent_result,
        "data_source": "SIMULATED DATA",
    }

    return _json_safe(
        result
    )


# ============================================================
# OCCUPANCY AGENT RESULT
# ============================================================

def get_occupancy_agent_result():
    dataframe = load_occupancy_dataset()

    result = occupancy_agent.run(
        dataframe
    )

    result["data_source"] = (
        "SIMULATED DATA"
    )

    return _json_safe(
        result
    )


# ============================================================
# OCCUPANCY SUMMARY
# ============================================================

def get_occupancy_summary():
    dataframe = load_occupancy_dataset()

    result = calculate_occupancy_summary(
        dataframe
    )

    result["data_source"] = (
        "SIMULATED DATA"
    )

    return _json_safe(
        result
    )


# ============================================================
# CURRENT SPACE OCCUPANCY
# ============================================================

def get_current_space_occupancy():
    dataframe = load_occupancy_dataset()

    result = get_latest_space_readings(
        dataframe
    )

    return _json_safe(
        result
    )


# ============================================================
# SPACE UTILIZATION
# ============================================================

def get_space_utilization():
    dataframe = load_occupancy_dataset()

    result = get_space_utilization_table(
        dataframe
    )

    return _json_safe(
        result
    )


# ============================================================
# BUILDING OCCUPANCY COMPARISON
# ============================================================

def get_building_occupancy():
    dataframe = load_occupancy_dataset()

    result = get_building_occupancy_comparison(
        dataframe
    )

    return _json_safe(
        result
    )


# ============================================================
# HOURLY OCCUPANCY PATTERN
# ============================================================

def get_occupancy_hourly_pattern():
    dataframe = load_occupancy_dataset()

    result = get_hourly_occupancy_pattern(
        dataframe
    )

    return _json_safe(
        result
    )


# ============================================================
# PEAK OCCUPANCY HOURS
# ============================================================

def get_occupancy_peak_hours():
    dataframe = load_occupancy_dataset()

    result = get_peak_usage_hours(
        dataframe
    )

    return _json_safe(
        result
    )


# ============================================================
# OCCUPANCY HEATMAP
# ============================================================

def get_occupancy_heatmap_data():
    dataframe = load_occupancy_dataset()

    result = get_occupancy_heatmap(
        dataframe
    )

    return _json_safe(
        result
    )


# ============================================================
# OVERCROWDING EVENTS
# ============================================================

def get_recent_overcrowding_events(
    limit=20,
):
    dataframe = load_occupancy_dataset()

    result = get_overcrowding_events(
        dataframe,
        limit=limit,
    )

    return _json_safe(
        result
    )


# ============================================================
# UNDERUSED SPACES
# ============================================================

def get_occupancy_underused_spaces():
    dataframe = load_occupancy_dataset()

    result = get_underused_spaces(
        dataframe
    )

    return _json_safe(
        result
    )


# ============================================================
# OCCUPANCY INSIGHTS
# ============================================================

def get_occupancy_insights():
    dataframe = load_occupancy_dataset()

    result = generate_occupancy_insights(
        dataframe
    )

    return _json_safe(
        result
    )


# ============================================================
# DATABASE OCCUPANCY RECORDS
# ============================================================

def get_database_occupancy_records(
    space_id=None,
    building=None,
    block=None,
    limit=500,
):
    result = get_occupancy_records(
        space_id=space_id,
        building=building,
        block=block,
        limit=limit,
    )

    return _json_safe(
        result
    )


# ============================================================
# DATABASE OCCUPANCY ALERTS
# ============================================================

def get_database_occupancy_alerts(
    limit=50,
    status=None,
):
    result = get_occupancy_alerts(
        limit=limit,
        status=status,
    )

    return _json_safe(
        result
    )


# ============================================================
# UPDATE OCCUPANCY ALERT STATUS
# ============================================================

def change_occupancy_alert_status(
    alert_id,
    status,
):
    result = update_occupancy_alert_status(
        alert_id,
        status,
    )

    return _json_safe(
        result
    )


# ============================================================
# SERVICE TEST
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print(
        "FACILITYOPS AI - OCCUPANCY SERVICE"
    )
    print("=" * 60)

    sync_result = sync_occupancy_data()

    print(
        "\nOccupancy Database Sync"
    )
    print("-" * 60)

    for key, value in sync_result.items():
        print(
            f"{key}: {value}"
        )

    dashboard = get_occupancy_dashboard()

    print(
        "\nOccupancy Summary"
    )
    print("-" * 60)

    for key, value in dashboard[
        "summary"
    ].items():
        print(
            f"{key}: {value}"
        )

    print(
        "\nCurrent Spaces"
    )
    print("-" * 60)

    print(
        "Spaces:",
        len(
            dashboard[
                "current_spaces"
            ]
        ),
    )

    print(
        "\nOccupancy Service completed successfully."
    )