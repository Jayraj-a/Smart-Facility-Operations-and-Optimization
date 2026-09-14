from datetime import timedelta

import pandas as pd

from analytics.occupancy_analytics import (
    load_occupancy_data,
    get_latest_space_readings,
    calculate_occupancy_summary,
    get_space_utilization_table,
    get_building_occupancy_comparison,
    get_peak_usage_hours,
    get_underused_spaces,
    get_overcrowding_events,
    get_occupancy_heatmap,
)


# ============================================================
# FACILITYOPS AI
# MILESTONE 3 - OCCUPANCY AGENT
# ============================================================


class OccupancyAgent:
    """
    FacilityOps AI Occupancy Agent.

    Responsibilities:
    - Monitor room and building occupancy
    - Analyse space utilization
    - Detect overcrowding
    - Detect underused spaces
    - Recommend workspace allocation improvements
    - Generate occupancy insights
    - Analyse facility usage patterns
    """

    def __init__(self):
        self.name = "FacilityOps Occupancy Agent"

        self.overcrowding_threshold = 100.0
        self.high_utilization_threshold = 75.0
        self.optimal_utilization_threshold = 40.0
        self.low_utilization_threshold = 15.0

    # ========================================================
    # SAFE VALUE HELPERS
    # ========================================================

    @staticmethod
    def safe_float(value, default=0.0):
        try:
            if pd.isna(value):
                return default

            return float(value)

        except (TypeError, ValueError):
            return default

    @staticmethod
    def safe_int(value, default=0):
        try:
            if pd.isna(value):
                return default

            return int(value)

        except (TypeError, ValueError):
            return default

    # ========================================================
    # UTILIZATION STATUS
    # ========================================================

    def determine_utilization_status(
        self,
        utilization_percent,
    ):
        utilization = self.safe_float(
            utilization_percent
        )

        if utilization > self.overcrowding_threshold:
            return "OVERCROWDED"

        if utilization >= self.high_utilization_threshold:
            return "HIGH"

        if utilization >= self.optimal_utilization_threshold:
            return "OPTIMAL"

        if utilization >= self.low_utilization_threshold:
            return "LOW"

        return "UNDERUSED"

    # ========================================================
    # OCCUPANCY SEVERITY
    # ========================================================

    def determine_severity(
        self,
        utilization_percent,
    ):
        utilization = self.safe_float(
            utilization_percent
        )

        if utilization >= 110:
            return "CRITICAL"

        if utilization > 100:
            return "HIGH"

        if utilization >= 90:
            return "WARNING"

        return "NORMAL"

    # ========================================================
    # ANALYSE ONE SPACE
    # ========================================================

    def analyse_space(self, record):
        capacity = self.safe_int(
            record.get("capacity")
        )

        occupancy = self.safe_int(
            record.get("occupancy_count")
        )

        available_capacity = max(
            0,
            capacity - occupancy,
        )

        if capacity > 0:
            utilization = (
                occupancy
                / capacity
                * 100
            )
        else:
            utilization = 0.0

        utilization = round(
            utilization,
            2,
        )

        status = (
            self.determine_utilization_status(
                utilization
            )
        )

        severity = self.determine_severity(
            utilization
        )

        overcrowded = (
            occupancy > capacity
            if capacity > 0
            else False
        )

        recommendation = (
            self.generate_space_recommendation(
                status=status,
                utilization_percent=utilization,
                space_name=record.get(
                    "space_name",
                    "Unknown Space",
                ),
            )
        )

        alert = self.generate_overcrowding_alert(
            record=record,
            utilization_percent=utilization,
            severity=severity,
        )

        return {
            "facility_id": record.get(
                "facility_id"
            ),
            "facility_name": record.get(
                "facility_name"
            ),
            "building_id": record.get(
                "building_id"
            ),
            "building_name": record.get(
                "building_name"
            ),
            "block_id": record.get(
                "block_id"
            ),
            "block_name": record.get(
                "block_name"
            ),
            "space_id": record.get(
                "space_id"
            ),
            "space_name": record.get(
                "space_name"
            ),
            "space_type": record.get(
                "space_type"
            ),
            "timestamp": self.format_timestamp(
                record.get("timestamp")
            ),
            "capacity": capacity,
            "occupancy_count": occupancy,
            "available_capacity": (
                available_capacity
            ),
            "utilization_percent": utilization,
            "utilization_status": status,
            "overcrowded": overcrowded,
            "severity": severity,
            "recommendation": recommendation,
            "alert": alert,
        }

    # ========================================================
    # GENERATE SPACE RECOMMENDATION
    # ========================================================

    def generate_space_recommendation(
        self,
        status,
        utilization_percent,
        space_name,
    ):
        if status == "OVERCROWDED":
            return (
                f"{space_name} is above its safe "
                f"capacity. Redirect occupants to "
                f"nearby available spaces."
            )

        if status == "HIGH":
            return (
                f"{space_name} has high utilization. "
                f"Monitor capacity and prepare nearby "
                f"spaces if occupancy increases."
            )

        if status == "OPTIMAL":
            return (
                f"{space_name} is being utilized "
                f"efficiently. No immediate space "
                f"allocation change is required."
            )

        if status == "LOW":
            return (
                f"{space_name} has low utilization. "
                f"Review whether the space can support "
                f"other facility activities."
            )

        return (
            f"{space_name} is underused at "
            f"{utilization_percent:.1f}% utilization. "
            f"Consider workspace consolidation or "
            f"shared-space allocation."
        )

    # ========================================================
    # OVERCROWDING ALERT
    # ========================================================

    def generate_overcrowding_alert(
        self,
        record,
        utilization_percent,
        severity,
    ):
        if utilization_percent <= 100:
            return None

        space_name = record.get(
            "space_name",
            "Unknown Space",
        )

        occupancy = self.safe_int(
            record.get("occupancy_count")
        )

        capacity = self.safe_int(
            record.get("capacity")
        )

        return {
            "alert_type": "OVERCROWDING",
            "severity": severity,
            "space_id": record.get(
                "space_id"
            ),
            "space_name": space_name,
            "building_name": record.get(
                "building_name"
            ),
            "timestamp": self.format_timestamp(
                record.get("timestamp")
            ),
            "occupancy_count": occupancy,
            "capacity": capacity,
            "utilization_percent": round(
                utilization_percent,
                2,
            ),
            "message": (
                f"Overcrowding detected in "
                f"{space_name}. Current occupancy is "
                f"{occupancy} while capacity is "
                f"{capacity}."
            ),
            "recommended_action": (
                "Redirect occupants to available "
                "spaces and review space allocation."
            ),
        }

    # ========================================================
    # ANALYSE ALL LATEST SPACES
    # ========================================================

    def analyse_spaces(self, dataframe):
        latest = get_latest_space_readings(
            dataframe
        )

        analyses = []
        alerts = []

        for _, row in latest.iterrows():
            result = self.analyse_space(
                row.to_dict()
            )

            analyses.append(result)

            if result["alert"] is not None:
                alerts.append(
                    result["alert"]
                )

        return {
            "agent": self.name,
            "spaces_analysed": len(analyses),
            "spaces": analyses,
            "alerts": alerts,
            "alert_count": len(alerts),
        }

    # ========================================================
    # HISTORICAL OVERCROWDING ANALYSIS
    # ========================================================

    def analyse_overcrowding_history(
        self,
        dataframe,
        limit=50,
    ):
        events = get_overcrowding_events(
            dataframe,
            limit=limit,
        )

        results = []

        for event in events:
            utilization = self.safe_float(
                event.get(
                    "utilization_percent"
                )
            )

            severity = (
                self.determine_severity(
                    utilization
                )
            )

            results.append(
                {
                    **event,
                    "severity": severity,
                    "recommended_action": (
                        "Review occupancy flow and "
                        "redirect users to spaces with "
                        "available capacity."
                    ),
                }
            )

        return results

    # ========================================================
    # WORKSPACE ALLOCATION RECOMMENDATIONS
    # ========================================================

    def generate_workspace_recommendations(
        self,
        dataframe,
    ):
        underused = get_underused_spaces(
            dataframe,
            threshold=25.0,
        )

        recommendations = []

        for space in underused:
            utilization = self.safe_float(
                space.get(
                    "average_utilization_percent"
                )
            )

            if utilization < 15:
                priority = "HIGH"

                action = (
                    "Consider consolidating this "
                    "workspace or reallocating it for "
                    "another facility requirement."
                )

            else:
                priority = "MEDIUM"

                action = (
                    "Review scheduling and shared-space "
                    "allocation to improve utilization."
                )

            recommendations.append(
                {
                    "space_id": space.get(
                        "space_id"
                    ),
                    "space_name": space.get(
                        "space_name"
                    ),
                    "space_type": space.get(
                        "space_type"
                    ),
                    "building_name": space.get(
                        "building_name"
                    ),
                    "average_utilization_percent":
                        round(
                            utilization,
                            2,
                        ),
                    "priority": priority,
                    "recommendation": action,
                }
            )

        return recommendations

    # ========================================================
    # PEAK USAGE ANALYSIS
    # ========================================================

    def analyse_peak_usage(
        self,
        dataframe,
    ):
        peak_hours = get_peak_usage_hours(
            dataframe,
            top_n=5,
        )

        results = []

        for item in peak_hours:
            hour = self.safe_int(
                item.get("hour")
            )

            utilization = self.safe_float(
                item.get(
                    "average_utilization_percent"
                )
            )

            results.append(
                {
                    "hour": hour,
                    "time_label": (
                        f"{hour:02d}:00"
                    ),
                    "average_occupancy": (
                        self.safe_float(
                            item.get(
                                "average_occupancy"
                            )
                        )
                    ),
                    "average_utilization_percent":
                        round(
                            utilization,
                            2,
                        ),
                    "peak_occupancy": (
                        self.safe_int(
                            item.get(
                                "peak_occupancy"
                            )
                        )
                    ),
                    "insight": (
                        f"Facility utilization is "
                        f"typically high around "
                        f"{hour:02d}:00."
                    ),
                }
            )

        return results

    # ========================================================
    # SIMPLE USAGE FORECAST
    # ========================================================

    def forecast_usage(
        self,
        dataframe,
        hours=6,
    ):
        """
        Simple historical hour-of-day forecast.

        This is a baseline forecast using average
        historical occupancy for each hour.
        """

        if dataframe.empty:
            return []

        working = dataframe.copy()

        working["timestamp"] = pd.to_datetime(
            working["timestamp"]
        )

        working["hour"] = (
            working["timestamp"].dt.hour
        )

        hourly_average = (
            working
            .groupby("hour")
            .agg(
                expected_occupancy=(
                    "occupancy_count",
                    "sum",
                ),
                samples=(
                    "timestamp",
                    "nunique",
                ),
                average_utilization=(
                    "utilization_percent",
                    "mean",
                ),
            )
            .reset_index()
        )

        hourly_average[
            "expected_occupancy"
        ] = (
            hourly_average[
                "expected_occupancy"
            ]
            / hourly_average["samples"]
        )

        lookup = {
            self.safe_int(row["hour"]): {
                "expected_occupancy":
                    self.safe_float(
                        row[
                            "expected_occupancy"
                        ]
                    ),
                "average_utilization":
                    self.safe_float(
                        row[
                            "average_utilization"
                        ]
                    ),
            }
            for _, row in (
                hourly_average.iterrows()
            )
        }

        last_timestamp = (
            working["timestamp"].max()
        )

        forecast = []

        for step in range(1, hours + 1):
            forecast_time = (
                last_timestamp
                + timedelta(hours=step)
            )

            hour = forecast_time.hour

            historical = lookup.get(
                hour,
                {
                    "expected_occupancy": 0,
                    "average_utilization": 0,
                },
            )

            forecast.append(
                {
                    "timestamp":
                        forecast_time.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                    "hour": hour,
                    "expected_occupancy": (
                        round(
                            historical[
                                "expected_occupancy"
                            ],
                            2,
                        )
                    ),
                    "expected_utilization_percent":
                        round(
                            historical[
                                "average_utilization"
                            ],
                            2,
                        ),
                }
            )

        return forecast

    # ========================================================
    # COMPLETE AGENT ANALYSIS
    # ========================================================

    def run(self, dataframe):
        summary = calculate_occupancy_summary(
            dataframe
        )

        spaces = self.analyse_spaces(
            dataframe
        )

        building_comparison = (
            get_building_occupancy_comparison(
                dataframe
            )
        )

        workspace_recommendations = (
            self.generate_workspace_recommendations(
                dataframe
            )
        )

        peak_usage = self.analyse_peak_usage(
            dataframe
        )

        overcrowding_history = (
            self.analyse_overcrowding_history(
                dataframe,
                limit=20,
            )
        )

        forecast = self.forecast_usage(
            dataframe,
            hours=6,
        )

        heatmap = get_occupancy_heatmap(
            dataframe
        )

        return {
            "agent": self.name,
            "summary": summary,
            "current_spaces": spaces[
                "spaces"
            ],
            "current_alerts": spaces[
                "alerts"
            ],
            "current_alert_count": spaces[
                "alert_count"
            ],
            "building_comparison":
                building_comparison,
            "workspace_recommendations":
                workspace_recommendations,
            "peak_usage": peak_usage,
            "overcrowding_history":
                overcrowding_history,
            "usage_forecast": forecast,
            "heatmap": heatmap,
        }

    # ========================================================
    # TIMESTAMP FORMATTER
    # ========================================================

    @staticmethod
    def format_timestamp(value):
        if value is None:
            return None

        try:
            timestamp = pd.to_datetime(
                value
            )

            return timestamp.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        except Exception:
            return str(value)


# ============================================================
# GLOBAL OCCUPANCY AGENT
# ============================================================

occupancy_agent = OccupancyAgent()


# ============================================================
# COMMAND-LINE TEST
# ============================================================

def main():
    print()
    print("=" * 60)
    print("FACILITYOPS AI - MILESTONE 3")
    print("OCCUPANCY AGENT")
    print("=" * 60)

    dataframe = load_occupancy_data()

    result = occupancy_agent.run(
        dataframe
    )

    print()
    print("Agent:")
    print(result["agent"])

    print()
    print("Occupancy Summary")
    print("-" * 60)

    for key, value in (
        result["summary"].items()
    ):
        print(f"{key}: {value}")

    print()
    print("Current Space Analysis")
    print("-" * 60)

    for space in result[
        "current_spaces"
    ]:
        print(
            f"{space['space_id']} | "
            f"{space['space_name']} | "
            f"{space['occupancy_count']}/"
            f"{space['capacity']} | "
            f"{space['utilization_percent']:.2f}% | "
            f"{space['utilization_status']} | "
            f"{space['severity']}"
        )

    print()
    print("Current Occupancy Alerts")
    print("-" * 60)

    if not result["current_alerts"]:
        print(
            "No current overcrowding alerts."
        )

    for alert in result[
        "current_alerts"
    ]:
        print(
            f"[{alert['severity']}] "
            f"{alert['space_name']} | "
            f"{alert['message']}"
        )

    print()
    print("Workspace Recommendations")
    print("-" * 60)

    if not result[
        "workspace_recommendations"
    ]:
        print(
            "No workspace allocation "
            "recommendations."
        )

    for recommendation in result[
        "workspace_recommendations"
    ]:
        print(
            f"[{recommendation['priority']}] "
            f"{recommendation['space_name']} | "
            f"Average Utilization: "
            f"{recommendation['average_utilization_percent']:.2f}%"
        )

    print()
    print("Peak Usage")
    print("-" * 60)

    for peak in result["peak_usage"]:
        print(
            f"{peak['time_label']} | "
            f"Average Utilization: "
            f"{peak['average_utilization_percent']:.2f}%"
        )

    print()
    print("Recent Overcrowding History")
    print("-" * 60)

    history = result[
        "overcrowding_history"
    ]

    print(
        f"Recent events analysed: "
        f"{len(history)}"
    )

    for event in history[:5]:
        print(
            f"[{event['severity']}] "
            f"{event['space_name']} | "
            f"{event['occupancy_count']}/"
            f"{event['capacity']} | "
            f"{event['utilization_percent']:.2f}%"
        )

    print()
    print("6-Hour Usage Forecast")
    print("-" * 60)

    for forecast in result[
        "usage_forecast"
    ]:
        print(
            f"{forecast['timestamp']} | "
            f"Expected Occupancy: "
            f"{forecast['expected_occupancy']:.2f} | "
            f"Expected Utilization: "
            f"{forecast['expected_utilization_percent']:.2f}%"
        )

    print()
    print(
        "Heatmap records:",
        len(result["heatmap"]),
    )

    print()
    print("=" * 60)
    print(
        "Occupancy Agent completed successfully."
    )
    print("=" * 60)


if __name__ == "__main__":
    main()