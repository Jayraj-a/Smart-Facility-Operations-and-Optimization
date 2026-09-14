import pandas as pd

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
    get_incident_details,
    generate_security_insights,
)


# ============================================================
# FACILITYOPS AI
# MILESTONE 3 - SECURITY AGENT
# ============================================================


class SecurityAgent:
    """
    FacilityOps AI Security Agent.

    Responsibilities:
    - Monitor access-control activity
    - Detect unauthorized access
    - Analyse CCTV-related events
    - Monitor after-hours activity
    - Track visitor movement
    - Prioritize security incidents
    - Generate security alerts
    - Recommend security actions
    - Support incident investigation
    """

    def __init__(self):
        self.name = "FacilityOps Security Agent"

        self.severity_rank = {
            "NORMAL": 0,
            "LOW": 1,
            "MEDIUM": 2,
            "HIGH": 3,
            "CRITICAL": 4,
        }

    # ========================================================
    # HELPERS
    # ========================================================

    @staticmethod
    def safe_int(value, default=0):
        try:
            if pd.isna(value):
                return default
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def safe_float(value, default=0.0):
        try:
            if pd.isna(value):
                return default
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def safe_bool(value):
        if isinstance(value, bool):
            return value

        try:
            return int(value) == 1
        except (TypeError, ValueError):
            return False

    @staticmethod
    def format_timestamp(value):
        if value is None:
            return None

        try:
            return pd.to_datetime(
                value
            ).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        except Exception:
            return str(value)

    # ========================================================
    # CALCULATE EVENT RISK SCORE
    # ========================================================

    def calculate_risk_score(self, record):
        score = 0

        unauthorized = self.safe_bool(
            record.get("unauthorized_attempt")
        )

        after_hours = self.safe_bool(
            record.get("after_hours")
        )

        forced_entry = self.safe_bool(
            record.get("forced_entry")
        )

        tailgating = self.safe_bool(
            record.get("tailgating_detected")
        )

        access_status = str(
            record.get(
                "access_status",
                "",
            )
        ).upper()

        zone_type = str(
            record.get(
                "zone_type",
                "",
            )
        ).upper()

        user_type = str(
            record.get(
                "user_type",
                "",
            )
        ).upper()

        cctv_event = str(
            record.get(
                "cctv_event",
                "NORMAL",
            )
        ).upper()

        if forced_entry:
            score += 50

        if unauthorized:
            score += 35

        if tailgating:
            score += 30

        if after_hours:
            score += 15

        if access_status == "DENIED":
            score += 10

        if zone_type == "RESTRICTED AREA":
            score += 10

        if (
            user_type == "VISITOR"
            and zone_type == "RESTRICTED AREA"
        ):
            score += 15

        if cctv_event == "FORCED_ENTRY":
            score += 20

        elif cctv_event == "TAILGATING":
            score += 15

        elif cctv_event == "SUSPICIOUS_ACCESS":
            score += 15

        elif cctv_event == "AFTER_HOURS_MOVEMENT":
            score += 5

        return min(score, 100)

    # ========================================================
    # RISK LEVEL
    # ========================================================

    @staticmethod
    def determine_risk_level(score):
        if score >= 80:
            return "CRITICAL"

        if score >= 55:
            return "HIGH"

        if score >= 30:
            return "MEDIUM"

        if score > 0:
            return "LOW"

        return "NORMAL"

    # ========================================================
    # EVENT PRIORITY
    # ========================================================

    def determine_priority(
        self,
        record,
        risk_score,
    ):
        if self.safe_bool(
            record.get("forced_entry")
        ):
            return "CRITICAL"

        if (
            self.safe_bool(
                record.get(
                    "unauthorized_attempt"
                )
            )
            and self.safe_bool(
                record.get("after_hours")
            )
        ):
            return "CRITICAL"

        if risk_score >= 80:
            return "CRITICAL"

        if (
            self.safe_bool(
                record.get(
                    "unauthorized_attempt"
                )
            )
            or self.safe_bool(
                record.get(
                    "tailgating_detected"
                )
            )
            or risk_score >= 55
        ):
            return "HIGH"

        if (
            str(
                record.get(
                    "access_status",
                    "",
                )
            ).upper()
            == "DENIED"
        ):
            return "MEDIUM"

        if self.safe_bool(
            record.get("after_hours")
        ):
            return "LOW"

        return "NORMAL"

    # ========================================================
    # RECOMMENDED SECURITY ACTION
    # ========================================================

    def generate_recommended_action(
        self,
        record,
        priority,
    ):
        access_point = record.get(
            "access_point_name",
            "access point",
        )

        if self.safe_bool(
            record.get("forced_entry")
        ):
            return (
                f"Immediately secure {access_point}, "
                f"notify security personnel, review "
                f"access logs, and investigate the "
                f"associated CCTV event."
            )

        if (
            self.safe_bool(
                record.get(
                    "unauthorized_attempt"
                )
            )
            and self.safe_bool(
                record.get("after_hours")
            )
        ):
            return (
                "Immediately verify the person's "
                "identity and authorization. Review "
                "after-hours access logs and CCTV "
                "activity."
            )

        if self.safe_bool(
            record.get(
                "unauthorized_attempt"
            )
        ):
            return (
                "Verify access credentials, review "
                "the attempted entry, and confirm "
                "whether access authorization should "
                "be changed."
            )

        if self.safe_bool(
            record.get(
                "tailgating_detected"
            )
        ):
            return (
                "Review CCTV activity and access logs "
                "for possible tailgating. Verify all "
                "people who entered the controlled "
                "area."
            )

        if (
            self.safe_bool(
                record.get("after_hours")
            )
            and priority
            in {
                "MEDIUM",
                "HIGH",
                "CRITICAL",
            }
        ):
            return (
                "Verify the reason for after-hours "
                "access and review the user's recent "
                "facility movement."
            )

        if (
            str(
                record.get(
                    "access_status",
                    "",
                )
            ).upper()
            == "DENIED"
        ):
            return (
                "Review the denied access event and "
                "verify the user's credentials and "
                "access permissions."
            )

        if self.safe_bool(
            record.get("after_hours")
        ):
            return (
                "Record and monitor the after-hours "
                "access event for unusual activity."
            )

        return (
            "No immediate security action required. "
            "Continue routine access monitoring."
        )

    # ========================================================
    # ANALYSE ONE SECURITY EVENT
    # ========================================================

    def analyse_event(self, record):
        risk_score = (
            self.calculate_risk_score(
                record
            )
        )

        risk_level = (
            self.determine_risk_level(
                risk_score
            )
        )

        priority = self.determine_priority(
            record,
            risk_score,
        )

        recommended_action = (
            self.generate_recommended_action(
                record,
                priority,
            )
        )

        requires_alert = priority in {
            "MEDIUM",
            "HIGH",
            "CRITICAL",
        }

        result = {
            "event_id": record.get(
                "event_id"
            ),
            "timestamp":
                self.format_timestamp(
                    record.get("timestamp")
                ),
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
            "access_point_id": record.get(
                "access_point_id"
            ),
            "access_point_name": record.get(
                "access_point_name"
            ),
            "zone_type": record.get(
                "zone_type"
            ),
            "user_id": record.get(
                "user_id"
            ),
            "user_name": record.get(
                "user_name"
            ),
            "user_type": record.get(
                "user_type"
            ),
            "event_type": record.get(
                "event_type"
            ),
            "access_status": record.get(
                "access_status"
            ),
            "after_hours":
                self.safe_bool(
                    record.get(
                        "after_hours"
                    )
                ),
            "unauthorized_attempt":
                self.safe_bool(
                    record.get(
                        "unauthorized_attempt"
                    )
                ),
            "forced_entry":
                self.safe_bool(
                    record.get(
                        "forced_entry"
                    )
                ),
            "tailgating_detected":
                self.safe_bool(
                    record.get(
                        "tailgating_detected"
                    )
                ),
            "cctv_event": record.get(
                "cctv_event"
            ),
            "original_severity":
                record.get(
                    "severity"
                ),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "priority": priority,
            "requires_alert":
                requires_alert,
            "recommended_action":
                recommended_action,
        }

        return result

    # ========================================================
    # GENERATE ALERT
    # ========================================================

    def generate_alert(self, analysis):
        if not analysis[
            "requires_alert"
        ]:
            return None

        event_id = analysis.get(
            "event_id"
        )

        access_point = analysis.get(
            "access_point_name"
        )

        user_id = analysis.get(
            "user_id"
        )

        priority = analysis.get(
            "priority"
        )

        event_type = analysis.get(
            "event_type"
        )

        return {
            "event_id": event_id,
            "alert_type":
                "SECURITY_INCIDENT",
            "severity": priority,
            "timestamp":
                analysis.get(
                    "timestamp"
                ),
            "building_name":
                analysis.get(
                    "building_name"
                ),
            "access_point_name":
                access_point,
            "user_id": user_id,
            "user_type":
                analysis.get(
                    "user_type"
                ),
            "event_type": event_type,
            "risk_score":
                analysis.get(
                    "risk_score"
                ),
            "message": (
                f"{priority} security event "
                f"detected at {access_point}. "
                f"Event: {event_type}. "
                f"User: {user_id}."
            ),
            "recommended_action":
                analysis.get(
                    "recommended_action"
                ),
        }

    # ========================================================
    # ANALYSE SECURITY EVENTS
    # ========================================================

    def analyse_events(
        self,
        dataframe,
        limit=None,
    ):
        if dataframe.empty:
            return {
                "agent": self.name,
                "events_analysed": 0,
                "events": [],
                "alerts": [],
                "alert_count": 0,
            }

        working = dataframe.copy()

        working = working.sort_values(
            "timestamp",
            ascending=False,
        )

        if limit is not None:
            working = working.head(
                limit
            )

        analyses = []
        alerts = []

        for _, row in working.iterrows():
            analysis = (
                self.analyse_event(
                    row.to_dict()
                )
            )

            analyses.append(
                analysis
            )

            alert = self.generate_alert(
                analysis
            )

            if alert is not None:
                alerts.append(alert)

        alerts.sort(
            key=lambda item: (
                self.severity_rank.get(
                    item["severity"],
                    0,
                ),
                item.get(
                    "risk_score",
                    0,
                ),
            ),
            reverse=True,
        )

        return {
            "agent": self.name,
            "events_analysed":
                len(analyses),
            "events": analyses,
            "alerts": alerts,
            "alert_count":
                len(alerts),
        }

    # ========================================================
    # INCIDENT INVESTIGATION
    # ========================================================

    def investigate_incident(
        self,
        dataframe,
        event_id,
    ):
        incident = get_incident_details(
            dataframe,
            event_id,
        )

        if incident is None:
            return {
                "found": False,
                "event_id": event_id,
                "message":
                    "Security incident not found.",
            }

        analysis = self.analyse_event(
            incident
        )

        return {
            "found": True,
            "event_id": event_id,
            "incident": incident,
            "analysis": analysis,
            "investigation_summary": (
                f"Incident {event_id} at "
                f"{incident['access_point_name']} "
                f"was evaluated as "
                f"{analysis['priority']} priority "
                f"with a risk score of "
                f"{analysis['risk_score']}/100."
            ),
            "recommended_action":
                analysis[
                    "recommended_action"
                ],
        }

    # ========================================================
    # ACCESS POINT RISK ANALYSIS
    # ========================================================

    def analyse_access_points(
        self,
        dataframe,
    ):
        access_points = (
            get_access_point_summary(
                dataframe
            )
        )

        results = []

        for point in access_points:
            total = self.safe_int(
                point.get(
                    "total_events"
                )
            )

            unauthorized = self.safe_int(
                point.get(
                    "unauthorized_attempts"
                )
            )

            alerts = self.safe_int(
                point.get(
                    "security_alerts"
                )
            )

            forced = self.safe_int(
                point.get(
                    "forced_entries"
                )
            )

            tailgating = self.safe_int(
                point.get(
                    "tailgating_events"
                )
            )

            risk_score = (
                unauthorized * 2
                + alerts
                + forced * 5
                + tailgating * 3
            )

            if total > 0:
                normalized_risk = (
                    risk_score
                    / total
                    * 100
                )
            else:
                normalized_risk = 0.0

            normalized_risk = min(
                normalized_risk,
                100.0,
            )

            if (
                forced > 0
                or normalized_risk >= 20
            ):
                risk_level = "HIGH"

            elif (
                unauthorized > 0
                or normalized_risk >= 10
            ):
                risk_level = "MEDIUM"

            else:
                risk_level = "LOW"

            results.append(
                {
                    **point,
                    "risk_score": round(
                        normalized_risk,
                        2,
                    ),
                    "risk_level":
                        risk_level,
                }
            )

        results.sort(
            key=lambda item: item[
                "risk_score"
            ],
            reverse=True,
        )

        return results

    # ========================================================
    # VISITOR SECURITY ANALYSIS
    # ========================================================

    def analyse_visitors(
        self,
        dataframe,
    ):
        visitor_data = dataframe[
            dataframe["user_type"]
            == "VISITOR"
        ].copy()

        if visitor_data.empty:
            return {
                "visitors_tracked": 0,
                "visitor_events": 0,
                "denied_events": 0,
                "unauthorized_attempts": 0,
                "after_hours_events": 0,
                "restricted_area_events": 0,
            }

        restricted = (
            visitor_data[
                "zone_type"
            ]
            == "Restricted Area"
        )

        denied = (
            visitor_data[
                "access_status"
            ]
            == "DENIED"
        )

        return {
            "visitors_tracked": int(
                visitor_data[
                    "user_id"
                ].nunique()
            ),
            "visitor_events": int(
                len(visitor_data)
            ),
            "denied_events": int(
                denied.sum()
            ),
            "unauthorized_attempts": int(
                visitor_data[
                    "unauthorized_attempt"
                ].sum()
            ),
            "after_hours_events": int(
                visitor_data[
                    "after_hours"
                ].sum()
            ),
            "restricted_area_events": int(
                restricted.sum()
            ),
        }

    # ========================================================
    # COMPLETE SECURITY AGENT
    # ========================================================

    def run(self, dataframe):
        summary = (
            calculate_security_summary(
                dataframe
            )
        )

        recent_analysis = (
            self.analyse_events(
                dataframe,
                limit=100,
            )
        )

        access_point_risk = (
            self.analyse_access_points(
                dataframe
            )
        )

        building_comparison = (
            get_building_security_comparison(
                dataframe
            )
        )

        security_insights = (
            generate_security_insights(
                dataframe
            )
        )

        visitor_analysis = (
            self.analyse_visitors(
                dataframe
            )
        )

        return {
            "agent": self.name,
            "summary": summary,

            "recent_events":
                get_recent_access_events(
                    dataframe,
                    limit=100,
                ),

            "recent_analysis":
                recent_analysis[
                    "events"
                ],

            "agent_alerts":
                recent_analysis[
                    "alerts"
                ],

            "agent_alert_count":
                recent_analysis[
                    "alert_count"
                ],

            "security_alerts":
                get_security_alerts(
                    dataframe,
                    limit=100,
                ),

            "unauthorized_access":
                get_unauthorized_access_events(
                    dataframe,
                    limit=100,
                ),

            "after_hours_activity":
                get_after_hours_events(
                    dataframe,
                    limit=100,
                ),

            "cctv_events":
                get_cctv_events(
                    dataframe,
                    limit=100,
                ),

            "visitor_movement":
                get_visitor_movement(
                    dataframe,
                    limit=100,
                ),

            "visitor_analysis":
                visitor_analysis,

            "access_point_risk":
                access_point_risk,

            "building_comparison":
                building_comparison,

            "hourly_pattern":
                get_hourly_security_pattern(
                    dataframe
                ),

            "insights":
                security_insights,
        }


# ============================================================
# GLOBAL SECURITY AGENT
# ============================================================

security_agent = SecurityAgent()


# ============================================================
# COMMAND-LINE TEST
# ============================================================

def main():
    print()
    print("=" * 60)
    print("FACILITYOPS AI - MILESTONE 3")
    print("SECURITY AGENT")
    print("=" * 60)

    dataframe = load_security_data()

    result = security_agent.run(
        dataframe
    )

    print()
    print("Agent:")
    print(result["agent"])

    print()
    print("Security Summary")
    print("-" * 60)

    for key, value in (
        result["summary"].items()
    ):
        print(
            f"{key}: {value}"
        )

    print()
    print("Access Point Risk")
    print("-" * 60)

    for point in result[
        "access_point_risk"
    ]:
        print(
            f"{point['access_point_id']} | "
            f"{point['access_point_name']} | "
            f"Risk: "
            f"{point['risk_score']:.2f} | "
            f"{point['risk_level']} | "
            f"Unauthorized: "
            f"{point['unauthorized_attempts']} | "
            f"Alerts: "
            f"{point['security_alerts']}"
        )

    print()
    print("Visitor Security Analysis")
    print("-" * 60)

    for key, value in result[
        "visitor_analysis"
    ].items():
        print(
            f"{key}: {value}"
        )

    print()
    print("Recent Agent Security Alerts")
    print("-" * 60)

    alerts = result[
        "agent_alerts"
    ]

    if not alerts:
        print(
            "No recent security alerts."
        )

    for alert in alerts[:10]:
        print(
            f"[{alert['severity']}] "
            f"{alert['event_id']} | "
            f"{alert['access_point_name']} | "
            f"Risk: "
            f"{alert['risk_score']}/100 | "
            f"{alert['event_type']}"
        )

    print()
    print(
        "Recent events analysed:",
        len(
            result[
                "recent_analysis"
            ]
        ),
    )

    print(
        "Agent alerts generated:",
        result[
            "agent_alert_count"
        ],
    )

    print()
    print("Security Insights")
    print("-" * 60)

    for insight in result[
        "insights"
    ]:
        print(
            f"[{insight['severity']}] "
            f"{insight['title']} - "
            f"{insight['message']}"
        )

    print()
    print("Incident Investigation Test")
    print("-" * 60)

    critical_events = dataframe[
        dataframe["severity"]
        == "CRITICAL"
    ]

    if not critical_events.empty:
        test_event_id = (
            critical_events
            .sort_values(
                "timestamp",
                ascending=False,
            )
            .iloc[0][
                "event_id"
            ]
        )

        investigation = (
            security_agent
            .investigate_incident(
                dataframe,
                test_event_id,
            )
        )

        print(
            investigation[
                "investigation_summary"
            ]
        )

        print(
            "Recommended Action:",
            investigation[
                "recommended_action"
            ],
        )

    else:
        print(
            "No critical event available "
            "for investigation test."
        )

    print()
    print("=" * 60)
    print(
        "Security Agent completed successfully."
    )
    print("=" * 60)


if __name__ == "__main__":
    main()