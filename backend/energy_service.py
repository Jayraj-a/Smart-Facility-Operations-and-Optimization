from datetime import datetime

import pandas as pd

from agents.energy_agent import (
    EnergyMonitoringAgent,
)

from backend.monitoring_db import (
    create_alert,
    save_energy_reading,
    save_energy_readings_batch,
    upsert_daily_summary,
)


# ============================================================
# ENERGY MONITORING AGENT INSTANCE
# ============================================================

energy_agent = EnergyMonitoringAgent()


# ============================================================
# HELPER
# ============================================================

def clean_value(value):

    if pd.isna(value):
        return None

    if hasattr(value, "item"):

        try:
            return value.item()
        except Exception:
            pass

    return value


def row_to_dict(row):

    return {
        key: clean_value(value)
        for key, value
        in row.to_dict().items()
    }


# ============================================================
# ANALYSE LATEST READING
# ============================================================

def analyse_latest_reading(df):

    if df.empty:

        return {
            "reading": None,
            "analysis": {
                "alerts": [],
                "alert_count": 0,
                "ml_detection": {
                    "model_available": False,
                    "is_anomaly": False,
                    "probability": 0.0,
                },
            },
        }

    working = df.copy()

    working["timestamp"] = pd.to_datetime(
        working["timestamp"],
        errors="coerce",
    )

    working = working.dropna(
        subset=["timestamp"]
    )

    working = working.sort_values(
        "timestamp"
    )

    if working.empty:

        return {
            "reading": None,
            "analysis": {
                "alerts": [],
                "alert_count": 0,
            },
        }

    current = working.iloc[-1]

    history = working.iloc[:-1]

    current_dict = row_to_dict(
        current
    )

    analysis = energy_agent.analyse_reading(
        current_dict,
        history,
    )

    return {
        "reading": current_dict,
        "analysis": analysis,
    }


# ============================================================
# ANALYSE AND STORE LATEST READING
# ============================================================

def analyse_and_store_latest(df):

    result = analyse_latest_reading(
        df
    )

    reading = result.get(
        "reading"
    )

    analysis = result.get(
        "analysis",
        {}
    )

    if not reading:

        return result

    # --------------------------------------------------------
    # SAVE READING
    # --------------------------------------------------------

    save_energy_reading(
        reading
    )

    # --------------------------------------------------------
    # STORE ALERTS
    # --------------------------------------------------------

    source_timestamp = str(
        reading.get(
            "timestamp",
            ""
        )
    )

    stored_alerts = 0

    for alert in analysis.get(
        "alerts",
        []
    ):

        alert_record = {

            "created_at":
                datetime.now().isoformat(),

            "source_timestamp":
                source_timestamp,

            "facility_id":
                reading.get(
                    "facility_id"
                ),

            "facility_name":
                reading.get(
                    "facility_name"
                ),

            "building_id":
                reading.get(
                    "building_id"
                ),

            "building_name":
                reading.get(
                    "building_name"
                ),

            "block_id":
                reading.get(
                    "block_id"
                ),

            "block_name":
                reading.get(
                    "block_name"
                ),

            "alert_type":
                alert.get(
                    "alert_type",
                    alert.get(
                        "type",
                        "ENERGY",
                    ),
                ),

            "metric":
                alert.get(
                    "metric",
                    "energy",
                ),

            "observed_value":
                alert.get(
                    "observed_value"
                ),

            "expected_value":
                alert.get(
                    "expected_value"
                ),

            "change_percent":
                alert.get(
                    "change_percent"
                ),

            "severity":
                alert.get(
                    "severity",
                    "WARNING",
                ),

            "title":
                alert.get(
                    "title",
                    "Energy Usage Issue",
                ),

            "message":
                alert.get(
                    "message",
                    alert.get(
                        "reason",
                        "",
                    ),
                ),

            "status":
                "OPEN",
        }

        alert_id = create_alert(
            alert_record
        )

        if alert_id is not None:
            stored_alerts += 1

    result[
        "stored_alerts"
    ] = stored_alerts

    return result


# ============================================================
# SYNCHRONISE HISTORICAL DATA
# ============================================================

def synchronise_historical_data(df):

    if df.empty:

        return {
            "inserted_readings": 0,
            "daily_summaries": 0,
        }

    working = df.copy()

    working["timestamp"] = pd.to_datetime(
        working["timestamp"],
        errors="coerce",
    )

    working = working.dropna(
        subset=["timestamp"]
    )

    # --------------------------------------------------------
    # STORE ALL HISTORICAL READINGS
    # --------------------------------------------------------

    records = []

    for _, row in working.iterrows():

        record = row_to_dict(
            row
        )

        record["timestamp"] = (
            pd.Timestamp(
                record["timestamp"]
            ).isoformat()
        )

        records.append(
            record
        )

    inserted_readings = (
        save_energy_readings_batch(
            records
        )
    )

    # --------------------------------------------------------
    # DAILY SUMMARIES
    # --------------------------------------------------------

    working[
        "summary_date"
    ] = (
        working[
            "timestamp"
        ]
        .dt.date
        .astype(str)
    )

    grouping = [
        "summary_date",
        "facility_name",
        "building_name",
        "block_name",
    ]

    grouped = working.groupby(
        grouping,
        dropna=False,
    )

    daily_summary_count = 0

    for keys, group in grouped:

        (
            summary_date,
            facility_name,
            building_name,
            block_name,
        ) = keys

        issue_count = 0

        if (
            "is_anomaly"
            in group.columns
        ):

            issue_count = int(
                group[
                    "is_anomaly"
                ]
                .astype(str)
                .str.lower()
                .isin(
                    [
                        "true",
                        "1",
                        "yes",
                    ]
                )
                .sum()
            )

        summary = {

            "summary_date":
                str(
                    summary_date
                ),

            "facility_name":
                str(
                    facility_name
                ),

            "building_name":
                str(
                    building_name
                ),

            "block_name":
                str(
                    block_name
                ),

            "total_electricity":
                float(
                    group[
                        "electricity_kwh"
                    ].sum()
                ),

            "average_electricity":
                float(
                    group[
                        "electricity_kwh"
                    ].mean()
                ),

            "peak_electricity":
                float(
                    group[
                        "electricity_kwh"
                    ].max()
                ),

            "average_hvac":
                float(
                    group[
                        "hvac_kwh"
                    ].mean()
                ),

            "average_lighting":
                float(
                    group[
                        "lighting_kwh"
                    ].mean()
                ),

            "total_water":
                float(
                    group[
                        "water_liters"
                    ].sum()
                ),

            "average_temperature":
                float(
                    group[
                        "temperature_c"
                    ].mean()
                ),

            "average_occupancy":
                float(
                    group[
                        "occupancy"
                    ].mean()
                ),

            "issue_count":
                issue_count,
        }

        upsert_daily_summary(
            summary
        )

        daily_summary_count += 1

    return {
        "inserted_readings":
            inserted_readings,

        "daily_summaries":
            daily_summary_count,
    }