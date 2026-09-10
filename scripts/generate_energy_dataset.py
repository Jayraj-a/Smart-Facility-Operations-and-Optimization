# ============================================================
# SMART FACILITY OPERATIONS
# Milestone 1 - Energy Dataset Generator
# ============================================================

import pandas as pd
import random

from datetime import datetime, timedelta

from config import (
    FACILITIES,
    START_DATE,
    NUMBER_OF_DAYS,
    OUTPUT_FILE
)


# ------------------------------------------------------------
# 1. INITIALIZE DATA
# ------------------------------------------------------------

data = []

start_date = datetime.strptime(
    START_DATE,
    "%Y-%m-%d"
)


# ------------------------------------------------------------
# 2. LOOP THROUGH FACILITIES
# ------------------------------------------------------------

for facility in FACILITIES:

    facility_id = facility["facility_id"]

    facility_name = facility["facility_name"]


    # --------------------------------------------------------
    # LOOP THROUGH BUILDINGS
    # --------------------------------------------------------

    for building in facility["buildings"]:

        building_id = building["building_id"]

        building_name = building["building_name"]


        # ----------------------------------------------------
        # LOOP THROUGH BLOCKS
        # ----------------------------------------------------

        for block in building["blocks"]:

            block_id = block["block_id"]

            block_name = block["block_name"]


            # ------------------------------------------------
            # LOOP THROUGH DAYS
            # ------------------------------------------------

            for day in range(NUMBER_OF_DAYS):

                current_date = (
                    start_date +
                    timedelta(days=day)
                )


                # --------------------------------------------
                # LOOP THROUGH 24 HOURS
                # --------------------------------------------

                for hour in range(24):

                    timestamp = (
                        current_date +
                        timedelta(hours=hour)
                    )


                    # ----------------------------------------
                    # OCCUPANCY
                    # ----------------------------------------

                    if 8 <= hour <= 18:

                        occupancy = random.randint(
                            100,
                            300
                        )

                    else:

                        occupancy = random.randint(
                            0,
                            50
                        )


                    # ----------------------------------------
                    # TEMPERATURE
                    # ----------------------------------------

                    temperature = round(
                        random.uniform(24, 32),
                        2
                    )


                    # ----------------------------------------
                    # ENERGY CONSUMPTION
                    # ----------------------------------------

                    electricity = random.uniform(
                        350,
                        600
                    )

                    hvac = random.uniform(
                        150,
                        300
                    )

                    lighting = random.uniform(
                        50,
                        120
                    )

                    water = random.uniform(
                        80,
                        200
                    )


                    # ----------------------------------------
                    # ANOMALY
                    # ----------------------------------------

                    is_anomaly = False


                    if random.random() < 0.03:

                        is_anomaly = True

                        electricity *= random.uniform(
                            1.8,
                            2.5
                        )

                        hvac *= random.uniform(
                            1.8,
                            2.5
                        )

                        lighting *= random.uniform(
                            1.5,
                            2.0
                        )


                    # ----------------------------------------
                    # ROUND VALUES
                    # ----------------------------------------

                    electricity = round(
                        electricity,
                        2
                    )

                    hvac = round(
                        hvac,
                        2
                    )

                    lighting = round(
                        lighting,
                        2
                    )

                    water = round(
                        water,
                        2
                    )


                    # ----------------------------------------
                    # STORE RECORD
                    # ----------------------------------------

                    data.append({

                        "facility_id":
                            facility_id,

                        "facility_name":
                            facility_name,

                        "building_id":
                            building_id,

                        "building_name":
                            building_name,

                        "block_id":
                            block_id,

                        "block_name":
                            block_name,

                        "timestamp":
                            timestamp,

                        "electricity_kwh":
                            electricity,

                        "water_liters":
                            water,

                        "hvac_kwh":
                            hvac,

                        "lighting_kwh":
                            lighting,

                        "temperature_c":
                            temperature,

                        "occupancy":
                            occupancy,

                        "is_anomaly":
                            is_anomaly
                    })


# ------------------------------------------------------------
# 3. CREATE DATAFRAME
# ------------------------------------------------------------

df = pd.DataFrame(data)


# ------------------------------------------------------------
# 4. SAVE CSV FILE
# ------------------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ------------------------------------------------------------
# 5. DISPLAY INFORMATION
# ------------------------------------------------------------

print("=" * 60)

print("ENERGY DATASET CREATED SUCCESSFULLY")

print("=" * 60)

print()

print("Number of records:")

print(len(df))

print()

print("Number of columns:")

print(len(df.columns))

print()

print("Columns:")

for column in df.columns:

    print("-", column)

print()

print("Number of anomalies:")

print(df["is_anomaly"].sum())

print()

print("First 5 records:")

print(df.head())

print()

print("Dataset saved at:")

print(OUTPUT_FILE)

print()

print("=" * 60)