from analytics.cost_analytics import (
    load_cost_data,
    calculate_cost_summary,
    get_cost_breakdown,
    get_building_cost_comparison,
    get_daily_cost_trend,
    get_hourly_cost_pattern,
    get_cost_inefficiencies,
    get_savings_opportunities,
    get_high_cost_records,
    generate_cost_insights,
)

from agents.cost_agent import (
    cost_agent,
)

from backend.monitoring_db import (
    initialise_monitoring_database,
    save_cost_reports_batch,
    create_cost_optimization_alert,
    get_cost_reports,
    get_cost_optimization_alerts,
    get_cost_database_counts,
)


# ============================================================
# FACILITYOPS AI
# MILESTONE 4 - COST OPTIMIZATION SERVICE
# ============================================================


def _clean_value(value):
    """
    Convert pandas/numpy values into normal Python values.
    """

    if value is None:
        return None

    try:
        if hasattr(value, "item"):
            return value.item()
    except Exception:
        pass

    return value


def _dataframe_records(dataframe):
    """
    Convert a pandas DataFrame into JSON/database-safe records.
    """

    if dataframe is None or dataframe.empty:
        return []

    records = []

    for record in dataframe.to_dict(
        orient="records"
    ):
        cleaned = {}

        for key, value in record.items():

            if key == "timestamp":
                try:
                    cleaned[key] = (
                        value.isoformat()
                        if hasattr(
                            value,
                            "isoformat",
                        )
                        else str(value)
                    )
                except Exception:
                    cleaned[key] = str(
                        value
                    )

            else:
                cleaned[key] = (
                    _clean_value(
                        value
                    )
                )

        records.append(
            cleaned
        )

    return records


# ============================================================
# LOAD COST DATASET
# ============================================================


def get_cost_dataframe():
    """
    Load the complete Milestone 4 cost dataset.
    """

    return load_cost_data()


# ============================================================
# FILTER COST DATA
# ============================================================


def filter_cost_dataframe(
    dataframe,
    building=None,
):
    """
    Filter cost data by building ID or building name.
    """

    if (
        dataframe is None
        or dataframe.empty
    ):
        return dataframe

    if not building:
        return dataframe.copy()

    building = str(
        building
    ).strip()

    filtered = dataframe[
        (
            dataframe[
                "building_id"
            ].astype(str)
            == building
        )
        |
        (
            dataframe[
                "building_name"
            ].astype(str)
            == building
        )
    ].copy()

    return filtered


# ============================================================
# SYNCHRONISE COST DATASET WITH DATABASE
# ============================================================


def synchronise_cost_data():
    """
    Save the Milestone 4 cost dataset into SQLite.

    Duplicate records are ignored by monitoring_db.py.
    """

    initialise_monitoring_database()

    dataframe = (
        get_cost_dataframe()
    )

    records = (
        _dataframe_records(
            dataframe
        )
    )

    inserted = (
        save_cost_reports_batch(
            records
        )
    )

    return {
        "status":
            "SUCCESS",

        "dataset_records":
            len(records),

        "inserted_records":
            int(inserted),

        "database":
            get_cost_database_counts(),
    }


# ============================================================
# COST SUMMARY
# ============================================================


def get_cost_summary(
    building=None,
):
    """
    Return overall or building-specific cost summary.
    """

    dataframe = (
        get_cost_dataframe()
    )

    dataframe = (
        filter_cost_dataframe(
            dataframe,
            building,
        )
    )

    return (
        calculate_cost_summary(
            dataframe
        )
    )


# ============================================================
# COST BREAKDOWN
# ============================================================


def get_cost_breakdown_data(
    building=None,
):
    """
    Return electricity, water, maintenance,
    security and operational cost breakdown.
    """

    dataframe = (
        get_cost_dataframe()
    )

    dataframe = (
        filter_cost_dataframe(
            dataframe,
            building,
        )
    )

    return (
        get_cost_breakdown(
            dataframe
        )
    )


# ============================================================
# BUILDING COST COMPARISON
# ============================================================


def get_cost_building_comparison():
    """
    Compare operating cost across all buildings.
    """

    dataframe = (
        get_cost_dataframe()
    )

    return (
        get_building_cost_comparison(
            dataframe
        )
    )


# ============================================================
# DAILY COST TREND
# ============================================================


def get_cost_daily_trend(
    building=None,
):
    """
    Return daily actual, expected and savings cost trend.
    """

    dataframe = (
        get_cost_dataframe()
    )

    dataframe = (
        filter_cost_dataframe(
            dataframe,
            building,
        )
    )

    return (
        get_daily_cost_trend(
            dataframe
        )
    )


# ============================================================
# HOURLY COST PATTERN
# ============================================================


def get_cost_hourly_pattern(
    building=None,
):
    """
    Return average hourly cost pattern.
    """

    dataframe = (
        get_cost_dataframe()
    )

    dataframe = (
        filter_cost_dataframe(
            dataframe,
            building,
        )
    )

    return (
        get_hourly_cost_pattern(
            dataframe
        )
    )


# ============================================================
# COST INEFFICIENCIES
# ============================================================


def get_cost_inefficiency_data(
    building=None,
    limit=50,
):
    """
    Return detected cost inefficiency records.
    """

    dataframe = (
        get_cost_dataframe()
    )

    dataframe = (
        filter_cost_dataframe(
            dataframe,
            building,
        )
    )

    return (
        get_cost_inefficiencies(
            dataframe,
            limit=limit,
        )
    )


# ============================================================
# SAVINGS OPPORTUNITIES
# ============================================================


def get_cost_savings_opportunities(
    building=None,
):
    """
    Return grouped cost-saving opportunities.
    """

    dataframe = (
        get_cost_dataframe()
    )

    dataframe = (
        filter_cost_dataframe(
            dataframe,
            building,
        )
    )

    return (
        get_savings_opportunities(
            dataframe
        )
    )


# ============================================================
# HIGH COST RECORDS
# ============================================================


def get_high_cost_data(
    building=None,
    limit=20,
):
    """
    Return highest-cost facility records.
    """

    dataframe = (
        get_cost_dataframe()
    )

    dataframe = (
        filter_cost_dataframe(
            dataframe,
            building,
        )
    )

    return (
        get_high_cost_records(
            dataframe,
            limit=limit,
        )
    )


# ============================================================
# COST INSIGHTS
# ============================================================


def get_cost_insights(
    building=None,
):
    """
    Return generated cost optimization insights.
    """

    dataframe = (
        get_cost_dataframe()
    )

    dataframe = (
        filter_cost_dataframe(
            dataframe,
            building,
        )
    )

    return (
        generate_cost_insights(
            dataframe
        )
    )


# ============================================================
# RUN COST OPTIMIZATION AGENT
# ============================================================


def run_cost_optimization_agent(
    building=None,
    store_alerts=True,
):
    """
    Run the Cost Optimization Agent.

    When store_alerts=True, generated optimization alerts
    are stored in facilityops.db.
    """

    initialise_monitoring_database()

    dataframe = (
        get_cost_dataframe()
    )

    dataframe = (
        filter_cost_dataframe(
            dataframe,
            building,
        )
    )

    if dataframe.empty:

        return {
            "agent":
                cost_agent.name,

            "status":
                "NO_DATA",

            "summary":
                {},

            "alerts":
                [],

            "alert_count":
                0,

            "stored_alerts":
                0,
        }

    result = (
        cost_agent.run(
            dataframe
        )
    )

    stored_alerts = 0

    if store_alerts:

        for alert in result.get(
            "alerts",
            [],
        ):

            alert_data = {
                "cost_record_id":
                    alert.get(
                        "cost_record_id",
                        "",
                    ),

                "source_timestamp":
                    alert.get(
                        "timestamp",
                        "",
                    ),

                "building_id":
                    alert.get(
                        "building_id",
                        "",
                    ),

                "building_name":
                    alert.get(
                        "building_name",
                        "",
                    ),

                "alert_type":
                    alert.get(
                        "alert_type",
                        "COST_OPTIMIZATION",
                    ),

                "inefficiency_type":
                    alert.get(
                        "inefficiency_type",
                        "NONE",
                    ),

                "severity":
                    alert.get(
                        "severity",
                        "LOW",
                    ),

                "potential_savings":
                    alert.get(
                        "potential_savings",
                        0,
                    ),

                "title":
                    (
                        "Cost Optimization Alert"
                    ),

                "message":
                    alert.get(
                        "message",
                        "",
                    ),

                "recommended_action":
                    alert.get(
                        "recommended_action",
                        "",
                    ),

                "status":
                    "OPEN",
            }

            alert_id = (
                create_cost_optimization_alert(
                    alert_data
                )
            )

            if alert_id is not None:
                stored_alerts += 1

    result[
        "stored_alerts"
    ] = stored_alerts

    result[
        "database"
    ] = (
        get_cost_database_counts()
    )

    return result


# ============================================================
# SYNCHRONISE AND RUN AGENT
# ============================================================


def synchronise_and_run_cost_agent():
    """
    Complete Milestone 4 processing workflow.

    1. Initialise database
    2. Load cost dataset
    3. Save cost records
    4. Run Cost Optimization Agent
    5. Save generated optimization alerts
    """

    sync_result = (
        synchronise_cost_data()
    )

    agent_result = (
        run_cost_optimization_agent(
            store_alerts=True
        )
    )

    return {
        "status":
            "SUCCESS",

        "synchronisation":
            sync_result,

        "agent":
            agent_result,

        "database":
            get_cost_database_counts(),
    }


# ============================================================
# DATABASE COST RECORDS
# ============================================================


def get_stored_cost_records(
    building=None,
    limit=100,
):
    """
    Read cost records directly from SQLite.
    """

    return (
        get_cost_reports(
            building=building,
            limit=limit,
        )
    )


# ============================================================
# DATABASE COST ALERTS
# ============================================================


def get_stored_cost_alerts(
    limit=50,
    status=None,
):
    """
    Read Cost Optimization Agent alerts from SQLite.
    """

    return (
        get_cost_optimization_alerts(
            limit=limit,
            status=status,
        )
    )


# ============================================================
# COST DATABASE STATUS
# ============================================================


def get_cost_database_status():
    """
    Return Milestone 4 database record counts.
    """

    initialise_monitoring_database()

    counts = (
        get_cost_database_counts()
    )

    return {
        "status":
            "READY",

        "cost_agent":
            "ACTIVE",

        "cost_reports":
            counts.get(
                "cost_reports",
                0,
            ),

        "cost_optimization_alerts":
            counts.get(
                "cost_optimization_alerts",
                0,
            ),
    }


# ============================================================
# COMMAND-LINE TEST
# ============================================================


def main():

    print()
    print("=" * 70)
    print(
        "FACILITYOPS AI - "
        "MILESTONE 4 COST SERVICE"
    )
    print("=" * 70)

    print()
    print(
        "Synchronising cost dataset..."
    )

    sync_result = (
        synchronise_cost_data()
    )

    print(
        "Dataset Records:",
        sync_result[
            "dataset_records"
        ],
    )

    print(
        "Inserted Records:",
        sync_result[
            "inserted_records"
        ],
    )

    print()
    print(
        "Running Cost Optimization Agent..."
    )

    agent_result = (
        run_cost_optimization_agent(
            store_alerts=True
        )
    )

    print(
        "Agent:",
        agent_result.get(
            "agent"
        ),
    )

    print(
        "Status:",
        agent_result.get(
            "status"
        ),
    )

    print(
        "Generated Alerts:",
        agent_result.get(
            "alert_count",
            0,
        ),
    )

    print(
        "New Alerts Stored:",
        agent_result.get(
            "stored_alerts",
            0,
        ),
    )

    print()
    print(
        "DATABASE STATUS"
    )
    print("-" * 70)

    database_status = (
        get_cost_database_status()
    )

    for key, value in (
        database_status.items()
    ):
        print(
            f"{key}: {value}"
        )

    print()
    print("=" * 70)
    print(
        "Cost service test completed successfully."
    )
    print("=" * 70)


if __name__ == "__main__":
    main()