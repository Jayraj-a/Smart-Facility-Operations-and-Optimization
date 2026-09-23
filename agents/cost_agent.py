import pandas as pd

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


# ============================================================
# FACILITYOPS AI
# MILESTONE 4 - COST OPTIMIZATION AGENT
# ============================================================


class CostOptimizationAgent:
    """
    Cost Optimization Agent

    Responsibilities:
    - Monitor facility operating costs
    - Compare actual and expected costs
    - Detect cost inefficiencies
    - Identify savings opportunities
    - Prioritize optimization actions
    - Generate cost recommendations
    - Estimate potential savings
    - Support cost optimization decisions
    """

    def __init__(self):

        self.name = (
            "FacilityOps Cost Optimization Agent"
        )

        self.priority_rank = {
            "NORMAL": 0,
            "LOW": 1,
            "MEDIUM": 2,
            "HIGH": 3,
            "CRITICAL": 4,
        }


    # ========================================================
    # SAFE VALUE HELPERS
    # ========================================================

    @staticmethod
    def safe_float(
        value,
        default=0.0,
    ):
        try:
            if pd.isna(value):
                return default

            return float(value)

        except (
            TypeError,
            ValueError,
        ):
            return default


    @staticmethod
    def safe_int(
        value,
        default=0,
    ):
        try:
            if pd.isna(value):
                return default

            return int(value)

        except (
            TypeError,
            ValueError,
        ):
            return default


    @staticmethod
    def safe_bool(value):

        if pd.isna(value):
            return False

        if isinstance(value, bool):
            return value

        if isinstance(
            value,
            (int, float),
        ):
            return bool(value)

        return str(value).strip().lower() in {
            "true",
            "1",
            "yes",
            "y",
        }


    @staticmethod
    def format_timestamp(value):

        if pd.isna(value):
            return None

        try:
            return pd.to_datetime(
                value
            ).isoformat()

        except Exception:
            return str(value)


    # ========================================================
    # CALCULATE COST EFFICIENCY SCORE
    # ========================================================

    def calculate_cost_efficiency_score(
        self,
        record,
    ):
        """
        Calculate a cost efficiency score from 0 to 100.

        Higher score means better cost efficiency.
        """

        total_cost = self.safe_float(
            record.get(
                "total_cost"
            )
        )

        expected_cost = self.safe_float(
            record.get(
                "expected_cost"
            )
        )

        potential_savings = (
            self.safe_float(
                record.get(
                    "potential_savings"
                )
            )
        )

        if expected_cost <= 0:
            return 100.0

        variance_percent = (
            (
                total_cost
                - expected_cost
            )
            / expected_cost
            * 100
        )

        penalty = 0.0

        if variance_percent > 0:
            penalty += min(
                variance_percent * 1.5,
                50,
            )

        savings_ratio = (
            potential_savings
            / total_cost
            * 100
            if total_cost > 0
            else 0.0
        )

        penalty += min(
            savings_ratio,
            30,
        )

        inefficiency = str(
            record.get(
                "inefficiency_type",
                "NONE",
            )
        ).upper()

        if inefficiency != "NONE":
            penalty += 10

        score = 100 - penalty

        return round(
            max(
                0.0,
                min(
                    score,
                    100.0,
                ),
            ),
            2,
        )


    # ========================================================
    # DETERMINE EFFICIENCY STATUS
    # ========================================================

    @staticmethod
    def determine_efficiency_status(
        score,
    ):

        if score >= 90:
            return "EXCELLENT"

        if score >= 75:
            return "GOOD"

        if score >= 55:
            return "WARNING"

        return "CRITICAL"


    # ========================================================
    # DETERMINE PRIORITY
    # ========================================================

    def determine_priority(
        self,
        record,
    ):

        potential_savings = (
            self.safe_float(
                record.get(
                    "potential_savings"
                )
            )
        )

        cost_status = str(
            record.get(
                "cost_status",
                "NORMAL",
            )
        ).upper()

        savings_priority = str(
            record.get(
                "savings_priority",
                "NORMAL",
            )
        ).upper()

        inefficiency_type = str(
            record.get(
                "inefficiency_type",
                "NONE",
            )
        ).upper()

        if (
            cost_status == "CRITICAL"
            or savings_priority
            == "CRITICAL"
        ):
            return "CRITICAL"

        if (
            cost_status == "HIGH"
            or savings_priority
            == "HIGH"
            or potential_savings >= 500
        ):
            return "HIGH"

        if (
            cost_status == "WARNING"
            or savings_priority
            == "MEDIUM"
            or potential_savings >= 200
        ):
            return "MEDIUM"

        if (
            inefficiency_type != "NONE"
            or potential_savings > 0
        ):
            return "LOW"

        return "NORMAL"


    # ========================================================
    # GENERATE RECOMMENDATION
    # ========================================================

    def generate_recommendation(
        self,
        record,
        priority,
    ):

        inefficiency_type = str(
            record.get(
                "inefficiency_type",
                "NONE",
            )
        ).upper()

        if (
            inefficiency_type
            == "HIGH_HVAC_USAGE"
        ):
            return (
                "Review HVAC operating schedules, "
                "temperature settings, equipment "
                "condition, and unnecessary runtime "
                "to reduce HVAC energy cost."
            )

        if (
            inefficiency_type
            == "EXCESS_LIGHTING"
        ):
            return (
                "Reduce unnecessary lighting usage "
                "and align lighting schedules with "
                "actual occupancy."
            )

        if (
            inefficiency_type
            == "HIGH_WATER_USAGE"
        ):
            return (
                "Inspect water usage for leaks, "
                "unnecessary consumption, and "
                "high-demand equipment."
            )

        if (
            inefficiency_type
            == "LOW_OCCUPANCY_HIGH_ENERGY"
        ):
            return (
                "Reduce energy consumption in "
                "low-occupancy areas and align "
                "HVAC and lighting operation with "
                "actual space utilization."
            )

        if (
            inefficiency_type
            == "MAINTENANCE_RISK"
        ):
            return (
                "Inspect equipment with increased "
                "operating cost and coordinate "
                "preventive maintenance to avoid "
                "further energy and repair costs."
            )

        if priority == "CRITICAL":
            return (
                "Immediately review this high-cost "
                "condition and implement cost "
                "reduction actions."
            )

        if priority == "HIGH":
            return (
                "Review this cost condition and "
                "schedule an optimization action."
            )

        if priority == "MEDIUM":
            return (
                "Monitor this cost condition and "
                "review possible savings actions."
            )

        if priority == "LOW":
            return (
                "Continue monitoring and apply "
                "low-impact optimization where "
                "appropriate."
            )

        return (
            "Cost performance is within the "
            "expected operating range."
        )


    # ========================================================
    # ANALYSE ONE COST RECORD
    # ========================================================

    def analyse_cost_record(
        self,
        record,
    ):

        total_cost = self.safe_float(
            record.get(
                "total_cost"
            )
        )

        expected_cost = self.safe_float(
            record.get(
                "expected_cost"
            )
        )

        potential_savings = (
            self.safe_float(
                record.get(
                    "potential_savings"
                )
            )
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

        efficiency_score = (
            self.calculate_cost_efficiency_score(
                record
            )
        )

        efficiency_status = (
            self.determine_efficiency_status(
                efficiency_score
            )
        )

        priority = (
            self.determine_priority(
                record
            )
        )

        recommendation = (
            self.generate_recommendation(
                record,
                priority,
            )
        )

        requires_action = (
            priority
            in {
                "MEDIUM",
                "HIGH",
                "CRITICAL",
            }
        )

        return {
            "cost_record_id":
                record.get(
                    "cost_record_id"
                ),

            "facility_id":
                record.get(
                    "facility_id"
                ),

            "facility_name":
                record.get(
                    "facility_name"
                ),

            "building_id":
                record.get(
                    "building_id"
                ),

            "building_name":
                record.get(
                    "building_name"
                ),

            "timestamp":
                self.format_timestamp(
                    record.get(
                        "timestamp"
                    )
                ),

            "occupancy":
                self.safe_int(
                    record.get(
                        "occupancy"
                    )
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
                    potential_savings,
                    2,
                ),

            "cost_per_occupant":
                round(
                    self.safe_float(
                        record.get(
                            "cost_per_occupant"
                        )
                    ),
                    2,
                ),

            "inefficiency_type":
                str(
                    record.get(
                        "inefficiency_type",
                        "NONE",
                    )
                ),

            "cost_status":
                str(
                    record.get(
                        "cost_status",
                        "NORMAL",
                    )
                ),

            "efficiency_score":
                efficiency_score,

            "efficiency_status":
                efficiency_status,

            "priority":
                priority,

            "requires_action":
                requires_action,

            "recommendation":
                recommendation,
        }


    # ========================================================
    # GENERATE OPTIMIZATION ALERT
    # ========================================================

    def generate_alert(
        self,
        analysis,
    ):

        if not analysis[
            "requires_action"
        ]:
            return None

        inefficiency = (
            analysis[
                "inefficiency_type"
            ]
            .replace("_", " ")
            .title()
        )

        return {
            "alert_type":
                "COST_OPTIMIZATION",

            "cost_record_id":
                analysis[
                    "cost_record_id"
                ],

            "building_id":
                analysis[
                    "building_id"
                ],

            "building_name":
                analysis[
                    "building_name"
                ],

            "timestamp":
                analysis[
                    "timestamp"
                ],

            "severity":
                analysis[
                    "priority"
                ],

            "inefficiency_type":
                analysis[
                    "inefficiency_type"
                ],

            "potential_savings":
                analysis[
                    "potential_savings"
                ],

            "message":
                (
                    f"{inefficiency} detected in "
                    f"{analysis['building_name']} "
                    f"with estimated potential "
                    f"savings of "
                    f"{analysis['potential_savings']:.2f}."
                ),

            "recommended_action":
                analysis[
                    "recommendation"
                ],
        }


    # ========================================================
    # ANALYSE COST RECORDS
    # ========================================================

    def analyse_cost_records(
        self,
        dataframe,
        limit=100,
    ):

        if dataframe.empty:
            return {
                "agent":
                    self.name,

                "records":
                    [],

                "alerts":
                    [],

                "alert_count":
                    0,
            }

        working = dataframe.copy()

        working = working.sort_values(
            "timestamp",
            ascending=False,
        )

        if limit:
            working = working.head(
                limit
            )

        analyses = []
        alerts = []

        for _, row in (
            working.iterrows()
        ):

            analysis = (
                self.analyse_cost_record(
                    row
                )
            )

            analyses.append(
                analysis
            )

            alert = (
                self.generate_alert(
                    analysis
                )
            )

            if alert:
                alerts.append(
                    alert
                )

        alerts = sorted(
            alerts,
            key=lambda item: (
                self.priority_rank.get(
                    item["severity"],
                    0,
                ),
                item[
                    "potential_savings"
                ],
            ),
            reverse=True,
        )

        return {
            "agent":
                self.name,

            "records":
                analyses,

            "alerts":
                alerts,

            "alert_count":
                len(alerts),
        }


    # ========================================================
    # GENERATE OPTIMIZATION OPPORTUNITIES
    # ========================================================

    def generate_optimization_opportunities(
        self,
        dataframe,
    ):

        opportunities = (
            get_savings_opportunities(
                dataframe
            )
        )

        results = []

        for item in opportunities:

            opportunity_type = str(
                item[
                    "inefficiency_type"
                ]
            )

            savings = (
                self.safe_float(
                    item[
                        "total_potential_savings"
                    ]
                )
            )

            if savings >= 5000:
                priority = "CRITICAL"

            elif savings >= 2500:
                priority = "HIGH"

            elif savings >= 1000:
                priority = "MEDIUM"

            else:
                priority = "LOW"

            recommendation = (
                self.generate_recommendation(
                    {
                        "inefficiency_type":
                            opportunity_type,
                    },
                    priority,
                )
            )

            results.append(
                {
                    "opportunity_type":
                        opportunity_type,

                    "event_count":
                        self.safe_int(
                            item[
                                "event_count"
                            ]
                        ),

                    "potential_savings":
                        round(
                            savings,
                            2,
                        ),

                    "average_savings":
                        round(
                            self.safe_float(
                                item[
                                    "average_potential_savings"
                                ]
                            ),
                            2,
                        ),

                    "priority":
                        priority,

                    "recommendation":
                        recommendation,
                }
            )

        return sorted(
            results,
            key=lambda item:
                item[
                    "potential_savings"
                ],
            reverse=True,
        )


    # ========================================================
    # BUILDING OPTIMIZATION
    # ========================================================

    def analyse_buildings(
        self,
        dataframe,
    ):

        buildings = (
            get_building_cost_comparison(
                dataframe
            )
        )

        results = []

        for building in buildings:

            total_cost = (
                self.safe_float(
                    building[
                        "total_cost"
                    ]
                )
            )

            expected_cost = (
                self.safe_float(
                    building[
                        "expected_cost"
                    ]
                )
            )

            potential_savings = (
                self.safe_float(
                    building[
                        "potential_savings"
                    ]
                )
            )

            savings_percent = (
                potential_savings
                / total_cost
                * 100
                if total_cost > 0
                else 0.0
            )

            if savings_percent >= 10:
                status = (
                    "HIGH_OPTIMIZATION_POTENTIAL"
                )

            elif savings_percent >= 5:
                status = (
                    "MODERATE_OPTIMIZATION_POTENTIAL"
                )

            else:
                status = (
                    "GOOD_COST_CONTROL"
                )

            results.append(
                {
                    **building,

                    "savings_percent":
                        round(
                            savings_percent,
                            2,
                        ),

                    "optimization_status":
                        status,

                    "is_above_expected_cost":
                        (
                            total_cost
                            > expected_cost
                        ),
                }
            )

        return results


    # ========================================================
    # COST FORECAST
    # ========================================================

    def forecast_cost(
        self,
        dataframe,
        days=7,
    ):
        """
        Generate a simple future cost forecast using
        recent average daily operating cost.

        This is a historical baseline forecast,
        not a machine-learning model.
        """

        if dataframe.empty:
            return []

        working = dataframe.copy()

        working["date"] = (
            working[
                "timestamp"
            ].dt.date
        )

        daily = (
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
            )
        )

        recent = daily.tail(7)

        if recent.empty:
            return []

        average_daily_cost = float(
            recent[
                "total_cost"
            ].mean()
        )

        average_expected_cost = float(
            recent[
                "expected_cost"
            ].mean()
        )

        last_timestamp = (
            working[
                "timestamp"
            ].max()
        )

        results = []

        for day_number in range(
            1,
            days + 1,
        ):

            forecast_date = (
                last_timestamp
                + pd.Timedelta(
                    days=day_number
                )
            )

            predicted_cost = (
                average_daily_cost
            )

            expected_cost = (
                average_expected_cost
            )

            predicted_variance = (
                predicted_cost
                - expected_cost
            )

            results.append(
                {
                    "date":
                        forecast_date
                        .date()
                        .isoformat(),

                    "predicted_cost":
                        round(
                            predicted_cost,
                            2,
                        ),

                    "expected_cost":
                        round(
                            expected_cost,
                            2,
                        ),

                    "predicted_variance":
                        round(
                            predicted_variance,
                            2,
                        ),
                }
            )

        return results


    # ========================================================
    # RUN COMPLETE AGENT
    # ========================================================

    def run(
        self,
        dataframe,
    ):

        summary = (
            calculate_cost_summary(
                dataframe
            )
        )

        record_analysis = (
            self.analyse_cost_records(
                dataframe,
                limit=100,
            )
        )

        return {
            "agent":
                self.name,

            "status":
                "ACTIVE",

            "summary":
                summary,

            "cost_breakdown":
                get_cost_breakdown(
                    dataframe
                ),

            "building_comparison":
                self.analyse_buildings(
                    dataframe
                ),

            "daily_cost_trend":
                get_daily_cost_trend(
                    dataframe
                ),

            "hourly_cost_pattern":
                get_hourly_cost_pattern(
                    dataframe
                ),

            "optimization_opportunities":
                self.generate_optimization_opportunities(
                    dataframe
                ),

            "cost_inefficiencies":
                get_cost_inefficiencies(
                    dataframe,
                    limit=30,
                ),

            "high_cost_records":
                get_high_cost_records(
                    dataframe,
                    limit=20,
                ),

            "alerts":
                record_analysis[
                    "alerts"
                ],

            "alert_count":
                record_analysis[
                    "alert_count"
                ],

            "recent_analysis":
                record_analysis[
                    "records"
                ],

            "forecast":
                self.forecast_cost(
                    dataframe,
                    days=7,
                ),

            "insights":
                generate_cost_insights(
                    dataframe
                ),
        }


# ============================================================
# GLOBAL AGENT INSTANCE
# ============================================================


cost_agent = CostOptimizationAgent()


# ============================================================
# COMMAND-LINE TEST
# ============================================================


def main():

    print()
    print("=" * 70)
    print(
        "FACILITYOPS AI - "
        "COST OPTIMIZATION AGENT"
    )
    print("=" * 70)

    dataframe = load_cost_data()

    print()
    print(
        "Cost dataset loaded."
    )

    print(
        "Records:",
        len(dataframe),
    )

    result = cost_agent.run(
        dataframe
    )

    print()
    print("AGENT")
    print("-" * 70)

    print(
        result["agent"]
    )

    print(
        "Status:",
        result["status"]
    )

    print()
    print("COST SUMMARY")
    print("-" * 70)

    for key, value in (
        result[
            "summary"
        ].items()
    ):
        print(
            f"{key}: {value}"
        )

    print()
    print(
        "OPTIMIZATION OPPORTUNITIES"
    )
    print("-" * 70)

    for opportunity in (
        result[
            "optimization_opportunities"
        ]
    ):
        print(
            opportunity
        )

    print()
    print("BUILDING ANALYSIS")
    print("-" * 70)

    for building in (
        result[
            "building_comparison"
        ]
    ):
        print(
            building
        )

    print()
    print("COST ALERTS")
    print("-" * 70)

    print(
        "Alert Count:",
        result[
            "alert_count"
        ],
    )

    for alert in (
        result[
            "alerts"
        ][:10]
    ):
        print(
            alert
        )

    print()
    print("7-DAY COST FORECAST")
    print("-" * 70)

    for forecast in (
        result[
            "forecast"
        ]
    ):
        print(
            forecast
        )

    print()
    print("COST INSIGHTS")
    print("-" * 70)

    for insight in (
        result[
            "insights"
        ]
    ):
        print(
            insight
        )

    print()
    print("=" * 70)
    print(
        "Cost Optimization Agent "
        "test completed successfully."
    )
    print("=" * 70)


if __name__ == "__main__":
    main()