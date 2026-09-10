# ============================================================
# MILESTONE 1
# ENERGY INTELLIGENCE DASHBOARD
# Agentic AI for Smart Facility Operations and Optimization
# ============================================================

from pathlib import Path
from datetime import datetime, timedelta
import random

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Energy Intelligence Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "milestone1_energy_dataset.csv"
)


# ============================================================
# CUSTOM DESIGN
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
        linear-gradient(
            135deg,
            #04131c 0%,
            #071b26 50%,
            #04131c 100%
        );
        color: white;
    }

    section[data-testid="stSidebar"] {
        background:
        linear-gradient(
            180deg,
            #061822,
            #092431
        );
        border-right: 1px solid #174454;
    }

    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 3rem;
    }

    .hero {
        background:
        linear-gradient(
            120deg,
            rgba(17,73,87,0.45),
            rgba(5,30,42,0.75)
        );

        border: 1px solid #176071;
        border-radius: 20px;

        padding: 24px 30px;
        margin-bottom: 22px;

        box-shadow:
        0 8px 35px rgba(0,0,0,0.20);
    }

    .hero-title {
        font-size: 38px;
        font-weight: 800;
        color: #43e8d2;
    }

    .hero-subtitle {
        color: #9ab7c2;
        font-size: 15px;
        margin-top: 6px;
    }

    .section-title {
        font-size: 23px;
        font-weight: 750;
        color: #eefcff;

        margin-top: 26px;
        margin-bottom: 13px;
    }

    .metric-card {
        background:
        linear-gradient(
            145deg,
            #0b2531,
            #071c26
        );

        border: 1px solid #174958;

        border-radius: 16px;

        padding: 18px;

        min-height: 125px;

        box-shadow:
        0 6px 22px rgba(0,0,0,0.16);
    }

    .metric-label {
        color: #8eaab5;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.7px;
    }

    .metric-value {
        font-size: 30px;
        font-weight: 800;
        color: #ffffff;
        margin-top: 8px;
    }

    .metric-unit {
        color: #45d4c1;
        font-size: 12px;
        margin-top: 4px;
    }

    .live-box {
        background: #092832;
        border: 1px solid #167c75;
        border-radius: 14px;
        padding: 14px;
        text-align: center;
    }

    .normal-box {
        background: rgba(25, 181, 112, 0.10);
        border: 1px solid #1db574;
        border-radius: 14px;
        padding: 15px;
    }

    .warning-box {
        background: rgba(244, 174, 44, 0.10);
        border: 1px solid #f4ae2c;
        border-radius: 14px;
        padding: 15px;
    }

    .danger-box {
        background: rgba(240, 75, 75, 0.10);
        border: 1px solid #f04b4b;
        border-radius: 14px;
        padding: 15px;
    }

    div[data-testid="stMetric"] {
        background: #091f29;
        border: 1px solid #174656;
        padding: 15px;
        border-radius: 14px;
    }

    .stButton button {
        border-radius: 10px;
        border: 1px solid #28cdb9;

        background:
        linear-gradient(
            90deg,
            #11685f,
            #169d8c
        );

        color: white;
        font-weight: 700;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATA FUNCTIONS
# ============================================================

@st.cache_data
def load_dataset():

    if not DATA_FILE.exists():
        return pd.DataFrame()

    try:
        data = pd.read_csv(DATA_FILE)

        data["timestamp"] = pd.to_datetime(
            data["timestamp"],
            errors="coerce"
        )

        # Convert anomaly column safely
        if data["is_anomaly"].dtype != bool:

            data["is_anomaly"] = (
                data["is_anomaly"]
                .astype(str)
                .str.lower()
                .map({
                    "true": True,
                    "false": False
                })
                .fillna(False)
            )

        return data

    except Exception as error:

        st.error(
            f"Unable to load dataset: {error}"
        )

        return pd.DataFrame()


# ============================================================
# OPTIONAL DATASET TEST GENERATOR
# ============================================================

def generate_test_dataset(
    record_count,
    building_count,
    blocks_per_building
):

    rows = []

    start_time = datetime(
        2026,
        8,
        1,
        0,
        0
    )

    for i in range(record_count):

        building_number = (
            i % building_count
        ) + 1

        block_number = (
            i % blocks_per_building
        ) + 1

        building_id = (
            f"B{building_number:03d}"
        )

        building_name = (
            f"Building {building_number}"
        )

        block_id = (
            f"BLK-{block_number}"
        )

        block_name = (
            f"Block {block_number}"
        )

        timestamp = (
            start_time
            + timedelta(
                minutes=15 * i
            )
        )

        hour = timestamp.hour


        # --------------------------------------------
        # Occupancy
        # --------------------------------------------

        if 8 <= hour <= 18:

            occupancy = random.randint(
                80,
                300
            )

        else:

            occupancy = random.randint(
                0,
                50
            )


        # --------------------------------------------
        # Utility measurements
        # --------------------------------------------

        temperature = round(
            random.uniform(
                22,
                32
            ),
            2
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

        electricity = random.uniform(
            350,
            600
        )


        # --------------------------------------------
        # Anomaly simulation
        # --------------------------------------------

        is_anomaly = False

        if random.random() < 0.03:

            is_anomaly = True

            electricity *= random.uniform(
                1.8,
                2.5
            )

            hvac *= random.uniform(
                1.6,
                2.4
            )

            lighting *= random.uniform(
                1.3,
                2.0
            )


        rows.append({

            "facility_id":
                "F001",

            "facility_name":
                "Smart Campus",

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
                round(
                    electricity,
                    2
                ),

            "water_liters":
                round(
                    water,
                    2
                ),

            "hvac_kwh":
                round(
                    hvac,
                    2
                ),

            "lighting_kwh":
                round(
                    lighting,
                    2
                ),

            "temperature_c":
                temperature,

            "occupancy":
                occupancy,

            "is_anomaly":
                is_anomaly
        })


    test_df = pd.DataFrame(
        rows
    )

    test_df.to_csv(
        DATA_FILE,
        index=False
    )

    return test_df


# ============================================================
# LOAD DATA
# ============================================================

df = load_dataset()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    """
    <h1 style="
        color:#38e4cf;
        margin-bottom:0;
    ">
    ⚡ ENERGY AI
    </h1>

    <p style="
        color:#8aa8b3;
        margin-top:3px;
    ">
    Smart Facility Operations
    </p>
    """,
    unsafe_allow_html=True
)


st.sidebar.divider()


# ============================================================
# MONITORING FILTERS
# ============================================================

st.sidebar.subheader(
    "🎛 Monitoring Controls"
)


if not df.empty:

    building_names = sorted(
        df["building_name"]
        .dropna()
        .unique()
        .tolist()
    )

else:

    building_names = []


selected_building = (
    st.sidebar.selectbox(
        "Building",

        [
            "All Buildings"
        ]
        + building_names
    )
)


if (
    selected_building
    != "All Buildings"
    and not df.empty
):

    building_blocks = sorted(

        df[
            df["building_name"]
            == selected_building
        ][
            "block_name"
        ]
        .dropna()
        .unique()
        .tolist()
    )

else:

    building_blocks = sorted(
        df["block_name"]
        .dropna()
        .unique()
        .tolist()
    ) if not df.empty else []


selected_block = (
    st.sidebar.selectbox(
        "Block",

        [
            "All Blocks"
        ]
        + building_blocks
    )
)


st.sidebar.divider()


# ============================================================
# DATASET INFORMATION
# ============================================================

st.sidebar.subheader(
    "📊 Dataset Information"
)


if not df.empty:

    st.sidebar.metric(
        "Total Records",
        f"{len(df):,}"
    )

    st.sidebar.metric(
        "Buildings",
        df["building_name"]
        .nunique()
    )

    st.sidebar.metric(
        "Blocks",
        df[
            [
                "building_id",
                "block_id"
            ]
        ]
        .drop_duplicates()
        .shape[0]
    )

    anomaly_count = int(
        df["is_anomaly"].sum()
    )

    st.sidebar.metric(
        "Labelled Anomalies",
        anomaly_count
    )


st.sidebar.divider()


# ============================================================
# DATASET TESTING
# ============================================================

st.sidebar.subheader(
    "🧪 Dataset Testing"
)


test_records = int(
    st.sidebar.number_input(
        "Number of Records",
        min_value=100,
        max_value=100000,
        value=2880,
        step=100
    )
)


test_buildings = int(
    st.sidebar.number_input(
        "Number of Buildings",
        min_value=1,
        max_value=20,
        value=3,
        step=1
    )
)


blocks_per_building = int(
    st.sidebar.number_input(
        "Blocks per Building",
        min_value=1,
        max_value=20,
        value=2,
        step=1
    )
)


if st.sidebar.button(
    "⚙ Generate Test Dataset",
    use_container_width=True
):

    generate_test_dataset(
        test_records,
        test_buildings,
        blocks_per_building
    )

    st.cache_data.clear()

    st.sidebar.success(
        f"{test_records:,} records generated!"
    )

    st.rerun()


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">

        <div class="hero-title">
        ⚡ Energy Intelligence Dashboard
        </div>

        <div class="hero-subtitle">
        Smart Facility Energy Monitoring •
        Utility Analytics •
        Anomaly Intelligence •
        Energy Efficiency Recommendations
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# STOP IF DATA IS EMPTY
# ============================================================

if df.empty:

    st.error(
        "Dataset is empty. Run the dataset generator first."
    )

    st.stop()


# ============================================================
# FILTER DATA
# ============================================================

filtered_df = df.copy()


if (
    selected_building
    != "All Buildings"
):

    filtered_df = filtered_df[
        filtered_df[
            "building_name"
        ] == selected_building
    ]


if (
    selected_block
    != "All Blocks"
):

    filtered_df = filtered_df[
        filtered_df[
            "block_name"
        ] == selected_block
    ]


filtered_df = (
    filtered_df
    .sort_values(
        "timestamp"
    )
    .reset_index(
        drop=True
    )
)


if filtered_df.empty:

    st.warning(
        "No records match the selected filters."
    )

    st.stop()


# ============================================================
# LIVE MONITORING SECTION
# ============================================================

live1, live2, live3 = st.columns(
    [1.3, 1, 2]
)


with live1:

    st.markdown(
        """
        <div class="live-box">

        🟢 <b>LIVE MONITORING</b>

        <br>

        <small>
        Simulated IoT Facility Stream
        </small>

        </div>
        """,
        unsafe_allow_html=True
    )


# Session index for next reading

if "reading_index" not in st.session_state:

    st.session_state.reading_index = 0


with live2:

    if st.button(
        "▶ Next Reading",
        use_container_width=True
    ):

        st.session_state.reading_index += 1

        if (
            st.session_state.reading_index
            >= len(filtered_df)
        ):

            st.session_state.reading_index = 0


current_index = (
    st.session_state.reading_index
    % len(filtered_df)
)


current = filtered_df.iloc[
    current_index
]


with live3:

    st.info(
        "Current reading: "
        + str(
            current[
                "timestamp"
            ]
        )
    )


# ============================================================
# LIVE FACILITY STATUS
# ============================================================

st.markdown(
    '<div class="section-title">⚡ Live Facility Status</div>',
    unsafe_allow_html=True
)


def metric_card(
    container,
    label,
    value,
    unit
):

    container.markdown(
        f"""
        <div class="metric-card">

            <div class="metric-label">
            {label}
            </div>

            <div class="metric-value">
            {value}
            </div>

            <div class="metric-unit">
            {unit}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


c1, c2, c3, c4 = st.columns(
    4
)


metric_card(
    c1,
    "ELECTRICITY",
    f"{current['electricity_kwh']:.2f}",
    "kWh"
)


metric_card(
    c2,
    "HVAC",
    f"{current['hvac_kwh']:.2f}",
    "kWh"
)


metric_card(
    c3,
    "LIGHTING",
    f"{current['lighting_kwh']:.2f}",
    "kWh"
)


metric_card(
    c4,
    "OCCUPANCY",
    int(
        current["occupancy"]
    ),
    "People"
)


st.markdown("")


c5, c6, c7, c8 = st.columns(
    4
)


metric_card(
    c5,
    "WATER",
    f"{current['water_liters']:.2f}",
    "Litres"
)


metric_card(
    c6,
    "TEMPERATURE",
    f"{current['temperature_c']:.1f}",
    "°C"
)


metric_card(
    c7,
    "BUILDING",
    current["building_id"],
    current["building_name"]
)


if bool(
    current[
        "is_anomaly"
    ]
):

    c8.markdown(
        """
        <div class="danger-box">

        <b>
        🚨 ENERGY STATUS
        </b>

        <h2>
        ANOMALY
        </h2>

        Abnormal energy behaviour detected.

        </div>
        """,
        unsafe_allow_html=True
    )

else:

    c8.markdown(
        """
        <div class="normal-box">

        <b>
        ✅ ENERGY STATUS
        </b>

        <h2>
        NORMAL
        </h2>

        Facility operating normally.

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# SUMMARY KPI
# ============================================================

st.markdown(
    '<div class="section-title">📊 Energy Analytics Summary</div>',
    unsafe_allow_html=True
)


k1, k2, k3, k4, k5 = st.columns(
    5
)


k1.metric(
    "Records",
    f"{len(filtered_df):,}"
)


k2.metric(
    "Avg Electricity",
    f"{filtered_df['electricity_kwh'].mean():.2f} kWh"
)


k3.metric(
    "Peak Electricity",
    f"{filtered_df['electricity_kwh'].max():.2f} kWh"
)


k4.metric(
    "Avg HVAC",
    f"{filtered_df['hvac_kwh'].mean():.2f} kWh"
)


anomaly_total = int(
    filtered_df[
        "is_anomaly"
    ].sum()
)


k5.metric(
    "Anomalies",
    anomaly_total
)


# ============================================================
# ENERGY TREND
# ============================================================

st.markdown(
    '<div class="section-title">📈 Electricity Consumption Monitoring</div>',
    unsafe_allow_html=True
)


chart_data = (
    filtered_df
    .tail(
        min(
            300,
            len(filtered_df)
        )
    )
)


energy_chart = px.line(

    chart_data,

    x="timestamp",

    y="electricity_kwh",

    color=(
        "building_name"

        if (
            selected_building
            == "All Buildings"
        )

        else None
    ),

    title="Electricity Consumption Over Time"
)


energy_chart.update_layout(

    template="plotly_dark",

    paper_bgcolor="#06131c",

    plot_bgcolor="#071b26",

    height=420,

    margin=dict(
        l=20,
        r=20,
        t=55,
        b=20
    )
)


st.plotly_chart(
    energy_chart,
    use_container_width=True
)


# ============================================================
# HVAC + LIGHTING TREND
# ============================================================

left, right = st.columns(
    2
)


with left:

    hvac_chart = px.line(

        chart_data,

        x="timestamp",

        y="hvac_kwh",

        title="HVAC Consumption"
    )


    hvac_chart.update_layout(

        template="plotly_dark",

        paper_bgcolor="#06131c",

        plot_bgcolor="#071b26",

        height=390
    )


    st.plotly_chart(
        hvac_chart,
        use_container_width=True
    )


with right:

    light_chart = px.line(

        chart_data,

        x="timestamp",

        y="lighting_kwh",

        title="Lighting Consumption"
    )


    light_chart.update_layout(

        template="plotly_dark",

        paper_bgcolor="#06131c",

        plot_bgcolor="#071b26",

        height=390
    )


    st.plotly_chart(
        light_chart,
        use_container_width=True
    )


# ============================================================
# OCCUPANCY VS ENERGY
# ============================================================

st.markdown(
    '<div class="section-title">👥 Occupancy & Energy Relationship</div>',
    unsafe_allow_html=True
)


sample_count = min(
    800,
    len(filtered_df)
)


scatter_data = filtered_df.sample(
    sample_count,
    random_state=42
)


scatter_chart = px.scatter(

    scatter_data,

    x="occupancy",

    y="electricity_kwh",

    size="hvac_kwh",

    color="building_name",

    hover_data=[
        "block_name",
        "temperature_c",
        "is_anomaly"
    ],

    title=
    "Occupancy vs Electricity Consumption"
)


scatter_chart.update_layout(

    template="plotly_dark",

    paper_bgcolor="#06131c",

    plot_bgcolor="#071b26",

    height=430
)


st.plotly_chart(
    scatter_chart,
    use_container_width=True
)


# ============================================================
# BUILDING COMPARISON
# ============================================================

st.markdown(
    '<div class="section-title">🏢 Building Energy Comparison</div>',
    unsafe_allow_html=True
)


building_summary = (

    df.groupby(
        "building_name"
    )

    .agg(

        records=(
            "building_name",
            "size"
        ),

        avg_electricity=(
            "electricity_kwh",
            "mean"
        ),

        avg_hvac=(
            "hvac_kwh",
            "mean"
        ),

        avg_lighting=(
            "lighting_kwh",
            "mean"
        ),

        avg_water=(
            "water_liters",
            "mean"
        ),

        avg_occupancy=(
            "occupancy",
            "mean"
        ),

        anomalies=(
            "is_anomaly",
            "sum"
        )
    )

    .reset_index()
)


building_summary[
    "avg_electricity"
] = building_summary[
    "avg_electricity"
].round(2)


comparison_chart = px.bar(

    building_summary,

    x="building_name",

    y="avg_electricity",

    text="avg_electricity",

    title=
    "Average Electricity Consumption by Building"
)


comparison_chart.update_layout(

    template="plotly_dark",

    paper_bgcolor="#06131c",

    plot_bgcolor="#071b26"
)


st.plotly_chart(
    comparison_chart,
    use_container_width=True
)


st.dataframe(
    building_summary,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# ANOMALY INTELLIGENCE
# ============================================================

st.markdown(
    '<div class="section-title">🚨 Anomaly Intelligence</div>',
    unsafe_allow_html=True
)


anomalies = filtered_df[
    filtered_df[
        "is_anomaly"
    ] == True
]


a1, a2, a3 = st.columns(
    3
)


a1.metric(
    "Total Records",
    f"{len(filtered_df):,}"
)


a2.metric(
    "Detected Anomalies",
    f"{len(anomalies):,}"
)


anomaly_rate = (

    len(anomalies)
    /
    len(filtered_df)
    *
    100
)


a3.metric(
    "Anomaly Rate",
    f"{anomaly_rate:.2f}%"
)


if not anomalies.empty:

    anomaly_chart = px.scatter(

        filtered_df,

        x="timestamp",

        y="electricity_kwh",

        color="is_anomaly",

        hover_data=[
            "building_name",
            "block_name",
            "hvac_kwh",
            "occupancy"
        ],

        title=
        "Normal vs Abnormal Energy Readings"
    )


    anomaly_chart.update_layout(

        template="plotly_dark",

        paper_bgcolor="#06131c",

        plot_bgcolor="#071b26",

        height=430
    )


    st.plotly_chart(
        anomaly_chart,
        use_container_width=True
    )


    with st.expander(
        "View Detected Anomaly Records"
    ):

        st.dataframe(

            anomalies[
                [
                    "timestamp",
                    "building_name",
                    "block_name",
                    "electricity_kwh",
                    "hvac_kwh",
                    "lighting_kwh",
                    "occupancy",
                    "temperature_c"
                ]
            ],

            use_container_width=True,

            hide_index=True
        )


# ============================================================
# ENERGY EFFICIENCY RECOMMENDATIONS
# ============================================================

st.markdown(
    '<div class="section-title">🤖 Energy Agent Recommendations</div>',
    unsafe_allow_html=True
)


recommendations = []


average_electricity = (
    filtered_df[
        "electricity_kwh"
    ].mean()
)


average_hvac = (
    filtered_df[
        "hvac_kwh"
    ].mean()
)


average_lighting = (
    filtered_df[
        "lighting_kwh"
    ].mean()
)


average_water = (
    filtered_df[
        "water_liters"
    ].mean()
)


average_occupancy = (
    filtered_df[
        "occupancy"
    ].mean()
)


# --------------------------------------------
# Recommendation 1
# --------------------------------------------

if anomaly_total > 0:

    recommendations.append(

        "🚨 "
        f"{anomaly_total} abnormal energy readings were detected. "
        "Inspect the affected building/block and verify HVAC, "
        "lighting schedules and equipment operation."
    )


# --------------------------------------------
# Recommendation 2
# --------------------------------------------

low_occupancy_high_hvac = filtered_df[

    (
        filtered_df[
            "occupancy"
        ]
        <
        average_occupancy * 0.5
    )

    &

    (
        filtered_df[
            "hvac_kwh"
        ]
        >
        average_hvac * 1.25
    )
]


if len(
    low_occupancy_high_hvac
) > 0:

    recommendations.append(

        "❄️ HVAC consumption is high during some low-occupancy "
        "periods. Consider occupancy-based HVAC scheduling."
    )


# --------------------------------------------
# Recommendation 3
# --------------------------------------------

low_occupancy_high_lighting = filtered_df[

    (
        filtered_df[
            "occupancy"
        ]
        <
        average_occupancy * 0.5
    )

    &

    (
        filtered_df[
            "lighting_kwh"
        ]
        >
        average_lighting * 1.25
    )
]


if len(
    low_occupancy_high_lighting
) > 0:

    recommendations.append(

        "💡 High lighting consumption was observed during "
        "low-occupancy periods. Consider occupancy sensors "
        "or automated lighting schedules."
    )


# --------------------------------------------
# Recommendation 4
# --------------------------------------------

if (
    filtered_df[
        "electricity_kwh"
    ].max()
    >
    average_electricity * 1.8
):

    recommendations.append(

        "⚡ Large electricity peaks are present. "
        "Investigate peak-hour equipment usage and consider "
        "load scheduling."
    )


# --------------------------------------------
# Recommendation 5
# --------------------------------------------

if (
    filtered_df[
        "water_liters"
    ].max()
    >
    average_water * 1.5
):

    recommendations.append(

        "💧 Water-consumption peaks were detected. "
        "Check for unusual demand or possible wastage."
    )


if not recommendations:

    recommendations.append(

        "✅ Energy usage is currently within expected operating "
        "patterns. Continue monitoring for efficiency changes."
    )


for recommendation in recommendations:

    st.info(
        recommendation
    )


# ============================================================
# RAW DATA VIEWER
# ============================================================

st.markdown(
    '<div class="section-title">📋 CSV Dataset Viewer</div>',
    unsafe_allow_html=True
)


with st.expander(
    "Open Dataset Records"
):

    st.dataframe(

        filtered_df,

        use_container_width=True,

        height=450,

        hide_index=True
    )


# ============================================================
# DOWNLOAD DATASET
# ============================================================

csv_data = (
    filtered_df
    .to_csv(
        index=False
    )
)


st.download_button(

    "⬇ Download Filtered CSV",

    data=csv_data,

    file_name=
    "energy_monitoring_data.csv",

    mime="text/csv"
)


# ============================================================
# FOOTER
# ============================================================

st.divider()


st.caption(
    "Milestone 1 • Energy Intelligence & Monitoring • "
    "Agentic AI for Smart Facility Operations and Optimization"
)