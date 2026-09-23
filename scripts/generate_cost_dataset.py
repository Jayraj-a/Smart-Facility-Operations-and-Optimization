from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# FACILITYOPS AI
# MILESTONE 4 - COST OPTIMIZATION DATASET GENERATOR
# ============================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"

OUTPUT_FILE = (
    DATA_DIR
    / "milestone4_cost_dataset.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_SEED = 42
DAYS = 30

np.random.seed(RANDOM_SEED)


BUILDINGS = [
    {
        "facility_id": "FAC-001",
        "facility_name": "Infosys Smart Campus",
        "building_id": "BLD-001",
        "building_name": "Building A",
        "base_electricity_kwh": 520,
        "base_water_liters": 145,
        "base_occupancy": 105,
        "maintenance_factor": 1.00,
    },
    {
        "facility_id": "FAC-001",
        "facility_name": "Infosys Smart Campus",
        "building_id": "BLD-002",
        "building_name": "Building B",
        "base_electricity_kwh": 470,
        "base_water_liters": 130,
        "base_occupancy": 95,
        "maintenance_factor": 0.90,
    },
    {
        "facility_id": "FAC-001",
        "facility_name": "Infosys Smart Campus",
        "building_id": "BLD-003",
        "building_name": "Building C",
        "base_electricity_kwh": 430,
        "base_water_liters": 120,
        "base_occupancy": 85,
        "maintenance_factor": 1.10,
    },
]


# ============================================================
# COST CONFIGURATION
# ============================================================

ELECTRICITY_RATE = 8.50
WATER_RATE = 0.055

BASE_MAINTENANCE_COST = 420.0
BASE_SECURITY_COST = 180.0
BASE_OPERATIONAL_COST = 260.0


# ============================================================
# HELPER FUNCTIONS
# ============================================================


def clamp(value, minimum, maximum):
    return max(
        minimum,
        min(value, maximum),
    )


def get_hour_factor(hour):
    if 0 <= hour < 6:
        return 0.45

    if 6 <= hour < 9:
        return 0.75

    if 9 <= hour < 17:
        return 1.15

    if 17 <= hour < 21:
        return 0.80

    return 0.55


def get_occupancy_factor(hour):
    if 0 <= hour < 6:
        return 0.08

    if 6 <= hour < 9:
        return 0.45

    if 9 <= hour < 17:
        return 1.00

    if 17 <= hour < 21:
        return 0.40

    return 0.12


def determine_cost_status(
    total_cost,
    expected_cost,
):
    if expected_cost <= 0:
        return "NORMAL"

    ratio = total_cost / expected_cost

    if ratio >= 1.30:
        return "CRITICAL"

    if ratio >= 1.15:
        return "HIGH"

    if ratio >= 1.05:
        return "WARNING"

    return "NORMAL"


def determine_savings_priority(
    potential_savings,
):
    if potential_savings >= 1000:
        return "CRITICAL"

    if potential_savings >= 500:
        return "HIGH"

    if potential_savings >= 200:
        return "MEDIUM"

    if potential_savings > 0:
        return "LOW"

    return "NORMAL"


# ============================================================
# GENERATE COST DATA
# ============================================================


def generate_cost_dataset():
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    records = []

    start_timestamp = (
        pd.Timestamp.now()
        .floor("h")
        - pd.Timedelta(days=DAYS)
    )

    record_number = 1

    for building in BUILDINGS:

        for hour_index in range(
            DAYS * 24
        ):
            timestamp = (
                start_timestamp
                + pd.Timedelta(
                    hours=hour_index
                )
            )

            hour = timestamp.hour

            hour_factor = get_hour_factor(
                hour
            )

            occupancy_factor = (
                get_occupancy_factor(hour)
            )

            # --------------------------------------------
            # OCCUPANCY
            # --------------------------------------------

            occupancy_noise = np.random.normal(
                1.0,
                0.10,
            )

            occupancy = int(
                building[
                    "base_occupancy"
                ]
                * occupancy_factor
                * occupancy_noise
            )

            occupancy = max(
                occupancy,
                0,
            )

            # --------------------------------------------
            # ELECTRICITY
            # --------------------------------------------

            electricity_noise = (
                np.random.normal(
                    1.0,
                    0.07,
                )
            )

            electricity_kwh = (
                building[
                    "base_electricity_kwh"
                ]
                * hour_factor
                * electricity_noise
            )

            electricity_kwh = max(
                electricity_kwh,
                50,
            )

            # --------------------------------------------
            # HVAC
            # --------------------------------------------

            hvac_ratio = (
                np.random.uniform(
                    0.40,
                    0.52,
                )
            )

            hvac_kwh = (
                electricity_kwh
                * hvac_ratio
            )

            # --------------------------------------------
            # LIGHTING
            # --------------------------------------------

            lighting_ratio = (
                np.random.uniform(
                    0.13,
                    0.20,
                )
            )

            lighting_kwh = (
                electricity_kwh
                * lighting_ratio
            )

            # --------------------------------------------
            # WATER
            # --------------------------------------------

            water_noise = np.random.normal(
                1.0,
                0.08,
            )

            water_liters = (
                building[
                    "base_water_liters"
                ]
                * (
                    0.45
                    + occupancy_factor
                )
                * water_noise
            )

            water_liters = max(
                water_liters,
                20,
            )

            # --------------------------------------------
            # RANDOM COST INEFFICIENCY EVENT
            # --------------------------------------------

            inefficiency_event = (
                np.random.random()
                < 0.045
            )

            inefficiency_type = "NONE"

            if inefficiency_event:

                event_type = np.random.choice(
                    [
                        "HIGH_HVAC_USAGE",
                        "EXCESS_LIGHTING",
                        "HIGH_WATER_USAGE",
                        "LOW_OCCUPANCY_HIGH_ENERGY",
                        "MAINTENANCE_RISK",
                    ]
                )

                inefficiency_type = event_type

                if (
                    event_type
                    == "HIGH_HVAC_USAGE"
                ):
                    extra = (
                        electricity_kwh
                        * np.random.uniform(
                            0.18,
                            0.35,
                        )
                    )

                    electricity_kwh += extra
                    hvac_kwh += extra

                elif (
                    event_type
                    == "EXCESS_LIGHTING"
                ):
                    extra = (
                        electricity_kwh
                        * np.random.uniform(
                            0.10,
                            0.20,
                        )
                    )

                    electricity_kwh += extra
                    lighting_kwh += extra

                elif (
                    event_type
                    == "HIGH_WATER_USAGE"
                ):
                    water_liters *= (
                        np.random.uniform(
                            1.5,
                            2.2,
                        )
                    )

                elif (
                    event_type
                    == "LOW_OCCUPANCY_HIGH_ENERGY"
                ):
                    occupancy = int(
                        occupancy
                        * 0.35
                    )

                    electricity_kwh *= (
                        np.random.uniform(
                            1.15,
                            1.30,
                        )
                    )

                elif (
                    event_type
                    == "MAINTENANCE_RISK"
                ):
                    electricity_kwh *= (
                        np.random.uniform(
                            1.08,
                            1.18,
                        )
                    )

            # --------------------------------------------
            # ENERGY COST
            # --------------------------------------------

            electricity_cost = (
                electricity_kwh
                * ELECTRICITY_RATE
            )

            hvac_cost = (
                hvac_kwh
                * ELECTRICITY_RATE
            )

            lighting_cost = (
                lighting_kwh
                * ELECTRICITY_RATE
            )

            # --------------------------------------------
            # WATER COST
            # --------------------------------------------

            water_cost = (
                water_liters
                * WATER_RATE
            )

            # --------------------------------------------
            # MAINTENANCE COST
            # --------------------------------------------

            maintenance_cost = (
                BASE_MAINTENANCE_COST
                * building[
                    "maintenance_factor"
                ]
                * np.random.uniform(
                    0.80,
                    1.20,
                )
            )

            if (
                inefficiency_type
                == "MAINTENANCE_RISK"
            ):
                maintenance_cost *= (
                    np.random.uniform(
                        1.4,
                        1.8,
                    )
                )

            # --------------------------------------------
            # SECURITY COST
            # --------------------------------------------

            security_cost = (
                BASE_SECURITY_COST
                * np.random.uniform(
                    0.90,
                    1.10,
                )
            )

            # --------------------------------------------
            # OPERATIONAL COST
            # --------------------------------------------

            operational_cost = (
                BASE_OPERATIONAL_COST
                * np.random.uniform(
                    0.85,
                    1.15,
                )
            )

            # --------------------------------------------
            # TOTAL COST
            # --------------------------------------------

            total_cost = (
                electricity_cost
                + water_cost
                + maintenance_cost
                + security_cost
                + operational_cost
            )

            # --------------------------------------------
            # EXPECTED COST
            # --------------------------------------------

            expected_electricity = (
                building[
                    "base_electricity_kwh"
                ]
                * hour_factor
            )

            expected_electricity_cost = (
                expected_electricity
                * ELECTRICITY_RATE
            )

            expected_water = (
                building[
                    "base_water_liters"
                ]
                * (
                    0.45
                    + occupancy_factor
                )
            )

            expected_water_cost = (
                expected_water
                * WATER_RATE
            )

            expected_maintenance = (
                BASE_MAINTENANCE_COST
                * building[
                    "maintenance_factor"
                ]
            )

            expected_cost = (
                expected_electricity_cost
                + expected_water_cost
                + expected_maintenance
                + BASE_SECURITY_COST
                + BASE_OPERATIONAL_COST
            )

            # --------------------------------------------
            # COST VARIANCE
            # --------------------------------------------

            cost_variance = (
                total_cost
                - expected_cost
            )

            if expected_cost > 0:
                cost_variance_percent = (
                    cost_variance
                    / expected_cost
                    * 100
                )
            else:
                cost_variance_percent = 0.0

            # --------------------------------------------
            # POTENTIAL SAVINGS
            # --------------------------------------------

            potential_savings = max(
                cost_variance,
                0,
            )

            if (
                inefficiency_type
                == "LOW_OCCUPANCY_HIGH_ENERGY"
            ):
                potential_savings += (
                    electricity_cost
                    * 0.12
                )

            elif (
                inefficiency_type
                == "HIGH_HVAC_USAGE"
            ):
                potential_savings += (
                    hvac_cost
                    * 0.10
                )

            elif (
                inefficiency_type
                == "EXCESS_LIGHTING"
            ):
                potential_savings += (
                    lighting_cost
                    * 0.15
                )

            elif (
                inefficiency_type
                == "HIGH_WATER_USAGE"
            ):
                potential_savings += (
                    water_cost
                    * 0.20
                )

            # --------------------------------------------
            # COST STATUS
            # --------------------------------------------

            cost_status = (
                determine_cost_status(
                    total_cost,
                    expected_cost,
                )
            )

            savings_priority = (
                determine_savings_priority(
                    potential_savings
                )
            )

            # --------------------------------------------
            # OCCUPANCY EFFICIENCY
            # --------------------------------------------

            if occupancy > 0:
                cost_per_occupant = (
                    total_cost
                    / occupancy
                )
            else:
                cost_per_occupant = (
                    total_cost
                )

            # --------------------------------------------
            # RECORD
            # --------------------------------------------

            record = {
                "cost_record_id":
                    f"COST-{record_number:06d}",

                "facility_id":
                    building[
                        "facility_id"
                    ],

                "facility_name":
                    building[
                        "facility_name"
                    ],

                "building_id":
                    building[
                        "building_id"
                    ],

                "building_name":
                    building[
                        "building_name"
                    ],

                "timestamp":
                    timestamp,

                "occupancy":
                    occupancy,

                "electricity_kwh":
                    round(
                        electricity_kwh,
                        2,
                    ),

                "hvac_kwh":
                    round(
                        hvac_kwh,
                        2,
                    ),

                "lighting_kwh":
                    round(
                        lighting_kwh,
                        2,
                    ),

                "water_liters":
                    round(
                        water_liters,
                        2,
                    ),

                "electricity_cost":
                    round(
                        electricity_cost,
                        2,
                    ),

                "water_cost":
                    round(
                        water_cost,
                        2,
                    ),

                "maintenance_cost":
                    round(
                        maintenance_cost,
                        2,
                    ),

                "security_cost":
                    round(
                        security_cost,
                        2,
                    ),

                "operational_cost":
                    round(
                        operational_cost,
                        2,
                    ),

                "total_cost":
                    round(
                        total_cost,
                        2,
                    ),

                "expected_cost":
                    round(
                        expected_cost,
                        2,
                    ),

                "cost_variance":
                    round(
                        cost_variance,
                        2,
                    ),

                "cost_variance_percent":
                    round(
                        cost_variance_percent,
                        2,
                    ),

                "potential_savings":
                    round(
                        potential_savings,
                        2,
                    ),

                "cost_per_occupant":
                    round(
                        cost_per_occupant,
                        2,
                    ),

                "inefficiency_type":
                    inefficiency_type,

                "cost_status":
                    cost_status,

                "savings_priority":
                    savings_priority,

                "is_cost_inefficiency":
                    int(
                        inefficiency_event
                    ),
            }

            records.append(record)

            record_number += 1

    dataframe = pd.DataFrame(
        records
    )

    dataframe.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    return dataframe


# ============================================================
# COMMAND-LINE TEST
# ============================================================


def main():
    print()
    print("=" * 65)
    print("FACILITYOPS AI - MILESTONE 4")
    print("COST OPTIMIZATION DATASET GENERATOR")
    print("=" * 65)

    dataframe = (
        generate_cost_dataset()
    )

    print()
    print(
        "Dataset created successfully."
    )

    print(
        "Output:",
        OUTPUT_FILE,
    )

    print()
    print(
        "Rows:",
        len(dataframe),
    )

    print(
        "Columns:",
        len(dataframe.columns),
    )

    print(
        "Buildings:",
        dataframe[
            "building_id"
        ].nunique(),
    )

    print()
    print("Cost Status")
    print("-" * 65)

    print(
        dataframe[
            "cost_status"
        ].value_counts()
    )

    print()
    print("Savings Priority")
    print("-" * 65)

    print(
        dataframe[
            "savings_priority"
        ].value_counts()
    )

    print()
    print("Inefficiency Types")
    print("-" * 65)

    print(
        dataframe[
            "inefficiency_type"
        ].value_counts()
    )

    print()
    print("Cost Summary")
    print("-" * 65)

    print(
        "Total Cost:",
        round(
            dataframe[
                "total_cost"
            ].sum(),
            2,
        ),
    )

    print(
        "Potential Savings:",
        round(
            dataframe[
                "potential_savings"
            ].sum(),
            2,
        ),
    )

    print(
        "Cost Inefficiency Events:",
        int(
            dataframe[
                "is_cost_inefficiency"
            ].sum()
        ),
    )

    print()
    print("=" * 65)
    print(
        "Milestone 4 cost dataset "
        "generated successfully."
    )
    print("=" * 65)


if __name__ == "__main__":
    main()