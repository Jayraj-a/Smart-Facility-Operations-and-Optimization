from pathlib import Path
import sqlite3
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_FILE = PROJECT_ROOT / "backend" / "facilityops.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    return connection


# ============================================================
# HELPER
# ============================================================

def safe_float(value):
    try:
        if value is None:
            return None

        return float(value)

    except (TypeError, ValueError):
        return None


# ============================================================
# INITIALISE DATABASE
# ============================================================

def initialise_monitoring_database():

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # ====================================================
        # MILESTONE 1
        # ENERGY READINGS
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS energy_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                facility_id TEXT,
                facility_name TEXT,

                building_id TEXT,
                building_name TEXT,

                block_id TEXT,
                block_name TEXT,

                timestamp TEXT NOT NULL,

                electricity_kwh REAL,
                water_liters REAL,
                hvac_kwh REAL,
                lighting_kwh REAL,
                temperature_c REAL,
                occupancy REAL,

                created_at TEXT NOT NULL,

                UNIQUE(
                    timestamp,
                    building_name,
                    block_name
                )
            )
        """)

        # ====================================================
        # MILESTONE 1
        # ALERTS / ISSUES
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                created_at TEXT NOT NULL,
                source_timestamp TEXT,

                facility_id TEXT,
                facility_name TEXT,

                building_id TEXT,
                building_name TEXT,

                block_id TEXT,
                block_name TEXT,

                alert_type TEXT,
                metric TEXT,

                observed_value REAL,
                expected_value REAL,
                change_percent REAL,

                severity TEXT,

                title TEXT NOT NULL,
                message TEXT,

                status TEXT DEFAULT 'OPEN',

                UNIQUE(
                    source_timestamp,
                    building_name,
                    block_name,
                    alert_type,
                    metric,
                    title
                )
            )
        """)

        # ====================================================
        # MILESTONE 1
        # DAILY SUMMARIES
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                summary_date TEXT NOT NULL,

                facility_name TEXT,
                building_name TEXT,
                block_name TEXT,

                total_electricity REAL,
                average_electricity REAL,
                peak_electricity REAL,

                average_hvac REAL,
                average_lighting REAL,

                total_water REAL,
                average_temperature REAL,
                average_occupancy REAL,

                issue_count INTEGER DEFAULT 0,

                updated_at TEXT NOT NULL,

                UNIQUE(
                    summary_date,
                    building_name,
                    block_name
                )
            )
        """)

        # ====================================================
        # MILESTONE 2
        # ASSETS
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                asset_id TEXT NOT NULL UNIQUE,
                asset_name TEXT,
                asset_type TEXT,

                facility_id TEXT,
                facility_name TEXT,

                building_name TEXT,
                block_name TEXT,

                age_years REAL,

                status TEXT DEFAULT 'ACTIVE',

                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # ====================================================
        # MILESTONE 2
        # ASSET MONITORING READINGS
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS asset_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                asset_id TEXT NOT NULL,
                asset_name TEXT,
                asset_type TEXT,

                facility_id TEXT,
                facility_name TEXT,

                building_name TEXT,
                block_name TEXT,

                timestamp TEXT NOT NULL,

                temperature_c REAL,
                vibration_mm_s REAL,
                pressure_bar REAL,
                power_kw REAL,

                runtime_hours REAL,
                operating_hours REAL,
                age_years REAL,
                days_since_service REAL,

                generated_health_score REAL,
                generated_health_status TEXT,

                abnormal_behavior INTEGER DEFAULT 0,
                maintenance_required INTEGER DEFAULT 0,
                days_to_maintenance INTEGER,

                created_at TEXT NOT NULL,

                UNIQUE(
                    asset_id,
                    timestamp
                )
            )
        """)

        # ====================================================
        # MILESTONE 2
        # MAINTENANCE PREDICTIONS
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS maintenance_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                asset_id TEXT NOT NULL,
                asset_name TEXT,
                asset_type TEXT,

                building_name TEXT,
                block_name TEXT,

                source_timestamp TEXT NOT NULL,

                health_score REAL,
                health_status TEXT,

                maintenance_required INTEGER DEFAULT 0,

                maintenance_probability REAL,
                maintenance_probability_percent REAL,

                risk_level TEXT,
                priority TEXT,

                recommended_maintenance_date TEXT,
                days_until_service INTEGER,

                created_at TEXT NOT NULL,

                UNIQUE(
                    asset_id,
                    source_timestamp
                )
            )
        """)

        # ====================================================
        # MILESTONE 2
        # MAINTENANCE ALERTS
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS maintenance_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                asset_id TEXT NOT NULL,
                asset_name TEXT,
                asset_type TEXT,

                building_name TEXT,
                block_name TEXT,

                source_timestamp TEXT,

                severity TEXT,

                title TEXT NOT NULL,
                message TEXT,

                health_score REAL,
                health_status TEXT,

                maintenance_probability REAL,
                maintenance_probability_percent REAL,

                recommended_maintenance_date TEXT,
                days_until_service INTEGER,

                status TEXT DEFAULT 'OPEN',

                created_at TEXT NOT NULL,

                UNIQUE(
                    asset_id,
                    source_timestamp,
                    title
                )
            )
        """)

        # ====================================================
        # MILESTONE 2
        # MAINTENANCE WORK ORDERS
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS maintenance_work_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                asset_id TEXT NOT NULL,
                asset_name TEXT,
                asset_type TEXT,

                building_name TEXT,
                block_name TEXT,

                priority TEXT,

                recommended_date TEXT,

                reason TEXT,

                status TEXT DEFAULT 'RECOMMENDED',

                source_timestamp TEXT,

                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,

                UNIQUE(
                    asset_id,
                    source_timestamp
                )
            )
        """)

        connection.commit()

    finally:

        connection.close()


# ============================================================
# MILESTONE 1
# SAVE ENERGY READING
# ============================================================

def save_energy_reading(reading):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT OR IGNORE INTO energy_readings (

                facility_id,
                facility_name,

                building_id,
                building_name,

                block_id,
                block_name,

                timestamp,

                electricity_kwh,
                water_liters,
                hvac_kwh,
                lighting_kwh,
                temperature_c,
                occupancy,

                created_at

            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(reading.get("facility_id", "")),
                str(reading.get("facility_name", "")),

                str(reading.get("building_id", "")),
                str(reading.get("building_name", "")),

                str(reading.get("block_id", "")),
                str(reading.get("block_name", "")),

                str(reading.get("timestamp", "")),

                float(reading.get("electricity_kwh", 0) or 0),
                float(reading.get("water_liters", 0) or 0),
                float(reading.get("hvac_kwh", 0) or 0),
                float(reading.get("lighting_kwh", 0) or 0),
                float(reading.get("temperature_c", 0) or 0),
                float(reading.get("occupancy", 0) or 0),

                datetime.now().isoformat(),
            ),
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:

        connection.close()


# ============================================================
# MILESTONE 1
# BATCH SAVE ENERGY READINGS
# ============================================================

def save_energy_readings_batch(readings):

    inserted = 0

    connection = get_connection()

    try:

        cursor = connection.cursor()

        for reading in readings:

            cursor.execute(
                """
                INSERT OR IGNORE INTO energy_readings (

                    facility_id,
                    facility_name,

                    building_id,
                    building_name,

                    block_id,
                    block_name,

                    timestamp,

                    electricity_kwh,
                    water_liters,
                    hvac_kwh,
                    lighting_kwh,
                    temperature_c,
                    occupancy,

                    created_at

                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(reading.get("facility_id", "")),
                    str(reading.get("facility_name", "")),

                    str(reading.get("building_id", "")),
                    str(reading.get("building_name", "")),

                    str(reading.get("block_id", "")),
                    str(reading.get("block_name", "")),

                    str(reading.get("timestamp", "")),

                    float(reading.get("electricity_kwh", 0) or 0),
                    float(reading.get("water_liters", 0) or 0),
                    float(reading.get("hvac_kwh", 0) or 0),
                    float(reading.get("lighting_kwh", 0) or 0),
                    float(reading.get("temperature_c", 0) or 0),
                    float(reading.get("occupancy", 0) or 0),

                    datetime.now().isoformat(),
                ),
            )

            if cursor.rowcount > 0:
                inserted += 1

        connection.commit()

        return inserted

    finally:

        connection.close()


# ============================================================
# MILESTONE 1
# GET HISTORICAL ENERGY READINGS
# ============================================================

def get_historical_readings(
    building=None,
    block=None,
    limit=500
):

    connection = get_connection()

    try:

        query = """
            SELECT *
            FROM energy_readings
            WHERE 1 = 1
        """

        params = []

        if building:
            query += " AND building_name = ?"
            params.append(building)

        if block:
            query += " AND block_name = ?"
            params.append(block)

        query += """
            ORDER BY timestamp DESC
            LIMIT ?
        """

        params.append(int(limit))

        rows = connection.execute(
            query,
            params
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        connection.close()


# ============================================================
# MILESTONE 1
# CREATE ALERT
# ============================================================

def create_alert(alert):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT OR IGNORE INTO alerts (

                created_at,
                source_timestamp,

                facility_id,
                facility_name,

                building_id,
                building_name,

                block_id,
                block_name,

                alert_type,
                metric,

                observed_value,
                expected_value,
                change_percent,

                severity,

                title,
                message,

                status

            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                alert.get(
                    "created_at",
                    datetime.now().isoformat()
                ),

                str(
                    alert.get(
                        "source_timestamp",
                        ""
                    )
                ),

                str(alert.get("facility_id", "")),
                str(alert.get("facility_name", "")),

                str(alert.get("building_id", "")),
                str(alert.get("building_name", "")),

                str(alert.get("block_id", "")),
                str(alert.get("block_name", "")),

                str(alert.get("alert_type", "ENERGY")),
                str(alert.get("metric", "energy")),

                safe_float(
                    alert.get("observed_value")
                ),

                safe_float(
                    alert.get("expected_value")
                ),

                safe_float(
                    alert.get("change_percent")
                ),

                str(alert.get("severity", "WARNING")),

                str(
                    alert.get(
                        "title",
                        "Facility Energy Issue"
                    )
                ),

                str(
                    alert.get(
                        "message",
                        ""
                    )
                ),

                str(
                    alert.get(
                        "status",
                        "OPEN"
                    )
                ),
            ),
        )

        connection.commit()

        if cursor.rowcount == 0:
            return None

        return cursor.lastrowid

    finally:

        connection.close()


# ============================================================
# MILESTONE 1
# GET ALERTS
# ============================================================

def get_alerts(
    limit=50,
    status=None
):

    connection = get_connection()

    try:

        query = """
            SELECT *
            FROM alerts
            WHERE 1 = 1
        """

        params = []

        if status:
            query += " AND status = ?"
            params.append(status.upper())

        query += """
            ORDER BY created_at DESC
            LIMIT ?
        """

        params.append(int(limit))

        rows = connection.execute(
            query,
            params
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        connection.close()


# ============================================================
# MILESTONE 1
# UPDATE ALERT STATUS
# ============================================================

def update_alert_status(
    alert_id,
    status
):

    allowed = {
        "OPEN",
        "INVESTIGATING",
        "RESOLVED"
    }

    status = str(status).upper()

    if status not in allowed:
        raise ValueError(
            "Invalid alert status."
        )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE alerts
            SET status = ?
            WHERE id = ?
            """,
            (
                status,
                int(alert_id)
            ),
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:

        connection.close()


# ============================================================
# MILESTONE 1
# DAILY SUMMARY
# ============================================================

def upsert_daily_summary(summary):

    connection = get_connection()

    try:

        connection.execute(
            """
            INSERT INTO daily_summaries (

                summary_date,

                facility_name,
                building_name,
                block_name,

                total_electricity,
                average_electricity,
                peak_electricity,

                average_hvac,
                average_lighting,

                total_water,
                average_temperature,
                average_occupancy,

                issue_count,

                updated_at

            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )

            ON CONFLICT(
                summary_date,
                building_name,
                block_name
            )

            DO UPDATE SET

                facility_name =
                    excluded.facility_name,

                total_electricity =
                    excluded.total_electricity,

                average_electricity =
                    excluded.average_electricity,

                peak_electricity =
                    excluded.peak_electricity,

                average_hvac =
                    excluded.average_hvac,

                average_lighting =
                    excluded.average_lighting,

                total_water =
                    excluded.total_water,

                average_temperature =
                    excluded.average_temperature,

                average_occupancy =
                    excluded.average_occupancy,

                issue_count =
                    excluded.issue_count,

                updated_at =
                    excluded.updated_at
            """,
            (
                summary.get("summary_date"),

                summary.get("facility_name", ""),
                summary.get("building_name", ""),
                summary.get("block_name", ""),

                safe_float(
                    summary.get(
                        "total_electricity"
                    )
                ),

                safe_float(
                    summary.get(
                        "average_electricity"
                    )
                ),

                safe_float(
                    summary.get(
                        "peak_electricity"
                    )
                ),

                safe_float(
                    summary.get(
                        "average_hvac"
                    )
                ),

                safe_float(
                    summary.get(
                        "average_lighting"
                    )
                ),

                safe_float(
                    summary.get(
                        "total_water"
                    )
                ),

                safe_float(
                    summary.get(
                        "average_temperature"
                    )
                ),

                safe_float(
                    summary.get(
                        "average_occupancy"
                    )
                ),

                int(
                    summary.get(
                        "issue_count",
                        0
                    )
                ),

                datetime.now().isoformat(),
            ),
        )

        connection.commit()

    finally:

        connection.close()


# ============================================================
# MILESTONE 1
# GET DAILY SUMMARIES
# ============================================================

def get_daily_summaries(
    building=None,
    block=None,
    limit=100
):

    connection = get_connection()

    try:

        query = """
            SELECT *
            FROM daily_summaries
            WHERE 1 = 1
        """

        params = []

        if building:
            query += " AND building_name = ?"
            params.append(building)

        if block:
            query += " AND block_name = ?"
            params.append(block)

        query += """
            ORDER BY summary_date DESC
            LIMIT ?
        """

        params.append(int(limit))

        rows = connection.execute(
            query,
            params
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        connection.close()


# ============================================================
# MILESTONE 2
# UPSERT ASSET
# ============================================================

def upsert_asset(asset):

    connection = get_connection()

    try:

        now = datetime.now().isoformat()

        connection.execute(
            """
            INSERT INTO assets (
                asset_id,
                asset_name,
                asset_type,

                facility_id,
                facility_name,

                building_name,
                block_name,

                age_years,

                status,

                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(asset_id)

            DO UPDATE SET
                asset_name = excluded.asset_name,
                asset_type = excluded.asset_type,
                facility_id = excluded.facility_id,
                facility_name = excluded.facility_name,
                building_name = excluded.building_name,
                block_name = excluded.block_name,
                age_years = excluded.age_years,
                status = excluded.status,
                updated_at = excluded.updated_at
            """,
            (
                str(asset.get("asset_id", "")),
                str(asset.get("asset_name", "")),
                str(asset.get("asset_type", "")),

                str(asset.get("facility_id", "")),
                str(asset.get("facility_name", "")),

                str(asset.get("building_name", "")),
                str(asset.get("block_name", "")),

                safe_float(
                    asset.get("age_years")
                ),

                str(
                    asset.get(
                        "status",
                        "ACTIVE"
                    )
                ),

                now,
                now,
            ),
        )

        connection.commit()

    finally:

        connection.close()


# ============================================================
# MILESTONE 2
# GET ASSETS
# ============================================================

def get_assets(
    building=None,
    asset_type=None
):

    connection = get_connection()

    try:

        query = """
            SELECT *
            FROM assets
            WHERE 1 = 1
        """

        params = []

        if building:
            query += " AND building_name = ?"
            params.append(building)

        if asset_type:
            query += " AND asset_type = ?"
            params.append(asset_type)

        query += """
            ORDER BY asset_id
        """

        rows = connection.execute(
            query,
            params
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        connection.close()


# ============================================================
# MILESTONE 2
# SAVE ASSET READING
# ============================================================

def save_asset_reading(reading):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT OR IGNORE INTO asset_readings (
                asset_id,
                asset_name,
                asset_type,

                facility_id,
                facility_name,

                building_name,
                block_name,

                timestamp,

                temperature_c,
                vibration_mm_s,
                pressure_bar,
                power_kw,

                runtime_hours,
                operating_hours,
                age_years,
                days_since_service,

                generated_health_score,
                generated_health_status,

                abnormal_behavior,
                maintenance_required,
                days_to_maintenance,

                created_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                str(reading.get("asset_id", "")),
                str(reading.get("asset_name", "")),
                str(reading.get("asset_type", "")),

                str(reading.get("facility_id", "")),
                str(reading.get("facility_name", "")),

                str(reading.get("building_name", "")),
                str(reading.get("block_name", "")),

                str(reading.get("timestamp", "")),

                safe_float(
                    reading.get("temperature_c")
                ),

                safe_float(
                    reading.get("vibration_mm_s")
                ),

                safe_float(
                    reading.get("pressure_bar")
                ),

                safe_float(
                    reading.get("power_kw")
                ),

                safe_float(
                    reading.get("runtime_hours")
                ),

                safe_float(
                    reading.get("operating_hours")
                ),

                safe_float(
                    reading.get("age_years")
                ),

                safe_float(
                    reading.get("days_since_service")
                ),

                safe_float(
                    reading.get(
                        "health_score"
                    )
                ),

                str(
                    reading.get(
                        "health_status",
                        ""
                    )
                ),

                int(
                    reading.get(
                        "abnormal_behavior",
                        0
                    )
                    or 0
                ),

                int(
                    reading.get(
                        "maintenance_required",
                        0
                    )
                    or 0
                ),

                int(
                    reading.get(
                        "days_to_maintenance",
                        0
                    )
                    or 0
                ),

                datetime.now().isoformat(),
            ),
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:

        connection.close()


# ============================================================
# MILESTONE 2
# BATCH SAVE ASSET READINGS
# ============================================================

def save_asset_readings_batch(readings):

    inserted = 0

    connection = get_connection()

    try:

        cursor = connection.cursor()

        now = datetime.now().isoformat()

        for reading in readings:

            cursor.execute(
                """
                INSERT OR IGNORE INTO asset_readings (
                    asset_id,
                    asset_name,
                    asset_type,

                    facility_id,
                    facility_name,

                    building_name,
                    block_name,

                    timestamp,

                    temperature_c,
                    vibration_mm_s,
                    pressure_bar,
                    power_kw,

                    runtime_hours,
                    operating_hours,
                    age_years,
                    days_since_service,

                    generated_health_score,
                    generated_health_status,

                    abnormal_behavior,
                    maintenance_required,
                    days_to_maintenance,

                    created_at
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    str(reading.get("asset_id", "")),
                    str(reading.get("asset_name", "")),
                    str(reading.get("asset_type", "")),

                    str(reading.get("facility_id", "")),
                    str(reading.get("facility_name", "")),

                    str(reading.get("building_name", "")),
                    str(reading.get("block_name", "")),

                    str(reading.get("timestamp", "")),

                    safe_float(
                        reading.get("temperature_c")
                    ),

                    safe_float(
                        reading.get("vibration_mm_s")
                    ),

                    safe_float(
                        reading.get("pressure_bar")
                    ),

                    safe_float(
                        reading.get("power_kw")
                    ),

                    safe_float(
                        reading.get("runtime_hours")
                    ),

                    safe_float(
                        reading.get("operating_hours")
                    ),

                    safe_float(
                        reading.get("age_years")
                    ),

                    safe_float(
                        reading.get("days_since_service")
                    ),

                    safe_float(
                        reading.get(
                            "health_score"
                        )
                    ),

                    str(
                        reading.get(
                            "health_status",
                            ""
                        )
                    ),

                    int(
                        reading.get(
                            "abnormal_behavior",
                            0
                        )
                        or 0
                    ),

                    int(
                        reading.get(
                            "maintenance_required",
                            0
                        )
                        or 0
                    ),

                    int(
                        reading.get(
                            "days_to_maintenance",
                            0
                        )
                        or 0
                    ),

                    now,
                ),
            )

            if cursor.rowcount > 0:
                inserted += 1

        connection.commit()

        return inserted

    finally:

        connection.close()


# ============================================================
# MILESTONE 2
# GET ASSET READINGS
# ============================================================

def get_asset_readings(
    asset_id=None,
    building=None,
    limit=500
):

    connection = get_connection()

    try:

        query = """
            SELECT *
            FROM asset_readings
            WHERE 1 = 1
        """

        params = []

        if asset_id:
            query += " AND asset_id = ?"
            params.append(asset_id)

        if building:
            query += " AND building_name = ?"
            params.append(building)

        query += """
            ORDER BY timestamp DESC
            LIMIT ?
        """

        params.append(int(limit))

        rows = connection.execute(
            query,
            params
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        connection.close()


# ============================================================
# MILESTONE 2
# SAVE MAINTENANCE PREDICTION
# ============================================================

def save_maintenance_prediction(prediction):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO maintenance_predictions (
                asset_id,
                asset_name,
                asset_type,

                building_name,
                block_name,

                source_timestamp,

                health_score,
                health_status,

                maintenance_required,

                maintenance_probability,
                maintenance_probability_percent,

                risk_level,
                priority,

                recommended_maintenance_date,
                days_until_service,

                created_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                str(prediction.get("asset_id", "")),
                str(prediction.get("asset_name", "")),
                str(prediction.get("asset_type", "")),

                str(prediction.get("building_name", "")),
                str(prediction.get("block_name", "")),

                str(
                    prediction.get(
                        "source_timestamp",
                        prediction.get(
                            "timestamp",
                            ""
                        )
                    )
                ),

                safe_float(
                    prediction.get("health_score")
                ),

                str(
                    prediction.get(
                        "health_status",
                        ""
                    )
                ),

                int(
                    prediction.get(
                        "maintenance_required",
                        0
                    )
                    or 0
                ),

                safe_float(
                    prediction.get(
                        "maintenance_probability"
                    )
                ),

                safe_float(
                    prediction.get(
                        "maintenance_probability_percent"
                    )
                ),

                str(
                    prediction.get(
                        "risk_level",
                        ""
                    )
                ),

                str(
                    prediction.get(
                        "priority",
                        ""
                    )
                ),

                str(
                    prediction.get(
                        "recommended_maintenance_date",
                        ""
                    )
                ),

                int(
                    prediction.get(
                        "days_until_service",
                        0
                    )
                    or 0
                ),

                datetime.now().isoformat(),
            ),
        )

        connection.commit()

        return cursor.lastrowid

    finally:

        connection.close()


# ============================================================
# MILESTONE 2
# GET MAINTENANCE PREDICTIONS
# ============================================================

def get_maintenance_predictions(
    asset_id=None,
    limit=100
):

    connection = get_connection()

    try:

        query = """
            SELECT *
            FROM maintenance_predictions
            WHERE 1 = 1
        """

        params = []

        if asset_id:
            query += " AND asset_id = ?"
            params.append(asset_id)

        query += """
            ORDER BY source_timestamp DESC
            LIMIT ?
        """

        params.append(int(limit))

        rows = connection.execute(
            query,
            params
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        connection.close()


# ============================================================
# MILESTONE 2
# CREATE MAINTENANCE ALERT
# ============================================================

def create_maintenance_alert(alert):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT OR IGNORE INTO maintenance_alerts (
                asset_id,
                asset_name,
                asset_type,

                building_name,
                block_name,

                source_timestamp,

                severity,

                title,
                message,

                health_score,
                health_status,

                maintenance_probability,
                maintenance_probability_percent,

                recommended_maintenance_date,
                days_until_service,

                status,

                created_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                str(alert.get("asset_id", "")),
                str(alert.get("asset_name", "")),
                str(alert.get("asset_type", "")),

                str(alert.get("building_name", "")),
                str(alert.get("block_name", "")),

                str(
                    alert.get(
                        "source_timestamp",
                        ""
                    )
                ),

                str(
                    alert.get(
                        "severity",
                        "MEDIUM"
                    )
                ),

                str(
                    alert.get(
                        "title",
                        "Maintenance Alert"
                    )
                ),

                str(
                    alert.get(
                        "message",
                        ""
                    )
                ),

                safe_float(
                    alert.get("health_score")
                ),

                str(
                    alert.get(
                        "health_status",
                        ""
                    )
                ),

                safe_float(
                    alert.get(
                        "maintenance_probability"
                    )
                ),

                safe_float(
                    alert.get(
                        "maintenance_probability_percent"
                    )
                ),

                str(
                    alert.get(
                        "recommended_maintenance_date",
                        ""
                    )
                ),

                int(
                    alert.get(
                        "days_until_service",
                        0
                    )
                    or 0
                ),

                str(
                    alert.get(
                        "status",
                        "OPEN"
                    )
                ),

                datetime.now().isoformat(),
            ),
        )

        connection.commit()

        if cursor.rowcount == 0:
            return None

        return cursor.lastrowid

    finally:

        connection.close()


# ============================================================
# MILESTONE 2
# GET MAINTENANCE ALERTS
# ============================================================

def get_maintenance_alerts(
    limit=50,
    status=None
):

    connection = get_connection()

    try:

        query = """
            SELECT *
            FROM maintenance_alerts
            WHERE 1 = 1
        """

        params = []

        if status:
            query += " AND status = ?"
            params.append(
                str(status).upper()
            )

        query += """
            ORDER BY created_at DESC
            LIMIT ?
        """

        params.append(int(limit))

        rows = connection.execute(
            query,
            params
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        connection.close()


# ============================================================
# MILESTONE 2
# UPDATE MAINTENANCE ALERT STATUS
# ============================================================

def update_maintenance_alert_status(
    alert_id,
    status
):

    allowed = {
        "OPEN",
        "INVESTIGATING",
        "RESOLVED"
    }

    status = str(status).upper()

    if status not in allowed:
        raise ValueError(
            "Invalid maintenance alert status."
        )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE maintenance_alerts
            SET status = ?
            WHERE id = ?
            """,
            (
                status,
                int(alert_id)
            ),
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:

        connection.close()


# ============================================================
# MILESTONE 2
# SAVE MAINTENANCE WORK ORDER
# ============================================================

def save_maintenance_work_order(
    work_order
):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        now = datetime.now().isoformat()

        cursor.execute(
            """
            INSERT OR IGNORE INTO maintenance_work_orders (
                asset_id,
                asset_name,
                asset_type,

                building_name,
                block_name,

                priority,

                recommended_date,

                reason,

                status,

                source_timestamp,

                created_at,
                updated_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                str(
                    work_order.get(
                        "asset_id",
                        ""
                    )
                ),

                str(
                    work_order.get(
                        "asset_name",
                        ""
                    )
                ),

                str(
                    work_order.get(
                        "asset_type",
                        ""
                    )
                ),

                str(
                    work_order.get(
                        "building_name",
                        ""
                    )
                ),

                str(
                    work_order.get(
                        "block_name",
                        ""
                    )
                ),

                str(
                    work_order.get(
                        "priority",
                        "LOW"
                    )
                ),

                str(
                    work_order.get(
                        "recommended_date",
                        ""
                    )
                ),

                str(
                    work_order.get(
                        "reason",
                        ""
                    )
                ),

                str(
                    work_order.get(
                        "status",
                        "RECOMMENDED"
                    )
                ),

                str(
                    work_order.get(
                        "source_timestamp",
                        ""
                    )
                ),

                now,
                now,
            ),
        )

        connection.commit()

        if cursor.rowcount == 0:
            return None

        return cursor.lastrowid

    finally:

        connection.close()


# ============================================================
# MILESTONE 2
# GET MAINTENANCE WORK ORDERS
# ============================================================

def get_maintenance_work_orders(
    limit=50,
    status=None
):

    connection = get_connection()

    try:

        query = """
            SELECT *
            FROM maintenance_work_orders
            WHERE 1 = 1
        """

        params = []

        if status:
            query += " AND status = ?"
            params.append(
                str(status).upper()
            )

        query += """
            ORDER BY recommended_date ASC, created_at DESC
            LIMIT ?
        """

        params.append(int(limit))

        rows = connection.execute(
            query,
            params
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        connection.close()


# ============================================================
# MILESTONE 2
# UPDATE WORK ORDER STATUS
# ============================================================

def update_maintenance_work_order_status(
    work_order_id,
    status
):

    allowed = {
        "RECOMMENDED",
        "SCHEDULED",
        "IN_PROGRESS",
        "COMPLETED",
        "CANCELLED"
    }

    status = str(status).upper()

    if status not in allowed:
        raise ValueError(
            "Invalid maintenance work-order status."
        )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE maintenance_work_orders
            SET
                status = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                status,
                datetime.now().isoformat(),
                int(work_order_id),
            ),
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:

        connection.close()


# ============================================================
# MILESTONE 2
# DATABASE COUNTS
# ============================================================

def get_maintenance_database_counts():
    """
    Useful for startup checks and Milestone 2 verification.
    """

    connection = get_connection()

    try:

        tables = [
            "assets",
            "asset_readings",
            "maintenance_predictions",
            "maintenance_alerts",
            "maintenance_work_orders",
        ]

        counts = {}

        for table in tables:

            row = connection.execute(
                f"""
                SELECT COUNT(*) AS total
                FROM {table}
                """
            ).fetchone()

            counts[table] = int(
                row["total"]
            )

        return counts

    finally:

        connection.close()