"use strict";


/* ============================================================
   FACILITYOPS AI
   UNIFIED ENERGY + MAINTENANCE DASHBOARD
   ============================================================ */


/* ============================================================
   COLOURS
   ============================================================ */

const COLORS = {

    page:
        "#0A1414",

    card:
        "#101C1C",

    border:
        "#1C2B2A",

    muted:
        "#6B8180",

    text:
        "#E5E7EB",

    teal:
        "#2DD4BF",

    danger:
        "#EF4444",

    dangerLight:
        "#F87171",

    chartMuted:
        "#4B5D5C",

    hvac:
        "#5DCAA5"

};


const AUTO_REFRESH_MS =
    30000;


/* ============================================================
   DOM
   ============================================================ */

const facilitySelect =
    document.getElementById(
        "facilitySelect"
    );


const buildingSelect =
    document.getElementById(
        "buildingSelect"
    );


const blockSelect =
    document.getElementById(
        "blockSelect"
    );


/* ============================================================
   GENERAL HELPERS
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

    const number =
        Number(value);


    if (
        !Number.isFinite(number)
    ) {
        return "--";
    }


    return number.toLocaleString(
        undefined,
        {
            minimumFractionDigits:
                decimals,

            maximumFractionDigits:
                decimals
        }
    );

}


function integerValue(value) {

    const number =
        Number(value);


    if (
        !Number.isFinite(number)
    ) {
        return "--";
    }


    return Math.round(number)
        .toLocaleString();

}


function percentValue(value) {

    let number =
        Number(value);


    if (
        !Number.isFinite(number)
    ) {
        return "--";
    }


    if (
        number >= 0 &&
        number <= 1
    ) {
        number *= 100;
    }


    return (
        number.toFixed(1) +
        "%"
    );

}


function timestampValue(value) {

    if (!value) {
        return "--";
    }


    const date =
        new Date(value);


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


    const date =
        new Date(value);


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

        element.textContent =
            value;

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


    for (
        const key
        of keys
    ) {

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

    if (
        Array.isArray(data)
    ) {
        return data;
    }


    if (
        !data ||
        typeof data !== "object"
    ) {
        return [];
    }


    for (
        const key
        of possibleKeys
    ) {

        if (
            Array.isArray(
                data[key]
            )
        ) {
            return data[key];
        }

    }


    for (
        const value
        of Object.values(data)
    ) {

        if (
            Array.isArray(value)
        ) {
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
        status === "EXCELLENT"
    ) {
        return "status-excellent";
    }


    if (
        status === "GOOD"
    ) {
        return "status-good";
    }


    if (
        status === "WARNING" ||
        status === "WATCH"
    ) {
        return "status-warning";
    }


    if (
        status === "CRITICAL"
    ) {
        return "status-critical";
    }


    return "status-good";

}


function priorityClass(value) {

    const priority =
        normalizeStatus(value);


    if (
        priority === "CRITICAL"
    ) {
        return "priority-critical";
    }


    if (
        priority === "HIGH"
    ) {
        return "priority-high";
    }


    if (
        priority === "MEDIUM"
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


    element.innerHTML =
        `
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


    element.innerHTML =
        `
        <div class="empty-state">
            <h3>
                ${escapeHTML(title)}
            </h3>

            <p>
                ${escapeHTML(message)}
            </p>
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
                credentials:
                    "same-origin",

                ...options
            }
        );


    if (
        response.status === 401
    ) {

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


    if (
        body !== null
    ) {

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
        queryParams(
            additional
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
                        typeof building ===
                        "string"
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


                    option.value =
                        name;


                    option.textContent =
                        name;


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
                        typeof block ===
                        "string"
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


                    option.value =
                        name;


                    option.textContent =
                        name;


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
   ENERGY SUMMARY
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


        setText(
            "lastUpdated",
            new Date()
                .toLocaleString()
        );


    } catch (error) {

        console.error(
            "Summary loading failed:",
            error
        );

    }

}


/* ============================================================
   ENERGY READINGS / CHARTS
   ============================================================ */

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


        if (
            readings.length === 0
        ) {

            return;

        }


        readings.sort(
            (a, b) =>
                new Date(
                    a.timestamp
                ) -
                new Date(
                    b.timestamp
                )
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


        drawOccupancyChart(
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


    layout.height =
        350;


    layout.showlegend =
        false;


    layout.yaxis = {
        ...layout.yaxis,
        title:
            "Electricity kWh"
    };


    Plotly.react(
        element,
        [
            {
                x:
                    timestamps,

                y:
                    values,

                type:
                    "scatter",

                mode:
                    "lines",

                line: {
                    color:
                        COLORS.teal,

                    width:
                        2
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


    layout.height =
        350;


    layout.showlegend =
        false;


    layout.yaxis = {
        ...layout.yaxis,
        title:
            "HVAC kWh"
    };


    Plotly.react(
        element,
        [
            {
                x:
                    timestamps,

                y:
                    values,

                type:
                    "scatter",

                mode:
                    "lines",

                line: {
                    color:
                        COLORS.hvac,

                    width:
                        2
                },

                hovertemplate:
                    "%{x}<br>%{y:.2f} kWh<extra></extra>"
            }
        ],
        layout,
        plotConfig
    );

}


function drawOccupancyChart(
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


    layout.height =
        350;


    layout.showlegend =
        false;


    layout.xaxis = {
        ...layout.xaxis,
        title:
            "Occupancy"
    };


    layout.yaxis = {
        ...layout.yaxis,
        title:
            "Electricity kWh"
    };


    Plotly.react(
        element,
        [
            {
                x:
                    occupancy,

                y:
                    electricity,

                type:
                    "scatter",

                mode:
                    "markers",

                marker: {
                    color:
                        COLORS.teal,

                    size:
                        5,

                    opacity:
                        0.55
                },

                hovertemplate:
                    "Occupancy: %{x}<br>Electricity: %{y:.2f}<extra></extra>"
            }
        ],
        layout,
        plotConfig
    );

}


/* ============================================================
   BUILDING ENERGY COMPARISON
   ============================================================ */

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


        if (
            rows.length === 0
        ) {

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


        layout.height =
            350;


        layout.showlegend =
            false;


        layout.yaxis = {
            ...layout.yaxis,
            title:
                "Electricity kWh"
        };


        Plotly.react(
            element,
            [
                {
                    x:
                        names,

                    y:
                        values,

                    type:
                        "bar",

                    marker: {
                        color:
                            COLORS.teal
                    },

                    hovertemplate:
                        "%{x}<br>%{y:.2f} kWh<extra></extra>"
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


/* ============================================================
   ENERGY AGENT
   ============================================================ */

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
   ISSUE CENTRE
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


        if (
            issues.length === 0
        ) {

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


                        const block =
                            firstDefined(
                                issue,
                                [
                                    "block_name",
                                    "block"
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
                                    ${block ? " · " + escapeHTML(block) : ""}
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
   ENERGY CONSUMPTION ALERTS
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


        if (
            alerts.length === 0
        ) {

            showEmpty(
                "consumptionAlerts",
                "No Energy Alerts",
                "No active consumption alerts are currently available."
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
                                        "severity",
                                        "priority",
                                        "level"
                                    ],
                                    "WATCH"
                                )
                            );


                        const title =
                            firstDefined(
                                alert,
                                [
                                    "title",
                                    "alert_type",
                                    "type"
                                ],
                                "Consumption Alert"
                            );


                        const message =
                            firstDefined(
                                alert,
                                [
                                    "message",
                                    "description",
                                    "recommendation"
                                ],
                                "Energy consumption requires review."
                            );


                        return `
                            <article class="recommendation-card">

                                <div class="card-topline">

                                    <h3 class="card-title">
                                        ${escapeHTML(title)}
                                    </h3>

                                    <span class="priority-badge ${priorityClass(severity)}">
                                        ${escapeHTML(severity)}
                                    </span>

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
            "Consumption alert loading failed:",
            error
        );


        showError(
            "consumptionAlerts",
            "Unable to load energy consumption alerts."
        );

    }

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

        const data =
            await getJSON(
                buildURL(
                    "/api/maintenance/summary"
                )
            );


        const summary =
            (
                data.summary &&
                typeof data.summary ===
                "object"
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


        if (
            rows.length === 0
        ) {

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
                            "id"
                        ],
                        firstDefined(
                            row,
                            [
                                "asset_name",
                                "name"
                            ],
                            "asset"
                        )
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


        container.innerHTML =
            `
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
                                row => {

                                    const assetId =
                                        firstDefined(
                                            row,
                                            [
                                                "asset_id",
                                                "id"
                                            ],
                                            "--"
                                        );


                                    const assetName =
                                        firstDefined(
                                            row,
                                            [
                                                "asset_name",
                                                "name"
                                            ],
                                            "Equipment"
                                        );


                                    const type =
                                        firstDefined(
                                            row,
                                            [
                                                "asset_type",
                                                "type"
                                            ],
                                            ""
                                        );


                                    const building =
                                        firstDefined(
                                            row,
                                            [
                                                "building_name",
                                                "building"
                                            ],
                                            "--"
                                        );


                                    const block =
                                        firstDefined(
                                            row,
                                            [
                                                "block_name",
                                                "block"
                                            ],
                                            ""
                                        );


                                    return `
                                        <tr>

                                            <td>
                                                <span class="asset-name">
                                                    ${escapeHTML(assetName)}
                                                </span>

                                                <span class="sub-text">
                                                    ${escapeHTML(assetId)}
                                                    ${type ? " · " + escapeHTML(type) : ""}
                                                </span>
                                            </td>

                                            <td>
                                                ${escapeHTML(building)}

                                                ${
                                                    block
                                                        ? `<span class="sub-text">${escapeHTML(block)}</span>`
                                                        : ""
                                                }
                                            </td>

                                            <td>
                                                ${numberValue(firstDefined(row, ["temperature_c", "temperature"], null), 1)}
                                                °C
                                            </td>

                                            <td>
                                                ${numberValue(firstDefined(row, ["vibration_mm_s", "vibration"], null), 2)}
                                                mm/s
                                            </td>

                                            <td>
                                                ${numberValue(firstDefined(row, ["pressure_bar", "pressure"], null), 2)}
                                                bar
                                            </td>

                                            <td>
                                                ${numberValue(firstDefined(row, ["power_kw", "power"], null), 1)}
                                                kW
                                            </td>

                                            <td>
                                                ${numberValue(firstDefined(row, ["age_years", "age"], null), 1)}
                                                yr
                                            </td>

                                            <td>
                                                ${integerValue(firstDefined(row, ["days_since_service"], null))}
                                                days
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
            "Unable to load asset monitoring data."
        );

    }

}


/* ============================================================
   EQUIPMENT HEALTH
   ============================================================ */

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


        if (
            rows.length === 0
        ) {

            showEmpty(
                "equipmentHealthTable",
                "No Health Data",
                "No equipment health scores are currently available."
            );


            drawMaintenanceHealthChart(
                []
            );


            return;

        }


        drawMaintenanceHealthChart(
            rows
        );


        container.innerHTML =
            `
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

                                    const assetId =
                                        firstDefined(
                                            row,
                                            [
                                                "asset_id",
                                                "id"
                                            ],
                                            "--"
                                        );


                                    const assetName =
                                        firstDefined(
                                            row,
                                            [
                                                "asset_name",
                                                "name"
                                            ],
                                            "Equipment"
                                        );


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
                                                "probability",
                                                "risk_probability"
                                            ],
                                            null
                                        );


                                    return `
                                        <tr>

                                            <td>
                                                <span class="asset-name">
                                                    ${escapeHTML(assetName)}
                                                </span>

                                                <span class="sub-text">
                                                    ${escapeHTML(assetId)}
                                                </span>
                                            </td>

                                            <td>
                                                ${escapeHTML(firstDefined(row, ["asset_type", "type"], "--"))}
                                            </td>

                                            <td>
                                                ${escapeHTML(firstDefined(row, ["building_name", "building"], "--"))}
                                            </td>

                                            <td class="health-cell">

                                                <div class="health-value">
                                                    ${numberValue(health, 1)}
                                                </div>

                                                <div class="health-track">

                                                    <div
                                                        class="health-fill"
                                                        style="width:${Math.max(0, Math.min(100, health))}%"
                                                    ></div>

                                                </div>

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
                                                            row.maintenance_probability_percent !== undefined &&
                                                            row.maintenance_probability_percent !== null
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

        console.error(
            "Equipment health failed:",
            error
        );


        showError(
            "equipmentHealthTable",
            "Unable to load equipment health scores."
        );

    }

}


function drawMaintenanceHealthChart(
    rows
) {

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


    if (
        rows.length === 0
    ) {

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


    layout.height =
        350;


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
                    "%{x}<br>Health: %{y:.1f}/100<extra></extra>"
            }
        ],
        layout,
        plotConfig
    );

}


/* ============================================================
   BUILDING HEALTH COMPARISON
   ============================================================ */

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


        if (
            rows.length === 0
        ) {

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


        layout.height =
            350;


        layout.showlegend =
            false;


        layout.yaxis = {
            ...layout.yaxis,

            title:
                "Average Health",

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
                            COLORS.hvac
                    },

                    hovertemplate:
                        "%{x}<br>Health: %{y:.1f}/100<extra></extra>"
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


        if (
            rows.length === 0
        ) {

            showEmpty(
                "maintenanceScheduleTable",
                "No Maintenance Schedule",
                "No maintenance schedule is currently available."
            );

            return;

        }


        container.innerHTML =
            `
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


                                    const health =
                                        firstDefined(
                                            row,
                                            [
                                                "equipment_health_score",
                                                "health_score"
                                            ],
                                            null
                                        );


                                    const risk =
                                        firstDefined(
                                            row,
                                            [
                                                "maintenance_probability_percent",
                                                "maintenance_probability",
                                                "maintenance_risk",
                                                "probability",
                                                "risk_probability"
                                            ],
                                            null
                                        );


                                    const serviceDate =
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
                                                ${
                                                    health === null
                                                        ? "--"
                                                        : numberValue(health, 1)
                                                }
                                            </td>

                                            <td>
                                                ${
                                                    risk === null
                                                        ? "--"
                                                        : (
                                                            row.maintenance_probability_percent !== undefined &&
                                                            row.maintenance_probability_percent !== null
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
                                                ${escapeHTML(dateValue(serviceDate))}
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

        console.error(
            "Maintenance schedule failed:",
            error
        );


        showError(
            "maintenanceScheduleTable",
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


        if (
            alerts.length === 0
        ) {

            showEmpty(
                "maintenanceAlerts",
                "No Maintenance Alerts",
                "No active equipment maintenance alerts are currently stored."
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
                                    "asset_name"
                                ],
                                "Maintenance Alert"
                            );


                        const assetId =
                            firstDefined(
                                alert,
                                [
                                    "asset_id"
                                ],
                                ""
                            );


                        const message =
                            firstDefined(
                                alert,
                                [
                                    "message",
                                    "description",
                                    "recommendation"
                                ],
                                "Equipment requires maintenance review."
                            );


                        const created =
                            firstDefined(
                                alert,
                                [
                                    "created_at",
                                    "timestamp",
                                    "detected_at"
                                ],
                                ""
                            );


                        return `
                            <article class="maintenance-alert-card">

                                <div class="card-topline">

                                    <h3 class="card-title">
                                        ${escapeHTML(title)}
                                    </h3>

                                    <span class="priority-badge ${priorityClass(priority)}">
                                        ${escapeHTML(priority)}
                                    </span>

                                </div>

                                <div class="card-meta">

                                    ${
                                        assetId
                                            ? escapeHTML(assetId)
                                            : "Equipment Alert"
                                    }

                                    ${
                                        created
                                            ? " · " + escapeHTML(timestampValue(created))
                                            : ""
                                    }

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
            "Maintenance alerts failed:",
            error
        );


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


        if (
            orders.length === 0
        ) {

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


                        const status =
                            normalizeStatus(
                                firstDefined(
                                    order,
                                    [
                                        "status",
                                        "work_order_status"
                                    ],
                                    "OPEN"
                                )
                            );


                        const assetName =
                            firstDefined(
                                order,
                                [
                                    "asset_name",
                                    "title"
                                ],
                                "Equipment Work Order"
                            );


                        const assetId =
                            firstDefined(
                                order,
                                [
                                    "asset_id"
                                ],
                                ""
                            );


                        const dueDate =
                            firstDefined(
                                order,
                                [
                                    "due_date",
                                    "scheduled_date",
                                    "recommended_service_date"
                                ],
                                ""
                            );


                        const description =
                            firstDefined(
                                order,
                                [
                                    "description",
                                    "message",
                                    "recommended_action",
                                    "recommendation"
                                ],
                                "Perform recommended equipment maintenance."
                            );


                        return `
                            <article class="work-order-card">

                                <div class="card-topline">

                                    <h3 class="card-title">
                                        ${escapeHTML(assetName)}
                                    </h3>

                                    <span class="priority-badge ${priorityClass(priority)}">
                                        ${escapeHTML(priority)}
                                    </span>

                                </div>

                                <div class="card-meta">

                                    ${
                                        assetId
                                            ? escapeHTML(assetId) + " · "
                                            : ""
                                    }

                                    Status:
                                    ${escapeHTML(status)}

                                    ${
                                        dueDate
                                            ? " · Due " + escapeHTML(dateValue(dueDate))
                                            : ""
                                    }

                                </div>

                                <p class="card-message">
                                    ${escapeHTML(description)}
                                </p>

                            </article>
                        `;

                    }
                )
                .join("");


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
   REFRESH
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
            refreshMaintenanceData()
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
        "maintenanceBuildingChart"
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