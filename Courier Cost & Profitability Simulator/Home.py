"""
Home page for the Courier Cost Intelligence application.

Responsibilities
----------------
- Configure the Streamlit page
- Initialise session state
- Introduce the application
- Display workflow progress
- Provide navigation to all analysis pages
- Display saved-analysis overview
- Reset the complete analysis

This page must not contain:
- Cost calculations
- Parcel calculations
- Route calculations
- Fleet-sizing calculations
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.components import (
    divider,
    empty_state,
    info_box,
    metric_cards,
    note_box,
    page_header,
    section_title,
    status_box,
    subsection_title,
)

from utils.formatting import (
    format_date,
    format_integer,
    format_percentage,
    format_rm,
    format_route,
)

from utils.page_configuration import (
    setup_page,
)

from utils.session import (
    APP_METADATA_KEY,
    PAGE_DISPLAY_NAMES,
    PAGE_SEQUENCE,
    calculate_workflow_progress,
    get_cost_per_parcel,
    get_fleet_capacity,
    get_latest_completed_page,
    get_operating_cost,
    get_page_data,
    get_profitability,
    get_route_intelligence,
    get_scenario_simulation,
    get_session_snapshot,
    get_shipment_information,
    get_workflow_status,
    initialise_session_state,
    reset_application,
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================
setup_page(
    page_title="Courier Cost Intelligence",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialise_session_state()


# =========================================================
# PAGE CONSTANTS
# =========================================================
PAGE_LINKS = {
    "shipment_information": (
        "pages/1_Shipment_Information.py"
    ),
    "route_intelligence": (
        "pages/2_Route_Intelligence.py"
    ),
    "parcel_assessment": (
        "pages/3_Parcel_Assessment.py"
    ),
    "fleet_capacity": (
        "pages/4_Fleet_Capacity.py"
    ),
    "operating_cost": (
        "pages/5_Operating_Cost.py"
    ),
    "cost_per_parcel": (
        "pages/6_Cost_Per_Parcel.py"
    ),
    "profitability": (
        "pages/7_Profitability.py"
    ),
    "scenario_simulation": (
        "pages/8_Scenario_Simulation.py"
    ),
    "management_dashboard": (
        "pages/9_Management_Dashboard.py"
    ),
}


PAGE_ICONS = {
    "shipment_information": "📦",
    "route_intelligence": "🗺️",
    "parcel_assessment": "📐",
    "fleet_capacity": "🚛",
    "operating_cost": "💰",
    "cost_per_parcel": "🧮",
    "profitability": "📈",
    "scenario_simulation": "🧪",
    "management_dashboard": "📊",
}


PAGE_DESCRIPTIONS = {
    "shipment_information": (
        "Enter the shipment profile, parcel quantity, "
        "shipment frequency and operating assumptions."
    ),
    "route_intelligence": (
        "Evaluate the route, service level, distance, journey "
        "time and feasible vehicle types."
    ),
    "parcel_assessment": (
        "Calculate parcel volume, volumetric weight, chargeable "
        "weight, density and parcel compliance."
    ),
    "fleet_capacity": (
        "Determine vehicle requirements based on parcel, weight "
        "and volume constraints."
    ),
    "operating_cost": (
        "Calculate fuel, manpower, maintenance, toll, financing "
        "and allocated fixed operating costs."
    ),
    "cost_per_parcel": (
        "Convert shipment operating costs into parcel, weight, "
        "volume, vehicle and distance unit costs."
    ),
    "profitability": (
        "Evaluate selling price, revenue, profit, margin, markup "
        "and break-even performance."
    ),
    "scenario_simulation": (
        "Compare changes in volume, fuel rates, operating costs "
        "and selling prices."
    ),
    "management_dashboard": (
        "Review consolidated management results, recommendations "
        "and export the complete analysis."
    ),
}


# =========================================================
# HELPER FUNCTIONS
# =========================================================
def render_sidebar() -> None:
    """
    Display application navigation and workflow progress.
    """

    workflow = calculate_workflow_progress()

    with st.sidebar:
        st.markdown(
            """
            <div style="
                color:#1E3A8A;
                font-size:22px;
                font-weight:700;
                margin-bottom:3px;
            ">
                🚚 Courier Cost Intelligence
            </div>

            <div style="
                color:#475569;
                font-size:13px;
                margin-bottom:18px;
            ">
                End-to-end courier cost and profitability analysis
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.progress(
            workflow["progress_ratio"]
        )

        st.caption(
            f'{workflow["completed_pages"]} of '
            f'{workflow["total_pages"]} analysis pages completed'
        )

        st.markdown("---")

        st.page_link(
            "Home.py",
            label="Home",
            icon="🏠",
        )

        for page_key in PAGE_SEQUENCE:
            completed = st.session_state[
                "page_status"
            ].get(
                page_key,
                False,
            )

            status_icon = (
                "✅"
                if completed
                else PAGE_ICONS[
                    page_key
                ]
            )

            st.page_link(
                PAGE_LINKS[
                    page_key
                ],
                label=PAGE_DISPLAY_NAMES[
                    page_key
                ],
                icon=status_icon,
            )

        st.page_link(
            PAGE_LINKS[
                "management_dashboard"
            ],
            label="Management Dashboard",
            icon="📊",
        )

        st.markdown("---")

        st.caption(
            "Complete the analysis pages in sequence to ensure "
            "that all dependent calculations remain current."
        )


def render_workflow_card(
    page_number: int,
    page_key: str,
    completed: bool,
    updated_at: str | None,
) -> None:
    """
    Display one workflow page card.
    """

    page_name = PAGE_DISPLAY_NAMES[
        page_key
    ]

    page_icon = PAGE_ICONS[
        page_key
    ]

    status_text = (
        "Completed"
        if completed
        else "Pending"
    )

    status_class = (
        "status-success"
        if completed
        else "status-warning"
    )

    updated_text = (
        f"Last saved: {updated_at}"
        if updated_at
        else "No saved result"
    )

    st.markdown(
        f"""
        <div class="summary-card">
            <div style="
                display:flex;
                justify-content:space-between;
                gap:12px;
                align-items:flex-start;
            ">
                <div>
                    <div class="summary-card-title">
                        Step {page_number}
                    </div>

                    <div style="
                        color:#1E3A8A;
                        font-size:17px;
                        font-weight:700;
                        margin-bottom:7px;
                    ">
                        {page_icon} {page_name}
                    </div>
                </div>

                <span class="status-badge {status_class}">
                    {status_text}
                </span>
            </div>

            <div style="
                color:#475569;
                font-size:13px;
                line-height:1.5;
                min-height:40px;
                margin-bottom:10px;
            ">
                {PAGE_DESCRIPTIONS[page_key]}
            </div>

            <div class="summary-card-note">
                {updated_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    button_label = (
        f"Review {page_name}"
        if completed
        else f"Start {page_name}"
    )

    st.page_link(
        PAGE_LINKS[
            page_key
        ],
        label=button_label,
        icon=(
            "📂"
            if completed
            else "➡️"
        ),
        use_container_width=True,
    )


def get_analysis_summary() -> dict:
    """
    Create a concise summary from the current saved analysis.
    """

    shipment = get_shipment_information()
    route = get_route_intelligence()
    fleet = get_fleet_capacity()
    operating_cost = get_operating_cost()
    cost_per_parcel = get_cost_per_parcel()
    profitability = get_profitability()
    scenarios = get_scenario_simulation()

    return {
        "shipment_reference": shipment.get(
            "shipment_reference",
            shipment.get(
                "shipment_id",
                "Not Available",
            ),
        ),
        "route": format_route(
            route.get(
                "origin_state",
                shipment.get(
                    "origin_state",
                    "Not Available",
                ),
            ),
            route.get(
                "destination_state",
                shipment.get(
                    "destination_state",
                    "Not Available",
                ),
            ),
        ),
        "service_level": route.get(
            "service_level",
            shipment.get(
                "service_level",
                "Not Available",
            ),
        ),
        "parcel_quantity": shipment.get(
            "parcel_quantity",
            get_page_data(
                "parcel_assessment"
            ).get(
                "parcel_quantity",
                0,
            ),
        ),
        "vehicle_type": fleet.get(
            "selected_vehicle_type",
            fleet.get(
                "vehicle_type",
                fleet.get(
                    "recommended_vehicle_type",
                    "Not Available",
                ),
            ),
        ),
        "planned_fleet_size": fleet.get(
            "planned_fleet_size",
            0,
        ),
        "operating_cost": operating_cost.get(
            "total_operating_cost_per_shipment",
            0,
        ),
        "cost_per_parcel": cost_per_parcel.get(
            "total_cost_per_parcel",
            0,
        ),
        "selling_price_per_parcel": profitability.get(
            "selling_price_per_parcel",
            profitability.get(
                "final_selling_price_per_parcel",
                0,
            ),
        ),
        "profit_per_shipment": profitability.get(
            "profit_per_shipment",
            0,
        ),
        "profit_margin_pct": profitability.get(
            "profit_margin_pct",
            0,
        ),
        "scenario_count": len(
            scenarios.get(
                "scenarios",
                scenarios.get(
                    "scenario_results",
                    [],
                ),
            )
        ),
    }


# =========================================================
# SIDEBAR
# =========================================================
render_sidebar()


# =========================================================
# PAGE HEADER
# =========================================================
page_header(
    title="Courier Cost Intelligence",
    subtitle=(
        "Evaluate shipment requirements, route feasibility, "
        "fleet capacity, operating costs, parcel economics and "
        "commercial profitability through one controlled workflow."
    ),
    icon="🚚",
)


# =========================================================
# INTRODUCTION
# =========================================================
info_box(
    title="Purpose of the Application",
    message=(
        "This application provides an end-to-end framework for "
        "evaluating courier operations. It converts shipment and "
        "route assumptions into fleet requirements, operating costs, "
        "unit economics, pricing and management recommendations."
    ),
)


# =========================================================
# WORKFLOW PROGRESS
# =========================================================
workflow = calculate_workflow_progress()
latest_completed_page = get_latest_completed_page()

section_title(
    "Analysis Progress"
)

progress_col, completed_col, pending_col, latest_col = (
    st.columns(
        4
    )
)

with progress_col:
    st.metric(
        label="Overall Progress",
        value=format_percentage(
            workflow[
                "progress_pct"
            ],
            decimal_places=0,
        ),
    )

with completed_col:
    st.metric(
        label="Completed Pages",
        value=(
            f'{workflow["completed_pages"]}'
            f' / {workflow["total_pages"]}'
        ),
    )

with pending_col:
    pending_pages = (
        workflow["total_pages"]
        - workflow["completed_pages"]
    )

    st.metric(
        label="Pending Pages",
        value=format_integer(
            pending_pages
        ),
    )

with latest_col:
    st.metric(
        label="Latest Completed",
        value=(
            latest_completed_page[
                "page_name"
            ]
            if latest_completed_page
            else "None"
        ),
    )

st.progress(
    workflow[
        "progress_ratio"
    ]
)

if workflow["completed_pages"] == 0:
    note_box(
        title="Start the Analysis",
        message=(
            "Begin with Shipment Information. The data saved on "
            "that page will be used by all subsequent calculations."
        ),
    )

elif workflow["completed_pages"] < workflow["total_pages"]:
    next_page_key = next(
        (
            page_key
            for page_key in PAGE_SEQUENCE
            if not st.session_state[
                "page_status"
            ].get(
                page_key,
                False,
            )
        ),
        None,
    )

    if next_page_key:
        note_box(
            title="Recommended Next Step",
            message=(
                f'Continue with '
                f'{PAGE_DISPLAY_NAMES[next_page_key]} '
                "to progress the analysis."
            ),
        )

else:
    status_box(
        status="success",
        title="Analysis Complete",
        message=(
            "All analysis pages are complete. Review the "
            "Management Dashboard to confirm the recommendation "
            "and export the complete workbook."
        ),
    )


# =========================================================
# CURRENT ANALYSIS SUMMARY
# =========================================================
section_title(
    "Current Analysis"
)

if workflow["completed_pages"] == 0:
    empty_state(
        title="No Saved Analysis",
        message=(
            "No shipment analysis has been saved in the current "
            "session. Start by entering the shipment information."
        ),
        icon="📦",
    )

    st.page_link(
        PAGE_LINKS[
            "shipment_information"
        ],
        label="Start Shipment Information",
        icon="➡️",
        use_container_width=True,
    )

else:
    analysis_summary = get_analysis_summary()

    summary_col_1, summary_col_2 = st.columns(
        2
    )

    with summary_col_1:
        subsection_title(
            "Shipment and Route"
        )

        shipment_summary_df = pd.DataFrame(
            [
                {
                    "Item": "Shipment Reference",
                    "Value": analysis_summary[
                        "shipment_reference"
                    ],
                },
                {
                    "Item": "Route",
                    "Value": analysis_summary[
                        "route"
                    ],
                },
                {
                    "Item": "Service Level",
                    "Value": analysis_summary[
                        "service_level"
                    ],
                },
                {
                    "Item": "Parcel Quantity",
                    "Value": format_integer(
                        analysis_summary[
                            "parcel_quantity"
                        ]
                    ),
                },
                {
                    "Item": "Selected Vehicle",
                    "Value": analysis_summary[
                        "vehicle_type"
                    ],
                },
                {
                    "Item": "Planned Fleet Size",
                    "Value": format_integer(
                        analysis_summary[
                            "planned_fleet_size"
                        ]
                    ),
                },
            ]
        )

        st.dataframe(
            shipment_summary_df,
            hide_index=True,
            use_container_width=True,
        )

    with summary_col_2:
        subsection_title(
            "Cost and Profitability"
        )

        commercial_summary_df = pd.DataFrame(
            [
                {
                    "Item": "Operating Cost per Shipment",
                    "Value": format_rm(
                        analysis_summary[
                            "operating_cost"
                        ]
                    ),
                },
                {
                    "Item": "Cost per Parcel",
                    "Value": format_rm(
                        analysis_summary[
                            "cost_per_parcel"
                        ]
                    ),
                },
                {
                    "Item": "Selling Price per Parcel",
                    "Value": format_rm(
                        analysis_summary[
                            "selling_price_per_parcel"
                        ]
                    ),
                },
                {
                    "Item": "Profit per Shipment",
                    "Value": format_rm(
                        analysis_summary[
                            "profit_per_shipment"
                        ],
                        show_negative_parentheses=True,
                    ),
                },
                {
                    "Item": "Profit Margin",
                    "Value": format_percentage(
                        analysis_summary[
                            "profit_margin_pct"
                        ]
                    ),
                },
                {
                    "Item": "Scenarios Assessed",
                    "Value": format_integer(
                        analysis_summary[
                            "scenario_count"
                        ]
                    ),
                },
            ]
        )

        st.dataframe(
            commercial_summary_df,
            hide_index=True,
            use_container_width=True,
        )


# =========================================================
# ANALYSIS WORKFLOW
# =========================================================
section_title(
    "Analysis Workflow"
)

workflow_status = get_workflow_status()

for row_start in range(
    0,
    len(workflow_status),
    3,
):
    row_records = workflow_status[
        row_start:
        row_start + 3
    ]

    columns = st.columns(
        3
    )

    for column, page_record in zip(
        columns,
        row_records,
    ):
        with column:
            render_workflow_card(
                page_number=page_record[
                    "page_number"
                ],
                page_key=page_record[
                    "page_key"
                ],
                completed=page_record[
                    "completed"
                ],
                updated_at=page_record[
                    "updated_at"
                ],
            )


# =========================================================
# MANAGEMENT DASHBOARD
# =========================================================
section_title(
    "Management Dashboard"
)

dashboard_requirements = [
    "shipment_information",
    "route_intelligence",
    "parcel_assessment",
    "fleet_capacity",
    "operating_cost",
    "cost_per_parcel",
    "profitability",
]

dashboard_ready = all(
    st.session_state[
        "page_status"
    ].get(
        page_key,
        False,
    )
    for page_key in dashboard_requirements
)

if dashboard_ready:
    status_box(
        status="success",
        title="Dashboard Available",
        message=(
            "The core analysis is complete. Open the Management "
            "Dashboard to review consolidated results, commercial "
            "recommendations and the Excel export."
        ),
    )

    st.page_link(
        PAGE_LINKS[
            "management_dashboard"
        ],
        label="Open Management Dashboard",
        icon="📊",
        use_container_width=True,
    )

else:
    incomplete_dashboard_pages = [
        PAGE_DISPLAY_NAMES[
            page_key
        ]
        for page_key in dashboard_requirements
        if not st.session_state[
            "page_status"
        ].get(
            page_key,
            False,
        )
    ]

    status_box(
        status="warning",
        title="Dashboard Not Yet Available",
        message=(
            "Complete the following pages first: "
            + ", ".join(
                incomplete_dashboard_pages
            )
            + "."
        ),
    )


# =========================================================
# APPLICATION GUIDANCE
# =========================================================
section_title(
    "How to Use the Application"
)

guidance_col_1, guidance_col_2, guidance_col_3 = (
    st.columns(
        3
    )
)

with guidance_col_1:
    note_box(
        title="1. Enter Assumptions",
        message=(
            "Start with shipment, parcel and route information. "
            "Use realistic operational assumptions and verify "
            "the selected master-data records."
        ),
    )

with guidance_col_2:
    note_box(
        title="2. Review Calculations",
        message=(
            "Review the recommended vehicle, fleet capacity, "
            "operating cost and unit-cost results before moving "
            "to pricing and profitability."
        ),
    )

with guidance_col_3:
    note_box(
        title="3. Compare Scenarios",
        message=(
            "Use scenario simulation to test changes in volume, "
            "fuel rates, selling price and operating costs before "
            "finalising the recommendation."
        ),
    )


# =========================================================
# SESSION INFORMATION
# =========================================================
section_title(
    "Session Information"
)

session_metadata = st.session_state.get(
    APP_METADATA_KEY,
    {},
)

session_col_1, session_col_2, session_col_3 = (
    st.columns(
        3
    )
)

with session_col_1:
    st.metric(
        label="Application Version",
        value=session_metadata.get(
            "application_version",
            "1.0",
        ),
    )

with session_col_2:
    st.metric(
        label="Session Started",
        value=(
            session_metadata.get(
                "session_started_at",
                "Not Available",
            )
            or "Not Available"
        ),
    )

with session_col_3:
    st.metric(
        label="Last Updated",
        value=(
            session_metadata.get(
                "last_updated_at",
                "Not Available",
            )
            or "Not Available"
        ),
    )


# =========================================================
# RESET ANALYSIS
# =========================================================
divider()

with st.expander(
    "Reset Complete Analysis",
    expanded=False,
):
    st.warning(
        "Resetting the analysis will permanently clear all "
        "saved page results in the current Streamlit session."
    )

    confirm_reset = st.checkbox(
        "I understand that all current analysis data will be cleared.",
        key="confirm_complete_reset",
    )

    reset_clicked = st.button(
        "Reset Complete Analysis",
        type="primary",
        disabled=not confirm_reset,
        use_container_width=True,
    )

    if reset_clicked:
        reset_application()

        st.success(
            "The complete analysis has been reset."
        )

        st.rerun()


# =========================================================
# FOOTNOTE
# =========================================================
st.caption(
    "Courier Cost Intelligence is a planning and decision-support "
    "application. Final operational and commercial decisions should "
    "be reviewed against approved company policies, contracts, "
    "master data and current market conditions."
)