from pathlib import Path
from datetime import datetime, timedelta
import random

import numpy as np
import pandas as pd


# ============================================================
# FACILITYOPS AI
# MILESTONE 3 - OCCUPANCY & SECURITY INTELLIGENCE
# Simulated dataset generator
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

OCCUPANCY_FILE = DATA_DIR / "milestone3_occupancy_dataset.csv"
SECURITY_FILE = DATA_DIR / "milestone3_security_dataset.csv"

random.seed(42)
np.random.seed(42)


# ============================================================
# FACILITY CONFIGURATION
# ============================================================

FACILITY_ID = "F001"
FACILITY_NAME = "Smart Campus"

SPACES = [
    {
        "building_id": "B001",
        "building_name": "Building A",
        "block_id": "BLK-A1",
        "block_name": "Block A1",
        "space_id": "SP-001",
        "space_name": "Open Workspace A1",
        "space_type": "Workspace",
        "capacity": 120,
    },
    {
        "building_id": "B001",
        "building_name": "Building A",
        "block_id": "BLK-A1",
        "block_name": "Block A1",
        "space_id": "SP-002",
        "space_name": "Conference Room A",
        "space_type": "Meeting Room",
        "capacity": 30,
    },
    {
        "building_id": "B001",
        "building_name": "Building A",
        "block_id": "BLK-A2",
        "block_name": "Block A2",
        "space_id": "SP-003",
        "space_name": "Training Hall A",
        "space_type": "Training Room",
        "capacity": 80,
    },
    {
        "building_id": "B002",
        "building_name": "Building B",
        "block_id": "BLK-B1",
        "block_name": "Block B1",
        "space_id": "SP-004",
        "space_name": "Open Workspace B1",
        "space_type": "Workspace",
        "capacity": 150,
    },
    {
        "building_id": "B002",
        "building_name": "Building B",
        "block_id": "BLK-B1",
        "block_name": "Block B1",
        "space_id": "SP-005",
        "space_name": "Meeting Room B",
        "space_type": "Meeting Room",
        "capacity": 25,
    },
    {
        "building_id": "B002",
        "building_name": "Building B",
        "block_id": "BLK-B2",
        "block_name": "Block B2",
        "space_id": "SP-006",
        "space_name": "Cafeteria B",
        "space_type": "Cafeteria",
        "capacity": 180,
    },
    {
        "building_id": "B003",
        "building_name": "Building C",
        "block_id": "BLK-C1",
        "block_name": "Block C1",
        "space_id": "SP-007",
        "space_name": "Open Workspace C1",
        "space_type": "Workspace",
        "capacity": 100,
    },
    {
        "building_id": "B003",
        "building_name": "Building C",
        "block_id": "BLK-C1",
        "block_name": "Block C1",
        "space_id": "SP-008",
        "space_name": "Server Operations Room",
        "space_type": "Restricted Area",
        "capacity": 20,
    },
]


ACCESS_POINTS = [
    {
        "access_point_id": "AP-001",
        "access_point_name": "Building A Main Entrance",
        "building_id": "B001",
        "building_name": "Building A",
        "block_id": "BLK-A1",
        "block_name": "Block A1",
        "zone_type": "Entrance",
    },
    {
        "access_point_id": "AP-002",
        "access_point_name": "Building A Side Entrance",
        "building_id": "B001",
        "building_name": "Building A",
        "block_id": "BLK-A2",
        "block_name": "Block A2",
        "zone_type": "Entrance",
    },
    {
        "access_point_id": "AP-003",
        "access_point_name": "Building B Main Entrance",
        "building_id": "B002",
        "building_name": "Building B",
        "block_id": "BLK-B1",
        "block_name": "Block B1",
        "zone_type": "Entrance",
    },
    {
        "access_point_id": "AP-004",
        "access_point_name": "Building B Service Door",
        "building_id": "B002",
        "building_name": "Building B",
        "block_id": "BLK-B2",
        "block_name": "Block B2",
        "zone_type": "Service Area",
    },
    {
        "access_point_id": "AP-005",
        "access_point_name": "Building C Main Entrance",
        "building_id": "B003",
        "building_name": "Building C",
        "block_id": "BLK-C1",
        "block_name": "Block C1",
        "zone_type": "Entrance",
    },
    {
        "access_point_id": "AP-006",
        "access_point_name": "Server Room Access",
        "building_id": "B003",
        "building_name": "Building C",
        "block_id": "BLK-C1",
        "block_name": "Block C1",
        "zone_type": "Restricted Area",
    },
]


# ============================================================
# OCCUPANCY DATASET
# ============================================================

def occupancy_ratio_for_hour(hour, space_type):
    """
    Return a realistic base occupancy ratio based on hour and space type.
    """

    if space_type == "Workspace":
        if 9 <= hour <= 11:
            return random.uniform(0.65, 0.90)
        if 12 <= hour <= 13:
            return random.uniform(0.35, 0.60)
        if 14 <= hour <= 17:
            return random.uniform(0.60, 0.88)
        if 18 <= hour <= 20:
            return random.uniform(0.15, 0.40)
        return random.uniform(0.01, 0.10)

    if space_type == "Meeting Room":
        if 9 <= hour <= 17:
            return random.uniform(0.20, 0.85)
        return random.uniform(0.00, 0.10)

    if space_type == "Training Room":
        if 9 <= hour <= 16:
            return random.uniform(0.20, 0.80)
        return random.uniform(0.00, 0.08)

    if space_type == "Cafeteria":
        if 8 <= hour <= 9:
            return random.uniform(0.25, 0.50)
        if 12 <= hour <= 14:
            return random.uniform(0.70, 0.95)
        if 16 <= hour <= 17:
            return random.uniform(0.25, 0.50)
        return random.uniform(0.02, 0.15)

    if space_type == "Restricted Area":
        return random.uniform(0.05, 0.35)

    return random.uniform(0.05, 0.50)


def classify_utilization(utilization_percent):
    if utilization_percent >= 100:
        return "OVERCROWDED"

    if utilization_percent >= 75:
        return "HIGH"

    if utilization_percent >= 40:
        return "OPTIMAL"

    if utilization_percent >= 15:
        return "LOW"

    return "UNDERUSED"


def generate_occupancy_dataset():
    records = []

    # 30 days of hourly data
    start_time = datetime(2026, 1, 1, 0, 0, 0)

    for day in range(30):
        for hour in range(24):

            timestamp = start_time + timedelta(days=day, hours=hour)

            for space in SPACES:

                ratio = occupancy_ratio_for_hour(
                    hour,
                    space["space_type"],
                )

                occupancy_count = int(
                    round(space["capacity"] * ratio)
                )

                # Simulate occasional overcrowding
                overcrowding_event = random.random() < 0.015

                if overcrowding_event:
                    occupancy_count = int(
                        space["capacity"]
                        * random.uniform(1.02, 1.20)
                    )

                occupancy_count = max(0, occupancy_count)

                utilization_percent = (
                    occupancy_count
                    / space["capacity"]
                    * 100
                )

                utilization_status = classify_utilization(
                    utilization_percent
                )

                overcrowded = int(
                    occupancy_count > space["capacity"]
                )

                available_capacity = max(
                    0,
                    space["capacity"] - occupancy_count
                )

                records.append(
                    {
                        "facility_id": FACILITY_ID,
                        "facility_name": FACILITY_NAME,
                        "building_id": space["building_id"],
                        "building_name": space["building_name"],
                        "block_id": space["block_id"],
                        "block_name": space["block_name"],
                        "space_id": space["space_id"],
                        "space_name": space["space_name"],
                        "space_type": space["space_type"],
                        "timestamp": timestamp.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "capacity": space["capacity"],
                        "occupancy_count": occupancy_count,
                        "available_capacity": available_capacity,
                        "utilization_percent": round(
                            utilization_percent,
                            2,
                        ),
                        "utilization_status": utilization_status,
                        "overcrowded": overcrowded,
                    }
                )

    dataframe = pd.DataFrame(records)

    return dataframe


# ============================================================
# SECURITY DATASET
# ============================================================

def choose_user_type():
    return random.choices(
        ["EMPLOYEE", "VISITOR", "CONTRACTOR"],
        weights=[75, 15, 10],
        k=1,
    )[0]


def create_identity(user_type):
    if user_type == "EMPLOYEE":
        number = random.randint(1, 500)
        return f"EMP-{number:04d}", f"Employee {number}"

    if user_type == "VISITOR":
        number = random.randint(1, 300)
        return f"VIS-{number:04d}", f"Visitor {number}"

    number = random.randint(1, 150)
    return f"CON-{number:04d}", f"Contractor {number}"


def determine_security_severity(
    access_status,
    unauthorized_attempt,
    after_hours,
    forced_entry,
    tailgating_detected,
):
    if forced_entry:
        return "CRITICAL"

    if unauthorized_attempt and after_hours:
        return "CRITICAL"

    if unauthorized_attempt:
        return "HIGH"

    if tailgating_detected:
        return "HIGH"

    if access_status == "DENIED":
        return "MEDIUM"

    if after_hours:
        return "LOW"

    return "NORMAL"


def generate_security_dataset():
    records = []

    start_time = datetime(2026, 1, 1, 0, 0, 0)

    event_counter = 1

    # Generate roughly 150 access/security events per day
    for day in range(30):

        current_date = start_time + timedelta(days=day)

        daily_events = random.randint(130, 170)

        for _ in range(daily_events):

            access_point = random.choice(ACCESS_POINTS)

            # Most access happens during working hours
            if random.random() < 0.82:
                hour = random.randint(7, 20)
            else:
                hour = random.choice(
                    list(range(0, 7))
                    + list(range(21, 24))
                )

            minute = random.randint(0, 59)
            second = random.randint(0, 59)

            timestamp = current_date.replace(
                hour=hour,
                minute=minute,
                second=second,
            )

            user_type = choose_user_type()

            user_id, user_name = create_identity(
                user_type
            )

            after_hours = int(
                hour < 7 or hour > 20
            )

            restricted_area = (
                access_point["zone_type"]
                == "Restricted Area"
            )

            unauthorized_probability = 0.018

            if user_type == "VISITOR":
                unauthorized_probability += 0.020

            if restricted_area:
                unauthorized_probability += 0.035

            if after_hours:
                unauthorized_probability += 0.025

            unauthorized_attempt = int(
                random.random()
                < unauthorized_probability
            )

            forced_entry = int(
                random.random() < 0.003
            )

            tailgating_detected = int(
                random.random() < 0.007
            )

            if forced_entry:
                access_status = "DENIED"

            elif unauthorized_attempt:
                access_status = "DENIED"

            else:
                access_status = random.choices(
                    ["GRANTED", "DENIED"],
                    weights=[97, 3],
                    k=1,
                )[0]

            # Simulated CCTV event linked to access activity
            cctv_event = "NORMAL"

            if forced_entry:
                cctv_event = "FORCED_ENTRY"

            elif tailgating_detected:
                cctv_event = "TAILGATING"

            elif unauthorized_attempt:
                cctv_event = "SUSPICIOUS_ACCESS"

            elif after_hours and random.random() < 0.15:
                cctv_event = "AFTER_HOURS_MOVEMENT"

            severity = determine_security_severity(
                access_status,
                unauthorized_attempt,
                after_hours,
                forced_entry,
                tailgating_detected,
            )

            security_alert = int(
                severity
                in {"MEDIUM", "HIGH", "CRITICAL"}
            )

            event_type = (
                "ACCESS_DENIED"
                if access_status == "DENIED"
                else "ACCESS_GRANTED"
            )

            if forced_entry:
                event_type = "FORCED_ENTRY"

            elif tailgating_detected:
                event_type = "TAILGATING"

            elif unauthorized_attempt:
                event_type = "UNAUTHORIZED_ACCESS"

            records.append(
                {
                    "event_id": f"SEC-{event_counter:06d}",
                    "facility_id": FACILITY_ID,
                    "facility_name": FACILITY_NAME,
                    "building_id": access_point[
                        "building_id"
                    ],
                    "building_name": access_point[
                        "building_name"
                    ],
                    "block_id": access_point[
                        "block_id"
                    ],
                    "block_name": access_point[
                        "block_name"
                    ],
                    "access_point_id": access_point[
                        "access_point_id"
                    ],
                    "access_point_name": access_point[
                        "access_point_name"
                    ],
                    "zone_type": access_point[
                        "zone_type"
                    ],
                    "timestamp": timestamp.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "user_id": user_id,
                    "user_name": user_name,
                    "user_type": user_type,
                    "event_type": event_type,
                    "access_status": access_status,
                    "after_hours": after_hours,
                    "unauthorized_attempt": unauthorized_attempt,
                    "forced_entry": forced_entry,
                    "tailgating_detected": tailgating_detected,
                    "cctv_event": cctv_event,
                    "severity": severity,
                    "security_alert": security_alert,
                }
            )

            event_counter += 1

    dataframe = pd.DataFrame(records)

    dataframe["timestamp"] = pd.to_datetime(
        dataframe["timestamp"]
    )

    dataframe = dataframe.sort_values(
        "timestamp"
    ).reset_index(drop=True)

    dataframe["timestamp"] = dataframe[
        "timestamp"
    ].dt.strftime("%Y-%m-%d %H:%M:%S")

    return dataframe


# ============================================================
# DATASET SUMMARY
# ============================================================

def print_occupancy_summary(dataframe):
    print()
    print("=" * 60)
    print("OCCUPANCY DATASET")
    print("=" * 60)

    print(f"Rows: {len(dataframe)}")
    print(f"Columns: {len(dataframe.columns)}")
    print(
        f"Spaces monitored: "
        f"{dataframe['space_id'].nunique()}"
    )

    print()
    print("Utilization Status Distribution:")
    print(
        dataframe[
            "utilization_status"
        ].value_counts()
    )

    print()
    print(
        "Overcrowding Events:",
        int(dataframe["overcrowded"].sum()),
    )


def print_security_summary(dataframe):
    print()
    print("=" * 60)
    print("SECURITY DATASET")
    print("=" * 60)

    print(f"Rows: {len(dataframe)}")
    print(f"Columns: {len(dataframe.columns)}")
    print(
        f"Access Points: "
        f"{dataframe['access_point_id'].nunique()}"
    )

    print()
    print("Access Status Distribution:")
    print(
        dataframe[
            "access_status"
        ].value_counts()
    )

    print()
    print("Security Severity Distribution:")
    print(
        dataframe[
            "severity"
        ].value_counts()
    )

    print()
    print(
        "Unauthorized Access Attempts:",
        int(
            dataframe[
                "unauthorized_attempt"
            ].sum()
        ),
    )

    print(
        "Security Alerts:",
        int(
            dataframe[
                "security_alert"
            ].sum()
        ),
    )


# ============================================================
# MAIN
# ============================================================

def main():
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    occupancy_dataframe = (
        generate_occupancy_dataset()
    )

    security_dataframe = (
        generate_security_dataset()
    )

    occupancy_dataframe.to_csv(
        OCCUPANCY_FILE,
        index=False,
    )

    security_dataframe.to_csv(
        SECURITY_FILE,
        index=False,
    )

    print()
    print("=" * 60)
    print("FACILITYOPS AI - MILESTONE 3")
    print("OCCUPANCY & SECURITY INTELLIGENCE")
    print("=" * 60)

    print()
    print(
        "Simulated Milestone 3 datasets "
        "generated successfully."
    )

    print_occupancy_summary(
        occupancy_dataframe
    )

    print_security_summary(
        security_dataframe
    )

    print()
    print("=" * 60)
    print("FILES CREATED")
    print("=" * 60)

    print()
    print("Occupancy Dataset:")
    print(OCCUPANCY_FILE)

    print()
    print("Security Dataset:")
    print(SECURITY_FILE)

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()