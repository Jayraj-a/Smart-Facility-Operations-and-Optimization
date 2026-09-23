"use strict";


/* ============================================================
   FACILITYOPS AI
   UNIFIED FACILITY OPERATIONS DASHBOARD

   Energy
   Predictive Maintenance
   Occupancy Intelligence
   Security Intelligence
   Cost Optimization
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


function currencyValue(value) {

    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "₹--";
    }

    return "₹" +
        number.toLocaleString(
            "en-IN",
            {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }
        );

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


/*
    Cost endpoints support the building filter,
    but do not use the Energy/Occupancy block filter.
*/

function costURL(
    path,
    additional = {}
) {

    const parameters =
        new URLSearchParams();

    const building =
        selectedBuilding();

    if (building) {

        parameters.set(
            "building",
            building
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
   GENERIC ALERT RENDERER
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


    if (
        !Array.isArray(alerts) ||
        alerts.length === 0
    ) {

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

                    const priority =
                        normalizeStatus(
                            firstDefined(
                                alert,
                                [
                                    "priority",
                                    "severity",
                                    "risk_level",
                                    "level"
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
                                "type",
                                "issue_type"
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
                                "recommended_action"
                            ],
                            "Facility condition requires review."
                        );


                    const building =
                        firstDefined(
                            alert,
                            [
                                "building_name",
                                "building"
                            ],
                            ""
                        );


                    const timestamp =
                        firstDefined(
                            alert,
                            [
                                "timestamp",
                                "created_at",
                                "detected_at",
                                "alert_timestamp"
                            ],
                            ""
                        );


                    return `
                        <article class="alert-item">

                            <div class="card-topline">

                                <h3 class="card-title">
                                    ${escapeHTML(title)}
                                </h3>

                                <span class="priority-badge ${priorityClass(priority)}">
                                    ${escapeHTML(priority)}
                                </span>

                            </div>

                            ${
                                building || timestamp
                                    ? `
                                        <div class="card-meta">
                                            ${escapeHTML(building)}
                                            ${
                                                timestamp
                                                    ? " · " +
                                                      escapeHTML(
                                                          timestampValue(
                                                              timestamp
                                                          )
                                                      )
                                                    : ""
                                            }
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
   MAINTENANCE AGENT
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


/* ============================================================
   MAINTENANCE SUMMARY
   ============================================================ */

async function loadMaintenanceSummary() {

    try {

        const response =
            await getJSON(
                buildURL(
                    "/api/maintenance/summary"
                )
            );


        const summary =
            response.summary &&
            typeof response.summary === "object"
                ? response.summary
                : response;


        const totalAssets =
            firstDefined(
                summary,
                [
                    "total_assets",
                    "asset_count",
                    "assets"
                ],
                0
            );


        const healthyAssets =
            firstDefined(
                summary,
                [
                    "healthy_assets",
                    "healthy_count",
                    "healthy"
                ],
                0
            );


        const warningAssets =
            firstDefined(
                summary,
                [
                    "warning_assets",
                    "warning_count",
                    "warning"
                ],
                0
            );


        const criticalAssets =
            firstDefined(
                summary,
                [
                    "critical_assets",
                    "critical_count",
                    "critical"
                ],
                0
            );


        const healthScore =
            firstDefined(
                summary,
                [
                    "average_health_score",
                    "avg_health_score",
                    "health_score",
                    "equipment_health_score"
                ],
                0
            );


        const maintenanceDue =
            firstDefined(
                summary,
                [
                    "maintenance_due",
                    "due_maintenance",
                    "maintenance_due_count",
                    "upcoming_maintenance"
                ],
                0
            );


        setText(
            "assetCountMetric",
            integerValue(
                totalAssets
            )
        );


        setText(
            "healthyAssetMetric",
            integerValue(
                healthyAssets
            )
        );


        setText(
            "warningAssetMetric",
            integerValue(
                warningAssets
            )
        );


        setText(
            "criticalAssetMetric",
            integerValue(
                criticalAssets
            )
        );


        setText(
            "equipmentHealthMetric",
            numberValue(
                healthScore,
                1
            )
        );


        setText(
            "maintenanceDueMetric",
            integerValue(
                maintenanceDue
            )
        );

    } catch (error) {

        console.error(
            "Maintenance summary failed:",
            error
        );

    }

}


/* ============================================================
   ASSET MONITORING
   ============================================================ */

async function loadAssetMonitoring() {

    const container =
        document.getElementById(
            "assetMonitoringTable"
        );

    if (!container) {
        return;
    }


    try {

        const response =
            await getJSON(
                buildURL(
                    "/api/maintenance/assets"
                )
            );


        const assets =
            extractArray(
                response,
                [
                    "assets",
                    "data",
                    "records",
                    "items"
                ]
            );


        if (!assets.length) {

            showEmpty(
                "assetMonitoringTable",
                "No Assets",
                "No monitored facility assets are currently available."
            );

            return;

        }


        container.innerHTML = `
            <table class="data-table">

                <thead>
                    <tr>
                        <th>Asset</th>
                        <th>Building</th>
                        <th>Type</th>
                        <th>Health</th>
                        <th>Status</th>
                        <th>Risk</th>
                    </tr>
                </thead>

                <tbody>

                    ${
                        assets
                            .map(
                                asset => {

                                    const name =
                                        firstDefined(
                                            asset,
                                            [
                                                "asset_name",
                                                "name",
                                                "asset_id"
                                            ],
                                            "--"
                                        );


                                    const building =
                                        firstDefined(
                                            asset,
                                            [
                                                "building_name",
                                                "building"
                                            ],
                                            "--"
                                        );


                                    const type =
                                        firstDefined(
                                            asset,
                                            [
                                                "asset_type",
                                                "equipment_type",
                                                "type"
                                            ],
                                            "--"
                                        );


                                    const health =
                                        firstDefined(
                                            asset,
                                            [
                                                "health_score",
                                                "equipment_health_score",
                                                "health"
                                            ],
                                            0
                                        );


                                    const status =
                                        normalizeStatus(
                                            firstDefined(
                                                asset,
                                                [
                                                    "health_status",
                                                    "status",
                                                    "condition"
                                                ],
                                                "NORMAL"
                                            )
                                        );


                                    const risk =
                                        normalizeStatus(
                                            firstDefined(
                                                asset,
                                                [
                                                    "risk_level",
                                                    "maintenance_risk",
                                                    "priority"
                                                ],
                                                "LOW"
                                            )
                                        );


                                    return `
                                        <tr>

                                            <td>
                                                <span class="asset-name">
                                                    ${escapeHTML(name)}
                                                </span>
                                            </td>

                                            <td>
                                                ${escapeHTML(building)}
                                            </td>

                                            <td>
                                                ${escapeHTML(type)}
                                            </td>

                                            <td>
                                                ${numberValue(health, 1)}
                                            </td>

                                            <td>
                                                <span class="status-badge ${statusClass(status)}">
                                                    ${escapeHTML(status)}
                                                </span>
                                            </td>

                                            <td>
                                                <span class="priority-badge ${priorityClass(risk)}">
                                                    ${escapeHTML(risk)}
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

        console.error(
            "Asset monitoring failed:",
            error
        );


        showError(
            "assetMonitoringTable",
            "Unable to load monitored assets."
        );

    }

}


/* ============================================================
   EQUIPMENT HEALTH
   ============================================================ */

async function loadEquipmentHealth() {

    try {

        const response =
            await getJSON(
                buildURL(
                    "/api/maintenance/equipment-health"
                )
            );


        const rows =
            extractArray(
                response,
                [
                    "equipment",
                    "assets",
                    "health",
                    "data",
                    "records",
                    "items"
                ]
            );


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


        if (!rows.length) {

            Plotly.purge(
                element
            );

            return;

        }


        const names =
            rows.map(
                row =>
                    firstDefined(
                        row,
                        [
                            "asset_name",
                            "name",
                            "asset_id"
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
                                "health_score",
                                "equipment_health_score",
                                "score"
                            ],
                            0
                        )
                    )
            );


        const layout =
            commonLayout();


        layout.height = 360;

        layout.showlegend =
            false;


        layout.yaxis = {
            ...layout.yaxis,
            title:
                "Health Score",
            range:
                [0, 100]
        };


        Plotly.react(
            element,
            [
                {
                    x:
                        names,

                    y:
                        scores,

                    type:
                        "bar",

                    marker: {
                        color:
                            COLORS.teal
                    },

                    hovertemplate:
                        "%{x}<br>Health: %{y:.1f}<extra></extra>"
                }
            ],
            layout,
            plotConfig
        );

    } catch (error) {

        console.error(
            "Equipment health failed:",
            error
        );

    }

}


/* ============================================================
   MAINTENANCE BUILDING COMPARISON
   ============================================================ */

async function loadMaintenanceBuildingComparison() {

    try {

        const response =
            await getJSON(
                "/api/maintenance/buildings"
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


        if (!rows.length) {

            Plotly.purge(
                element
            );

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


        const health =
            rows.map(
                row =>
                    Number(
                        firstDefined(
                            row,
                            [
                                "average_health_score",
                                "avg_health_score",
                                "health_score"
                            ],
                            0
                        )
                    )
            );


        const layout =
            commonLayout();


        layout.height = 360;

        layout.showlegend =
            false;


        layout.yaxis = {
            ...layout.yaxis,
            title:
                "Average Health Score",
            range:
                [0, 100]
        };


        Plotly.react(
            element,
            [
                {
                    x:
                        names,

                    y:
                        health,

                    type:
                        "bar",

                    marker: {
                        color:
                            COLORS.hvac
                    },

                    hovertemplate:
                        "%{x}<br>Health: %{y:.1f}<extra></extra>"
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


/* ============================================================
   MAINTENANCE SCHEDULE
   ============================================================ */

async function loadMaintenanceSchedule() {

    const container =
        document.getElementById(
            "maintenanceSchedule"
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
                    "maintenance_schedule",
                    "records",
                    "data",
                    "items"
                ]
            );


        if (!rows.length) {

            showEmpty(
                "maintenanceSchedule",
                "No Scheduled Maintenance",
                "No maintenance activities are currently scheduled."
            );

            return;

        }


        container.innerHTML = `
            <table class="data-table">

                <thead>
                    <tr>
                        <th>Asset</th>
                        <th>Building</th>
                        <th>Maintenance</th>
                        <th>Scheduled Date</th>
                        <th>Priority</th>
                        <th>Status</th>
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
                                                    "risk_level",
                                                    "severity"
                                                ],
                                                "LOW"
                                            )
                                        );


                                    const status =
                                        normalizeStatus(
                                            firstDefined(
                                                row,
                                                [
                                                    "status",
                                                    "work_order_status"
                                                ],
                                                "PENDING"
                                            )
                                        );


                                    return `
                                        <tr>

                                            <td>
                                                <span class="asset-name">
                                                    ${escapeHTML(
                                                        firstDefined(
                                                            row,
                                                            [
                                                                "asset_name",
                                                                "asset_id",
                                                                "name"
                                                            ],
                                                            "--"
                                                        )
                                                    )}
                                                </span>
                                            </td>

                                            <td>
                                                ${escapeHTML(
                                                    firstDefined(
                                                        row,
                                                        [
                                                            "building_name",
                                                            "building"
                                                        ],
                                                        "--"
                                                    )
                                                )}
                                            </td>

                                            <td>
                                                ${escapeHTML(
                                                    firstDefined(
                                                        row,
                                                        [
                                                            "maintenance_type",
                                                            "work_type",
                                                            "recommendation",
                                                            "description"
                                                        ],
                                                        "Preventive Maintenance"
                                                    )
                                                )}
                                            </td>

                                            <td>
                                                ${escapeHTML(
                                                    dateValue(
                                                        firstDefined(
                                                            row,
                                                            [
                                                                "scheduled_date",
                                                                "due_date",
                                                                "maintenance_date"
                                                            ],
                                                            ""
                                                        )
                                                    )
                                                )}
                                            </td>

                                            <td>
                                                <span class="priority-badge ${priorityClass(priority)}">
                                                    ${escapeHTML(priority)}
                                                </span>
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

        console.error(
            "Maintenance schedule failed:",
            error
        );


        showError(
            "maintenanceSchedule",
            "Unable to load the maintenance schedule."
        );

    }

}


/* ============================================================
   MAINTENANCE ALERTS
   ============================================================ */

async function loadMaintenanceAlerts() {

    const container =
        document.getElementById(
            "maintenanceAlerts"
        );


    if (!container) {
        return;
    }


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
            "No active maintenance alerts are currently available."
        );

    } catch (error) {

        showError(
            "maintenanceAlerts",
            "Unable to load maintenance alerts."
        );

    }

}


/* ============================================================
   MAINTENANCE WORK ORDERS
   ============================================================ */

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


        const rows =
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


        if (!rows.length) {

            showEmpty(
                "maintenanceWorkOrders",
                "No Work Orders",
                "No maintenance work orders are currently stored."
            );

            return;

        }


        container.innerHTML = `
            <table class="data-table">

                <thead>
                    <tr>
                        <th>Work Order</th>
                        <th>Asset</th>
                        <th>Building</th>
                        <th>Priority</th>
                        <th>Status</th>
                        <th>Created</th>
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
                                                    "severity"
                                                ],
                                                "LOW"
                                            )
                                        );


                                    const status =
                                        normalizeStatus(
                                            firstDefined(
                                                row,
                                                [
                                                    "status",
                                                    "work_order_status"
                                                ],
                                                "OPEN"
                                            )
                                        );


                                    return `
                                        <tr>

                                            <td>
                                                ${escapeHTML(
                                                    firstDefined(
                                                        row,
                                                        [
                                                            "work_order_id",
                                                            "id"
                                                        ],
                                                        "--"
                                                    )
                                                )}
                                            </td>

                                            <td>
                                                <span class="asset-name">
                                                    ${escapeHTML(
                                                        firstDefined(
                                                            row,
                                                            [
                                                                "asset_name",
                                                                "asset_id"
                                                            ],
                                                            "--"
                                                        )
                                                    )}
                                                </span>
                                            </td>

                                            <td>
                                                ${escapeHTML(
                                                    firstDefined(
                                                        row,
                                                        [
                                                            "building_name",
                                                            "building"
                                                        ],
                                                        "--"
                                                    )
                                                )}
                                            </td>

                                            <td>
                                                <span class="priority-badge ${priorityClass(priority)}">
                                                    ${escapeHTML(priority)}
                                                </span>
                                            </td>

                                            <td>
                                                <span class="status-badge ${statusClass(status)}">
                                                    ${escapeHTML(status)}
                                                </span>
                                            </td>

                                            <td>
                                                ${escapeHTML(
                                                    timestampValue(
                                                        firstDefined(
                                                            row,
                                                            [
                                                                "created_at",
                                                                "timestamp"
                                                            ],
                                                            ""
                                                        )
                                                    )
                                                )}
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

        console.error(
            "Maintenance work orders failed:",
            error
        );


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

        const response =
            await getJSON(
                buildURL(
                    "/api/occupancy/summary"
                )
            );


        const summary =
            response.summary &&
            typeof response.summary === "object"
                ? response.summary
                : response;


        const currentOccupancy =
            firstDefined(
                summary,
                [
                    "current_occupancy",
                    "total_current_occupancy",
                    "occupancy"
                ],
                0
            );


        const totalCapacity =
            firstDefined(
                summary,
                [
                    "total_capacity",
                    "capacity"
                ],
                0
            );


        const currentUtilization =
            firstDefined(
                summary,
                [
                    "current_utilization_percent",
                    "current_utilization",
                    "utilization_percent"
                ],
                0
            );


        const averageUtilization =
            firstDefined(
                summary,
                [
                    "average_utilization_percent",
                    "avg_utilization_percent",
                    "average_utilization"
                ],
                0
            );


        const peakOccupancy =
            firstDefined(
                summary,
                [
                    "peak_occupancy",
                    "maximum_occupancy"
                ],
                0
            );


        const overcrowding =
            firstDefined(
                summary,
                [
                    "overcrowding_events",
                    "overcrowded_events",
                    "overcrowding_count"
                ],
                0
            );


        setText(
            "currentOccupancyMetric",
            integerValue(
                currentOccupancy
            )
        );


        setText(
            "occupancyCapacityMetric",
            integerValue(
                totalCapacity
            )
        );


        setText(
            "occupancyUtilizationMetric",
            percentValue(
                currentUtilization
            )
        );


        setText(
            "averageUtilizationMetric",
            percentValue(
                averageUtilization
            )
        );


        setText(
            "peakOccupancyMetric",
            integerValue(
                peakOccupancy
            )
        );


        setText(
            "overcrowdingMetric",
            integerValue(
                overcrowding
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
                buildURL(
                    "/api/occupancy/current"
                )
            );


        const rows =
            extractArray(
                response,
                [
                    "spaces",
                    "occupancy",
                    "readings",
                    "data",
                    "records",
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
                                                    "utilization_status",
                                                    "status",
                                                    "occupancy_status"
                                                ],
                                                "NORMAL"
                                            )
                                        );


                                    return `
                                        <tr>

                                            <td>
                                                <span class="asset-name">
                                                    ${escapeHTML(
                                                        firstDefined(
                                                            row,
                                                            [
                                                                "space_name",
                                                                "space_id",
                                                                "name"
                                                            ],
                                                            "--"
                                                        )
                                                    )}
                                                </span>
                                            </td>

                                            <td>
                                                ${escapeHTML(
                                                    firstDefined(
                                                        row,
                                                        [
                                                            "building_name",
                                                            "building"
                                                        ],
                                                        "--"
                                                    )
                                                )}
                                            </td>

                                            <td>
                                                ${integerValue(
                                                    firstDefined(
                                                        row,
                                                        [
                                                            "occupancy",
                                                            "current_occupancy",
                                                            "occupancy_count"
                                                        ],
                                                        0
                                                    )
                                                )}
                                            </td>

                                            <td>
                                                ${integerValue(
                                                    firstDefined(
                                                        row,
                                                        [
                                                            "capacity",
                                                            "max_capacity"
                                                        ],
                                                        0
                                                    )
                                                )}
                                            </td>

                                            <td>
                                                ${percentValue(
                                                    firstDefined(
                                                        row,
                                                        [
                                                            "utilization_percent",
                                                            "utilization"
                                                        ],
                                                        0
                                                    )
                                                )}
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

        console.error(
            "Current occupancy failed:",
            error
        );


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
                        color: COLORS.teal,
                        width: 2
                    },

                    marker: {
                        color: COLORS.teal,
                        size: 6
                    },

                    hovertemplate:
                        "%{x}<br>Utilization: %{y:.1f}%<extra></extra>"
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
                        color: COLORS.teal
                    },

                    hovertemplate:
                        "%{x}<br>Utilization: %{y:.1f}%<extra></extra>"
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
                            "space_id",
                            "name"
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

        layout.height = 390;
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
                        color: COLORS.teal
                    },

                    hovertemplate:
                        "%{x}<br>Utilization: %{y:.1f}%<extra></extra>"
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
                    type: "bar",

                    marker: {
                        color: COLORS.hvac
                    },

                    hovertemplate:
                        "%{x}<br>Utilization: %{y:.1f}%<extra></extra>"
                }
            ],
            layout,
            plotConfig
        );

    } catch (error) {

        console.error(
            "Peak hours failed:",
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

            Plotly.purge(element);
            return;

        }

        const spaceNames =
            [
                ...new Set(
                    rows.map(
                        row =>
                            firstDefined(
                                row,
                                [
                                    "space_name",
                                    "space_id",
                                    "space"
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
                                    "hour_label",
                                    "time"
                                ],
                                ""
                            )
                    )
                )
            ];

        const matrix =
            spaceNames.map(
                spaceName =>
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
                                                    "space"
                                                ],
                                                ""
                                            )
                                        ) ===
                                            String(spaceName) &&
                                        String(
                                            firstDefined(
                                                row,
                                                [
                                                    "hour",
                                                    "hour_label",
                                                    "time"
                                                ],
                                                ""
                                            )
                                        ) ===
                                            String(hour)
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

        layout.height = 430;

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
                    y: spaceNames,
                    z: matrix,
                    type: "heatmap",

                    colorscale: [
                        [0, "#101C1C"],
                        [0.5, "#4B5D5C"],
                        [1, "#2DD4BF"]
                    ],

                    hovertemplate:
                        "Space: %{y}<br>Hour: %{x}<br>Utilization: %{z:.1f}%<extra></extra>"
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
                    "underused_spaces",
                    "spaces",
                    "data",
                    "records",
                    "items"
                ]
            );

        if (!rows.length) {

            showEmpty(
                "underusedSpaces",
                "No Underused Spaces",
                "No significant underused spaces are currently identified."
            );

            return;

        }

        container.innerHTML =
            rows
                .slice(0, 20)
                .map(
                    row => {

                        const status =
                            normalizeStatus(
                                firstDefined(
                                    row,
                                    [
                                        "utilization_status",
                                        "status"
                                    ],
                                    "UNDERUSED"
                                )
                            );

                        return `
                            <article class="issue-card">

                                <div class="card-topline">

                                    <h3 class="card-title">
                                        ${escapeHTML(
                                            firstDefined(
                                                row,
                                                [
                                                    "space_name",
                                                    "space_id",
                                                    "name"
                                                ],
                                                "Facility Space"
                                            )
                                        )}
                                    </h3>

                                    <span class="status-badge ${statusClass(status)}">
                                        ${escapeHTML(status)}
                                    </span>

                                </div>

                                <div class="card-meta">
                                    ${escapeHTML(
                                        firstDefined(
                                            row,
                                            [
                                                "building_name",
                                                "building"
                                            ],
                                            ""
                                        )
                                    )}
                                </div>

                                <p class="card-message">
                                    Average utilization:
                                    ${percentValue(
                                        firstDefined(
                                            row,
                                            [
                                                "average_utilization_percent",
                                                "utilization_percent",
                                                "utilization"
                                            ],
                                            0
                                        )
                                    )}
                                </p>

                            </article>
                        `;

                    }
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
                "/api/occupancy/overcrowding"
            );

        const rows =
            extractArray(
                response,
                [
                    "overcrowding_events",
                    "events",
                    "data",
                    "records",
                    "items"
                ]
            );

        if (!rows.length) {

            showEmpty(
                "overcrowdingEvents",
                "No Overcrowding Events",
                "No overcrowding events are currently available."
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
                                        "priority"
                                    ],
                                    "HIGH"
                                )
                            );

                        return `
                            <article class="issue-card">

                                <div class="card-topline">

                                    <h3 class="card-title">
                                        ${escapeHTML(
                                            firstDefined(
                                                row,
                                                [
                                                    "space_name",
                                                    "space_id"
                                                ],
                                                "Overcrowding Event"
                                            )
                                        )}
                                    </h3>

                                    <span class="priority-badge ${priorityClass(severity)}">
                                        ${escapeHTML(severity)}
                                    </span>

                                </div>

                                <div class="card-meta">

                                    ${escapeHTML(
                                        firstDefined(
                                            row,
                                            [
                                                "building_name",
                                                "building"
                                            ],
                                            ""
                                        )
                                    )}

                                    ${
                                        firstDefined(
                                            row,
                                            [
                                                "timestamp",
                                                "detected_at"
                                            ],
                                            ""
                                        )
                                            ? " · " +
                                              escapeHTML(
                                                  timestampValue(
                                                      firstDefined(
                                                          row,
                                                          [
                                                              "timestamp",
                                                              "detected_at"
                                                          ],
                                                          ""
                                                      )
                                                  )
                                              )
                                            : ""
                                    }

                                </div>

                                <p class="card-message">
                                    Occupancy:
                                    ${integerValue(
                                        firstDefined(
                                            row,
                                            [
                                                "occupancy",
                                                "occupancy_count"
                                            ],
                                            0
                                        )
                                    )}
                                    /
                                    ${integerValue(
                                        firstDefined(
                                            row,
                                            [
                                                "capacity",
                                                "max_capacity"
                                            ],
                                            0
                                        )
                                    )}
                                    · Utilization:
                                    ${percentValue(
                                        firstDefined(
                                            row,
                                            [
                                                "utilization_percent",
                                                "utilization"
                                            ],
                                            0
                                        )
                                    )}
                                </p>

                            </article>
                        `;

                    }
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

        let insights =
            extractArray(
                response,
                [
                    "insights",
                    "recommendations",
                    "data",
                    "items"
                ]
            );

        if (
            !insights.length &&
            typeof response === "object"
        ) {

            insights =
                Object.values(response)
                    .filter(
                        value =>
                            typeof value === "string"
                    );

        }

        if (!insights.length) {

            showEmpty(
                "occupancyInsights",
                "No Occupancy Insights",
                "No additional occupancy recommendations are currently available."
            );

            return;

        }

        container.innerHTML =
            insights
                .map(
                    insight => {

                        const message =
                            typeof insight === "string"
                                ? insight
                                : firstDefined(
                                    insight,
                                    [
                                        "message",
                                        "insight",
                                        "recommendation",
                                        "description"
                                    ],
                                    "Occupancy insight"
                                );

                        const title =
                            typeof insight === "string"
                                ? "Occupancy Insight"
                                : firstDefined(
                                    insight,
                                    [
                                        "title",
                                        "type"
                                    ],
                                    "Occupancy Insight"
                                );

                        return `
                            <article class="issue-card">

                                <h3 class="card-title">
                                    ${escapeHTML(title)}
                                </h3>

                                <p class="card-message">
                                    ${escapeHTML(message)}
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
                "/api/occupancy/alerts"
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

        const response =
            await getJSON(
                "/api/security/summary"
            );

        const summary =
            response.summary &&
            typeof response.summary === "object"
                ? response.summary
                : response;

        setText(
            "securityEventsMetric",
            integerValue(
                firstDefined(
                    summary,
                    [
                        "total_events",
                        "events",
                        "event_count"
                    ],
                    0
                )
            )
        );

        setText(
            "securityGrantedMetric",
            integerValue(
                firstDefined(
                    summary,
                    [
                        "granted_events",
                        "granted",
                        "access_granted"
                    ],
                    0
                )
            )
        );

        setText(
            "securityDeniedMetric",
            integerValue(
                firstDefined(
                    summary,
                    [
                        "denied_events",
                        "denied",
                        "access_denied"
                    ],
                    0
                )
            )
        );

        const unauthorized =
            firstDefined(
                summary,
                [
                    "unauthorized_access_attempts",
                    "unauthorized_attempts",
                    "unauthorized"
                ],
                0
            );

        setText(
            "securityUnauthorizedMetric",
            integerValue(
                unauthorized
            )
        );

        setText(
            "unauthorizedMetric",
            integerValue(
                unauthorized
            )
        );

        setText(
            "securityAlertsMetric",
            integerValue(
                firstDefined(
                    summary,
                    [
                        "security_alerts",
                        "alerts",
                        "alert_count"
                    ],
                    0
                )
            )
        );

        setText(
            "securityCriticalMetric",
            integerValue(
                firstDefined(
                    summary,
                    [
                        "critical_events",
                        "critical",
                        "critical_count"
                    ],
                    0
                )
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
                    "records",
                    "items"
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
                            "access_point",
                            "name"
                        ],
                        "Access Point"
                    )
            );

        const granted =
            rows.map(
                row =>
                    Number(
                        firstDefined(
                            row,
                            [
                                "granted_count",
                                "granted",
                                "access_granted"
                            ],
                            0
                        )
                    )
            );

        const denied =
            rows.map(
                row =>
                    Number(
                        firstDefined(
                            row,
                            [
                                "denied_count",
                                "denied",
                                "access_denied"
                            ],
                            0
                        )
                    )
            );

        const layout =
            commonLayout();

        layout.height = 370;

        layout.barmode =
            "group";

        layout.yaxis = {
            ...layout.yaxis,
            title: "Access Events"
        };

        Plotly.react(
            element,
            [
                {
                    x: names,
                    y: granted,
                    type: "bar",
                    name: "Granted",

                    marker: {
                        color: COLORS.teal
                    }
                },

                {
                    x: names,
                    y: denied,
                    type: "bar",
                    name: "Denied",

                    marker: {
                        color: COLORS.danger
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
                    "pattern",
                    "hours",
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
                                "event_count",
                                "events",
                                "total_events"
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
                        color: COLORS.teal,
                        width: 2
                    },

                    marker: {
                        color: COLORS.teal,
                        size: 6
                    },

                    hovertemplate:
                        "%{x}<br>Events: %{y}<extra></extra>"
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
                "/api/security/events?limit=50"
            );

        const rows =
            extractArray(
                response,
                [
                    "events",
                    "security_events",
                    "data",
                    "records",
                    "items"
                ]
            );

        if (!rows.length) {

            showEmpty(
                "securityEventsTable",
                "No Security Events",
                "No recent security events are currently available."
            );

            return;

        }

        container.innerHTML = `
            <table class="data-table">

                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Access Point</th>
                        <th>Person</th>
                        <th>Access</th>
                        <th>Event</th>
                        <th>Severity</th>
                    </tr>
                </thead>

                <tbody>

                    ${
                        rows
                            .slice(0, 50)
                            .map(
                                row => {

                                    const accessStatus =
                                        normalizeStatus(
                                            firstDefined(
                                                row,
                                                [
                                                    "access_status",
                                                    "access_result",
                                                    "status"
                                                ],
                                                "UNKNOWN"
                                            )
                                        );

                                    const severity =
                                        normalizeStatus(
                                            firstDefined(
                                                row,
                                                [
                                                    "severity",
                                                    "risk_level",
                                                    "priority"
                                                ],
                                                "NORMAL"
                                            )
                                        );

                                    return `
                                        <tr>

                                            <td>
                                                ${escapeHTML(
                                                    timestampValue(
                                                        firstDefined(
                                                            row,
                                                            [
                                                                "timestamp",
                                                                "event_timestamp",
                                                                "created_at"
                                                            ],
                                                            ""
                                                        )
                                                    )
                                                )}
                                            </td>

                                            <td>
                                                <span class="asset-name">
                                                    ${escapeHTML(
                                                        firstDefined(
                                                            row,
                                                            [
                                                                "access_point_name",
                                                                "access_point",
                                                                "location"
                                                            ],
                                                            "--"
                                                        )
                                                    )}
                                                </span>
                                            </td>

                                            <td>
                                                ${escapeHTML(
                                                    firstDefined(
                                                        row,
                                                        [
                                                            "person_name",
                                                            "employee_name",
                                                            "visitor_name",
                                                            "person_id",
                                                            "employee_id"
                                                        ],
                                                        "--"
                                                    )
                                                )}
                                            </td>

                                            <td>
                                                <span class="status-badge ${statusClass(accessStatus)}">
                                                    ${escapeHTML(accessStatus)}
                                                </span>
                                            </td>

                                            <td>
                                                ${escapeHTML(
                                                    firstDefined(
                                                        row,
                                                        [
                                                            "event_type",
                                                            "security_event_type",
                                                            "type"
                                                        ],
                                                        "ACCESS EVENT"
                                                    )
                                                )}
                                            </td>

                                            <td>
                                                <span class="priority-badge ${priorityClass(severity)}">
                                                    ${escapeHTML(severity)}
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

        console.error(
            "Security events failed:",
            error
        );

        showError(
            "securityEventsTable",
            "Unable to load security events."
        );

    }

}


/* ============================================================
   UNAUTHORIZED ACCESS
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
                "/api/security/unauthorized?limit=30"
            );

        const rows =
            extractArray(
                response,
                [
                    "unauthorized_events",
                    "events",
                    "attempts",
                    "data",
                    "records",
                    "items"
                ]
            );

        if (!rows.length) {

            showEmpty(
                "unauthorizedEvents",
                "No Unauthorized Attempts",
                "No unauthorized access attempts are currently stored."
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
                                        "risk_level",
                                        "priority"
                                    ],
                                    "HIGH"
                                )
                            );

                        const accessPoint =
                            firstDefined(
                                row,
                                [
                                    "access_point_name",
                                    "access_point",
                                    "location"
                                ],
                                "Access Point"
                            );

                        const person =
                            firstDefined(
                                row,
                                [
                                    "person_name",
                                    "employee_name",
                                    "visitor_name",
                                    "person_id",
                                    "employee_id",
                                    "credential_id"
                                ],
                                "Unknown person"
                            );

                        const timestamp =
                            firstDefined(
                                row,
                                [
                                    "timestamp",
                                    "event_timestamp",
                                    "created_at"
                                ],
                                ""
                            );

                        return `
                            <article class="issue-card">

                                <div class="card-topline">

                                    <h3 class="card-title">
                                        Unauthorized Access Attempt
                                    </h3>

                                    <span class="priority-badge ${priorityClass(severity)}">
                                        ${escapeHTML(severity)}
                                    </span>

                                </div>

                                <div class="card-meta">
                                    ${escapeHTML(accessPoint)}
                                    ${
                                        timestamp
                                            ? " · " +
                                              escapeHTML(
                                                  timestampValue(
                                                      timestamp
                                                  )
                                              )
                                            : ""
                                    }
                                </div>

                                <p class="card-message">
                                    Access was denied for
                                    ${escapeHTML(person)}.
                                </p>

                            </article>
                        `;

                    }
                )
                .join("");

    } catch (error) {

        showError(
            "unauthorizedEvents",
            "Unable to load unauthorized access attempts."
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
                    "records",
                    "items"
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

        container.innerHTML = `
            <table class="data-table">

                <thead>
                    <tr>
                        <th>Visitor</th>
                        <th>Access Point</th>
                        <th>Building</th>
                        <th>Event</th>
                        <th>Time</th>
                        <th>Status</th>
                    </tr>
                </thead>

                <tbody>

                    ${
                        rows
                            .slice(0, 30)
                            .map(
                                row => {

                                    const status =
                                        normalizeStatus(
                                            firstDefined(
                                                row,
                                                [
                                                    "access_status",
                                                    "status",
                                                    "access_result"
                                                ],
                                                "NORMAL"
                                            )
                                        );

                                    return `
                                        <tr>

                                            <td>
                                                <span class="asset-name">
                                                    ${escapeHTML(
                                                        firstDefined(
                                                            row,
                                                            [
                                                                "visitor_name",
                                                                "person_name",
                                                                "visitor_id",
                                                                "person_id"
                                                            ],
                                                            "Visitor"
                                                        )
                                                    )}
                                                </span>
                                            </td>

                                            <td>
                                                ${escapeHTML(
                                                    firstDefined(
                                                        row,
                                                        [
                                                            "access_point_name",
                                                            "access_point",
                                                            "location"
                                                        ],
                                                        "--"
                                                    )
                                                )}
                                            </td>

                                            <td>
                                                ${escapeHTML(
                                                    firstDefined(
                                                        row,
                                                        [
                                                            "building_name",
                                                            "building"
                                                        ],
                                                        "--"
                                                    )
                                                )}
                                            </td>

                                            <td>
                                                ${escapeHTML(
                                                    firstDefined(
                                                        row,
                                                        [
                                                            "event_type",
                                                            "movement_type",
                                                            "type"
                                                        ],
                                                        "ACCESS"
                                                    )
                                                )}
                                            </td>

                                            <td>
                                                ${escapeHTML(
                                                    timestampValue(
                                                        firstDefined(
                                                            row,
                                                            [
                                                                "timestamp",
                                                                "event_timestamp"
                                                            ],
                                                            ""
                                                        )
                                                    )
                                                )}
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

        let insights =
            extractArray(
                response,
                [
                    "insights",
                    "recommendations",
                    "data",
                    "items"
                ]
            );

        if (
            !insights.length &&
            response &&
            typeof response === "object"
        ) {

            insights =
                Object.values(response)
                    .filter(
                        value =>
                            typeof value === "string"
                    );

        }

        if (!insights.length) {

            showEmpty(
                "securityInsights",
                "No Security Insights",
                "No additional security recommendations are currently available."
            );

            return;

        }

        container.innerHTML =
            insights
                .map(
                    insight => {

                        const title =
                            typeof insight === "string"
                                ? "Security Insight"
                                : firstDefined(
                                    insight,
                                    [
                                        "title",
                                        "type",
                                        "alert_type"
                                    ],
                                    "Security Insight"
                                );

                        const message =
                            typeof insight === "string"
                                ? insight
                                : firstDefined(
                                    insight,
                                    [
                                        "message",
                                        "insight",
                                        "recommendation",
                                        "description"
                                    ],
                                    "Review the latest security activity."
                                );

                        return `
                            <article class="issue-card">

                                <h3 class="card-title">
                                    ${escapeHTML(title)}
                                </h3>

                                <p class="card-message">
                                    ${escapeHTML(message)}
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
                "/api/security/alerts"
            );

        const alerts =
            extractArray(
                response,
                [
                    "alerts",
                    "security_alerts",
                    "data",
                    "records",
                    "items"
                ]
            );

        renderAlertCards(
            "securityIssueCentre",
            alerts,
            "No Security Issues",
            "No active security issues are currently stored."
        );

    } catch (error) {

        showError(
            "securityIssueCentre",
            "Unable to load the security Issue Centre."
        );

    }

}


/* ============================================================
   SECURITY ALERTS
   ============================================================ */

async function loadSecurityAlerts() {

    try {

        const response =
            await getJSON(
                "/api/security/alerts"
            );

        const alerts =
            extractArray(
                response,
                [
                    "alerts",
                    "security_alerts",
                    "data",
                    "records",
                    "items"
                ]
            );

        renderAlertCards(
            "securityAlerts",
            alerts,
            "No Security Alerts",
            "No active security alerts are currently stored."
        );

    } catch (error) {

        showError(
            "securityAlerts",
            "Unable to load security alerts."
        );

    }

}


/* ============================================================
   COST OPTIMIZATION AGENT
   ============================================================ */

async function runCostOptimizationAgent() {

    try {

        await postJSON(
            costURL(
                "/api/cost/agent/run"
            )
        );

    } catch (error) {

        console.error(
            "Cost Optimization Agent failed:",
            error
        );

    }

}


/* ============================================================
   COST SUMMARY
   ============================================================ */

async function loadCostSummary() {

    try {

        const response =
            await getJSON(
                costURL(
                    "/api/cost/summary"
                )
            );

        const summary =
            response.summary &&
            typeof response.summary === "object"
                ? response.summary
                : response;

        const totalCost =
            firstDefined(
                summary,
                [
                    "total_cost",
                    "actual_cost",
                    "operational_cost",
                    "cost_total"
                ],
                0
            );

        const expectedCost =
            firstDefined(
                summary,
                [
                    "expected_cost",
                    "total_expected_cost",
                    "expected_total"
                ],
                0
            );

        const variance =
            firstDefined(
                summary,
                [
                    "cost_variance",
                    "total_cost_variance",
                    "variance",
                    "variance_amount"
                ],
                0
            );

        const savings =
            firstDefined(
                summary,
                [
                    "potential_savings",
                    "total_potential_savings",
                    "savings",
                    "savings_potential"
                ],
                0
            );

        const inefficiencies =
            firstDefined(
                summary,
                [
                    "inefficiency_count",
                    "cost_inefficiencies",
                    "inefficiencies",
                    "inefficient_records"
                ],
                0
            );

        setText(
            "costTotalMetric",
            currencyValue(
                totalCost
            )
        );

        setText(
            "costExpectedMetric",
            currencyValue(
                expectedCost
            )
        );

        setText(
            "costVarianceMetric",
            currencyValue(
                variance
            )
        );

        setText(
            "costSavingsMetric",
            currencyValue(
                savings
            )
        );

        setText(
            "costInefficiencyMetric",
            integerValue(
                inefficiencies
            )
        );

    } catch (error) {

        console.error(
            "Cost summary failed:",
            error
        );

    }

}


/* ============================================================
   COST DATABASE STATUS
   ============================================================ */

async function loadCostDatabaseStatus() {

    try {

        const response =
            await getJSON(
                "/api/cost/database-status"
            );

        const status =
            response.database &&
            typeof response.database === "object"
                ? response.database
                : response;

        const alertCount =
            firstDefined(
                status,
                [
                    "cost_optimization_alerts",
                    "alert_count",
                    "alerts"
                ],
                null
            );

        if (alertCount !== null) {

            setText(
                "costAlertsMetric",
                integerValue(
                    alertCount
                )
            );

        }

    } catch (error) {

        console.error(
            "Cost database status failed:",
            error
        );

    }

}


/* ============================================================
   COST DAILY TREND
   ============================================================ */

async function loadCostDailyTrend() {

    try {

        const response =
            await getJSON(
                costURL(
                    "/api/cost/daily-trend"
                )
            );

        const rows =
            extractArray(
                response,
                [
                    "daily_trend",
                    "trend",
                    "daily_costs",
                    "data",
                    "records",
                    "items"
                ]
            );

        const element =
            document.getElementById(
                "costDailyTrendChart"
            );

        if (
            !element ||
            typeof Plotly === "undefined"
        ) {
            return;
        }

        if (!rows.length) {

            Plotly.purge(element);
            return;

        }

        const dates =
            rows.map(
                row =>
                    firstDefined(
                        row,
                        [
                            "date",
                            "day",
                            "timestamp"
                        ],
                        ""
                    )
            );

        const actual =
            rows.map(
                row =>
                    Number(
                        firstDefined(
                            row,
                            [
                                "total_cost",
                                "actual_cost",
                                "cost"
                            ],
                            0
                        )
                    )
            );

        const expected =
            rows.map(
                row =>
                    Number(
                        firstDefined(
                            row,
                            [
                                "expected_cost",
                                "total_expected_cost"
                            ],
                            0
                        )
                    )
            );

        const layout =
            commonLayout();

        layout.height = 370;

        layout.yaxis = {
            ...layout.yaxis,
            title: "Cost (₹)"
        };

        Plotly.react(
            element,
            [
                {
                    x: dates,
                    y: actual,
                    type: "scatter",
                    mode: "lines+markers",
                    name: "Actual Cost",

                    line: {
                        color: COLORS.teal,
                        width: 2
                    },

                    marker: {
                        color: COLORS.teal,
                        size: 5
                    },

                    hovertemplate:
                        "%{x}<br>Actual: ₹%{y:,.2f}<extra></extra>"
                },

                {
                    x: dates,
                    y: expected,
                    type: "scatter",
                    mode: "lines",
                    name: "Expected Cost",

                    line: {
                        color: COLORS.chartMuted,
                        width: 2,
                        dash: "dot"
                    },

                    hovertemplate:
                        "%{x}<br>Expected: ₹%{y:,.2f}<extra></extra>"
                }
            ],
            layout,
            plotConfig
        );

    } catch (error) {

        console.error(
            "Cost daily trend failed:",
            error
        );

    }

}


/* ============================================================
   COST BUILDING COMPARISON
   ============================================================ */

async function loadCostBuildingComparison() {

    try {

        const response =
            await getJSON(
                "/api/cost/buildings"
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
                "costBuildingChart"
            );

        if (
            !element ||
            typeof Plotly === "undefined"
        ) {
            return;
        }

        if (!rows.length) {

            Plotly.purge(element);
            return;

        }

        const buildings =
            rows.map(
                row =>
                    firstDefined(
                        row,
                        [
                            "building_name",
                            "building_id",
                            "building",
                            "name"
                        ],
                        "Building"
                    )
            );

        const costs =
            rows.map(
                row =>
                    Number(
                        firstDefined(
                            row,
                            [
                                "total_cost",
                                "actual_cost",
                                "cost"
                            ],
                            0
                        )
                    )
            );

        const savings =
            rows.map(
                row =>
                    Number(
                        firstDefined(
                            row,
                            [
                                "potential_savings",
                                "savings",
                                "savings_potential"
                            ],
                            0
                        )
                    )
            );

        const layout =
            commonLayout();

        layout.height = 370;
        layout.barmode = "group";

        layout.yaxis = {
            ...layout.yaxis,
            title: "Cost (₹)"
        };

        Plotly.react(
            element,
            [
                {
                    x: buildings,
                    y: costs,
                    type: "bar",
                    name: "Operational Cost",

                    marker: {
                        color: COLORS.chartMuted
                    },

                    hovertemplate:
                        "%{x}<br>Cost: ₹%{y:,.2f}<extra></extra>"
                },

                {
                    x: buildings,
                    y: savings,
                    type: "bar",
                    name: "Potential Savings",

                    marker: {
                        color: COLORS.teal
                    },

                    hovertemplate:
                        "%{x}<br>Savings: ₹%{y:,.2f}<extra></extra>"
                }
            ],
            layout,
            plotConfig
        );

    } catch (error) {

        console.error(
            "Cost building comparison failed:",
            error
        );

    }

}


/* ============================================================
   COST BREAKDOWN
   ============================================================ */

async function loadCostBreakdown() {

    try {

        const response =
            await getJSON(
                costURL(
                    "/api/cost/breakdown"
                )
            );

        const element =
            document.getElementById(
                "costBreakdownChart"
            );

        if (
            !element ||
            typeof Plotly === "undefined"
        ) {
            return;
        }

        let rows =
            extractArray(
                response,
                [
                    "breakdown",
                    "cost_breakdown",
                    "categories",
                    "data",
                    "records",
                    "items"
                ]
            );

        let labels = [];
        let values = [];

        if (rows.length) {

            labels =
                rows.map(
                    row =>
                        firstDefined(
                            row,
                            [
                                "category",
                                "cost_type",
                                "type",
                                "name"
                            ],
                            "Cost"
                        )
                );

            values =
                rows.map(
                    row =>
                        Number(
                            firstDefined(
                                row,
                                [
                                    "cost",
                                    "amount",
                                    "total_cost",
                                    "value"
                                ],
                                0
                            )
                        )
                );

        } else {

            const breakdown =
                response.breakdown &&
                typeof response.breakdown === "object"
                    ? response.breakdown
                    : response;

            const candidates = [
                [
                    "Electricity",
                    firstDefined(
                        breakdown,
                        [
                            "electricity_cost",
                            "total_electricity_cost"
                        ],
                        null
                    )
                ],
                [
                    "HVAC",
                    firstDefined(
                        breakdown,
                        [
                            "hvac_cost",
                            "total_hvac_cost"
                        ],
                        null
                    )
                ],
                [
                    "Lighting",
                    firstDefined(
                        breakdown,
                        [
                            "lighting_cost",
                            "total_lighting_cost"
                        ],
                        null
                    )
                ],
                [
                    "Water",
                    firstDefined(
                        breakdown,
                        [
                            "water_cost",
                            "total_water_cost"
                        ],
                        null
                    )
                ],
                [
                    "Maintenance",
                    firstDefined(
                        breakdown,
                        [
                            "maintenance_cost",
                            "total_maintenance_cost"
                        ],
                        null
                    )
                ],
                [
                    "Security",
                    firstDefined(
                        breakdown,
                        [
                            "security_cost",
                            "total_security_cost"
                        ],
                        null
                    )
                ],
                [
                    "Operations",
                    firstDefined(
                        breakdown,
                        [
                            "operational_cost",
                            "operations_cost",
                            "other_operational_cost"
                        ],
                        null
                    )
                ]
            ];

            candidates.forEach(
                ([label, value]) => {

                    const number =
                        Number(value);

                    if (
                        value !== null &&
                        Number.isFinite(number)
                    ) {

                        labels.push(label);
                        values.push(number);

                    }

                }
            );

        }

        if (!labels.length) {

            Plotly.purge(element);
            return;

        }

        const layout =
            commonLayout();

        layout.height = 370;

        layout.showlegend =
            true;

        layout.margin = {
            l: 20,
            r: 20,
            t: 20,
            b: 20
        };

        Plotly.react(
            element,
            [
                {
                    labels: labels,
                    values: values,
                    type: "pie",
                    hole: 0.55,

                    textinfo:
                        "label+percent",

                    hovertemplate:
                        "%{label}<br>₹%{value:,.2f}<br>%{percent}<extra></extra>"
                }
            ],
            layout,
            plotConfig
        );

    } catch (error) {

        console.error(
            "Cost breakdown failed:",
            error
        );

    }

}


/* ============================================================
   COST HOURLY PATTERN
   ============================================================ */

async function loadCostHourlyPattern() {

    try {

        const response =
            await getJSON(
                costURL(
                    "/api/cost/hourly-pattern"
                )
            );

        const rows =
            extractArray(
                response,
                [
                    "hourly_pattern",
                    "pattern",
                    "hours",
                    "data",
                    "records",
                    "items"
                ]
            );

        const element =
            document.getElementById(
                "costHourlyChart"
            );

        if (
            !element ||
            typeof Plotly === "undefined"
        ) {
            return;
        }

        if (!rows.length) {

            Plotly.purge(element);
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

        const costs =
            rows.map(
                row =>
                    Number(
                        firstDefined(
                            row,
                            [
                                "average_cost",
                                "avg_cost",
                                "total_cost",
                                "cost"
                            ],
                            0
                        )
                    )
            );

        const layout =
            commonLayout();

        layout.height = 370;
        layout.showlegend = false;

        layout.yaxis = {
            ...layout.yaxis,
            title: "Average Cost (₹)"
        };

        Plotly.react(
            element,
            [
                {
                    x: hours,
                    y: costs,
                    type: "scatter",
                    mode: "lines+markers",

                    line: {
                        color: COLORS.hvac,
                        width: 2
                    },

                    marker: {
                        color: COLORS.teal,
                        size: 6
                    },

                    hovertemplate:
                        "Hour: %{x}<br>Average Cost: ₹%{y:,.2f}<extra></extra>"
                }
            ],
            layout,
            plotConfig
        );

    } catch (error) {

        console.error(
            "Cost hourly pattern failed:",
            error
        );

    }

}
/* ============================================================
   COST SAVINGS OPPORTUNITIES
   ============================================================ */

async function loadCostSavings() {

    const container =
        document.getElementById(
            "costSavingsTable"
        );

    if (!container) {
        return;
    }

    try {

        const response =
            await getJSON(
                costURL(
                    "/api/cost/savings"
                )
            );

        const rows =
            extractArray(
                response,
                [
                    "opportunities",
                    "savings_opportunities",
                    "savings",
                    "data",
                    "records",
                    "items"
                ]
            );

        if (!rows.length) {

            showEmpty(
                "costSavingsTable",
                "No Savings Opportunities",
                "No cost optimization opportunities are currently identified."
            );

            return;
        }

        container.innerHTML = `
            <table class="data-table">

                <thead>
                    <tr>
                        <th>Building</th>
                        <th>Opportunity</th>
                        <th>Current Cost</th>
                        <th>Potential Savings</th>
                        <th>Priority</th>
                        <th>Recommendation</th>
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
                                                    "savings_priority",
                                                    "severity"
                                                ],
                                                "LOW"
                                            )
                                        );

                                    return `
                                        <tr>

                                            <td>
                                                <span class="asset-name">
                                                    ${escapeHTML(
                                                        firstDefined(
                                                            row,
                                                            [
                                                                "building_name",
                                                                "building"
                                                            ],
                                                            "--"
                                                        )
                                                    )}
                                                </span>
                                            </td>

                                            <td>
                                                ${escapeHTML(
                                                    firstDefined(
                                                        row,
                                                        [
                                                            "inefficiency_type",
                                                            "opportunity",
                                                            "type"
                                                        ],
                                                        "Cost Optimization"
                                                    )
                                                )}
                                            </td>

                                            <td>
                                                ${currencyValue(
                                                    firstDefined(
                                                        row,
                                                        [
                                                            "total_cost",
                                                            "current_cost",
                                                            "cost"
                                                        ],
                                                        0
                                                    )
                                                )}
                                            </td>

                                            <td>
                                                ${currencyValue(
                                                    firstDefined(
                                                        row,
                                                        [
                                                            "potential_savings",
                                                            "savings",
                                                            "savings_amount"
                                                        ],
                                                        0
                                                    )
                                                )}
                                            </td>

                                            <td>
                                                <span class="priority-badge ${priorityClass(priority)}">
                                                    ${escapeHTML(priority)}
                                                </span>
                                            </td>

                                            <td>
                                                ${escapeHTML(
                                                    firstDefined(
                                                        row,
                                                        [
                                                            "recommendation",
                                                            "recommended_action",
                                                            "message"
                                                        ],
                                                        "Review the identified cost driver."
                                                    )
                                                )}
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

        console.error(
            "Cost savings failed:",
            error
        );

        showError(
            "costSavingsTable",
            "Unable to load cost savings opportunities."
        );

    }

}


/* ============================================================
   COST INEFFICIENCIES
   ============================================================ */

async function loadCostInefficiencies() {

    const container =
        document.getElementById(
            "costInefficiencyTable"
        );

    if (!container) {
        return;
    }

    try {

        const response =
            await getJSON(
                costURL(
                    "/api/cost/inefficiencies",
                    {
                        limit: 30
                    }
                )
            );

        const rows =
            extractArray(
                response,
                [
                    "inefficiencies",
                    "cost_inefficiencies",
                    "records",
                    "data",
                    "items"
                ]
            );

        if (!rows.length) {

            showEmpty(
                "costInefficiencyTable",
                "No Cost Inefficiencies",
                "No significant cost inefficiencies are currently identified."
            );

            return;
        }

        container.innerHTML = `
            <table class="data-table">

                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Building</th>
                        <th>Issue</th>
                        <th>Actual Cost</th>
                        <th>Expected Cost</th>
                        <th>Variance</th>
                        <th>Savings</th>
                        <th>Priority</th>
                    </tr>
                </thead>

                <tbody>

                    ${
                        rows
                            .slice(0, 30)
                            .map(
                                row => {

                                    const priority =
                                        normalizeStatus(
                                            firstDefined(
                                                row,
                                                [
                                                    "savings_priority",
                                                    "priority",
                                                    "severity"
                                                ],
                                                "LOW"
                                            )
                                        );

                                    return `
                                        <tr>

                                            <td>
                                                ${escapeHTML(
                                                    timestampValue(
                                                        firstDefined(
                                                            row,
                                                            [
                                                                "timestamp",
                                                                "created_at",
                                                                "date"
                                                            ],
                                                            ""
                                                        )
                                                    )
                                                )}
                                            </td>

                                            <td>
                                                <span class="asset-name">
                                                    ${escapeHTML(
                                                        firstDefined(
                                                            row,
                                                            [
                                                                "building_name",
                                                                "building_id",
                                                                "building"
                                                            ],
                                                            "--"
                                                        )
                                                    )}
                                                </span>
                                            </td>

                                            <td>
                                                ${escapeHTML(
                                                    firstDefined(
                                                        row,
                                                        [
                                                            "inefficiency_type",
                                                            "issue_type",
                                                            "type"
                                                        ],
                                                        "Cost Inefficiency"
                                                    )
                                                )}
                                            </td>

                                            <td>
                                                ${currencyValue(
                                                    firstDefined(
                                                        row,
                                                        [
                                                            "total_cost",
                                                            "actual_cost",
                                                            "cost"
                                                        ],
                                                        0
                                                    )
                                                )}
                                            </td>

                                            <td>
                                                ${currencyValue(
                                                    firstDefined(
                                                        row,
                                                        [
                                                            "expected_cost",
                                                            "expected_total_cost"
                                                        ],
                                                        0
                                                    )
                                                )}
                                            </td>

                                            <td>
                                                ${currencyValue(
                                                    firstDefined(
                                                        row,
                                                        [
                                                            "cost_variance",
                                                            "variance",
                                                            "variance_amount"
                                                        ],
                                                        0
                                                    )
                                                )}
                                            </td>

                                            <td>
                                                ${currencyValue(
                                                    firstDefined(
                                                        row,
                                                        [
                                                            "potential_savings",
                                                            "savings",
                                                            "savings_amount"
                                                        ],
                                                        0
                                                    )
                                                )}
                                            </td>

                                            <td>
                                                <span class="priority-badge ${priorityClass(priority)}">
                                                    ${escapeHTML(priority)}
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

        console.error(
            "Cost inefficiencies failed:",
            error
        );

        showError(
            "costInefficiencyTable",
            "Unable to load cost inefficiencies."
        );

    }

}


/* ============================================================
   COST OPTIMIZATION INSIGHTS
   ============================================================ */

async function loadCostInsights() {

    const container =
        document.getElementById(
            "costInsights"
        );

    if (!container) {
        return;
    }

    try {

        const response =
            await getJSON(
                costURL(
                    "/api/cost/insights"
                )
            );

        let insights =
            extractArray(
                response,
                [
                    "insights",
                    "recommendations",
                    "data",
                    "items"
                ]
            );

        if (
            !insights.length &&
            response &&
            typeof response === "object"
        ) {

            insights =
                Object.values(response)
                    .filter(
                        value =>
                            typeof value === "string"
                    );

        }

        if (!insights.length) {

            showEmpty(
                "costInsights",
                "No Cost Insights",
                "No additional cost optimization insights are currently available."
            );

            return;
        }

        container.innerHTML =
            insights
                .map(
                    insight => {

                        const message =
                            typeof insight === "string"
                                ? insight
                                : firstDefined(
                                    insight,
                                    [
                                        "message",
                                        "insight",
                                        "recommendation",
                                        "description"
                                    ],
                                    "Review current operational costs."
                                );

                        const title =
                            typeof insight === "string"
                                ? "Cost Optimization Insight"
                                : firstDefined(
                                    insight,
                                    [
                                        "title",
                                        "type",
                                        "inefficiency_type"
                                    ],
                                    "Cost Optimization Insight"
                                );

                        return `
                            <article class="cost-insight-card">

                                <h3 class="card-title">
                                    ${escapeHTML(title)}
                                </h3>

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
            "Cost insights failed:",
            error
        );

        showError(
            "costInsights",
            "Unable to load cost optimization insights."
        );

    }

}


/* ============================================================
   COST OPTIMIZATION ALERTS
   ============================================================ */

async function loadCostAlerts() {

    try {

        const response =
            await getJSON(
                "/api/cost/alerts?limit=30"
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
            "costOptimizationAlerts",
            alerts,
            "No Cost Alerts",
            "No cost optimization alerts are currently stored."
        );

        /*
            Same cost alerts are also displayed in the
            unified alert section.
        */

        renderAlertCards(
            "costAlertsUnified",
            alerts,
            "No Cost Alerts",
            "No active cost optimization alerts."
        );

        setText(
            "costAlertsMetric",
            integerValue(
                firstDefined(
                    response,
                    [
                        "total",
                        "count",
                        "alert_count"
                    ],
                    alerts.length
                )
            )
        );

    } catch (error) {

        console.error(
            "Cost alerts failed:",
            error
        );

        showError(
            "costOptimizationAlerts",
            "Unable to load cost optimization alerts."
        );

        showError(
            "costAlertsUnified",
            "Unable to load cost optimization alerts."
        );

    }

}


/* ============================================================
   COST DATA REFRESH
   ============================================================ */

async function refreshCostData() {

    await Promise.allSettled(
        [
            loadCostSummary(),
            loadCostDatabaseStatus(),
            loadCostDailyTrend(),
            loadCostBuildingComparison(),
            loadCostBreakdown(),
            loadCostHourlyPattern(),
            loadCostSavings(),
            loadCostInefficiencies(),
            loadCostInsights(),
            loadCostAlerts()
        ]
    );

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


/* ============================================================
   COMPLETE DASHBOARD REFRESH
   ============================================================ */

async function refreshDashboard(
    runAgents = false
) {

    if (runAgents) {

        await Promise.allSettled(
            [
                runEnergyAgent(),
                runMaintenanceAgent(),
                runCostOptimizationAgent()
            ]
        );

    }

    await Promise.allSettled(
        [
            refreshEnergyData(),
            refreshMaintenanceData(),
            refreshOccupancyData(),
            refreshSecurityData(),
            refreshCostData()
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
        "securityHourlyChart",

        "costDailyTrendChart",
        "costBuildingChart",
        "costBreakdownChart",
        "costHourlyChart"
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