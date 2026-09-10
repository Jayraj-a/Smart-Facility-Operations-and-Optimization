import pandas as pd


def filter_energy_data(
    df,
    building=None,
    block=None
):

    filtered = df.copy()

    if building:
        filtered = filtered[
            filtered["building_name"] == building
        ]

    if block:
        filtered = filtered[
            filtered["block_name"] == block
        ]

    return filtered


def calculate_summary(df):

    if df.empty:
        return {}

    return {
        "records": int(len(df)),

        "electricity_total": round(
            float(df["electricity_kwh"].sum()),
            2
        ),

        "electricity_average": round(
            float(df["electricity_kwh"].mean()),
            2
        ),

        "electricity_peak": round(
            float(df["electricity_kwh"].max()),
            2
        ),

        "hvac_average": round(
            float(df["hvac_kwh"].mean()),
            2
        ),

        "lighting_average": round(
            float(df["lighting_kwh"].mean()),
            2
        ),

        "water_average": round(
            float(df["water_liters"].mean()),
            2
        ),

        "temperature_average": round(
            float(df["temperature_c"].mean()),
            2
        ),

        "occupancy_average": round(
            float(df["occupancy"].mean()),
            2
        ),

        "anomalies": int(
            df["is_anomaly"].sum()
        )
    }


def building_comparison(df):

    result = (
        df.groupby("building_name")
        .agg(
            electricity_kwh=(
                "electricity_kwh",
                "mean"
            ),
            hvac_kwh=(
                "hvac_kwh",
                "mean"
            ),
            lighting_kwh=(
                "lighting_kwh",
                "mean"
            ),
            water_liters=(
                "water_liters",
                "mean"
            ),
            occupancy=(
                "occupancy",
                "mean"
            ),
            anomalies=(
                "is_anomaly",
                "sum"
            )
        )
        .round(2)
        .reset_index()
    )

    return result.to_dict(
        orient="records"
    )