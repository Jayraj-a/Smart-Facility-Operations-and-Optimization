import pandas as pd


def forecast_energy(
    df,
    hours=24,
):
    """
    Forecast future electricity consumption using
    a historical hour-of-day baseline.
    """

    if df.empty:
        return {
            "forecast": [],
            "method": "historical_hour_of_day_baseline",
            "forecast_hours": hours,
        }

    working = df.copy()

    # Convert timestamp safely
    working["timestamp"] = pd.to_datetime(
        working["timestamp"],
        errors="coerce",
    )

    # Remove rows with invalid timestamps
    working = working.dropna(
        subset=["timestamp"]
    )

    if working.empty:
        return {
            "forecast": [],
            "method": "historical_hour_of_day_baseline",
            "forecast_hours": hours,
        }

    # Extract hour of day
    working["hour"] = (
        working["timestamp"].dt.hour
    )

    # Average electricity consumption for each hour
    hourly_baseline = (
        working
        .groupby("hour")["electricity_kwh"]
        .mean()
    )

    # Latest timestamp in the dataset
    latest_time = (
        working["timestamp"].max()
    )

    # Fallback average
    overall_average = float(
        working["electricity_kwh"].mean()
    )

    forecast = []

    for step in range(
        1,
        hours + 1,
    ):
        future_time = (
            latest_time
            + pd.Timedelta(
                hours=step
            )
        )

        future_hour = future_time.hour

        if future_hour in hourly_baseline.index:
            prediction = float(
                hourly_baseline.loc[
                    future_hour
                ]
            )
        else:
            prediction = overall_average

        forecast.append(
            {
                "timestamp":
                    future_time.isoformat(),

                "predicted_electricity_kwh":
                    round(
                        prediction,
                        2,
                    ),
            }
        )

    return {
        "forecast":
            forecast,

        "method":
            "historical_hour_of_day_baseline",

        "forecast_hours":
            hours,

        "description":
            (
                "Forecast generated from historical "
                "electricity consumption patterns "
                "for the same hour of day."
            ),
    }