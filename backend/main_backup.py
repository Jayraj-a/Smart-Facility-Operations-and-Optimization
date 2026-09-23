import os
from pathlib import Path

import pandas as pd

from fastapi import (
    FastAPI,
    Request,
    Form,
    HTTPException,
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
)

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from starlette.middleware.sessions import SessionMiddleware


# ============================================================
# AUTHENTICATION
# ============================================================

from backend.auth import (
    initialise_users_database,
    authenticate_user,
)


# ============================================================
# ENERGY ANALYTICS
# ============================================================

from analytics.energy_analytics import (
    calculate_summary,
    building_comparison,
)


# ============================================================
# ENERGY AGENT
# ============================================================

from agents.energy_agent import (
    generate_recommendations,
)


# ============================================================
# UNUSUAL USAGE DETECTION
# ============================================================

from analytics.anomaly_detection import (
    get_model_metrics,
)


# ============================================================
# ENERGY FORECAST
# ============================================================

from analytics.energy_forecast import (
    forecast_energy,
)


# ============================================================
# ENERGY SERVICE
# ============================================================

from backend.energy_service import (
    analyse_latest_reading,
    analyse_and_store_latest,
    synchronise_historical_data,
)


# ============================================================
# MONITORING DATABASE
# ============================================================

from backend.monitoring_db import (
    initialise_monitoring_database,
    get_alerts,
    update_alert_status,
    get_historical_readings,
    get_daily_summaries,

    # Milestone 2
    get_assets,
    get_asset_readings,
    get_maintenance_predictions,
)


# ============================================================
# MILESTONE 2 - MAINTENANCE SERVICE
# ============================================================

from backend.maintenance_service import (
    synchronise_maintenance_data,
    get_maintenance_summary,
    get_asset_health,
    get_maintenance_building_comparison,
    get_current_maintenance_analysis,
    get_current_maintenance_schedule,
    get_saved_maintenance_alerts,
    set_maintenance_alert_status,
    get_saved_work_orders,
    set_work_order_status,
    get_maintenance_model_metrics,
    get_maintenance_database_status,
    run_maintenance_agent,
    get_maintenance_dataframe,
)


# ============================================================
# MILESTONE 3 - OCCUPANCY SERVICE
# ============================================================

from backend.occupancy_service import (
    sync_occupancy_data,
    sync_occupancy_alerts,
    get_occupancy_dashboard,
    get_occupancy_agent_result,
    get_occupancy_summary,
    get_current_space_occupancy,
    get_space_utilization,
    get_building_occupancy,
    get_occupancy_hourly_pattern,
    get_occupancy_peak_hours,
    get_occupancy_heatmap_data,
    get_recent_overcrowding_events,
    get_occupancy_underused_spaces,
    get_occupancy_insights,
    get_database_occupancy_records,
    get_database_occupancy_alerts,
    change_occupancy_alert_status,
)


# ============================================================
# MILESTONE 3 - SECURITY SERVICE
# ============================================================

from backend.security_service import (
    sync_security_data,
    sync_security_agent_alerts,
    get_security_dashboard,
    get_security_agent_result,
    get_security_summary,
    get_recent_security_events,
    get_recent_unauthorized_events,
    get_recent_after_hours_events,
    get_recent_cctv_events,
    get_recent_security_alert_events,
    get_security_access_points,
    get_security_buildings,
    get_security_hourly_pattern,
    get_security_visitor_movement,
    get_security_insights,
    get_database_security_events,
    get_database_security_alerts,
    change_security_alert_status,
)


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parent.parent


DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "milestone1_energy_dataset.csv"
)


MAINTENANCE_DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "milestone2_asset_dataset.csv"
)


TEMPLATE_DIR = (
    PROJECT_ROOT
    / "frontend"
    / "templates"
)


STATIC_DIR = (
    PROJECT_ROOT
    / "frontend"
    / "static"
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="FacilityOps AI",
    description=(
        "Agentic Facility Operations, Energy, Maintenance, "
        "Occupancy and Security Intelligence Platform"
    ),
    version="3.0.0",
)


# ============================================================
# SESSION
# ============================================================

SESSION_SECRET = os.getenv(
    "SESSION_SECRET",
    "facilityops-development-secret-key",
)


app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    https_only=False,
    same_site="lax",
)


# ============================================================
# STATIC FILES
# ============================================================

app.mount(
    "/static",
    StaticFiles(
        directory=str(
            STATIC_DIR
        )
    ),
    name="static",
)


# ============================================================
# HTML TEMPLATES
# ============================================================

templates = Jinja2Templates(
    directory=str(
        TEMPLATE_DIR
    )
)


# ============================================================
# ENERGY DATA LOADING
# ============================================================

def load_data():

    if not DATA_FILE.exists():

        raise HTTPException(
            status_code=500,
            detail=(
                "Energy dataset could not be found."
            ),
        )

    df = pd.read_csv(
        DATA_FILE
    )

    if "timestamp" in df.columns:

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce",
        )

    if "is_anomaly" in df.columns:

        df["is_anomaly"] = (
            df["is_anomaly"]
            .astype(str)
            .str.lower()
            .isin(
                [
                    "true",
                    "1",
                    "yes",
                ]
            )
        )

    return df


# ============================================================
# AUTH HELPER
# ============================================================

def require_user(
    request: Request,
):

    user = request.session.get(
        "user"
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )

    return user


# ============================================================
# FILTER HELPER
# ============================================================

def apply_filters(
    df,
    building="",
    block="",
):

    filtered = df.copy()

    if building:

        filtered = filtered[
            filtered[
                "building_name"
            ] == building
        ]

    if block:

        filtered = filtered[
            filtered[
                "block_name"
            ] == block
        ]

    return filtered


# ============================================================
# DATAFRAME -> JSON
# ============================================================

def dataframe_records(
    df,
):

    working = df.copy()

    if "timestamp" in working.columns:

        working["timestamp"] = (
            working["timestamp"]
            .astype(str)
        )

    return working.to_dict(
        orient="records"
    )


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
def startup_event():

    initialise_users_database()

    initialise_monitoring_database()

    # ========================================================
    # MILESTONE 1
    # ========================================================

    df = load_data()

    try:

        energy_sync = (
            synchronise_historical_data(
                df
            )
        )

    except Exception as error:

        print(
            "Historical energy data synchronisation warning:",
            error
        )

        energy_sync = {
            "inserted_readings": 0,
            "daily_summaries": 0,
        }

    energy_metrics = (
        get_model_metrics()
    )

    # ========================================================
    # MILESTONE 2
    # ========================================================

    try:

        maintenance_sync = (
            synchronise_maintenance_data()
        )

    except Exception as error:

        print(
            "Maintenance data synchronisation warning:",
            error
        )

        maintenance_sync = {
            "dataset_rows": 0,
            "assets_synced": 0,
            "asset_readings_newly_stored": 0,
            "assets_analysed": 0,
            "predictions_saved": 0,
            "alerts_newly_stored": 0,
            "work_orders_newly_stored": 0,
            "database_counts": {},
        }

    # ========================================================
    # MILESTONE 3
    # ========================================================

    try:

        occupancy_sync = sync_occupancy_data()

    except Exception as error:

        print(
            "Occupancy data synchronisation warning:",
            error
        )

        occupancy_sync = {
            "dataset_rows": 0,
            "inserted_rows": 0,
            "database_rows": 0,
        }

    try:

        security_sync = sync_security_data()

    except Exception as error:

        print(
            "Security data synchronisation warning:",
            error
        )

        security_sync = {
            "dataset_rows": 0,
            "inserted_rows": 0,
            "database_rows": 0,
        }

    maintenance_metrics = (
        get_maintenance_model_metrics()
    )

    print()

    print(
        "FacilityOps AI backend started successfully."
    )

    print()

    print(
        "MILESTONE 1 - ENERGY INTELLIGENCE"
    )

    print(
        "---------------------------------"
    )

    print(
        f"Energy dataset: {DATA_FILE}"
    )

    if energy_metrics:

        accuracy = (
            float(
                energy_metrics.get(
                    "accuracy",
                    0,
                )
            )
            * 100
        )

        print(
            "Unusual Usage Detection Model: READY"
        )

        print(
            f"Issue Detection Accuracy: "
            f"{accuracy:.2f}%"
        )

    else:

        print(
            "Unusual Usage Detection Model: "
            "NOT TRAINED"
        )

    print(
        "Historical readings newly stored:",
        energy_sync.get(
            "inserted_readings",
            0
        )
    )

    print(
        "Daily summaries available:",
        energy_sync.get(
            "daily_summaries",
            0
        )
    )

    print()

    print(
        "MILESTONE 2 - PREDICTIVE MAINTENANCE"
    )

    print(
        "------------------------------------"
    )

    print(
        f"Asset dataset: {MAINTENANCE_DATA_FILE}"
    )

    print(
        "Maintenance Prediction Model:",
        (
            "READY"
            if maintenance_metrics.get(
                "model_ready",
                False
            )
            else "NOT TRAINED"
        ),
    )

    if maintenance_metrics.get(
        "model_ready",
        False
    ):

        print(
            "Maintenance Prediction Accuracy:",
            f"{float(maintenance_metrics.get('accuracy', 0)) * 100:.2f}%"
        )

        print(
            "Maintenance Prediction Recall:",
            f"{float(maintenance_metrics.get('recall', 0)) * 100:.2f}%"
        )

        print(
            "Maintenance Prediction F1:",
            f"{float(maintenance_metrics.get('f1_score', 0)) * 100:.2f}%"
        )

    print(
        "Assets synced:",
        maintenance_sync.get(
            "assets_synced",
            0
        )
    )

    print(
        "Asset readings newly stored:",
        maintenance_sync.get(
            "asset_readings_newly_stored",
            0
        )
    )

    print(
        "Assets analysed:",
        maintenance_sync.get(
            "assets_analysed",
            0
        )
    )

    print(
        "Maintenance predictions saved:",
        maintenance_sync.get(
            "predictions_saved",
            0
        )
    )

    print(
        "Maintenance alerts newly stored:",
        maintenance_sync.get(
            "alerts_newly_stored",
            0
        )
    )

    print(
        "Work orders newly stored:",
        maintenance_sync.get(
            "work_orders_newly_stored",
            0
        )
    )

    print()

    print(
        "MILESTONE 3 - OCCUPANCY & SECURITY INTELLIGENCE"
    )

    print(
        "-----------------------------------------------"
    )

    print(
        "Occupancy records available:",
        occupancy_sync.get(
            "database_rows",
            0
        )
    )

    print(
        "Security events available:",
        security_sync.get(
            "database_rows",
            0
        )
    )

    print()


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home(
    request: Request,
):

    if request.session.get(
        "user"
    ):

        return RedirectResponse(
            url="/dashboard",
            status_code=302,
        )

    return RedirectResponse(
        url="/login",
        status_code=302,
    )


# ============================================================
# LOGIN PAGE
# ============================================================

@app.get(
    "/login",
    response_class=HTMLResponse,
)
def login_page(
    request: Request,
):

    if request.session.get(
        "user"
    ):

        return RedirectResponse(
            url="/dashboard",
            status_code=302,
        )

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "error": None,
        },
    )


# ============================================================
# LOGIN
# ============================================================

@app.post(
    "/login",
    response_class=HTMLResponse,
)
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):

    user = authenticate_user(
        username,
        password,
    )

    if user is None:

        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error":
                    "Invalid username or password.",
            },
            status_code=401,
        )

    if not isinstance(
        user,
        dict
    ):

        try:

            user = dict(
                user
            )

        except Exception:

            user = {
                "username":
                    username,

                "full_name":
                    username,

                "role":
                    "User",
            }

    request.session[
        "user"
    ] = user

    return RedirectResponse(
        url="/dashboard",
        status_code=303,
    )


# ============================================================
# LOGOUT
# ============================================================

@app.get("/logout")
def logout(
    request: Request,
):

    request.session.clear()

    return RedirectResponse(
        url="/login",
        status_code=302,
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.get(
    "/dashboard",
    response_class=HTMLResponse,
)
def dashboard(
    request: Request,
):

    user = request.session.get(
        "user"
    )

    if not user:

        return RedirectResponse(
            url="/login",
            status_code=302,
        )

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "user": user,
        },
    )


# ============================================================
# MILESTONE 1
# FACILITY API
# ============================================================

@app.get("/api/facility")
def facility_information(
    request: Request,
):

    require_user(
        request
    )

    df = load_data()

    if df.empty:

        return {
            "facility_name":
                "Smart Campus",

            "buildings":
                [],
        }

    facility_name = (
        str(
            df[
                "facility_name"
            ].iloc[0]
        )
        if "facility_name"
        in df.columns
        else "Smart Campus"
    )

    buildings = []

    for building in sorted(
        df[
            "building_name"
        ]
        .dropna()
        .unique()
        .tolist()
    ):

        building_df = df[
            df[
                "building_name"
            ] == building
        ]

        blocks = sorted(
            building_df[
                "block_name"
            ]
            .dropna()
            .unique()
            .tolist()
        )

        buildings.append(
            {
                "name":
                    str(building),

                "blocks":
                    [
                        str(block)
                        for block in blocks
                    ],
            }
        )

    return {
        "facility_name":
            facility_name,

        "buildings":
            buildings,
    }


# ============================================================
# MILESTONE 1
# SUMMARY
# ============================================================

@app.get("/api/summary")
def summary(
    request: Request,
    building: str = "",
    block: str = "",
):

    require_user(
        request
    )

    df = load_data()

    filtered_df = apply_filters(
        df,
        building,
        block,
    )

    return calculate_summary(
        filtered_df
    )


# ============================================================
# MILESTONE 1
# READINGS
# ============================================================

@app.get("/api/readings")
def readings(
    request: Request,
    building: str = "",
    block: str = "",
    limit: int = 300,
):

    require_user(
        request
    )

    limit = max(
        1,
        min(
            limit,
            2000
        )
    )

    df = load_data()

    filtered_df = apply_filters(
        df,
        building,
        block,
    )

    filtered_df = (
        filtered_df
        .sort_values(
            "timestamp"
        )
        .tail(
            limit
        )
        .copy()
    )

    return dataframe_records(
        filtered_df
    )


# ============================================================
# MILESTONE 1
# BUILDING COMPARISON
# ============================================================

@app.get(
    "/api/building-comparison"
)
def building_comparison_api(
    request: Request,
):

    require_user(
        request
    )

    df = load_data()

    result = building_comparison(
        df
    )

    if isinstance(
        result,
        pd.DataFrame
    ):

        return result.to_dict(
            orient="records"
        )

    return result


# ============================================================
# MILESTONE 1
# LABELLED UNUSUAL READINGS
# ============================================================

@app.get("/api/anomalies")
def labelled_issues(
    request: Request,
    building: str = "",
    block: str = "",
    limit: int = 50,
):

    require_user(
        request
    )

    df = load_data()

    filtered_df = apply_filters(
        df,
        building,
        block,
    )

    if (
        "is_anomaly"
        not in filtered_df.columns
    ):

        return []

    issues = filtered_df[
        filtered_df[
            "is_anomaly"
        ] == True
    ].copy()

    issues = (
        issues
        .sort_values(
            "timestamp",
            ascending=False,
        )
        .head(
            max(
                1,
                min(
                    limit,
                    200
                )
            )
        )
    )

    issues[
        "timestamp"
    ] = issues[
        "timestamp"
    ].astype(str)

    return issues.to_dict(
        orient="records"
    )


# ============================================================
# MILESTONE 1
# RECOMMENDATIONS
# ============================================================

@app.get("/api/recommendations")
def consumption_analysis(
    request: Request,
    building: str = "",
    block: str = "",
):

    require_user(
        request
    )

    df = load_data()

    filtered_df = apply_filters(
        df,
        building,
        block,
    )

    return generate_recommendations(
        filtered_df
    )


# ============================================================
# MILESTONE 1
# ENERGY AGENT STATUS
# ============================================================

@app.get("/api/agent/status")
def agent_status(
    request: Request,
):

    require_user(
        request
    )

    metrics = get_model_metrics()

    model_status = (
        "READY"
        if metrics
        else "NOT_TRAINED"
    )

    response = {
        "energy_monitoring_agent":
            "ACTIVE",

        "unusual_usage_detection":
            model_status,

        "consumption_analysis":
            "ACTIVE",

        "energy_forecasting":
            "ACTIVE",

        "issue_detection_metrics":
            metrics,
    }

    if metrics:

        response[
            "issue_detection_accuracy_percent"
        ] = round(
            float(
                metrics.get(
                    "accuracy",
                    0,
                )
            )
            * 100,
            2,
        )

    return response


# ============================================================
# MILESTONE 1
# ANALYSE ENERGY
# ============================================================

@app.get("/api/agent/analyse")
def analyse_energy(
    request: Request,
    building: str = "",
    block: str = "",
):

    require_user(
        request
    )

    df = load_data()

    filtered_df = apply_filters(
        df,
        building,
        block,
    )

    if filtered_df.empty:

        raise HTTPException(
            status_code=404,
            detail=(
                "No energy data was found "
                "for the selected area."
            ),
        )

    return analyse_latest_reading(
        filtered_df
    )


# ============================================================
# MILESTONE 1
# RUN ENERGY AGENT
# ============================================================

@app.post("/api/agent/run")
def run_energy_agent(
    request: Request,
    building: str = "",
    block: str = "",
):

    require_user(
        request
    )

    df = load_data()

    filtered_df = apply_filters(
        df,
        building,
        block,
    )

    if filtered_df.empty:

        raise HTTPException(
            status_code=404,
            detail=(
                "No energy data was found "
                "for the selected area."
            ),
        )

    return analyse_and_store_latest(
        filtered_df
    )


# ============================================================
# MILESTONE 1
# ISSUE CENTRE
# ============================================================

@app.get("/api/issues")
def issue_centre(
    request: Request,
    limit: int = 50,
    status: str = "",
):

    require_user(
        request
    )

    limit = max(
        1,
        min(
            limit,
            200
        )
    )

    return get_alerts(
        limit=limit,
        status=(
            status.upper()
            if status
            else None
        ),
    )


# ============================================================
# MILESTONE 1
# CONSUMPTION ALERTS
# ============================================================

@app.get(
    "/api/consumption-alerts"
)
def consumption_alerts(
    request: Request,
    limit: int = 50,
    status: str = "",
):

    require_user(
        request
    )

    limit = max(
        1,
        min(
            limit,
            200
        )
    )

    return get_alerts(
        limit=limit,
        status=(
            status.upper()
            if status
            else None
        ),
    )


# ============================================================
# MILESTONE 1
# ALL ALERTS
# ============================================================

@app.get("/api/alerts")
def all_alerts(
    request: Request,
    limit: int = 50,
    status: str = "",
):

    require_user(
        request
    )

    limit = max(
        1,
        min(
            limit,
            200
        )
    )

    return get_alerts(
        limit=limit,
        status=(
            status.upper()
            if status
            else None
        ),
    )


# ============================================================
# MILESTONE 1
# UPDATE ISSUE STATUS
# ============================================================

@app.put(
    "/api/issues/{alert_id}/status"
)
async def change_issue_status(
    alert_id: int,
    request: Request,
):

    require_user(
        request
    )

    body = await request.json()

    status = str(
        body.get(
            "status",
            ""
        )
    ).upper()

    if not status:

        raise HTTPException(
            status_code=400,
            detail="status is required",
        )

    try:

        updated = update_alert_status(
            alert_id,
            status,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(
                error
            ),
        )

    if not updated:

        raise HTTPException(
            status_code=404,
            detail="Issue not found",
        )

    return {
        "success": True,
        "alert_id": alert_id,
        "status": status,
    }


# ============================================================
# MILESTONE 1
# ENERGY FORECAST
# ============================================================

@app.get("/api/forecast")
def energy_forecast_api(
    request: Request,
    building: str = "",
    block: str = "",
    hours: int = 24,
):

    require_user(
        request
    )

    hours = max(
        1,
        min(
            hours,
            168
        )
    )

    df = load_data()

    filtered_df = apply_filters(
        df,
        building,
        block,
    )

    if filtered_df.empty:

        raise HTTPException(
            status_code=404,
            detail=(
                "No data was found for "
                "energy forecasting."
            ),
        )

    return forecast_energy(
        filtered_df,
        hours=hours,
    )


# ============================================================
# MILESTONE 1
# MODEL METRICS
# ============================================================

@app.get(
    "/api/usage-detection/metrics"
)
def usage_detection_metrics(
    request: Request,
):

    require_user(
        request
    )

    metrics = get_model_metrics()

    if metrics is None:

        return {
            "status":
                "NOT_TRAINED",

            "message":
                (
                    "The Unusual Usage Detection "
                    "model has not been trained."
                ),
        }

    return {
        "status":
            "READY",

        "model":
            "Unusual Usage Detection",

        "issue_detection_accuracy":
            round(
                float(
                    metrics.get(
                        "accuracy",
                        0,
                    )
                )
                * 100,
                2,
            ),

        "precision":
            round(
                float(
                    metrics.get(
                        "precision",
                        0,
                    )
                )
                * 100,
                2,
            ),

        "recall":
            round(
                float(
                    metrics.get(
                        "recall",
                        0,
                    )
                )
                * 100,
                2,
            ),

        "f1_score":
            round(
                float(
                    metrics.get(
                        "f1_score",
                        0,
                    )
                )
                * 100,
                2,
            ),

        "training_rows":
            metrics.get(
                "training_rows",
                0
            ),

        "testing_rows":
            metrics.get(
                "testing_rows",
                0
            ),

        "features":
            metrics.get(
                "features",
                []
            ),

        "evaluation_note":
            (
                "Measured on held-out "
                "synthetic test data."
            ),
    }


# ============================================================
# MILESTONE 1
# DAILY REPORTS
# ============================================================

@app.get("/api/daily-reports")
def daily_reports(
    request: Request,
    building: str = "",
    block: str = "",
    limit: int = 100,
):

    require_user(
        request
    )

    limit = max(
        1,
        min(
            limit,
            500
        )
    )

    return get_daily_summaries(
        building=(
            building
            if building
            else None
        ),
        block=(
            block
            if block
            else None
        ),
        limit=limit,
    )


# ============================================================
# MILESTONE 1
# HISTORICAL DATA
# ============================================================

@app.get("/api/historical-data")
def historical_data(
    request: Request,
    building: str = "",
    block: str = "",
    limit: int = 500,
):

    require_user(
        request
    )

    limit = max(
        1,
        min(
            limit,
            2000
        )
    )

    return get_historical_readings(
        building=(
            building
            if building
            else None
        ),
        block=(
            block
            if block
            else None
        ),
        limit=limit,
    )


# ============================================================
# MILESTONE 2
# MAINTENANCE SUMMARY
# ============================================================

@app.get(
    "/api/maintenance/summary"
)
def maintenance_summary_api(
    request: Request,
):

    require_user(
        request
    )

    return get_maintenance_summary()


# ============================================================
# MILESTONE 2
# ASSET MASTER
# ============================================================

@app.get(
    "/api/maintenance/assets"
)
def maintenance_assets_api(
    request: Request,
    building: str = "",
    asset_type: str = "",
):

    require_user(
        request
    )

    return get_assets(
        building=(
            building
            if building
            else None
        ),
        asset_type=(
            asset_type
            if asset_type
            else None
        ),
    )


# ============================================================
# MILESTONE 2
# ASSET SENSOR READINGS
# ============================================================

@app.get(
    "/api/maintenance/readings"
)
def maintenance_readings_api(
    request: Request,
    asset_id: str = "",
    building: str = "",
    limit: int = 500,
):

    require_user(
        request
    )

    limit = max(
        1,
        min(
            limit,
            5000
        )
    )

    return get_asset_readings(
        asset_id=(
            asset_id
            if asset_id
            else None
        ),
        building=(
            building
            if building
            else None
        ),
        limit=limit,
    )


# ============================================================
# MILESTONE 2
# EQUIPMENT HEALTH
# ============================================================

@app.get(
    "/api/maintenance/health"
)
def maintenance_health_api(
    request: Request,
):

    require_user(
        request
    )

    return get_asset_health()


# ============================================================
# MILESTONE 2
# BUILDING HEALTH COMPARISON
# ============================================================

@app.get(
    "/api/maintenance/building-comparison"
)
def maintenance_building_comparison_api(
    request: Request,
):

    require_user(
        request
    )

    return (
        get_maintenance_building_comparison()
    )


# ============================================================
# MILESTONE 2
# SAVED PREDICTIONS
# ============================================================

@app.get(
    "/api/maintenance/predictions"
)
def maintenance_predictions_api(
    request: Request,
    asset_id: str = "",
    limit: int = 100,
):

    require_user(
        request
    )

    limit = max(
        1,
        min(
            limit,
            1000
        )
    )

    return get_maintenance_predictions(
        asset_id=(
            asset_id
            if asset_id
            else None
        ),
        limit=limit,
    )


# ============================================================
# MILESTONE 2
# CURRENT AGENT ANALYSIS
# ============================================================

@app.get(
    "/api/maintenance/analysis"
)
def maintenance_analysis_api(
    request: Request,
):

    require_user(
        request
    )

    return (
        get_current_maintenance_analysis()
    )


# ============================================================
# MILESTONE 2
# MAINTENANCE SCHEDULE
# ============================================================

@app.get(
    "/api/maintenance/schedule"
)
def maintenance_schedule_api(
    request: Request,
):

    require_user(
        request
    )

    return (
        get_current_maintenance_schedule()
    )


# ============================================================
# MILESTONE 2
# MAINTENANCE ALERTS
# ============================================================

@app.get(
    "/api/maintenance/alerts"
)
def maintenance_alerts_api(
    request: Request,
    limit: int = 50,
    status: str = "",
):

    require_user(
        request
    )

    limit = max(
        1,
        min(
            limit,
            500
        )
    )

    return (
        get_saved_maintenance_alerts(
            limit=limit,
            status=(
                status.upper()
                if status
                else None
            ),
        )
    )


# ============================================================
# MILESTONE 2
# UPDATE MAINTENANCE ALERT
# ============================================================

@app.put(
    "/api/maintenance/alerts/{alert_id}/status"
)
async def maintenance_alert_status_api(
    alert_id: int,
    request: Request,
):

    require_user(
        request
    )

    body = await request.json()

    status = str(
        body.get(
            "status",
            ""
        )
    ).upper()

    if not status:

        raise HTTPException(
            status_code=400,
            detail="status is required",
        )

    try:

        updated = (
            set_maintenance_alert_status(
                alert_id,
                status,
            )
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(
                error
            ),
        )

    if not updated:

        raise HTTPException(
            status_code=404,
            detail=(
                "Maintenance alert not found"
            ),
        )

    return {
        "success": True,
        "alert_id": alert_id,
        "status": status,
    }


# ============================================================
# MILESTONE 2
# WORK ORDERS
# ============================================================

@app.get(
    "/api/maintenance/work-orders"
)
def maintenance_work_orders_api(
    request: Request,
    limit: int = 50,
    status: str = "",
):

    require_user(
        request
    )

    limit = max(
        1,
        min(
            limit,
            500
        )
    )

    return get_saved_work_orders(
        limit=limit,
        status=(
            status.upper()
            if status
            else None
        ),
    )


# ============================================================
# MILESTONE 2
# UPDATE WORK ORDER
# ============================================================

@app.put(
    "/api/maintenance/work-orders/{work_order_id}/status"
)
async def maintenance_work_order_status_api(
    work_order_id: int,
    request: Request,
):

    require_user(
        request
    )

    body = await request.json()

    status = str(
        body.get(
            "status",
            ""
        )
    ).upper()

    if not status:

        raise HTTPException(
            status_code=400,
            detail="status is required",
        )

    try:

        updated = (
            set_work_order_status(
                work_order_id,
                status,
            )
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(
                error
            ),
        )

    if not updated:

        raise HTTPException(
            status_code=404,
            detail="Work order not found",
        )

    return {
        "success": True,
        "work_order_id": work_order_id,
        "status": status,
    }


# ============================================================
# MILESTONE 2
# RUN MAINTENANCE AGENT
# ============================================================

@app.post(
    "/api/maintenance/agent/run"
)
def maintenance_agent_run_api(
    request: Request,
):

    require_user(
        request
    )

    dataframe = (
        get_maintenance_dataframe()
    )

    return run_maintenance_agent(
        dataframe
    )


# ============================================================
# MILESTONE 2
# MODEL METRICS
# ============================================================

@app.get(
    "/api/maintenance/model-metrics"
)
def maintenance_model_metrics_api(
    request: Request,
):

    require_user(
        request
    )

    metrics = (
        get_maintenance_model_metrics()
    )

    if not metrics.get(
        "model_ready",
        False
    ):

        return {
            "status":
                "NOT_TRAINED",

            **metrics,
        }

    return {
        "status":
            "READY",

        "model":
            "Predictive Maintenance",

        "accuracy_percent":
            round(
                float(
                    metrics.get(
                        "accuracy",
                        0
                    )
                )
                * 100,
                2,
            ),

        "precision_percent":
            round(
                float(
                    metrics.get(
                        "precision",
                        0
                    )
                )
                * 100,
                2,
            ),

        "recall_percent":
            round(
                float(
                    metrics.get(
                        "recall",
                        0
                    )
                )
                * 100,
                2,
            ),

        "f1_score_percent":
            round(
                float(
                    metrics.get(
                        "f1_score",
                        0
                    )
                )
                * 100,
                2,
            ),

        "records":
            metrics.get(
                "records",
                0
            ),

        "training_records":
            metrics.get(
                "training_records",
                0
            ),

        "testing_records":
            metrics.get(
                "testing_records",
                0
            ),

        "normal_records":
            metrics.get(
                "normal_records",
                0
            ),

        "maintenance_required_records":
            metrics.get(
                "maintenance_required_records",
                0
            ),

        "confusion_matrix":
            metrics.get(
                "confusion_matrix",
                []
            ),

        "feature_importance":
            metrics.get(
                "feature_importance",
                {}
            ),

        "evaluation_note":
            metrics.get(
                "evaluation_note",
                (
                    "Measured on held-out "
                    "simulated asset data."
                )
            ),
    }


# ============================================================
# MILESTONE 2
# DATABASE STATUS
# ============================================================

@app.get(
    "/api/maintenance/database-status"
)
def maintenance_database_status_api(
    request: Request,
):

    require_user(
        request
    )

    return (
        get_maintenance_database_status()
    )


# ============================================================
# MILESTONE 3
# OCCUPANCY SUMMARY
# ============================================================

@app.get("/api/occupancy/summary")
def occupancy_summary_api(
    request: Request,
):
    require_user(request)
    return get_occupancy_summary()


@app.get("/api/occupancy/dashboard")
def occupancy_dashboard_api(
    request: Request,
):
    require_user(request)
    return get_occupancy_dashboard()


@app.get("/api/occupancy/spaces")
def occupancy_spaces_api(
    request: Request,
):
    require_user(request)
    return get_current_space_occupancy()


@app.get("/api/occupancy/utilization")
def occupancy_utilization_api(
    request: Request,
):
    require_user(request)
    return get_space_utilization()


@app.get("/api/occupancy/buildings")
def occupancy_buildings_api(
    request: Request,
):
    require_user(request)
    return get_building_occupancy()


@app.get("/api/occupancy/hourly-pattern")
def occupancy_hourly_pattern_api(
    request: Request,
):
    require_user(request)
    return get_occupancy_hourly_pattern()


@app.get("/api/occupancy/peak-hours")
def occupancy_peak_hours_api(
    request: Request,
):
    require_user(request)
    return get_occupancy_peak_hours()


@app.get("/api/occupancy/heatmap")
def occupancy_heatmap_api(
    request: Request,
):
    require_user(request)
    return get_occupancy_heatmap_data()


@app.get("/api/occupancy/overcrowding")
def occupancy_overcrowding_api(
    request: Request,
    limit: int = 20,
):
    require_user(request)
    limit = max(1, min(limit, 200))
    return get_recent_overcrowding_events(limit=limit)


@app.get("/api/occupancy/underused")
def occupancy_underused_api(
    request: Request,
):
    require_user(request)
    return get_occupancy_underused_spaces()


@app.get("/api/occupancy/insights")
def occupancy_insights_api(
    request: Request,
):
    require_user(request)
    return get_occupancy_insights()


@app.get("/api/occupancy/agent")
def occupancy_agent_api(
    request: Request,
):
    require_user(request)
    return get_occupancy_agent_result()


@app.post("/api/occupancy/sync")
def occupancy_sync_api(
    request: Request,
):
    require_user(request)
    return sync_occupancy_data()


@app.post("/api/occupancy/alerts/sync")
def occupancy_alert_sync_api(
    request: Request,
):
    require_user(request)
    return sync_occupancy_alerts()


@app.get("/api/occupancy/records")
def occupancy_records_api(
    request: Request,
    space_id: str = "",
    building: str = "",
    block: str = "",
    limit: int = 500,
):
    require_user(request)
    limit = max(1, min(limit, 5000))
    return get_database_occupancy_records(
        space_id=space_id if space_id else None,
        building=building if building else None,
        block=block if block else None,
        limit=limit,
    )


@app.get("/api/occupancy/alerts")
def occupancy_alerts_api(
    request: Request,
    limit: int = 50,
    status: str = "",
):
    require_user(request)
    limit = max(1, min(limit, 500))
    return get_database_occupancy_alerts(
        limit=limit,
        status=status.upper() if status else None,
    )


@app.put("/api/occupancy/alerts/{alert_id}/status")
async def occupancy_alert_status_api(
    alert_id: int,
    request: Request,
):
    require_user(request)
    body = await request.json()
    status = str(body.get("status", "")).upper()

    if not status:
        raise HTTPException(
            status_code=400,
            detail="status is required",
        )

    try:
        updated = change_occupancy_alert_status(
            alert_id,
            status,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Occupancy alert not found",
        )

    return {
        "success": True,
        "alert_id": alert_id,
        "status": status,
    }


# ============================================================
# MILESTONE 3
# SECURITY INTELLIGENCE
# ============================================================

@app.get("/api/security/summary")
def security_summary_api(
    request: Request,
):
    require_user(request)
    return get_security_summary()


@app.get("/api/security/dashboard")
def security_dashboard_api(
    request: Request,
):
    require_user(request)
    return get_security_dashboard()


@app.get("/api/security/events")
def security_events_api(
    request: Request,
    limit: int = 20,
):
    require_user(request)
    limit = max(1, min(limit, 500))
    return get_recent_security_events(limit=limit)


@app.get("/api/security/unauthorized")
def security_unauthorized_api(
    request: Request,
    limit: int = 20,
):
    require_user(request)
    limit = max(1, min(limit, 500))
    return get_recent_unauthorized_events(limit=limit)


@app.get("/api/security/after-hours")
def security_after_hours_api(
    request: Request,
    limit: int = 20,
):
    require_user(request)
    limit = max(1, min(limit, 500))
    return get_recent_after_hours_events(limit=limit)


@app.get("/api/security/cctv")
def security_cctv_api(
    request: Request,
    limit: int = 20,
):
    require_user(request)
    limit = max(1, min(limit, 500))
    return get_recent_cctv_events(limit=limit)


@app.get("/api/security/alert-events")
def security_alert_events_api(
    request: Request,
    limit: int = 20,
):
    require_user(request)
    limit = max(1, min(limit, 500))
    return get_recent_security_alert_events(limit=limit)


@app.get("/api/security/access-points")
def security_access_points_api(
    request: Request,
):
    require_user(request)
    return get_security_access_points()


@app.get("/api/security/buildings")
def security_buildings_api(
    request: Request,
):
    require_user(request)
    return get_security_buildings()


@app.get("/api/security/hourly-pattern")
def security_hourly_pattern_api(
    request: Request,
):
    require_user(request)
    return get_security_hourly_pattern()


@app.get("/api/security/visitors")
def security_visitors_api(
    request: Request,
):
    require_user(request)
    return get_security_visitor_movement()


@app.get("/api/security/insights")
def security_insights_api(
    request: Request,
):
    require_user(request)
    return get_security_insights()


@app.get("/api/security/agent")
def security_agent_api(
    request: Request,
):
    require_user(request)
    return get_security_agent_result()


@app.post("/api/security/sync")
def security_sync_api(
    request: Request,
):
    require_user(request)
    return sync_security_data()


@app.post("/api/security/alerts/sync")
def security_alert_sync_api(
    request: Request,
):
    require_user(request)
    return sync_security_agent_alerts()


@app.get("/api/security/database-events")
def security_database_events_api(
    request: Request,
    event_id: str = "",
    building: str = "",
    access_point_id: str = "",
    severity: str = "",
    limit: int = 500,
):
    require_user(request)
    limit = max(1, min(limit, 5000))
    return get_database_security_events(
        event_id=event_id if event_id else None,
        building=building if building else None,
        access_point_id=(
            access_point_id if access_point_id else None
        ),
        severity=severity.upper() if severity else None,
        limit=limit,
    )


@app.get("/api/security/alerts")
def security_alerts_api(
    request: Request,
    limit: int = 50,
    status: str = "",
):
    require_user(request)
    limit = max(1, min(limit, 500))
    return get_database_security_alerts(
        limit=limit,
        status=status.upper() if status else None,
    )


@app.put("/api/security/alerts/{alert_id}/status")
async def security_alert_status_api(
    alert_id: int,
    request: Request,
):
    require_user(request)
    body = await request.json()
    status = str(body.get("status", "")).upper()

    if not status:
        raise HTTPException(
            status_code=400,
            detail="status is required",
        )

    try:
        updated = change_security_alert_status(
            alert_id,
            status,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Security alert not found",
        )

    return {
        "success": True,
        "alert_id": alert_id,
        "status": status,
    }


# ============================================================
# SYSTEM HEALTH
# ============================================================

@app.get("/health")
def health():

    energy_metrics = (
        get_model_metrics()
    )

    maintenance_metrics = (
        get_maintenance_model_metrics()
    )

    try:

        maintenance_database = (
            get_maintenance_database_status()
        )

        maintenance_database_ready = True

    except Exception:

        maintenance_database = {}

        maintenance_database_ready = False

    return {
        "status":
            "healthy",

        "application":
            "FacilityOps AI",

        "milestones":
            [
                "Energy Intelligence",
                "Predictive Maintenance",
                "Occupancy Intelligence",
                "Security Intelligence",
            ],

        "energy_monitoring_agent":
            "ACTIVE",

        "unusual_usage_detection":
            (
                "READY"
                if energy_metrics
                else "NOT_TRAINED"
            ),

        "maintenance_agent":
            "ACTIVE",

        "occupancy_agent":
            "ACTIVE",

        "security_agent":
            "ACTIVE",

        "maintenance_prediction_model":
            (
                "READY"
                if maintenance_metrics.get(
                    "model_ready",
                    False
                )
                else "NOT_TRAINED"
            ),

        "database":
            "READY",

        "historical_energy_data":
            "READY",

        "daily_reporting":
            "READY",

        "asset_monitoring":
            (
                "READY"
                if maintenance_database_ready
                else "ERROR"
            ),

        "maintenance_database":
            maintenance_database,
    }