from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd
import streamlit as st

from utils.components import cost_basis
from utils.data_loader import load_shipment_reference_data
from utils.page_configuration import page_config, page_style


# =========================================================
# PAGE CONFIGURATION
# =========================================================
page_config()
page_style()


# =========================================================
# CONSTANTS
# =========================================================
SHIPMENT_KEY = "shipment_information"
UPLOAD_DATA_KEY = "uploaded_shipment_data"
MANUAL_MODE = "Manual Input"
UPLOAD_MODE = "Upload Shipment File"

REQUIRED_UPLOAD_COLUMNS = [
    "Shipment ID",
    "Shipment Date",
    "Customer",
    "Origin State",
    "Destination State",
    "Service Level",
    "Parcel Type",
    "Weight (kg)",
    "Length (cm)",
    "Width (cm)",
    "Height (cm)",
    "Selling Price (RM)",
]

COLUMN_ALIASES = {
    "shipment id": "Shipment ID",
    "shipment date": "Shipment Date",
    "customer": "Customer",
    "origin state": "Origin State",
    "origin region": "Origin Region",
    "destination state": "Destination State",
    "destination region": "Destination Region",
    "service level": "Service Level",
    "parcel type": "Parcel Type",
    "weight": "Weight (kg)",
    "weight(kg)": "Weight (kg)",
    "weight (kg)": "Weight (kg)",
    "length": "Length (cm)",
    "length (cm)": "Length (cm)",
    "width": "Width (cm)",
    "width (cm)": "Width (cm)",
    "height": "Height (cm)",
    "height (cm)": "Height (cm)",
    "selling price": "Selling Price (RM)",
    "selling price (rm)": "Selling Price (RM)",
}


# =========================================================
# SESSION STATE
# =========================================================
st.session_state.setdefault(SHIPMENT_KEY, {})
st.session_state.setdefault(UPLOAD_DATA_KEY, pd.DataFrame())


# =========================================================
# HELPERS
# =========================================================
@st.cache_data(show_spinner=False)
def get_reference_data() -> dict[str, pd.DataFrame]:
    return load_shipment_reference_data()


def read_uploaded_file(uploaded_file: Any) -> pd.DataFrame:
    file_name = str(uploaded_file.name).lower()

    if file_name.endswith(".csv"):
        dataframe = pd.read_csv(uploaded_file, encoding="utf-8-sig")
    elif file_name.endswith(".xlsx"):
        dataframe = pd.read_excel(uploaded_file)
    else:
        raise ValueError("Only CSV and XLSX files are supported.")

    dataframe.columns = [str(column).strip() for column in dataframe.columns]
    dataframe = dataframe.loc[
        :, ~dataframe.columns.str.lower().str.startswith("unnamed:")
    ]

    rename_map = {
        column: COLUMN_ALIASES[column.strip().lower()]
        for column in dataframe.columns
        if column.strip().lower() in COLUMN_ALIASES
    }

    return dataframe.rename(columns=rename_map)


def to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype("string")
        .str.replace(",", "", regex=False)
        .str.replace("RM", "", regex=False)
        .str.strip(),
        errors="coerce",
    )


def validate_upload(
    dataframe: pd.DataFrame,
    valid_states: set[str],
    valid_services: set[str],
    valid_parcel_types: set[str],
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    missing_columns = [
        column for column in REQUIRED_UPLOAD_COLUMNS if column not in dataframe.columns
    ]

    if missing_columns:
        return (
            dataframe,
            pd.DataFrame(),
            ["Missing required columns: " + ", ".join(missing_columns)],
        )

    cleaned = dataframe.copy()

    text_columns = [
        "Shipment ID",
        "Customer",
        "Origin State",
        "Destination State",
        "Service Level",
        "Parcel Type",
    ]

    for column in text_columns:
        cleaned[column] = cleaned[column].astype("string").str.strip()

    cleaned["Shipment Date"] = pd.to_datetime(
        cleaned["Shipment Date"], errors="coerce", dayfirst=True
    )

    numeric_columns = [
        "Weight (kg)",
        "Length (cm)",
        "Width (cm)",
        "Height (cm)",
        "Selling Price (RM)",
    ]

    for column in numeric_columns:
        cleaned[column] = to_numeric(cleaned[column])

    duplicate_ids = cleaned["Shipment ID"].duplicated(keep=False)
    exceptions: list[dict[str, Any]] = []

    for index, row in cleaned.iterrows():
        row_number = index + 2
        shipment_id = row.get("Shipment ID", "")

        def add_exception(field: str, issue: str, suggested_fix: str) -> None:
            exceptions.append(
                {
                    "Row": row_number,
                    "Shipment ID": shipment_id,
                    "Field": field,
                    "Issue": issue,
                    "Suggested Fix": suggested_fix,
                }
            )

        if pd.isna(shipment_id) or not str(shipment_id).strip():
            add_exception("Shipment ID", "Missing value", "Enter a unique ID.")
        elif bool(duplicate_ids.loc[index]):
            add_exception("Shipment ID", "Duplicate ID", "Use a unique ID.")

        if pd.isna(row["Shipment Date"]):
            add_exception("Shipment Date", "Invalid date", "Use DD/MM/YYYY.")

        if pd.isna(row["Customer"]) or not str(row["Customer"]).strip():
            add_exception("Customer", "Missing value", "Enter a customer name.")

        if row["Origin State"] not in valid_states:
            add_exception(
                "Origin State",
                f'Invalid state: {row["Origin State"]}',
                "Use a state in state_master.csv.",
            )

        if row["Destination State"] not in valid_states:
            add_exception(
                "Destination State",
                f'Invalid state: {row["Destination State"]}',
                "Use a state in state_master.csv.",
            )

        if row["Service Level"] not in valid_services:
            add_exception(
                "Service Level",
                f'Invalid value: {row["Service Level"]}',
                "Use a service level in service_level.csv.",
            )

        if row["Parcel Type"] not in valid_parcel_types:
            add_exception(
                "Parcel Type",
                f'Invalid value: {row["Parcel Type"]}',
                "Use a parcel type in parcel_master.csv.",
            )

        for column in numeric_columns:
            value = row[column]
            if pd.isna(value) or float(value) <= 0:
                add_exception(
                    column,
                    "Value must be greater than zero",
                    "Enter a valid positive number.",
                )

    return cleaned, pd.DataFrame(exceptions), []


def calculate_upload_fields(
    dataframe: pd.DataFrame,
    state_region_map: dict[str, str],
    parcel_divisor_map: dict[str, float],
) -> pd.DataFrame:
    result = dataframe.copy()

    result["Origin Region"] = result["Origin State"].map(state_region_map)
    result["Destination Region"] = result["Destination State"].map(
        state_region_map
    )
    result["Volumetric Divisor"] = (
        result["Parcel Type"].map(parcel_divisor_map).fillna(5000.0)
    )
    result["Volume (m³)"] = (
        result["Length (cm)"]
        * result["Width (cm)"]
        * result["Height (cm)"]
    ) / 1_000_000
    result["Volumetric Weight (kg)"] = (
        result["Length (cm)"]
        * result["Width (cm)"]
        * result["Height (cm)"]
    ) / result["Volumetric Divisor"]
    result["Chargeable Weight (kg)"] = result[
        ["Weight (kg)", "Volumetric Weight (kg)"]
    ].max(axis=1)

    return result


def clear_page() -> None:
    st.session_state[SHIPMENT_KEY] = {}
    st.session_state[UPLOAD_DATA_KEY] = pd.DataFrame()

    for key in [
        "shipment_source",
        "manual_shipment_id",
        "manual_customer",
        "manual_origin_state",
        "manual_destination_state",
        "manual_service_level",
        "manual_shipment_date",
        "manual_delivery_frequency",
        "manual_parcel_type",
        "manual_parcel_quantity",
        "manual_parcel_length",
        "manual_parcel_width",
        "manual_parcel_height",
        "manual_parcel_weight",
        "shipment_upload",
    ]:
        st.session_state.pop(key, None)


# =========================================================
# LOAD MASTER DATA
# =========================================================
try:
    reference_data = get_reference_data()
    state_master_df = reference_data["states"]
    service_level_df = reference_data["service_levels"]
    parcel_master_df = reference_data["parcels"]
except Exception as error:
    st.error("Unable to load the shipment master data.")
    st.exception(error)
    st.stop()

state_options = sorted(state_master_df["State"].dropna().astype(str).unique())
service_options = service_level_df["Service Level"].dropna().astype(str).tolist()
parcel_options = parcel_master_df["Parcel Type"].dropna().astype(str).tolist()

state_region_map = dict(
    zip(state_master_df["State"], state_master_df["Region"])
)
parcel_divisor_map = dict(
    zip(parcel_master_df["Parcel Type"], parcel_master_df["Volumetric Divisor"])
)


# =========================================================
# PAGE HEADER
# =========================================================
st.markdown(
    '<div class="main-title">📦 Shipment Information</div>',
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div class="page-subtitle">
        Enter one shipment manually or upload a CSV/XLSX transaction file.
    </div>
    """,
    unsafe_allow_html=True,
)

cost_basis(
    title="Shipment Information Basis",
    message=(
        "States determine the operational regions. Actual weight and volume "
        "support fleet sizing, while chargeable weight supports pricing."
    ),
    items=[
        "Manual input for a single or aggregate shipment",
        "CSV/XLSX upload for bulk shipment transactions",
        "Regions generated automatically from state_master.csv",
        "Actual weight used as the fleet payload basis",
    ],
)


# =========================================================
# DATA SOURCE
# =========================================================
st.markdown(
    '<div class="section-title">Shipment Data Source</div>',
    unsafe_allow_html=True,
)

shipment_source = st.radio(
    "Select the shipment input method",
    [MANUAL_MODE, UPLOAD_MODE],
    horizontal=True,
    key="shipment_source",
)


# =========================================================
# MANUAL INPUT
# =========================================================
if shipment_source == MANUAL_MODE:

    # -----------------------------------------------------
    # SHIPMENT DETAILS
    # -----------------------------------------------------
    st.markdown(
        '<div class="section-title">Shipment Details</div>',
        unsafe_allow_html=True,
    )

    detail_col1, detail_col2 = st.columns(2)

    with detail_col1:
        shipment_id = st.text_input(
            "Shipment ID",
            value="TEST-0001",
            key="manual_shipment_id",
        )

    with detail_col2:
        customer = st.text_input(
            "Customer",
            value="Dummy Customer",
            key="manual_customer",
        )

    # -----------------------------------------------------
    # ROUTE INFORMATION
    # -----------------------------------------------------
    # -----------------------------------------------------
    # ROUTE INFORMATION
    # -----------------------------------------------------
    st.markdown(
        '<div class="section-title">Route Information</div>',
        unsafe_allow_html=True,
    )

    # Build a clean lookup dictionary
    state_region_map = {
        str(state).strip(): str(region).strip()
        for state, region in zip(
            state_master_df["State"],
            state_master_df["Region"],
        )
    }

    route_col1, route_col2 = st.columns(2)

    # ==========================
    # Origin
    # ==========================
    with route_col1:

        origin_state = st.selectbox(
            "Origin State",
            options=["Select State"] + state_options,
            key="manual_origin_state",
        )

        origin_region = ""

        if origin_state != "Select State":
            origin_region = state_region_map.get(
                origin_state.strip(),
                "Region Not Found",
            )

        st.text_input(
            "Origin Region",
            value=origin_region,
            disabled=True,
        )

    # ==========================
    # Destination
    # ==========================
    with route_col2:

        destination_state = st.selectbox(
            "Destination State",
            options=["Select State"] + state_options,
            key="manual_destination_state",
        )

        destination_region = ""

        if destination_state != "Select State":
            destination_region = state_region_map.get(
                destination_state.strip(),
                "Region Not Found",
            )

        st.text_input(
            "Destination Region",
            value=destination_region,
            disabled=True,
        )

    # Optional validation
    if (
        origin_region == "Region Not Found"
        and origin_state != "Select State"
    ):
        st.error(
            f"No region mapping found for {origin_state}."
        )

    if (
        destination_region == "Region Not Found"
        and destination_state != "Select State"
    ):
        st.error(
            f"No region mapping found for {destination_state}."
        )


    # -----------------------------------------------------
    # DELIVERY REQUIREMENT
    # -----------------------------------------------------
    st.markdown(
        '<div class="section-title">Delivery Requirement</div>',
        unsafe_allow_html=True,
    )

    delivery_col1, delivery_col2, delivery_col3 = st.columns(3)

    with delivery_col1:
        service_level = st.selectbox(
            "Service Level",
            options=[
                "Select Service Level",
                *service_options,
            ],
            key="manual_service_level",
        )

    with delivery_col2:
        shipment_date = st.date_input(
            "Shipment Date",
            value=date.today(),
            key="manual_shipment_date",
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
            key="manual_delivery_frequency",
        )

    selected_service = None

    if service_level != "Select Service Level":
        matched_service = service_level_df.loc[
            service_level_df[
                "Service Level"
            ] == service_level
        ]

        if not matched_service.empty:
            selected_service = matched_service.iloc[0]

            service_col1, service_col2, service_col3 = (
                st.columns(3)
            )

            with service_col1:
                st.metric(
                    "Target Delivery",
                    selected_service[
                        "Target Delivery (Days)"
                    ],
                )

            with service_col2:
                st.metric(
                    "Priority",
                    selected_service[
                        "Priority"
                    ],
                )

            with service_col3:
                st.metric(
                    "Cost Multiplier",
                    (
                        f'{float(selected_service["Cost Multiplier"]):.2f}x'
                    ),
                )

    # -----------------------------------------------------
    # PARCEL INFORMATION
    # -----------------------------------------------------
    st.markdown(
        '<div class="section-title">Parcel Information</div>',
        unsafe_allow_html=True,
    )

    parcel_col1, parcel_col2 = st.columns(2)

    with parcel_col1:
        parcel_type = st.selectbox(
            "Parcel Type",
            options=[
                "Select Parcel Type",
                *parcel_options,
            ],
            key="manual_parcel_type",
        )

    with parcel_col2:
        parcel_quantity = st.number_input(
            "Number of Parcels",
            min_value=1,
            value=1,
            step=1,
            key="manual_parcel_quantity",
        )

    # Default values before a parcel type is selected.
    length_cm = 0.0
    width_cm = 0.0
    height_cm = 0.0
    weight_per_parcel_kg = 0.0

    default_length_cm = 0.0
    default_width_cm = 0.0
    default_height_cm = 0.0

    maximum_weight_kg = None
    volumetric_divisor = 5000.0
    dimension_warning = None

    if parcel_type != "Select Parcel Type":
        matched_parcel = parcel_master_df.loc[
            parcel_master_df[
                "Parcel Type"
            ] == parcel_type
        ]

        if matched_parcel.empty:
            st.error(
                "The selected parcel type was not found "
                "in parcel_master.csv."
            )

        else:
            selected_parcel = matched_parcel.iloc[0]

            default_length_cm = float(
                selected_parcel[
                    "Length (cm)"
                ]
            )

            default_width_cm = float(
                selected_parcel[
                    "Width (cm)"
                ]
            )

            default_height_cm = float(
                selected_parcel[
                    "Height (cm)"
                ]
            )

            maximum_weight_kg = float(
                selected_parcel[
                    "Max Weight (kg)"
                ]
            )

            volumetric_divisor = float(
                selected_parcel[
                    "Volumetric Divisor"
                ]
            )

            st.caption(
                "The parcel master provides suggested dimensions. "
                "You may amend the actual Length × Width × Height."
            )

            dimension_col1, dimension_col2, dimension_col3 = (
                st.columns(3)
            )

            with dimension_col1:
                length_cm = st.number_input(
                    "Length per Parcel (cm)",
                    min_value=0.10,
                    value=default_length_cm,
                    step=1.00,
                    key="manual_parcel_length",
                )

            with dimension_col2:
                width_cm = st.number_input(
                    "Width per Parcel (cm)",
                    min_value=0.10,
                    value=default_width_cm,
                    step=1.00,
                    key="manual_parcel_width",
                )

            with dimension_col3:
                height_cm = st.number_input(
                    "Height per Parcel (cm)",
                    min_value=0.10,
                    value=default_height_cm,
                    step=1.00,
                    key="manual_parcel_height",
                )

            weight_per_parcel_kg = st.number_input(
                "Actual Weight per Parcel (kg)",
                min_value=0.01,
                value=min(
                    1.50,
                    maximum_weight_kg,
                ),
                step=0.10,
                key="manual_parcel_weight",
                help=(
                    f"Recommended maximum weight for a "
                    f"{parcel_type} parcel is "
                    f"{maximum_weight_kg:,.2f} kg."
                ),
            )

            if (
                length_cm > default_length_cm
                or width_cm > default_width_cm
                or height_cm > default_height_cm
            ):
                dimension_warning = (
                    "The entered dimensions exceed the standard "
                    f"{parcel_type} dimensions of "
                    f"{default_length_cm:g} × "
                    f"{default_width_cm:g} × "
                    f"{default_height_cm:g} cm."
                )

            if dimension_warning:
                st.warning(
                    dimension_warning
                )

            if (
                maximum_weight_kg is not None
                and weight_per_parcel_kg
                > maximum_weight_kg
            ):
                st.error(
                    "The entered weight exceeds the recommended "
                    f"maximum of {maximum_weight_kg:,.2f} kg "
                    f"for {parcel_type}."
                )

    # -----------------------------------------------------
    # SHIPMENT CALCULATIONS
    # -----------------------------------------------------
    volume_per_parcel_m3 = 0.0
    total_volume_m3 = 0.0
    volumetric_weight_per_parcel_kg = 0.0
    total_actual_weight_kg = 0.0
    total_volumetric_weight_kg = 0.0
    chargeable_weight_kg = 0.0

    if parcel_type != "Select Parcel Type":
        volume_per_parcel_m3 = (
            length_cm
            * width_cm
            * height_cm
        ) / 1_000_000

        total_volume_m3 = (
            volume_per_parcel_m3
            * int(parcel_quantity)
        )

        if volumetric_divisor > 0:
            volumetric_weight_per_parcel_kg = (
                length_cm
                * width_cm
                * height_cm
            ) / volumetric_divisor

        total_actual_weight_kg = (
            weight_per_parcel_kg
            * int(parcel_quantity)
        )

        total_volumetric_weight_kg = (
            volumetric_weight_per_parcel_kg
            * int(parcel_quantity)
        )

        chargeable_weight_kg = max(
            total_actual_weight_kg,
            total_volumetric_weight_kg,
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
                f"{int(parcel_quantity):,}",
            )

        with summary_col2:
            st.metric(
                "Total Actual Weight",
                f"{total_actual_weight_kg:,.2f} kg",
            )

        with summary_col3:
            st.metric(
                "Total Volume",
                f"{total_volume_m3:,.3f} m³",
            )

        with summary_col4:
            st.metric(
                "Chargeable Weight",
                f"{chargeable_weight_kg:,.2f} kg",
            )

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------
    validation_errors: list[str] = []

    if not shipment_id.strip():
        validation_errors.append(
            "Enter the shipment ID."
        )

    if not customer.strip():
        validation_errors.append(
            "Enter the customer name."
        )

    if origin_state == "Select State":
        validation_errors.append(
            "Select the origin state."
        )

    if destination_state == "Select State":
        validation_errors.append(
            "Select the destination state."
        )

    if not origin_region or origin_region == "Region Not Found":
        validation_errors.append(
            "The origin region could not be identified."
        )

    if (
        not destination_region
        or destination_region == "Region Not Found"
    ):
        validation_errors.append(
            "The destination region could not be identified."
        )

    if service_level == "Select Service Level":
        validation_errors.append(
            "Select the service level."
        )

    if parcel_type == "Select Parcel Type":
        validation_errors.append(
            "Select the parcel type."
        )

    if weight_per_parcel_kg <= 0:
        validation_errors.append(
            "Actual weight must be greater than zero."
        )

    if (
        length_cm <= 0
        or width_cm <= 0
        or height_cm <= 0
    ):
        validation_errors.append(
            "Length, width and height must be greater than zero."
        )

    # -----------------------------------------------------
    # SAVE AND CLEAR
    # -----------------------------------------------------
    button_col1, button_col2, button_col3 = st.columns(
        [1, 1, 2]
    )

    with button_col1:
        save_clicked = st.button(
            "💾 Save Shipment",
            type="primary",
            use_container_width=True,
        )

    with button_col2:
        clear_clicked = st.button(
            "🗑️ Clear",
            use_container_width=True,
        )

    if save_clicked:
        if validation_errors:
            for validation_error in validation_errors:
                st.warning(
                    validation_error
                )

        elif selected_service is None:
            st.error(
                "The selected service level was not found "
                "in service_level.csv."
            )

        else:
            st.session_state[
                SHIPMENT_KEY
            ] = {
                "shipment_source": MANUAL_MODE,
                "shipment_id": shipment_id.strip(),
                "shipment_date": shipment_date.isoformat(),
                "customer": customer.strip(),

                "origin_state": origin_state,
                "origin_region": origin_region,
                "destination_state": destination_state,
                "destination_region": destination_region,

                "service_level": service_level,
                "target_delivery": selected_service[
                    "Target Delivery (Days)"
                ],
                "priority": selected_service[
                    "Priority"
                ],
                "service_cost_multiplier": float(
                    selected_service[
                        "Cost Multiplier"
                    ]
                ),
                "delivery_frequency": (
                    delivery_frequency
                ),

                "parcel_type": parcel_type,
                "parcel_quantity": int(
                    parcel_quantity
                ),

                "length_cm": float(
                    length_cm
                ),
                "width_cm": float(
                    width_cm
                ),
                "height_cm": float(
                    height_cm
                ),
                "weight_per_parcel_kg": float(
                    weight_per_parcel_kg
                ),

                "volume_per_parcel_m3": float(
                    volume_per_parcel_m3
                ),
                "volumetric_weight_per_parcel_kg": float(
                    volumetric_weight_per_parcel_kg
                ),

                "total_actual_weight_kg": float(
                    total_actual_weight_kg
                ),
                "total_volumetric_weight_kg": float(
                    total_volumetric_weight_kg
                ),
                "chargeable_weight_kg": float(
                    chargeable_weight_kg
                ),
                "total_volume_m3": float(
                    total_volume_m3
                ),
                "volumetric_divisor": float(
                    volumetric_divisor
                ),

                # Inputs required by Fleet Capacity.
                "capacity_quantity_basis": int(
                    parcel_quantity
                ),
                "capacity_weight_basis_kg": float(
                    total_actual_weight_kg
                ),
                "capacity_volume_basis_m3": float(
                    total_volume_m3
                ),
            }

            st.success(
                "Shipment information has been saved successfully."
            )

    if clear_clicked:
        clear_page()
        st.rerun()


# =========================================================
# FILE UPLOAD
# =========================================================
else:
    st.markdown(
        '<div class="section-title">Upload Shipment File</div>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload CSV or XLSX shipment transactions",
        type=["csv", "xlsx"],
        key="shipment_upload",
    )
    st.caption("Required columns: " + ", ".join(REQUIRED_UPLOAD_COLUMNS))

    if uploaded_file is None:
        st.info("Upload a file to begin validation.")
    else:
        try:
            uploaded_df = read_uploaded_file(uploaded_file)
            cleaned_df, exception_df, file_errors = validate_upload(
                uploaded_df,
                set(state_options),
                set(service_options),
                set(parcel_options),
            )

            st.dataframe(cleaned_df.head(20), hide_index=True, use_container_width=True)

            if file_errors:
                for error in file_errors:
                    st.error(error)
            elif not exception_df.empty:
                invalid_rows = exception_df["Row"].nunique()
                st.warning(
                    f"{invalid_rows:,} row(s) contain validation errors."
                )
                st.dataframe(
                    exception_df, hide_index=True, use_container_width=True
                )
                st.download_button(
                    "Download Exception Report",
                    exception_df.to_csv(index=False).encode("utf-8-sig"),
                    "shipment_upload_exceptions.csv",
                    "text/csv",
                )
            else:
                processed_df = calculate_upload_fields(
                    cleaned_df, state_region_map, parcel_divisor_map
                )

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Shipments", f"{len(processed_df):,}")
                col2.metric(
                    "Actual Weight", f'{processed_df["Weight (kg)"].sum():,.2f} kg'
                )
                col3.metric(
                    "Total Volume", f'{processed_df["Volume (m³)"].sum():,.3f} m³'
                )
                col4.metric(
                    "Revenue",
                    f'RM {processed_df["Selling Price (RM)"].sum():,.2f}',
                )

                if st.button(
                    "💾 Save Uploaded Shipments",
                    type="primary",
                    use_container_width=True,
                ):
                    st.session_state[UPLOAD_DATA_KEY] = processed_df
                    st.session_state[SHIPMENT_KEY] = {
                        "shipment_source": UPLOAD_MODE,
                        "shipment_file_name": uploaded_file.name,
                        "shipment_count": int(len(processed_df)),
                        "parcel_quantity": int(len(processed_df)),
                        "total_actual_weight_kg": float(
                            processed_df["Weight (kg)"].sum()
                        ),
                        "chargeable_weight_kg": float(
                            processed_df["Chargeable Weight (kg)"].sum()
                        ),
                        "total_volume_m3": float(
                            processed_df["Volume (m³)"].sum()
                        ),
                        "total_revenue_rm": float(
                            processed_df["Selling Price (RM)"].sum()
                        ),
                        "capacity_quantity_basis": int(len(processed_df)),
                        "capacity_weight_basis_kg": float(
                            processed_df["Weight (kg)"].sum()
                        ),
                        "capacity_volume_basis_m3": float(
                            processed_df["Volume (m³)"].sum()
                        ),
                        "origin_regions": sorted(
                            processed_df["Origin Region"].dropna().unique().tolist()
                        ),
                        "destination_regions": sorted(
                            processed_df["Destination Region"]
                            .dropna()
                            .unique()
                            .tolist()
                        ),
                        "service_levels": sorted(
                            processed_df["Service Level"]
                            .dropna()
                            .unique()
                            .tolist()
                        ),
                        "parcel_types": sorted(
                            processed_df["Parcel Type"]
                            .dropna()
                            .unique()
                            .tolist()
                        ),
                    }
                    st.success(
                        f"{len(processed_df):,} shipment records were saved successfully."
                    )

        except Exception as error:
            st.error("Unable to process the uploaded shipment file.")
            st.exception(error)


# =========================================================
# SAVED DATA STATUS
# =========================================================
saved_shipment = st.session_state.get(SHIPMENT_KEY, {})

if saved_shipment:
    st.markdown(
        '<div class="section-title">Current Saved Shipment</div>',
        unsafe_allow_html=True,
    )

    if saved_shipment.get("shipment_source") == MANUAL_MODE:
        st.success("Manual shipment data is ready for Route Intelligence.")
        st.write(
            {
                "Shipment ID": saved_shipment.get("shipment_id"),
                "Route": (
                    f'{saved_shipment.get("origin_state", "")} → '
                    f'{saved_shipment.get("destination_state", "")}'
                ),
                "Service Level": saved_shipment.get("service_level"),
                "Parcel Type": saved_shipment.get("parcel_type"),
                "Parcel Quantity": saved_shipment.get("parcel_quantity"),
            }
        )
    else:
        st.success("Uploaded shipment data has been validated and saved.")
        st.write(
            {
                "File": saved_shipment.get("shipment_file_name"),
                "Shipment Records": saved_shipment.get("shipment_count"),
                "Actual Weight (kg)": saved_shipment.get(
                    "total_actual_weight_kg"
                ),
                "Total Volume (m³)": saved_shipment.get("total_volume_m3"),
                "Revenue (RM)": saved_shipment.get("total_revenue_rm"),
            }
        )
    