"use strict";


/* ============================================================
   FACILITYOPS AI
   UNIFIED FACILITY OPERATIONS DASHBOARD

   Energy
   Predictive Maintenance
   Occupancy Intelligence
   Security Intelligence
   ============================================================ */


const COLORS = {

    page: "#0A1414",
    card: "#101C1C",
    border: "#1C2B2A",
    muted: "#6B8180",
    text: "#E5E7EB",
    teal: "#2DD4BF",
    danger: "#EF4444",
    dangerLight: "#F87171",
    chartMuted: "#4B5D5C",
    hvac: "#5DCAA5"

};


const AUTO_REFRESH_MS = 30000;


const facilitySelect =
    document.getElementById("facilitySelect");

const buildingSelect =
    document.getElementById("buildingSelect");

const blockSelect =
    document.getElementById("blockSelect");


/* ============================================================
   HELPERS
   ============================================================ */

function escapeHTML(value) {

    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");

}


function numberValue(
    value,
    decimals = 1
) {

    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "--";
    }

    return number.toLocaleString(
        undefined,
        {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }
    );

}


function integerValue(value) {

    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "--";
    }

    return Math.round(number)
        .toLocaleString();

}


function percentValue(value) {

    let number = Number(value);

    if (!Number.isFinite(number)) {
        return "--";
    }

    if (
        number >= 0 &&
        number <= 1
    ) {
        number *= 100;
    }

    return number.toFixed(1) + "%";

}


function timestampValue(value) {

    if (!value) {
        return "--";
    }

    const date = new Date(value);

    if (
        Number.isNaN(
            date.getTime()
        )
    ) {
        return String(value);
    }

    return date.toLocaleString();

}


function dateValue(value) {

    if (!value) {
        return "--";
    }

    const date = new Date(value);

    if (
        Number.isNaN(
            date.getTime()
        )
    ) {
        return String(value);
    }

    return date.toLocaleDateString();

}


function setText(
    elementId,
    value
) {

    const element =
        document.getElementById(
            elementId
        );

    if (element) {
        element.textContent = value;
    }

}


function firstDefined(
    object,
    keys,
    fallback = null
) {

    if (
        !object ||
        typeof object !== "object"
    ) {
        return fallback;
    }

    for (const key of keys) {

        if (
            object[key] !== undefined &&
            object[key] !== null
        ) {
            return object[key];
        }

    }

    return fallback;

}


function extractArray(
    data,
    possibleKeys = []
) {

    if (Array.isArray(data)) {
        return data;
    }

    if (
        !data ||
        typeof data !== "object"
    ) {
        return [];
    }

    for (const key of possibleKeys) {

        if (Array.isArray(data[key])) {
            return data[key];
        }

    }

    for (const value of Object.values(data)) {

        if (Array.isArray(value)) {
            return value;
        }

    }

    return [];

}


function normalizeStatus(value) {

    return String(
        value || "UNKNOWN"
    )
        .trim()
        .toUpperCase();

}


function statusClass(value) {

    const status =
        normalizeStatus(value);

    if (
        status === "EXCELLENT" ||
        status === "OPTIMAL" ||
        status === "NORMAL" ||
        status === "GRANTED"
    ) {
        return "status-excellent";
    }

    if (
        status === "GOOD" ||
        status === "LOW"
    ) {
        return "status-good";
    }

    if (
        status === "WARNING" ||
        status === "WATCH" ||
        status === "HIGH" ||
        status === "UNDERUSED"
    ) {
        return "status-warning";
    }

    if (
        status === "CRITICAL" ||
        status === "OVERCROWDED" ||
        status === "DENIED"
    ) {
        return "status-critical";
    }

    return "status-good";

}


function priorityClass(value) {

    const priority =
        normalizeStatus(value);

    if (priority === "CRITICAL") {
        return "priority-critical";
    }

    if (
        priority === "HIGH" ||
        priority === "OVERCROWDED"
    ) {
        return "priority-high";
    }

    if (
        priority === "MEDIUM" ||
        priority === "WARNING"
    ) {
        return "priority-medium";
    }

    return "priority-low";

}


function showError(
    elementId,
    message
) {

    const element =
        document.getElementById(
            elementId
        );

    if (!element) {
        return;
    }

    element.innerHTML = `
        <div class="data-error">
            ${escapeHTML(message)}
        </div>
    `;

}


function showEmpty(
    elementId,
    title,
    message
) {

    const element =
        document.getElementById(
            elementId
        );

    if (!element) {
        return;
    }

    element.innerHTML = `
        <div class="empty-state">
            <h3>${escapeHTML(title)}</h3>
            <p>${escapeHTML(message)}</p>
        </div>
    `;

}


/* ============================================================
   HTTP
   ============================================================ */

async function requestJSON(
    url,
    options = {}
) {

    const response =
        await fetch(
            url,
            {
                credentials: "same-origin",
                ...options
            }
        );

    if (response.status === 401) {

        window.location.href =
            "/login";

        throw new Error(
            "Authentication required."
        );

    }

    if (!response.ok) {

        let detail =
            `Request failed (${response.status})`;

        try {

            const errorData =
                await response.json();

            if (
                errorData &&
                errorData.detail
            ) {
                detail =
                    errorData.detail;
            }

        } catch (error) {

            console.debug(
                "No JSON error response.",
                error
            );

        }

        throw new Error(detail);

    }

    return response.json();

}


async function getJSON(url) {

    return requestJSON(
        url,
        {
            method: "GET"
        }
    );

}


async function postJSON(
    url,
    body = null
) {

    const options = {

        method: "POST",

        headers: {
            "Content-Type":
                "application/json"
        }

    };

    if (body !== null) {

        options.body =
            JSON.stringify(body);

    }

    return requestJSON(
        url,
        options
    );

}


/* ============================================================
   FILTER HELPERS
   ============================================================ */

function selectedBuilding() {

    if (!buildingSelect) {
        return "";
    }

    return buildingSelect.value || "";

}


function selectedBlock() {

    if (!blockSelect) {
        return "";
    }

    return blockSelect.value || "";

}


function queryParams(
    additional = {}
) {

    const parameters =
        new URLSearchParams();

    const building =
        selectedBuilding();

    const block =
        selectedBlock();

    if (building) {

        parameters.set(
            "building",
            building
        );

    }

    if (block) {

        parameters.set(
            "block",
            block
        );

    }

    Object.entries(
        additional
    ).forEach(
        ([key, value]) => {

            if (
                value !== undefined &&
                value !== null &&
                value !== ""
            ) {

                parameters.set(
                    key,
                    value
                );

            }

        }
    );

    return parameters;

}


function buildURL(
    path,
    additional = {}
) {

    const parameters =
        queryParams(additional);

    const query =
        parameters.toString();

    return query
        ? `${path}?${query}`
        : path;

}


/* ============================================================
   PLOTLY
   ============================================================ */

function commonLayout() {

    return {

        paper_bgcolor:
            COLORS.card,

        plot_bgcolor:
            COLORS.card,

        font: {

            color:
                COLORS.muted,

            family:
                "Inter, Arial, sans-serif",

            size:
                10

        },

        margin: {
            l: 48,
            r: 18,
            t: 18,
            b: 45
        },

        xaxis: {

            gridcolor:
                COLORS.border,

            zerolinecolor:
                COLORS.border,

            linecolor:
                COLORS.border,

            tickfont: {
                color:
                    COLORS.muted
            },

            automargin:
                true

        },

        yaxis: {

            gridcolor:
                COLORS.border,

            zerolinecolor:
                COLORS.border,

            linecolor:
                COLORS.border,

            tickfont: {
                color:
                    COLORS.muted
            },

            automargin:
                true

        },

        hoverlabel: {

            bgcolor:
                COLORS.page,

            bordercolor:
                COLORS.border,

            font: {
                color:
                    COLORS.text
            }

        },

        legend: {

            font: {
                color:
                    COLORS.muted
            }

        }

    };

}


const plotConfig = {

    responsive:
        true,

    displaylogo:
        false,

    modeBarButtonsToRemove: [
        "lasso2d",
        "select2d"
    ]

};


/* ============================================================
   FACILITY
   ============================================================ */

async function loadFacility() {

    try {

        const data =
            await getJSON(
                "/api/facility"
            );


        if (facilitySelect) {

            facilitySelect.innerHTML =
                "";

            let facilityName =
                firstDefined(
                    data,
                    [
                        "facility_name",
                        "name",
                        "facility"
                    ],
                    "Facility"
                );

            if (
                Array.isArray(
                    data.facilities
                ) &&
                data.facilities.length
            ) {

                facilityName =
                    firstDefined(
                        data.facilities[0],
                        [
                            "facility_name",
                            "name"
                        ],
                        facilityName
                    );

            }

            const option =
                document.createElement(
                    "option"
                );

            option.value =
                facilityName;

            option.textContent =
                facilityName;

            facilitySelect.appendChild(
                option
            );

        }


        const buildings =
            Array.isArray(
                data.buildings
            )
                ? data.buildings
                : [];


        if (buildingSelect) {

            buildingSelect.innerHTML =
                '<option value="">All Buildings</option>';

            buildings.forEach(
                building => {

                    const name =
                        typeof building === "string"
                            ? building
                            : firstDefined(
                                building,
                                [
                                    "building_name",
                                    "name"
                                ],
                                ""
                            );

                    if (!name) {
                        return;
                    }

                    const option =
                        document.createElement(
                            "option"
                        );

                    option.value = name;
                    option.textContent = name;

                    buildingSelect.appendChild(
                        option
                    );

                }
            );

        }


        const blocks =
            Array.isArray(
                data.blocks
            )
                ? data.blocks
                : [];


        if (blockSelect) {

            blockSelect.innerHTML =
                '<option value="">All Blocks</option>';

            const seen =
                new Set();

            blocks.forEach(
                block => {

                    const name =
                        typeof block === "string"
                            ? block
                            : firstDefined(
                                block,
                                [
                                    "block_name",
                                    "name"
                                ],
                                ""
                            );

                    if (
                        !name ||
                        seen.has(name)
                    ) {
                        return;
                    }

                    seen.add(name);

                    const option =
                        document.createElement(
                            "option"
                        );

                    option.value = name;
                    option.textContent = name;

                    blockSelect.appendChild(
                        option
                    );

                }
            );

        }

    } catch (error) {

        console.error(
            "Facility loading failed:",
            error
        );

    }

}


/* ============================================================
   ENERGY
   ============================================================ */

async function loadSummary() {

    try {

        const data =
            await getJSON(
                buildURL(
                    "/api/summary"
                )
            );


        setText(
            "electricityMetric",
            numberValue(
                data.electricity_total,
                1
            )
        );

        setText(
            "energyElectricityMetric",
            numberValue(
                data.electricity_total,
                1
            )
        );

        setText(
            "hvacMetric",
            numberValue(
                data.hvac_average,
                1
            )
        );

        setText(
            "lightingMetric",
            numberValue(
                data.lighting_average,
                1
            )
        );

        setText(
            "occupancyMetric",
            numberValue(
                data.occupancy_average,
                0
            )
        );

        setText(
            "waterMetric",
            numberValue(
                data.water_average,
                1
            )
        );

        setText(
            "anomalyMetric",
            integerValue(
                data.anomalies
            )
        );

    } catch (error) {

        console.error(
            "Energy summary failed:",
            error
        );

    }

}


async function loadReadings() {

    try {

        const response =
            await getJSON(
                buildURL(
                    "/api/readings",
                    {
                        limit: 300
                    }
                )
            );

        const readings =
            extractArray(
                response,
                [
                    "readings",
                    "records",
                    "data",
                    "items"
                ]
            );

        if (!readings.length) {
            return;
        }

        readings.sort(
            (a, b) =>
                new Date(a.timestamp) -
                new Date(b.timestamp)
        );

        const timestamps =
            readings.map(
                row =>
                    row.timestamp
            );

        const electricity =
            readings.map(
                row =>
                    Number(
                        firstDefined(
                            row,
                            [
                                "electricity_kwh",
                                "electricity"
                            ],
                            0
                        )
                    )
            );

        const hvac =
            readings.map(
                row =>
                    Number(
                        firstDefined(
                            row,
                            [
                                "hvac_kwh",
                                "hvac"
                            ],
                            0
                        )
                    )
            );

        const occupancy =
            readings.map(
                row =>
                    Number(
                        row.occupancy || 0
                    )
            );

        drawEnergyChart(
            timestamps,
            electricity
        );

        drawHVACChart(
            timestamps,
            hvac
        );

        drawEnergyOccupancyChart(
            occupancy,
            electricity
        );

    } catch (error) {

        console.error(
            "Energy readings failed:",
            error
        );

    }

}


function drawEnergyChart(
    timestamps,
    values
) {

    const element =
        document.getElementById(
            "energyChart"
        );

    if (
        !element ||
        typeof Plotly === "undefined"
    ) {
        return;
    }

    const layout =
        commonLayout();

    layout.height = 350;
    layout.showlegend = false;

    layout.yaxis = {
        ...layout.yaxis,
        title: "Electricity kWh"
    };

    Plotly.react(
        element,
        [
            {
                x: timestamps,
                y: values,
                type: "scatter",
                mode: "lines",

                line: {
                    color:
                        COLORS.teal,
                    width: 2
                },

                fill:
                    "tozeroy",

                fillcolor:
                    "rgba(45,212,191,0.04)",

                hovertemplate:
                    "%{x}<br>%{y:.2f} kWh<extra></extra>"
            }
        ],
        layout,
        plotConfig
    );

}


function drawHVACChart(
    timestamps,
    values
) {

    const element =
        document.getElementById(
            "hvacChart"
        );

    if (
        !element ||
        typeof Plotly === "undefined"
    ) {
        return;
    }

    const layout =
        commonLayout();

    layout.height = 350;
    layout.showlegend = false;

    layout.yaxis = {
        ...layout.yaxis,
        title: "HVAC kWh"
    };

    Plotly.react(
        element,
        [
            {
                x: timestamps,
                y: values,
                type: "scatter",
                mode: "lines",

                line: {
                    color:
                        COLORS.hvac,
                    width: 2
                },

                hovertemplate:
                    "%{x}<br>%{y:.2f} kWh<extra></extra>"
            }
        ],
        layout,
        plotConfig
    );

}


function drawEnergyOccupancyChart(
    occupancy,
    electricity
) {

    const element =
        document.getElementById(
            "occupancyChart"
        );

    if (
        !element ||
        typeof Plotly === "undefined"
    ) {
        return;
    }

    const layout =
        commonLayout();

    layout.height = 350;
    layout.showlegend = false;

    layout.xaxis = {
        ...layout.xaxis,
        title: "Occupancy"
    };

    layout.yaxis = {
        ...layout.yaxis,
        title: "Electricity kWh"
    };

    Plotly.react(
        element,
        [
            {
                x: occupancy,
                y: electricity,
                type: "scatter",
                mode: "markers",

                marker: {
                    color:
                        COLORS.teal,
                    size: 5,
                    opacity: 0.55
                },

                hovertemplate:
                    "Occupancy: %{x}<br>Electricity: %{y:.2f}<extra></extra>"
            }
        ],
        layout,
        plotConfig
    );

}


async function loadBuildingComparison() {

    try {

        const response =
            await getJSON(
                buildURL(
                    "/api/building-comparison"
                )
            );

        const rows =
            extractArray(
                response,
                [
                    "buildings",
                    "comparison",
                    "data",
                    "records",
                    "items"
                ]
            );

        const element =
            document.getElementById(
                "buildingChart"
            );

        if (
            !element ||
            typeof Plotly === "undefined"
        ) {
            return;
        }

        const names =
            rows.map(
                row =>
                    firstDefined(
                        row,
                        [
                            "building_name",
                            "building",
                            "name"
                        ],
                        "Building"
                    )
            );

        const values =
            rows.map(
                row =>
                    Number(
                        firstDefined(
                            row,
                            [
                                "electricity_kwh",
                                "electricity_total",
                                "electricity_average",
                                "total_electricity",
                                "average_electricity"
                            ],
                            0
                        )
                    )
            );

        const layout =
            commonLayout();

        layout.height = 350;
        layout.showlegend = false;

        layout.yaxis = {
            ...layout.yaxis,
            title: "Electricity kWh"
        };

        Plotly.react(
            element,
            [
                {
                    x: names,
                    y: values,
                    type: "bar",

                    marker: {
                        color:
                            COLORS.teal
                    }
                }
            ],
            layout,
            plotConfig
        );

    } catch (error) {

        console.error(
            "Building comparison failed:",
            error
        );

    }

}


async function runEnergyAgent() {

    try {

        await postJSON(
            buildURL(
                "/api/agent/run"
            )
        );

    } catch (error) {

        console.error(
            "Energy agent failed:",
            error
        );

    }

}


/* ============================================================
   ENERGY ISSUE CENTRE
   ============================================================ */

async function loadStoredIssues() {

    const container =
        document.getElementById(
            "anomalyTable"
        );

    if (!container) {
        return;
    }

    try {

        const response =
            await getJSON(
                buildURL(
                    "/api/issues"
                )
            );

        const issues =
            extractArray(
                response,
                [
                    "issues",
                    "alerts",
                    "data",
                    "records",
                    "items"
                ]
            );

        if (!issues.length) {

            showEmpty(
                "anomalyTable",
                "No Flagged Issues",
                "No unusual usage issues are currently stored."
            );

            return;

        }

        container.innerHTML =
            issues
                .slice(0, 30)
                .map(
                    issue => {

                        const severity =
                            normalizeStatus(
                                firstDefined(
                                    issue,
                                    [
                                        "severity",
                                        "priority",
                                        "level"
                                    ],
                                    "WATCH"
                                )
                            );

                        const title =
                            firstDefined(
                                issue,
                                [
                                    "title",
                                    "issue_type",
                                    "alert_type",
                                    "type"
                                ],
                                "Unusual Reading"
                            );

                        const message =
                            firstDefined(
                                issue,
                                [
                                    "message",
                                    "description",
                                    "recommendation"
                                ],
                                "Unusual facility usage detected."
                            );

                        const building =
                            firstDefined(
                                issue,
                                [
                                    "building_name",
                                    "building"
                                ],
                                ""
                            );

                        const timestamp =
                            firstDefined(
                                issue,
                                [
                                    "timestamp",
                                    "created_at",
                                    "detected_at"
                                ],
                                ""
                            );

                        return `
                            <article class="issue-card">

                                <div class="card-topline">

                                    <h3 class="card-title">
                                        ${escapeHTML(title)}
                                    </h3>

                                    <span class="priority-badge ${priorityClass(severity)}">
                                        ${escapeHTML(severity)}
                                    </span>

                                </div>

                                <div class="card-meta">
                                    ${escapeHTML(building)}
                                    ${timestamp ? " · " + escapeHTML(timestampValue(timestamp)) : ""}
                                </div>

                                <p class="card-message">
                                    ${escapeHTML(message)}
                                </p>

                            </article>
                        `;

                    }
                )
                .join("");

    } catch (error) {

        console.error(
            "Issue loading failed:",
            error
        );

        showError(
            "anomalyTable",
            "Unable to load the Issue Centre."
        );

    }

}


/* ============================================================
   ENERGY ALERTS
   ============================================================ */

async function loadConsumptionAlerts() {

    const container =
        document.getElementById(
            "consumptionAlerts"
        );

    if (!container) {
        return;
    }

    try {

        const response =
            await getJSON(
                buildURL(
                    "/api/consumption-alerts"
                )
            );

        const alerts =
            extractArray(
                response,
                [
                    "alerts",
                    "recommendations",
                    "data",
                    "items"
                ]
            );

        renderAlertCards(
            "consumptionAlerts",
            alerts,
            "No Energy Alerts",
            "No active consumption alerts are currently available."
        );

    } catch (error) {

        showError(
            "consumptionAlerts",
            "Unable to load energy consumption alerts."
        );

    }

}


/* ============================================================
   MAINTENANCE
   ============================================================ */

async function runMaintenanceAgent() {

    try {

        await postJSON(
            "/api/maintenance/agent/run"
        );

    } catch (error) {

        console.error(
            "Maintenance agent failed:",
            error
        );

    }

}


async function loadMaintenanceSummary() {

    try {

        const data =
            await getJSON(
                buildURL(
                    "/api/maintenance/summary"
                )
            );

        const summary =
            (
                data.summary &&
                typeof data.summary === "object"
            )
                ? data.summary
                : data;

        setText(
            "maintenanceAssetsMetric",
            integerValue(
                firstDefined(
                    summary,
                    [
                        "assets_monitored",
                        "assets",
                        "total_assets"
                    ],
                    0
                )
            )
        );

        setText(
            "maintenanceHealthMetric",
            numberValue(
                firstDefined(
                    summary,
                    [
                        "average_health_score",
                        "average_health",
                        "health_score"
                    ],
                    0
                ),
                1
            )
        );

        setText(
            "excellentAssetsMetric",
            integerValue(
                firstDefined(
                    summary,
                    [
                        "excellent_assets",
                        "excellent"
                    ],
                    0
                )
            )
        );

        setText(
            "goodAssetsMetric",
            integerValue(
                firstDefined(
                    summary,
                    [
                        "good_assets",
                        "good"
                    ],
                    0
                )
            )
        );

        setText(
            "warningAssetsMetric",
            integerValue(
                firstDefined(
                    summary,
                    [
                        "warning_assets",
                        "warning"
                    ],
                    0
                )
            )
        );

        setText(
            "criticalAssetsMetric",
            integerValue(
                firstDefined(
                    summary,
                    [
                        "critical_assets",
                        "critical"
                    ],
                    0
                )
            )
        );

    } catch (error) {

        console.error(
            "Maintenance summary failed:",
            error
        );

    }

}


async function loadAssetMonitoring() {

    const container =
        document.getElementById(
            "assetMonitoringTable"
        );

    if (!container) {
        return;
    }

    try {

        let response;

        try {

            response =
                await getJSON(
                    buildURL(
                        "/api/maintenance/readings",
                        {
                            limit: 100
                        }
                    )
                );

        } catch (error) {

            response =
                await getJSON(
                    buildURL(
                        "/api/maintenance/assets"
                    )
                );

        }

        const rows =
            extractArray(
                response,
                [
                    "readings",
                    "assets",
                    "data",
                    "records",
                    "items"
                ]
            );

        if (!rows.length) {

            showEmpty(
                "assetMonitoringTable",
                "No Asset Data",
                "No equipment monitoring data is currently available."
            );

            return;

        }

        const latestMap =
            new Map();

        rows.forEach(
            row => {

                const assetId =
                    firstDefined(
                        row,
                        [
                            "asset_id",
                            "id",
                            "asset_name"
                        ],
                        "asset"
                    );

                const previous =
                    latestMap.get(
                        assetId
                    );

                if (!previous) {

                    latestMap.set(
                        assetId,
                        row
                    );

                    return;
                }

                const currentTime =
                    new Date(
                        firstDefined(
                            row,
                            [
                                "timestamp",
                                "reading_timestamp"
                            ],
                            0
                        )
                    ).getTime();

                const previousTime =
                    new Date(
                        firstDefined(
                            previous,
                            [
                                "timestamp",
                                "reading_timestamp"
                            ],
                            0
                        )
                    ).getTime();

                if (
                    currentTime >
                    previousTime
                ) {

                    latestMap.set(
                        assetId,
                        row
                    );

                }

            }
        );

        const latestRows =
            Array.from(
                latestMap.values()
            );

        container.innerHTML = `
            <table class="data-table">

                <thead>
                    <tr>
                        <th>Asset</th>
                        <th>Location</th>
                        <th>Temperature</th>
                        <th>Vibration</th>
                        <th>Pressure</th>
                        <th>Power</th>
                        <th>Age</th>
                        <th>Service Age</th>
                    </tr>
                </thead>

                <tbody>

                    ${
                        latestRows
                            .map(
                                row => `
                                    <tr>

                                        <td>
                                            <span class="asset-name">
                                                ${escapeHTML(firstDefined(row, ["asset_name", "name"], "Equipment"))}
                                            </span>

                                            <span class="sub-text">
                                                ${escapeHTML(firstDefined(row, ["asset_id", "id"], "--"))}
                                            </span>
                                        </td>

                                        <td>
                                            ${escapeHTML(firstDefined(row, ["building_name", "building"], "--"))}
                                            <span class="sub-text">
                                                ${escapeHTML(firstDefined(row, ["block_name", "block"], ""))}
                                            </span>
                                        </td>

                                        <td>
                                            ${numberValue(firstDefined(row, ["temperature_c", "temperature"], null), 1)} °C
                                        </td>

                                        <td>
                                            ${numberValue(firstDefined(row, ["vibration_mm_s", "vibration"], null), 2)} mm/s
                                        </td>

                                        <td>
                                            ${numberValue(firstDefined(row, ["pressure_bar", "pressure"], null), 2)} bar
                                        </td>

                                        <td>
                                            ${numberValue(firstDefined(row, ["power_kw", "power"], null), 1)} kW
                                        </td>

                                        <td>
                                            ${numberValue(firstDefined(row, ["age_years", "age"], null), 1)} yr
                                        </td>

                                        <td>
                                            ${integerValue(firstDefined(row, ["days_since_service"], null))} days
                                        </td>

                                    </tr>
                                `
                            )
                            .join("")
                    }

                </tbody>

            </table>
        `;

    } catch (error) {

        showError(
            "assetMonitoringTable",
            "Unable to load asset monitoring data."
        );

    }

}


async function loadEquipmentHealth() {

    const container =
        document.getElementById(
            "equipmentHealthTable"
        );

    if (!container) {
        return;
    }

    try {

        const response =
            await getJSON(
                buildURL(
                    "/api/maintenance/health"
                )
            );

        const rows =
            extractArray(
                response,
                [
                    "assets",
                    "health",
                    "data",
                    "records",
                    "items"
                ]
            );

        drawMaintenanceHealthChart(
            rows
        );

        if (!rows.length) {

            showEmpty(
                "equipmentHealthTable",
                "No Health Data",
                "No equipment health scores are currently available."
            );

            return;

        }

        container.innerHTML = `
            <table class="data-table">

                <thead>
                    <tr>
                        <th>Asset</th>
                        <th>Type</th>
                        <th>Building</th>
                        <th>Health Score</th>
                        <th>Status</th>
                        <th>Maintenance Risk</th>
                    </tr>
                </thead>

                <tbody>

                    ${
                        rows
                            .map(
                                row => {

                                    const health =
                                        Number(
                                            firstDefined(
                                                row,
                                                [
                                                    "equipment_health_score",
                                                    "health_score",
                                                    "score"
                                                ],
                                                0
                                            )
                                        );

                                    const status =
                                        normalizeStatus(
                                            firstDefined(
                                                row,
                                                [
                                                    "equipment_health_status",
                                                    "health_status",
                                                    "status"
                                                ],
                                                "UNKNOWN"
                                            )
                                        );

                                    const risk =
                                        firstDefined(
                                            row,
                                            [
                                                "maintenance_probability_percent",
                                                "maintenance_probability",
                                                "maintenance_risk",
                                                "probability"
                                            ],
                                            null
                                        );

                                    return `
                                        <tr>

                                            <td>
                                                <span class="asset-name">
                                                    ${escapeHTML(firstDefined(row, ["asset_name", "name"], "Equipment"))}
                                                </span>

                                                <span class="sub-text">
                                                    ${escapeHTML(firstDefined(row, ["asset_id", "id"], "--"))}
                                                </span>
                                            </td>

                                            <td>
                                                ${escapeHTML(firstDefined(row, ["asset_type", "type"], "--"))}
                                            </td>

                                            <td>
                                                ${escapeHTML(firstDefined(row, ["building_name", "building"], "--"))}
                                            </td>

                                            <td>
                                                ${numberValue(health, 1)} / 100
                                            </td>

                                            <td>
                                                <span class="status-badge ${statusClass(status)}">
                                                    ${escapeHTML(status)}
                                                </span>
                                            </td>

                                            <td>
                                                ${
                                                    risk === null
                                                        ? "--"
                                                        : (
                                                            row.maintenance_probability_percent !== undefined
                                                                ? numberValue(risk, 2) + "%"
                                                                : percentValue(risk)
                                                        )
                                                }
                                            </td>

                                        </tr>
                                    `;

                                }
                            )
                            .join("")
                    }

                </tbody>

            </table>
        `;

    } catch (error) {

        showError(
            "equipmentHealthTable",
            "Unable to load equipment health scores."
        );

    }

}


function drawMaintenanceHealthChart(rows) {

    const element =
        document.getElementById(
            "maintenanceHealthChart"
        );

    if (
        !element ||
        typeof Plotly === "undefined"
    ) {
        return;
    }

    const names =
        rows.map(
            row =>
                firstDefined(
                    row,
                    [
                        "asset_name",
                        "asset_id",
                        "name"
                    ],
                    "Asset"
                )
        );

    const scores =
        rows.map(
            row =>
                Number(
                    firstDefined(
                        row,
                        [
                            "equipment_health_score",
                            "health_score",
                            "score"
                        ],
                        0
                    )
                )
        );

    const layout =
        commonLayout();

    layout.height = 350;
    layout.showlegend = false;

    layout.yaxis = {
        ...layout.yaxis,
        title: "Health Score",
        range: [0, 100]
    };

    Plotly.react(
        element,
        [
            {
                x: names,
                y: scores,
                type: "bar",

                marker: {
                    color:
                        COLORS.teal
                }
            }
        ],
        layout,
        plotConfig
    );

}


async function loadMaintenanceBuildingComparison() {

    try {

        const response =
            await getJSON(
                buildURL(
                    "/api/maintenance/building-comparison"
                )
            );

        const rows =
            extractArray(
                response,
                [
                    "buildings",
                    "comparison",
                    "data",
                    "records",
                    "items"
                ]
            );

        const element =
            document.getElementById(
                "maintenanceBuildingChart"
            );

        if (
            !element ||
            typeof Plotly === "undefined"
        ) {
            return;
        }

        const names =
            rows.map(
                row =>
                    firstDefined(
                        row,
                        [
                            "building_name",
                            "building",
                            "name"
                        ],
                        "Building"
                    )
            );

        const scores =
            rows.map(
                row =>
                    Number(
                        firstDefined(
                            row,
                            [
                                "average_health_score",
                                "health_score",
                                "average_health"
                            ],
                            0
                        )
                    )
            );

        const layout =
            commonLayout();

        layout.height = 350;
        layout.showlegend = false;

        layout.yaxis = {
            ...layout.yaxis,
            title: "Average Health",
            range: [0, 100]
        };

        Plotly.react(
            element,
            [
                {
                    x: names,
                    y: scores,
                    type: "bar",

                    marker: {
                        color:
                            COLORS.hvac
                    }
                }
            ],
            layout,
            plotConfig
        );

    } catch (error) {

        console.error(
            "Maintenance building comparison failed:",
            error
        );

    }

}


async function loadMaintenanceSchedule() {

    const container =
        document.getElementById(
            "maintenanceScheduleTable"
        );

    if (!container) {
        return;
    }

    try {

        const response =
            await getJSON(
                buildURL(
                    "/api/maintenance/schedule"
                )
            );

        const rows =
            extractArray(
                response,
                [
                    "schedule",
                    "assets",
                    "data",
                    "records",
                    "items"
                ]
            );

        if (!rows.length) {

            showEmpty(
                "maintenanceScheduleTable",
                "No Maintenance Schedule",
                "No maintenance schedule is currently available."
            );

            return;

        }

        container.innerHTML = `
            <table class="data-table">

                <thead>
                    <tr>
                        <th>Asset</th>
                        <th>Health</th>
                        <th>Risk</th>
                        <th>Priority</th>
                        <th>Recommended Service</th>
                        <th>Reason</th>
                    </tr>
                </thead>

                <tbody>

                    ${
                        rows
                            .map(
                                row => {

                                    const priority =
                                        normalizeStatus(
                                            firstDefined(
                                                row,
                                                [
                                                    "priority",
                                                    "maintenance_priority"
                                                ],
                                                "LOW"
                                            )
                                        );

                                    const risk =
                                        firstDefined(
                                            row,
                                            [
                                                "maintenance_probability_percent",
                                                "maintenance_probability",
                                                "maintenance_risk",
                                                "probability"
                                            ],
                                            null
                                        );

                                    return `
                                        <tr>

                                            <td>
                                                <span class="asset-name">
                                                    ${escapeHTML(firstDefined(row, ["asset_name", "name"], "Equipment"))}
                                                </span>

                                                <span class="sub-text">
                                                    ${escapeHTML(firstDefined(row, ["asset_id", "id"], "--"))}
                                                </span>
                                            </td>

                                            <td>
                                                ${numberValue(firstDefined(row, ["equipment_health_score", "health_score"], null), 1)}
                                            </td>

                                            <td>
                                                ${
                                                    risk === null
                                                        ? "--"
                                                        : (
                                                            row.maintenance_probability_percent !== undefined
                                                                ? numberValue(risk, 2) + "%"
                                                                : percentValue(risk)
                                                        )
                                                }
                                            </td>

                                            <td>
                                                <span class="priority-badge ${priorityClass(priority)}">
                                                    ${escapeHTML(priority)}
                                                </span>
                                            </td>

                                            <td>
                                                ${escapeHTML(
                                                    dateValue(
                                                        firstDefined(
                                                            row,
                                                            [
                                                                "recommended_maintenance_date",
                                                                "recommended_service_date",
                                                                "scheduled_date",
                                                                "maintenance_date",
                                                                "service_date",
                                                                "due_date"
                                                            ],
                                                            ""
                                                        )
                                                    )
                                                )}
                                            </td>

                                            <td>
                                                ${escapeHTML(firstDefined(row, ["reason", "message", "recommendation"], "Scheduled equipment service"))}
                                            </td>

                                        </tr>
                                    `;

                                }
                            )
                            .join("")
                    }

                </tbody>

            </table>
        `;

    } catch (error) {

        showError(
            "maintenanceScheduleTable",
            "Unable to load the maintenance schedule."
        );

    }

}


async function loadMaintenanceAlerts() {

    try {

        const response =
            await getJSON(
                buildURL(
                    "/api/maintenance/alerts"
                )
            );

        const alerts =
            extractArray(
                response,
                [
                    "alerts",
                    "data",
                    "records",
                    "items"
                ]
            );

        renderAlertCards(
            "maintenanceAlerts",
            alerts,
            "No Maintenance Alerts",
            "No active equipment maintenance alerts are currently stored."
        );

    } catch (error) {

        showError(
            "maintenanceAlerts",
            "Unable to load maintenance alerts."
        );

    }

}


async function loadMaintenanceWorkOrders() {

    const container =
        document.getElementById(
            "maintenanceWorkOrders"
        );

    if (!container) {
        return;
    }

    try {

        const response =
            await getJSON(
                buildURL(
                    "/api/maintenance/work-orders"
                )
            );

        const orders =
            extractArray(
                response,
                [
                    "work_orders",
                    "orders",
                    "data",
                    "records",
                    "items"
                ]
            );

        if (!orders.length) {

            showEmpty(
                "maintenanceWorkOrders",
                "No Work Orders",
                "No maintenance work orders are currently stored."
            );

            return;

        }

        container.innerHTML =
            orders
                .slice(0, 30)
                .map(
                    order => {

                        const priority =
                            normalizeStatus(
                                firstDefined(
                                    order,
                                    [
                                        "priority",
                                        "severity"
                                    ],
                                    "LOW"
                                )
                            );

                        return `
                            <article class="work-order-card">

                                <div class="card-topline">

                                    <h3 class="card-title">
                                        ${escapeHTML(firstDefined(order, ["asset_name", "title"], "Equipment Work Order"))}
                                    </h3>

                                    <span class="priority-badge ${priorityClass(priority)}">
                                        ${escapeHTML(priority)}
                                    </span>

                                </div>

                                <div class="card-meta">
                                    ${escapeHTML(firstDefined(order, ["asset_id"], "Equipment"))}
                                    · Status:
                                    ${escapeHTML(firstDefined(order, ["status", "work_order_status"], "OPEN"))}
                                </div>

                                <p class="card-message">
                                    ${escapeHTML(firstDefined(order, ["description", "message", "recommended_action", "recommendation"], "Perform recommended equipment maintenance."))}
                                </p>

                            </article>
                        `;

                    }
                )
                .join("");

    } catch (error) {

        showError(
            "maintenanceWorkOrders",
            "Unable to load maintenance work orders."
        );

    }

}


/* ============================================================
   OCCUPANCY SUMMARY
   ============================================================ */

async function loadOccupancySummary() {

    try {

        const data =
            await getJSON(
                "/api/occupancy/summary"
            );

        setText(
            "occupancySpacesMetric",
            integerValue(
                data.spaces_monitored
            )
        );

        setText(
            "occupancyCurrentMetric",
            integerValue(
                data.current_occupancy
            )
        );

        setText(
            "currentOccupancyOverviewMetric",
            integerValue(
                data.current_occupancy
            )
        );

        setText(
            "occupancyCapacityMetric",
            integerValue(
                data.total_capacity
            )
        );

        setText(
            "occupancyUtilizationMetric",
            percentValue(
                data.current_utilization_percent
            )
        );

        setText(
            "occupancyUnderusedMetric",
            integerValue(
                data.underused_spaces
            )
        );

        setText(
            "occupancyOvercrowdedMetric",
            integerValue(
                data.overcrowded_spaces
            )
        );

    } catch (error) {

        console.error(
            "Occupancy summary failed:",
            error
        );

    }

}


/* ============================================================
   CURRENT OCCUPANCY
   ============================================================ */

async function loadCurrentOccupancy() {

    const container =
        document.getElementById(
            "occupancySpacesTable"
        );

    if (!container) {
        return;
    }

    try {

        const response =
            await getJSON(
                "/api/occupancy/spaces"
            );

        const rows =
            extractArray(
                response,
                [
                    "spaces",
                    "occupancy",
                    "records",
                    "data",
                    "items"
                ]
            );

        if (!rows.length) {

            showEmpty(
                "occupancySpacesTable",
                "No Occupancy Data",
                "No current space occupancy readings are available."
            );

            return;

        }

        container.innerHTML = `
            <table class="data-table">

                <thead>
                    <tr>
                        <th>Space</th>
                        <th>Building</th>
                        <th>Type</th>
                        <th>Occupancy</th>
                        <th>Capacity</th>
                        <th>Utilization</th>
                        <th>Status</th>
                    </tr>
                </thead>

                <tbody>

                    ${
                        rows
                            .map(
                                row => {

                                    const status =
                                        normalizeStatus(
                                            firstDefined(
                                                row,
                                                [
                                                    "occupancy_status",
                                                    "utilization_status",
                                                    "status"
                                                ],
                                                "NORMAL"
                                            )
                                        );

                                    const occupancy =
                                        firstDefined(
                                            row,
                                            [
                                                "occupancy",
                                                "current_occupancy",
                                                "occupancy_count",
                                                "people_count"
                                            ],
                                            0
                                        );

                                    const capacity =
                                        firstDefined(
                                            row,
                                            [
                                                "capacity",
                                                "max_capacity"
                                            ],
                                            0
                                        );

                                    const utilization =
                                        firstDefined(
                                            row,
                                            [
                                                "utilization_percent",
                                                "occupancy_percent",
                                                "utilization"
                                            ],
                                            0
                                        );

                                    return `
                                        <tr>

                                            <td>
                                                <span class="asset-name">
                                                    ${escapeHTML(firstDefined(row, ["space_name", "room_name", "name"], "Space"))}
                                                </span>

                                                <span class="sub-text">
                                                    ${escapeHTML(firstDefined(row, ["space_id", "room_id", "id"], "--"))}
                                                </span>
                                            </td>

                                            <td>
                                                ${escapeHTML(firstDefined(row, ["building_name", "building"], "--"))}

                                                <span class="sub-text">
                                                    ${escapeHTML(firstDefined(row, ["block_name", "block"], ""))}
                                                </span>
                                            </td>

                                            <td>
                                                ${escapeHTML(firstDefined(row, ["space_type", "room_type", "type"], "--"))}
                                            </td>

                                            <td>
                                                ${integerValue(occupancy)}
                                            </td>

                                            <td>
                                                ${integerValue(capacity)}
                                            </td>

                                            <td>
                                                ${percentValue(utilization)}
                                            </td>

                                            <td>
                                                <span class="status-badge ${statusClass(status)}">
                                                    ${escapeHTML(status)}
                                                </span>
                                            </td>

                                        </tr>
                                    `;

                                }
                            )
                            .join("")
                    }

                </tbody>

            </table>
        `;

    } catch (error) {

        showError(
            "occupancySpacesTable",
            "Unable to load current occupancy."
        );

    }

}


/* ============================================================
   OCCUPANCY HOURLY PATTERN
   ============================================================ */

async function loadOccupancyHourlyPattern() {

    try {

        const response =
            await getJSON(
                "/api/occupancy/hourly-pattern"
            );

        const rows =
            extractArray(
                response,
                [
                    "hourly_pattern",
                    "pattern",
                    "hours",
                    "data",
                    "records"
                ]
            );

        const element =
            document.getElementById(
                "occupancyHourlyChart"
            );

        if (
            !element ||
            typeof Plotly === "undefined"
        ) {
            return;
        }

        const hours =
            rows.map(
                row =>
                    firstDefined(
                        row,
                        [
                            "hour",
                            "hour_label",
                            "time"
                        ],
                        ""
                    )
            );

        const utilization =
            rows.map(
                row =>
                    Number(
                        firstDefined(
                            row,
                            [
                                "average_utilization_percent",
                                "utilization_percent",
                                "average_utilization",
                                "occupancy_percent",
                                "utilization"
                            ],
                            0
                        )
                    )
            );

        const layout =
            commonLayout();

        layout.height = 350;
        layout.showlegend = false;

        layout.yaxis = {
            ...layout.yaxis,
            title: "Utilization %"
        };

        Plotly.react(
            element,
            [
                {
                    x: hours,
                    y: utilization,
                    type: "scatter",
                    mode: "lines+markers",

                    line: {
                        color:
                            COLORS.teal,
                        width: 2
                    },

                    marker: {
                        color:
                            COLORS.teal,
                        size: 6
                    }
                }
            ],
            layout,
            plotConfig
        );

    } catch (error) {

        console.error(
            "Occupancy hourly pattern failed:",
            error
        );

    }

}


/* ============================================================
   BUILDING OCCUPANCY
   ============================================================ */

async function loadOccupancyBuildings() {

    try {

        const response =
            await getJSON(
                "/api/occupancy/buildings"
            );

        const rows =
            extractArray(
                response,
                [
                    "buildings",
                    "comparison",
                    "data",
                    "records"
                ]
            );

        const element =
            document.getElementById(
                "occupancyBuildingChart"
            );

        if (
            !element ||
            typeof Plotly === "undefined"
        ) {
            return;
        }

        const names =
            rows.map(
                row =>
                    firstDefined(
                        row,
                        [
                            "building_name",
                            "building",
                            "name"
                        ],
                        "Building"
                    )
            );

        const values =
            rows.map(
                row =>
                    Number(
                        firstDefined(
                            row,
                            [
                                "average_utilization_percent",
                                "utilization_percent",
                                "average_utilization",
                                "current_utilization_percent"
                            ],
                            0
                        )
                    )
            );

        const layout =
            commonLayout();

        layout.height = 350;
        layout.showlegend = false;

        layout.yaxis = {
            ...layout.yaxis,
            title: "Utilization %"
        };

        Plotly.react(
            element,
            [
                {
                    x: names,
                    y: values,
                    type: "bar",

                    marker: {
                        color:
                            COLORS.teal
                    }
                }
            ],
            layout,
            plotConfig
        );

    } catch (error) {

        console.error(
            "Building occupancy failed:",
            error
        );

    }

}


/* ============================================================
   SPACE UTILIZATION
   ============================================================ */

async function loadSpaceUtilization() {

    try {

        const response =
            await getJSON(
                "/api/occupancy/utilization"
            );

        const rows =
            extractArray(
                response,
                [
                    "spaces",
                    "utilization",
                    "data",
                    "records"
                ]
            );

        const element =
            document.getElementById(
                "spaceUtilizationChart"
            );

        if (
            !element ||
            typeof Plotly === "undefined"
        ) {
            return;
        }

        const names =
            rows.map(
                row =>
                    firstDefined(
                        row,
                        [
                            "space_name",
                            "room_name",
                            "name",
                            "space_id"
                        ],
                        "Space"
                    )
            );

        const values =
            rows.map(
                row =>
                    Number(
                        firstDefined(
                            row,
                            [
                                "average_utilization_percent",
                                "utilization_percent",
                                "average_utilization",
                                "utilization"
                            ],
                            0
                        )
                    )
            );

        const layout =
            commonLayout();

        layout.height = 350;
        layout.showlegend = false;

        layout.yaxis = {
            ...layout.yaxis,
            title: "Utilization %"
        };

        Plotly.react(
            element,
            [
                {
                    x: names,
                    y: values,
                    type: "bar",

                    marker: {
                        color:
                            COLORS.hvac
                    }
                }
            ],
            layout,
            plotConfig
        );

    } catch (error) {

        console.error(
            "Space utilization failed:",
            error
        );

    }

}


/* ============================================================
   PEAK HOURS
   ============================================================ */

async function loadPeakHours() {

    try {

        const response =
            await getJSON(
                "/api/occupancy/peak-hours"
            );

        const rows =
            extractArray(
                response,
                [
                    "peak_hours",
                    "hours",
                    "data",
                    "records"
                ]
            );

        const element =
            document.getElementById(
                "peakHoursChart"
            );

        if (
            !element ||
            typeof Plotly === "undefined"
        ) {
            return;
        }

        const hours =
            rows.map(
                row =>
                    firstDefined(
                        row,
                        [
                            "hour",
                            "hour_label",
                            "time"
                        ],
                        ""
                    )
            );

        const values =
            rows.map(
                row =>
                    Number(
                        firstDefined(
                            row,
                            [
                                "average_utilization_percent",
                                "utilization_percent",
                                "average_utilization",
                                "utilization"
                            ],
                            0
                        )
                    )
            );

        const layout =
            commonLayout();

        layout.height = 350;
        layout.showlegend = false;

        layout.yaxis = {
            ...layout.yaxis,
            title: "Utilization %"
        };

        Plotly.react(
            element,
            [
                {
                    x: hours,
                    y: values,
                    type: "bar",

                    marker: {
                        color:
                            COLORS.teal
                    }
                }
            ],
            layout,
            plotConfig
        );

    } catch (error) {

        console.error(
            "Peak occupancy hours failed:",
            error
        );

    }

}


/* ============================================================
   OCCUPANCY HEATMAP
   ============================================================ */

async function loadOccupancyHeatmap() {

    try {

        const response =
            await getJSON(
                "/api/occupancy/heatmap"
            );

        const rows =
            extractArray(
                response,
                [
                    "heatmap",
                    "data",
                    "records",
                    "items"
                ]
            );

        const element =
            document.getElementById(
                "occupancyHeatmapChart"
            );

        if (
            !element ||
            typeof Plotly === "undefined"
        ) {
            return;
        }

        if (!rows.length) {

            Plotly.purge(
                element
            );

            return;
        }

        const spaces =
            [
                ...new Set(
                    rows.map(
                        row =>
                            firstDefined(
                                row,
                                [
                                    "space_name",
                                    "space_id",
                                    "room_name"
                                ],
                                "Space"
                            )
                    )
                )
            ];

        const hours =
            [
                ...new Set(
                    rows.map(
                        row =>
                            firstDefined(
                                row,
                                [
                                    "hour",
                                    "hour_label"
                                ],
                                ""
                            )
                    )
                )
            ];

        const z =
            spaces.map(
                space =>
                    hours.map(
                        hour => {

                            const match =
                                rows.find(
                                    row =>
                                        String(
                                            firstDefined(
                                                row,
                                                [
                                                    "space_name",
                                                    "space_id",
                                                    "room_name"
                                                ],
                                                "Space"
                                            )
                                        ) === String(space) &&
                                        String(
                                            firstDefined(
                                                row,
                                                [
                                                    "hour",
                                                    "hour_label"
                                                ],
                                                ""
                                            )
                                        ) === String(hour)
                                );

                            return match
                                ? Number(
                                    firstDefined(
                                        match,
                                        [
                                            "average_utilization_percent",
                                            "utilization_percent",
                                            "utilization",
                                            "value"
                                        ],
                                        0
                                    )
                                )
                                : 0;

                        }
                    )
            );

        const layout =
            commonLayout();

        layout.height = 420;

        layout.xaxis = {
            ...layout.xaxis,
            title: "Hour"
        };

        layout.yaxis = {
            ...layout.yaxis,
            title: "Space"
        };

        Plotly.react(
            element,
            [
                {
                    x: hours,
                    y: spaces,
                    z: z,
                    type: "heatmap",

                    colorscale: [
                        [0, "#101C1C"],
                        [0.5, "#4B5D5C"],
                        [1, "#2DD4BF"]
                    ],

                    hovertemplate:
                        "%{y}<br>Hour: %{x}<br>Utilization: %{z:.1f}%<extra></extra>"
                }
            ],
            layout,
            plotConfig
        );

    } catch (error) {

        console.error(
            "Occupancy heatmap failed:",
            error
        );

    }

}


/* ============================================================
   UNDERUSED SPACES
   ============================================================ */

async function loadUnderusedSpaces() {

    const container =
        document.getElementById(
            "underusedSpaces"
        );

    if (!container) {
        return;
    }

    try {

        const response =
            await getJSON(
                "/api/occupancy/underused"
            );

        const rows =
            extractArray(
                response,
                [
                    "spaces",
                    "underused_spaces",
                    "data",
                    "records"
                ]
            );

        if (!rows.length) {

            showEmpty(
                "underusedSpaces",
                "No Underused Spaces",
                "No spaces are currently classified as underused."
            );

            return;

        }

        container.innerHTML =
            rows
                .slice(0, 20)
                .map(
                    row => `
                        <article class="issue-card">

                            <div class="card-topline">

                                <h3 class="card-title">
                                    ${escapeHTML(firstDefined(row, ["space_name", "room_name", "name"], "Space"))}
                                </h3>

                                <span class="priority-badge priority-low">
                                    UNDERUSED
                                </span>

                            </div>

                            <div class="card-meta">
                                ${escapeHTML(firstDefined(row, ["building_name", "building"], "--"))}
                                · Capacity:
                                ${integerValue(firstDefined(row, ["capacity", "max_capacity"], 0))}
                            </div>

                            <p class="card-message">
                                Average utilization:
                                ${percentValue(firstDefined(row, ["average_utilization_percent", "utilization_percent", "utilization"], 0))}
                            </p>

                        </article>
                    `
                )
                .join("");

    } catch (error) {

        showError(
            "underusedSpaces",
            "Unable to load underused spaces."
        );

    }

}


/* ============================================================
   OVERCROWDING EVENTS
   ============================================================ */

async function loadOvercrowdingEvents() {

    const container =
        document.getElementById(
            "overcrowdingEvents"
        );

    if (!container) {
        return;
    }

    try {

        const response =
            await getJSON(
                "/api/occupancy/overcrowding?limit=20"
            );

        const rows =
            extractArray(
                response,
                [
                    "events",
                    "overcrowding_events",
                    "data",
                    "records"
                ]
            );

        if (!rows.length) {

            showEmpty(
                "overcrowdingEvents",
                "No Recent Overcrowding",
                "No recent overcrowding events are available."
            );

            return;

        }

        container.innerHTML =
            rows
                .slice(0, 20)
                .map(
                    row => `
                        <article class="issue-card">

                            <div class="card-topline">

                                <h3 class="card-title">
                                    ${escapeHTML(firstDefined(row, ["space_name", "room_name", "name"], "Overcrowding Event"))}
                                </h3>

                                <span class="priority-badge priority-high">
                                    OVERCROWDED
                                </span>

                            </div>

                            <div class="card-meta">
                                ${escapeHTML(firstDefined(row, ["building_name", "building"], "--"))}
                                ·
                                ${escapeHTML(timestampValue(firstDefined(row, ["timestamp", "detected_at"], "")))}
                            </div>

                            <p class="card-message">
                                Occupancy:
                                ${integerValue(firstDefined(row, ["occupancy", "occupancy_count", "current_occupancy"], 0))}
                                · Capacity:
                                ${integerValue(firstDefined(row, ["capacity", "max_capacity"], 0))}
                            </p>

                        </article>
                    `
                )
                .join("");

    } catch (error) {

        showError(
            "overcrowdingEvents",
            "Unable to load overcrowding events."
        );

    }

}


/* ============================================================
   OCCUPANCY INSIGHTS
   ============================================================ */

async function loadOccupancyInsights() {

    const container =
        document.getElementById(
            "occupancyInsights"
        );

    if (!container) {
        return;
    }

    try {

        const response =
            await getJSON(
                "/api/occupancy/insights"
            );

        const insights =
            extractArray(
                response,
                [
                    "insights",
                    "recommendations",
                    "data",
                    "items"
                ]
            );

        if (!insights.length) {

            showEmpty(
                "occupancyInsights",
                "No Occupancy Insights",
                "No occupancy recommendations are currently available."
            );

            return;

        }

        container.innerHTML =
            insights
                .slice(0, 20)
                .map(
                    insight => {

                        const text =
                            typeof insight === "string"
                                ? insight
                                : firstDefined(
                                    insight,
                                    [
                                        "message",
                                        "insight",
                                        "recommendation",
                                        "description",
                                        "title"
                                    ],
                                    "Occupancy insight"
                                );

                        return `
                            <article class="recommendation-card">
                                <div class="card-topline">
                                    <h3 class="card-title">
                                        Occupancy Insight
                                    </h3>
                                </div>

                                <p class="card-message">
                                    ${escapeHTML(text)}
                                </p>
                            </article>
                        `;

                    }
                )
                .join("");

    } catch (error) {

        showError(
            "occupancyInsights",
            "Unable to load occupancy insights."
        );

    }

}


/* ============================================================
   OCCUPANCY ALERTS
   ============================================================ */

async function loadOccupancyAlerts() {

    try {

        const response =
            await getJSON(
                "/api/occupancy/alerts?limit=30"
            );

        const alerts =
            extractArray(
                response,
                [
                    "alerts",
                    "data",
                    "records",
                    "items"
                ]
            );

        renderAlertCards(
            "occupancyAlerts",
            alerts,
            "No Occupancy Alerts",
            "No active occupancy alerts are currently stored."
        );

    } catch (error) {

        showError(
            "occupancyAlerts",
            "Unable to load occupancy alerts."
        );

    }

}


/* ============================================================
   SECURITY SUMMARY
   ============================================================ */

async function loadSecuritySummary() {

    try {

        const data =
            await getJSON(
                "/api/security/summary"
            );

        setText(
            "securityEventsMetric",
            integerValue(
                data.total_events
            )
        );

        setText(
            "securityGrantedMetric",
            integerValue(
                data.granted_access
            )
        );

        setText(
            "securityDeniedMetric",
            integerValue(
                data.denied_access
            )
        );

        setText(
            "securityUnauthorizedMetric",
            integerValue(
                data.unauthorized_attempts
            )
        );

        setText(
            "unauthorizedOverviewMetric",
            integerValue(
                data.unauthorized_attempts
            )
        );

        setText(
            "securityAfterHoursMetric",
            integerValue(
                data.after_hours_events
            )
        );

        setText(
            "securityAlertsMetric",
            integerValue(
                data.security_alerts
            )
        );

    } catch (error) {

        console.error(
            "Security summary failed:",
            error
        );

    }

}


/* ============================================================
   SECURITY ACCESS POINTS
   ============================================================ */

async function loadSecurityAccessPoints() {

    try {

        const response =
            await getJSON(
                "/api/security/access-points"
            );

        const rows =
            extractArray(
                response,
                [
                    "access_points",
                    "points",
                    "data",
                    "records"
                ]
            );

        const element =
            document.getElementById(
                "securityAccessPointChart"
            );

        if (
            !element ||
            typeof Plotly === "undefined"
        ) {
            return;
        }

        const names =
            rows.map(
                row =>
                    firstDefined(
                        row,
                        [
                            "access_point_name",
                            "access_point_id",
                            "name"
                        ],
                        "Access Point"
                    )
            );

        const values =
            rows.map(
                row =>
                    Number(
                        firstDefined(
                            row,
                            [
                                "total_events",
                                "event_count",
                                "events",
                                "access_count"
                            ],
                            0
                        )
                    )
            );

        const layout =
            commonLayout();

        layout.height = 350;
        layout.showlegend = false;

        layout.yaxis = {
            ...layout.yaxis,
            title: "Events"
        };

        Plotly.react(
            element,
            [
                {
                    x: names,
                    y: values,
                    type: "bar",

                    marker: {
                        color:
                            COLORS.teal
                    }
                }
            ],
            layout,
            plotConfig
        );

    } catch (error) {

        console.error(
            "Security access point analysis failed:",
            error
        );

    }

}


/* ============================================================
   SECURITY HOURLY PATTERN
   ============================================================ */

async function loadSecurityHourlyPattern() {

    try {

        const response =
            await getJSON(
                "/api/security/hourly-pattern"
            );

        const rows =
            extractArray(
                response,
                [
                    "hourly_pattern",
                    "hours",
                    "pattern",
                    "data",
                    "records"
                ]
            );

        const element =
            document.getElementById(
                "securityHourlyChart"
            );

        if (
            !element ||
            typeof Plotly === "undefined"
        ) {
            return;
        }

        const hours =
            rows.map(
                row =>
                    firstDefined(
                        row,
                        [
                            "hour",
                            "hour_label",
                            "time"
                        ],
                        ""
                    )
            );

        const events =
            rows.map(
                row =>
                    Number(
                        firstDefined(
                            row,
                            [
                                "total_events",
                                "event_count",
                                "events",
                                "count"
                            ],
                            0
                        )
                    )
            );

        const layout =
            commonLayout();

        layout.height = 350;
        layout.showlegend = false;

        layout.yaxis = {
            ...layout.yaxis,
            title: "Security Events"
        };

        Plotly.react(
            element,
            [
                {
                    x: hours,
                    y: events,
                    type: "scatter",
                    mode: "lines+markers",

                    line: {
                        color:
                            COLORS.teal,
                        width: 2
                    },

                    marker: {
                        color:
                            COLORS.teal,
                        size: 6
                    }
                }
            ],
            layout,
            plotConfig
        );

    } catch (error) {

        console.error(
            "Security hourly pattern failed:",
            error
        );

    }

}


/* ============================================================
   SECURITY EVENTS
   ============================================================ */

async function loadSecurityEvents() {

    const container =
        document.getElementById(
            "securityEventsTable"
        );

    if (!container) {
        return;
    }

    try {

        const response =
            await getJSON(
                "/api/security/events?limit=30"
            );

        const rows =
            extractArray(
                response,
                [
                    "events",
                    "security_events",
                    "data",
                    "records"
                ]
            );

        if (!rows.length) {

            showEmpty(
                "securityEventsTable",
                "No Security Events",
                "No recent security events are available."
            );

            return;

        }

        container.innerHTML = `
            <table class="data-table">

                <thead>
                    <tr>
                        <th>Event</th>
                        <th>Access Point</th>
                        <th>Person</th>
                        <th>Access</th>
                        <th>Severity</th>
                        <th>Time</th>
                    </tr>
                </thead>

                <tbody>

                    ${
                        rows
                            .map(
                                row => {

                                    const severity =
                                        normalizeStatus(
                                            firstDefined(
                                                row,
                                                [
                                                    "severity",
                                                    "risk_level"
                                                ],
                                                "NORMAL"
                                            )
                                        );

                                    const access =
                                        normalizeStatus(
                                            firstDefined(
                                                row,
                                                [
                                                    "access_status",
                                                    "access_result",
                                                    "result",
                                                    "status"
                                                ],
                                                "--"
                                            )
                                        );

                                    return `
                                        <tr>

                                            <td>
                                                <span class="asset-name">
                                                    ${escapeHTML(firstDefined(row, ["event_type", "event_name", "type"], "Access Event"))}
                                                </span>

                                                <span class="sub-text">
                                                    ${escapeHTML(firstDefined(row, ["event_id", "id"], "--"))}
                                                </span>
                                            </td>

                                            <td>
                                                ${escapeHTML(firstDefined(row, ["access_point_name", "access_point_id"], "--"))}

                                                <span class="sub-text">
                                                    ${escapeHTML(firstDefined(row, ["building_name", "building"], ""))}
                                                </span>
                                            </td>

                                            <td>
                                                ${escapeHTML(firstDefined(row, ["person_name", "person_id", "visitor_id", "user_id"], "--"))}
                                            </td>

                                            <td>
                                                <span class="status-badge ${statusClass(access)}">
                                                    ${escapeHTML(access)}
                                                </span>
                                            </td>

                                            <td>
                                                <span class="priority-badge ${priorityClass(severity)}">
                                                    ${escapeHTML(severity)}
                                                </span>
                                            </td>

                                            <td>
                                                ${escapeHTML(timestampValue(firstDefined(row, ["timestamp", "event_timestamp", "created_at"], "")))}
                                            </td>

                                        </tr>
                                    `;

                                }
                            )
                            .join("")
                    }

                </tbody>

            </table>
        `;

    } catch (error) {

        showError(
            "securityEventsTable",
            "Unable to load security events."
        );

    }

}


/* ============================================================
   UNAUTHORIZED EVENTS
   ============================================================ */

async function loadUnauthorizedEvents() {

    const container =
        document.getElementById(
            "unauthorizedEvents"
        );

    if (!container) {
        return;
    }

    try {

        const response =
            await getJSON(
                "/api/security/unauthorized?limit=20"
            );

        const rows =
            extractArray(
                response,
                [
                    "events",
                    "unauthorized_events",
                    "data",
                    "records"
                ]
            );

        if (!rows.length) {

            showEmpty(
                "unauthorizedEvents",
                "No Unauthorized Attempts",
                "No recent unauthorized access attempts are available."
            );

            return;

        }

        container.innerHTML =
            rows
                .slice(0, 20)
                .map(
                    row => {

                        const severity =
                            normalizeStatus(
                                firstDefined(
                                    row,
                                    [
                                        "severity",
                                        "risk_level"
                                    ],
                                    "HIGH"
                                )
                            );

                        return `
                            <article class="issue-card">

                                <div class="card-topline">

                                    <h3 class="card-title">
                                        ${escapeHTML(firstDefined(row, ["event_type", "event_name"], "Unauthorized Access"))}
                                    </h3>

                                    <span class="priority-badge ${priorityClass(severity)}">
                                        ${escapeHTML(severity)}
                                    </span>

                                </div>

                                <div class="card-meta">
                                    ${escapeHTML(firstDefined(row, ["access_point_name", "access_point_id"], "--"))}
                                    ·
                                    ${escapeHTML(firstDefined(row, ["building_name", "building"], "--"))}
                                </div>

                                <p class="card-message">
                                    ${escapeHTML(timestampValue(firstDefined(row, ["timestamp", "event_timestamp"], "")))}
                                </p>

                            </article>
                        `;

                    }
                )
                .join("");

    } catch (error) {

        showError(
            "unauthorizedEvents",
            "Unable to load unauthorized access events."
        );

    }

}


/* ============================================================
   VISITOR MOVEMENT
   ============================================================ */

async function loadVisitorMovement() {

    const container =
        document.getElementById(
            "visitorMovement"
        );

    if (!container) {
        return;
    }

    try {

        const response =
            await getJSON(
                "/api/security/visitors"
            );

        const rows =
            extractArray(
                response,
                [
                    "visitors",
                    "visitor_movement",
                    "movements",
                    "data",
                    "records"
                ]
            );

        if (!rows.length) {

            showEmpty(
                "visitorMovement",
                "No Visitor Movement",
                "No visitor movement records are currently available."
            );

            return;

        }

        container.innerHTML =
            rows
                .slice(0, 20)
                .map(
                    row => `
                        <article class="recommendation-card">

                            <div class="card-topline">

                                <h3 class="card-title">
                                    ${escapeHTML(firstDefined(row, ["visitor_name", "visitor_id", "person_name"], "Visitor"))}
                                </h3>

                                <span class="priority-badge priority-low">
                                    VISITOR
                                </span>

                            </div>

                            <div class="card-meta">
                                ${escapeHTML(firstDefined(row, ["access_point_name", "access_point_id", "location"], "--"))}
                                ·
                                ${escapeHTML(firstDefined(row, ["building_name", "building"], "--"))}
                            </div>

                            <p class="card-message">
                                ${escapeHTML(timestampValue(firstDefined(row, ["timestamp", "event_timestamp", "last_seen"], "")))}
                            </p>

                        </article>
                    `
                )
                .join("");

    } catch (error) {

        showError(
            "visitorMovement",
            "Unable to load visitor movement."
        );

    }

}


/* ============================================================
   SECURITY INSIGHTS
   ============================================================ */

async function loadSecurityInsights() {

    const container =
        document.getElementById(
            "securityInsights"
        );

    if (!container) {
        return;
    }

    try {

        const response =
            await getJSON(
                "/api/security/insights"
            );

        const insights =
            extractArray(
                response,
                [
                    "insights",
                    "recommendations",
                    "data",
                    "items"
                ]
            );

        if (!insights.length) {

            showEmpty(
                "securityInsights",
                "No Security Insights",
                "No security recommendations are currently available."
            );

            return;

        }

        container.innerHTML =
            insights
                .slice(0, 20)
                .map(
                    insight => {

                        const text =
                            typeof insight === "string"
                                ? insight
                                : firstDefined(
                                    insight,
                                    [
                                        "message",
                                        "insight",
                                        "recommendation",
                                        "description",
                                        "title"
                                    ],
                                    "Security insight"
                                );

                        return `
                            <article class="recommendation-card">

                                <div class="card-topline">

                                    <h3 class="card-title">
                                        Security Insight
                                    </h3>

                                </div>

                                <p class="card-message">
                                    ${escapeHTML(text)}
                                </p>

                            </article>
                        `;

                    }
                )
                .join("");

    } catch (error) {

        showError(
            "securityInsights",
            "Unable to load security insights."
        );

    }

}


/* ============================================================
   SECURITY ISSUE CENTRE
   ============================================================ */

async function loadSecurityIssueCentre() {

    const container =
        document.getElementById(
            "securityIssueCentre"
        );

    if (!container) {
        return;
    }

    try {

        const response =
            await getJSON(
                "/api/security/alert-events?limit=30"
            );

        const rows =
            extractArray(
                response,
                [
                    "events",
                    "alerts",
                    "security_alerts",
                    "data",
                    "records"
                ]
            );

        if (!rows.length) {

            showEmpty(
                "securityIssueCentre",
                "No Security Issues",
                "No recent security issues are available."
            );

            return;

        }

        container.innerHTML =
            rows
                .slice(0, 30)
                .map(
                    row => {

                        const severity =
                            normalizeStatus(
                                firstDefined(
                                    row,
                                    [
                                        "severity",
                                        "priority",
                                        "risk_level"
                                    ],
                                    "MEDIUM"
                                )
                            );

                        return `
                            <article class="issue-card">

                                <div class="card-topline">

                                    <h3 class="card-title">
                                        ${escapeHTML(firstDefined(row, ["event_type", "title", "event_name"], "Security Event"))}
                                    </h3>

                                    <span class="priority-badge ${priorityClass(severity)}">
                                        ${escapeHTML(severity)}
                                    </span>

                                </div>

                                <div class="card-meta">
                                    ${escapeHTML(firstDefined(row, ["access_point_name", "access_point_id"], "--"))}
                                    ·
                                    ${escapeHTML(firstDefined(row, ["building_name", "building"], "--"))}
                                </div>

                                <p class="card-message">
                                    ${escapeHTML(firstDefined(row, ["message", "description"], "Security event requires review."))}
                                </p>

                            </article>
                        `;

                    }
                )
                .join("");

    } catch (error) {

        showError(
            "securityIssueCentre",
            "Unable to load security issues."
        );

    }

}


/* ============================================================
   SECURITY ALERTS
   ============================================================ */

async function loadSecurityAlerts() {

    try {

        let response =
            await getJSON(
                "/api/security/alerts?limit=30"
            );

        let alerts =
            extractArray(
                response,
                [
                    "alerts",
                    "data",
                    "records",
                    "items"
                ]
            );

        /*
         Database alerts can initially be empty.
         Fall back to security alert events so the dashboard
         still presents detected security conditions.
        */

        if (!alerts.length) {

            response =
                await getJSON(
                    "/api/security/alert-events?limit=30"
                );

            alerts =
                extractArray(
                    response,
                    [
                        "events",
                        "alerts",
                        "data",
                        "records"
                    ]
                );

        }

        renderAlertCards(
            "securityAlerts",
            alerts,
            "No Security Alerts",
            "No active security alerts are currently available."
        );

    } catch (error) {

        showError(
            "securityAlerts",
            "Unable to load security alerts."
        );

    }

}


/* ============================================================
   GENERIC ALERT CARD RENDERER
   ============================================================ */

function renderAlertCards(
    elementId,
    alerts,
    emptyTitle,
    emptyMessage
) {

    const container =
        document.getElementById(
            elementId
        );

    if (!container) {
        return;
    }

    if (!alerts.length) {

        showEmpty(
            elementId,
            emptyTitle,
            emptyMessage
        );

        return;

    }

    container.innerHTML =
        alerts
            .slice(0, 30)
            .map(
                alert => {

                    const severity =
                        normalizeStatus(
                            firstDefined(
                                alert,
                                [
                                    "priority",
                                    "severity",
                                    "level",
                                    "risk_level"
                                ],
                                "LOW"
                            )
                        );

                    const title =
                        firstDefined(
                            alert,
                            [
                                "title",
                                "alert_type",
                                "event_type",
                                "asset_name",
                                "space_name",
                                "type"
                            ],
                            "Facility Alert"
                        );

                    const message =
                        firstDefined(
                            alert,
                            [
                                "message",
                                "description",
                                "recommendation",
                                "reason"
                            ],
                            "Facility condition requires review."
                        );

                    const created =
                        firstDefined(
                            alert,
                            [
                                "created_at",
                                "timestamp",
                                "detected_at",
                                "event_timestamp"
                            ],
                            ""
                        );

                    return `
                        <article class="maintenance-alert-card">

                            <div class="card-topline">

                                <h3 class="card-title">
                                    ${escapeHTML(title)}
                                </h3>

                                <span class="priority-badge ${priorityClass(severity)}">
                                    ${escapeHTML(severity)}
                                </span>

                            </div>

                            ${
                                created
                                    ? `
                                        <div class="card-meta">
                                            ${escapeHTML(timestampValue(created))}
                                        </div>
                                    `
                                    : ""
                            }

                            <p class="card-message">
                                ${escapeHTML(message)}
                            </p>

                        </article>
                    `;

                }
            )
            .join("");

}


/* ============================================================
   REFRESH GROUPS
   ============================================================ */

async function refreshEnergyData() {

    await Promise.allSettled(
        [
            loadSummary(),
            loadReadings(),
            loadBuildingComparison(),
            loadStoredIssues(),
            loadConsumptionAlerts()
        ]
    );

}


async function refreshMaintenanceData() {

    await Promise.allSettled(
        [
            loadMaintenanceSummary(),
            loadAssetMonitoring(),
            loadEquipmentHealth(),
            loadMaintenanceBuildingComparison(),
            loadMaintenanceSchedule(),
            loadMaintenanceAlerts(),
            loadMaintenanceWorkOrders()
        ]
    );

}


async function refreshOccupancyData() {

    await Promise.allSettled(
        [
            loadOccupancySummary(),
            loadCurrentOccupancy(),
            loadOccupancyHourlyPattern(),
            loadOccupancyBuildings(),
            loadSpaceUtilization(),
            loadPeakHours(),
            loadOccupancyHeatmap(),
            loadUnderusedSpaces(),
            loadOvercrowdingEvents(),
            loadOccupancyInsights(),
            loadOccupancyAlerts()
        ]
    );

}


async function refreshSecurityData() {

    await Promise.allSettled(
        [
            loadSecuritySummary(),
            loadSecurityAccessPoints(),
            loadSecurityHourlyPattern(),
            loadSecurityEvents(),
            loadUnauthorizedEvents(),
            loadVisitorMovement(),
            loadSecurityInsights(),
            loadSecurityIssueCentre(),
            loadSecurityAlerts()
        ]
    );

}


async function refreshDashboard(
    runAgents = false
) {

    if (runAgents) {

        await Promise.allSettled(
            [
                runEnergyAgent(),
                runMaintenanceAgent()
            ]
        );

    }


    await Promise.allSettled(
        [
            refreshEnergyData(),
            refreshMaintenanceData(),
            refreshOccupancyData(),
            refreshSecurityData()
        ]
    );


    setText(
        "lastUpdated",
        new Date()
            .toLocaleString()
    );

}


/* ============================================================
   CHART RESIZE
   ============================================================ */

function resizeCharts() {

    if (
        typeof Plotly ===
        "undefined"
    ) {
        return;
    }


    [
        "energyChart",
        "hvacChart",
        "occupancyChart",
        "buildingChart",
        "maintenanceHealthChart",
        "maintenanceBuildingChart",
        "occupancyHourlyChart",
        "occupancyBuildingChart",
        "spaceUtilizationChart",
        "peakHoursChart",
        "occupancyHeatmapChart",
        "securityAccessPointChart",
        "securityHourlyChart"
    ].forEach(
        chartId => {

            const element =
                document.getElementById(
                    chartId
                );

            if (
                element &&
                element.data
            ) {

                try {

                    Plotly.Plots.resize(
                        element
                    );

                } catch (error) {

                    console.debug(
                        "Resize skipped:",
                        chartId
                    );

                }

            }

        }
    );

}


/* ============================================================
   FILTER EVENTS
   ============================================================ */

if (buildingSelect) {

    buildingSelect.addEventListener(
        "change",
        async function () {

            await refreshDashboard(
                false
            );

        }
    );

}


if (blockSelect) {

    blockSelect.addEventListener(
        "change",
        async function () {

            await refreshDashboard(
                false
            );

        }
    );

}


/* ============================================================
   INITIALISE
   ============================================================ */

async function initialiseDashboard() {

    try {

        await loadFacility();

        await refreshDashboard(
            true
        );

    } catch (error) {

        console.error(
            "Dashboard initialisation failed:",
            error
        );

    }

}


/* ============================================================
   DOM READY
   ============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        initialiseDashboard();

    }
);


/* ============================================================
   AUTO REFRESH
   ============================================================ */

setInterval(
    function () {

        if (
            document.visibilityState ===
            "visible"
        ) {

            refreshDashboard(
                false
            );

        }

    },
    AUTO_REFRESH_MS
);


/* ============================================================
   WINDOW EVENTS
   ============================================================ */

window.addEventListener(
    "resize",
    function () {

        clearTimeout(
            window.facilityOpsChartResizeTimer
        );

        window.facilityOpsChartResizeTimer =
            setTimeout(
                resizeCharts,
                150
            );

    }
);


document.addEventListener(
    "visibilitychange",
    function () {

        if (
            document.visibilityState ===
            "visible"
        ) {

            refreshDashboard(
                false
            );

        }

    }
);