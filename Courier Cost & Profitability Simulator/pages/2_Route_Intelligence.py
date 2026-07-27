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
# FILE PATHS
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

ROUTE_FILE = DATA_DIR / "region_routes.csv"
VEHICLE_FILE = DATA_DIR / "vehicle_master.csv"


# =========================================================
# DATA LOADING FUNCTIONS
# =========================================================
@st.cache_data
def load_route_master() -> pd.DataFrame:
    """Load and clean the regional route master."""

    route_df = pd.read_csv(ROUTE_FILE)

    text_columns = [
        "Route ID",
        "Origin Region",
        "Destination Region",
        "Vehicle Type",
        "Service Level",
        "Target Delivery (Days)",
        "Priority",
    ]

    for column in text_columns:
        if column in route_df.columns:
            route_df[column] = (
                route_df[column]
                .astype(str)
                .str.strip()
            )

    route_df = route_df.dropna(
        subset=[
            "Route ID",
            "Origin Region",
            "Destination Region",
            "Vehicle Type",
            "Service Level",
        ]
    )

    return route_df.reset_index(drop=True)


@st.cache_data
def load_vehicle_master() -> pd.DataFrame:
    """Load active vehicle records."""

    vehicle_df = pd.read_csv(VEHICLE_FILE)

    text_columns = [
        "Vehicle ID",
        "Vehicle Type",
        "Category",
        "Fuel Type",
        "State",
        "Region Availability",
        "Status",
    ]

    for column in text_columns:
        if column in vehicle_df.columns:
            vehicle_df[column] = (
                vehicle_df[column]
                .astype(str)
                .str.strip()
            )

    numeric_columns = [
        "Max Weight (kg)",
        "Max Volume (m³)",
        "Max Parcels",
        "Avg Speed (km/h)",
        "Average Parcel Per Item",
    ]

    for column in numeric_columns:
        if column in vehicle_df.columns:
            vehicle_df[column] = pd.to_numeric(
                vehicle_df[column],
                errors="coerce",
            )

    vehicle_df = vehicle_df[
        vehicle_df["Status"].str.lower() == "active"
    ]

    return vehicle_df.reset_index(drop=True)


# =========================================================
# LOAD DATA
# =========================================================
try:
    route_master = load_route_master()
    vehicle_master = load_vehicle_master()

except FileNotFoundError as error:
    st.error(
        f"Required master-data file was not found: "
        f"{error.filename}"
    )
    st.stop()

except Exception as error:
    st.error(
        f"Unable to load the route intelligence data: {error}"
    )
    st.stop()


# =========================================================
# REQUIRED SESSION STATE
# =========================================================
shipment = st.session_state.get(
    "shipment_information",
    {},
)

if not shipment:
    st.warning(
        "Shipment information has not been entered. "
        "Complete Page 1 before proceeding."
    )

    if st.button(
        "⬅ Go to Shipment Information",
        use_container_width=False,
    ):
        st.switch_page("pages/1_Shipment_Information.py")

    st.stop()


# =========================================================
# READ SHIPMENT INFORMATION
# =========================================================
origin_region = shipment.get("origin_region")
origin_state = shipment.get("origin_state")
destination_region = shipment.get("destination_region")
destination_state = shipment.get("destination_state")
service_level = shipment.get("service_level")


required_fields = {
    "Origin Region": origin_region,
    "Origin State": origin_state,
    "Destination Region": destination_region,
    "Destination State": destination_state,
    "Service Level": service_level,
}

missing_fields = [
    field_name
    for field_name, field_value in required_fields.items()
    if not field_value
    or field_value in {
        "Select Region",
        "Select State",
        "Select Service Level",
    }
]

if missing_fields:
    st.error(
        "The following shipment information is incomplete: "
        + ", ".join(missing_fields)
    )
    st.stop()


# =========================================================
# SESSION STATE
# =========================================================
if "route_intelligence" not in st.session_state:
    st.session_state.route_intelligence = {}


# =========================================================
# PAGE TITLE
# =========================================================
st.markdown(
    '<div class="main-title">🗺️ Route Intelligence</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-subtitle">
        Identify the matching route, feasible transport modes,
        estimated journey and delivery requirements.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# INFORMATION BASIS
# =========================================================
cost_basis(
    "Route Intelligence Basis",
    """
    The system matches the origin region, destination region and
    selected service level against the regional route master.

    Feasible vehicle types are based on the approved route combinations.
    Vehicle capacity and the number of vehicles required will be assessed
    separately in the Fleet Capacity page.
    """,
)


# =========================================================
# SHIPMENT ROUTE SUMMARY
# =========================================================
st.markdown(
    '<div class="section-title">Selected Shipment Route</div>',
    unsafe_allow_html=True,
)

summary_col1, summary_col2, summary_col3 = st.columns(3)

with summary_col1:
    st.markdown("**Origin**")
    st.write(f"{origin_state}, {origin_region}")

with summary_col2:
    st.markdown("**Destination**")
    st.write(f"{destination_state}, {destination_region}")

with summary_col3:
    st.markdown("**Service Level**")
    st.write(service_level)


# =========================================================
# FILTER MATCHING ROUTES
# =========================================================
matching_routes = route_master[
    (
        route_master["Origin Region"]
        .str.casefold()
        == str(origin_region).casefold()
    )
    & (
        route_master["Destination Region"]
        .str.casefold()
        == str(destination_region).casefold()
    )
    & (
        route_master["Service Level"]
        .str.casefold()
        == str(service_level).casefold()
    )
].copy()


if matching_routes.empty:
    st.error(
        "No route combination was found for the selected "
        "origin region, destination region and service level."
    )

    st.info(
        "Review the route master or return to Page 1 and select "
        "a different route or service level."
    )

    st.stop()


# =========================================================
# MATCH VEHICLE AVAILABILITY
# =========================================================
route_vehicle_types = (
    matching_routes["Vehicle Type"]
    .dropna()
    .unique()
    .tolist()
)

available_vehicle_records = vehicle_master[
    vehicle_master["Vehicle Type"].isin(route_vehicle_types)
].copy()


def region_is_available(
    availability_value: str,
    selected_region: str,
) -> bool:
    """
    Check whether the vehicle's region-availability field
    supports the selected route.

    Supports values such as:
    - All
    - Nationwide
    - Peninsular
    - Northern
    - Central
    - Sabah
    - Sarawak
    - Northern, Central
    """

    value = str(availability_value).strip().casefold()
    region = str(selected_region).strip().casefold()

    if value in {
        "all",
        "nationwide",
        "malaysia",
    }:
        return True

    if value == "peninsular":
        return region in {
            "northern",
            "central",
            "southern",
            "east coast",
        }

    availability_regions = [
        item.strip().casefold()
        for item in str(availability_value).split(",")
    ]

    return region in availability_regions


if "Region Availability" in available_vehicle_records.columns:
    available_vehicle_records = available_vehicle_records[
        available_vehicle_records[
            "Region Availability"
        ].apply(
            lambda value: region_is_available(
                value,
                origin_region,
            )
        )
    ]


available_vehicle_types = (
    available_vehicle_records["Vehicle Type"]
    .dropna()
    .unique()
    .tolist()
)


# If no matching vehicle inventory was found, retain
# the approved route vehicle types from region_routes.csv.
if not available_vehicle_types:
    available_vehicle_types = route_vehicle_types


# =========================================================
# ROUTE CLASSIFICATION
# =========================================================
def classify_route(
    origin: str,
    destination: str,
) -> str:
    """Classify the route into a management-friendly category."""

    peninsular_regions = {
        "Northern",
        "Central",
        "Southern",
        "East Coast",
    }

    if origin == destination:
        return "Intra-Region"

    if (
        origin in peninsular_regions
        and destination in peninsular_regions
    ):
        return "Inter-Region Peninsular"

    if {
        origin,
        destination,
    }.issubset({"Sabah", "Sarawak"}):
        return "East Malaysia Inter-Region"

    if (
        origin in peninsular_regions
        and destination in {"Sabah", "Sarawak"}
    ) or (
        destination in peninsular_regions
        and origin in {"Sabah", "Sarawak"}
    ):
        return "Peninsular–East Malaysia"

    return "Other Route"


route_category = classify_route(
    origin_region,
    destination_region,
)


# =========================================================
# ROUTE DETAILS
# =========================================================
st.markdown(
    '<div class="section-title">Route Details</div>',
    unsafe_allow_html=True,
)

route_col1, route_col2 = st.columns(2)

route_ids = matching_routes["Route ID"].unique().tolist()

with route_col1:
    selected_route_id = st.selectbox(
        "Route ID",
        options=route_ids,
        key="selected_route_id",
        help=(
            "The route ID is retrieved from the regional "
            "route master."
        ),
    )

with route_col2:
    st.text_input(
        "Route Category",
        value=route_category,
        disabled=True,
    )


selected_route_records = matching_routes[
    matching_routes["Route ID"] == selected_route_id
].copy()


target_delivery_options = (
    selected_route_records["Target Delivery (Days)"]
    .dropna()
    .unique()
    .tolist()
)

priority_options = (
    selected_route_records["Priority"]
    .dropna()
    .unique()
    .tolist()
)

target_delivery = (
    target_delivery_options[0]
    if target_delivery_options
    else "Not Available"
)

route_priority = (
    priority_options[0]
    if priority_options
    else "Not Available"
)


detail_col1, detail_col2, detail_col3 = st.columns(3)

with detail_col1:
    st.metric(
        "Target Delivery",
        target_delivery,
    )

with detail_col2:
    st.metric(
        "Route Priority",
        route_priority,
    )

with detail_col3:
    st.metric(
        "Feasible Vehicle Types",
        len(available_vehicle_types),
    )


# =========================================================
# FEASIBLE TRANSPORT MODES
# =========================================================
st.markdown(
    '<div class="section-title">Feasible Transport Modes</div>',
    unsafe_allow_html=True,
)

if not available_vehicle_types:
    st.warning(
        "No feasible vehicle type is available for this route."
    )
    st.stop()


selected_vehicle_type = st.selectbox(
    "Preferred Vehicle Type",
    options=available_vehicle_types,
    key="route_preferred_vehicle",
    help=(
        "This is a preliminary route preference only. "
        "The final vehicle recommendation will be determined "
        "on the Fleet Capacity page."
    ),
)


selected_vehicle_data = available_vehicle_records[
    available_vehicle_records["Vehicle Type"]
    == selected_vehicle_type
].copy()


if not selected_vehicle_data.empty:
    vehicle_summary = (
        selected_vehicle_data.groupby(
            "Vehicle Type",
            as_index=False,
        )
        .agg(
            Active_Vehicles=("Vehicle ID", "nunique"),
            Maximum_Weight_kg=(
                "Max Weight (kg)",
                "max",
            ),
            Maximum_Volume_m3=(
                "Max Volume (m³)",
                "max",
            ),
            Maximum_Parcels=(
                "Max Parcels",
                "max",
            ),
            Average_Speed_kmh=(
                "Avg Speed (km/h)",
                "mean",
            ),
        )
    )

    vehicle_row = vehicle_summary.iloc[0]

    vehicle_col1, vehicle_col2, vehicle_col3, vehicle_col4 = (
        st.columns(4)
    )

    with vehicle_col1:
        st.metric(
            "Active Vehicles",
            f'{int(vehicle_row["Active_Vehicles"]):,}',
        )

    with vehicle_col2:
        st.metric(
            "Maximum Weight",
            f'{vehicle_row["Maximum_Weight_kg"]:,.0f} kg',
        )

    with vehicle_col3:
        st.metric(
            "Maximum Volume",
            f'{vehicle_row["Maximum_Volume_m3"]:,.2f} m³',
        )

    with vehicle_col4:
        st.metric(
            "Maximum Parcels",
            f'{vehicle_row["Maximum_Parcels"]:,.0f}',
        )

    average_speed = float(
        vehicle_row["Average_Speed_kmh"]
    )

else:
    average_speed = 0.0

    st.info(
        "Vehicle specifications were not found in the vehicle "
        "master. The route can still be saved, but capacity "
        "details should be reviewed."
    )


# =========================================================
# JOURNEY ASSUMPTIONS
# =========================================================
st.markdown(
    '<div class="section-title">Journey Assumptions</div>',
    unsafe_allow_html=True,
)

journey_col1, journey_col2, journey_col3 = st.columns(3)

with journey_col1:
    estimated_distance_km = st.number_input(
        "Estimated One-Way Distance (km)",
        min_value=0.0,
        value=0.0,
        step=10.0,
        key="estimated_distance_km",
        help=(
            "Enter the estimated road distance between the "
            "origin and destination."
        ),
    )

with journey_col2:
    return_trip_required = st.selectbox(
        "Return Trip Required",
        options=["Yes", "No"],
        key="return_trip_required",
    )

with journey_col3:
    loading_unloading_hours = st.number_input(
        "Loading and Unloading Time (Hours)",
        min_value=0.0,
        value=1.0,
        step=0.5,
        key="loading_unloading_hours",
    )


distance_multiplier = (
    2
    if return_trip_required == "Yes"
    else 1
)

total_trip_distance_km = (
    estimated_distance_km * distance_multiplier
)


if average_speed > 0:
    estimated_driving_hours = (
        total_trip_distance_km / average_speed
    )
else:
    estimated_driving_hours = 0.0


estimated_total_journey_hours = (
    estimated_driving_hours
    + loading_unloading_hours
)


journey_summary_col1, journey_summary_col2, journey_summary_col3 = (
    st.columns(3)
)

with journey_summary_col1:
    st.metric(
        "Total Trip Distance",
        f"{total_trip_distance_km:,.1f} km",
    )

with journey_summary_col2:
    st.metric(
        "Estimated Driving Time",
        f"{estimated_driving_hours:,.2f} hours",
    )

with journey_summary_col3:
    st.metric(
        "Total Journey Time",
        f"{estimated_total_journey_hours:,.2f} hours",
    )


st.caption(
    "Travel time is a planning estimate based on average vehicle "
    "speed and does not include traffic congestion, rest stops, "
    "ferry schedules, flight schedules or weather disruption."
)


# =========================================================
# ROUTE MATCH TABLE
# =========================================================
with st.expander(
    "View Matching Route Options",
    expanded=False,
):
    display_routes = matching_routes[
        [
            "Route ID",
            "Origin Region",
            "Destination Region",
            "Vehicle Type",
            "Service Level",
            "Target Delivery (Days)",
            "Priority",
        ]
    ].copy()

    st.dataframe(
        display_routes,
        hide_index=True,
        use_container_width=True,
    )


# =========================================================
# VALIDATION
# =========================================================
validation_errors = []

if not selected_route_id:
    validation_errors.append(
        "Select a route ID."
    )

if not selected_vehicle_type:
    validation_errors.append(
        "Select a preferred vehicle type."
    )

if estimated_distance_km <= 0:
    validation_errors.append(
        "Enter an estimated one-way distance greater than zero."
    )


# =========================================================
# SAVE ROUTE INTELLIGENCE
# =========================================================
st.markdown("<br>", unsafe_allow_html=True)

button_col1, button_col2, button_col3 = st.columns(
    [1, 1, 2]
)

with button_col1:
    save_route = st.button(
        "💾 Save Route",
        type="primary",
        use_container_width=True,
    )

with button_col2:
    clear_route = st.button(
        "🗑️ Clear",
        use_container_width=True,
    )


if save_route:
    if validation_errors:
        for error in validation_errors:
            st.warning(error)

    else:
        st.session_state.route_intelligence = {
            "route_id": selected_route_id,
            "origin_region": origin_region,
            "origin_state": origin_state,
            "destination_region": destination_region,
            "destination_state": destination_state,
            "route_category": route_category,
            "service_level": service_level,
            "target_delivery": target_delivery,
            "priority": route_priority,
            "feasible_vehicle_types": available_vehicle_types,
            "preferred_vehicle_type": selected_vehicle_type,
            "estimated_one_way_distance_km": float(
                estimated_distance_km
            ),
            "return_trip_required": return_trip_required,
            "distance_multiplier": int(
                distance_multiplier
            ),
            "total_trip_distance_km": float(
                total_trip_distance_km
            ),
            "average_speed_kmh": float(
                average_speed
            ),
            "estimated_driving_hours": float(
                estimated_driving_hours
            ),
            "loading_unloading_hours": float(
                loading_unloading_hours
            ),
            "estimated_total_journey_hours": float(
                estimated_total_journey_hours
            ),
        }

        st.success(
            "Route intelligence has been saved successfully."
        )


if clear_route:
    st.session_state.route_intelligence = {}

    route_keys = [
        "selected_route_id",
        "route_preferred_vehicle",
        "estimated_distance_km",
        "return_trip_required",
        "loading_unloading_hours",
    ]

    for key in route_keys:
        st.session_state.pop(key, None)

    st.rerun()


# =========================================================
# NEXT PAGE
# =========================================================
if st.session_state.get("route_intelligence"):
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button(
        "Continue to Parcel Assessment ➡",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/3_Parcel_Assessment.py"
        )