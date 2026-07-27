from datetime import datetime
import io

import pandas as pd
import streamlit as st

from utils.page_configuration import page_config, page_style
from utils.components import cost_basis


# =========================================================
# PAGE CONFIGURATION
# =========================================================
page_config()
page_style()


# =========================================================
# REQUIRED SESSION-STATE DATA
# =========================================================
shipment = st.session_state.get(
    "shipment_information",
    {},
)

route = st.session_state.get(
    "route_intelligence",
    {},
)

parcel = st.session_state.get(
    "parcel_assessment",
    {},
)

fleet = st.session_state.get(
    "fleet_capacity",
    {},
)

operating_cost = st.session_state.get(
    "operating_cost",
    {},
)

cost_per_parcel = st.session_state.get(
    "cost_per_parcel",
    {},
)

profitability = st.session_state.get(
    "profitability",
    {},
)

scenario_simulation = st.session_state.get(
    "scenario_simulation",
    {},
)


required_pages = {
    "Shipment Information": shipment,
    "Route Intelligence": route,
    "Parcel Assessment": parcel,
    "Fleet Capacity": fleet,
    "Operating Cost": operating_cost,
    "Cost per Parcel": cost_per_parcel,
    "Profitability": profitability,
    "Scenario Simulation": scenario_simulation,
}


incomplete_pages = [
    page_name
    for page_name, page_data in required_pages.items()
    if not page_data
]


if incomplete_pages:
    st.warning(
        "Complete and save the following pages before viewing "
        "the Management Dashboard: "
        + ", ".join(incomplete_pages)
    )

    st.stop()


# =========================================================
# HELPER FUNCTIONS
# =========================================================
def safe_float(
    value,
    default: float = 0.0,
) -> float:
    """
    Safely convert a value to float.
    """

    try:
        if value is None:
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def safe_int(
    value,
    default: int = 0,
) -> int:
    """
    Safely convert a value to integer.
    """

    try:
        if value is None:
            return default

        return int(round(float(value)))

    except (TypeError, ValueError):
        return default


def format_currency(
    value: float,
) -> str:
    """
    Format numeric values as Malaysian Ringgit.
    """

    return f"RM {safe_float(value):,.2f}"


def format_percentage(
    value: float,
) -> str:
    """
    Format numeric values as percentages.
    """

    return f"{safe_float(value):,.1f}%"


def profitability_status_message(
    profit_value: float,
    margin_pct: float,
) -> tuple[str, str]:
    """
    Return management-level profitability status.
    """

    if profit_value < 0:
        return (
            "Critical",
            (
                "The current pricing and operating structure "
                "results in a loss."
            ),
        )

    if margin_pct < 5:
        return (
            "Watch",
            (
                "The service is profitable, but the margin is "
                "too low to absorb material cost changes."
            ),
        )

    if margin_pct < 15:
        return (
            "Moderate",
            (
                "The service is profitable with a moderate "
                "commercial margin."
            ),
        )

    if margin_pct < 30:
        return (
            "Healthy",
            (
                "The service generates a healthy operating "
                "margin under the current assumptions."
            ),
        )

    return (
        "Strong",
        (
            "The service generates a strong margin. Confirm "
            "that the price remains commercially competitive."
        ),
    )


def utilisation_status_message(
    utilisation_pct: float,
) -> tuple[str, str]:
    """
    Return management-level fleet-utilisation status.
    """

    if utilisation_pct < 40:
        return (
            "Low",
            (
                "The selected fleet is underutilised. Vehicle "
                "downsizing or shipment consolidation should "
                "be considered."
            ),
        )

    if utilisation_pct < 65:
        return (
            "Moderate",
            (
                "The fleet has material spare capacity that "
                "could absorb additional volume."
            ),
        )

    if utilisation_pct < 85:
        return (
            "Efficient",
            (
                "The fleet has an appropriate balance between "
                "utilisation and operating flexibility."
            ),
        )

    return (
        "High",
        (
            "The fleet is highly utilised, with limited spare "
            "capacity for operational disruption or volume growth."
        ),
    )


# =========================================================
# READ SHIPMENT AND ROUTE DATA
# =========================================================
origin_region = shipment.get(
    "origin_region",
    "",
)

origin_state = shipment.get(
    "origin_state",
    "",
)

destination_region = shipment.get(
    "destination_region",
    "",
)

destination_state = shipment.get(
    "destination_state",
    "",
)

service_level = shipment.get(
    "service_level",
    "",
)

parcel_type = parcel.get(
    "parcel_type",
    "",
)

route_id = route.get(
    "route_id",
    "",
)

route_category = route.get(
    "route_category",
    "",
)

target_delivery = route.get(
    "target_delivery",
    "",
)

route_priority = route.get(
    "priority",
    "",
)

total_trip_distance_km = safe_float(
    route.get(
        "total_trip_distance_km",
        0,
    )
)

estimated_journey_hours = safe_float(
    route.get(
        "estimated_total_journey_hours",
        0,
    )
)


# =========================================================
# READ PARCEL DATA
# =========================================================
parcel_quantity = safe_int(
    parcel.get(
        "parcel_quantity",
        0,
    )
)

weight_per_parcel_kg = safe_float(
    parcel.get(
        "weight_per_parcel_kg",
        0,
    )
)

total_actual_weight_kg = safe_float(
    parcel.get(
        "total_actual_weight_kg",
        0,
    )
)

total_volumetric_weight_kg = safe_float(
    parcel.get(
        "total_volumetric_weight_kg",
        0,
    )
)

chargeable_weight_kg = safe_float(
    parcel.get(
        "chargeable_weight_kg",
        0,
    )
)

chargeable_weight_basis = parcel.get(
    "chargeable_weight_basis",
    "",
)

total_volume_m3 = safe_float(
    parcel.get(
        "total_volume_m3",
        0,
    )
)

parcel_standard_compliant = bool(
    parcel.get(
        "parcel_standard_compliant",
        False,
    )
)


# =========================================================
# READ FLEET DATA
# =========================================================
vehicle_type = fleet.get(
    "selected_vehicle_type",
    "",
)

recommended_vehicle_type = fleet.get(
    "recommended_vehicle_type",
    "",
)

required_vehicles = safe_int(
    fleet.get(
        "required_vehicles",
        0,
    )
)

planned_fleet_size = safe_int(
    fleet.get(
        "planned_fleet_size",
        required_vehicles,
    )
)

additional_buffer_vehicles = safe_int(
    fleet.get(
        "additional_buffer_vehicles",
        0,
    )
)

capacity_constraint = fleet.get(
    "capacity_constraint",
    "",
)

overall_utilisation_pct = safe_float(
    fleet.get(
        "overall_utilisation_pct",
        0,
    )
)

parcel_utilisation_pct = safe_float(
    fleet.get(
        "parcel_utilisation_pct",
        0,
    )
)

weight_utilisation_pct = safe_float(
    fleet.get(
        "weight_utilisation_pct",
        0,
    )
)

volume_utilisation_pct = safe_float(
    fleet.get(
        "volume_utilisation_pct",
        0,
    )
)

availability_status = fleet.get(
    "availability_status",
    "",
)

fleet_shortfall = safe_int(
    fleet.get(
        "planned_fleet_shortfall",
        fleet.get(
            "fleet_shortfall",
            0,
        ),
    )
)


# =========================================================
# READ OPERATING-COST DATA
# =========================================================
shipments_per_month = safe_int(
    operating_cost.get(
        "shipments_per_month",
        0,
    )
)

fuel_cost_per_shipment = safe_float(
    operating_cost.get(
        "fuel_cost_per_shipment",
        0,
    )
)

toll_cost_per_shipment = safe_float(
    operating_cost.get(
        "toll_cost_per_shipment",
        0,
    )
)

maintenance_cost_per_shipment = safe_float(
    operating_cost.get(
        "maintenance_cost_per_shipment",
        0,
    )
)

tyre_cost_per_shipment = safe_float(
    operating_cost.get(
        "tyre_cost_per_shipment",
        0,
    )
)

overtime_cost_per_shipment = safe_float(
    operating_cost.get(
        "overtime_cost_per_shipment",
        0,
    )
)

direct_trip_cost = safe_float(
    operating_cost.get(
        "direct_trip_cost",
        0,
    )
)

allocated_fixed_cost_per_shipment = safe_float(
    operating_cost.get(
        "allocated_fixed_cost_per_shipment",
        0,
    )
)

total_operating_cost_per_shipment = safe_float(
    operating_cost.get(
        "total_operating_cost_per_shipment",
        0,
    )
)

total_monthly_operating_cost = safe_float(
    operating_cost.get(
        "total_monthly_operating_cost",
        0,
    )
)

monthly_regional_overhead = safe_float(
    operating_cost.get(
        "monthly_regional_overhead",
        0,
    )
)


# =========================================================
# READ UNIT-COST DATA
# =========================================================
direct_cost_per_parcel = safe_float(
    cost_per_parcel.get(
        "direct_cost_per_parcel",
        0,
    )
)

fixed_cost_per_parcel = safe_float(
    cost_per_parcel.get(
        "fixed_cost_per_parcel",
        0,
    )
)

total_cost_per_parcel = safe_float(
    cost_per_parcel.get(
        "total_cost_per_parcel",
        0,
    )
)

cost_per_actual_kg = safe_float(
    cost_per_parcel.get(
        "cost_per_actual_kg",
        0,
    )
)

cost_per_chargeable_kg = safe_float(
    cost_per_parcel.get(
        "cost_per_chargeable_kg",
        0,
    )
)

cost_per_cubic_metre = safe_float(
    cost_per_parcel.get(
        "cost_per_cubic_metre",
        0,
    )
)

cost_per_vehicle_km = safe_float(
    cost_per_parcel.get(
        "cost_per_vehicle_km",
        0,
    )
)

monthly_parcel_quantity = safe_int(
    cost_per_parcel.get(
        "monthly_parcel_quantity",
        parcel_quantity * shipments_per_month,
    )
)


# =========================================================
# READ PROFITABILITY DATA
# =========================================================
pricing_method = profitability.get(
    "pricing_method",
    "",
)

net_selling_price_per_parcel = safe_float(
    profitability.get(
        "net_selling_price_per_parcel",
        0,
    )
)

total_revenue_per_shipment = safe_float(
    profitability.get(
        "total_revenue_per_shipment",
        0,
    )
)

profit_per_parcel = safe_float(
    profitability.get(
        "profit_per_parcel",
        0,
    )
)

profit_per_shipment = safe_float(
    profitability.get(
        "profit_per_shipment",
        0,
    )
)

profit_margin_pct = safe_float(
    profitability.get(
        "profit_margin_pct",
        0,
    )
)

markup_on_cost_pct = safe_float(
    profitability.get(
        "markup_on_cost_pct",
        0,
    )
)

monthly_revenue = safe_float(
    profitability.get(
        "monthly_revenue",
        0,
    )
)

monthly_profit = safe_float(
    profitability.get(
        "monthly_profit",
        0,
    )
)

break_even_price_per_parcel = safe_float(
    profitability.get(
        "break_even_price_per_parcel",
        total_cost_per_parcel,
    )
)

target_selling_price_per_parcel = safe_float(
    profitability.get(
        "target_selling_price_per_parcel",
        0,
    )
)

analysis_target_margin_pct = safe_float(
    profitability.get(
        "analysis_target_margin_pct",
        0,
    )
)


# =========================================================
# READ SCENARIO DATA
# =========================================================
selected_scenario_name = scenario_simulation.get(
    "selected_scenario",
    "",
)

selected_scenario = scenario_simulation.get(
    "selected_scenario_results",
    {},
)

scenario_records = scenario_simulation.get(
    "scenario_results",
    [],
)

best_profit_scenario = scenario_simulation.get(
    "best_profit_scenario",
    "",
)

best_margin_scenario = scenario_simulation.get(
    "best_margin_scenario",
    "",
)

lowest_cost_scenario = scenario_simulation.get(
    "lowest_cost_scenario",
    "",
)

highest_utilisation_scenario = scenario_simulation.get(
    "highest_utilisation_scenario",
    "",
)


scenario_df = pd.DataFrame(
    scenario_records
)


# =========================================================
# PAGE TITLE
# =========================================================
st.markdown(
    '<div class="main-title">📋 Management Dashboard</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-subtitle">
        Consolidated management view of route, parcel, fleet,
        operating cost, profitability and scenario performance.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# DASHBOARD BASIS
# =========================================================
cost_basis(
    "Management Dashboard Basis",
    """
    This dashboard consolidates the saved outputs from the complete
    courier cost-analysis workflow.

    The dashboard does not independently recalculate the underlying
    assumptions. Changes to route, parcel, fleet, operating cost or
    pricing assumptions should be made on the relevant assessment
    page and saved before returning here.
    """,
)


# =========================================================
# MANAGEMENT HEADER
# =========================================================
st.markdown(
    '<div class="section-title">Management Overview</div>',
    unsafe_allow_html=True,
)

header_col1, header_col2, header_col3, header_col4 = (
    st.columns(4)
)

with header_col1:
    st.markdown("**Route**")
    st.write(
        f"{origin_state} → {destination_state}"
    )

with header_col2:
    st.markdown("**Service Level**")
    st.write(service_level)

with header_col3:
    st.markdown("**Vehicle Type**")
    st.write(vehicle_type)

with header_col4:
    st.markdown("**Selected Scenario**")
    st.write(selected_scenario_name)


# =========================================================
# EXECUTIVE KPI CARDS
# =========================================================
st.markdown(
    '<div class="section-title">Executive KPI Summary</div>',
    unsafe_allow_html=True,
)

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = (
    st.columns(4)
)

with kpi_col1:
    st.metric(
        "Monthly Parcel Volume",
        f"{monthly_parcel_quantity:,}",
    )

with kpi_col2:
    st.metric(
        "Cost per Parcel",
        format_currency(
            total_cost_per_parcel
        ),
    )

with kpi_col3:
    st.metric(
        "Selling Price per Parcel",
        format_currency(
            net_selling_price_per_parcel
        ),
    )

with kpi_col4:
    st.metric(
        "Profit per Parcel",
        format_currency(
            profit_per_parcel
        ),
        delta=format_currency(
            profit_per_parcel
        ),
    )


kpi_col5, kpi_col6, kpi_col7, kpi_col8 = (
    st.columns(4)
)

with kpi_col5:
    st.metric(
        "Monthly Revenue",
        format_currency(
            monthly_revenue
        ),
    )

with kpi_col6:
    st.metric(
        "Monthly Operating Cost",
        format_currency(
            total_monthly_operating_cost
        ),
    )

with kpi_col7:
    st.metric(
        "Monthly Profit",
        format_currency(
            monthly_profit
        ),
        delta=format_currency(
            monthly_profit
        ),
    )

with kpi_col8:
    st.metric(
        "Profit Margin",
        format_percentage(
            profit_margin_pct
        ),
    )


# =========================================================
# OPERATIONAL PROFILE
# =========================================================
st.markdown(
    '<div class="section-title">Operational Profile</div>',
    unsafe_allow_html=True,
)

operation_col1, operation_col2, operation_col3, operation_col4 = (
    st.columns(4)
)

with operation_col1:
    st.metric(
        "Parcels per Shipment",
        f"{parcel_quantity:,}",
    )

with operation_col2:
    st.metric(
        "Shipments per Month",
        f"{shipments_per_month:,}",
    )

with operation_col3:
    st.metric(
        "Trip Distance",
        f"{total_trip_distance_km:,.1f} km",
    )

with operation_col4:
    st.metric(
        "Journey Time",
        f"{estimated_journey_hours:,.1f} hours",
    )


operation_col5, operation_col6, operation_col7, operation_col8 = (
    st.columns(4)
)

with operation_col5:
    st.metric(
        "Shipment Weight",
        f"{total_actual_weight_kg:,.2f} kg",
    )

with operation_col6:
    st.metric(
        "Shipment Volume",
        f"{total_volume_m3:,.3f} m³",
    )

with operation_col7:
    st.metric(
        "Required Fleet",
        f"{required_vehicles:,}",
    )

with operation_col8:
    st.metric(
        "Planned Fleet",
        f"{planned_fleet_size:,}",
    )


# =========================================================
# FLEET CAPACITY VIEW
# =========================================================
st.markdown(
    '<div class="section-title">Fleet Capacity and Utilisation</div>',
    unsafe_allow_html=True,
)

fleet_col1, fleet_col2, fleet_col3, fleet_col4 = (
    st.columns(4)
)

with fleet_col1:
    st.metric(
        "Parcel Utilisation",
        format_percentage(
            parcel_utilisation_pct
        ),
    )

with fleet_col2:
    st.metric(
        "Weight Utilisation",
        format_percentage(
            weight_utilisation_pct
        ),
    )

with fleet_col3:
    st.metric(
        "Volume Utilisation",
        format_percentage(
            volume_utilisation_pct
        ),
    )

with fleet_col4:
    st.metric(
        "Maximum Utilisation",
        format_percentage(
            overall_utilisation_pct
        ),
    )


utilisation_status, utilisation_message = (
    utilisation_status_message(
        overall_utilisation_pct
    )
)


fleet_status_col1, fleet_status_col2 = (
    st.columns(2)
)

with fleet_status_col1:
    st.markdown("**Controlling Capacity Constraint**")
    st.info(
        f"{capacity_constraint} determines the fleet "
        f"requirement of {required_vehicles:,} vehicle(s)."
    )

with fleet_status_col2:
    st.markdown("**Fleet Efficiency Status**")

    if utilisation_status in {
        "Efficient",
        "High",
    }:
        st.success(
            f"{utilisation_status}: "
            f"{utilisation_message}"
        )

    elif utilisation_status == "Moderate":
        st.info(
            f"{utilisation_status}: "
            f"{utilisation_message}"
        )

    else:
        st.warning(
            f"{utilisation_status}: "
            f"{utilisation_message}"
        )


if fleet_shortfall > 0:
    st.error(
        f"The planned fleet exceeds available fleet capacity by "
        f"{fleet_shortfall:,} vehicle(s)."
    )

elif availability_status:
    st.success(
        f"Fleet availability status: {availability_status}."
    )


# =========================================================
# COST STRUCTURE
# =========================================================
st.markdown(
    '<div class="section-title">Operating Cost Structure</div>',
    unsafe_allow_html=True,
)

cost_col1, cost_col2, cost_col3 = st.columns(3)

with cost_col1:
    st.metric(
        "Direct Cost per Shipment",
        format_currency(
            direct_trip_cost
        ),
    )

with cost_col2:
    st.metric(
        "Fixed Cost per Shipment",
        format_currency(
            allocated_fixed_cost_per_shipment
        ),
    )

with cost_col3:
    st.metric(
        "Total Cost per Shipment",
        format_currency(
            total_operating_cost_per_shipment
        ),
    )


cost_breakdown_df = pd.DataFrame(
    [
        {
            "Cost Item": "Fuel",
            "Cost per Shipment (RM)": (
                fuel_cost_per_shipment
            ),
        },
        {
            "Cost Item": "Toll",
            "Cost per Shipment (RM)": (
                toll_cost_per_shipment
            ),
        },
        {
            "Cost Item": "Maintenance",
            "Cost per Shipment (RM)": (
                maintenance_cost_per_shipment
            ),
        },
        {
            "Cost Item": "Tyres",
            "Cost per Shipment (RM)": (
                tyre_cost_per_shipment
            ),
        },
        {
            "Cost Item": "Overtime",
            "Cost per Shipment (RM)": (
                overtime_cost_per_shipment
            ),
        },
        {
            "Cost Item": "Allocated Fixed Cost",
            "Cost per Shipment (RM)": (
                allocated_fixed_cost_per_shipment
            ),
        },
    ]
)


cost_breakdown_df[
    "Share of Total (%)"
] = (
    cost_breakdown_df[
        "Cost per Shipment (RM)"
    ]
    / total_operating_cost_per_shipment
    * 100
    if total_operating_cost_per_shipment > 0
    else 0
)


chart_cost_data = cost_breakdown_df[
    [
        "Cost Item",
        "Cost per Shipment (RM)",
    ]
].set_index(
    "Cost Item"
)

st.bar_chart(
    chart_cost_data,
    use_container_width=True,
)


with st.expander(
    "View Detailed Operating Cost",
    expanded=False,
):
    cost_display = cost_breakdown_df.copy()

    cost_display[
        "Cost per Shipment (RM)"
    ] = cost_display[
        "Cost per Shipment (RM)"
    ].map(
        lambda value: f"{value:,.2f}"
    )

    cost_display[
        "Share of Total (%)"
    ] = cost_display[
        "Share of Total (%)"
    ].map(
        lambda value: f"{value:,.1f}%"
    )

    st.dataframe(
        cost_display,
        hide_index=True,
        use_container_width=True,
    )


# =========================================================
# UNIT COST SUMMARY
# =========================================================
st.markdown(
    '<div class="section-title">Unit Cost Summary</div>',
    unsafe_allow_html=True,
)

unit_col1, unit_col2, unit_col3, unit_col4 = (
    st.columns(4)
)

with unit_col1:
    st.metric(
        "Direct Cost per Parcel",
        format_currency(
            direct_cost_per_parcel
        ),
    )

with unit_col2:
    st.metric(
        "Fixed Cost per Parcel",
        format_currency(
            fixed_cost_per_parcel
        ),
    )

with unit_col3:
    st.metric(
        "Cost per Actual kg",
        format_currency(
            cost_per_actual_kg
        ),
    )

with unit_col4:
    st.metric(
        "Cost per Chargeable kg",
        format_currency(
            cost_per_chargeable_kg
        ),
    )


unit_col5, unit_col6 = st.columns(2)

with unit_col5:
    st.metric(
        "Cost per Cubic Metre",
        format_currency(
            cost_per_cubic_metre
        ),
    )

with unit_col6:
    st.metric(
        "Cost per Vehicle-km",
        format_currency(
            cost_per_vehicle_km
        ),
    )


# =========================================================
# PROFITABILITY SUMMARY
# =========================================================
st.markdown(
    '<div class="section-title">Commercial and Profitability Summary</div>',
    unsafe_allow_html=True,
)

profit_col1, profit_col2, profit_col3, profit_col4 = (
    st.columns(4)
)

with profit_col1:
    st.metric(
        "Revenue per Shipment",
        format_currency(
            total_revenue_per_shipment
        ),
    )

with profit_col2:
    st.metric(
        "Profit per Shipment",
        format_currency(
            profit_per_shipment
        ),
        delta=format_currency(
            profit_per_shipment
        ),
    )

with profit_col3:
    st.metric(
        "Profit Margin",
        format_percentage(
            profit_margin_pct
        ),
    )

with profit_col4:
    st.metric(
        "Mark-up on Cost",
        format_percentage(
            markup_on_cost_pct
        ),
    )


profitability_status, profitability_message = (
    profitability_status_message(
        profit_per_shipment,
        profit_margin_pct,
    )
)


commercial_col1, commercial_col2 = (
    st.columns(2)
)

with commercial_col1:
    st.markdown("**Profitability Status**")

    if profitability_status in {
        "Healthy",
        "Strong",
    }:
        st.success(
            f"{profitability_status}: "
            f"{profitability_message}"
        )

    elif profitability_status in {
        "Watch",
        "Moderate",
    }:
        st.warning(
            f"{profitability_status}: "
            f"{profitability_message}"
        )

    else:
        st.error(
            f"{profitability_status}: "
            f"{profitability_message}"
        )


with commercial_col2:
    st.markdown("**Pricing Position**")

    price_above_break_even = (
        net_selling_price_per_parcel
        - break_even_price_per_parcel
    )

    if price_above_break_even > 0:
        st.success(
            f"The selling price is "
            f"{format_currency(price_above_break_even)} "
            "per parcel above break-even."
        )

    elif price_above_break_even == 0:
        st.warning(
            "The selling price is equal to the break-even "
            "price. No profit buffer is available."
        )

    else:
        st.error(
            f"The selling price is "
            f"{format_currency(abs(price_above_break_even))} "
            "per parcel below break-even."
        )


# =========================================================
# TARGET-MARGIN POSITION
# =========================================================
st.markdown(
    '<div class="section-title">Target Margin Position</div>',
    unsafe_allow_html=True,
)

target_col1, target_col2, target_col3 = (
    st.columns(3)
)

with target_col1:
    st.metric(
        "Target Margin",
        format_percentage(
            analysis_target_margin_pct
        ),
    )

with target_col2:
    st.metric(
        "Required Target Price",
        format_currency(
            target_selling_price_per_parcel
        ),
    )

with target_col3:
    target_price_gap = (
        net_selling_price_per_parcel
        - target_selling_price_per_parcel
    )

    st.metric(
        "Price Gap",
        format_currency(
            target_price_gap
        ),
        delta=format_currency(
            target_price_gap
        ),
    )


# =========================================================
# SCENARIO COMPARISON
# =========================================================
st.markdown(
    '<div class="section-title">Scenario Comparison</div>',
    unsafe_allow_html=True,
)


if not scenario_df.empty:
    scenario_columns = [
        "Scenario",
        "Parcels per Shipment",
        "Shipments per Month",
        "Planned Fleet Size",
        "Fleet Utilisation (%)",
        "Cost per Parcel (RM)",
        "Selling Price per Parcel (RM)",
        "Profit per Shipment (RM)",
        "Profit Margin (%)",
        "Monthly Profit (RM)",
        "Scenario Status",
    ]

    available_scenario_columns = [
        column
        for column in scenario_columns
        if column in scenario_df.columns
    ]

    scenario_display = scenario_df[
        available_scenario_columns
    ].copy()

    currency_columns = [
        "Cost per Parcel (RM)",
        "Selling Price per Parcel (RM)",
        "Profit per Shipment (RM)",
        "Monthly Profit (RM)",
    ]

    for column in currency_columns:
        if column in scenario_display.columns:
            scenario_display[column] = (
                pd.to_numeric(
                    scenario_display[column],
                    errors="coerce",
                )
                .fillna(0)
                .map(
                    lambda value: f"{value:,.2f}"
                )
            )

    percentage_columns = [
        "Fleet Utilisation (%)",
        "Profit Margin (%)",
    ]

    for column in percentage_columns:
        if column in scenario_display.columns:
            scenario_display[column] = (
                pd.to_numeric(
                    scenario_display[column],
                    errors="coerce",
                )
                .fillna(0)
                .map(
                    lambda value: f"{value:,.1f}%"
                )
            )

    st.dataframe(
        scenario_display,
        hide_index=True,
        use_container_width=True,
    )


    if {
        "Scenario",
        "Monthly Profit (RM)",
    }.issubset(
        scenario_df.columns
    ):
        monthly_profit_chart = (
            scenario_df[
                [
                    "Scenario",
                    "Monthly Profit (RM)",
                ]
            ]
            .copy()
        )

        monthly_profit_chart[
            "Monthly Profit (RM)"
        ] = pd.to_numeric(
            monthly_profit_chart[
                "Monthly Profit (RM)"
            ],
            errors="coerce",
        ).fillna(0)

        monthly_profit_chart = (
            monthly_profit_chart.set_index(
                "Scenario"
            )
        )

        st.markdown("**Monthly Profit by Scenario**")

        st.bar_chart(
            monthly_profit_chart,
            use_container_width=True,
        )


    if {
        "Scenario",
        "Cost per Parcel (RM)",
        "Selling Price per Parcel (RM)",
    }.issubset(
        scenario_df.columns
    ):
        cost_price_chart = scenario_df[
            [
                "Scenario",
                "Cost per Parcel (RM)",
                "Selling Price per Parcel (RM)",
            ]
        ].copy()

        for column in [
            "Cost per Parcel (RM)",
            "Selling Price per Parcel (RM)",
        ]:
            cost_price_chart[column] = pd.to_numeric(
                cost_price_chart[column],
                errors="coerce",
            ).fillna(0)

        cost_price_chart = (
            cost_price_chart.set_index(
                "Scenario"
            )
        )

        st.markdown(
            "**Cost and Selling Price by Scenario**"
        )

        st.bar_chart(
            cost_price_chart,
            use_container_width=True,
        )

else:
    st.info(
        "No scenario results are available."
    )


# =========================================================
# SCENARIO RANKING
# =========================================================
st.markdown(
    '<div class="section-title">Scenario Ranking</div>',
    unsafe_allow_html=True,
)

ranking_col1, ranking_col2, ranking_col3, ranking_col4 = (
    st.columns(4)
)

with ranking_col1:
    st.metric(
        "Highest Monthly Profit",
        best_profit_scenario or "Not Available",
    )

with ranking_col2:
    st.metric(
        "Highest Profit Margin",
        best_margin_scenario or "Not Available",
    )

with ranking_col3:
    st.metric(
        "Lowest Cost",
        lowest_cost_scenario or "Not Available",
    )

with ranking_col4:
    st.metric(
        "Highest Utilisation",
        highest_utilisation_scenario
        or "Not Available",
    )


# =========================================================
# SELECTED SCENARIO SUMMARY
# =========================================================
st.markdown(
    '<div class="section-title">Selected Scenario Summary</div>',
    unsafe_allow_html=True,
)


if selected_scenario:
    selected_col1, selected_col2, selected_col3, selected_col4 = (
        st.columns(4)
    )

    with selected_col1:
        st.metric(
            "Scenario",
            selected_scenario_name,
        )

    with selected_col2:
        st.metric(
            "Simulated Cost per Parcel",
            format_currency(
                selected_scenario.get(
                    "Cost per Parcel (RM)",
                    0,
                )
            ),
        )

    with selected_col3:
        st.metric(
            "Simulated Margin",
            format_percentage(
                selected_scenario.get(
                    "Profit Margin (%)",
                    0,
                )
            ),
        )

    with selected_col4:
        st.metric(
            "Simulated Monthly Profit",
            format_currency(
                selected_scenario.get(
                    "Monthly Profit (RM)",
                    0,
                )
            ),
        )


# =========================================================
# MANAGEMENT OBSERVATIONS
# =========================================================
st.markdown(
    '<div class="section-title">Key Management Observations</div>',
    unsafe_allow_html=True,
)

management_observations = []


if profit_per_shipment < 0:
    management_observations.append(
        {
            "Priority": "Critical",
            "Area": "Profitability",
            "Observation": (
                "The baseline service is loss-making."
            ),
            "Management Action": (
                "Review selling price, vehicle selection, "
                "shipment frequency and operating-cost assumptions."
            ),
        }
    )

elif profit_margin_pct < 5:
    management_observations.append(
        {
            "Priority": "High",
            "Area": "Profitability",
            "Observation": (
                "The baseline profit margin is below 5%."
            ),
            "Management Action": (
                "Introduce a stronger pricing buffer or cost "
                "reduction plan before implementation."
            ),
        }
    )

else:
    management_observations.append(
        {
            "Priority": "Normal",
            "Area": "Profitability",
            "Observation": (
                f"The baseline profit margin is "
                f"{profit_margin_pct:,.1f}%."
            ),
            "Management Action": (
                "Continue monitoring actual volume, fuel and "
                "manpower performance against the model."
            ),
        }
    )


if overall_utilisation_pct < 40:
    management_observations.append(
        {
            "Priority": "High",
            "Area": "Fleet Capacity",
            "Observation": (
                "The planned fleet is significantly underutilised."
            ),
            "Management Action": (
                "Assess a smaller vehicle, remove unnecessary "
                "buffer vehicles or consolidate shipments."
            ),
        }
    )

elif overall_utilisation_pct > 90:
    management_observations.append(
        {
            "Priority": "High",
            "Area": "Fleet Capacity",
            "Observation": (
                "The fleet is operating close to maximum capacity."
            ),
            "Management Action": (
                "Maintain contingency capacity and monitor peak "
                "volume or delivery disruption risks."
            ),
        }
    )

else:
    management_observations.append(
        {
            "Priority": "Normal",
            "Area": "Fleet Capacity",
            "Observation": (
                f"Fleet utilisation is "
                f"{overall_utilisation_pct:,.1f}%."
            ),
            "Management Action": (
                "Maintain current fleet planning and review "
                "utilisation when actual volume becomes available."
            ),
        }
    )


if fleet_shortfall > 0:
    management_observations.append(
        {
            "Priority": "Critical",
            "Area": "Fleet Availability",
            "Observation": (
                f"A shortfall of {fleet_shortfall:,} vehicle(s) "
                "exists against the planned requirement."
            ),
            "Management Action": (
                "Secure additional internal fleet, rental or "
                "third-party transport capacity."
            ),
        }
    )


if not parcel_standard_compliant:
    management_observations.append(
        {
            "Priority": "High",
            "Area": "Parcel Compliance",
            "Observation": (
                "One or more parcel measurements exceed the "
                "selected parcel standard."
            ),
            "Management Action": (
                "Review parcel classification, special handling "
                "requirements and commercial pricing."
            ),
        }
    )


if net_selling_price_per_parcel < break_even_price_per_parcel:
    management_observations.append(
        {
            "Priority": "Critical",
            "Area": "Pricing",
            "Observation": (
                "The selling price is below break-even."
            ),
            "Management Action": (
                "Increase price or reduce operating cost before "
                "commercial approval."
            ),
        }
    )


if best_profit_scenario and (
    best_profit_scenario
    != "Baseline"
):
    management_observations.append(
        {
            "Priority": "Opportunity",
            "Area": "Scenario Planning",
            "Observation": (
                f"The {best_profit_scenario} scenario produces "
                "the highest monthly profit."
            ),
            "Management Action": (
                "Review whether the assumptions supporting this "
                "scenario are commercially achievable."
            ),
        }
    )


management_observation_df = pd.DataFrame(
    management_observations
)

st.dataframe(
    management_observation_df,
    hide_index=True,
    use_container_width=True,
)


# =========================================================
# MANAGEMENT RECOMMENDATION
# =========================================================
st.markdown(
    '<div class="section-title">Management Recommendation</div>',
    unsafe_allow_html=True,
)


critical_observations = [
    observation
    for observation in management_observations
    if observation["Priority"] == "Critical"
]

high_observations = [
    observation
    for observation in management_observations
    if observation["Priority"] == "High"
]


if critical_observations:
    recommendation_status = "Do Not Proceed"

    recommendation_text = (
        "The current model contains critical issues that should "
        "be resolved before commercial or operational approval."
    )

    st.error(
        f"**{recommendation_status}** — "
        f"{recommendation_text}"
    )

elif high_observations:
    recommendation_status = "Proceed with Conditions"

    recommendation_text = (
        "The service may proceed only after the identified "
        "high-priority operational or commercial risks are "
        "addressed."
    )

    st.warning(
        f"**{recommendation_status}** — "
        f"{recommendation_text}"
    )

else:
    recommendation_status = "Proceed"

    recommendation_text = (
        "The service is operationally feasible and commercially "
        "profitable under the saved baseline assumptions."
    )

    st.success(
        f"**{recommendation_status}** — "
        f"{recommendation_text}"
    )


# =========================================================
# DETAILED MANAGEMENT SUMMARY
# =========================================================
with st.expander(
    "View Complete Management Summary",
    expanded=False,
):
    management_summary = pd.DataFrame(
        {
            "Section": [
                "Route",
                "Route",
                "Route",
                "Parcel",
                "Parcel",
                "Parcel",
                "Parcel",
                "Fleet",
                "Fleet",
                "Fleet",
                "Cost",
                "Cost",
                "Cost",
                "Profitability",
                "Profitability",
                "Profitability",
                "Profitability",
                "Scenario",
                "Recommendation",
            ],
            "Measure": [
                "Route ID",
                "Route",
                "Service Level",
                "Parcel Type",
                "Parcel Quantity",
                "Actual Weight",
                "Chargeable Weight",
                "Vehicle Type",
                "Planned Fleet Size",
                "Fleet Utilisation",
                "Cost per Shipment",
                "Cost per Parcel",
                "Monthly Operating Cost",
                "Selling Price per Parcel",
                "Profit per Shipment",
                "Profit Margin",
                "Monthly Profit",
                "Selected Scenario",
                "Management Recommendation",
            ],
            "Value": [
                route_id,
                (
                    f"{origin_state} → "
                    f"{destination_state}"
                ),
                service_level,
                parcel_type,
                f"{parcel_quantity:,}",
                f"{total_actual_weight_kg:,.2f} kg",
                f"{chargeable_weight_kg:,.2f} kg",
                vehicle_type,
                f"{planned_fleet_size:,}",
                format_percentage(
                    overall_utilisation_pct
                ),
                format_currency(
                    total_operating_cost_per_shipment
                ),
                format_currency(
                    total_cost_per_parcel
                ),
                format_currency(
                    total_monthly_operating_cost
                ),
                format_currency(
                    net_selling_price_per_parcel
                ),
                format_currency(
                    profit_per_shipment
                ),
                format_percentage(
                    profit_margin_pct
                ),
                format_currency(
                    monthly_profit
                ),
                selected_scenario_name,
                recommendation_status,
            ],
        }
    )

    st.dataframe(
        management_summary,
        hide_index=True,
        use_container_width=True,
    )


# =========================================================
# EXPORT REPORT DATA
# =========================================================
def create_excel_report() -> bytes:
    """
    Create an Excel workbook containing the main dashboard
    summaries and scenario results.
    """

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl",
    ) as writer:

        executive_summary_df = pd.DataFrame(
            [
                {
                    "Report Date": (
                        datetime.now().strftime(
                            "%d/%m/%Y %H:%M"
                        )
                    ),
                    "Route ID": route_id,
                    "Origin": origin_state,
                    "Destination": destination_state,
                    "Service Level": service_level,
                    "Parcel Type": parcel_type,
                    "Parcels per Shipment": (
                        parcel_quantity
                    ),
                    "Shipments per Month": (
                        shipments_per_month
                    ),
                    "Vehicle Type": vehicle_type,
                    "Required Fleet": required_vehicles,
                    "Planned Fleet": planned_fleet_size,
                    "Fleet Utilisation (%)": (
                        overall_utilisation_pct
                    ),
                    "Cost per Parcel (RM)": (
                        total_cost_per_parcel
                    ),
                    "Selling Price per Parcel (RM)": (
                        net_selling_price_per_parcel
                    ),
                    "Profit per Parcel (RM)": (
                        profit_per_parcel
                    ),
                    "Profit per Shipment (RM)": (
                        profit_per_shipment
                    ),
                    "Profit Margin (%)": (
                        profit_margin_pct
                    ),
                    "Monthly Revenue (RM)": (
                        monthly_revenue
                    ),
                    "Monthly Operating Cost (RM)": (
                        total_monthly_operating_cost
                    ),
                    "Monthly Profit (RM)": (
                        monthly_profit
                    ),
                    "Selected Scenario": (
                        selected_scenario_name
                    ),
                    "Management Recommendation": (
                        recommendation_status
                    ),
                }
            ]
        )

        parcel_summary_df = pd.DataFrame(
            [
                {
                    "Parcel Type": parcel_type,
                    "Parcel Quantity": parcel_quantity,
                    "Weight per Parcel (kg)": (
                        weight_per_parcel_kg
                    ),
                    "Actual Weight (kg)": (
                        total_actual_weight_kg
                    ),
                    "Volumetric Weight (kg)": (
                        total_volumetric_weight_kg
                    ),
                    "Chargeable Weight (kg)": (
                        chargeable_weight_kg
                    ),
                    "Chargeable Weight Basis": (
                        chargeable_weight_basis
                    ),
                    "Total Volume (m³)": (
                        total_volume_m3
                    ),
                    "Standard Compliant": (
                        parcel_standard_compliant
                    ),
                }
            ]
        )

        fleet_summary_df = pd.DataFrame(
            [
                {
                    "Recommended Vehicle": (
                        recommended_vehicle_type
                    ),
                    "Selected Vehicle": vehicle_type,
                    "Required Vehicles": (
                        required_vehicles
                    ),
                    "Buffer Vehicles": (
                        additional_buffer_vehicles
                    ),
                    "Planned Fleet": planned_fleet_size,
                    "Capacity Constraint": (
                        capacity_constraint
                    ),
                    "Parcel Utilisation (%)": (
                        parcel_utilisation_pct
                    ),
                    "Weight Utilisation (%)": (
                        weight_utilisation_pct
                    ),
                    "Volume Utilisation (%)": (
                        volume_utilisation_pct
                    ),
                    "Maximum Utilisation (%)": (
                        overall_utilisation_pct
                    ),
                    "Availability Status": (
                        availability_status
                    ),
                    "Fleet Shortfall": fleet_shortfall,
                }
            ]
        )

        profitability_summary_df = pd.DataFrame(
            [
                {
                    "Pricing Method": pricing_method,
                    "Cost per Parcel (RM)": (
                        total_cost_per_parcel
                    ),
                    "Break-Even Price (RM)": (
                        break_even_price_per_parcel
                    ),
                    "Selling Price (RM)": (
                        net_selling_price_per_parcel
                    ),
                    "Revenue per Shipment (RM)": (
                        total_revenue_per_shipment
                    ),
                    "Profit per Parcel (RM)": (
                        profit_per_parcel
                    ),
                    "Profit per Shipment (RM)": (
                        profit_per_shipment
                    ),
                    "Profit Margin (%)": (
                        profit_margin_pct
                    ),
                    "Mark-up on Cost (%)": (
                        markup_on_cost_pct
                    ),
                    "Monthly Revenue (RM)": (
                        monthly_revenue
                    ),
                    "Monthly Cost (RM)": (
                        total_monthly_operating_cost
                    ),
                    "Monthly Profit (RM)": (
                        monthly_profit
                    ),
                }
            ]
        )

        executive_summary_df.to_excel(
            writer,
            sheet_name="Executive Summary",
            index=False,
        )

        parcel_summary_df.to_excel(
            writer,
            sheet_name="Parcel Assessment",
            index=False,
        )

        fleet_summary_df.to_excel(
            writer,
            sheet_name="Fleet Capacity",
            index=False,
        )

        cost_breakdown_df.to_excel(
            writer,
            sheet_name="Operating Cost",
            index=False,
        )

        profitability_summary_df.to_excel(
            writer,
            sheet_name="Profitability",
            index=False,
        )

        if not scenario_df.empty:
            scenario_df.to_excel(
                writer,
                sheet_name="Scenario Simulation",
                index=False,
            )

        management_observation_df.to_excel(
            writer,
            sheet_name="Management Actions",
            index=False,
        )

    output.seek(0)

    return output.getvalue()


# =========================================================
# DOWNLOAD REPORT
# =========================================================
st.markdown(
    '<div class="section-title">Management Report Export</div>',
    unsafe_allow_html=True,
)

report_filename = (
    "Courier_Cost_Management_Report_"
    + datetime.now().strftime(
        "%Y%m%d_%H%M"
    )
    + ".xlsx"
)


try:
    excel_report = create_excel_report()

    st.download_button(
        label="⬇️ Download Management Report",
        data=excel_report,
        file_name=report_filename,
        mime=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        use_container_width=True,
    )

except ModuleNotFoundError:
    st.error(
        "The Excel export requires openpyxl. "
        "Install it using: pip install openpyxl"
    )

except Exception as error:
    st.error(
        f"Unable to generate the management report: {error}"
    )


# =========================================================
# NAVIGATION
# =========================================================
st.markdown(
    "<br>",
    unsafe_allow_html=True,
)

navigation_col1, navigation_col2 = st.columns(2)

with navigation_col1:
    if st.button(
        "⬅ Back to Scenario Simulation",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/8_Scenario_Simulation.py"
        )

with navigation_col2:
    if st.button(
        "🔄 Start New Assessment",
        use_container_width=True,
    ):
        keys_to_clear = [
            "shipment_information",
            "route_intelligence",
            "parcel_assessment",
            "fleet_capacity",
            "operating_cost",
            "cost_per_parcel",
            "profitability",
            "scenario_simulation",
        ]

        for key in keys_to_clear:
            st.session_state.pop(
                key,
                None,
            )

        st.switch_page(
            "pages/1_Shipment_Information.py"
        )