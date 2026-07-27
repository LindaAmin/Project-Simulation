import math

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


required_pages = {
    "Shipment Information": shipment,
    "Route Intelligence": route,
    "Parcel Assessment": parcel,
    "Fleet Capacity": fleet,
    "Operating Cost": operating_cost,
    "Cost per Parcel": cost_per_parcel,
    "Profitability": profitability,
}

incomplete_pages = [
    page_name
    for page_name, page_data in required_pages.items()
    if not page_data
]

if incomplete_pages:
    st.warning(
        "Complete and save the following pages before running "
        "scenario simulations: "
        + ", ".join(incomplete_pages)
    )
    st.stop()


# =========================================================
# READ BASELINE DATA
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

route_id = route.get(
    "route_id",
    "",
)

route_category = route.get(
    "route_category",
    "",
)

total_trip_distance_km = float(
    route.get(
        "total_trip_distance_km",
        0,
    )
)

parcel_type = parcel.get(
    "parcel_type",
    "",
)

baseline_parcel_quantity = int(
    parcel.get(
        "parcel_quantity",
        0,
    )
)

baseline_actual_weight_kg = float(
    parcel.get(
        "total_actual_weight_kg",
        0,
    )
)

baseline_volume_m3 = float(
    parcel.get(
        "total_volume_m3",
        0,
    )
)

baseline_weight_per_parcel_kg = (
    baseline_actual_weight_kg
    / baseline_parcel_quantity
    if baseline_parcel_quantity > 0
    else 0
)

baseline_volume_per_parcel_m3 = (
    baseline_volume_m3
    / baseline_parcel_quantity
    if baseline_parcel_quantity > 0
    else 0
)

vehicle_type = fleet.get(
    "selected_vehicle_type",
    "",
)

max_parcels_per_vehicle = int(
    fleet.get(
        "max_parcels_per_vehicle",
        0,
    )
)

max_weight_per_vehicle_kg = float(
    fleet.get(
        "max_weight_per_vehicle_kg",
        0,
    )
)

max_volume_per_vehicle_m3 = float(
    fleet.get(
        "max_volume_per_vehicle_m3",
        0,
    )
)

baseline_required_vehicles = int(
    fleet.get(
        "required_vehicles",
        0,
    )
)

baseline_planned_fleet_size = int(
    fleet.get(
        "planned_fleet_size",
        baseline_required_vehicles,
    )
)

baseline_operational_buffer_pct = float(
    fleet.get(
        "operational_buffer_pct",
        0,
    )
)

baseline_shipments_per_month = int(
    operating_cost.get(
        "shipments_per_month",
        0,
    )
)

baseline_direct_cost_per_shipment = float(
    operating_cost.get(
        "direct_trip_cost",
        0,
    )
)

baseline_fixed_cost_per_shipment = float(
    operating_cost.get(
        "allocated_fixed_cost_per_shipment",
        0,
    )
)

baseline_total_cost_per_shipment = float(
    operating_cost.get(
        "total_operating_cost_per_shipment",
        0,
    )
)

baseline_monthly_fixed_cost = float(
    operating_cost.get(
        "total_monthly_fixed_cost",
        0,
    )
)

baseline_fuel_cost = float(
    operating_cost.get(
        "fuel_cost_per_shipment",
        0,
    )
)

baseline_toll_cost = float(
    operating_cost.get(
        "toll_cost_per_shipment",
        0,
    )
)

baseline_maintenance_cost = float(
    operating_cost.get(
        "maintenance_cost_per_shipment",
        0,
    )
)

baseline_tyre_cost = float(
    operating_cost.get(
        "tyre_cost_per_shipment",
        0,
    )
)

baseline_overtime_cost = float(
    operating_cost.get(
        "overtime_cost_per_shipment",
        0,
    )
)

baseline_selling_price_per_parcel = float(
    profitability.get(
        "net_selling_price_per_parcel",
        0,
    )
)

baseline_additional_fee_per_shipment = float(
    profitability.get(
        "additional_fee_per_shipment",
        0,
    )
)

baseline_profit_per_shipment = float(
    profitability.get(
        "profit_per_shipment",
        0,
    )
)

baseline_profit_margin_pct = float(
    profitability.get(
        "profit_margin_pct",
        0,
    )
)


# =========================================================
# VALIDATION
# =========================================================
required_numeric_values = {
    "Baseline parcel quantity": baseline_parcel_quantity,
    "Shipments per month": baseline_shipments_per_month,
    "Vehicle parcel capacity": max_parcels_per_vehicle,
    "Vehicle weight capacity": max_weight_per_vehicle_kg,
    "Vehicle volume capacity": max_volume_per_vehicle_m3,
    "Baseline direct cost": baseline_direct_cost_per_shipment,
    "Baseline fixed cost": baseline_fixed_cost_per_shipment,
    "Selling price per parcel": baseline_selling_price_per_parcel,
}

invalid_values = [
    field_name
    for field_name, field_value in required_numeric_values.items()
    if field_value is None or float(field_value) <= 0
]

if invalid_values:
    st.error(
        "The following scenario inputs are missing or invalid: "
        + ", ".join(invalid_values)
    )

    st.info(
        "Review and save the assessments on Pages 4 to 7."
    )

    st.stop()


# =========================================================
# SESSION STATE
# =========================================================
if "scenario_simulation" not in st.session_state:
    st.session_state.scenario_simulation = {}


# =========================================================
# PAGE TITLE
# =========================================================
st.markdown(
    '<div class="main-title">🧪 Scenario Simulation</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-subtitle">
        Compare baseline, conservative, optimistic and custom
        operating scenarios before making commercial decisions.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SIMULATION BASIS
# =========================================================
cost_basis(
    "Scenario Simulation Basis",
    """
    Each scenario adjusts shipment volume, monthly frequency,
    operating cost and selling-price assumptions.

    Fleet capacity is recalculated against parcel quantity,
    shipment weight and shipment volume. Where the required fleet
    changes, variable operating costs are adjusted using the ratio
    between the simulated and baseline planned fleet sizes.

    Fixed monthly costs are allocated across the simulated number
    of monthly shipments.
    """,
)


# =========================================================
# BASELINE SUMMARY
# =========================================================
st.markdown(
    '<div class="section-title">Baseline Summary</div>',
    unsafe_allow_html=True,
)

summary_col1, summary_col2, summary_col3, summary_col4 = (
    st.columns(4)
)

with summary_col1:
    st.markdown("**Route**")
    st.write(
        f"{origin_state} → {destination_state}"
    )

with summary_col2:
    st.markdown("**Service Level**")
    st.write(service_level)

with summary_col3:
    st.markdown("**Vehicle Type**")
    st.write(vehicle_type)

with summary_col4:
    st.markdown("**Parcel Type**")
    st.write(parcel_type)


baseline_col1, baseline_col2, baseline_col3, baseline_col4 = (
    st.columns(4)
)

with baseline_col1:
    st.metric(
        "Parcels per Shipment",
        f"{baseline_parcel_quantity:,}",
    )

with baseline_col2:
    st.metric(
        "Shipments per Month",
        f"{baseline_shipments_per_month:,}",
    )

with baseline_col3:
    st.metric(
        "Selling Price per Parcel",
        f"RM {baseline_selling_price_per_parcel:,.2f}",
    )

with baseline_col4:
    st.metric(
        "Profit Margin",
        f"{baseline_profit_margin_pct:,.1f}%",
    )


# =========================================================
# SCENARIO DEFAULTS
# =========================================================
scenario_defaults = {
    "Baseline": {
        "parcel_change_pct": 0.0,
        "shipment_change_pct": 0.0,
        "selling_price_change_pct": 0.0,
        "fuel_cost_change_pct": 0.0,
        "toll_cost_change_pct": 0.0,
        "other_direct_cost_change_pct": 0.0,
        "fixed_cost_change_pct": 0.0,
        "operational_buffer_pct": (
            baseline_operational_buffer_pct
        ),
    },
    "Conservative": {
        "parcel_change_pct": -15.0,
        "shipment_change_pct": -10.0,
        "selling_price_change_pct": -5.0,
        "fuel_cost_change_pct": 15.0,
        "toll_cost_change_pct": 10.0,
        "other_direct_cost_change_pct": 8.0,
        "fixed_cost_change_pct": 5.0,
        "operational_buffer_pct": max(
            baseline_operational_buffer_pct,
            10.0,
        ),
    },
    "Optimistic": {
        "parcel_change_pct": 20.0,
        "shipment_change_pct": 15.0,
        "selling_price_change_pct": 5.0,
        "fuel_cost_change_pct": -5.0,
        "toll_cost_change_pct": 0.0,
        "other_direct_cost_change_pct": -5.0,
        "fixed_cost_change_pct": 0.0,
        "operational_buffer_pct": (
            baseline_operational_buffer_pct
        ),
    },
}


# =========================================================
# CUSTOM SCENARIO INPUTS
# =========================================================
st.markdown(
    '<div class="section-title">Custom Scenario Assumptions</div>',
    unsafe_allow_html=True,
)

st.caption(
    "Enter percentage changes compared with the saved baseline."
)

custom_col1, custom_col2, custom_col3 = st.columns(3)

with custom_col1:
    custom_parcel_change_pct = st.number_input(
        "Parcel Quantity Change (%)",
        min_value=-99.0,
        max_value=500.0,
        value=0.0,
        step=5.0,
        key="scenario_parcel_change_pct",
    )

with custom_col2:
    custom_shipment_change_pct = st.number_input(
        "Monthly Shipment Change (%)",
        min_value=-99.0,
        max_value=500.0,
        value=0.0,
        step=5.0,
        key="scenario_shipment_change_pct",
    )

with custom_col3:
    custom_selling_price_change_pct = st.number_input(
        "Selling Price Change (%)",
        min_value=-99.0,
        max_value=500.0,
        value=0.0,
        step=5.0,
        key="scenario_selling_price_change_pct",
    )


custom_cost_col1, custom_cost_col2, custom_cost_col3 = (
    st.columns(3)
)

with custom_cost_col1:
    custom_fuel_change_pct = st.number_input(
        "Fuel Cost Change (%)",
        min_value=-99.0,
        max_value=500.0,
        value=0.0,
        step=5.0,
        key="scenario_fuel_change_pct",
    )

with custom_cost_col2:
    custom_toll_change_pct = st.number_input(
        "Toll Cost Change (%)",
        min_value=-99.0,
        max_value=500.0,
        value=0.0,
        step=5.0,
        key="scenario_toll_change_pct",
    )

with custom_cost_col3:
    custom_other_direct_change_pct = st.number_input(
        "Other Direct Cost Change (%)",
        min_value=-99.0,
        max_value=500.0,
        value=0.0,
        step=5.0,
        key="scenario_other_direct_change_pct",
        help=(
            "Applied to maintenance, tyres and overtime."
        ),
    )


custom_fixed_col1, custom_fixed_col2 = st.columns(2)

with custom_fixed_col1:
    custom_fixed_cost_change_pct = st.number_input(
        "Monthly Fixed Cost Change (%)",
        min_value=-99.0,
        max_value=500.0,
        value=0.0,
        step=5.0,
        key="scenario_fixed_cost_change_pct",
    )

with custom_fixed_col2:
    custom_operational_buffer_pct = st.number_input(
        "Operational Buffer (%)",
        min_value=0.0,
        max_value=100.0,
        value=float(
            baseline_operational_buffer_pct
        ),
        step=5.0,
        key="scenario_operational_buffer_pct",
    )


scenario_defaults["Custom"] = {
    "parcel_change_pct": (
        custom_parcel_change_pct
    ),
    "shipment_change_pct": (
        custom_shipment_change_pct
    ),
    "selling_price_change_pct": (
        custom_selling_price_change_pct
    ),
    "fuel_cost_change_pct": (
        custom_fuel_change_pct
    ),
    "toll_cost_change_pct": (
        custom_toll_change_pct
    ),
    "other_direct_cost_change_pct": (
        custom_other_direct_change_pct
    ),
    "fixed_cost_change_pct": (
        custom_fixed_cost_change_pct
    ),
    "operational_buffer_pct": (
        custom_operational_buffer_pct
    ),
}


# =========================================================
# HELPER FUNCTIONS
# =========================================================
def adjusted_value(
    baseline_value: float,
    change_pct: float,
) -> float:
    """
    Apply a percentage change to a baseline value.
    """

    return baseline_value * (
        1 + change_pct / 100
    )


def calculate_required_fleet(
    parcel_quantity: int,
    shipment_weight_kg: float,
    shipment_volume_m3: float,
    operational_buffer_pct: float,
) -> dict:
    """
    Recalculate the required and planned fleet size.
    """

    vehicles_by_parcel = math.ceil(
        parcel_quantity
        / max_parcels_per_vehicle
    )

    vehicles_by_weight = math.ceil(
        shipment_weight_kg
        / max_weight_per_vehicle_kg
    )

    vehicles_by_volume = math.ceil(
        shipment_volume_m3
        / max_volume_per_vehicle_m3
    )

    required_vehicles = max(
        vehicles_by_parcel,
        vehicles_by_weight,
        vehicles_by_volume,
    )

    constraint_values = {
        "Parcel Quantity": vehicles_by_parcel,
        "Actual Weight": vehicles_by_weight,
        "Shipment Volume": vehicles_by_volume,
    }

    maximum_value = max(
        constraint_values.values()
    )

    controlling_constraints = [
        constraint
        for constraint, value
        in constraint_values.items()
        if value == maximum_value
    ]

    capacity_constraint = " and ".join(
        controlling_constraints
    )

    buffer_vehicles = math.ceil(
        required_vehicles
        * operational_buffer_pct
        / 100
    )

    planned_fleet_size = (
        required_vehicles
        + buffer_vehicles
    )

    total_parcel_capacity = (
        planned_fleet_size
        * max_parcels_per_vehicle
    )

    total_weight_capacity = (
        planned_fleet_size
        * max_weight_per_vehicle_kg
    )

    total_volume_capacity = (
        planned_fleet_size
        * max_volume_per_vehicle_m3
    )

    parcel_utilisation_pct = (
        parcel_quantity
        / total_parcel_capacity
        * 100
        if total_parcel_capacity > 0
        else 0
    )

    weight_utilisation_pct = (
        shipment_weight_kg
        / total_weight_capacity
        * 100
        if total_weight_capacity > 0
        else 0
    )

    volume_utilisation_pct = (
        shipment_volume_m3
        / total_volume_capacity
        * 100
        if total_volume_capacity > 0
        else 0
    )

    overall_utilisation_pct = max(
        parcel_utilisation_pct,
        weight_utilisation_pct,
        volume_utilisation_pct,
    )

    return {
        "vehicles_by_parcel": vehicles_by_parcel,
        "vehicles_by_weight": vehicles_by_weight,
        "vehicles_by_volume": vehicles_by_volume,
        "required_vehicles": required_vehicles,
        "buffer_vehicles": buffer_vehicles,
        "planned_fleet_size": planned_fleet_size,
        "capacity_constraint": capacity_constraint,
        "parcel_utilisation_pct": (
            parcel_utilisation_pct
        ),
        "weight_utilisation_pct": (
            weight_utilisation_pct
        ),
        "volume_utilisation_pct": (
            volume_utilisation_pct
        ),
        "overall_utilisation_pct": (
            overall_utilisation_pct
        ),
    }


def calculate_scenario(
    scenario_name: str,
    assumptions: dict,
) -> dict:
    """
    Calculate operational and profitability results
    for one scenario.
    """

    simulated_parcel_quantity = max(
        int(
            round(
                adjusted_value(
                    baseline_parcel_quantity,
                    assumptions[
                        "parcel_change_pct"
                    ],
                )
            )
        ),
        1,
    )

    simulated_shipments_per_month = max(
        int(
            round(
                adjusted_value(
                    baseline_shipments_per_month,
                    assumptions[
                        "shipment_change_pct"
                    ],
                )
            )
        ),
        1,
    )

    simulated_weight_kg = (
        baseline_weight_per_parcel_kg
        * simulated_parcel_quantity
    )

    simulated_volume_m3 = (
        baseline_volume_per_parcel_m3
        * simulated_parcel_quantity
    )

    fleet_result = calculate_required_fleet(
        parcel_quantity=(
            simulated_parcel_quantity
        ),
        shipment_weight_kg=(
            simulated_weight_kg
        ),
        shipment_volume_m3=(
            simulated_volume_m3
        ),
        operational_buffer_pct=(
            assumptions[
                "operational_buffer_pct"
            ]
        ),
    )

    simulated_planned_fleet = fleet_result[
        "planned_fleet_size"
    ]

    fleet_scaling_ratio = (
        simulated_planned_fleet
        / baseline_planned_fleet_size
        if baseline_planned_fleet_size > 0
        else 1
    )

    simulated_fuel_cost = (
        adjusted_value(
            baseline_fuel_cost,
            assumptions[
                "fuel_cost_change_pct"
            ],
        )
        * fleet_scaling_ratio
    )

    simulated_toll_cost = (
        adjusted_value(
            baseline_toll_cost,
            assumptions[
                "toll_cost_change_pct"
            ],
        )
        * fleet_scaling_ratio
    )

    baseline_other_direct_cost = (
        baseline_maintenance_cost
        + baseline_tyre_cost
        + baseline_overtime_cost
    )

    simulated_other_direct_cost = (
        adjusted_value(
            baseline_other_direct_cost,
            assumptions[
                "other_direct_cost_change_pct"
            ],
        )
        * fleet_scaling_ratio
    )

    simulated_direct_cost_per_shipment = (
        simulated_fuel_cost
        + simulated_toll_cost
        + simulated_other_direct_cost
    )

    simulated_monthly_fixed_cost = (
        adjusted_value(
            baseline_monthly_fixed_cost,
            assumptions[
                "fixed_cost_change_pct"
            ],
        )
        * fleet_scaling_ratio
    )

    simulated_fixed_cost_per_shipment = (
        simulated_monthly_fixed_cost
        / simulated_shipments_per_month
    )

    simulated_total_cost_per_shipment = (
        simulated_direct_cost_per_shipment
        + simulated_fixed_cost_per_shipment
    )

    simulated_cost_per_parcel = (
        simulated_total_cost_per_shipment
        / simulated_parcel_quantity
    )

    simulated_selling_price_per_parcel = (
        adjusted_value(
            baseline_selling_price_per_parcel,
            assumptions[
                "selling_price_change_pct"
            ],
        )
    )

    simulated_revenue_per_shipment = (
        simulated_selling_price_per_parcel
        * simulated_parcel_quantity
        + baseline_additional_fee_per_shipment
    )

    simulated_profit_per_shipment = (
        simulated_revenue_per_shipment
        - simulated_total_cost_per_shipment
    )

    simulated_profit_margin_pct = (
        simulated_profit_per_shipment
        / simulated_revenue_per_shipment
        * 100
        if simulated_revenue_per_shipment > 0
        else 0
    )

    simulated_markup_pct = (
        simulated_profit_per_shipment
        / simulated_total_cost_per_shipment
        * 100
        if simulated_total_cost_per_shipment > 0
        else 0
    )

    simulated_monthly_parcels = (
        simulated_parcel_quantity
        * simulated_shipments_per_month
    )

    simulated_monthly_revenue = (
        simulated_revenue_per_shipment
        * simulated_shipments_per_month
    )

    simulated_monthly_direct_cost = (
        simulated_direct_cost_per_shipment
        * simulated_shipments_per_month
    )

    simulated_monthly_total_cost = (
        simulated_monthly_direct_cost
        + simulated_monthly_fixed_cost
    )

    simulated_monthly_profit = (
        simulated_monthly_revenue
        - simulated_monthly_total_cost
    )

    break_even_price_per_parcel = (
        simulated_total_cost_per_shipment
        - baseline_additional_fee_per_shipment
    ) / simulated_parcel_quantity

    break_even_parcel_quantity = (
        math.ceil(
            (
                simulated_total_cost_per_shipment
                - baseline_additional_fee_per_shipment
            )
            / simulated_selling_price_per_parcel
        )
        if simulated_selling_price_per_parcel > 0
        else 0
    )

    if simulated_profit_per_shipment < 0:
        scenario_status = "Loss-Making"

    elif simulated_profit_margin_pct < 5:
        scenario_status = "Low Margin"

    elif simulated_profit_margin_pct < 15:
        scenario_status = "Moderate Margin"

    elif simulated_profit_margin_pct < 30:
        scenario_status = "Healthy Margin"

    else:
        scenario_status = "High Margin"

    return {
        "Scenario": scenario_name,
        "Parcel Change (%)": assumptions[
            "parcel_change_pct"
        ],
        "Shipment Change (%)": assumptions[
            "shipment_change_pct"
        ],
        "Price Change (%)": assumptions[
            "selling_price_change_pct"
        ],
        "Fuel Cost Change (%)": assumptions[
            "fuel_cost_change_pct"
        ],
        "Toll Cost Change (%)": assumptions[
            "toll_cost_change_pct"
        ],
        "Other Direct Cost Change (%)": assumptions[
            "other_direct_cost_change_pct"
        ],
        "Fixed Cost Change (%)": assumptions[
            "fixed_cost_change_pct"
        ],
        "Operational Buffer (%)": assumptions[
            "operational_buffer_pct"
        ],

        "Parcels per Shipment": (
            simulated_parcel_quantity
        ),
        "Shipments per Month": (
            simulated_shipments_per_month
        ),
        "Monthly Parcel Volume": (
            simulated_monthly_parcels
        ),

        "Shipment Weight (kg)": (
            simulated_weight_kg
        ),
        "Shipment Volume (m³)": (
            simulated_volume_m3
        ),

        "Vehicles by Parcel": fleet_result[
            "vehicles_by_parcel"
        ],
        "Vehicles by Weight": fleet_result[
            "vehicles_by_weight"
        ],
        "Vehicles by Volume": fleet_result[
            "vehicles_by_volume"
        ],
        "Required Vehicles": fleet_result[
            "required_vehicles"
        ],
        "Buffer Vehicles": fleet_result[
            "buffer_vehicles"
        ],
        "Planned Fleet Size": fleet_result[
            "planned_fleet_size"
        ],
        "Capacity Constraint": fleet_result[
            "capacity_constraint"
        ],
        "Fleet Utilisation (%)": fleet_result[
            "overall_utilisation_pct"
        ],

        "Fuel Cost per Shipment (RM)": (
            simulated_fuel_cost
        ),
        "Toll Cost per Shipment (RM)": (
            simulated_toll_cost
        ),
        "Other Direct Cost per Shipment (RM)": (
            simulated_other_direct_cost
        ),
        "Direct Cost per Shipment (RM)": (
            simulated_direct_cost_per_shipment
        ),
        "Fixed Cost per Shipment (RM)": (
            simulated_fixed_cost_per_shipment
        ),
        "Total Cost per Shipment (RM)": (
            simulated_total_cost_per_shipment
        ),
        "Cost per Parcel (RM)": (
            simulated_cost_per_parcel
        ),

        "Selling Price per Parcel (RM)": (
            simulated_selling_price_per_parcel
        ),
        "Revenue per Shipment (RM)": (
            simulated_revenue_per_shipment
        ),
        "Profit per Shipment (RM)": (
            simulated_profit_per_shipment
        ),
        "Profit Margin (%)": (
            simulated_profit_margin_pct
        ),
        "Mark-up on Cost (%)": (
            simulated_markup_pct
        ),

        "Monthly Revenue (RM)": (
            simulated_monthly_revenue
        ),
        "Monthly Cost (RM)": (
            simulated_monthly_total_cost
        ),
        "Monthly Profit (RM)": (
            simulated_monthly_profit
        ),

        "Break-Even Price per Parcel (RM)": (
            break_even_price_per_parcel
        ),
        "Break-Even Parcel Quantity": (
            break_even_parcel_quantity
        ),
        "Scenario Status": scenario_status,
    }


# =========================================================
# RUN SCENARIOS
# =========================================================
scenario_results = []

for scenario_name, assumptions in scenario_defaults.items():
    scenario_results.append(
        calculate_scenario(
            scenario_name=scenario_name,
            assumptions=assumptions,
        )
    )


scenario_df = pd.DataFrame(
    scenario_results
)


# =========================================================
# SCENARIO SELECTION
# =========================================================
st.markdown(
    '<div class="section-title">Scenario Comparison</div>',
    unsafe_allow_html=True,
)

selected_scenario_name = st.selectbox(
    "Scenario for Detailed Review",
    options=scenario_df["Scenario"].tolist(),
    index=0,
    key="scenario_selected_name",
)

selected_scenario = scenario_df[
    scenario_df["Scenario"]
    == selected_scenario_name
].iloc[0]


# =========================================================
# SELECTED SCENARIO RESULTS
# =========================================================
selected_col1, selected_col2, selected_col3, selected_col4 = (
    st.columns(4)
)

with selected_col1:
    st.metric(
        "Parcels per Shipment",
        f'{int(selected_scenario["Parcels per Shipment"]):,}',
        delta=(
            f'{int(selected_scenario["Parcels per Shipment"]) - baseline_parcel_quantity:+,}'
        ),
    )

with selected_col2:
    st.metric(
        "Planned Fleet Size",
        f'{int(selected_scenario["Planned Fleet Size"]):,}',
        delta=(
            f'{int(selected_scenario["Planned Fleet Size"]) - baseline_planned_fleet_size:+,}'
        ),
        delta_color="inverse",
    )

with selected_col3:
    st.metric(
        "Cost per Parcel",
        (
            f'RM '
            f'{selected_scenario["Cost per Parcel (RM)"]:,.2f}'
        ),
        delta=(
            f'RM '
            f'{selected_scenario["Cost per Parcel (RM)"] - baseline_total_cost_per_shipment / baseline_parcel_quantity:,.2f}'
        ),
        delta_color="inverse",
    )

with selected_col4:
    st.metric(
        "Selling Price per Parcel",
        (
            f'RM '
            f'{selected_scenario["Selling Price per Parcel (RM)"]:,.2f}'
        ),
        delta=(
            f'RM '
            f'{selected_scenario["Selling Price per Parcel (RM)"] - baseline_selling_price_per_parcel:,.2f}'
        ),
    )


profit_col1, profit_col2, profit_col3, profit_col4 = (
    st.columns(4)
)

with profit_col1:
    st.metric(
        "Revenue per Shipment",
        (
            f'RM '
            f'{selected_scenario["Revenue per Shipment (RM)"]:,.2f}'
        ),
    )

with profit_col2:
    st.metric(
        "Profit per Shipment",
        (
            f'RM '
            f'{selected_scenario["Profit per Shipment (RM)"]:,.2f}'
        ),
        delta=(
            f'RM '
            f'{selected_scenario["Profit per Shipment (RM)"] - baseline_profit_per_shipment:,.2f}'
        ),
    )

with profit_col3:
    st.metric(
        "Profit Margin",
        (
            f'{selected_scenario["Profit Margin (%)"]:,.1f}%'
        ),
        delta=(
            f'{selected_scenario["Profit Margin (%)"] - baseline_profit_margin_pct:,.1f} pts'
        ),
    )

with profit_col4:
    st.metric(
        "Monthly Profit",
        (
            f'RM '
            f'{selected_scenario["Monthly Profit (RM)"]:,.2f}'
        ),
    )


# =========================================================
# SELECTED SCENARIO INTERPRETATION
# =========================================================
st.markdown(
    '<div class="section-title">Scenario Interpretation</div>',
    unsafe_allow_html=True,
)

interpretation_col1, interpretation_col2 = st.columns(2)

with interpretation_col1:
    st.markdown("**Profitability Status**")

    scenario_status = selected_scenario[
        "Scenario Status"
    ]

    if scenario_status in {
        "Healthy Margin",
        "High Margin",
    }:
        st.success(scenario_status)

    elif scenario_status in {
        "Moderate Margin",
        "Low Margin",
    }:
        st.warning(scenario_status)

    else:
        st.error(scenario_status)


with interpretation_col2:
    st.markdown("**Capacity Constraint**")

    st.info(
        f'{selected_scenario["Capacity Constraint"]} determines '
        f'the requirement of '
        f'{int(selected_scenario["Required Vehicles"]):,} '
        f'vehicle(s), excluding operational buffer.'
    )


if selected_scenario["Profit per Shipment (RM)"] < 0:
    st.error(
        "The selected scenario does not recover the total "
        "operating cost."
    )

elif (
    selected_scenario[
        "Selling Price per Parcel (RM)"
    ]
    < selected_scenario[
        "Break-Even Price per Parcel (RM)"
    ]
):
    st.warning(
        "The selected selling price is below the simulated "
        "break-even price."
    )

else:
    st.success(
        "The selected selling price exceeds the simulated "
        "break-even requirement."
    )


# =========================================================
# MANAGEMENT COMPARISON TABLE
# =========================================================
comparison_columns = [
    "Scenario",
    "Parcels per Shipment",
    "Shipments per Month",
    "Monthly Parcel Volume",
    "Planned Fleet Size",
    "Fleet Utilisation (%)",
    "Cost per Parcel (RM)",
    "Selling Price per Parcel (RM)",
    "Revenue per Shipment (RM)",
    "Profit per Shipment (RM)",
    "Profit Margin (%)",
    "Monthly Profit (RM)",
    "Scenario Status",
]

comparison_display = scenario_df[
    comparison_columns
].copy()


currency_columns = [
    "Cost per Parcel (RM)",
    "Selling Price per Parcel (RM)",
    "Revenue per Shipment (RM)",
    "Profit per Shipment (RM)",
    "Monthly Profit (RM)",
]

for column in currency_columns:
    comparison_display[column] = (
        comparison_display[column]
        .map(
            lambda value: f"{value:,.2f}"
        )
    )


percentage_columns = [
    "Fleet Utilisation (%)",
    "Profit Margin (%)",
]

for column in percentage_columns:
    comparison_display[column] = (
        comparison_display[column]
        .map(
            lambda value: f"{value:,.1f}%"
        )
    )


st.dataframe(
    comparison_display,
    hide_index=True,
    use_container_width=True,
)


# =========================================================
# BEST SCENARIO IDENTIFICATION
# =========================================================
st.markdown(
    '<div class="section-title">Scenario Ranking</div>',
    unsafe_allow_html=True,
)

best_profit_scenario = scenario_df.loc[
    scenario_df["Monthly Profit (RM)"].idxmax()
]

best_margin_scenario = scenario_df.loc[
    scenario_df["Profit Margin (%)"].idxmax()
]

lowest_cost_scenario = scenario_df.loc[
    scenario_df["Cost per Parcel (RM)"].idxmin()
]

highest_utilisation_scenario = scenario_df.loc[
    scenario_df["Fleet Utilisation (%)"].idxmax()
]


ranking_col1, ranking_col2, ranking_col3, ranking_col4 = (
    st.columns(4)
)

with ranking_col1:
    st.metric(
        "Highest Monthly Profit",
        best_profit_scenario["Scenario"],
        delta=(
            f'RM '
            f'{best_profit_scenario["Monthly Profit (RM)"]:,.2f}'
        ),
    )

with ranking_col2:
    st.metric(
        "Highest Profit Margin",
        best_margin_scenario["Scenario"],
        delta=(
            f'{best_margin_scenario["Profit Margin (%)"]:,.1f}%'
        ),
    )

with ranking_col3:
    st.metric(
        "Lowest Cost per Parcel",
        lowest_cost_scenario["Scenario"],
        delta=(
            f'RM '
            f'{lowest_cost_scenario["Cost per Parcel (RM)"]:,.2f}'
        ),
        delta_color="inverse",
    )

with ranking_col4:
    st.metric(
        "Highest Fleet Utilisation",
        highest_utilisation_scenario["Scenario"],
        delta=(
            f'{highest_utilisation_scenario["Fleet Utilisation (%)"]:,.1f}%'
        ),
    )


# =========================================================
# PROFIT-MARGIN CHART
# =========================================================
st.markdown(
    '<div class="section-title">Profit Margin by Scenario</div>',
    unsafe_allow_html=True,
)

profit_margin_chart = (
    scenario_df[
        [
            "Scenario",
            "Profit Margin (%)",
        ]
    ]
    .set_index("Scenario")
)

st.bar_chart(
    profit_margin_chart,
    use_container_width=True,
)


# =========================================================
# MONTHLY PROFIT CHART
# =========================================================
st.markdown(
    '<div class="section-title">Monthly Profit by Scenario</div>',
    unsafe_allow_html=True,
)

monthly_profit_chart = (
    scenario_df[
        [
            "Scenario",
            "Monthly Profit (RM)",
        ]
    ]
    .set_index("Scenario")
)

st.bar_chart(
    monthly_profit_chart,
    use_container_width=True,
)


# =========================================================
# COST AND PRICE COMPARISON
# =========================================================
st.markdown(
    '<div class="section-title">Cost and Selling Price Comparison</div>',
    unsafe_allow_html=True,
)

cost_price_chart = scenario_df[
    [
        "Scenario",
        "Cost per Parcel (RM)",
        "Selling Price per Parcel (RM)",
    ]
].set_index("Scenario")

st.bar_chart(
    cost_price_chart,
    use_container_width=True,
)


# =========================================================
# DETAILED SCENARIO TABLE
# =========================================================
with st.expander(
    "View Detailed Scenario Calculations",
    expanded=False,
):
    detailed_display = scenario_df.copy()

    detailed_currency_columns = [
        column
        for column in detailed_display.columns
        if "(RM)" in column
    ]

    for column in detailed_currency_columns:
        detailed_display[column] = (
            detailed_display[column]
            .map(
                lambda value: f"{value:,.2f}"
            )
        )

    detailed_percentage_columns = [
        column
        for column in detailed_display.columns
        if "(%)" in column
    ]

    for column in detailed_percentage_columns:
        detailed_display[column] = (
            detailed_display[column]
            .map(
                lambda value: f"{value:,.1f}%"
            )
        )

    st.dataframe(
        detailed_display,
        hide_index=True,
        use_container_width=True,
    )


# =========================================================
# ASSUMPTION TABLE
# =========================================================
with st.expander(
    "View Scenario Assumptions",
    expanded=False,
):
    assumption_records = []

    for scenario_name, assumptions in (
        scenario_defaults.items()
    ):
        assumption_records.append(
            {
                "Scenario": scenario_name,
                "Parcel Quantity Change (%)": assumptions[
                    "parcel_change_pct"
                ],
                "Monthly Shipment Change (%)": assumptions[
                    "shipment_change_pct"
                ],
                "Selling Price Change (%)": assumptions[
                    "selling_price_change_pct"
                ],
                "Fuel Cost Change (%)": assumptions[
                    "fuel_cost_change_pct"
                ],
                "Toll Cost Change (%)": assumptions[
                    "toll_cost_change_pct"
                ],
                "Other Direct Cost Change (%)": assumptions[
                    "other_direct_cost_change_pct"
                ],
                "Fixed Cost Change (%)": assumptions[
                    "fixed_cost_change_pct"
                ],
                "Operational Buffer (%)": assumptions[
                    "operational_buffer_pct"
                ],
            }
        )

    assumption_df = pd.DataFrame(
        assumption_records
    )

    st.dataframe(
        assumption_df,
        hide_index=True,
        use_container_width=True,
    )


# =========================================================
# SAVE SCENARIO SIMULATION
# =========================================================
st.markdown(
    "<br>",
    unsafe_allow_html=True,
)

button_col1, button_col2, button_col3 = (
    st.columns([1, 1, 2])
)

with button_col1:
    save_simulation = st.button(
        "💾 Save Scenario Simulation",
        type="primary",
        use_container_width=True,
    )

with button_col2:
    clear_simulation = st.button(
        "🗑️ Clear",
        use_container_width=True,
    )


if save_simulation:
    st.session_state.scenario_simulation = {
        "route_id": route_id,
        "route_category": route_category,
        "origin_region": origin_region,
        "origin_state": origin_state,
        "destination_region": destination_region,
        "destination_state": destination_state,
        "service_level": service_level,

        "parcel_type": parcel_type,
        "vehicle_type": vehicle_type,
        "total_trip_distance_km": float(
            total_trip_distance_km
        ),

        "baseline_parcel_quantity": int(
            baseline_parcel_quantity
        ),
        "baseline_shipments_per_month": int(
            baseline_shipments_per_month
        ),
        "baseline_planned_fleet_size": int(
            baseline_planned_fleet_size
        ),
        "baseline_total_cost_per_shipment": float(
            baseline_total_cost_per_shipment
        ),
        "baseline_selling_price_per_parcel": float(
            baseline_selling_price_per_parcel
        ),
        "baseline_profit_per_shipment": float(
            baseline_profit_per_shipment
        ),
        "baseline_profit_margin_pct": float(
            baseline_profit_margin_pct
        ),

        "selected_scenario": (
            selected_scenario_name
        ),
        "selected_scenario_results": (
            selected_scenario.to_dict()
        ),

        "best_profit_scenario": (
            best_profit_scenario["Scenario"]
        ),
        "best_margin_scenario": (
            best_margin_scenario["Scenario"]
        ),
        "lowest_cost_scenario": (
            lowest_cost_scenario["Scenario"]
        ),
        "highest_utilisation_scenario": (
            highest_utilisation_scenario[
                "Scenario"
            ]
        ),

        "scenario_assumptions": (
            assumption_records
        ),
        "scenario_results": (
            scenario_df.to_dict(
                orient="records"
            )
        ),
    }

    st.success(
        "Scenario simulation has been saved successfully."
    )


if clear_simulation:
    st.session_state.scenario_simulation = {}

    keys_to_clear = [
        "scenario_parcel_change_pct",
        "scenario_shipment_change_pct",
        "scenario_selling_price_change_pct",
        "scenario_fuel_change_pct",
        "scenario_toll_change_pct",
        "scenario_other_direct_change_pct",
        "scenario_fixed_cost_change_pct",
        "scenario_operational_buffer_pct",
        "scenario_selected_name",
    ]

    for key in keys_to_clear:
        st.session_state.pop(
            key,
            None,
        )

    st.rerun()


# =========================================================
# NEXT PAGE
# =========================================================
if st.session_state.get(
    "scenario_simulation"
):
    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )

    if st.button(
        "Continue to Management Dashboard ➡",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/9_Management_Dashboard.py"
        )