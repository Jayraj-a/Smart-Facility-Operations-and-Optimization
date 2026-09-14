from pathlib import Path

import pandas as pd


# ============================================================
# FACILITYOPS AI
# MILESTONE 3 - SECURITY ANALYTICS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "milestone3_security_dataset.csv"
)


# ============================================================
# HELPERS
# ============================================================

def safe_int(value, default=0):
    try:
        if pd.isna(value):
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_float(value, default=0.0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def format_timestamp(value):
    if value is None:
        return None

    try:
        return pd.to_datetime(value).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    except Exception:
        return str(value)


# ============================================================
# LOAD SECURITY DATA
# ============================================================

def load_security_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Security dataset not found: {DATA_FILE}"
        )

    dataframe = pd.read_csv(DATA_FILE)

    dataframe["timestamp"] = pd.to_datetime(
        dataframe["timestamp"],
        errors="coerce",
    )

    dataframe = dataframe.dropna(
        subset=["timestamp"]
    )

    numeric_columns = [
        "after_hours",
        "unauthorized_attempt",
        "forced_entry",
        "tailgating_detected",
        "security_alert",
    ]

    for column in numeric_columns:
        if column in dataframe.columns:
            dataframe[column] = (
                pd.to_numeric(
                    dataframe[column],
                    errors="coerce",
                )
                .fillna(0)
                .astype(int)
            )

    dataframe = dataframe.sort_values(
        "timestamp"
    ).reset_index(drop=True)

    return dataframe


# ============================================================
# FILTER SECURITY DATA
# ============================================================

def filter_security_data(
    dataframe,
    facility_id=None,
    building_name=None,
    block_name=None,
    access_point_id=None,
    severity=None,
    access_status=None,
    user_type=None,
    start_time=None,
    end_time=None,
):
    filtered = dataframe.copy()

    if facility_id:
        filtered = filtered[
            filtered["facility_id"]
            == facility_id
        ]

    if building_name:
        filtered = filtered[
            filtered["building_name"]
            == building_name
        ]

    if block_name:
        filtered = filtered[
            filtered["block_name"]
            == block_name
        ]

    if access_point_id:
        filtered = filtered[
            filtered["access_point_id"]
            == access_point_id
        ]

    if severity:
        filtered = filtered[
            filtered["severity"]
            == severity
        ]

    if access_status:
        filtered = filtered[
            filtered["access_status"]
            == access_status
        ]

    if user_type:
        filtered = filtered[
            filtered["user_type"]
            == user_type
        ]

    if start_time is not None:
        start_time = pd.to_datetime(
            start_time
        )

        filtered = filtered[
            filtered["timestamp"]
            >= start_time
        ]

    if end_time is not None:
        end_time = pd.to_datetime(
            end_time
        )

        filtered = filtered[
            filtered["timestamp"]
            <= end_time
        ]

    return filtered.reset_index(drop=True)


# ============================================================
# SECURITY SUMMARY
# ============================================================

def calculate_security_summary(dataframe):
    if dataframe.empty:
        return {
            "total_events": 0,
            "access_points": 0,
            "granted_access": 0,
            "denied_access": 0,
            "unauthorized_attempts": 0,
            "after_hours_events": 0,
            "forced_entry_events": 0,
            "tailgating_events": 0,
            "security_alerts": 0,
            "critical_events": 0,
            "high_events": 0,
            "medium_events": 0,
            "visitors_tracked": 0,
            "visitor_events": 0,
        }

    granted = int(
        (
            dataframe["access_status"]
            == "GRANTED"
        ).sum()
    )

    denied = int(
        (
            dataframe["access_status"]
            == "DENIED"
        ).sum()
    )

    unauthorized = int(
        dataframe[
            "unauthorized_attempt"
        ].sum()
    )

    after_hours = int(
        dataframe["after_hours"].sum()
    )

    forced_entry = int(
        dataframe["forced_entry"].sum()
    )

    tailgating = int(
        dataframe[
            "tailgating_detected"
        ].sum()
    )

    alerts = int(
        dataframe["security_alert"].sum()
    )

    critical = int(
        (
            dataframe["severity"]
            == "CRITICAL"
        ).sum()
    )

    high = int(
        (
            dataframe["severity"]
            == "HIGH"
        ).sum()
    )

    medium = int(
        (
            dataframe["severity"]
            == "MEDIUM"
        ).sum()
    )

    visitor_data = dataframe[
        dataframe["user_type"]
        == "VISITOR"
    ]

    return {
        "total_events": int(
            len(dataframe)
        ),
        "access_points": int(
            dataframe[
                "access_point_id"
            ].nunique()
        ),
        "granted_access": granted,
        "denied_access": denied,
        "unauthorized_attempts": unauthorized,
        "after_hours_events": after_hours,
        "forced_entry_events": forced_entry,
        "tailgating_events": tailgating,
        "security_alerts": alerts,
        "critical_events": critical,
        "high_events": high,
        "medium_events": medium,
        "visitors_tracked": int(
            visitor_data[
                "user_id"
            ].nunique()
        ),
        "visitor_events": int(
            len(visitor_data)
        ),
    }


# ============================================================
# RECENT ACCESS EVENTS
# ============================================================

def get_recent_access_events(
    dataframe,
    limit=100,
):
    if dataframe.empty:
        return []

    events = (
        dataframe
        .sort_values(
            "timestamp",
            ascending=False,
        )
        .head(limit)
    )

    records = []

    for _, row in events.iterrows():
        records.append(
            {
                "event_id": row[
                    "event_id"
                ],
                "timestamp":
                    format_timestamp(
                        row["timestamp"]
                    ),
                "building_name": row[
                    "building_name"
                ],
                "block_name": row[
                    "block_name"
                ],
                "access_point_id": row[
                    "access_point_id"
                ],
                "access_point_name": row[
                    "access_point_name"
                ],
                "zone_type": row[
                    "zone_type"
                ],
                "user_id": row[
                    "user_id"
                ],
                "user_name": row[
                    "user_name"
                ],
                "user_type": row[
                    "user_type"
                ],
                "event_type": row[
                    "event_type"
                ],
                "access_status": row[
                    "access_status"
                ],
                "after_hours": bool(
                    safe_int(
                        row["after_hours"]
                    )
                ),
                "severity": row[
                    "severity"
                ],
            }
        )

    return records


# ============================================================
# UNAUTHORIZED ACCESS EVENTS
# ============================================================

def get_unauthorized_access_events(
    dataframe,
    limit=100,
):
    if dataframe.empty:
        return []

    events = dataframe[
        dataframe[
            "unauthorized_attempt"
        ] == 1
    ].copy()

    events = events.sort_values(
        "timestamp",
        ascending=False,
    ).head(limit)

    records = []

    for _, row in events.iterrows():
        records.append(
            {
                "event_id": row[
                    "event_id"
                ],
                "timestamp":
                    format_timestamp(
                        row["timestamp"]
                    ),
                "building_name": row[
                    "building_name"
                ],
                "block_name": row[
                    "block_name"
                ],
                "access_point_name": row[
                    "access_point_name"
                ],
                "zone_type": row[
                    "zone_type"
                ],
                "user_id": row[
                    "user_id"
                ],
                "user_name": row[
                    "user_name"
                ],
                "user_type": row[
                    "user_type"
                ],
                "access_status": row[
                    "access_status"
                ],
                "after_hours": bool(
                    safe_int(
                        row["after_hours"]
                    )
                ),
                "cctv_event": row[
                    "cctv_event"
                ],
                "severity": row[
                    "severity"
                ],
            }
        )

    return records


# ============================================================
# AFTER-HOURS ACTIVITY
# ============================================================

def get_after_hours_events(
    dataframe,
    limit=100,
):
    if dataframe.empty:
        return []

    events = dataframe[
        dataframe["after_hours"] == 1
    ].copy()

    events = events.sort_values(
        "timestamp",
        ascending=False,
    ).head(limit)

    records = []

    for _, row in events.iterrows():
        records.append(
            {
                "event_id": row[
                    "event_id"
                ],
                "timestamp":
                    format_timestamp(
                        row["timestamp"]
                    ),
                "building_name": row[
                    "building_name"
                ],
                "access_point_name": row[
                    "access_point_name"
                ],
                "user_id": row[
                    "user_id"
                ],
                "user_name": row[
                    "user_name"
                ],
                "user_type": row[
                    "user_type"
                ],
                "event_type": row[
                    "event_type"
                ],
                "access_status": row[
                    "access_status"
                ],
                "severity": row[
                    "severity"
                ],
            }
        )

    return records


# ============================================================
# CCTV EVENTS
# ============================================================

def get_cctv_events(
    dataframe,
    limit=100,
):
    if dataframe.empty:
        return []

    events = dataframe[
        dataframe["cctv_event"]
        != "NORMAL"
    ].copy()

    events = events.sort_values(
        "timestamp",
        ascending=False,
    ).head(limit)

    records = []

    for _, row in events.iterrows():
        records.append(
            {
                "event_id": row[
                    "event_id"
                ],
                "timestamp":
                    format_timestamp(
                        row["timestamp"]
                    ),
                "building_name": row[
                    "building_name"
                ],
                "access_point_name": row[
                    "access_point_name"
                ],
                "zone_type": row[
                    "zone_type"
                ],
                "user_id": row[
                    "user_id"
                ],
                "user_type": row[
                    "user_type"
                ],
                "cctv_event": row[
                    "cctv_event"
                ],
                "severity": row[
                    "severity"
                ],
            }
        )

    return records


# ============================================================
# SECURITY ALERTS
# ============================================================

def get_security_alerts(
    dataframe,
    limit=100,
):
    if dataframe.empty:
        return []

    alerts = dataframe[
        dataframe[
            "security_alert"
        ] == 1
    ].copy()

    severity_order = {
        "CRITICAL": 4,
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
        "NORMAL": 0,
    }

    alerts[
        "_severity_order"
    ] = alerts["severity"].map(
        severity_order
    ).fillna(0)

    alerts = alerts.sort_values(
        [
            "_severity_order",
            "timestamp",
        ],
        ascending=[
            False,
            False,
        ],
    ).head(limit)

    records = []

    for _, row in alerts.iterrows():
        records.append(
            {
                "event_id": row[
                    "event_id"
                ],
                "timestamp":
                    format_timestamp(
                        row["timestamp"]
                    ),
                "building_name": row[
                    "building_name"
                ],
                "block_name": row[
                    "block_name"
                ],
                "access_point_name": row[
                    "access_point_name"
                ],
                "zone_type": row[
                    "zone_type"
                ],
                "user_id": row[
                    "user_id"
                ],
                "user_name": row[
                    "user_name"
                ],
                "user_type": row[
                    "user_type"
                ],
                "event_type": row[
                    "event_type"
                ],
                "access_status": row[
                    "access_status"
                ],
                "after_hours": bool(
                    safe_int(
                        row["after_hours"]
                    )
                ),
                "unauthorized_attempt":
                    bool(
                        safe_int(
                            row[
                                "unauthorized_attempt"
                            ]
                        )
                    ),
                "forced_entry": bool(
                    safe_int(
                        row[
                            "forced_entry"
                        ]
                    )
                ),
                "tailgating_detected":
                    bool(
                        safe_int(
                            row[
                                "tailgating_detected"
                            ]
                        )
                    ),
                "cctv_event": row[
                    "cctv_event"
                ],
                "severity": row[
                    "severity"
                ],
            }
        )

    return records


# ============================================================
# ACCESS POINT ANALYTICS
# ============================================================

def get_access_point_summary(
    dataframe,
):
    if dataframe.empty:
        return []

    grouped = (
        dataframe
        .groupby(
            [
                "access_point_id",
                "access_point_name",
                "building_name",
                "block_name",
                "zone_type",
            ]
        )
        .agg(
            total_events=(
                "event_id",
                "count",
            ),
            unauthorized_attempts=(
                "unauthorized_attempt",
                "sum",
            ),
            after_hours_events=(
                "after_hours",
                "sum",
            ),
            security_alerts=(
                "security_alert",
                "sum",
            ),
            forced_entries=(
                "forced_entry",
                "sum",
            ),
            tailgating_events=(
                "tailgating_detected",
                "sum",
            ),
        )
        .reset_index()
    )

    records = []

    for _, row in grouped.iterrows():
        records.append(
            {
                "access_point_id": row[
                    "access_point_id"
                ],
                "access_point_name": row[
                    "access_point_name"
                ],
                "building_name": row[
                    "building_name"
                ],
                "block_name": row[
                    "block_name"
                ],
                "zone_type": row[
                    "zone_type"
                ],
                "total_events": safe_int(
                    row["total_events"]
                ),
                "unauthorized_attempts":
                    safe_int(
                        row[
                            "unauthorized_attempts"
                        ]
                    ),
                "after_hours_events":
                    safe_int(
                        row[
                            "after_hours_events"
                        ]
                    ),
                "security_alerts":
                    safe_int(
                        row[
                            "security_alerts"
                        ]
                    ),
                "forced_entries":
                    safe_int(
                        row[
                            "forced_entries"
                        ]
                    ),
                "tailgating_events":
                    safe_int(
                        row[
                            "tailgating_events"
                        ]
                    ),
            }
        )

    records.sort(
        key=lambda item: (
            item["security_alerts"],
            item[
                "unauthorized_attempts"
            ],
        ),
        reverse=True,
    )

    return records


# ============================================================
# BUILDING SECURITY COMPARISON
# ============================================================

def get_building_security_comparison(
    dataframe,
):
    if dataframe.empty:
        return []

    grouped = (
        dataframe
        .groupby("building_name")
        .agg(
            total_events=(
                "event_id",
                "count",
            ),
            unauthorized_attempts=(
                "unauthorized_attempt",
                "sum",
            ),
            after_hours_events=(
                "after_hours",
                "sum",
            ),
            forced_entries=(
                "forced_entry",
                "sum",
            ),
            tailgating_events=(
                "tailgating_detected",
                "sum",
            ),
            security_alerts=(
                "security_alert",
                "sum",
            ),
        )
        .reset_index()
    )

    records = []

    for _, row in grouped.iterrows():
        total = safe_int(
            row["total_events"]
        )

        alerts = safe_int(
            row["security_alerts"]
        )

        alert_rate = (
            alerts / total * 100
            if total > 0
            else 0.0
        )

        records.append(
            {
                "building_name": row[
                    "building_name"
                ],
                "total_events": total,
                "unauthorized_attempts":
                    safe_int(
                        row[
                            "unauthorized_attempts"
                        ]
                    ),
                "after_hours_events":
                    safe_int(
                        row[
                            "after_hours_events"
                        ]
                    ),
                "forced_entries":
                    safe_int(
                        row[
                            "forced_entries"
                        ]
                    ),
                "tailgating_events":
                    safe_int(
                        row[
                            "tailgating_events"
                        ]
                    ),
                "security_alerts": alerts,
                "alert_rate_percent":
                    round(
                        alert_rate,
                        2,
                    ),
            }
        )

    records.sort(
        key=lambda item: item[
            "security_alerts"
        ],
        reverse=True,
    )

    return records


# ============================================================
# HOURLY SECURITY PATTERN
# ============================================================

def get_hourly_security_pattern(
    dataframe,
):
    if dataframe.empty:
        return []

    working = dataframe.copy()

    working["hour"] = (
        working["timestamp"].dt.hour
    )

    grouped = (
        working
        .groupby("hour")
        .agg(
            access_events=(
                "event_id",
                "count",
            ),
            unauthorized_attempts=(
                "unauthorized_attempt",
                "sum",
            ),
            security_alerts=(
                "security_alert",
                "sum",
            ),
        )
        .reset_index()
    )

    records = []

    for _, row in grouped.iterrows():
        records.append(
            {
                "hour": safe_int(
                    row["hour"]
                ),
                "access_events": safe_int(
                    row["access_events"]
                ),
                "unauthorized_attempts":
                    safe_int(
                        row[
                            "unauthorized_attempts"
                        ]
                    ),
                "security_alerts":
                    safe_int(
                        row[
                            "security_alerts"
                        ]
                    ),
            }
        )

    return records


# ============================================================
# VISITOR MOVEMENT
# ============================================================

def get_visitor_movement(
    dataframe,
    limit=100,
):
    if dataframe.empty:
        return []

    visitors = dataframe[
        dataframe["user_type"]
        == "VISITOR"
    ].copy()

    visitors = visitors.sort_values(
        "timestamp",
        ascending=False,
    ).head(limit)

    records = []

    for _, row in visitors.iterrows():
        records.append(
            {
                "event_id": row[
                    "event_id"
                ],
                "timestamp":
                    format_timestamp(
                        row["timestamp"]
                    ),
                "visitor_id": row[
                    "user_id"
                ],
                "visitor_name": row[
                    "user_name"
                ],
                "building_name": row[
                    "building_name"
                ],
                "block_name": row[
                    "block_name"
                ],
                "access_point_name": row[
                    "access_point_name"
                ],
                "zone_type": row[
                    "zone_type"
                ],
                "access_status": row[
                    "access_status"
                ],
                "after_hours": bool(
                    safe_int(
                        row["after_hours"]
                    )
                ),
                "severity": row[
                    "severity"
                ],
            }
        )

    return records


# ============================================================
# INCIDENT INVESTIGATION DATA
# ============================================================

def get_incident_details(
    dataframe,
    event_id,
):
    if dataframe.empty:
        return None

    matching = dataframe[
        dataframe["event_id"]
        == event_id
    ]

    if matching.empty:
        return None

    row = matching.iloc[0]

    user_id = row["user_id"]

    timestamp = row["timestamp"]

    window_start = (
        timestamp
        - pd.Timedelta(hours=2)
    )

    window_end = (
        timestamp
        + pd.Timedelta(hours=2)
    )

    related_activity = dataframe[
        (
            dataframe["user_id"]
            == user_id
        )
        &
        (
            dataframe["timestamp"]
            >= window_start
        )
        &
        (
            dataframe["timestamp"]
            <= window_end
        )
    ].sort_values(
        "timestamp"
    )

    related_records = []

    for _, related in (
        related_activity.iterrows()
    ):
        related_records.append(
            {
                "event_id": related[
                    "event_id"
                ],
                "timestamp":
                    format_timestamp(
                        related[
                            "timestamp"
                        ]
                    ),
                "access_point_name":
                    related[
                        "access_point_name"
                    ],
                "building_name":
                    related[
                        "building_name"
                    ],
                "event_type":
                    related[
                        "event_type"
                    ],
                "access_status":
                    related[
                        "access_status"
                    ],
                "severity":
                    related[
                        "severity"
                    ],
            }
        )

    return {
        "event_id": row[
            "event_id"
        ],
        "timestamp":
            format_timestamp(
                row["timestamp"]
            ),
        "user_id": row[
            "user_id"
        ],
        "user_name": row[
            "user_name"
        ],
        "user_type": row[
            "user_type"
        ],
        "building_name": row[
            "building_name"
        ],
        "block_name": row[
            "block_name"
        ],
        "access_point_name": row[
            "access_point_name"
        ],
        "zone_type": row[
            "zone_type"
        ],
        "event_type": row[
            "event_type"
        ],
        "access_status": row[
            "access_status"
        ],
        "after_hours": bool(
            safe_int(
                row["after_hours"]
            )
        ),
        "unauthorized_attempt":
            bool(
                safe_int(
                    row[
                        "unauthorized_attempt"
                    ]
                )
            ),
        "forced_entry": bool(
            safe_int(
                row["forced_entry"]
            )
        ),
        "tailgating_detected":
            bool(
                safe_int(
                    row[
                        "tailgating_detected"
                    ]
                )
            ),
        "cctv_event": row[
            "cctv_event"
        ],
        "severity": row[
            "severity"
        ],
        "related_user_activity":
            related_records,
    }


# ============================================================
# SECURITY INSIGHTS
# ============================================================

def generate_security_insights(
    dataframe,
):
    summary = (
        calculate_security_summary(
            dataframe
        )
    )

    access_points = (
        get_access_point_summary(
            dataframe
        )
    )

    insights = []

    if summary[
        "critical_events"
    ] > 0:
        insights.append(
            {
                "type":
                    "CRITICAL_SECURITY",
                "severity": "CRITICAL",
                "title":
                    "Critical Security Events",
                "message": (
                    f"{summary['critical_events']} "
                    f"critical security events "
                    f"were detected."
                ),
            }
        )

    if summary[
        "unauthorized_attempts"
    ] > 0:
        insights.append(
            {
                "type":
                    "UNAUTHORIZED_ACCESS",
                "severity": "HIGH",
                "title":
                    "Unauthorized Access Attempts",
                "message": (
                    f"{summary['unauthorized_attempts']} "
                    f"unauthorized access attempts "
                    f"were identified."
                ),
            }
        )

    if summary[
        "after_hours_events"
    ] > 0:
        insights.append(
            {
                "type":
                    "AFTER_HOURS_ACTIVITY",
                "severity": "INFO",
                "title":
                    "After-Hours Activity",
                "message": (
                    f"{summary['after_hours_events']} "
                    f"access events occurred "
                    f"outside normal operating hours."
                ),
            }
        )

    if summary[
        "forced_entry_events"
    ] > 0:
        insights.append(
            {
                "type": "FORCED_ENTRY",
                "severity": "CRITICAL",
                "title":
                    "Forced Entry Events",
                "message": (
                    f"{summary['forced_entry_events']} "
                    f"forced-entry events require "
                    f"security review."
                ),
            }
        )

    if summary[
        "tailgating_events"
    ] > 0:
        insights.append(
            {
                "type": "TAILGATING",
                "severity": "HIGH",
                "title":
                    "Tailgating Detected",
                "message": (
                    f"{summary['tailgating_events']} "
                    f"tailgating events were "
                    f"identified by simulated "
                    f"CCTV monitoring."
                ),
            }
        )

    if access_points:
        highest_risk = access_points[0]

        insights.append(
            {
                "type":
                    "ACCESS_POINT_RISK",
                "severity": "INFO",
                "title":
                    "Highest Alert Access Point",
                "message": (
                    f"{highest_risk['access_point_name']} "
                    f"recorded "
                    f"{highest_risk['security_alerts']} "
                    f"security alerts."
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
    print("SECURITY ANALYTICS")
    print("=" * 60)

    dataframe = load_security_data()

    print()
    print(
        f"Dataset rows: {len(dataframe)}"
    )

    print(
        "Access points:",
        dataframe[
            "access_point_id"
        ].nunique(),
    )

    summary = (
        calculate_security_summary(
            dataframe
        )
    )

    print()
    print("Security Summary")
    print("-" * 60)

    for key, value in summary.items():
        print(
            f"{key}: {value}"
        )

    print()
    print("Building Security Comparison")
    print("-" * 60)

    buildings = (
        get_building_security_comparison(
            dataframe
        )
    )

    for building in buildings:
        print(
            f"{building['building_name']} | "
            f"Events: "
            f"{building['total_events']} | "
            f"Unauthorized: "
            f"{building['unauthorized_attempts']} | "
            f"Alerts: "
            f"{building['security_alerts']} | "
            f"Alert Rate: "
            f"{building['alert_rate_percent']:.2f}%"
        )

    print()
    print("Access Point Analysis")
    print("-" * 60)

    access_points = (
        get_access_point_summary(
            dataframe
        )
    )

    for point in access_points:
        print(
            f"{point['access_point_id']} | "
            f"{point['access_point_name']} | "
            f"Events: "
            f"{point['total_events']} | "
            f"Unauthorized: "
            f"{point['unauthorized_attempts']} | "
            f"Alerts: "
            f"{point['security_alerts']}"
        )

    print()
    print("Recent Unauthorized Access")
    print("-" * 60)

    unauthorized = (
        get_unauthorized_access_events(
            dataframe,
            limit=5,
        )
    )

    for event in unauthorized:
        print(
            f"[{event['severity']}] "
            f"{event['timestamp']} | "
            f"{event['access_point_name']} | "
            f"{event['user_type']} | "
            f"{event['user_id']}"
        )

    print()
    print("Recent CCTV Events")
    print("-" * 60)

    cctv_events = get_cctv_events(
        dataframe,
        limit=5,
    )

    for event in cctv_events:
        print(
            f"[{event['severity']}] "
            f"{event['timestamp']} | "
            f"{event['access_point_name']} | "
            f"{event['cctv_event']}"
        )

    print()
    print("Security Insights")
    print("-" * 60)

    insights = (
        generate_security_insights(
            dataframe
        )
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
        "Security analytics completed successfully."
    )
    print("=" * 60)


if __name__ == "__main__":
    main()