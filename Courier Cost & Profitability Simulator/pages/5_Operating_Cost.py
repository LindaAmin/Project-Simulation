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

FUEL_FILE = DATA_DIR / "fuel_rates.csv"
TOLL_FILE = DATA_DIR / "toll_rates.csv"
MAINTENANCE_FILE = DATA_DIR / "maintenance_rates.csv"
TYRE_FILE = DATA_DIR / "tyre_rates.csv"
MANPOWER_FILE = DATA_DIR / "manpower_rates.csv"
FINANCING_FILE = DATA_DIR / "vehicle_financing.csv"
OVERHEAD_FILE = DATA_DIR / "overhead_rates.csv"


# =========================================================
# GENERAL CLEANING FUNCTIONS
# =========================================================
def clean_numeric(series: pd.Series) -> pd.Series:
    """
    Convert values such as RM1,500, 1,500 and RM0.15
    into numeric values.
    """

    return pd.to_numeric(
        series.astype(str)
        .str.replace("RM", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.strip(),
        errors="coerce",
    )


def clean_text_columns(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Trim spaces from all text columns."""

    dataframe = dataframe.copy()

    for column in dataframe.select_dtypes(
        include="object"
    ).columns:
        dataframe[column] = (
            dataframe[column]
            .astype(str)
            .str.strip()
        )

    return dataframe


# =========================================================
# DATA LOADING FUNCTIONS
# =========================================================
@st.cache_data
def load_fuel_rates() -> pd.DataFrame:
    fuel_df = pd.read_csv(FUEL_FILE)

    fuel_df = fuel_df.drop(
        columns=[
            column
            for column in fuel_df.columns
            if str(column).startswith("Unnamed")
        ],
        errors="ignore",
    )

    fuel_df = clean_text_columns(fuel_df)

    fuel_df["Current Rate (RM)"] = clean_numeric(
        fuel_df["Current Rate (RM)"]
    )

    fuel_df = fuel_df.dropna(
        subset=[
            "Fuel Type",
            "Current Rate (RM)",
        ]
    )

    return fuel_df.reset_index(drop=True)


@st.cache_data
def load_toll_rates() -> pd.DataFrame:
    toll_df = pd.read_csv(TOLL_FILE)
    toll_df = clean_text_columns(toll_df)

    toll_df["Toll/km"] = clean_numeric(
        toll_df["Toll/km"]
    )

    toll_df = toll_df.dropna(
        subset=[
            "Vehicle Type",
            "Toll/km",
        ]
    )

    return toll_df.reset_index(drop=True)


@st.cache_data
def load_maintenance_rates() -> pd.DataFrame:
    maintenance_df = pd.read_csv(
        MAINTENANCE_FILE
    )

    maintenance_df = clean_text_columns(
        maintenance_df
    )

    maintenance_df["Service Interval (km)"] = clean_numeric(
        maintenance_df["Service Interval (km)"]
    )

    maintenance_df["Service Cost (RM)"] = clean_numeric(
        maintenance_df["Service Cost (RM)"]
    )

    maintenance_df = maintenance_df.dropna(
        subset=[
            "Vehicle Type",
            "Service Interval (km)",
            "Service Cost (RM)",
        ]
    )

    return maintenance_df.reset_index(
        drop=True
    )


@st.cache_data
def load_tyre_rates() -> pd.DataFrame:
    tyre_df = pd.read_csv(TYRE_FILE)
    tyre_df = clean_text_columns(tyre_df)

    tyre_df["Tyre Change Interval (km)"] = clean_numeric(
        tyre_df["Tyre Change Interval (km)"]
    )

    tyre_df["Tyre Cost (RM)"] = clean_numeric(
        tyre_df["Tyre Cost (RM)"]
    )

    tyre_df = tyre_df.dropna(
        subset=[
            "Vehicle Type",
            "Tyre Change Interval (km)",
            "Tyre Cost (RM)",
        ]
    )

    return tyre_df.reset_index(drop=True)


@st.cache_data
def load_manpower_rates() -> pd.DataFrame:
    manpower_df = pd.read_csv(
        MANPOWER_FILE
    )

    manpower_df = clean_text_columns(
        manpower_df
    )

    numeric_columns = [
        "Monthly Salary (RM)",
        "EPF %",
        "SOCSO (RM)",
        "EIS (RM)",
        "Other Cost (RM)",
        "OT / Hr",
    ]

    for column in numeric_columns:
        manpower_df[column] = clean_numeric(
            manpower_df[column]
        )

    manpower_df = manpower_df.dropna(
        subset=[
            "Position",
            "Monthly Salary (RM)",
        ]
    )

    return manpower_df.reset_index(
        drop=True
    )


@st.cache_data
def load_financing_rates() -> pd.DataFrame:
    financing_df = pd.read_csv(
        FINANCING_FILE
    )

    financing_df = clean_text_columns(
        financing_df
    )

    numeric_columns = [
        "Estimated Vehicle Price (RM)",
        "Down Payment (%)",
        "Loan/Lease Period (Years)",
        "Monthly Instalment (RM)",
        "Insurance - Year 1 (RM)",
        "Insurance - Year 2 (RM)",
        "Insurance - Year 3 (RM)",
        "Insurance - Year 4 (RM)",
        "Insurance - Year 5 (RM)",
    ]

    for column in numeric_columns:
        financing_df[column] = clean_numeric(
            financing_df[column]
        )

    financing_df = financing_df.dropna(
        subset=[
            "Vehicle Type",
            "Financing Type",
            "Monthly Instalment (RM)",
        ]
    )

    return financing_df.reset_index(
        drop=True
    )


@st.cache_data
def load_overhead_rates() -> pd.DataFrame:
    overhead_df = pd.read_csv(
        OVERHEAD_FILE
    )

    overhead_df = overhead_df.drop(
        columns=[
            column
            for column in overhead_df.columns
            if str(column).startswith("Unnamed")
        ],
        errors="ignore",
    )

    overhead_df = clean_text_columns(
        overhead_df
    )

    # Correct spelling in the uploaded master.
    overhead_df.columns = [
        str(column).replace(
            "Sourthern",
            "Southern",
        )
        for column in overhead_df.columns
    ]

    for column in overhead_df.columns:
        if (
            "Suggested Monthly Cost"
            in column
        ):
            overhead_df[column] = clean_numeric(
                overhead_df[column]
            )

    overhead_df = overhead_df.dropna(
        subset=["Cost Item"]
    )

    return overhead_df.reset_index(
        drop=True
    )


# =========================================================
# LOAD MASTER DATA
# =========================================================
try:
    fuel_master = load_fuel_rates()
    toll_master = load_toll_rates()
    maintenance_master = (
        load_maintenance_rates()
    )
    tyre_master = load_tyre_rates()
    manpower_master = load_manpower_rates()
    financing_master = (
        load_financing_rates()
    )
    overhead_master = load_overhead_rates()

except FileNotFoundError as error:
    st.error(
        "A required operating-cost master file "
        f"was not found: {error.filename}"
    )
    st.stop()

except Exception as error:
    st.error(
        "Unable to load the operating-cost "
        f"master data: {error}"
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

fleet = st.session_state.get(
    "fleet_capacity",
    {},
)


required_pages = {
    "Shipment Information": shipment,
    "Route Intelligence": route,
    "Parcel Assessment": parcel,
    "Fleet Capacity": fleet,
}

incomplete_pages = [
    page_name
    for page_name, page_data
    in required_pages.items()
    if not page_data
]

if incomplete_pages:
    st.warning(
        "Complete and save the following pages before "
        "calculating operating costs: "
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

parcel_quantity = int(
    parcel.get(
        "parcel_quantity",
        0,
    )
)

vehicle_type = fleet.get(
    "selected_vehicle_type",
    "",
)

fuel_type = fleet.get(
    "fuel_type",
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

total_trip_distance_km = float(
    route.get(
        "total_trip_distance_km",
        0,
    )
)

estimated_journey_hours = float(
    route.get(
        "estimated_total_journey_hours",
        0,
    )
)


# =========================================================
# VALIDATION
# =========================================================
required_values = {
    "Vehicle type": vehicle_type,
    "Planned fleet size": planned_fleet_size,
    "Total trip distance": total_trip_distance_km,
    "Parcel quantity": parcel_quantity,
}

invalid_values = []

for field_name, field_value in required_values.items():
    if field_value is None:
        invalid_values.append(field_name)

    elif isinstance(field_value, str):
        if not field_value.strip():
            invalid_values.append(field_name)

    elif float(field_value) <= 0:
        invalid_values.append(field_name)


if invalid_values:
    st.error(
        "The following operating-cost inputs are "
        "missing or invalid: "
        + ", ".join(invalid_values)
    )
    st.stop()


# =========================================================
# SESSION STATE
# =========================================================
if "operating_cost" not in st.session_state:
    st.session_state.operating_cost = {}


# =========================================================
# PAGE TITLE
# =========================================================
st.markdown(
    '<div class="main-title">💰 Operating Cost</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-subtitle">
        Calculate direct trip costs and allocated fixed costs
        for the selected vehicle fleet.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# COST BASIS
# =========================================================
cost_basis(
    "Operating Cost Basis",
    """
    Direct operating costs include fuel, toll, maintenance,
    tyres and overtime incurred for the shipment.

    Fixed monthly costs include manpower, vehicle financing,
    insurance and regional overheads. These costs are allocated
    to the shipment based on the assumed number of shipments
    completed each month.

    Fuel efficiency and monthly shipment volume are planning
    assumptions because they are not currently available in the
    uploaded master data.
    """,
)


# =========================================================
# OPERATIONAL SUMMARY
# =========================================================
st.markdown(
    '<div class="section-title">Operational Summary</div>',
    unsafe_allow_html=True,
)

summary_col1, summary_col2, summary_col3, summary_col4 = (
    st.columns(4)
)

with summary_col1:
    st.metric(
        "Selected Vehicle",
        vehicle_type,
    )

with summary_col2:
    st.metric(
        "Planned Fleet Size",
        f"{planned_fleet_size:,}",
    )

with summary_col3:
    st.metric(
        "Total Trip Distance",
        f"{total_trip_distance_km:,.1f} km",
    )

with summary_col4:
    st.metric(
        "Shipment Parcels",
        f"{parcel_quantity:,}",
    )


# =========================================================
# DEFAULT FUEL EFFICIENCY
# =========================================================
default_fuel_efficiency = {
    "Motorcycle": 35.0,
    "Van": 10.0,
    "1-Ton Lorry": 7.0,
    "3-Ton Lorry": 5.0,
}

fuel_efficiency_default = (
    default_fuel_efficiency.get(
        vehicle_type,
        8.0,
    )
)


# =========================================================
# OPERATING ASSUMPTIONS
# =========================================================
st.markdown(
    '<div class="section-title">Operating Assumptions</div>',
    unsafe_allow_html=True,
)

assumption_col1, assumption_col2, assumption_col3 = (
    st.columns(3)
)

with assumption_col1:
    fuel_efficiency_km_per_litre = (
        st.number_input(
            "Fuel Efficiency (km/litre)",
            min_value=0.10,
            value=float(
                fuel_efficiency_default
            ),
            step=0.50,
            key="cost_fuel_efficiency",
            help=(
                "Editable planning assumption because "
                "fuel efficiency is not included in the "
                "current vehicle master."
            ),
        )
    )

with assumption_col2:
    shipments_per_month = st.number_input(
        "Shipments per Month",
        min_value=1,
        value=26,
        step=1,
        key="cost_shipments_per_month",
        help=(
            "Used to allocate monthly financing, "
            "insurance, manpower and overhead costs "
            "to one shipment."
        ),
    )

with assumption_col3:
    insurance_year = st.selectbox(
        "Vehicle Insurance Year",
        options=[1, 2, 3, 4, 5],
        index=0,
        key="cost_insurance_year",
    )


# =========================================================
# FUEL RATE MATCHING
# =========================================================
def standardise_fuel_type(
    selected_fuel_type: str,
) -> str:
    """
    Match vehicle-master fuel descriptions to
    fuel-rate master descriptions.
    """

    fuel_name = (
        str(selected_fuel_type)
        .strip()
        .casefold()
    )

    if "petrol" in fuel_name:
        return "Petrol RON95"

    if "diesel" in fuel_name:
        return "Diesel"

    return selected_fuel_type


matched_fuel_type = standardise_fuel_type(
    fuel_type
)

fuel_record = fuel_master[
    fuel_master["Fuel Type"]
    .str.casefold()
    .eq(
        str(matched_fuel_type)
        .casefold()
    )
]


if fuel_record.empty:
    st.error(
        f"No fuel rate was found for {fuel_type}."
    )
    st.stop()


fuel_rate_rm_per_litre = float(
    fuel_record.iloc[0][
        "Current Rate (RM)"
    ]
)


# =========================================================
# FUEL COST
# =========================================================
fuel_litres_per_vehicle = (
    total_trip_distance_km
    / fuel_efficiency_km_per_litre
)

total_fuel_litres = (
    fuel_litres_per_vehicle
    * planned_fleet_size
)

fuel_cost_per_shipment = (
    total_fuel_litres
    * fuel_rate_rm_per_litre
)


# =========================================================
# TOLL COST
# =========================================================
def toll_region_from_route(
    origin: str,
    destination: str,
) -> str:
    """
    Determine the applicable toll-rate region.
    """

    peninsular_regions = {
        "Northern",
        "Central",
        "Southern",
        "East Coast",
    }

    if (
        origin in peninsular_regions
        and destination in peninsular_regions
    ):
        return "Peninsular"

    if origin == "Sabah":
        return "Sabah"

    if origin == "Sarawak":
        return "Sarawak"

    return origin


toll_region = toll_region_from_route(
    origin_region,
    destination_region,
)

toll_record = toll_master[
    (
        toll_master["Vehicle Type"]
        .str.casefold()
        .eq(vehicle_type.casefold())
    )
    & (
        toll_master["Region Availability"]
        .str.casefold()
        .eq(toll_region.casefold())
    )
]


if toll_record.empty:
    toll_rate_rm_per_km = 0.0
    route_type = "Not Available"

else:
    toll_rate_rm_per_km = float(
        toll_record.iloc[0]["Toll/km"]
    )

    route_type = toll_record.iloc[0][
        "Route Type"
    ]


toll_cost_per_shipment = (
    toll_rate_rm_per_km
    * total_trip_distance_km
    * planned_fleet_size
)


# =========================================================
# MAINTENANCE COST
# =========================================================
maintenance_record = maintenance_master[
    maintenance_master["Vehicle Type"]
    .str.casefold()
    .eq(vehicle_type.casefold())
]


if maintenance_record.empty:
    st.error(
        f"No maintenance rate was found for "
        f"{vehicle_type}."
    )
    st.stop()


service_interval_km = float(
    maintenance_record.iloc[0][
        "Service Interval (km)"
    ]
)

service_cost_rm = float(
    maintenance_record.iloc[0][
        "Service Cost (RM)"
    ]
)

maintenance_cost_per_km = (
    service_cost_rm
    / service_interval_km
)

maintenance_cost_per_shipment = (
    maintenance_cost_per_km
    * total_trip_distance_km
    * planned_fleet_size
)


# =========================================================
# TYRE COST
# =========================================================
tyre_record = tyre_master[
    tyre_master["Vehicle Type"]
    .str.casefold()
    .eq(vehicle_type.casefold())
]


if tyre_record.empty:
    st.error(
        f"No tyre rate was found for "
        f"{vehicle_type}."
    )
    st.stop()


tyre_interval_km = float(
    tyre_record.iloc[0][
        "Tyre Change Interval (km)"
    ]
)

tyre_cost_rm = float(
    tyre_record.iloc[0][
        "Tyre Cost (RM)"
    ]
)

tyre_cost_per_km = (
    tyre_cost_rm
    / tyre_interval_km
)

tyre_cost_per_shipment = (
    tyre_cost_per_km
    * total_trip_distance_km
    * planned_fleet_size
)


# =========================================================
# MANPOWER POSITION MATCHING
# =========================================================
driver_position_map = {
    "Motorcycle": "Rider",
    "Van": "Van Driver",
    "1-Ton Lorry": "Lorry Driver",
    "3-Ton Lorry": "Lorry Driver",
}

driver_position = driver_position_map.get(
    vehicle_type,
    "Lorry Driver",
)

driver_record = manpower_master[
    manpower_master["Position"]
    .str.casefold()
    .eq(driver_position.casefold())
]


if driver_record.empty:
    st.error(
        f"No manpower rate was found for "
        f"{driver_position}."
    )
    st.stop()


driver_data = driver_record.iloc[0]

monthly_salary_rm = float(
    driver_data["Monthly Salary (RM)"]
)

epf_rate_pct = float(
    driver_data["EPF %"]
)

socso_rm = float(
    driver_data["SOCSO (RM)"]
)

eis_rm = float(
    driver_data["EIS (RM)"]
)

other_manpower_cost_rm = float(
    driver_data["Other Cost (RM)"]
)

overtime_rate_rm = float(
    driver_data["OT / Hr"]
)


# =========================================================
# DRIVER MONTHLY COST
# =========================================================
monthly_epf_rm = (
    monthly_salary_rm
    * epf_rate_pct
    / 100
)

monthly_driver_cost_per_person = (
    monthly_salary_rm
    + monthly_epf_rm
    + socso_rm
    + eis_rm
    + other_manpower_cost_rm
)

monthly_driver_cost = (
    monthly_driver_cost_per_person
    * planned_fleet_size
)


# =========================================================
# OVERTIME
# =========================================================
st.markdown(
    '<div class="section-title">Manpower Assumptions</div>',
    unsafe_allow_html=True,
)

manpower_col1, manpower_col2, manpower_col3 = (
    st.columns(3)
)

with manpower_col1:
    normal_hours_per_shipment = st.number_input(
        "Normal Working Hours per Shipment",
        min_value=0.0,
        value=8.0,
        step=0.5,
        key="cost_normal_hours",
    )

with manpower_col2:
    calculated_overtime_hours = max(
        estimated_journey_hours
        - normal_hours_per_shipment,
        0,
    )

    overtime_hours_per_driver = st.number_input(
        "Overtime Hours per Driver",
        min_value=0.0,
        value=float(
            round(
                calculated_overtime_hours,
                2,
            )
        ),
        step=0.5,
        key="cost_overtime_hours",
    )

with manpower_col3:
    include_operations_executive = (
        st.checkbox(
            "Include Operations Executive",
            value=True,
            key="cost_include_operations_executive",
        )
    )


overtime_cost_per_shipment = (
    overtime_hours_per_driver
    * overtime_rate_rm
    * planned_fleet_size
)


# =========================================================
# OPERATIONS EXECUTIVE
# =========================================================
operations_executive_monthly_cost = 0.0

if include_operations_executive:
    executive_record = manpower_master[
        manpower_master["Position"]
        .str.casefold()
        .eq("operations executive")
    ]

    if not executive_record.empty:
        executive_data = executive_record.iloc[0]

        executive_salary = float(
            executive_data[
                "Monthly Salary (RM)"
            ]
        )

        executive_epf = (
            executive_salary
            * float(
                executive_data["EPF %"]
            )
            / 100
        )

        operations_executive_monthly_cost = (
            executive_salary
            + executive_epf
            + float(
                executive_data["SOCSO (RM)"]
            )
            + float(
                executive_data["EIS (RM)"]
            )
            + float(
                executive_data["Other Cost (RM)"]
            )
        )


total_monthly_manpower_cost = (
    monthly_driver_cost
    + operations_executive_monthly_cost
)

allocated_manpower_per_shipment = (
    total_monthly_manpower_cost
    / shipments_per_month
)


# =========================================================
# VEHICLE FINANCING
# =========================================================
st.markdown(
    '<div class="section-title">Vehicle Financing</div>',
    unsafe_allow_html=True,
)

available_financing = financing_master[
    financing_master["Vehicle Type"]
    .str.casefold()
    .eq(vehicle_type.casefold())
].copy()


if available_financing.empty:
    st.error(
        f"No financing information was found for "
        f"{vehicle_type}."
    )
    st.stop()


financing_options = (
    available_financing["Financing Type"]
    .drop_duplicates()
    .tolist()
)

financing_col1, financing_col2 = (
    st.columns(2)
)

with financing_col1:
    financing_type = st.selectbox(
        "Financing Type",
        options=financing_options,
        key="cost_financing_type",
    )

with financing_col2:
    include_financing_cost = st.checkbox(
        "Include Financing and Insurance",
        value=True,
        key="cost_include_financing",
    )


selected_financing = available_financing[
    available_financing["Financing Type"]
    .str.casefold()
    .eq(financing_type.casefold())
].iloc[0]


monthly_instalment_per_vehicle = float(
    selected_financing[
        "Monthly Instalment (RM)"
    ]
)

monthly_financing_cost = (
    monthly_instalment_per_vehicle
    * planned_fleet_size
)


insurance_column = (
    f"Insurance - Year {insurance_year} (RM)"
)

annual_insurance_per_vehicle = (
    selected_financing.get(
        insurance_column,
        0,
    )
)

if pd.isna(annual_insurance_per_vehicle):
    annual_insurance_per_vehicle = 0.0

annual_insurance_per_vehicle = float(
    annual_insurance_per_vehicle
)

monthly_insurance_cost = (
    annual_insurance_per_vehicle
    / 12
    * planned_fleet_size
)


if not include_financing_cost:
    monthly_financing_cost = 0.0
    monthly_insurance_cost = 0.0


allocated_financing_per_shipment = (
    monthly_financing_cost
    / shipments_per_month
)

allocated_insurance_per_shipment = (
    monthly_insurance_cost
    / shipments_per_month
)


# =========================================================
# REGIONAL OVERHEAD
# =========================================================
region_column = (
    "Suggested Monthly Cost (RM) - "
    f"{origin_region}"
)


if region_column not in overhead_master.columns:
    st.error(
        "No overhead column was found for the "
        f"{origin_region} region."
    )
    st.stop()


excluded_overhead_items = {
    "Warehouse Size (sqft)",
    "Rental Rate (sqft)",
}

allocated_overhead_records = (
    overhead_master[
        ~overhead_master["Cost Item"].isin(
            excluded_overhead_items
        )
    ]
    .copy()
)


allocated_overhead_records[
    region_column
] = pd.to_numeric(
    allocated_overhead_records[
        region_column
    ],
    errors="coerce",
).fillna(0)


monthly_regional_overhead = float(
    allocated_overhead_records[
        region_column
    ].sum()
)

allocated_overhead_per_shipment = (
    monthly_regional_overhead
    / shipments_per_month
)


# =========================================================
# COST TOTALS
# =========================================================
direct_trip_cost = (
    fuel_cost_per_shipment
    + toll_cost_per_shipment
    + maintenance_cost_per_shipment
    + tyre_cost_per_shipment
    + overtime_cost_per_shipment
)

allocated_fixed_cost_per_shipment = (
    allocated_manpower_per_shipment
    + allocated_financing_per_shipment
    + allocated_insurance_per_shipment
    + allocated_overhead_per_shipment
)

total_operating_cost_per_shipment = (
    direct_trip_cost
    + allocated_fixed_cost_per_shipment
)

monthly_direct_operating_cost = (
    direct_trip_cost
    * shipments_per_month
)

total_monthly_fixed_cost = (
    total_monthly_manpower_cost
    + monthly_financing_cost
    + monthly_insurance_cost
    + monthly_regional_overhead
)

total_monthly_operating_cost = (
    monthly_direct_operating_cost
    + total_monthly_fixed_cost
)


# =========================================================
# DIRECT COST RESULTS
# =========================================================
st.markdown(
    '<div class="section-title">Direct Shipment Cost</div>',
    unsafe_allow_html=True,
)

direct_col1, direct_col2, direct_col3 = (
    st.columns(3)
)

with direct_col1:
    st.metric(
        "Fuel Cost",
        f"RM {fuel_cost_per_shipment:,.2f}",
    )

with direct_col2:
    st.metric(
        "Toll Cost",
        f"RM {toll_cost_per_shipment:,.2f}",
    )

with direct_col3:
    st.metric(
        "Maintenance Cost",
        f"RM {maintenance_cost_per_shipment:,.2f}",
    )


direct_col4, direct_col5, direct_col6 = (
    st.columns(3)
)

with direct_col4:
    st.metric(
        "Tyre Cost",
        f"RM {tyre_cost_per_shipment:,.2f}",
    )

with direct_col5:
    st.metric(
        "Overtime Cost",
        f"RM {overtime_cost_per_shipment:,.2f}",
    )

with direct_col6:
    st.metric(
        "Total Direct Cost",
        f"RM {direct_trip_cost:,.2f}",
    )


# =========================================================
# FIXED COST RESULTS
# =========================================================
st.markdown(
    '<div class="section-title">Allocated Fixed Cost per Shipment</div>',
    unsafe_allow_html=True,
)

fixed_col1, fixed_col2 = st.columns(2)

with fixed_col1:
    st.metric(
        "Allocated Manpower",
        f"RM {allocated_manpower_per_shipment:,.2f}",
    )

with fixed_col2:
    st.metric(
        "Allocated Vehicle Financing",
        f"RM {allocated_financing_per_shipment:,.2f}",
    )


fixed_col3, fixed_col4 = st.columns(2)

with fixed_col3:
    st.metric(
        "Allocated Insurance",
        f"RM {allocated_insurance_per_shipment:,.2f}",
    )

with fixed_col4:
    st.metric(
        "Allocated Regional Overhead",
        f"RM {allocated_overhead_per_shipment:,.2f}",
    )


# =========================================================
# TOTAL OPERATING COST
# =========================================================
st.markdown(
    '<div class="section-title">Operating Cost Summary</div>',
    unsafe_allow_html=True,
)

total_col1, total_col2, total_col3 = (
    st.columns(3)
)

with total_col1:
    st.metric(
        "Direct Cost per Shipment",
        f"RM {direct_trip_cost:,.2f}",
    )

with total_col2:
    st.metric(
        "Fixed Cost per Shipment",
        f"RM {allocated_fixed_cost_per_shipment:,.2f}",
    )

with total_col3:
    st.metric(
        "Total Operating Cost",
        f"RM {total_operating_cost_per_shipment:,.2f}",
    )


monthly_col1, monthly_col2, monthly_col3 = (
    st.columns(3)
)

with monthly_col1:
    st.metric(
        "Monthly Direct Cost",
        f"RM {monthly_direct_operating_cost:,.2f}",
    )

with monthly_col2:
    st.metric(
        "Monthly Fixed Cost",
        f"RM {total_monthly_fixed_cost:,.2f}",
    )

with monthly_col3:
    st.metric(
        "Total Monthly Cost",
        f"RM {total_monthly_operating_cost:,.2f}",
    )


# =========================================================
# COST BREAKDOWN TABLE
# =========================================================
cost_breakdown = pd.DataFrame(
    [
        {
            "Cost Category": "Direct Cost",
            "Cost Item": "Fuel",
            "Cost per Shipment (RM)": (
                fuel_cost_per_shipment
            ),
        },
        {
            "Cost Category": "Direct Cost",
            "Cost Item": "Toll",
            "Cost per Shipment (RM)": (
                toll_cost_per_shipment
            ),
        },
        {
            "Cost Category": "Direct Cost",
            "Cost Item": "Maintenance",
            "Cost per Shipment (RM)": (
                maintenance_cost_per_shipment
            ),
        },
        {
            "Cost Category": "Direct Cost",
            "Cost Item": "Tyres",
            "Cost per Shipment (RM)": (
                tyre_cost_per_shipment
            ),
        },
        {
            "Cost Category": "Direct Cost",
            "Cost Item": "Overtime",
            "Cost per Shipment (RM)": (
                overtime_cost_per_shipment
            ),
        },
        {
            "Cost Category": "Fixed Cost",
            "Cost Item": "Manpower",
            "Cost per Shipment (RM)": (
                allocated_manpower_per_shipment
            ),
        },
        {
            "Cost Category": "Fixed Cost",
            "Cost Item": "Vehicle Financing",
            "Cost per Shipment (RM)": (
                allocated_financing_per_shipment
            ),
        },
        {
            "Cost Category": "Fixed Cost",
            "Cost Item": "Vehicle Insurance",
            "Cost per Shipment (RM)": (
                allocated_insurance_per_shipment
            ),
        },
        {
            "Cost Category": "Fixed Cost",
            "Cost Item": "Regional Overhead",
            "Cost per Shipment (RM)": (
                allocated_overhead_per_shipment
            ),
        },
    ]
)

cost_breakdown[
    "Share of Total (%)"
] = (
    cost_breakdown[
        "Cost per Shipment (RM)"
    ]
    / total_operating_cost_per_shipment
    * 100
    if total_operating_cost_per_shipment > 0
    else 0
)


with st.expander(
    "View Detailed Cost Breakdown",
    expanded=False,
):
    formatted_breakdown = cost_breakdown.copy()

    formatted_breakdown[
        "Cost per Shipment (RM)"
    ] = formatted_breakdown[
        "Cost per Shipment (RM)"
    ].map(
        lambda value: f"{value:,.2f}"
    )

    formatted_breakdown[
        "Share of Total (%)"
    ] = formatted_breakdown[
        "Share of Total (%)"
    ].map(
        lambda value: f"{value:,.1f}%"
    )

    st.dataframe(
        formatted_breakdown,
        hide_index=True,
        use_container_width=True,
    )


# =========================================================
# CALCULATION BASIS
# =========================================================
with st.expander(
    "View Cost Calculation Basis",
    expanded=False,
):
    calculation_basis = pd.DataFrame(
        {
            "Assumption": [
                "Fuel type",
                "Fuel rate",
                "Fuel efficiency",
                "Fuel litres used",
                "Toll region",
                "Route type",
                "Toll rate",
                "Maintenance cost per kilometre",
                "Tyre cost per kilometre",
                "Driver position",
                "Monthly driver cost per person",
                "Overtime rate",
                "Financing type",
                "Monthly instalment per vehicle",
                "Insurance year",
                "Annual insurance per vehicle",
                "Shipments per month",
                "Monthly regional overhead",
            ],
            "Value": [
                matched_fuel_type,
                f"RM {fuel_rate_rm_per_litre:,.2f}/litre",
                (
                    f"{fuel_efficiency_km_per_litre:,.2f} "
                    "km/litre"
                ),
                f"{total_fuel_litres:,.2f} litres",
                toll_region,
                route_type,
                f"RM {toll_rate_rm_per_km:,.2f}/km",
                f"RM {maintenance_cost_per_km:,.4f}/km",
                f"RM {tyre_cost_per_km:,.4f}/km",
                driver_position,
                (
                    f"RM "
                    f"{monthly_driver_cost_per_person:,.2f}"
                ),
                f"RM {overtime_rate_rm:,.2f}/hour",
                financing_type,
                (
                    f"RM "
                    f"{monthly_instalment_per_vehicle:,.2f}"
                ),
                f"Year {insurance_year}",
                (
                    f"RM "
                    f"{annual_insurance_per_vehicle:,.2f}"
                ),
                f"{shipments_per_month:,}",
                f"RM {monthly_regional_overhead:,.2f}",
            ],
        }
    )

    st.dataframe(
        calculation_basis,
        hide_index=True,
        use_container_width=True,
    )


# =========================================================
# OVERHEAD DETAILS
# =========================================================
with st.expander(
    "View Regional Overhead Details",
    expanded=False,
):
    overhead_display = allocated_overhead_records[
        [
            "Cost Item",
            region_column,
            "Allocation Method",
        ]
    ].copy()

    overhead_display = overhead_display.rename(
        columns={
            region_column: (
                "Monthly Cost (RM)"
            )
        }
    )

    overhead_display[
        "Monthly Cost (RM)"
    ] = overhead_display[
        "Monthly Cost (RM)"
    ].map(
        lambda value: f"{value:,.2f}"
    )

    st.dataframe(
        overhead_display,
        hide_index=True,
        use_container_width=True,
    )


# =========================================================
# SAVE OPERATING COST
# =========================================================
st.markdown(
    "<br>",
    unsafe_allow_html=True,
)

button_col1, button_col2, button_col3 = (
    st.columns([1, 1, 2])
)

with button_col1:
    save_operating_cost = st.button(
        "💾 Save Operating Cost",
        type="primary",
        use_container_width=True,
    )

with button_col2:
    clear_operating_cost = st.button(
        "🗑️ Clear",
        use_container_width=True,
    )


if save_operating_cost:
    st.session_state.operating_cost = {
        "origin_region": origin_region,
        "origin_state": origin_state,
        "destination_region": (
            destination_region
        ),
        "destination_state": (
            destination_state
        ),
        "service_level": service_level,

        "vehicle_type": vehicle_type,
        "fuel_type": matched_fuel_type,
        "planned_fleet_size": int(
            planned_fleet_size
        ),
        "total_trip_distance_km": float(
            total_trip_distance_km
        ),
        "estimated_journey_hours": float(
            estimated_journey_hours
        ),
        "parcel_quantity": int(
            parcel_quantity
        ),

        "fuel_efficiency_km_per_litre": float(
            fuel_efficiency_km_per_litre
        ),
        "fuel_rate_rm_per_litre": float(
            fuel_rate_rm_per_litre
        ),
        "fuel_litres_per_vehicle": float(
            fuel_litres_per_vehicle
        ),
        "total_fuel_litres": float(
            total_fuel_litres
        ),
        "fuel_cost_per_shipment": float(
            fuel_cost_per_shipment
        ),

        "toll_region": toll_region,
        "route_type": route_type,
        "toll_rate_rm_per_km": float(
            toll_rate_rm_per_km
        ),
        "toll_cost_per_shipment": float(
            toll_cost_per_shipment
        ),

        "service_interval_km": float(
            service_interval_km
        ),
        "service_cost_rm": float(
            service_cost_rm
        ),
        "maintenance_cost_per_km": float(
            maintenance_cost_per_km
        ),
        "maintenance_cost_per_shipment": float(
            maintenance_cost_per_shipment
        ),

        "tyre_interval_km": float(
            tyre_interval_km
        ),
        "tyre_cost_rm": float(
            tyre_cost_rm
        ),
        "tyre_cost_per_km": float(
            tyre_cost_per_km
        ),
        "tyre_cost_per_shipment": float(
            tyre_cost_per_shipment
        ),

        "driver_position": driver_position,
        "driver_monthly_cost_per_person": float(
            monthly_driver_cost_per_person
        ),
        "total_monthly_driver_cost": float(
            monthly_driver_cost
        ),
        "include_operations_executive": bool(
            include_operations_executive
        ),
        "operations_executive_monthly_cost": float(
            operations_executive_monthly_cost
        ),
        "total_monthly_manpower_cost": float(
            total_monthly_manpower_cost
        ),
        "overtime_hours_per_driver": float(
            overtime_hours_per_driver
        ),
        "overtime_rate_rm": float(
            overtime_rate_rm
        ),
        "overtime_cost_per_shipment": float(
            overtime_cost_per_shipment
        ),
        "allocated_manpower_per_shipment": float(
            allocated_manpower_per_shipment
        ),

        "financing_type": financing_type,
        "include_financing_cost": bool(
            include_financing_cost
        ),
        "monthly_instalment_per_vehicle": float(
            monthly_instalment_per_vehicle
        ),
        "monthly_financing_cost": float(
            monthly_financing_cost
        ),
        "insurance_year": int(
            insurance_year
        ),
        "annual_insurance_per_vehicle": float(
            annual_insurance_per_vehicle
        ),
        "monthly_insurance_cost": float(
            monthly_insurance_cost
        ),
        "allocated_financing_per_shipment": float(
            allocated_financing_per_shipment
        ),
        "allocated_insurance_per_shipment": float(
            allocated_insurance_per_shipment
        ),

        "shipments_per_month": int(
            shipments_per_month
        ),
        "monthly_regional_overhead": float(
            monthly_regional_overhead
        ),
        "allocated_overhead_per_shipment": float(
            allocated_overhead_per_shipment
        ),

        "direct_trip_cost": float(
            direct_trip_cost
        ),
        "allocated_fixed_cost_per_shipment": float(
            allocated_fixed_cost_per_shipment
        ),
        "total_operating_cost_per_shipment": float(
            total_operating_cost_per_shipment
        ),

        "monthly_direct_operating_cost": float(
            monthly_direct_operating_cost
        ),
        "total_monthly_fixed_cost": float(
            total_monthly_fixed_cost
        ),
        "total_monthly_operating_cost": float(
            total_monthly_operating_cost
        ),

        "cost_breakdown": (
            cost_breakdown.to_dict(
                orient="records"
            )
        ),
    }

    st.success(
        "Operating-cost assessment has been "
        "saved successfully."
    )


if clear_operating_cost:
    st.session_state.operating_cost = {}

    keys_to_clear = [
        "cost_fuel_efficiency",
        "cost_shipments_per_month",
        "cost_insurance_year",
        "cost_normal_hours",
        "cost_overtime_hours",
        "cost_include_operations_executive",
        "cost_financing_type",
        "cost_include_financing",
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
    "operating_cost"
):
    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )

    if st.button(
        "Continue to Cost per Parcel ➡",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/6_Cost_Per_Parcel.py"
        )