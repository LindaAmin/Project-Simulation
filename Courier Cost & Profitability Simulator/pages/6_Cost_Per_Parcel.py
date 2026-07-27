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


required_pages = {
    "Shipment Information": shipment,
    "Route Intelligence": route,
    "Parcel Assessment": parcel,
    "Fleet Capacity": fleet,
    "Operating Cost": operating_cost,
}

incomplete_pages = [
    page_name
    for page_name, page_data in required_pages.items()
    if not page_data
]

if incomplete_pages:
    st.warning(
        "Complete and save the following pages before calculating "
        "the cost per parcel: "
        + ", ".join(incomplete_pages)
    )
    st.stop()


# =========================================================
# READ SAVED INFORMATION
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

parcel_quantity = int(
    parcel.get(
        "parcel_quantity",
        0,
    )
)

total_actual_weight_kg = float(
    parcel.get(
        "total_actual_weight_kg",
        0,
    )
)

chargeable_weight_kg = float(
    parcel.get(
        "chargeable_weight_kg",
        0,
    )
)

total_volume_m3 = float(
    parcel.get(
        "total_volume_m3",
        0,
    )
)

vehicle_type = fleet.get(
    "selected_vehicle_type",
    "",
)

required_vehicles = int(
    fleet.get(
        "required_vehicles",
        0,
    )
)

planned_fleet_size = int(
    fleet.get(
        "planned_fleet_size",
        required_vehicles,
    )
)

overall_utilisation_pct = float(
    fleet.get(
        "overall_utilisation_pct",
        0,
    )
)

shipments_per_month = int(
    operating_cost.get(
        "shipments_per_month",
        0,
    )
)

direct_trip_cost = float(
    operating_cost.get(
        "direct_trip_cost",
        0,
    )
)

allocated_fixed_cost_per_shipment = float(
    operating_cost.get(
        "allocated_fixed_cost_per_shipment",
        0,
    )
)

total_operating_cost_per_shipment = float(
    operating_cost.get(
        "total_operating_cost_per_shipment",
        0,
    )
)

monthly_direct_operating_cost = float(
    operating_cost.get(
        "monthly_direct_operating_cost",
        0,
    )
)

total_monthly_fixed_cost = float(
    operating_cost.get(
        "total_monthly_fixed_cost",
        0,
    )
)

total_monthly_operating_cost = float(
    operating_cost.get(
        "total_monthly_operating_cost",
        0,
    )
)

cost_breakdown_records = operating_cost.get(
    "cost_breakdown",
    [],
)


# =========================================================
# VALIDATION
# =========================================================
required_numeric_values = {
    "Parcel quantity": parcel_quantity,
    "Total actual weight": total_actual_weight_kg,
    "Chargeable weight": chargeable_weight_kg,
    "Shipment volume": total_volume_m3,
    "Planned fleet size": planned_fleet_size,
    "Shipments per month": shipments_per_month,
    "Total operating cost": total_operating_cost_per_shipment,
}

invalid_values = [
    field_name
    for field_name, field_value in required_numeric_values.items()
    if field_value is None or float(field_value) <= 0
]

if invalid_values:
    st.error(
        "The following cost-per-parcel inputs are missing or invalid: "
        + ", ".join(invalid_values)
    )

    st.info(
        "Review the saved information on Pages 3, 4 and 5."
    )

    st.stop()


# =========================================================
# SESSION STATE
# =========================================================
if "cost_per_parcel" not in st.session_state:
    st.session_state.cost_per_parcel = {}


# =========================================================
# PAGE TITLE
# =========================================================
st.markdown(
    '<div class="main-title">📊 Cost per Parcel</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-subtitle">
        Convert total shipment operating costs into parcel,
        weight, volume and fleet unit-cost measures.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# COST BASIS
# =========================================================
cost_basis(
    "Cost per Parcel Basis",
    """
    Direct and fixed costs are allocated across the total number of
    parcels in the shipment.

    Additional unit-cost measures are calculated using actual shipment
    weight, chargeable weight, shipment volume, distance and planned
    fleet size. These results provide the cost baseline for the
    profitability assessment.
    """,
)


# =========================================================
# SHIPMENT SUMMARY
# =========================================================
st.markdown(
    '<div class="section-title">Shipment Costing Summary</div>',
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


shipment_col1, shipment_col2, shipment_col3, shipment_col4 = (
    st.columns(4)
)

with shipment_col1:
    st.metric(
        "Parcel Quantity",
        f"{parcel_quantity:,}",
    )

with shipment_col2:
    st.metric(
        "Actual Weight",
        f"{total_actual_weight_kg:,.2f} kg",
    )

with shipment_col3:
    st.metric(
        "Shipment Volume",
        f"{total_volume_m3:,.3f} m³",
    )

with shipment_col4:
    st.metric(
        "Planned Fleet",
        f"{planned_fleet_size:,}",
    )


# =========================================================
# COST PER PARCEL CALCULATION
# =========================================================
direct_cost_per_parcel = (
    direct_trip_cost
    / parcel_quantity
)

fixed_cost_per_parcel = (
    allocated_fixed_cost_per_shipment
    / parcel_quantity
)

total_cost_per_parcel = (
    total_operating_cost_per_shipment
    / parcel_quantity
)


# =========================================================
# MONTHLY PARCEL VOLUME
# =========================================================
monthly_parcel_quantity = (
    parcel_quantity
    * shipments_per_month
)

monthly_direct_cost_per_parcel = (
    monthly_direct_operating_cost
    / monthly_parcel_quantity
)

monthly_fixed_cost_per_parcel = (
    total_monthly_fixed_cost
    / monthly_parcel_quantity
)

monthly_total_cost_per_parcel = (
    total_monthly_operating_cost
    / monthly_parcel_quantity
)


# =========================================================
# OTHER UNIT-COST MEASURES
# =========================================================
cost_per_actual_kg = (
    total_operating_cost_per_shipment
    / total_actual_weight_kg
)

cost_per_chargeable_kg = (
    total_operating_cost_per_shipment
    / chargeable_weight_kg
)

cost_per_cubic_metre = (
    total_operating_cost_per_shipment
    / total_volume_m3
)

cost_per_vehicle = (
    total_operating_cost_per_shipment
    / planned_fleet_size
)

cost_per_trip_km = (
    total_operating_cost_per_shipment
    / total_trip_distance_km
    if total_trip_distance_km > 0
    else 0
)

cost_per_vehicle_km = (
    total_operating_cost_per_shipment
    / (
        total_trip_distance_km
        * planned_fleet_size
    )
    if (
        total_trip_distance_km > 0
        and planned_fleet_size > 0
    )
    else 0
)


# =========================================================
# DIRECT AND FIXED COST SHARES
# =========================================================
direct_cost_share_pct = (
    direct_trip_cost
    / total_operating_cost_per_shipment
    * 100
)

fixed_cost_share_pct = (
    allocated_fixed_cost_per_shipment
    / total_operating_cost_per_shipment
    * 100
)


# =========================================================
# COST PER PARCEL RESULTS
# =========================================================
st.markdown(
    '<div class="section-title">Cost per Parcel Results</div>',
    unsafe_allow_html=True,
)

parcel_cost_col1, parcel_cost_col2, parcel_cost_col3 = (
    st.columns(3)
)

with parcel_cost_col1:
    st.metric(
        "Direct Cost per Parcel",
        f"RM {direct_cost_per_parcel:,.2f}",
    )

with parcel_cost_col2:
    st.metric(
        "Fixed Cost per Parcel",
        f"RM {fixed_cost_per_parcel:,.2f}",
    )

with parcel_cost_col3:
    st.metric(
        "Total Cost per Parcel",
        f"RM {total_cost_per_parcel:,.2f}",
    )


share_col1, share_col2, share_col3 = st.columns(3)

with share_col1:
    st.metric(
        "Direct Cost Share",
        f"{direct_cost_share_pct:,.1f}%",
    )

with share_col2:
    st.metric(
        "Fixed Cost Share",
        f"{fixed_cost_share_pct:,.1f}%",
    )

with share_col3:
    st.metric(
        "Fleet Utilisation",
        f"{overall_utilisation_pct:,.1f}%",
    )


# =========================================================
# UNIT-COST RESULTS
# =========================================================
st.markdown(
    '<div class="section-title">Additional Unit-Cost Measures</div>',
    unsafe_allow_html=True,
)

unit_col1, unit_col2, unit_col3 = st.columns(3)

with unit_col1:
    st.metric(
        "Cost per Actual kg",
        f"RM {cost_per_actual_kg:,.2f}",
    )

with unit_col2:
    st.metric(
        "Cost per Chargeable kg",
        f"RM {cost_per_chargeable_kg:,.2f}",
    )

with unit_col3:
    st.metric(
        "Cost per m³",
        f"RM {cost_per_cubic_metre:,.2f}",
    )


unit_col4, unit_col5, unit_col6 = st.columns(3)

with unit_col4:
    st.metric(
        "Cost per Vehicle",
        f"RM {cost_per_vehicle:,.2f}",
    )

with unit_col5:
    st.metric(
        "Cost per Trip km",
        f"RM {cost_per_trip_km:,.2f}",
    )

with unit_col6:
    st.metric(
        "Cost per Vehicle-km",
        f"RM {cost_per_vehicle_km:,.2f}",
    )


# =========================================================
# MONTHLY COST RESULTS
# =========================================================
st.markdown(
    '<div class="section-title">Monthly Unit-Cost Projection</div>',
    unsafe_allow_html=True,
)

monthly_col1, monthly_col2, monthly_col3 = st.columns(3)

with monthly_col1:
    st.metric(
        "Monthly Parcel Volume",
        f"{monthly_parcel_quantity:,}",
    )

with monthly_col2:
    st.metric(
        "Monthly Operating Cost",
        f"RM {total_monthly_operating_cost:,.2f}",
    )

with monthly_col3:
    st.metric(
        "Monthly Cost per Parcel",
        f"RM {monthly_total_cost_per_parcel:,.2f}",
    )


monthly_detail_col1, monthly_detail_col2 = st.columns(2)

with monthly_detail_col1:
    st.metric(
        "Monthly Direct Cost per Parcel",
        f"RM {monthly_direct_cost_per_parcel:,.2f}",
    )

with monthly_detail_col2:
    st.metric(
        "Monthly Fixed Cost per Parcel",
        f"RM {monthly_fixed_cost_per_parcel:,.2f}",
    )


# =========================================================
# COST EFFICIENCY INTERPRETATION
# =========================================================
st.markdown(
    '<div class="section-title">Cost Efficiency Interpretation</div>',
    unsafe_allow_html=True,
)


def classify_fleet_utilisation(
    utilisation_pct: float,
) -> tuple[str, str]:
    """
    Classify fleet utilisation for management interpretation.
    """

    if utilisation_pct >= 85:
        return (
            "High Utilisation",
            (
                "The selected fleet is highly utilised. "
                "There is limited spare capacity for an increase "
                "in shipment volume."
            ),
        )

    if utilisation_pct >= 65:
        return (
            "Efficient Utilisation",
            (
                "The selected fleet has a reasonable balance between "
                "capacity usage and operational flexibility."
            ),
        )

    if utilisation_pct >= 40:
        return (
            "Moderate Utilisation",
            (
                "The fleet has available capacity. Consolidating "
                "additional parcels may reduce the cost per parcel."
            ),
        )

    return (
        "Low Utilisation",
        (
            "The selected fleet is underutilised. Review the vehicle "
            "type, operational buffer, shipment frequency or parcel "
            "consolidation strategy."
        ),
    )


utilisation_classification, utilisation_message = (
    classify_fleet_utilisation(
        overall_utilisation_pct
    )
)


interpretation_col1, interpretation_col2 = st.columns(2)

with interpretation_col1:
    st.markdown("**Fleet Cost Efficiency**")

    if utilisation_classification in {
        "High Utilisation",
        "Efficient Utilisation",
    }:
        st.success(
            f"{utilisation_classification}: "
            f"{utilisation_message}"
        )

    elif utilisation_classification == "Moderate Utilisation":
        st.info(
            f"{utilisation_classification}: "
            f"{utilisation_message}"
        )

    else:
        st.warning(
            f"{utilisation_classification}: "
            f"{utilisation_message}"
        )


with interpretation_col2:
    st.markdown("**Cost Structure**")

    if direct_cost_share_pct > fixed_cost_share_pct:
        st.info(
            f"Direct costs represent "
            f"{direct_cost_share_pct:,.1f}% of the total cost. "
            "Fuel, toll, maintenance, tyres and overtime are the "
            "main shipment-sensitive cost components."
        )

    else:
        st.info(
            f"Fixed costs represent "
            f"{fixed_cost_share_pct:,.1f}% of the total cost. "
            "Increasing monthly shipment and parcel volume may "
            "improve fixed-cost absorption."
        )


# =========================================================
# BREAK-EVEN VOLUME SENSITIVITY
# =========================================================
st.markdown(
    '<div class="section-title">Parcel Volume Sensitivity</div>',
    unsafe_allow_html=True,
)

sensitivity_col1, sensitivity_col2 = st.columns(2)

with sensitivity_col1:
    volume_adjustment_pct = st.slider(
        "Parcel Volume Change (%)",
        min_value=-50,
        max_value=100,
        value=0,
        step=5,
        key="cost_parcel_volume_adjustment",
        help=(
            "This simple sensitivity assumes total shipment cost "
            "remains unchanged within the current fleet capacity."
        ),
    )

with sensitivity_col2:
    adjusted_parcel_quantity = max(
        round(
            parcel_quantity
            * (
                1
                + volume_adjustment_pct / 100
            )
        ),
        1,
    )

    st.metric(
        "Adjusted Parcel Quantity",
        f"{adjusted_parcel_quantity:,}",
    )


adjusted_cost_per_parcel = (
    total_operating_cost_per_shipment
    / adjusted_parcel_quantity
)

cost_change_per_parcel = (
    adjusted_cost_per_parcel
    - total_cost_per_parcel
)

cost_change_pct = (
    cost_change_per_parcel
    / total_cost_per_parcel
    * 100
    if total_cost_per_parcel > 0
    else 0
)


sensitivity_result_col1, sensitivity_result_col2, sensitivity_result_col3 = (
    st.columns(3)
)

with sensitivity_result_col1:
    st.metric(
        "Current Cost per Parcel",
        f"RM {total_cost_per_parcel:,.2f}",
    )

with sensitivity_result_col2:
    st.metric(
        "Adjusted Cost per Parcel",
        f"RM {adjusted_cost_per_parcel:,.2f}",
    )

with sensitivity_result_col3:
    st.metric(
        "Cost Change",
        f"{cost_change_pct:,.1f}%",
        delta=f"RM {cost_change_per_parcel:,.2f}",
        delta_color="inverse",
    )


st.caption(
    "The volume sensitivity is valid only while the adjusted parcel "
    "quantity remains within the selected fleet capacity. A larger "
    "shipment may require recalculation on the Fleet Capacity page."
)


# =========================================================
# COST BREAKDOWN BY PARCEL
# =========================================================
st.markdown(
    '<div class="section-title">Cost Breakdown per Parcel</div>',
    unsafe_allow_html=True,
)

if cost_breakdown_records:
    cost_breakdown_df = pd.DataFrame(
        cost_breakdown_records
    )

    required_breakdown_columns = {
        "Cost Category",
        "Cost Item",
        "Cost per Shipment (RM)",
    }

    if required_breakdown_columns.issubset(
        cost_breakdown_df.columns
    ):
        cost_breakdown_df[
            "Cost per Shipment (RM)"
        ] = pd.to_numeric(
            cost_breakdown_df[
                "Cost per Shipment (RM)"
            ],
            errors="coerce",
        ).fillna(0)

        cost_breakdown_df[
            "Cost per Parcel (RM)"
        ] = (
            cost_breakdown_df[
                "Cost per Shipment (RM)"
            ]
            / parcel_quantity
        )

        cost_breakdown_df[
            "Share of Parcel Cost (%)"
        ] = (
            cost_breakdown_df[
                "Cost per Parcel (RM)"
            ]
            / total_cost_per_parcel
            * 100
            if total_cost_per_parcel > 0
            else 0
        )

        display_cost_breakdown = cost_breakdown_df[
            [
                "Cost Category",
                "Cost Item",
                "Cost per Shipment (RM)",
                "Cost per Parcel (RM)",
                "Share of Parcel Cost (%)",
            ]
        ].copy()

        display_cost_breakdown[
            "Cost per Shipment (RM)"
        ] = display_cost_breakdown[
            "Cost per Shipment (RM)"
        ].map(
            lambda value: f"{value:,.2f}"
        )

        display_cost_breakdown[
            "Cost per Parcel (RM)"
        ] = display_cost_breakdown[
            "Cost per Parcel (RM)"
        ].map(
            lambda value: f"{value:,.2f}"
        )

        display_cost_breakdown[
            "Share of Parcel Cost (%)"
        ] = display_cost_breakdown[
            "Share of Parcel Cost (%)"
        ].map(
            lambda value: f"{value:,.1f}%"
        )

        st.dataframe(
            display_cost_breakdown,
            hide_index=True,
            use_container_width=True,
        )

    else:
        st.info(
            "The saved operating-cost breakdown does not contain "
            "all required columns."
        )

else:
    cost_breakdown_df = pd.DataFrame()

    st.info(
        "No detailed operating-cost breakdown was saved on Page 5."
    )


# =========================================================
# COST SUMMARY TABLE
# =========================================================
with st.expander(
    "View Detailed Unit-Cost Summary",
    expanded=False,
):
    unit_cost_summary = pd.DataFrame(
        {
            "Cost Measure": [
                "Direct cost per shipment",
                "Fixed cost per shipment",
                "Total cost per shipment",
                "Direct cost per parcel",
                "Fixed cost per parcel",
                "Total cost per parcel",
                "Cost per actual kilogram",
                "Cost per chargeable kilogram",
                "Cost per cubic metre",
                "Cost per vehicle",
                "Cost per trip kilometre",
                "Cost per vehicle-kilometre",
                "Monthly parcel quantity",
                "Monthly total operating cost",
                "Monthly cost per parcel",
            ],
            "Value": [
                f"RM {direct_trip_cost:,.2f}",
                (
                    f"RM "
                    f"{allocated_fixed_cost_per_shipment:,.2f}"
                ),
                (
                    f"RM "
                    f"{total_operating_cost_per_shipment:,.2f}"
                ),
                f"RM {direct_cost_per_parcel:,.2f}",
                f"RM {fixed_cost_per_parcel:,.2f}",
                f"RM {total_cost_per_parcel:,.2f}",
                f"RM {cost_per_actual_kg:,.2f}",
                f"RM {cost_per_chargeable_kg:,.2f}",
                f"RM {cost_per_cubic_metre:,.2f}",
                f"RM {cost_per_vehicle:,.2f}",
                f"RM {cost_per_trip_km:,.2f}",
                f"RM {cost_per_vehicle_km:,.2f}",
                f"{monthly_parcel_quantity:,}",
                f"RM {total_monthly_operating_cost:,.2f}",
                f"RM {monthly_total_cost_per_parcel:,.2f}",
            ],
        }
    )

    st.dataframe(
        unit_cost_summary,
        hide_index=True,
        use_container_width=True,
    )


# =========================================================
# SAVE COST PER PARCEL
# =========================================================
st.markdown(
    "<br>",
    unsafe_allow_html=True,
)

button_col1, button_col2, button_col3 = (
    st.columns([1, 1, 2])
)

with button_col1:
    save_cost_per_parcel = st.button(
        "💾 Save Cost per Parcel",
        type="primary",
        use_container_width=True,
    )

with button_col2:
    clear_cost_per_parcel = st.button(
        "🗑️ Clear",
        use_container_width=True,
    )


if save_cost_per_parcel:
    st.session_state.cost_per_parcel = {
        "route_id": route_id,
        "route_category": route_category,
        "origin_region": origin_region,
        "origin_state": origin_state,
        "destination_region": destination_region,
        "destination_state": destination_state,
        "service_level": service_level,

        "parcel_type": parcel_type,
        "parcel_quantity": int(
            parcel_quantity
        ),
        "monthly_parcel_quantity": int(
            monthly_parcel_quantity
        ),

        "total_actual_weight_kg": float(
            total_actual_weight_kg
        ),
        "chargeable_weight_kg": float(
            chargeable_weight_kg
        ),
        "total_volume_m3": float(
            total_volume_m3
        ),

        "vehicle_type": vehicle_type,
        "required_vehicles": int(
            required_vehicles
        ),
        "planned_fleet_size": int(
            planned_fleet_size
        ),
        "overall_utilisation_pct": float(
            overall_utilisation_pct
        ),
        "utilisation_classification": (
            utilisation_classification
        ),

        "shipments_per_month": int(
            shipments_per_month
        ),
        "total_trip_distance_km": float(
            total_trip_distance_km
        ),

        "direct_cost_per_shipment": float(
            direct_trip_cost
        ),
        "fixed_cost_per_shipment": float(
            allocated_fixed_cost_per_shipment
        ),
        "total_cost_per_shipment": float(
            total_operating_cost_per_shipment
        ),

        "direct_cost_per_parcel": float(
            direct_cost_per_parcel
        ),
        "fixed_cost_per_parcel": float(
            fixed_cost_per_parcel
        ),
        "total_cost_per_parcel": float(
            total_cost_per_parcel
        ),

        "direct_cost_share_pct": float(
            direct_cost_share_pct
        ),
        "fixed_cost_share_pct": float(
            fixed_cost_share_pct
        ),

        "cost_per_actual_kg": float(
            cost_per_actual_kg
        ),
        "cost_per_chargeable_kg": float(
            cost_per_chargeable_kg
        ),
        "cost_per_cubic_metre": float(
            cost_per_cubic_metre
        ),
        "cost_per_vehicle": float(
            cost_per_vehicle
        ),
        "cost_per_trip_km": float(
            cost_per_trip_km
        ),
        "cost_per_vehicle_km": float(
            cost_per_vehicle_km
        ),

        "monthly_direct_cost_per_parcel": float(
            monthly_direct_cost_per_parcel
        ),
        "monthly_fixed_cost_per_parcel": float(
            monthly_fixed_cost_per_parcel
        ),
        "monthly_total_cost_per_parcel": float(
            monthly_total_cost_per_parcel
        ),
        "total_monthly_operating_cost": float(
            total_monthly_operating_cost
        ),

        "volume_adjustment_pct": float(
            volume_adjustment_pct
        ),
        "adjusted_parcel_quantity": int(
            adjusted_parcel_quantity
        ),
        "adjusted_cost_per_parcel": float(
            adjusted_cost_per_parcel
        ),
        "cost_change_per_parcel": float(
            cost_change_per_parcel
        ),
        "cost_change_pct": float(
            cost_change_pct
        ),

        "cost_breakdown_per_parcel": (
            cost_breakdown_df.to_dict(
                orient="records"
            )
            if not cost_breakdown_df.empty
            else []
        ),
    }

    st.success(
        "Cost-per-parcel assessment has been saved successfully."
    )


if clear_cost_per_parcel:
    st.session_state.cost_per_parcel = {}

    keys_to_clear = [
        "cost_parcel_volume_adjustment",
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
    "cost_per_parcel"
):
    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )

    if st.button(
        "Continue to Profitability ➡",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/7_Profitability.py"
        )


cost_basis(
    "Calculation Basis",
    """
    Cost per Parcel = Total Allocated Operating Cost ÷ Total Number of Chargeable Parcels.
    The calculation may include transportation, vehicle, manpower and overhead costs.
    """,
)