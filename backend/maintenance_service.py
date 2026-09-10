"""
FacilityOps AI
Milestone 2 - Maintenance Service

Responsibilities:
- Load simulated asset-monitoring data
- Synchronise assets with SQLite
- Synchronise asset sensor readings with SQLite
- Run the Maintenance Agent
- Store maintenance predictions
- Store maintenance alerts
- Store work-order recommendations
- Provide service functions for FastAPI endpoints
"""

from pathlib import Path

import pandas as pd

from agents.maintenance_agent import MaintenanceAgent

from analytics.maintenance_analytics import (
    load_maintenance_data,
    add_health_scores,
    calculate_asset_summary,
    get_asset_health_table,
    get_building_health_comparison,
)

from analytics.maintenance_prediction import (
    get_model_metrics,
)

from backend.monitoring_db import (
    initialise_monitoring_database,
    upsert_asset,
    get_assets,
    save_asset_readings_batch,
    get_asset_readings,
    save_maintenance_prediction,
    get_maintenance_predictions,
    create_maintenance_alert,
    get_maintenance_alerts,
    update_maintenance_alert_status,
    save_maintenance_work_order,
    get_maintenance_work_orders,
    update_maintenance_work_order_status,
    get_maintenance_database_counts,
)


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
# AGENT
# ============================================================

maintenance_agent = MaintenanceAgent()


# ============================================================
# HELPERS
# ============================================================

def clean_value(value):
    """
    Convert pandas/numpy values into JSON/SQLite-safe values.
    """

    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, AttributeError):
            pass

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    return value


def clean_record(record):
    """
    Clean every value in a dictionary.
    """

    return {
        key: clean_value(value)
        for key, value in record.items()
    }


def clean_records(records):
    """
    Clean a list of dictionaries.
    """

    return [
        clean_record(record)
        for record in records
    ]


def safe_float(
    value,
    default=0.0,
):
    try:

        if value is None:
            return default

        number = float(value)

        if pd.isna(number):
            return default

        return number

    except (TypeError, ValueError):
        return default


def safe_int(
    value,
    default=0,
):
    try:

        if value is None:
            return default

        number = float(value)

        if pd.isna(number):
            return default

        return int(number)

    except (TypeError, ValueError):
        return default


# ============================================================
# LOAD DATA
# ============================================================

def get_maintenance_dataframe():
    """
    Load the Milestone 2 simulated asset-monitoring dataset.
    """

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Maintenance dataset not found: {DATA_FILE}"
        )

    dataframe = load_maintenance_data()

    if dataframe.empty:
        raise ValueError(
            "Maintenance dataset is empty."
        )

    dataframe = dataframe.copy()

    dataframe["timestamp"] = pd.to_datetime(
        dataframe["timestamp"],
        errors="coerce",
    )

    dataframe = dataframe.dropna(
        subset=[
            "asset_id",
            "timestamp",
        ]
    )

    dataframe = dataframe.sort_values(
        [
            "timestamp",
            "asset_id",
        ]
    )

    return dataframe


# ============================================================
# LATEST ASSET READINGS
# ============================================================

def get_latest_asset_dataframe(
    dataframe=None,
):
    """
    Return the latest sensor reading for every asset.
    """

    if dataframe is None:
        dataframe = get_maintenance_dataframe()

    if dataframe.empty:
        return dataframe.copy()

    df = dataframe.copy()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
    )

    df = df.dropna(
        subset=[
            "asset_id",
            "timestamp",
        ]
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
        .sort_values(
            "asset_id"
        )
        .reset_index(
            drop=True
        )
    )

    return latest


# ============================================================
# SYNCHRONISE ASSET MASTER DATA
# ============================================================

def synchronise_assets(
    dataframe=None,
):
    """
    Insert/update the asset master records in SQLite.
    """

    if dataframe is None:
        dataframe = get_maintenance_dataframe()

    latest = get_latest_asset_dataframe(
        dataframe
    )

    synced = 0

    for _, row in latest.iterrows():

        record = clean_record(
            row.to_dict()
        )

        asset = {
            "asset_id":
                record.get(
                    "asset_id",
                    ""
                ),

            "asset_name":
                record.get(
                    "asset_name",
                    ""
                ),

            "asset_type":
                record.get(
                    "asset_type",
                    ""
                ),

            "facility_id":
                record.get(
                    "facility_id",
                    ""
                ),

            "facility_name":
                record.get(
                    "facility_name",
                    ""
                ),

            "building_name":
                record.get(
                    "building_name",
                    ""
                ),

            "block_name":
                record.get(
                    "block_name",
                    ""
                ),

            "age_years":
                safe_float(
                    record.get(
                        "age_years"
                    )
                ),

            "status":
                "ACTIVE",
        }

        upsert_asset(
            asset
        )

        synced += 1

    return synced


# ============================================================
# SYNCHRONISE ASSET SENSOR READINGS
# ============================================================

def synchronise_asset_readings(
    dataframe=None,
):
    """
    Store all simulated asset-monitoring readings in SQLite.

    INSERT OR IGNORE in monitoring_db.py prevents duplicate
    readings when the application starts again.
    """

    if dataframe is None:
        dataframe = get_maintenance_dataframe()

    readings = []

    for _, row in dataframe.iterrows():

        record = clean_record(
            row.to_dict()
        )

        timestamp = record.get(
            "timestamp"
        )

        if isinstance(
            timestamp,
            pd.Timestamp,
        ):
            timestamp = timestamp.isoformat()

        reading = {
            "asset_id":
                record.get(
                    "asset_id",
                    ""
                ),

            "asset_name":
                record.get(
                    "asset_name",
                    ""
                ),

            "asset_type":
                record.get(
                    "asset_type",
                    ""
                ),

            "facility_id":
                record.get(
                    "facility_id",
                    ""
                ),

            "facility_name":
                record.get(
                    "facility_name",
                    ""
                ),

            "building_name":
                record.get(
                    "building_name",
                    ""
                ),

            "block_name":
                record.get(
                    "block_name",
                    ""
                ),

            "timestamp":
                str(
                    timestamp
                ),

            "temperature_c":
                safe_float(
                    record.get(
                        "temperature_c"
                    )
                ),

            "vibration_mm_s":
                safe_float(
                    record.get(
                        "vibration_mm_s"
                    )
                ),

            "pressure_bar":
                safe_float(
                    record.get(
                        "pressure_bar"
                    )
                ),

            "power_kw":
                safe_float(
                    record.get(
                        "power_kw"
                    )
                ),

            "runtime_hours":
                safe_float(
                    record.get(
                        "runtime_hours"
                    )
                ),

            "operating_hours":
                safe_float(
                    record.get(
                        "operating_hours"
                    )
                ),

            "age_years":
                safe_float(
                    record.get(
                        "age_years"
                    )
                ),

            "days_since_service":
                safe_float(
                    record.get(
                        "days_since_service"
                    )
                ),

            "health_score":
                safe_float(
                    record.get(
                        "health_score"
                    )
                ),

            "health_status":
                str(
                    record.get(
                        "health_status",
                        ""
                    )
                ),

            "abnormal_behavior":
                safe_int(
                    record.get(
                        "abnormal_behavior"
                    )
                ),

            "maintenance_required":
                safe_int(
                    record.get(
                        "maintenance_required"
                    )
                ),

            "days_to_maintenance":
                safe_int(
                    record.get(
                        "days_to_maintenance"
                    )
                ),
        }

        readings.append(
            reading
        )

    inserted = save_asset_readings_batch(
        readings
    )

    return inserted


# ============================================================
# CONVERT AGENT RESULT TO DATABASE PREDICTION
# ============================================================

def build_prediction_record(
    result,
):
    """
    Convert a Maintenance Agent result into the format
    required by maintenance_predictions.
    """

    health = result.get(
        "health",
        {},
    )

    prediction = result.get(
        "prediction",
        {},
    )

    schedule = result.get(
        "maintenance_schedule",
        {},
    )

    return {
        "asset_id":
            result.get(
                "asset_id",
                ""
            ),

        "asset_name":
            result.get(
                "asset_name",
                ""
            ),

        "asset_type":
            result.get(
                "asset_type",
                ""
            ),

        "building_name":
            result.get(
                "building_name",
                ""
            ),

        "block_name":
            result.get(
                "block_name",
                ""
            ),

        "source_timestamp":
            result.get(
                "timestamp",
                ""
            ),

        "health_score":
            safe_float(
                health.get(
                    "health_score"
                )
            ),

        "health_status":
            health.get(
                "health_status",
                ""
            ),

        "maintenance_required":
            safe_int(
                prediction.get(
                    "maintenance_required"
                )
            ),

        "maintenance_probability":
            safe_float(
                prediction.get(
                    "maintenance_probability"
                )
            ),

        "maintenance_probability_percent":
            safe_float(
                prediction.get(
                    "maintenance_probability_percent"
                )
            ),

        "risk_level":
            prediction.get(
                "risk_level",
                ""
            ),

        "priority":
            result.get(
                "priority",
                ""
            ),

        "recommended_maintenance_date":
            schedule.get(
                "recommended_maintenance_date",
                ""
            ),

        "days_until_service":
            safe_int(
                schedule.get(
                    "days_until_service"
                )
            ),
    }


# ============================================================
# SAVE AGENT ANALYSIS
# ============================================================

def save_agent_result(
    result,
):
    """
    Save one Maintenance Agent result.

    Stores:
    - Prediction
    - Alert, if generated
    - Work-order recommendation, if generated
    """

    prediction_record = (
        build_prediction_record(
            result
        )
    )

    save_maintenance_prediction(
        prediction_record
    )

    alert_saved = False
    work_order_saved = False

    alert = result.get(
        "alert"
    )

    if alert:

        alert = dict(
            alert
        )

        alert[
            "source_timestamp"
        ] = result.get(
            "timestamp",
            alert.get(
                "source_timestamp",
                ""
            ),
        )

        alert_id = (
            create_maintenance_alert(
                alert
            )
        )

        alert_saved = (
            alert_id is not None
        )

    work_order = result.get(
        "work_order"
    )

    if work_order:

        work_order = dict(
            work_order
        )

        work_order[
            "source_timestamp"
        ] = result.get(
            "timestamp",
            ""
        )

        work_order_id = (
            save_maintenance_work_order(
                work_order
            )
        )

        work_order_saved = (
            work_order_id is not None
        )

    return {
        "prediction_saved": True,
        "alert_saved": alert_saved,
        "work_order_saved": work_order_saved,
    }


# ============================================================
# RUN MAINTENANCE AGENT
# ============================================================

def run_maintenance_agent(
    dataframe=None,
):
    """
    Analyse the latest reading for all assets and save
    predictions, alerts and work-order recommendations.
    """

    if dataframe is None:
        dataframe = get_maintenance_dataframe()

    results = (
        maintenance_agent.analyse_assets(
            dataframe
        )
    )

    predictions_saved = 0
    alerts_saved = 0
    work_orders_saved = 0

    for result in results:

        saved = save_agent_result(
            result
        )

        if saved[
            "prediction_saved"
        ]:
            predictions_saved += 1

        if saved[
            "alert_saved"
        ]:
            alerts_saved += 1

        if saved[
            "work_order_saved"
        ]:
            work_orders_saved += 1

    return {
        "assets_analysed":
            len(results),

        "predictions_saved":
            predictions_saved,

        "alerts_saved":
            alerts_saved,

        "work_orders_saved":
            work_orders_saved,

        "results":
            results,
    }


# ============================================================
# FULL MILESTONE 2 SYNCHRONISATION
# ============================================================

def synchronise_maintenance_data():
    """
    Complete Milestone 2 synchronisation.

    Called at application startup later from backend.main.
    """

    initialise_monitoring_database()

    dataframe = (
        get_maintenance_dataframe()
    )

    assets_synced = (
        synchronise_assets(
            dataframe
        )
    )

    readings_inserted = (
        synchronise_asset_readings(
            dataframe
        )
    )

    agent_result = (
        run_maintenance_agent(
            dataframe
        )
    )

    counts = (
        get_maintenance_database_counts()
    )

    return {
        "dataset_rows":
            int(
                len(dataframe)
            ),

        "assets_synced":
            assets_synced,

        "asset_readings_newly_stored":
            readings_inserted,

        "assets_analysed":
            agent_result[
                "assets_analysed"
            ],

        "predictions_saved":
            agent_result[
                "predictions_saved"
            ],

        "alerts_newly_stored":
            agent_result[
                "alerts_saved"
            ],

        "work_orders_newly_stored":
            agent_result[
                "work_orders_saved"
            ],

        "database_counts":
            counts,
    }


# ============================================================
# MAINTENANCE SUMMARY
# ============================================================

def get_maintenance_summary():
    """
    Return summary information for the Maintenance Dashboard.
    """

    dataframe = (
        get_maintenance_dataframe()
    )

    scored = add_health_scores(
        dataframe
    )

    summary = calculate_asset_summary(
        scored
    )

    latest = get_latest_asset_dataframe(
        scored
    )

    agent_results = (
        maintenance_agent.analyse_assets(
            latest
        )
    )

    priorities = {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0,
    }

    predicted_maintenance = 0

    for result in agent_results:

        priority = str(
            result.get(
                "priority",
                "LOW"
            )
        ).upper()

        if priority in priorities:
            priorities[
                priority
            ] += 1

        prediction = result.get(
            "prediction",
            {},
        )

        if safe_int(
            prediction.get(
                "maintenance_required"
            )
        ) == 1:
            predicted_maintenance += 1

    return {
        **summary,

        "predicted_maintenance_required":
            predicted_maintenance,

        "critical_priority":
            priorities[
                "CRITICAL"
            ],

        "high_priority":
            priorities[
                "HIGH"
            ],

        "medium_priority":
            priorities[
                "MEDIUM"
            ],

        "low_priority":
            priorities[
                "LOW"
            ],

        "open_maintenance_alerts":
            len(
                get_maintenance_alerts(
                    limit=1000,
                    status="OPEN",
                )
            ),

        "work_orders":
            len(
                get_maintenance_work_orders(
                    limit=1000
                )
            ),
    }


# ============================================================
# ASSET HEALTH
# ============================================================

def get_asset_health():
    """
    Return current equipment-health information for all assets.

    Includes:
    - Equipment health score
    - Equipment health status
    - Maintenance prediction probability
    - Maintenance risk level
    - Maintenance priority
    - Recommended maintenance date
    """

    dataframe = (
        get_maintenance_dataframe()
    )

    scored = (
        add_health_scores(
            dataframe
        )
    )

    records = (
        get_asset_health_table(
            scored
        )
    )

    latest = (
        get_latest_asset_dataframe(
            scored
        )
    )

    agent_results = (
        maintenance_agent.analyse_assets(
            latest
        )
    )

    prediction_map = {}

    for result in agent_results:

        asset_id = str(
            result.get(
                "asset_id",
                ""
            )
        )

        prediction = (
            result.get(
                "prediction",
                {}
            )
        )

        schedule = (
            result.get(
                "maintenance_schedule",
                {}
            )
        )

        prediction_map[
            asset_id
        ] = {

            "maintenance_required":
                safe_int(
                    prediction.get(
                        "maintenance_required"
                    )
                ),

            "maintenance_probability":
                safe_float(
                    prediction.get(
                        "maintenance_probability"
                    )
                ),

            "maintenance_probability_percent":
                safe_float(
                    prediction.get(
                        "maintenance_probability_percent"
                    )
                ),

            "risk_level":
                prediction.get(
                    "risk_level",
                    ""
                ),

            "priority":
                result.get(
                    "priority",
                    "LOW"
                ),

            "recommended_maintenance_date":
                schedule.get(
                    "recommended_maintenance_date",
                    ""
                ),

            "days_until_service":
                safe_int(
                    schedule.get(
                        "days_until_service"
                    )
                ),
        }

    enriched_records = []

    for record in records:

        clean = (
            clean_record(
                record
            )
        )

        asset_id = str(
            clean.get(
                "asset_id",
                ""
            )
        )

        prediction_data = (
            prediction_map.get(
                asset_id,
                {}
            )
        )

        clean.update(
            prediction_data
        )

        enriched_records.append(
            clean
        )

    return clean_records(
        enriched_records
    )
# ============================================================
# BUILDING HEALTH
# ============================================================

def get_maintenance_building_comparison():
    """
    Return equipment-health comparison by building.
    """

    dataframe = (
        get_maintenance_dataframe()
    )

    scored = add_health_scores(
        dataframe
    )

    records = (
        get_building_health_comparison(
            scored
        )
    )

    return clean_records(
        records
    )


# ============================================================
# CURRENT AGENT ANALYSIS
# ============================================================

def get_current_maintenance_analysis():
    """
    Run Maintenance Agent against latest asset readings
    without creating additional database duplicates.
    """

    dataframe = (
        get_maintenance_dataframe()
    )

    results = (
        maintenance_agent.analyse_assets(
            dataframe
        )
    )

    return clean_records(
        results
    )


# ============================================================
# MAINTENANCE SCHEDULE
# ============================================================

def get_current_maintenance_schedule():
    """
    Return maintenance schedule for all current assets.
    """

    results = (
        get_current_maintenance_analysis()
    )

    schedule = []

    for result in results:

        maintenance_schedule = (
            result.get(
                "maintenance_schedule",
                {},
            )
        )

        prediction = result.get(
            "prediction",
            {},
        )

        health = result.get(
            "health",
            {},
        )

        schedule.append(
            {
                "asset_id":
                    result.get(
                        "asset_id"
                    ),

                "asset_name":
                    result.get(
                        "asset_name"
                    ),

                "asset_type":
                    result.get(
                        "asset_type"
                    ),

                "building_name":
                    result.get(
                        "building_name"
                    ),

                "block_name":
                    result.get(
                        "block_name"
                    ),

                "health_score":
                    health.get(
                        "health_score"
                    ),

                "health_status":
                    health.get(
                        "health_status"
                    ),

                "maintenance_probability_percent":
                    prediction.get(
                        "maintenance_probability_percent"
                    ),

                "risk_level":
                    prediction.get(
                        "risk_level"
                    ),

                "priority":
                    result.get(
                        "priority"
                    ),

                "recommended_maintenance_date":
                    maintenance_schedule.get(
                        "recommended_maintenance_date"
                    ),

                "days_until_service":
                    maintenance_schedule.get(
                        "days_until_service"
                    ),
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
                str(
                    item.get(
                        "priority",
                        "LOW"
                    )
                ).upper(),
                4,
            ),
            str(
                item.get(
                    "recommended_maintenance_date",
                    ""
                )
            ),
        )
    )

    return schedule


# ============================================================
# MAINTENANCE ALERT API HELPERS
# ============================================================

def get_saved_maintenance_alerts(
    limit=50,
    status=None,
):
    return get_maintenance_alerts(
        limit=limit,
        status=status,
    )


def set_maintenance_alert_status(
    alert_id,
    status,
):
    return update_maintenance_alert_status(
        alert_id,
        status,
    )


# ============================================================
# WORK ORDER API HELPERS
# ============================================================

def get_saved_work_orders(
    limit=50,
    status=None,
):
    return get_maintenance_work_orders(
        limit=limit,
        status=status,
    )


def set_work_order_status(
    work_order_id,
    status,
):
    return (
        update_maintenance_work_order_status(
            work_order_id,
            status,
        )
    )


# ============================================================
# MODEL METRICS
# ============================================================

def get_maintenance_model_metrics():
    """
    Return predictive-maintenance model metrics.
    """

    return get_model_metrics()


# ============================================================
# DATABASE STATUS
# ============================================================

def get_maintenance_database_status():
    """
    Return current Milestone 2 database counts.
    """

    initialise_monitoring_database()

    return (
        get_maintenance_database_counts()
    )


# ============================================================
# COMMAND-LINE TEST
# ============================================================

def main():

    print()

    print(
        "FacilityOps AI - Milestone 2"
    )

    print(
        "Maintenance Service"
    )

    print()

    print(
        "Synchronising asset monitoring data..."
    )

    result = (
        synchronise_maintenance_data()
    )

    print()

    print(
        "Maintenance synchronisation completed."
    )

    print()

    print(
        f"Dataset rows: "
        f"{result['dataset_rows']}"
    )

    print(
        f"Assets synced: "
        f"{result['assets_synced']}"
    )

    print(
        f"Asset readings newly stored: "
        f"{result['asset_readings_newly_stored']}"
    )

    print(
        f"Assets analysed: "
        f"{result['assets_analysed']}"
    )

    print(
        f"Predictions saved: "
        f"{result['predictions_saved']}"
    )

    print(
        f"Maintenance alerts newly stored: "
        f"{result['alerts_newly_stored']}"
    )

    print(
        f"Work orders newly stored: "
        f"{result['work_orders_newly_stored']}"
    )

    print()

    print(
        "Database Counts"
    )

    print(
        "---------------"
    )

    for key, value in (
        result[
            "database_counts"
        ].items()
    ):

        print(
            f"{key}: {value}"
        )

    print()


if __name__ == "__main__":
    main()