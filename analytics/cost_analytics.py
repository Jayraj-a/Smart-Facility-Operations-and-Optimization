from pathlib import Path

import pandas as pd


# ============================================================
# FACILITYOPS AI
# MILESTONE 4 - COST ANALYTICS
# ============================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "milestone4_cost_dataset.csv"
)


# ============================================================
# LOAD COST DATA
# ============================================================


def load_cost_data():
    """
    Load the Milestone 4 cost dataset.
    """

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Cost dataset not found: {DATA_FILE}"
        )

    dataframe = pd.read_csv(
        DATA_FILE
    )

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
# FILTER COST DATA
# ============================================================


def filter_cost_data(
    dataframe,
    building_id=None,
    start_date=None,
    end_date=None,
):
    """
    Filter cost records by building and date range.
    """

    filtered = dataframe.copy()

    if building_id:
        filtered = filtered[
            filtered["building_id"]
            == building_id
        ]

    if start_date:
        start_date = pd.to_datetime(
            start_date
        )

        filtered = filtered[
            filtered["timestamp"]
            >= start_date
        ]

    if end_date:
        end_date = pd.to_datetime(
            end_date
        )

        filtered = filtered[
            filtered["timestamp"]
            <= end_date
        ]

    return filtered.reset_index(
        drop=True
    )


# ============================================================
# COST SUMMARY
# ============================================================


def calculate_cost_summary(
    dataframe,
):
    """
    Calculate the overall facility cost summary.
    """

    if dataframe.empty:
        return {
            "total_records": 0,
            "total_cost": 0.0,
            "expected_cost": 0.0,
            "cost_variance": 0.0,
            "potential_savings": 0.0,
            "electricity_cost": 0.0,
            "water_cost": 0.0,
            "maintenance_cost": 0.0,
            "security_cost": 0.0,
            "operational_cost": 0.0,
            "average_hourly_cost": 0.0,
            "average_cost_per_occupant": 0.0,
            "inefficiency_events": 0,
        }

    total_cost = float(
        dataframe[
            "total_cost"
        ].sum()
    )

    expected_cost = float(
        dataframe[
            "expected_cost"
        ].sum()
    )

    total_variance = (
        total_cost
        - expected_cost
    )

    return {
        "total_records":
            int(len(dataframe)),

        "buildings":
            int(
                dataframe[
                    "building_id"
                ].nunique()
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
                total_variance,
                2,
            ),

        "cost_variance_percent":
            round(
                (
                    total_variance
                    / expected_cost
                    * 100
                )
                if expected_cost > 0
                else 0.0,
                2,
            ),

        "potential_savings":
            round(
                float(
                    dataframe[
                        "potential_savings"
                    ].sum()
                ),
                2,
            ),

        "electricity_cost":
            round(
                float(
                    dataframe[
                        "electricity_cost"
                    ].sum()
                ),
                2,
            ),

        "water_cost":
            round(
                float(
                    dataframe[
                        "water_cost"
                    ].sum()
                ),
                2,
            ),

        "maintenance_cost":
            round(
                float(
                    dataframe[
                        "maintenance_cost"
                    ].sum()
                ),
                2,
            ),

        "security_cost":
            round(
                float(
                    dataframe[
                        "security_cost"
                    ].sum()
                ),
                2,
            ),

        "operational_cost":
            round(
                float(
                    dataframe[
                        "operational_cost"
                    ].sum()
                ),
                2,
            ),

        "average_hourly_cost":
            round(
                float(
                    dataframe[
                        "total_cost"
                    ].mean()
                ),
                2,
            ),

        "average_cost_per_occupant":
            round(
                float(
                    dataframe[
                        "cost_per_occupant"
                    ].mean()
                ),
                2,
            ),

        "inefficiency_events":
            int(
                dataframe[
                    "is_cost_inefficiency"
                ].sum()
            ),
    }


# ============================================================
# COST BREAKDOWN
# ============================================================


def get_cost_breakdown(
    dataframe,
):
    """
    Return the total cost for each cost category.
    """

    categories = {
        "Electricity":
            "electricity_cost",

        "Water":
            "water_cost",

        "Maintenance":
            "maintenance_cost",

        "Security":
            "security_cost",

        "Operations":
            "operational_cost",
    }

    total_cost = float(
        dataframe[
            "total_cost"
        ].sum()
    )

    result = []

    for category, column in (
        categories.items()
    ):
        value = float(
            dataframe[column].sum()
        )

        percentage = (
            value
            / total_cost
            * 100
            if total_cost > 0
            else 0.0
        )

        result.append(
            {
                "category":
                    category,

                "cost":
                    round(
                        value,
                        2,
                    ),

                "percentage":
                    round(
                        percentage,
                        2,
                    ),
            }
        )

    return result


# ============================================================
# BUILDING COST COMPARISON
# ============================================================


def get_building_cost_comparison(
    dataframe,
):
    """
    Compare cost performance across buildings.
    """

    if dataframe.empty:
        return []

    grouped = (
        dataframe
        .groupby(
            [
                "building_id",
                "building_name",
            ],
            as_index=False,
        )
        .agg(
            total_cost=(
                "total_cost",
                "sum",
            ),
            expected_cost=(
                "expected_cost",
                "sum",
            ),
            potential_savings=(
                "potential_savings",
                "sum",
            ),
            electricity_cost=(
                "electricity_cost",
                "sum",
            ),
            maintenance_cost=(
                "maintenance_cost",
                "sum",
            ),
            occupancy=(
                "occupancy",
                "sum",
            ),
            inefficiency_events=(
                "is_cost_inefficiency",
                "sum",
            ),
        )
    )

    records = []

    for _, row in grouped.iterrows():

        total_cost = float(
            row["total_cost"]
        )

        expected_cost = float(
            row["expected_cost"]
        )

        variance = (
            total_cost
            - expected_cost
        )

        variance_percent = (
            variance
            / expected_cost
            * 100
            if expected_cost > 0
            else 0.0
        )

        records.append(
            {
                "building_id":
                    row[
                        "building_id"
                    ],

                "building_name":
                    row[
                        "building_name"
                    ],

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
                        variance,
                        2,
                    ),

                "cost_variance_percent":
                    round(
                        variance_percent,
                        2,
                    ),

                "potential_savings":
                    round(
                        float(
                            row[
                                "potential_savings"
                            ]
                        ),
                        2,
                    ),

                "electricity_cost":
                    round(
                        float(
                            row[
                                "electricity_cost"
                            ]
                        ),
                        2,
                    ),

                "maintenance_cost":
                    round(
                        float(
                            row[
                                "maintenance_cost"
                            ]
                        ),
                        2,
                    ),

                "inefficiency_events":
                    int(
                        row[
                            "inefficiency_events"
                        ]
                    ),
            }
        )

    return sorted(
        records,
        key=lambda item:
            item[
                "potential_savings"
            ],
        reverse=True,
    )


# ============================================================
# DAILY COST TREND
# ============================================================


def get_daily_cost_trend(
    dataframe,
):
    """
    Calculate daily actual and expected costs.
    """

    if dataframe.empty:
        return []

    working = dataframe.copy()

    working["date"] = (
        working[
            "timestamp"
        ]
        .dt.date
    )

    grouped = (
        working
        .groupby(
            "date",
            as_index=False,
        )
        .agg(
            total_cost=(
                "total_cost",
                "sum",
            ),
            expected_cost=(
                "expected_cost",
                "sum",
            ),
            potential_savings=(
                "potential_savings",
                "sum",
            ),
        )
    )

    records = []

    for _, row in grouped.iterrows():

        total_cost = float(
            row["total_cost"]
        )

        expected_cost = float(
            row["expected_cost"]
        )

        records.append(
            {
                "date":
                    str(
                        row["date"]
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
                        total_cost
                        - expected_cost,
                        2,
                    ),

                "potential_savings":
                    round(
                        float(
                            row[
                                "potential_savings"
                            ]
                        ),
                        2,
                    ),
            }
        )

    return records


# ============================================================
# HOURLY COST PATTERN
# ============================================================


def get_hourly_cost_pattern(
    dataframe,
):
    """
    Calculate average cost for each hour of the day.
    """

    if dataframe.empty:
        return []

    working = dataframe.copy()

    working["hour"] = (
        working[
            "timestamp"
        ].dt.hour
    )

    grouped = (
        working
        .groupby(
            "hour",
            as_index=False,
        )
        .agg(
            average_cost=(
                "total_cost",
                "mean",
            ),
            average_expected_cost=(
                "expected_cost",
                "mean",
            ),
            average_electricity_cost=(
                "electricity_cost",
                "mean",
            ),
            average_occupancy=(
                "occupancy",
                "mean",
            ),
        )
    )

    records = []

    for _, row in grouped.iterrows():

        records.append(
            {
                "hour":
                    int(
                        row["hour"]
                    ),

                "average_cost":
                    round(
                        float(
                            row[
                                "average_cost"
                            ]
                        ),
                        2,
                    ),

                "average_expected_cost":
                    round(
                        float(
                            row[
                                "average_expected_cost"
                            ]
                        ),
                        2,
                    ),

                "average_electricity_cost":
                    round(
                        float(
                            row[
                                "average_electricity_cost"
                            ]
                        ),
                        2,
                    ),

                "average_occupancy":
                    round(
                        float(
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
# COST INEFFICIENCIES
# ============================================================


def get_cost_inefficiencies(
    dataframe,
    limit=50,
):
    """
    Return the highest-cost inefficiency events.
    """

    if dataframe.empty:
        return []

    filtered = dataframe[
        dataframe[
            "is_cost_inefficiency"
        ] == 1
    ].copy()

    filtered = filtered.sort_values(
        [
            "potential_savings",
            "cost_variance",
        ],
        ascending=False,
    )

    if limit:
        filtered = filtered.head(
            limit
        )

    records = []

    for _, row in filtered.iterrows():

        records.append(
            {
                "cost_record_id":
                    row[
                        "cost_record_id"
                    ],

                "building_id":
                    row[
                        "building_id"
                    ],

                "building_name":
                    row[
                        "building_name"
                    ],

                "timestamp":
                    row[
                        "timestamp"
                    ].isoformat(),

                "inefficiency_type":
                    row[
                        "inefficiency_type"
                    ],

                "total_cost":
                    round(
                        float(
                            row[
                                "total_cost"
                            ]
                        ),
                        2,
                    ),

                "expected_cost":
                    round(
                        float(
                            row[
                                "expected_cost"
                            ]
                        ),
                        2,
                    ),

                "cost_variance":
                    round(
                        float(
                            row[
                                "cost_variance"
                            ]
                        ),
                        2,
                    ),

                "potential_savings":
                    round(
                        float(
                            row[
                                "potential_savings"
                            ]
                        ),
                        2,
                    ),

                "cost_status":
                    row[
                        "cost_status"
                    ],

                "savings_priority":
                    row[
                        "savings_priority"
                    ],
            }
        )

    return records


# ============================================================
# SAVINGS OPPORTUNITIES
# ============================================================


def get_savings_opportunities(
    dataframe,
):
    """
    Group potential savings by inefficiency type.
    """

    if dataframe.empty:
        return []

    filtered = dataframe[
        dataframe[
            "inefficiency_type"
        ] != "NONE"
    ].copy()

    if filtered.empty:
        return []

    grouped = (
        filtered
        .groupby(
            "inefficiency_type",
            as_index=False,
        )
        .agg(
            event_count=(
                "cost_record_id",
                "count",
            ),
            total_potential_savings=(
                "potential_savings",
                "sum",
            ),
            average_potential_savings=(
                "potential_savings",
                "mean",
            ),
            total_cost=(
                "total_cost",
                "sum",
            ),
        )
    )

    grouped = grouped.sort_values(
        "total_potential_savings",
        ascending=False,
    )

    records = []

    for _, row in grouped.iterrows():

        records.append(
            {
                "inefficiency_type":
                    row[
                        "inefficiency_type"
                    ],

                "event_count":
                    int(
                        row[
                            "event_count"
                        ]
                    ),

                "total_potential_savings":
                    round(
                        float(
                            row[
                                "total_potential_savings"
                            ]
                        ),
                        2,
                    ),

                "average_potential_savings":
                    round(
                        float(
                            row[
                                "average_potential_savings"
                            ]
                        ),
                        2,
                    ),

                "total_cost":
                    round(
                        float(
                            row[
                                "total_cost"
                            ]
                        ),
                        2,
                    ),
            }
        )

    return records


# ============================================================
# HIGH COST RECORDS
# ============================================================


def get_high_cost_records(
    dataframe,
    limit=20,
):
    """
    Return records with the highest total costs.
    """

    if dataframe.empty:
        return []

    filtered = dataframe.sort_values(
        "total_cost",
        ascending=False,
    )

    if limit:
        filtered = filtered.head(
            limit
        )

    records = []

    for _, row in filtered.iterrows():

        records.append(
            {
                "cost_record_id":
                    row[
                        "cost_record_id"
                    ],

                "building_name":
                    row[
                        "building_name"
                    ],

                "timestamp":
                    row[
                        "timestamp"
                    ].isoformat(),

                "occupancy":
                    int(
                        row[
                            "occupancy"
                        ]
                    ),

                "total_cost":
                    round(
                        float(
                            row[
                                "total_cost"
                            ]
                        ),
                        2,
                    ),

                "expected_cost":
                    round(
                        float(
                            row[
                                "expected_cost"
                            ]
                        ),
                        2,
                    ),

                "potential_savings":
                    round(
                        float(
                            row[
                                "potential_savings"
                            ]
                        ),
                        2,
                    ),

                "inefficiency_type":
                    row[
                        "inefficiency_type"
                    ],

                "cost_status":
                    row[
                        "cost_status"
                    ],
            }
        )

    return records

# ============================================================
# COST INSIGHTS
# ============================================================


def generate_cost_insights(
    dataframe,
):
    """
    Generate simple cost optimization insights.
    """

    if dataframe.empty:
        return []

    summary = calculate_cost_summary(
        dataframe
    )

    buildings = (
        get_building_cost_comparison(
            dataframe
        )
    )

    opportunities = (
        get_savings_opportunities(
            dataframe
        )
    )

    insights = []

    insights.append(
        {
            "type": "COST_SUMMARY",
            "severity": "INFO",
            "message": (
                f"Total facility operating cost is "
                f"{summary['total_cost']:.2f}, "
                f"with estimated potential savings of "
                f"{summary['potential_savings']:.2f}."
            ),
        }
    )

    if (
        summary[
            "cost_variance"
        ] > 0
    ):
        insights.append(
            {
                "type":
                    "COST_VARIANCE",

                "severity":
                    "WARNING",

                "message":
                    (
                        "Actual operating cost is "
                        f"{summary['cost_variance']:.2f} "
                        "above the expected cost."
                    ),
            }
        )

    if buildings:

        highest_building = (
            buildings[0]
        )

        insights.append(
            {
                "type":
                    "BUILDING_SAVINGS",

                "severity":
                    "INFO",

                "message":
                    (
                        f"{highest_building['building_name']} "
                        "has the highest identified "
                        "potential savings at "
                        f"{highest_building['potential_savings']:.2f}."
                    ),
            }
        )

    if opportunities:

        top_opportunity = (
            opportunities[0]
        )

        readable_name = (
            top_opportunity[
                "inefficiency_type"
            ]
            .replace("_", " ")
            .title()
        )

        insights.append(
            {
                "type":
                    "OPTIMIZATION_OPPORTUNITY",

                "severity":
                    "INFO",

                "message":
                    (
                        f"{readable_name} is a major "
                        "optimization opportunity with "
                        "estimated savings of "
                        f"{top_opportunity['total_potential_savings']:.2f}."
                    ),
            }
        )

    return insights


# ============================================================
# COMMAND-LINE TEST
# ============================================================


def main():

    print()
    print("=" * 65)
    print(
        "FACILITYOPS AI - "
        "MILESTONE 4 COST ANALYTICS"
    )
    print("=" * 65)

    dataframe = load_cost_data()

    print()
    print(
        "Dataset loaded successfully."
    )

    print(
        "Rows:",
        len(dataframe),
    )

    print(
        "Buildings:",
        dataframe[
            "building_id"
        ].nunique(),
    )

    print()
    print("COST SUMMARY")
    print("-" * 65)

    summary = (
        calculate_cost_summary(
            dataframe
        )
    )

    for key, value in (
        summary.items()
    ):
        print(
            f"{key}: {value}"
        )

    print()
    print("COST BREAKDOWN")
    print("-" * 65)

    for item in (
        get_cost_breakdown(
            dataframe
        )
    ):
        print(item)

    print()
    print(
        "BUILDING COST COMPARISON"
    )
    print("-" * 65)

    for item in (
        get_building_cost_comparison(
            dataframe
        )
    ):
        print(item)

    print()
    print(
        "SAVINGS OPPORTUNITIES"
    )
    print("-" * 65)

    for item in (
        get_savings_opportunities(
            dataframe
        )
    ):
        print(item)

    print()
    print("COST INSIGHTS")
    print("-" * 65)

    for item in (
        generate_cost_insights(
            dataframe
        )
    ):
        print(item)

    print()
    print("=" * 65)
    print(
        "Cost analytics test completed."
    )
    print("=" * 65)


if __name__ == "__main__":
    main()