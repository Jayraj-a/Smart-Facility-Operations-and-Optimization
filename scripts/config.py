# ============================================================
# SMART FACILITY OPERATIONS
# Milestone 1 - Dataset Configuration
# ============================================================


# ------------------------------------------------------------
# DATASET SETTINGS
# ------------------------------------------------------------

START_DATE = "2026-08-01"

NUMBER_OF_DAYS = 30

OUTPUT_FILE = "data/milestone1_energy_dataset.csv"


# ------------------------------------------------------------
# FACILITY CONFIGURATION
# ------------------------------------------------------------

FACILITIES = [

    {
        "facility_id": "F001",
        "facility_name": "Smart Campus",

        "buildings": [

            {
                "building_id": "B001",
                "building_name": "Main Building",

                "blocks": [

                    {
                        "block_id": "BLK-A",
                        "block_name": "North Block"
                    },

                    {
                        "block_id": "BLK-B",
                        "block_name": "South Block"
                    }

                ]
            },

            {
                "building_id": "B002",
                "building_name": "Academic Building",

                "blocks": [

                    {
                        "block_id": "BLK-A",
                        "block_name": "Academic Block"
                    }

                ]
            },

            {
                "building_id": "B003",
                "building_name": "Administration Building",

                "blocks": [

                    {
                        "block_id": "BLK-A",
                        "block_name": "Admin Block"
                    }

                ]
            }

        ]
    }

]