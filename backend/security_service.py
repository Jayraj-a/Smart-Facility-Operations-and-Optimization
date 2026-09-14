from agents.security_agent import security_agent

from analytics.security_analytics import (
    load_security_data,
    calculate_security_summary,
    get_recent_access_events,
    get_unauthorized_access_events,
    get_after_hours_events,
    get_cctv_events,
    get_security_alerts,
    get_access_point_summary,
    get_building_security_comparison,
    get_hourly_security_pattern,
    get_visitor_movement,
    generate_security_insights,
)

from backend.monitoring_db import (
    initialise_monitoring_database,
    save_security_events_batch,
    get_security_events,
    create_security_alert,
    get_security_alerts_db,
    update_security_alert_status,
)


# ============================================================
# DATA HELPERS
# ============================================================

def _records_from_dataframe(dataframe):
    if dataframe is None or dataframe.empty:
        return []

    clean_df = dataframe.copy()

    if "timestamp" in clean_df.columns:
        clean_df["timestamp"] = clean_df["timestamp"].astype(str)

    clean_df = clean_df.where(
        clean_df.notna(),
        None,
    )

    return clean_df.to_dict(
        orient="records"
    )


# ============================================================
# LOAD SECURITY DATASET
# ============================================================

def load_security_dataset():
    return load_security_data()


# ============================================================
# SYNCHRONISE SECURITY DATA WITH SQLITE
# ============================================================

def sync_security_data():
    initialise_monitoring_database()

    dataframe = load_security_dataset()

    records = _records_from_dataframe(
        dataframe
    )

    inserted = save_security_events_batch(
        records
    )

    database_records = get_security_events(
        limit=max(
            len(records),
            1,
        )
    )

    return {
        "dataset_rows": len(records),
        "inserted_rows": inserted,
        "database_rows": len(database_records),
        "data_source": "SIMULATED DATA",
    }


# ============================================================
# SYNCHRONISE SECURITY AGENT ALERTS
# ============================================================

def sync_security_agent_alerts():
    initialise_monitoring_database()

    dataframe = load_security_dataset()

    agent_result = security_agent.run(
        dataframe
    )

    alerts = agent_result.get(
        "alerts",
        [],
    )

    inserted = 0

    for alert in alerts:
        alert_id = create_security_alert(
            alert
        )

        if alert_id is not None:
            inserted += 1

    return {
        "agent_alerts": len(alerts),
        "inserted_alerts": inserted,
        "data_source": "SIMULATED DATA",
    }


# ============================================================
# SECURITY DASHBOARD
# ============================================================

def get_security_dashboard():
    dataframe = load_security_dataset()

    summary = calculate_security_summary(
        dataframe
    )

    recent_events = get_recent_access_events(
        dataframe,
        limit=20,
    )

    unauthorized_events = get_unauthorized_access_events(
        dataframe,
        limit=20,
    )

    after_hours_events = get_after_hours_events(
        dataframe,
        limit=20,
    )

    cctv_events = get_cctv_events(
        dataframe,
        limit=20,
    )

    security_alert_events = get_security_alerts(
        dataframe,
        limit=20,
    )

    access_points = get_access_point_summary(
        dataframe
    )

    building_comparison = get_building_security_comparison(
        dataframe
    )

    hourly_pattern = get_hourly_security_pattern(
        dataframe
    )

    visitor_movement = get_visitor_movement(
        dataframe
    )

    insights = generate_security_insights(
        dataframe
    )

    agent_result = security_agent.run(
        dataframe
    )

    return {
        "summary": summary,
        "recent_events": recent_events,
        "unauthorized_events": unauthorized_events,
        "after_hours_events": after_hours_events,
        "cctv_events": cctv_events,
        "security_alert_events": security_alert_events,
        "access_points": access_points,
        "building_comparison": building_comparison,
        "hourly_pattern": hourly_pattern,
        "visitor_movement": visitor_movement,
        "insights": insights,
        "agent": agent_result,
        "data_source": "SIMULATED DATA",
    }


# ============================================================
# SECURITY AGENT RESULT
# ============================================================

def get_security_agent_result():
    dataframe = load_security_dataset()

    result = security_agent.run(
        dataframe
    )

    result["data_source"] = "SIMULATED DATA"

    return result


# ============================================================
# SECURITY SUMMARY
# ============================================================

def get_security_summary():
    dataframe = load_security_dataset()

    result = calculate_security_summary(
        dataframe
    )

    result["data_source"] = "SIMULATED DATA"

    return result


# ============================================================
# RECENT ACCESS EVENTS
# ============================================================

def get_recent_security_events(
    limit=20,
):
    dataframe = load_security_dataset()

    return get_recent_access_events(
        dataframe,
        limit=limit,
    )


# ============================================================
# UNAUTHORIZED ACCESS EVENTS
# ============================================================

def get_recent_unauthorized_events(
    limit=20,
):
    dataframe = load_security_dataset()

    return get_unauthorized_access_events(
        dataframe,
        limit=limit,
    )


# ============================================================
# AFTER-HOURS EVENTS
# ============================================================

def get_recent_after_hours_events(
    limit=20,
):
    dataframe = load_security_dataset()

    return get_after_hours_events(
        dataframe,
        limit=limit,
    )


# ============================================================
# CCTV EVENTS
# ============================================================

def get_recent_cctv_events(
    limit=20,
):
    dataframe = load_security_dataset()

    return get_cctv_events(
        dataframe,
        limit=limit,
    )


# ============================================================
# SECURITY ALERT EVENTS FROM ANALYTICS
# ============================================================

def get_recent_security_alert_events(
    limit=20,
):
    dataframe = load_security_dataset()

    return get_security_alerts(
        dataframe,
        limit=limit,
    )


# ============================================================
# ACCESS POINT SUMMARY
# ============================================================

def get_security_access_points():
    dataframe = load_security_dataset()

    return get_access_point_summary(
        dataframe
    )


# ============================================================
# BUILDING SECURITY COMPARISON
# ============================================================

def get_security_buildings():
    dataframe = load_security_dataset()

    return get_building_security_comparison(
        dataframe
    )


# ============================================================
# HOURLY SECURITY PATTERN
# ============================================================

def get_security_hourly_pattern():
    dataframe = load_security_dataset()

    return get_hourly_security_pattern(
        dataframe
    )


# ============================================================
# VISITOR MOVEMENT
# ============================================================

def get_security_visitor_movement():
    dataframe = load_security_dataset()

    return get_visitor_movement(
        dataframe
    )


# ============================================================
# SECURITY INSIGHTS
# ============================================================

def get_security_insights():
    dataframe = load_security_dataset()

    return generate_security_insights(
        dataframe
    )


# ============================================================
# DATABASE SECURITY EVENTS
# ============================================================

def get_database_security_events(
    event_id=None,
    building=None,
    access_point_id=None,
    severity=None,
    limit=500,
):
    return get_security_events(
        event_id=event_id,
        building=building,
        access_point_id=access_point_id,
        severity=severity,
        limit=limit,
    )


# ============================================================
# DATABASE SECURITY ALERTS
# ============================================================

def get_database_security_alerts(
    limit=50,
    status=None,
):
    return get_security_alerts_db(
        limit=limit,
        status=status,
    )


# ============================================================
# UPDATE SECURITY ALERT STATUS
# ============================================================

def change_security_alert_status(
    alert_id,
    status,
):
    return update_security_alert_status(
        alert_id,
        status,
    )


# ============================================================
# SERVICE TEST
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("FACILITYOPS AI - SECURITY SERVICE")
    print("=" * 60)

    sync_result = sync_security_data()

    print("\nSecurity Database Sync")
    print("-" * 60)

    for key, value in sync_result.items():
        print(f"{key}: {value}")

    dashboard = get_security_dashboard()

    print("\nSecurity Summary")
    print("-" * 60)

    for key, value in dashboard["summary"].items():
        print(f"{key}: {value}")

    print("\nAccess Points")
    print("-" * 60)

    print(
        "Access Points:",
        len(
            dashboard["access_points"]
        ),
    )

    print("\nSecurity Service completed successfully.")