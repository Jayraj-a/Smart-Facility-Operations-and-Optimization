"""
FacilityOps AI
Milestone 2 - Maintenance Agent

Responsibilities:
- Monitor equipment health
- Analyse asset sensor readings
- Detect abnormal equipment behaviour
- Use the predictive maintenance ML model
- Calculate equipment health scores
- Determine maintenance priority
- Predict maintenance schedules
- Generate maintenance alerts
- Generate maintenance work-order recommendations

This agent operates on simulated asset-monitoring data
for the Milestone 2 prototype.
"""

from datetime import timedelta

import pandas as pd

from analytics.maintenance_analytics import (
    calculate_equipment_health_score,
    health_status_from_score,
    maintenance_priority,
)

from analytics.maintenance_prediction import (
    predict_maintenance,
)


# ============================================================
# MAINTENANCE AGENT
# ============================================================

class MaintenanceAgent:
    """
    FacilityOps AI Maintenance Agent.

    Combines:
    - Equipment health scoring
    - Sensor-condition analysis
    - ML maintenance prediction
    - Maintenance scheduling
    - Alert generation
    """

    def __init__(self):
        self.name = "Maintenance Agent"

        self.version = "1.0"

        self.health_thresholds = {
            "critical": 50,
            "warning": 70,
            "good": 85,
        }

    # ========================================================
    # SAFE NUMBER
    # ========================================================

    @staticmethod
    def safe_float(
        value,
        default=0.0,
    ):
        try:
            number = float(value)

            if pd.isna(number):
                return default

            return number

        except (
            TypeError,
            ValueError,
        ):
            return default

    # ========================================================
    # HEALTH ANALYSIS
    # ========================================================

    def analyse_health(
        self,
        reading,
    ):
        """
        Calculate current equipment health.
        """

        health_score = (
            calculate_equipment_health_score(
                reading
            )
        )

        health_status = (
            health_status_from_score(
                health_score
            )
        )

        return {
            "health_score":
                health_score,

            "health_status":
                health_status,
        }

    # ========================================================
    # ML PREDICTION
    # ========================================================

    def analyse_prediction(
        self,
        reading,
    ):
        """
        Run the predictive-maintenance model.
        """

        return predict_maintenance(
            reading
        )

    # ========================================================
    # SENSOR CONDITION ANALYSIS
    # ========================================================

    def analyse_sensor_conditions(
        self,
        reading,
    ):
        """
        Detect potentially concerning equipment conditions.
        """

        conditions = []

        temperature = self.safe_float(
            reading.get(
                "temperature_c"
            )
        )

        vibration = self.safe_float(
            reading.get(
                "vibration_mm_s"
            )
        )

        pressure = self.safe_float(
            reading.get(
                "pressure_bar"
            )
        )

        power = self.safe_float(
            reading.get(
                "power_kw"
            )
        )

        days_since_service = (
            self.safe_float(
                reading.get(
                    "days_since_service"
                )
            )
        )

        # ----------------------------------------------------
        # TEMPERATURE
        # ----------------------------------------------------

        if temperature > 80:

            conditions.append(
                {
                    "metric":
                        "Temperature",

                    "severity":
                        "CRITICAL",

                    "observed_value":
                        round(
                            temperature,
                            2,
                        ),

                    "message":
                        (
                            "Equipment temperature is "
                            "at a critical level."
                        ),
                }
            )

        elif temperature > 70:

            conditions.append(
                {
                    "metric":
                        "Temperature",

                    "severity":
                        "HIGH",

                    "observed_value":
                        round(
                            temperature,
                            2,
                        ),

                    "message":
                        (
                            "Equipment temperature is "
                            "higher than the recommended "
                            "operating range."
                        ),
                }
            )

        # ----------------------------------------------------
        # VIBRATION
        # ----------------------------------------------------

        if vibration > 5.0:

            conditions.append(
                {
                    "metric":
                        "Vibration",

                    "severity":
                        "CRITICAL",

                    "observed_value":
                        round(
                            vibration,
                            2,
                        ),

                    "message":
                        (
                            "Very high vibration detected. "
                            "Mechanical inspection is "
                            "recommended."
                        ),
                }
            )

        elif vibration > 4.0:

            conditions.append(
                {
                    "metric":
                        "Vibration",

                    "severity":
                        "HIGH",

                    "observed_value":
                        round(
                            vibration,
                            2,
                        ),

                    "message":
                        (
                            "Elevated vibration detected."
                        ),
                }
            )

        # ----------------------------------------------------
        # PRESSURE
        # ----------------------------------------------------

        if (
            pressure < 3.0
            or pressure > 8.0
        ):

            conditions.append(
                {
                    "metric":
                        "Pressure",

                    "severity":
                        "HIGH",

                    "observed_value":
                        round(
                            pressure,
                            2,
                        ),

                    "message":
                        (
                            "Equipment pressure is outside "
                            "the expected operating range."
                        ),
                }
            )

        # ----------------------------------------------------
        # POWER
        # ----------------------------------------------------

        if power > 90:

            conditions.append(
                {
                    "metric":
                        "Power",

                    "severity":
                        "HIGH",

                    "observed_value":
                        round(
                            power,
                            2,
                        ),

                    "message":
                        (
                            "High equipment power demand "
                            "detected."
                        ),
                }
            )

        # ----------------------------------------------------
        # SERVICE AGE
        # ----------------------------------------------------

        if days_since_service > 180:

            conditions.append(
                {
                    "metric":
                        "Service Interval",

                    "severity":
                        "HIGH",

                    "observed_value":
                        round(
                            days_since_service,
                            1,
                        ),

                    "message":
                        (
                            "The asset has exceeded the "
                            "recommended service interval."
                        ),
                }
            )

        elif days_since_service > 120:

            conditions.append(
                {
                    "metric":
                        "Service Interval",

                    "severity":
                        "MEDIUM",

                    "observed_value":
                        round(
                            days_since_service,
                            1,
                        ),

                    "message":
                        (
                            "The asset is approaching a "
                            "scheduled maintenance interval."
                        ),
                }
            )

        return conditions

    # ========================================================
    # PRIORITY
    # ========================================================

    def determine_priority(
        self,
        health_score,
        prediction,
        conditions,
    ):
        """
        Determine overall maintenance priority.
        """

        probability = (
            self.safe_float(
                prediction.get(
                    "maintenance_probability"
                )
            )
        )

        predicted_required = int(
            self.safe_float(
                prediction.get(
                    "maintenance_required"
                )
            )
        )

        severities = {
            str(
                condition.get(
                    "severity",
                    ""
                )
            ).upper()
            for condition
            in conditions
        }

        if (
            health_score < 50
            or probability >= 0.80
            or "CRITICAL" in severities
        ):
            return "CRITICAL"

        if (
            predicted_required == 1
            or probability >= 0.60
            or health_score < 70
            or "HIGH" in severities
        ):
            return "HIGH"

        if (
            probability >= 0.35
            or health_score < 85
            or "MEDIUM" in severities
        ):
            return "MEDIUM"

        return "LOW"

    # ========================================================
    # MAINTENANCE SCHEDULE
    # ========================================================

    def predict_schedule(
        self,
        reading,
        priority,
    ):
        """
        Generate the recommended maintenance date.
        """

        timestamp = pd.to_datetime(
            reading.get(
                "timestamp"
            ),
            errors="coerce",
        )

        if pd.isna(timestamp):
            timestamp = (
                pd.Timestamp.now()
            )

        if priority == "CRITICAL":
            days_until_service = 1

        elif priority == "HIGH":
            days_until_service = 7

        elif priority == "MEDIUM":
            days_until_service = 30

        else:
            days_until_service = 90

        recommended_date = (
            timestamp
            + timedelta(
                days=days_until_service
            )
        )

        return {
            "days_until_service":
                days_until_service,

            "recommended_maintenance_date":
                recommended_date
                .date()
                .isoformat(),
        }

    # ========================================================
    # ALERT
    # ========================================================

    def generate_alert(
        self,
        reading,
        health,
        prediction,
        priority,
        conditions,
        schedule,
    ):
        """
        Generate a maintenance alert when attention is needed.
        """

        if priority == "LOW":
            return None

        asset_name = (
            reading.get(
                "asset_name"
            )
            or reading.get(
                "asset_id"
            )
            or "Asset"
        )

        health_score = (
            health[
                "health_score"
            ]
        )

        probability_percent = (
            prediction.get(
                "maintenance_probability_percent",
                0,
            )
        )

        if priority == "CRITICAL":

            title = (
                f"Critical Maintenance Required - "
                f"{asset_name}"
            )

            message = (
                f"{asset_name} requires immediate "
                f"maintenance review. Equipment health "
                f"is {health_score:.1f}/100 and the "
                f"predicted maintenance risk is "
                f"{probability_percent:.1f}%."
            )

        elif priority == "HIGH":

            title = (
                f"Maintenance Required - "
                f"{asset_name}"
            )

            message = (
                f"{asset_name} shows conditions that "
                f"require maintenance attention. "
                f"Recommended service is within "
                f"{schedule['days_until_service']} days."
            )

        else:

            title = (
                f"Maintenance Watch - "
                f"{asset_name}"
            )

            message = (
                f"{asset_name} should be monitored and "
                f"scheduled for preventive maintenance "
                f"within "
                f"{schedule['days_until_service']} days."
            )

        return {
            "alert_type":
                "MAINTENANCE",

            "asset_id":
                reading.get(
                    "asset_id"
                ),

            "asset_name":
                asset_name,

            "asset_type":
                reading.get(
                    "asset_type"
                ),

            "building_name":
                reading.get(
                    "building_name"
                ),

            "block_name":
                reading.get(
                    "block_name"
                ),

            "source_timestamp":
                (
                    str(
                        reading.get(
                            "timestamp"
                        )
                    )
                ),

            "severity":
                priority,

            "title":
                title,

            "message":
                message,

            "health_score":
                health_score,

            "health_status":
                health[
                    "health_status"
                ],

            "maintenance_probability":
                prediction.get(
                    "maintenance_probability"
                ),

            "maintenance_probability_percent":
                probability_percent,

            "recommended_maintenance_date":
                schedule[
                    "recommended_maintenance_date"
                ],

            "days_until_service":
                schedule[
                    "days_until_service"
                ],

            "conditions":
                conditions,
        }

    # ========================================================
    # WORK ORDER RECOMMENDATION
    # ========================================================

    def generate_work_order(
        self,
        reading,
        priority,
        schedule,
        conditions,
    ):
        """
        Generate a maintenance work-order recommendation.

        This does not represent an external ticketing system.
        It creates the work-order information required by
        the FacilityOps prototype.
        """

        if priority == "LOW":
            return None

        condition_metrics = [
            condition.get(
                "metric"
            )
            for condition
            in conditions
            if condition.get(
                "metric"
            )
        ]

        if condition_metrics:
            reason = (
                "Review "
                + ", ".join(
                    condition_metrics
                )
                + "."
            )
        else:
            reason = (
                "Preventive maintenance recommended "
                "based on equipment health and "
                "predictive-maintenance risk."
            )

        return {
            "asset_id":
                reading.get(
                    "asset_id"
                ),

            "asset_name":
                reading.get(
                    "asset_name"
                ),

            "asset_type":
                reading.get(
                    "asset_type"
                ),

            "building_name":
                reading.get(
                    "building_name"
                ),

            "block_name":
                reading.get(
                    "block_name"
                ),

            "priority":
                priority,

            "status":
                "RECOMMENDED",

            "recommended_date":
                schedule[
                    "recommended_maintenance_date"
                ],

            "reason":
                reason,
        }

    # ========================================================
    # ANALYSE READING
    # ========================================================

    def analyse_reading(
        self,
        reading,
    ):
        """
        Complete Maintenance Agent analysis for one reading.
        """

        health = (
            self.analyse_health(
                reading
            )
        )

        prediction = (
            self.analyse_prediction(
                reading
            )
        )

        conditions = (
            self.analyse_sensor_conditions(
                reading
            )
        )

        priority = (
            self.determine_priority(
                health[
                    "health_score"
                ],
                prediction,
                conditions,
            )
        )

        schedule = (
            self.predict_schedule(
                reading,
                priority,
            )
        )

        alert = (
            self.generate_alert(
                reading,
                health,
                prediction,
                priority,
                conditions,
                schedule,
            )
        )

        work_order = (
            self.generate_work_order(
                reading,
                priority,
                schedule,
                conditions,
            )
        )

        return {
            "asset_id":
                reading.get(
                    "asset_id"
                ),

            "asset_name":
                reading.get(
                    "asset_name"
                ),

            "asset_type":
                reading.get(
                    "asset_type"
                ),

            "building_name":
                reading.get(
                    "building_name"
                ),

            "block_name":
                reading.get(
                    "block_name"
                ),

            "timestamp":
                str(
                    reading.get(
                        "timestamp"
                    )
                ),

            "health":
                health,

            "prediction":
                prediction,

            "sensor_conditions":
                conditions,

            "priority":
                priority,

            "maintenance_schedule":
                schedule,

            "alert":
                alert,

            "work_order":
                work_order,
        }

    # ========================================================
    # ANALYSE ALL LATEST ASSETS
    # ========================================================

    def analyse_assets(
        self,
        dataframe,
    ):
        """
        Analyse the latest reading from every asset.
        """

        if dataframe.empty:
            return []

        df = dataframe.copy()

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce",
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
        )

        results = []

        for _, row in latest.iterrows():

            reading = (
                row.to_dict()
            )

            result = (
                self.analyse_reading(
                    reading
                )
            )

            results.append(
                result
            )

        return results


# ============================================================
# AGENT INSTANCE
# ============================================================

maintenance_agent = (
    MaintenanceAgent()
)


# ============================================================
# COMMAND-LINE TEST
# ============================================================

def main():
    from analytics.maintenance_analytics import (
        load_maintenance_data,
    )

    dataframe = (
        load_maintenance_data()
    )

    agent = (
        MaintenanceAgent()
    )

    results = (
        agent.analyse_assets(
            dataframe
        )
    )

    print()

    print(
        "FacilityOps AI - Milestone 2"
    )

    print(
        "Maintenance Agent"
    )

    print()

    print(
        f"Assets analysed: "
        f"{len(results)}"
    )

    print()

    print(
        "Latest Asset Analysis"
    )

    print(
        "---------------------"
    )

    for result in results:

        health = (
            result[
                "health"
            ]
        )

        prediction = (
            result[
                "prediction"
            ]
        )

        schedule = (
            result[
                "maintenance_schedule"
            ]
        )

        print(
            f"{result['asset_id']} | "
            f"{result['asset_name']} | "
            f"Health: "
            f"{health['health_score']:.2f} | "
            f"{health['health_status']} | "
            f"Risk: "
            f"{prediction['maintenance_probability_percent']:.2f}% | "
            f"Priority: "
            f"{result['priority']} | "
            f"Service: "
            f"{schedule['recommended_maintenance_date']}"
        )

    print()

    alerts = [
        result[
            "alert"
        ]
        for result in results
        if result[
            "alert"
        ]
        is not None
    ]

    work_orders = [
        result[
            "work_order"
        ]
        for result in results
        if result[
            "work_order"
        ]
        is not None
    ]

    print(
        f"Maintenance alerts generated: "
        f"{len(alerts)}"
    )

    print(
        f"Work-order recommendations: "
        f"{len(work_orders)}"
    )

    print()


if __name__ == "__main__":
    main()