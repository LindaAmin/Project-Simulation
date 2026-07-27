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
# FILE PATHS
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

PARCEL_FILE = DATA_DIR / "parcel_master.csv"


# =========================================================
# DATA LOADING FUNCTION
# =========================================================
@st.cache_data
def load_parcel_master() -> pd.DataFrame:
    """
    Load and clean parcel assumptions.

    Standard parcel types contain fixed dimensions and maximum
    weight limits. Oversized parcels use user-entered values.
    """

    parcel_df = pd.read_csv(PARCEL_FILE)

    required_columns = [
        "Parcel Type",
        "Length (cm)",
        "Width (cm)",
        "Height (cm)",
        "Max Weight (kg)",
        "Volumetric Divisor",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in parcel_df.columns
    ]

    if missing_columns:
        raise ValueError(
            "The parcel master is missing these columns: "
            + ", ".join(missing_columns)
        )

    parcel_df["Parcel Type"] = (
        parcel_df["Parcel Type"]
        .astype(str)
        .str.strip()
    )

    parcel_df["Volumetric Divisor"] = pd.to_numeric(
        parcel_df["Volumetric Divisor"],
        errors="coerce",
    )

    return parcel_df.reset_index(drop=True)


# =========================================================
# LOAD MASTER DATA
# =========================================================
try:
    parcel_master = load_parcel_master()

except FileNotFoundError:
    st.error(
        "The parcel master file was not found. Ensure that "
        "'parcel_master.csv' is stored in the data folder."
    )
    st.stop()

except ValueError as error:
    st.error(str(error))
    st.stop()

except Exception as error:
    st.error(
        f"Unable to load the parcel master data: {error}"
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

    if st.button("⬅ Go to Shipment Information"):
        st.switch_page(
            "pages/1_Shipment_Information.py"
        )

    st.stop()


# =========================================================
# READ SHIPMENT INFORMATION
# =========================================================
parcel_type = shipment.get("parcel_type")
parcel_quantity = shipment.get("parcel_quantity", 0)

length_cm = shipment.get("length_cm", 0.0)
width_cm = shipment.get("width_cm", 0.0)
height_cm = shipment.get("height_cm", 0.0)

weight_per_parcel_kg = shipment.get(
    "weight_per_parcel_kg",
    0.0,
)

origin_state = shipment.get(
    "origin_state",
    "Not Available",
)

destination_state = shipment.get(
    "destination_state",
    "Not Available",
)

service_level = shipment.get(
    "service_level",
    "Not Available",
)


# =========================================================
# VALIDATE REQUIRED INPUTS
# =========================================================
required_inputs = {
    "Parcel Type": parcel_type,
    "Parcel Quantity": parcel_quantity,
    "Length": length_cm,
    "Width": width_cm,
    "Height": height_cm,
    "Weight per Parcel": weight_per_parcel_kg,
}

missing_inputs = []

for field_name, field_value in required_inputs.items():
    if field_value is None:
        missing_inputs.append(field_name)

    elif isinstance(field_value, str):
        if not field_value.strip():
            missing_inputs.append(field_name)

    elif float(field_value) <= 0:
        missing_inputs.append(field_name)


if missing_inputs:
    st.error(
        "The following shipment inputs are incomplete or invalid: "
        + ", ".join(missing_inputs)
    )

    st.info(
        "Return to Page 1 and complete the parcel information."
    )

    st.stop()


# Convert values to suitable numeric types
parcel_quantity = int(parcel_quantity)
length_cm = float(length_cm)
width_cm = float(width_cm)
height_cm = float(height_cm)
weight_per_parcel_kg = float(
    weight_per_parcel_kg
)


# =========================================================
# SESSION STATE
# =========================================================
if "parcel_assessment" not in st.session_state:
    st.session_state.parcel_assessment = {}


# =========================================================
# PAGE TITLE
# =========================================================
st.markdown(
    '<div class="main-title">📐 Parcel Assessment</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-subtitle">
        Assess shipment weight, dimensions, volume,
        volumetric weight and chargeable weight.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ASSESSMENT BASIS
# =========================================================
cost_basis(
    "Parcel Assessment Basis",
    """
    Actual shipment weight is calculated using the number of parcels
    and actual weight per parcel.

    Volumetric weight is calculated using parcel dimensions divided
    by the applicable volumetric divisor. Chargeable weight is the
    higher of actual weight and volumetric weight.

    These results will be used in the Fleet Capacity page to assess
    vehicle capacity and determine the required number of vehicles.
    """,
)


# =========================================================
# SHIPMENT SUMMARY
# =========================================================
st.markdown(
    '<div class="section-title">Shipment Summary</div>',
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
    st.markdown("**Parcel Type**")
    st.write(parcel_type)

with summary_col4:
    st.markdown("**Parcel Quantity**")
    st.write(f"{parcel_quantity:,}")


# =========================================================
# RETRIEVE PARCEL STANDARD
# =========================================================
parcel_record = parcel_master[
    parcel_master["Parcel Type"]
    .str.casefold()
    == str(parcel_type).casefold()
].copy()


if parcel_record.empty:
    st.error(
        f"The parcel type '{parcel_type}' was not found "
        "in the parcel master."
    )
    st.stop()


parcel_standard = parcel_record.iloc[0]

volumetric_divisor = pd.to_numeric(
    parcel_standard["Volumetric Divisor"],
    errors="coerce",
)

if pd.isna(volumetric_divisor) or volumetric_divisor <= 0:
    st.error(
        "The volumetric divisor in the parcel master "
        "must be greater than zero."
    )
    st.stop()

volumetric_divisor = float(
    volumetric_divisor
)


# =========================================================
# PARCEL DIMENSION DETAILS
# =========================================================
st.markdown(
    '<div class="section-title">Parcel Dimensions and Weight</div>',
    unsafe_allow_html=True,
)

dimension_col1, dimension_col2, dimension_col3, dimension_col4 = (
    st.columns(4)
)

with dimension_col1:
    st.metric(
        "Length per Parcel",
        f"{length_cm:,.1f} cm",
    )

with dimension_col2:
    st.metric(
        "Width per Parcel",
        f"{width_cm:,.1f} cm",
    )

with dimension_col3:
    st.metric(
        "Height per Parcel",
        f"{height_cm:,.1f} cm",
    )

with dimension_col4:
    st.metric(
        "Actual Weight per Parcel",
        f"{weight_per_parcel_kg:,.2f} kg",
    )


# =========================================================
# PARCEL CALCULATIONS
# =========================================================

# Volume in cubic centimetres
volume_per_parcel_cm3 = (
    length_cm
    * width_cm
    * height_cm
)

# Convert cubic centimetres to cubic metres
volume_per_parcel_m3 = (
    volume_per_parcel_cm3
    / 1_000_000
)

# Total shipment volume
total_volume_m3 = (
    volume_per_parcel_m3
    * parcel_quantity
)

# Total actual shipment weight
total_actual_weight_kg = (
    weight_per_parcel_kg
    * parcel_quantity
)

# Volumetric weight per parcel
volumetric_weight_per_parcel_kg = (
    volume_per_parcel_cm3
    / volumetric_divisor
)

# Total volumetric shipment weight
total_volumetric_weight_kg = (
    volumetric_weight_per_parcel_kg
    * parcel_quantity
)

# Chargeable weight
chargeable_weight_kg = max(
    total_actual_weight_kg,
    total_volumetric_weight_kg,
)

# Chargeable weight per parcel
chargeable_weight_per_parcel_kg = max(
    weight_per_parcel_kg,
    volumetric_weight_per_parcel_kg,
)

# Weight difference
weight_difference_kg = abs(
    total_actual_weight_kg
    - total_volumetric_weight_kg
)

# Volumetric weight ratio
if total_actual_weight_kg > 0:
    volumetric_weight_ratio = (
        total_volumetric_weight_kg
        / total_actual_weight_kg
    )
else:
    volumetric_weight_ratio = 0.0


# =========================================================
# DETERMINE CHARGEABLE-WEIGHT BASIS
# =========================================================
if (
    total_volumetric_weight_kg
    > total_actual_weight_kg
):
    chargeable_weight_basis = "Volumetric Weight"
    shipment_density_status = "Low-Density Shipment"

elif (
    total_actual_weight_kg
    > total_volumetric_weight_kg
):
    chargeable_weight_basis = "Actual Weight"
    shipment_density_status = "Weight-Dense Shipment"

else:
    chargeable_weight_basis = "Equal Weight"
    shipment_density_status = "Balanced Shipment"


# =========================================================
# CALCULATION RESULTS
# =========================================================
st.markdown(
    '<div class="section-title">Parcel Assessment Results</div>',
    unsafe_allow_html=True,
)

result_col1, result_col2, result_col3, result_col4 = (
    st.columns(4)
)

with result_col1:
    st.metric(
        "Total Actual Weight",
        f"{total_actual_weight_kg:,.2f} kg",
    )

with result_col2:
    st.metric(
        "Total Volumetric Weight",
        f"{total_volumetric_weight_kg:,.2f} kg",
    )

with result_col3:
    st.metric(
        "Chargeable Weight",
        f"{chargeable_weight_kg:,.2f} kg",
    )

with result_col4:
    st.metric(
        "Total Shipment Volume",
        f"{total_volume_m3:,.3f} m³",
    )


secondary_col1, secondary_col2, secondary_col3 = (
    st.columns(3)
)

with secondary_col1:
    st.metric(
        "Volume per Parcel",
        f"{volume_per_parcel_m3:,.4f} m³",
    )

with secondary_col2:
    st.metric(
        "Volumetric Weight per Parcel",
        f"{volumetric_weight_per_parcel_kg:,.2f} kg",
    )

with secondary_col3:
    st.metric(
        "Chargeable Weight per Parcel",
        f"{chargeable_weight_per_parcel_kg:,.2f} kg",
    )


# =========================================================
# PARCEL STANDARD COMPLIANCE
# =========================================================
st.markdown(
    '<div class="section-title">Parcel Standard Compliance</div>',
    unsafe_allow_html=True,
)


def convert_standard_value(value):
    """
    Convert a standard parcel value to float.

    Values such as 'User Input' return None.
    """

    numeric_value = pd.to_numeric(
        value,
        errors="coerce",
    )

    if pd.isna(numeric_value):
        return None

    return float(numeric_value)


standard_length_cm = convert_standard_value(
    parcel_standard["Length (cm)"]
)

standard_width_cm = convert_standard_value(
    parcel_standard["Width (cm)"]
)

standard_height_cm = convert_standard_value(
    parcel_standard["Height (cm)"]
)

maximum_weight_kg = convert_standard_value(
    parcel_standard["Max Weight (kg)"]
)


compliance_results = []

if standard_length_cm is not None:
    compliance_results.append(
        {
            "Assessment Item": "Length per Parcel",
            "Shipment Value": f"{length_cm:,.1f} cm",
            "Master Standard": (
                f"{standard_length_cm:,.1f} cm"
            ),
            "Status": (
                "Within Standard"
                if length_cm <= standard_length_cm
                else "Exceeds Standard"
            ),
        }
    )

if standard_width_cm is not None:
    compliance_results.append(
        {
            "Assessment Item": "Width per Parcel",
            "Shipment Value": f"{width_cm:,.1f} cm",
            "Master Standard": (
                f"{standard_width_cm:,.1f} cm"
            ),
            "Status": (
                "Within Standard"
                if width_cm <= standard_width_cm
                else "Exceeds Standard"
            ),
        }
    )

if standard_height_cm is not None:
    compliance_results.append(
        {
            "Assessment Item": "Height per Parcel",
            "Shipment Value": f"{height_cm:,.1f} cm",
            "Master Standard": (
                f"{standard_height_cm:,.1f} cm"
            ),
            "Status": (
                "Within Standard"
                if height_cm <= standard_height_cm
                else "Exceeds Standard"
            ),
        }
    )

if maximum_weight_kg is not None:
    compliance_results.append(
        {
            "Assessment Item": "Weight per Parcel",
            "Shipment Value": (
                f"{weight_per_parcel_kg:,.2f} kg"
            ),
            "Master Standard": (
                f"{maximum_weight_kg:,.2f} kg"
            ),
            "Status": (
                "Within Standard"
                if weight_per_parcel_kg
                <= maximum_weight_kg
                else "Exceeds Standard"
            ),
        }
    )


if compliance_results:
    compliance_df = pd.DataFrame(
        compliance_results
    )

    st.dataframe(
        compliance_df,
        hide_index=True,
        use_container_width=True,
    )

    non_compliant_items = compliance_df[
        compliance_df["Status"]
        == "Exceeds Standard"
    ]

    parcel_standard_compliant = (
        non_compliant_items.empty
    )

else:
    parcel_standard_compliant = True

    st.info(
        "The selected oversized parcel uses user-defined "
        "dimensions and weight. Standard size limits are "
        "therefore not applicable."
    )


# =========================================================
# ASSESSMENT INTERPRETATION
# =========================================================
st.markdown(
    '<div class="section-title">Assessment Interpretation</div>',
    unsafe_allow_html=True,
)

interpretation_col1, interpretation_col2 = (
    st.columns(2)
)

with interpretation_col1:
    st.markdown("**Chargeable Weight Basis**")
    st.info(
        f"{chargeable_weight_basis} is used because the "
        f"higher assessed shipment weight is "
        f"{chargeable_weight_kg:,.2f} kg."
    )

with interpretation_col2:
    st.markdown("**Shipment Density Classification**")
    st.info(shipment_density_status)


if parcel_standard_compliant:
    st.success(
        "The parcel measurements comply with the selected "
        "parcel-type standard."
    )

else:
    st.warning(
        "One or more parcel measurements exceed the selected "
        "parcel-type standard. Review the parcel type or update "
        "the shipment details on Page 1."
    )


# =========================================================
# CAPACITY ASSESSMENT BASIS
# =========================================================
st.markdown(
    '<div class="section-title">Fleet Capacity Inputs</div>',
    unsafe_allow_html=True,
)

capacity_col1, capacity_col2, capacity_col3 = (
    st.columns(3)
)

with capacity_col1:
    st.metric(
        "Parcel Quantity Basis",
        f"{parcel_quantity:,} parcels",
    )

with capacity_col2:
    st.metric(
        "Weight Capacity Basis",
        f"{total_actual_weight_kg:,.2f} kg",
    )

with capacity_col3:
    st.metric(
        "Volume Capacity Basis",
        f"{total_volume_m3:,.3f} m³",
    )


st.caption(
    "Fleet capacity should be assessed separately against all "
    "three constraints: parcel quantity, actual shipment weight "
    "and total shipment volume."
)


# =========================================================
# DETAILED CALCULATION
# =========================================================
with st.expander(
    "View Detailed Parcel Calculation",
    expanded=False,
):
    calculation_data = {
        "Calculation Item": [
            "Number of Parcels",
            "Length per Parcel",
            "Width per Parcel",
            "Height per Parcel",
            "Actual Weight per Parcel",
            "Volume per Parcel",
            "Total Shipment Volume",
            "Volumetric Divisor",
            "Volumetric Weight per Parcel",
            "Total Actual Weight",
            "Total Volumetric Weight",
            "Chargeable Weight",
            "Weight Difference",
            "Volumetric-to-Actual Weight Ratio",
        ],
        "Value": [
            f"{parcel_quantity:,}",
            f"{length_cm:,.1f} cm",
            f"{width_cm:,.1f} cm",
            f"{height_cm:,.1f} cm",
            f"{weight_per_parcel_kg:,.2f} kg",
            f"{volume_per_parcel_m3:,.4f} m³",
            f"{total_volume_m3:,.3f} m³",
            f"{volumetric_divisor:,.0f}",
            (
                f"{volumetric_weight_per_parcel_kg:,.2f} kg"
            ),
            f"{total_actual_weight_kg:,.2f} kg",
            f"{total_volumetric_weight_kg:,.2f} kg",
            f"{chargeable_weight_kg:,.2f} kg",
            f"{weight_difference_kg:,.2f} kg",
            f"{volumetric_weight_ratio:,.2f}x",
        ],
    }

    calculation_df = pd.DataFrame(
        calculation_data
    )

    st.dataframe(
        calculation_df,
        hide_index=True,
        use_container_width=True,
    )


# =========================================================
# SAVE ASSESSMENT
# =========================================================
st.markdown("<br>", unsafe_allow_html=True)

button_col1, button_col2, button_col3 = (
    st.columns([1, 1, 2])
)

with button_col1:
    save_assessment = st.button(
        "💾 Save Assessment",
        type="primary",
        use_container_width=True,
    )

with button_col2:
    clear_assessment = st.button(
        "🗑️ Clear",
        use_container_width=True,
    )


if save_assessment:
    st.session_state.parcel_assessment = {
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
        "volume_per_parcel_cm3": float(
            volume_per_parcel_cm3
        ),
        "volume_per_parcel_m3": float(
            volume_per_parcel_m3
        ),
        "total_volume_m3": float(
            total_volume_m3
        ),
        "total_actual_weight_kg": float(
            total_actual_weight_kg
        ),
        "volumetric_divisor": float(
            volumetric_divisor
        ),
        "volumetric_weight_per_parcel_kg": float(
            volumetric_weight_per_parcel_kg
        ),
        "total_volumetric_weight_kg": float(
            total_volumetric_weight_kg
        ),
        "chargeable_weight_per_parcel_kg": float(
            chargeable_weight_per_parcel_kg
        ),
        "chargeable_weight_kg": float(
            chargeable_weight_kg
        ),
        "chargeable_weight_basis": (
            chargeable_weight_basis
        ),
        "shipment_density_status": (
            shipment_density_status
        ),
        "weight_difference_kg": float(
            weight_difference_kg
        ),
        "volumetric_weight_ratio": float(
            volumetric_weight_ratio
        ),
        "parcel_standard_compliant": bool(
            parcel_standard_compliant
        ),
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
        "Parcel assessment has been saved successfully."
    )


if clear_assessment:
    st.session_state.parcel_assessment = {}
    st.rerun()


# =========================================================
# NEXT PAGE
# =========================================================
if st.session_state.get(
    "parcel_assessment"
):
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button(
        "Continue to Fleet Capacity ➡",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/4_Fleet_Capacity.py"
        )