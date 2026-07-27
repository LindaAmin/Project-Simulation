from pathlib import Path
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
# FILE PATH
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

VEHICLE_FILE = DATA_DIR / "vehicle_master.csv"


# =========================================================
# DATA LOADING FUNCTION
# =========================================================
@st.cache_data
def load_vehicle_master() -> pd.DataFrame:
    """
    Load and clean active vehicle master data.
    """

    vehicle_df = pd.read_csv(VEHICLE_FILE)

    required_columns = [
        "Vehicle ID",
        "Vehicle Type",
        "Category",
        "Fuel Type",
        "Max Weight (kg)",
        "Max Volume (m³)",
        "Max Parcels",
        "Avg Speed (km/h)",
        "State",
        "Region Availability",
        "Average Parcel Per Item",
        "Status",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in vehicle_df.columns
    ]

    if missing_columns:
        raise ValueError(
            "The vehicle master is missing these columns: "
            + ", ".join(missing_columns)
        )

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
        vehicle_df[column] = pd.to_numeric(
            vehicle_df[column],
            errors="coerce",
        )

    vehicle_df = vehicle_df[
        vehicle_df["Status"]
        .str.casefold()
        .eq("active")
    ].copy()

    vehicle_df = vehicle_df.dropna(
        subset=[
            "Vehicle ID",
            "Vehicle Type",
            "Max Weight (kg)",
            "Max Volume (m³)",
            "Max Parcels",
        ]
    )

    return vehicle_df.reset_index(drop=True)


# =========================================================
# LOAD VEHICLE MASTER
# =========================================================
try:
    vehicle_master = load_vehicle_master()

except FileNotFoundError:
    st.error(
        "The vehicle master file was not found. Ensure that "
        "'vehicle_master.csv' is stored in the data folder."
    )
    st.stop()

except ValueError as error:
    st.error(str(error))
    st.stop()

except Exception as error:
    st.error(
        f"Unable to load vehicle master data: {error}"
    )
    st.stop()


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


if not shipment:
    st.warning(
        "Shipment information has not been saved. "
        "Complete Page 1 before proceeding."
    )

    if st.button("⬅ Go to Shipment Information"):
        st.switch_page(
            "pages/1_Shipment_Information.py"
        )

    st.stop()


if not route:
    st.warning(
        "Route intelligence has not been saved. "
        "Complete Page 2 before proceeding."
    )

    if st.button("⬅ Go to Route Intelligence"):
        st.switch_page(
            "pages/2_Route_Intelligence.py"
        )

    st.stop()


if not parcel:
    st.warning(
        "Parcel assessment has not been saved. "
        "Complete Page 3 before proceeding."
    )

    if st.button("⬅ Go to Parcel Assessment"):
        st.switch_page(
            "pages/3_Parcel_Assessment.py"
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

feasible_vehicle_types = route.get(
    "feasible_vehicle_types",
    [],
)

preferred_vehicle_type = route.get(
    "preferred_vehicle_type",
    "",
)

parcel_quantity = int(
    parcel.get(
        "capacity_quantity_basis",
        parcel.get("parcel_quantity", 0),
    )
)

total_actual_weight_kg = float(
    parcel.get(
        "capacity_weight_basis_kg",
        parcel.get("total_actual_weight_kg", 0),
    )
)

total_volume_m3 = float(
    parcel.get(
        "capacity_volume_basis_m3",
        parcel.get("total_volume_m3", 0),
    )
)

chargeable_weight_kg = float(
    parcel.get(
        "chargeable_weight_kg",
        0,
    )
)


# =========================================================
# VALIDATE CAPACITY INPUTS
# =========================================================
capacity_inputs = {
    "Parcel quantity": parcel_quantity,
    "Total actual weight": total_actual_weight_kg,
    "Total shipment volume": total_volume_m3,
}

invalid_inputs = [
    name
    for name, value in capacity_inputs.items()
    if value is None or float(value) <= 0
]

if invalid_inputs:
    st.error(
        "The following parcel capacity inputs are invalid: "
        + ", ".join(invalid_inputs)
    )

    st.info(
        "Return to Page 3 and review the parcel assessment."
    )

    st.stop()


# =========================================================
# SESSION STATE
# =========================================================
if "fleet_capacity" not in st.session_state:
    st.session_state.fleet_capacity = {}


# =========================================================
# PAGE TITLE
# =========================================================
st.markdown(
    '<div class="main-title">🚚 Fleet Capacity</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-subtitle">
        Determine the appropriate vehicle type, required fleet size
        and controlling capacity constraint.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# CAPACITY BASIS
# =========================================================
cost_basis(
    "Fleet Capacity Basis",
    """
    The required number of vehicles is assessed independently against
    parcel quantity, actual shipment weight and total shipment volume.

    The final fleet requirement is the highest result across the three
    capacity constraints. This ensures that the selected fleet can carry
    the complete shipment without exceeding vehicle capacity.
    """,
)


# =========================================================
# SHIPMENT REQUIREMENT SUMMARY
# =========================================================
st.markdown(
    '<div class="section-title">Shipment Capacity Requirement</div>',
    unsafe_allow_html=True,
)

summary_col1, summary_col2, summary_col3, summary_col4 = (
    st.columns(4)
)

with summary_col1:
    st.metric(
        "Parcel Quantity",
        f"{parcel_quantity:,}",
    )

with summary_col2:
    st.metric(
        "Actual Weight",
        f"{total_actual_weight_kg:,.2f} kg",
    )

with summary_col3:
    st.metric(
        "Shipment Volume",
        f"{total_volume_m3:,.3f} m³",
    )

with summary_col4:
    st.metric(
        "Chargeable Weight",
        f"{chargeable_weight_kg:,.2f} kg",
    )


# =========================================================
# REGION AVAILABILITY FUNCTION
# =========================================================
def is_vehicle_available_for_region(
    availability_value: str,
    selected_region: str,
) -> bool:
    """
    Determine whether a vehicle availability category supports
    the selected operational region.
    """

    availability = (
        str(availability_value)
        .strip()
        .casefold()
    )

    region = (
        str(selected_region)
        .strip()
        .casefold()
    )

    universal_values = {
        "all",
        "nationwide",
        "malaysia",
    }

    if availability in universal_values:
        return True

    if availability == "peninsular":
        return region in {
            "northern",
            "central",
            "southern",
            "east coast",
        }

    availability_items = [
        item.strip().casefold()
        for item in str(availability_value).split(",")
    ]

    return region in availability_items


# =========================================================
# FILTER FEASIBLE VEHICLES
# =========================================================
available_vehicles = vehicle_master.copy()

if feasible_vehicle_types:
    available_vehicles = available_vehicles[
        available_vehicles["Vehicle Type"].isin(
            feasible_vehicle_types
        )
    ].copy()


available_vehicles = available_vehicles[
    available_vehicles["Region Availability"].apply(
        lambda value: is_vehicle_available_for_region(
            value,
            origin_region,
        )
    )
].copy()


if available_vehicles.empty:
    st.error(
        "No active vehicle records are available for the selected "
        "route and origin region."
    )

    st.info(
        "Review the vehicle master, regional availability or "
        "route vehicle options."
    )

    st.stop()


# =========================================================
# CREATE VEHICLE-TYPE CAPACITY SUMMARY
# =========================================================
vehicle_type_summary = (
    available_vehicles.groupby(
        "Vehicle Type",
        as_index=False,
    )
    .agg(
        Active_Vehicles=(
            "Vehicle ID",
            "nunique",
        ),
        Category=(
            "Category",
            "first",
        ),
        Fuel_Type=(
            "Fuel Type",
            "first",
        ),
        Max_Weight_kg=(
            "Max Weight (kg)",
            "max",
        ),
        Max_Volume_m3=(
            "Max Volume (m³)",
            "max",
        ),
        Max_Parcels=(
            "Max Parcels",
            "max",
        ),
        Average_Speed_kmh=(
            "Avg Speed (km/h)",
            "mean",
        ),
        Average_Parcel_Per_Item=(
            "Average Parcel Per Item",
            "mean",
        ),
    )
)


# =========================================================
# VEHICLE REQUIREMENT CALCULATION
# =========================================================
def calculate_vehicle_requirement(
    vehicle_row: pd.Series,
) -> dict:
    """
    Calculate required vehicles by quantity, weight and volume.
    """

    max_parcels = float(
        vehicle_row["Max_Parcels"]
    )

    max_weight_kg = float(
        vehicle_row["Max_Weight_kg"]
    )

    max_volume_m3 = float(
        vehicle_row["Max_Volume_m3"]
    )

    if (
        max_parcels <= 0
        or max_weight_kg <= 0
        or max_volume_m3 <= 0
    ):
        return {
            "Vehicles by Parcel": None,
            "Vehicles by Weight": None,
            "Vehicles by Volume": None,
            "Required Vehicles": None,
            "Capacity Constraint": (
                "Invalid Vehicle Capacity"
            ),
        }

    vehicles_by_parcel = math.ceil(
        parcel_quantity / max_parcels
    )

    vehicles_by_weight = math.ceil(
        total_actual_weight_kg / max_weight_kg
    )

    vehicles_by_volume = math.ceil(
        total_volume_m3 / max_volume_m3
    )

    required_vehicles = max(
        vehicles_by_parcel,
        vehicles_by_weight,
        vehicles_by_volume,
    )

    constraints = {
        "Parcel Quantity": vehicles_by_parcel,
        "Actual Weight": vehicles_by_weight,
        "Shipment Volume": vehicles_by_volume,
    }

    maximum_requirement = max(
        constraints.values()
    )

    controlling_constraints = [
        name
        for name, value in constraints.items()
        if value == maximum_requirement
    ]

    capacity_constraint = " and ".join(
        controlling_constraints
    )

    return {
        "Vehicles by Parcel": vehicles_by_parcel,
        "Vehicles by Weight": vehicles_by_weight,
        "Vehicles by Volume": vehicles_by_volume,
        "Required Vehicles": required_vehicles,
        "Capacity Constraint": capacity_constraint,
    }


requirement_records = []

for _, vehicle_row in vehicle_type_summary.iterrows():
    calculation = calculate_vehicle_requirement(
        vehicle_row
    )

    required_vehicles = calculation[
        "Required Vehicles"
    ]

    active_vehicles = int(
        vehicle_row["Active_Vehicles"]
    )

    if required_vehicles is None:
        fleet_shortfall = None
        availability_status = "Invalid Capacity"

    else:
        fleet_shortfall = max(
            required_vehicles - active_vehicles,
            0,
        )

        availability_status = (
            "Sufficient Fleet"
            if active_vehicles >= required_vehicles
            else "Fleet Shortfall"
        )

    requirement_records.append(
        {
            "Vehicle Type": vehicle_row[
                "Vehicle Type"
            ],
            "Category": vehicle_row[
                "Category"
            ],
            "Fuel Type": vehicle_row[
                "Fuel_Type"
            ],
            "Active Vehicles": active_vehicles,
            "Max Weight per Vehicle (kg)": float(
                vehicle_row["Max_Weight_kg"]
            ),
            "Max Volume per Vehicle (m³)": float(
                vehicle_row["Max_Volume_m3"]
            ),
            "Max Parcels per Vehicle": int(
                vehicle_row["Max_Parcels"]
            ),
            "Vehicles by Parcel": calculation[
                "Vehicles by Parcel"
            ],
            "Vehicles by Weight": calculation[
                "Vehicles by Weight"
            ],
            "Vehicles by Volume": calculation[
                "Vehicles by Volume"
            ],
            "Required Vehicles": required_vehicles,
            "Capacity Constraint": calculation[
                "Capacity Constraint"
            ],
            "Fleet Shortfall": fleet_shortfall,
            "Availability Status": availability_status,
            "Average Speed (km/h)": float(
                vehicle_row["Average_Speed_kmh"]
            ),
        }
    )


capacity_comparison = pd.DataFrame(
    requirement_records
)

capacity_comparison = capacity_comparison[
    capacity_comparison["Required Vehicles"].notna()
].copy()


if capacity_comparison.empty:
    st.error(
        "The available vehicle records do not contain valid "
        "capacity values."
    )
    st.stop()


# =========================================================
# RECOMMEND VEHICLE TYPE
# =========================================================
sufficient_options = capacity_comparison[
    capacity_comparison["Availability Status"]
    == "Sufficient Fleet"
].copy()


if not sufficient_options.empty:
    recommendation_pool = sufficient_options

else:
    recommendation_pool = capacity_comparison


recommendation_pool = recommendation_pool.sort_values(
    by=[
        "Required Vehicles",
        "Fleet Shortfall",
        "Max Weight per Vehicle (kg)",
    ],
    ascending=[
        True,
        True,
        True,
    ],
)


recommended_vehicle_type = (
    recommendation_pool.iloc[0]["Vehicle Type"]
)


# Prefer the preliminary Page 2 vehicle when it remains feasible
if (
    preferred_vehicle_type
    and preferred_vehicle_type
    in capacity_comparison["Vehicle Type"].tolist()
):
    default_vehicle_type = preferred_vehicle_type

else:
    default_vehicle_type = recommended_vehicle_type


vehicle_type_options = (
    capacity_comparison["Vehicle Type"]
    .drop_duplicates()
    .tolist()
)

default_vehicle_index = vehicle_type_options.index(
    default_vehicle_type
)


# =========================================================
# VEHICLE SELECTION
# =========================================================
st.markdown(
    '<div class="section-title">Vehicle Capacity Selection</div>',
    unsafe_allow_html=True,
)

selection_col1, selection_col2 = st.columns(
    [2, 1]
)

with selection_col1:
    selected_vehicle_type = st.selectbox(
        "Selected Vehicle Type",
        options=vehicle_type_options,
        index=default_vehicle_index,
        key="fleet_selected_vehicle_type",
        help=(
            "The system recommends the vehicle type requiring "
            "the smallest feasible fleet. You may select another "
            "approved vehicle type for comparison."
        ),
    )

with selection_col2:
    st.markdown("**System Recommendation**")
    st.success(recommended_vehicle_type)


selected_capacity = capacity_comparison[
    capacity_comparison["Vehicle Type"]
    == selected_vehicle_type
].iloc[0]


# =========================================================
# SELECTED VEHICLE CAPACITY
# =========================================================
st.markdown(
    '<div class="section-title">Selected Vehicle Capacity</div>',
    unsafe_allow_html=True,
)

capacity_col1, capacity_col2, capacity_col3, capacity_col4 = (
    st.columns(4)
)

with capacity_col1:
    st.metric(
        "Maximum Parcels",
        f'{int(selected_capacity["Max Parcels per Vehicle"]):,}',
    )

with capacity_col2:
    st.metric(
        "Maximum Weight",
        (
            f'{selected_capacity["Max Weight per Vehicle (kg)"]:,.0f} kg'
        ),
    )

with capacity_col3:
    st.metric(
        "Maximum Volume",
        (
            f'{selected_capacity["Max Volume per Vehicle (m³)"]:,.2f} m³'
        ),
    )

with capacity_col4:
    st.metric(
        "Active Fleet",
        f'{int(selected_capacity["Active Vehicles"]):,}',
    )


# =========================================================
# REQUIRED FLEET CALCULATION
# =========================================================
st.markdown(
    '<div class="section-title">Required Fleet Assessment</div>',
    unsafe_allow_html=True,
)

required_by_parcel = int(
    selected_capacity["Vehicles by Parcel"]
)

required_by_weight = int(
    selected_capacity["Vehicles by Weight"]
)

required_by_volume = int(
    selected_capacity["Vehicles by Volume"]
)

required_vehicles = int(
    selected_capacity["Required Vehicles"]
)

capacity_constraint = selected_capacity[
    "Capacity Constraint"
]

active_vehicle_count = int(
    selected_capacity["Active Vehicles"]
)

fleet_shortfall = int(
    selected_capacity["Fleet Shortfall"]
)

availability_status = selected_capacity[
    "Availability Status"
]


requirement_col1, requirement_col2, requirement_col3, requirement_col4 = (
    st.columns(4)
)

with requirement_col1:
    st.metric(
        "Vehicles by Parcel",
        required_by_parcel,
    )

with requirement_col2:
    st.metric(
        "Vehicles by Weight",
        required_by_weight,
    )

with requirement_col3:
    st.metric(
        "Vehicles by Volume",
        required_by_volume,
    )

with requirement_col4:
    st.metric(
        "Required Fleet",
        required_vehicles,
    )


# =========================================================
# UTILISATION CALCULATIONS
# =========================================================
total_parcel_capacity = (
    required_vehicles
    * int(
        selected_capacity[
            "Max Parcels per Vehicle"
        ]
    )
)

total_weight_capacity_kg = (
    required_vehicles
    * float(
        selected_capacity[
            "Max Weight per Vehicle (kg)"
        ]
    )
)

total_volume_capacity_m3 = (
    required_vehicles
    * float(
        selected_capacity[
            "Max Volume per Vehicle (m³)"
        ]
    )
)


parcel_utilisation_pct = (
    parcel_quantity
    / total_parcel_capacity
    * 100
    if total_parcel_capacity > 0
    else 0
)

weight_utilisation_pct = (
    total_actual_weight_kg
    / total_weight_capacity_kg
    * 100
    if total_weight_capacity_kg > 0
    else 0
)

volume_utilisation_pct = (
    total_volume_m3
    / total_volume_capacity_m3
    * 100
    if total_volume_capacity_m3 > 0
    else 0
)

overall_utilisation_pct = max(
    parcel_utilisation_pct,
    weight_utilisation_pct,
    volume_utilisation_pct,
)


st.markdown(
    '<div class="section-title">Fleet Utilisation</div>',
    unsafe_allow_html=True,
)

utilisation_col1, utilisation_col2, utilisation_col3, utilisation_col4 = (
    st.columns(4)
)

with utilisation_col1:
    st.metric(
        "Parcel Utilisation",
        f"{parcel_utilisation_pct:,.1f}%",
    )

with utilisation_col2:
    st.metric(
        "Weight Utilisation",
        f"{weight_utilisation_pct:,.1f}%",
    )

with utilisation_col3:
    st.metric(
        "Volume Utilisation",
        f"{volume_utilisation_pct:,.1f}%",
    )

with utilisation_col4:
    st.metric(
        "Maximum Utilisation",
        f"{overall_utilisation_pct:,.1f}%",
    )


# =========================================================
# ASSESSMENT INTERPRETATION
# =========================================================
st.markdown(
    '<div class="section-title">Fleet Assessment Interpretation</div>',
    unsafe_allow_html=True,
)

interpretation_col1, interpretation_col2 = st.columns(2)

with interpretation_col1:
    st.markdown("**Controlling Capacity Constraint**")
    st.info(
        f"{capacity_constraint} determines the required fleet "
        f"size of {required_vehicles:,} "
        f"{selected_vehicle_type} vehicle(s)."
    )

with interpretation_col2:
    st.markdown("**Fleet Availability**")

    if availability_status == "Sufficient Fleet":
        st.success(
            f"{active_vehicle_count:,} active vehicle(s) are "
            f"available. The fleet requirement can be fulfilled."
        )

    else:
        st.error(
            f"A shortfall of {fleet_shortfall:,} vehicle(s) exists. "
            f"Only {active_vehicle_count:,} active vehicle(s) are "
            f"currently available."
        )


if selected_vehicle_type == recommended_vehicle_type:
    st.success(
        "The selected vehicle type matches the system recommendation."
    )

else:
    st.warning(
        f"The system-recommended vehicle type is "
        f"{recommended_vehicle_type}. The selected "
        f"{selected_vehicle_type} may require a larger fleet or "
        f"have lower utilisation."
    )


# =========================================================
# FLEET CONFIGURATION
# =========================================================
st.markdown(
    '<div class="section-title">Fleet Configuration</div>',
    unsafe_allow_html=True,
)

configuration_col1, configuration_col2, configuration_col3 = (
    st.columns(3)
)

with configuration_col1:
    operational_buffer_pct = st.number_input(
        "Operational Buffer (%)",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=5.0,
        key="fleet_operational_buffer_pct",
        help=(
            "Optional additional fleet allowance for breakdowns, "
            "peak volume or operational uncertainty."
        ),
    )

with configuration_col2:
    additional_buffer_vehicles = math.ceil(
        required_vehicles
        * operational_buffer_pct
        / 100
    )

    st.metric(
        "Additional Buffer Vehicles",
        additional_buffer_vehicles,
    )

with configuration_col3:
    planned_fleet_size = (
        required_vehicles
        + additional_buffer_vehicles
    )

    st.metric(
        "Planned Fleet Size",
        planned_fleet_size,
    )


planned_fleet_shortfall = max(
    planned_fleet_size - active_vehicle_count,
    0,
)


if planned_fleet_shortfall > 0:
    st.warning(
        f"The planned fleet, including the operational buffer, "
        f"exceeds the current active fleet by "
        f"{planned_fleet_shortfall:,} vehicle(s)."
    )


# =========================================================
# AVAILABLE VEHICLE ALLOCATION
# =========================================================
selected_vehicle_records = available_vehicles[
    available_vehicles["Vehicle Type"]
    == selected_vehicle_type
].copy()

selected_vehicle_records = selected_vehicle_records.sort_values(
    by=[
        "State",
        "Vehicle ID",
    ]
)

allocated_vehicle_ids = (
    selected_vehicle_records["Vehicle ID"]
    .head(
        min(
            planned_fleet_size,
            len(selected_vehicle_records),
        )
    )
    .tolist()
)


with st.expander(
    "View Proposed Vehicle Allocation",
    expanded=False,
):
    allocation_columns = [
        "Vehicle ID",
        "Vehicle Type",
        "Category",
        "Fuel Type",
        "State",
        "Region Availability",
        "Max Weight (kg)",
        "Max Volume (m³)",
        "Max Parcels",
        "Avg Speed (km/h)",
    ]

    allocation_df = selected_vehicle_records[
        selected_vehicle_records["Vehicle ID"].isin(
            allocated_vehicle_ids
        )
    ][allocation_columns].copy()

    st.dataframe(
        allocation_df,
        hide_index=True,
        use_container_width=True,
    )


# =========================================================
# VEHICLE COMPARISON TABLE
# =========================================================
with st.expander(
    "Compare All Feasible Vehicle Types",
    expanded=False,
):
    comparison_display = capacity_comparison[
        [
            "Vehicle Type",
            "Active Vehicles",
            "Max Weight per Vehicle (kg)",
            "Max Volume per Vehicle (m³)",
            "Max Parcels per Vehicle",
            "Vehicles by Parcel",
            "Vehicles by Weight",
            "Vehicles by Volume",
            "Required Vehicles",
            "Capacity Constraint",
            "Fleet Shortfall",
            "Availability Status",
        ]
    ].copy()

    comparison_display = comparison_display.sort_values(
        by=[
            "Required Vehicles",
            "Fleet Shortfall",
        ],
        ascending=[
            True,
            True,
        ],
    )

    st.dataframe(
        comparison_display,
        hide_index=True,
        use_container_width=True,
    )


# =========================================================
# SAVE FLEET CAPACITY
# =========================================================
st.markdown("<br>", unsafe_allow_html=True)

button_col1, button_col2, button_col3 = st.columns(
    [1, 1, 2]
)

with button_col1:
    save_fleet = st.button(
        "💾 Save Fleet Capacity",
        type="primary",
        use_container_width=True,
    )

with button_col2:
    clear_fleet = st.button(
        "🗑️ Clear",
        use_container_width=True,
    )


if save_fleet:
    st.session_state.fleet_capacity = {
        "route_id": route_id,
        "route_category": route_category,
        "origin_region": origin_region,
        "origin_state": origin_state,
        "destination_region": destination_region,
        "destination_state": destination_state,
        "service_level": service_level,

        "recommended_vehicle_type": (
            recommended_vehicle_type
        ),
        "selected_vehicle_type": (
            selected_vehicle_type
        ),
        "vehicle_category": selected_capacity[
            "Category"
        ],
        "fuel_type": selected_capacity[
            "Fuel Type"
        ],

        "active_vehicle_count": int(
            active_vehicle_count
        ),
        "max_parcels_per_vehicle": int(
            selected_capacity[
                "Max Parcels per Vehicle"
            ]
        ),
        "max_weight_per_vehicle_kg": float(
            selected_capacity[
                "Max Weight per Vehicle (kg)"
            ]
        ),
        "max_volume_per_vehicle_m3": float(
            selected_capacity[
                "Max Volume per Vehicle (m³)"
            ]
        ),
        "average_speed_kmh": float(
            selected_capacity[
                "Average Speed (km/h)"
            ]
        ),

        "shipment_parcel_quantity": int(
            parcel_quantity
        ),
        "shipment_actual_weight_kg": float(
            total_actual_weight_kg
        ),
        "shipment_volume_m3": float(
            total_volume_m3
        ),
        "shipment_chargeable_weight_kg": float(
            chargeable_weight_kg
        ),

        "vehicles_by_parcel": int(
            required_by_parcel
        ),
        "vehicles_by_weight": int(
            required_by_weight
        ),
        "vehicles_by_volume": int(
            required_by_volume
        ),
        "required_vehicles": int(
            required_vehicles
        ),
        "capacity_constraint": (
            capacity_constraint
        ),

        "parcel_utilisation_pct": float(
            parcel_utilisation_pct
        ),
        "weight_utilisation_pct": float(
            weight_utilisation_pct
        ),
        "volume_utilisation_pct": float(
            volume_utilisation_pct
        ),
        "overall_utilisation_pct": float(
            overall_utilisation_pct
        ),

        "operational_buffer_pct": float(
            operational_buffer_pct
        ),
        "additional_buffer_vehicles": int(
            additional_buffer_vehicles
        ),
        "planned_fleet_size": int(
            planned_fleet_size
        ),

        "fleet_shortfall": int(
            fleet_shortfall
        ),
        "planned_fleet_shortfall": int(
            planned_fleet_shortfall
        ),
        "availability_status": (
            availability_status
        ),

        "allocated_vehicle_ids": (
            allocated_vehicle_ids
        ),
    }

    st.success(
        "Fleet-capacity assessment has been saved successfully."
    )


if clear_fleet:
    st.session_state.fleet_capacity = {}

    keys_to_clear = [
        "fleet_selected_vehicle_type",
        "fleet_operational_buffer_pct",
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
if st.session_state.get("fleet_capacity"):
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button(
        "Continue to Operating Cost ➡",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/5_Operating_Cost.py"
        )