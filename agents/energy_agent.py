import pandas as pd

from analytics.anomaly_detection import (
    predict_anomaly,
)


class EnergyMonitoringAgent:

    def __init__(
        self,
        electricity_threshold=25,
        hvac_threshold=25,
        water_threshold=40,
    ):

        self.electricity_threshold = (
            electricity_threshold
        )

        self.hvac_threshold = (
            hvac_threshold
        )

        self.water_threshold = (
            water_threshold
        )


    def percentage_change(
        self,
        observed,
        expected,
    ):

        if expected is None:
            return 0.0

        if expected == 0:
            return 0.0

        return (
            (observed - expected)
            / expected
        ) * 100


    def get_baseline(
        self,
        historical_data,
        current_row,
        metric,
    ):
        """
        Baseline is calculated from readings for the same
        building/block and preferably the same hour.

        This avoids simply comparing unrelated buildings.
        """

        if historical_data.empty:
            return float(current_row[metric])

        filtered = historical_data.copy()

        if "building_name" in filtered.columns:

            filtered = filtered[
                filtered["building_name"]
                == current_row["building_name"]
            ]

        if (
            "block_name" in filtered.columns
            and "block_name" in current_row
        ):

            filtered = filtered[
                filtered["block_name"]
                == current_row["block_name"]
            ]

        if filtered.empty:

            filtered = historical_data.copy()

        if (
            "timestamp" in filtered.columns
            and "timestamp" in current_row
        ):

            filtered["timestamp"] = pd.to_datetime(
                filtered["timestamp"],
                errors="coerce",
            )

            current_time = pd.to_datetime(
                current_row["timestamp"]
            )

            same_hour = filtered[
                filtered["timestamp"].dt.hour
                == current_time.hour
            ]

            if len(same_hour) >= 3:
                filtered = same_hour

        value = filtered[metric].mean()

        if pd.isna(value):
            return float(current_row[metric])

        return float(value)


    def classify_severity(
        self,
        percentage,
    ):

        absolute = abs(percentage)

        if absolute >= 50:
            return "CRITICAL"

        if absolute >= 30:
            return "HIGH"

        if absolute >= 20:
            return "WARNING"

        return "WATCH"


    def analyse_reading(
        self,
        current_row,
        historical_data,
    ):
        """
        Main Energy Monitoring Agent.

        Combines:
        1. ML anomaly detection
        2. Historical baseline analysis
        3. Operational energy rules
        """

        alerts = []


        # ===============================================
        # ML ANOMALY DETECTION
        # ===============================================

        ml_result = predict_anomaly(
            current_row
        )

        if (
            ml_result["model_available"]
            and ml_result["is_anomaly"]
        ):

            alerts.append(
                {
                    "alert_type":
                        "ISSUE",

                    "metric":
                        "combined_energy",

                    "observed_value":
                        float(
                            current_row[
                                "electricity_kwh"
                            ]
                        ),

                    "expected_value":
                        None,

                    "change_percent":
                        None,

                    "severity":
                        (
                            "CRITICAL"
                            if ml_result[
                                "probability"
                            ] >= 0.85
                            else "HIGH"
                        ),

                    "title":
                        "Unusual consumption pattern detected",

                    "message":
                        (
                            "The energy anomaly model detected "
                            f"an abnormal facility pattern with "
                            f"{ml_result['probability'] * 100:.1f}% "
                            "model confidence."
                        ),

                    "model_probability":
                        ml_result[
                            "probability"
                        ],
                }
            )


        # ===============================================
        # ELECTRICITY
        # ===============================================

        electricity = float(
            current_row[
                "electricity_kwh"
            ]
        )

        electricity_baseline = (
            self.get_baseline(
                historical_data,
                current_row,
                "electricity_kwh",
            )
        )

        electricity_change = (
            self.percentage_change(
                electricity,
                electricity_baseline,
            )
        )

        if (
            electricity_change
            >= self.electricity_threshold
        ):

            severity = (
                self.classify_severity(
                    electricity_change
                )
            )

            alerts.append(
                {
                    "alert_type":
                        "CONSUMPTION",

                    "metric":
                        "electricity",

                    "observed_value":
                        round(
                            electricity,
                            2,
                        ),

                    "expected_value":
                        round(
                            electricity_baseline,
                            2,
                        ),

                    "change_percent":
                        round(
                            electricity_change,
                            2,
                        ),

                    "severity":
                        severity,

                    "title":
                        "Electricity consumption increased",

                    "message":
                        (
                            f"Electricity usage is "
                            f"{electricity_change:.1f}% "
                            "above the normal baseline."
                        ),
                }
            )


        # ===============================================
        # HVAC
        # ===============================================

        hvac = float(
            current_row[
                "hvac_kwh"
            ]
        )

        hvac_baseline = (
            self.get_baseline(
                historical_data,
                current_row,
                "hvac_kwh",
            )
        )

        hvac_change = (
            self.percentage_change(
                hvac,
                hvac_baseline,
            )
        )

        occupancy = float(
            current_row[
                "occupancy"
            ]
        )


        if (
            hvac_change
            >= self.hvac_threshold
            and occupancy < 80
        ):

            alerts.append(
                {
                    "alert_type":
                        "CONSUMPTION",

                    "metric":
                        "hvac",

                    "observed_value":
                        round(
                            hvac,
                            2,
                        ),

                    "expected_value":
                        round(
                            hvac_baseline,
                            2,
                        ),

                    "change_percent":
                        round(
                            hvac_change,
                            2,
                        ),

                    "severity":
                        self.classify_severity(
                            hvac_change
                        ),

                    "title":
                        "High HVAC usage during low occupancy",

                    "message":
                        (
                            f"HVAC usage is "
                            f"{hvac_change:.1f}% "
                            "above baseline while occupancy "
                            f"is only {occupancy:.0f} people."
                        ),
                }
            )


        # ===============================================
        # LIGHTING
        # ===============================================

        timestamp = pd.to_datetime(
            current_row[
                "timestamp"
            ]
        )

        lighting = float(
            current_row[
                "lighting_kwh"
            ]
        )

        if (
            (
                timestamp.hour < 7
                or timestamp.hour >= 19
            )
            and occupancy < 50
            and lighting > 70
        ):

            alerts.append(
                {
                    "alert_type":
                        "ISSUE",

                    "metric":
                        "lighting",

                    "observed_value":
                        round(
                            lighting,
                            2,
                        ),

                    "expected_value":
                        70.0,

                    "change_percent":
                        round(
                            self.percentage_change(
                                lighting,
                                70,
                            ),
                            2,
                        ),

                    "severity":
                        "WARNING",

                    "title":
                        "Lighting active outside busy hours",

                    "message":
                        (
                            "Lighting consumption is elevated "
                            "during a low-occupancy period."
                        ),
                }
            )


        # ===============================================
        # WATER
        # ===============================================

        water = float(
            current_row[
                "water_liters"
            ]
        )

        water_baseline = (
            self.get_baseline(
                historical_data,
                current_row,
                "water_liters",
            )
        )

        water_change = (
            self.percentage_change(
                water,
                water_baseline,
            )
        )

        if (
            water_change
            >= self.water_threshold
        ):

            alerts.append(
                {
                    "alert_type":
                        "ISSUE",

                    "metric":
                        "water",

                    "observed_value":
                        round(
                            water,
                            2,
                        ),

                    "expected_value":
                        round(
                            water_baseline,
                            2,
                        ),

                    "change_percent":
                        round(
                            water_change,
                            2,
                        ),

                    "severity":
                        self.classify_severity(
                            water_change
                        ),

                    "title":
                        "Unusual water consumption",

                    "message":
                        (
                            f"Water consumption is "
                            f"{water_change:.1f}% "
                            "above its historical baseline."
                        ),
                }
            )


        return {
            "ml_detection":
                ml_result,

            "alerts":
                alerts,

            "alert_count":
                len(alerts),
        }



def generate_recommendations(df):
    """
    Compatibility function for the existing frontend.

    The frontend still calls the existing
    /api/recommendations endpoint.

    We return consumption analysis alerts instead of
    calling them AI recommendations.
    """

    if df.empty:

        return [
            {
                "level":
                    "success",

                "title":
                    "Monitoring active",

                "message":
                    "No consumption data is available for analysis.",
            }
        ]


    recommendations = []


    electricity_average = (
        df["electricity_kwh"].mean()
    )

    electricity_peak = (
        df["electricity_kwh"].max()
    )

    if electricity_peak > (
        electricity_average * 1.25
    ):

        percentage = (
            (
                electricity_peak
                - electricity_average
            )
            / electricity_average
        ) * 100

        recommendations.append(
            {
                "level":
                    "warning",

                "title":
                    "Electricity peak detected",

                "message":
                    (
                        f"Peak electricity consumption is "
                        f"{percentage:.1f}% above the "
                        "selected-period average."
                    ),
            }
        )


    low_occupancy = df[
        df["occupancy"] < 80
    ]

    if not low_occupancy.empty:

        overall_hvac = (
            df["hvac_kwh"].mean()
        )

        low_occupancy_hvac = (
            low_occupancy[
                "hvac_kwh"
            ].mean()
        )

        if (
            low_occupancy_hvac
            > overall_hvac
        ):

            recommendations.append(
                {
                    "level":
                        "warning",

                    "title":
                        "HVAC consumption needs attention",

                    "message":
                        (
                            "HVAC consumption remains high "
                            "during low-occupancy periods."
                        ),
                }
            )


    after_hours = df.copy()

    after_hours["timestamp"] = (
        pd.to_datetime(
            after_hours["timestamp"]
        )
    )

    after_hours = after_hours[
        (
            after_hours[
                "timestamp"
            ].dt.hour < 7
        )
        |
        (
            after_hours[
                "timestamp"
            ].dt.hour >= 19
        )
    ]

    if not after_hours.empty:

        lighting_average = (
            after_hours[
                "lighting_kwh"
            ].mean()
        )

        if lighting_average > 70:

            recommendations.append(
                {
                    "level":
                        "warning",

                    "title":
                        "After-hours lighting usage",

                    "message":
                        (
                            "Lighting consumption remains "
                            "elevated outside normal "
                            "operating hours."
                        ),
                }
            )


    labelled_count = (
        df["is_anomaly"].sum()
        if "is_anomaly" in df.columns
        else 0
    )

    if labelled_count > 0:

        recommendations.append(
            {
                "level":
                    "danger",

                "title":
                    "Labelled abnormal readings present",

                "message":
                    (
                        f"{int(labelled_count)} simulated "
                        "ground-truth abnormal readings "
                        "exist in the selected dataset."
                    ),
            }
        )


    if not recommendations:

        recommendations.append(
            {
                "level":
                    "success",

                "title":
                    "Consumption within normal range",

                "message":
                    (
                        "No significant consumption issue "
                        "was identified for the current "
                        "selection."
                    ),
            }
        )


    return recommendations