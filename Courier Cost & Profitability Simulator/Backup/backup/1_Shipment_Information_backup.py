from utils.data_loader import (load_shipment_reference_data,)
from pathlib import Path

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
# LOAD SHIPMENT REFERENCE DATA
# =========================================================

try:
    shipment_master_data = (
        load_shipment_reference_data()
    )

    state_master_df = (
        shipment_master_data[
            "states"
        ]
    )

    service_level_df = (
        shipment_master_data[
            "service_levels"
        ]
    )

    parcel_master_df = (
        shipment_master_data[
            "parcels"
        ]
    )

except Exception as error:
    st.error(
        "Unable to load the shipment master data."
    )

    st.exception(
        error
    )

    st.stop()

state_options = sorted(
    state_master_df[
        "State"
    ]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

service_level_options = (
    service_level_df[
        "Service Level"
    ]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

parcel_type_options = (
    parcel_master_df[
        "Parcel Type"
    ]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)
# =========================================================
# SESSION STATE
# =========================================================
if "shipment_information" not in st.session_state:
    st.session_state.shipment_information = {}


# =========================================================
# PAGE TITLE
# =========================================================
st.markdown(
    '<div class="main-title">📦 Shipment Information</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-subtitle">
        Enter the shipment route, delivery requirement and parcel details.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# INFORMATION BASIS
# =========================================================
cost_basis(
    "Shipment Information Basis",
    """
    Origin and destination are used to determine the applicable operational
    regions, route options and available transport modes.

    Vehicle requirements will subsequently be evaluated based on parcel
    quantity, total weight, shipment volume, service level and vehicle capacity.
    """,
)


# =========================================================
# ROUTE INFORMATION
# =========================================================
st.markdown(
    '<div class="section-title">Route Information</div>',
    unsafe_allow_html=True,
)

region_options = sorted(state_master_df["Region"].unique().tolist())

route_col1, route_col2 = st.columns(2)

with route_col1:
    origin_region = st.selectbox(
        "Origin Region",
        options=["Select Region"] + region_options,
        key="origin_region",
    )

    if origin_region != "Select Region":
        origin_states = (
            state_master_df.loc[
                state_master_df["Region"] == origin_region,
                "State",
            ]
            .sort_values()
            .tolist()
        )
    else:
        origin_states = []
        
        origin_state = st.selectbox(
            "Origin State",
            options=state_options,
            )

with route_col2:
    destination_region = st.selectbox(
        "Destination Region",
        options=["Select Region"] + region_options,
        key="destination_region",
    )

    if destination_region != "Select Region":
        destination_states = (
            state_master_df.loc[
                state_master_df["Region"] == destination_region,
                "State",
            ]
            .sort_values()
            .tolist()
        )
    else:
        destination_states = []

    destination_state = st.selectbox(
        "Destination State",
        options=state_options,
        )

state_region_mapping = dict(
    zip(
        state_master_df[
            "State"
        ],
        state_master_df[
            "Region"
        ],
    )
)

origin_region = state_region_mapping.get(origin_state, "")
destination_region = state_region_mapping.get(destination_state, "")

# =========================================================
# DELIVERY REQUIREMENT
# =========================================================
st.markdown(
    '<div class="section-title">Delivery Requirement</div>',
    unsafe_allow_html=True,
)

delivery_col1, delivery_col2, delivery_col3 = st.columns(3)

service_options = service_master_df["Service Level"].tolist()

with delivery_col1:
    service_level = st.selectbox(
        "Service Level",
        options=service_level_options,
        )

with delivery_col2:
    shipment_date = st.date_input(
        "Shipment Date",
        key="shipment_date",
    )

with delivery_col3:
    delivery_frequency = st.selectbox(
        "Delivery Frequency",
        options=[
            "One-Time Delivery",
            "Daily",
            "Weekly",
            "Monthly",
        ],
        key="delivery_frequency",
    )


# =========================================================
# DISPLAY SERVICE-LEVEL INFORMATION
# =========================================================
if service_level != "Select Service Level":
    selected_service = service_master_df.loc[
        service_master_df["Service Level"] == service_level
    ].iloc[0]

    info_col1, info_col2, info_col3 = st.columns(3)

    with info_col1:
        st.metric(
            "Target Delivery",
            selected_service["Target Delivery (Days)"],
        )

    with info_col2:
        st.metric(
            "Priority",
            selected_service["Priority"],
        )

    with info_col3:
        st.metric(
            "Cost Multiplier",
            f'{float(selected_service["Cost Multiplier"]):.2f}x',
        )


# =========================================================
# PARCEL INFORMATION
# =========================================================
st.markdown(
    '<div class="section-title">Parcel Information</div>',
    unsafe_allow_html=True,
)

parcel_col1, parcel_col2 = st.columns(2)

parcel_options = parcel_master_df["Parcel Type"].tolist()

with parcel_col1:
    parcel_type = st.selectbox(
        "Parcel Type",
        options=parcel_type_options,
        )

with parcel_col2:
    parcel_quantity = st.number_input(
        "Number of Parcels",
        min_value=1,
        value=1,
        step=1,
        key="parcel_quantity",
    )


# =========================================================
# STANDARD OR USER-DEFINED DIMENSIONS
# =========================================================
length_cm = 0.0
width_cm = 0.0
height_cm = 0.0
weight_per_parcel_kg = 0.0
volumetric_divisor = 5000.0

if parcel_type != "Select Parcel Type":
    selected_parcel = parcel_master_df.loc[
        parcel_master_df["Parcel Type"] == parcel_type
    ].iloc[0]

    volumetric_divisor = float(
        selected_parcel["Volumetric Divisor"]
    )

    is_oversized = parcel_type == "Oversized"

    dimension_col1, dimension_col2 = st.columns(2)

    with dimension_col1:
        if is_oversized:
            length_cm = st.number_input(
                "Length per Parcel (cm)",
                min_value=0.10,
                value=60.0,
                step=1.0,
                key="parcel_length",
            )

            width_cm = st.number_input(
                "Width per Parcel (cm)",
                min_value=0.10,
                value=50.0,
                step=1.0,
                key="parcel_width",
            )

        else:
            length_cm = float(selected_parcel["Length (cm)"])
            width_cm = float(selected_parcel["Width (cm)"])

            st.number_input(
                "Length per Parcel (cm)",
                value=length_cm,
                disabled=True,
            )

            st.number_input(
                "Width per Parcel (cm)",
                value=width_cm,
                disabled=True,
            )

    with dimension_col2:
        if is_oversized:
            height_cm = st.number_input(
                "Height per Parcel (cm)",
                min_value=0.10,
                value=40.0,
                step=1.0,
                key="parcel_height",
            )

            weight_per_parcel_kg = st.number_input(
                "Actual Weight per Parcel (kg)",
                min_value=0.01,
                value=1.0,
                step=0.10,
                key="parcel_weight",
            )

        else:
            height_cm = float(selected_parcel["Height (cm)"])
            maximum_weight = float(
                selected_parcel["Max Weight (kg)"]
            )

            st.number_input(
                "Height per Parcel (cm)",
                value=height_cm,
                disabled=True,
            )

            weight_per_parcel_kg = st.number_input(
                "Actual Weight per Parcel (kg)",
                min_value=0.01,
                max_value=maximum_weight,
                value=min(1.0, maximum_weight),
                step=0.10,
                key="parcel_weight",
                help=(
                    f"Maximum recommended weight for a "
                    f"{parcel_type.lower()} parcel is "
                    f"{maximum_weight:,.2f} kg."
                ),
            )


# =========================================================
# SHIPMENT CALCULATION
# =========================================================
if parcel_type != "Select Parcel Type":
    volume_per_parcel_m3 = (
        length_cm * width_cm * height_cm
    ) / 1_000_000

    total_volume_m3 = volume_per_parcel_m3 * parcel_quantity

    volumetric_weight_per_parcel = (
        length_cm * width_cm * height_cm
    ) / volumetric_divisor

    total_actual_weight = (
        weight_per_parcel_kg * parcel_quantity
    )

    total_volumetric_weight = (
        volumetric_weight_per_parcel * parcel_quantity
    )

    chargeable_weight = max(
        total_actual_weight,
        total_volumetric_weight,
    )

    st.markdown(
        '<div class="section-title">Shipment Summary</div>',
        unsafe_allow_html=True,
    )

    summary_col1, summary_col2, summary_col3, summary_col4 = (
        st.columns(4)
    )

    with summary_col1:
        st.metric(
            "Total Parcels",
            f"{parcel_quantity:,}",
        )

    with summary_col2:
        st.metric(
            "Total Actual Weight",
            f"{total_actual_weight:,.2f} kg",
        )

    with summary_col3:
        st.metric(
            "Total Volume",
            f"{total_volume_m3:,.3f} m³",
        )

    with summary_col4:
        st.metric(
            "Chargeable Weight",
            f"{chargeable_weight:,.2f} kg",
        )

else:
    volume_per_parcel_m3 = 0.0
    total_volume_m3 = 0.0
    volumetric_weight_per_parcel = 0.0
    total_actual_weight = 0.0
    total_volumetric_weight = 0.0
    chargeable_weight = 0.0


# =========================================================
# VALIDATION
# =========================================================
validation_errors = []

if origin_region == "Select Region":
    validation_errors.append("Select the origin region.")

if not origin_state:
    validation_errors.append("Select the origin state.")

if destination_region == "Select Region":
    validation_errors.append("Select the destination region.")

if not destination_state:
    validation_errors.append("Select the destination state.")

if service_level == "Select Service Level":
    validation_errors.append("Select the service level.")

if parcel_type == "Select Parcel Type":
    validation_errors.append("Select the parcel type.")


# =========================================================
# SAVE SHIPMENT INFORMATION
# =========================================================
st.markdown("<br>", unsafe_allow_html=True)

button_col1, button_col2, button_col3 = st.columns([1, 1, 2])

with button_col1:
    save_shipment = st.button(
        "💾 Save Shipment",
        type="primary",
        use_container_width=True,
    )

with button_col2:
    clear_shipment = st.button(
        "🗑️ Clear",
        use_container_width=True,
    )


if save_shipment:
    if validation_errors:
        for error in validation_errors:
            st.warning(error)

    else:
        selected_service = service_master_df.loc[
            service_master_df["Service Level"] == service_level
        ].iloc[0]

        st.session_state.shipment_information = {
            "origin_region": origin_region,
            "origin_state": origin_state,
            "destination_region": destination_region,
            "destination_state": destination_state,
            "service_level": service_level,
            "target_delivery": selected_service[
                "Target Delivery (Days)"
            ],
            "priority": selected_service["Priority"],
            "service_cost_multiplier": float(
                selected_service["Cost Multiplier"]
            ),
            "shipment_date": shipment_date,
            "delivery_frequency": delivery_frequency,
            "parcel_type": parcel_type,
            "parcel_quantity": int(parcel_quantity),
            "length_cm": float(length_cm),
            "width_cm": float(width_cm),
            "height_cm": float(height_cm),
            "weight_per_parcel_kg": float(
                weight_per_parcel_kg
            ),
            "volume_per_parcel_m3": float(
                volume_per_parcel_m3
            ),
            "total_actual_weight_kg": float(
                total_actual_weight
            ),
            "total_volumetric_weight_kg": float(
                total_volumetric_weight
            ),
            "chargeable_weight_kg": float(
                chargeable_weight
            ),
            "total_volume_m3": float(total_volume_m3),
            "volumetric_divisor": float(
                volumetric_divisor
            ),
        }

        st.success(
            "Shipment information has been saved successfully."
        )


if clear_shipment:
    st.session_state.shipment_information = {}

    keys_to_clear = [
        "origin_region",
        "origin_state",
        "destination_region",
        "destination_state",
        "service_level",
        "shipment_date",
        "delivery_frequency",
        "parcel_type",
        "parcel_quantity",
        "parcel_length",
        "parcel_width",
        "parcel_height",
        "parcel_weight",
    ]

    for key in keys_to_clear:
        st.session_state.pop(key, None)

    st.rerun()