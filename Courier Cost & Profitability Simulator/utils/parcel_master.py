"""
Parcel assessment and parcel-capacity calculations for the
Courier Cost Analysis application.

Responsibilities
----------------
- Parcel dimensions
- Parcel volume
- Volumetric weight
- Actual weight
- Chargeable weight
- Parcel density
- Parcel compliance
- Shipment-level parcel totals
- Capacity basis for fleet sizing

This module must not contain:
- Streamlit widgets
- Streamlit session state
- CSV loading
- CSS
- Page navigation
"""

from __future__ import annotations

from typing import Any

from utils.calculations import (
    safe_float,
    safe_int,
    validate_positive,
)


# =========================================================
# DEFAULT PARCEL CONSTANTS
# =========================================================
DEFAULT_VOLUMETRIC_DIVISOR = 5000.0

CM3_PER_M3 = 1_000_000.0


# =========================================================
# PARCEL DIMENSION CALCULATIONS
# =========================================================
def calculate_parcel_volume_cm3(
    length_cm: float,
    width_cm: float,
    height_cm: float,
) -> float:
    """
    Calculate the volume of one parcel in cubic centimetres.

    Formula
    -------
    Volume (cm³) = Length × Width × Height
    """

    length = validate_positive(
        length_cm,
        "Parcel length",
    )

    width = validate_positive(
        width_cm,
        "Parcel width",
    )

    height = validate_positive(
        height_cm,
        "Parcel height",
    )

    return (
        length
        * width
        * height
    )


def calculate_parcel_volume_m3(
    length_cm: float,
    width_cm: float,
    height_cm: float,
) -> float:
    """
    Calculate the volume of one parcel in cubic metres.

    Formula
    -------
    Volume (m³) =
        Length × Width × Height ÷ 1,000,000
    """

    volume_cm3 = calculate_parcel_volume_cm3(
        length_cm=length_cm,
        width_cm=width_cm,
        height_cm=height_cm,
    )

    return volume_cm3 / CM3_PER_M3


def calculate_total_parcel_volume(
    parcel_quantity: int,
    volume_per_parcel_m3: float,
) -> float:
    """
    Calculate total shipment volume.

    Formula
    -------
    Total volume =
        Parcel volume × Parcel quantity
    """

    quantity = safe_int(
        parcel_quantity
    )

    if quantity <= 0:
        raise ValueError(
            "Parcel quantity must be greater than zero."
        )

    parcel_volume = validate_positive(
        volume_per_parcel_m3,
        "Parcel volume",
    )

    return (
        parcel_volume
        * quantity
    )


# =========================================================
# VOLUMETRIC WEIGHT
# =========================================================
def calculate_volumetric_weight_kg(
    length_cm: float,
    width_cm: float,
    height_cm: float,
    volumetric_divisor: float = DEFAULT_VOLUMETRIC_DIVISOR,
) -> float:
    """
    Calculate volumetric weight for one parcel.

    Formula
    -------
    Volumetric weight (kg) =
        Length × Width × Height ÷ Volumetric divisor

    A common courier divisor is 5,000.
    """

    parcel_volume_cm3 = calculate_parcel_volume_cm3(
        length_cm=length_cm,
        width_cm=width_cm,
        height_cm=height_cm,
    )

    divisor = validate_positive(
        volumetric_divisor,
        "Volumetric divisor",
    )

    return (
        parcel_volume_cm3
        / divisor
    )


def calculate_total_volumetric_weight(
    parcel_quantity: int,
    volumetric_weight_per_parcel_kg: float,
) -> float:
    """
    Calculate total shipment volumetric weight.
    """

    quantity = safe_int(
        parcel_quantity
    )

    if quantity <= 0:
        raise ValueError(
            "Parcel quantity must be greater than zero."
        )

    volumetric_weight = validate_positive(
        volumetric_weight_per_parcel_kg,
        "Volumetric weight per parcel",
        allow_zero=True,
    )

    return (
        volumetric_weight
        * quantity
    )


# =========================================================
# ACTUAL WEIGHT
# =========================================================
def calculate_total_actual_weight(
    parcel_quantity: int,
    weight_per_parcel_kg: float,
) -> float:
    """
    Calculate total actual shipment weight.

    Formula
    -------
    Total actual weight =
        Parcel quantity × Actual weight per parcel
    """

    quantity = safe_int(
        parcel_quantity
    )

    if quantity <= 0:
        raise ValueError(
            "Parcel quantity must be greater than zero."
        )

    weight_per_parcel = validate_positive(
        weight_per_parcel_kg,
        "Weight per parcel",
    )

    return (
        quantity
        * weight_per_parcel
    )


# =========================================================
# CHARGEABLE WEIGHT
# =========================================================
def calculate_chargeable_weight(
    actual_weight_kg: float,
    volumetric_weight_kg: float,
) -> dict[str, Any]:
    """
    Determine chargeable weight.

    Chargeable weight is the higher of:
    - Actual weight
    - Volumetric weight
    """

    actual_weight = validate_positive(
        actual_weight_kg,
        "Actual weight",
    )

    volumetric_weight = validate_positive(
        volumetric_weight_kg,
        "Volumetric weight",
        allow_zero=True,
    )

    if actual_weight >= volumetric_weight:
        chargeable_weight = actual_weight
        chargeable_weight_basis = "Actual Weight"

    else:
        chargeable_weight = volumetric_weight
        chargeable_weight_basis = "Volumetric Weight"

    difference_kg = abs(
        actual_weight
        - volumetric_weight
    )

    return {
        "actual_weight_kg": actual_weight,
        "volumetric_weight_kg": (
            volumetric_weight
        ),
        "chargeable_weight_kg": (
            chargeable_weight
        ),
        "chargeable_weight_basis": (
            chargeable_weight_basis
        ),
        "weight_difference_kg": difference_kg,
    }


# =========================================================
# PARCEL DENSITY
# =========================================================
def calculate_parcel_density(
    actual_weight_kg: float,
    parcel_volume_m3: float,
) -> float:
    """
    Calculate parcel density.

    Formula
    -------
    Density (kg/m³) =
        Actual weight ÷ Parcel volume
    """

    actual_weight = validate_positive(
        actual_weight_kg,
        "Actual parcel weight",
    )

    parcel_volume = validate_positive(
        parcel_volume_m3,
        "Parcel volume",
    )

    return (
        actual_weight
        / parcel_volume
    )


def classify_parcel_density(
    density_kg_per_m3: float,
) -> dict[str, str]:
    """
    Classify parcel density for operational interpretation.

    The thresholds are planning indicators and can be adjusted
    to match the company's parcel policy.
    """

    density = validate_positive(
        density_kg_per_m3,
        "Parcel density",
        allow_zero=True,
    )

    if density < 100:
        return {
            "density_classification": "Very Low Density",
            "density_message": (
                "The parcel occupies substantial space relative "
                "to its actual weight. Vehicle volume may become "
                "the main capacity constraint."
            ),
        }

    if density < 250:
        return {
            "density_classification": "Low Density",
            "density_message": (
                "The parcel is relatively bulky. Volumetric "
                "weight and vehicle volume should be monitored."
            ),
        }

    if density < 500:
        return {
            "density_classification": "Medium Density",
            "density_message": (
                "The parcel has a balanced relationship between "
                "weight and occupied volume."
            ),
        }

    if density < 1_000:
        return {
            "density_classification": "High Density",
            "density_message": (
                "The parcel is relatively heavy for its size. "
                "Vehicle weight capacity may become the main "
                "constraint."
            ),
        }

    return {
        "density_classification": "Very High Density",
        "density_message": (
            "The parcel is very heavy relative to its volume. "
            "Review handling requirements and vehicle payload limits."
        ),
    }


# =========================================================
# PARCEL COMPLIANCE
# =========================================================
def assess_dimension_compliance(
    actual_value: float,
    maximum_value: float | None,
    dimension_name: str,
    unit: str = "cm",
) -> dict[str, Any]:
    """
    Assess one parcel dimension against its maximum limit.

    When maximum_value is None or zero, the check is treated
    as not applicable.
    """

    actual = validate_positive(
        actual_value,
        dimension_name,
    )

    if maximum_value is None:
        return {
            "field": dimension_name,
            "actual_value": actual,
            "maximum_value": None,
            "unit": unit,
            "compliant": True,
            "status": "Not Assessed",
            "excess_value": 0.0,
        }

    maximum = safe_float(
        maximum_value
    )

    if maximum <= 0:
        return {
            "field": dimension_name,
            "actual_value": actual,
            "maximum_value": maximum,
            "unit": unit,
            "compliant": True,
            "status": "Not Assessed",
            "excess_value": 0.0,
        }

    compliant = actual <= maximum

    excess_value = max(
        actual - maximum,
        0,
    )

    return {
        "field": dimension_name,
        "actual_value": actual,
        "maximum_value": maximum,
        "unit": unit,
        "compliant": compliant,
        "status": (
            "Compliant"
            if compliant
            else "Exceeded"
        ),
        "excess_value": excess_value,
    }


def assess_parcel_compliance(
    length_cm: float,
    width_cm: float,
    height_cm: float,
    weight_per_parcel_kg: float,
    max_length_cm: float | None = None,
    max_width_cm: float | None = None,
    max_height_cm: float | None = None,
    max_weight_kg: float | None = None,
) -> dict[str, Any]:
    """
    Assess parcel dimensions and weight against master-data limits.
    """

    compliance_checks = [
        assess_dimension_compliance(
            actual_value=length_cm,
            maximum_value=max_length_cm,
            dimension_name="Length",
            unit="cm",
        ),
        assess_dimension_compliance(
            actual_value=width_cm,
            maximum_value=max_width_cm,
            dimension_name="Width",
            unit="cm",
        ),
        assess_dimension_compliance(
            actual_value=height_cm,
            maximum_value=max_height_cm,
            dimension_name="Height",
            unit="cm",
        ),
        assess_dimension_compliance(
            actual_value=weight_per_parcel_kg,
            maximum_value=max_weight_kg,
            dimension_name="Weight",
            unit="kg",
        ),
    ]

    failed_checks = [
        check["field"]
        for check in compliance_checks
        if (
            check["status"] != "Not Assessed"
            and not check["compliant"]
        )
    ]

    assessed_checks = [
        check
        for check in compliance_checks
        if check["status"] != "Not Assessed"
    ]

    if not assessed_checks:
        compliance_status = "Not Assessed"
        parcel_standard_compliant = True

    elif not failed_checks:
        compliance_status = "Compliant"
        parcel_standard_compliant = True

    else:
        compliance_status = "Non-Compliant"
        parcel_standard_compliant = False

    return {
        "parcel_standard_compliant": (
            parcel_standard_compliant
        ),
        "compliance_status": (
            compliance_status
        ),
        "failed_compliance_checks": (
            failed_checks
        ),
        "compliance_checks": (
            compliance_checks
        ),
    }


# =========================================================
# PARCEL TYPE VALIDATION
# =========================================================
def compare_parcel_with_master(
    parcel_type: str,
    length_cm: float,
    width_cm: float,
    height_cm: float,
    weight_per_parcel_kg: float,
    parcel_master_record: dict[str, Any],
) -> dict[str, Any]:
    """
    Compare entered parcel information with a parcel-master record.

    Expected possible master-data keys:
    - Max Length (cm)
    - Max Width (cm)
    - Max Height (cm)
    - Max Weight (kg)

    Alternative key names are also supported.
    """

    max_length = parcel_master_record.get(
        "Max Length (cm)",
        parcel_master_record.get(
            "Maximum Length (cm)",
            parcel_master_record.get(
                "Max Length",
                None,
            ),
        ),
    )

    max_width = parcel_master_record.get(
        "Max Width (cm)",
        parcel_master_record.get(
            "Maximum Width (cm)",
            parcel_master_record.get(
                "Max Width",
                None,
            ),
        ),
    )

    max_height = parcel_master_record.get(
        "Max Height (cm)",
        parcel_master_record.get(
            "Maximum Height (cm)",
            parcel_master_record.get(
                "Max Height",
                None,
            ),
        ),
    )

    max_weight = parcel_master_record.get(
        "Max Weight (kg)",
        parcel_master_record.get(
            "Maximum Weight (kg)",
            parcel_master_record.get(
                "Max Weight",
                None,
            ),
        ),
    )

    compliance_result = assess_parcel_compliance(
        length_cm=length_cm,
        width_cm=width_cm,
        height_cm=height_cm,
        weight_per_parcel_kg=(
            weight_per_parcel_kg
        ),
        max_length_cm=(
            safe_float(max_length)
            if max_length is not None
            else None
        ),
        max_width_cm=(
            safe_float(max_width)
            if max_width is not None
            else None
        ),
        max_height_cm=(
            safe_float(max_height)
            if max_height is not None
            else None
        ),
        max_weight_kg=(
            safe_float(max_weight)
            if max_weight is not None
            else None
        ),
    )

    return {
        "parcel_type": parcel_type,
        "parcel_master_limits": {
            "max_length_cm": (
                safe_float(max_length)
                if max_length is not None
                else None
            ),
            "max_width_cm": (
                safe_float(max_width)
                if max_width is not None
                else None
            ),
            "max_height_cm": (
                safe_float(max_height)
                if max_height is not None
                else None
            ),
            "max_weight_kg": (
                safe_float(max_weight)
                if max_weight is not None
                else None
            ),
        },
        **compliance_result,
    }


# =========================================================
# COMPLETE PARCEL ASSESSMENT
# =========================================================
def calculate_parcel_assessment(
    parcel_quantity: int,
    length_cm: float,
    width_cm: float,
    height_cm: float,
    weight_per_parcel_kg: float,
    volumetric_divisor: float = DEFAULT_VOLUMETRIC_DIVISOR,
    parcel_type: str = "",
    max_length_cm: float | None = None,
    max_width_cm: float | None = None,
    max_height_cm: float | None = None,
    max_weight_kg: float | None = None,
) -> dict[str, Any]:
    """
    Run the complete parcel assessment for Page 3.

    Returns:
    - Per-parcel dimensions and weights
    - Shipment-level totals
    - Chargeable weight
    - Density
    - Compliance
    - Fleet-capacity basis
    """

    quantity = safe_int(
        parcel_quantity
    )

    if quantity <= 0:
        raise ValueError(
            "Parcel quantity must be greater than zero."
        )

    length = validate_positive(
        length_cm,
        "Parcel length",
    )

    width = validate_positive(
        width_cm,
        "Parcel width",
    )

    height = validate_positive(
        height_cm,
        "Parcel height",
    )

    actual_weight_per_parcel = (
        validate_positive(
            weight_per_parcel_kg,
            "Weight per parcel",
        )
    )

    divisor = validate_positive(
        volumetric_divisor,
        "Volumetric divisor",
    )

    volume_per_parcel_cm3 = (
        calculate_parcel_volume_cm3(
            length_cm=length,
            width_cm=width,
            height_cm=height,
        )
    )

    volume_per_parcel_m3 = (
        volume_per_parcel_cm3
        / CM3_PER_M3
    )

    volumetric_weight_per_parcel = (
        calculate_volumetric_weight_kg(
            length_cm=length,
            width_cm=width,
            height_cm=height,
            volumetric_divisor=divisor,
        )
    )

    total_actual_weight = (
        calculate_total_actual_weight(
            parcel_quantity=quantity,
            weight_per_parcel_kg=(
                actual_weight_per_parcel
            ),
        )
    )

    total_volumetric_weight = (
        calculate_total_volumetric_weight(
            parcel_quantity=quantity,
            volumetric_weight_per_parcel_kg=(
                volumetric_weight_per_parcel
            ),
        )
    )

    total_volume = calculate_total_parcel_volume(
        parcel_quantity=quantity,
        volume_per_parcel_m3=(
            volume_per_parcel_m3
        ),
    )

    chargeable_result = calculate_chargeable_weight(
        actual_weight_kg=(
            total_actual_weight
        ),
        volumetric_weight_kg=(
            total_volumetric_weight
        ),
    )

    density = calculate_parcel_density(
        actual_weight_kg=(
            actual_weight_per_parcel
        ),
        parcel_volume_m3=(
            volume_per_parcel_m3
        ),
    )

    density_result = classify_parcel_density(
        density_kg_per_m3=density
    )

    compliance_result = assess_parcel_compliance(
        length_cm=length,
        width_cm=width,
        height_cm=height,
        weight_per_parcel_kg=(
            actual_weight_per_parcel
        ),
        max_length_cm=max_length_cm,
        max_width_cm=max_width_cm,
        max_height_cm=max_height_cm,
        max_weight_kg=max_weight_kg,
    )

    return {
        "parcel_type": parcel_type,
        "parcel_quantity": quantity,

        "length_cm": length,
        "width_cm": width,
        "height_cm": height,

        "weight_per_parcel_kg": (
            actual_weight_per_parcel
        ),
        "volume_per_parcel_cm3": (
            volume_per_parcel_cm3
        ),
        "volume_per_parcel_m3": (
            volume_per_parcel_m3
        ),
        "volumetric_divisor": divisor,
        "volumetric_weight_per_parcel_kg": (
            volumetric_weight_per_parcel
        ),

        "total_actual_weight_kg": (
            total_actual_weight
        ),
        "total_volumetric_weight_kg": (
            total_volumetric_weight
        ),
        "total_volume_m3": total_volume,

        "chargeable_weight_kg": (
            chargeable_result[
                "chargeable_weight_kg"
            ]
        ),
        "chargeable_weight_basis": (
            chargeable_result[
                "chargeable_weight_basis"
            ]
        ),
        "weight_difference_kg": (
            chargeable_result[
                "weight_difference_kg"
            ]
        ),

        "density_kg_per_m3": density,
        "density_classification": (
            density_result[
                "density_classification"
            ]
        ),
        "density_message": (
            density_result[
                "density_message"
            ]
        ),

        # Fleet capacity must use actual weight,
        # not chargeable weight.
        "capacity_quantity_basis": quantity,
        "capacity_weight_basis_kg": (
            total_actual_weight
        ),
        "capacity_volume_basis_m3": (
            total_volume
        ),

        **compliance_result,
    }


# =========================================================
# MULTIPLE PARCEL GROUPS
# =========================================================
def calculate_mixed_parcel_assessment(
    parcel_groups: list[dict[str, Any]],
    volumetric_divisor: float = DEFAULT_VOLUMETRIC_DIVISOR,
) -> dict[str, Any]:
    """
    Calculate shipment totals for multiple parcel groups.

    Each parcel-group record should contain:
    {
        "parcel_type": "Medium",
        "parcel_quantity": 100,
        "length_cm": 40,
        "width_cm": 30,
        "height_cm": 20,
        "weight_per_parcel_kg": 3
    }
    """

    if not parcel_groups:
        raise ValueError(
            "At least one parcel group is required."
        )

    parcel_group_results = []

    total_parcel_quantity = 0
    total_actual_weight_kg = 0.0
    total_volumetric_weight_kg = 0.0
    total_volume_m3 = 0.0

    all_groups_compliant = True
    failed_group_records = []

    for index, parcel_group in enumerate(
        parcel_groups,
        start=1,
    ):
        group_result = calculate_parcel_assessment(
            parcel_quantity=parcel_group.get(
                "parcel_quantity",
                0,
            ),
            length_cm=parcel_group.get(
                "length_cm",
                0,
            ),
            width_cm=parcel_group.get(
                "width_cm",
                0,
            ),
            height_cm=parcel_group.get(
                "height_cm",
                0,
            ),
            weight_per_parcel_kg=parcel_group.get(
                "weight_per_parcel_kg",
                0,
            ),
            volumetric_divisor=parcel_group.get(
                "volumetric_divisor",
                volumetric_divisor,
            ),
            parcel_type=parcel_group.get(
                "parcel_type",
                f"Parcel Group {index}",
            ),
            max_length_cm=parcel_group.get(
                "max_length_cm",
                None,
            ),
            max_width_cm=parcel_group.get(
                "max_width_cm",
                None,
            ),
            max_height_cm=parcel_group.get(
                "max_height_cm",
                None,
            ),
            max_weight_kg=parcel_group.get(
                "max_weight_kg",
                None,
            ),
        )

        group_result[
            "parcel_group_number"
        ] = index

        parcel_group_results.append(
            group_result
        )

        total_parcel_quantity += (
            group_result[
                "parcel_quantity"
            ]
        )

        total_actual_weight_kg += (
            group_result[
                "total_actual_weight_kg"
            ]
        )

        total_volumetric_weight_kg += (
            group_result[
                "total_volumetric_weight_kg"
            ]
        )

        total_volume_m3 += (
            group_result[
                "total_volume_m3"
            ]
        )

        if not group_result[
            "parcel_standard_compliant"
        ]:
            all_groups_compliant = False

            failed_group_records.append(
                {
                    "parcel_group_number": index,
                    "parcel_type": group_result[
                        "parcel_type"
                    ],
                    "failed_checks": group_result[
                        "failed_compliance_checks"
                    ],
                }
            )

    chargeable_result = calculate_chargeable_weight(
        actual_weight_kg=(
            total_actual_weight_kg
        ),
        volumetric_weight_kg=(
            total_volumetric_weight_kg
        ),
    )

    overall_density = (
        total_actual_weight_kg
        / total_volume_m3
        if total_volume_m3 > 0
        else 0
    )

    density_result = classify_parcel_density(
        density_kg_per_m3=(
            overall_density
        )
    )

    return {
        "parcel_group_count": len(
            parcel_group_results
        ),
        "parcel_groups": parcel_group_results,

        "parcel_quantity": (
            total_parcel_quantity
        ),
        "total_actual_weight_kg": (
            total_actual_weight_kg
        ),
        "total_volumetric_weight_kg": (
            total_volumetric_weight_kg
        ),
        "total_volume_m3": (
            total_volume_m3
        ),

        "chargeable_weight_kg": (
            chargeable_result[
                "chargeable_weight_kg"
            ]
        ),
        "chargeable_weight_basis": (
            chargeable_result[
                "chargeable_weight_basis"
            ]
        ),

        "density_kg_per_m3": (
            overall_density
        ),
        "density_classification": (
            density_result[
                "density_classification"
            ]
        ),
        "density_message": (
            density_result[
                "density_message"
            ]
        ),

        "parcel_standard_compliant": (
            all_groups_compliant
        ),
        "compliance_status": (
            "Compliant"
            if all_groups_compliant
            else "Non-Compliant"
        ),
        "failed_parcel_groups": (
            failed_group_records
        ),

        "capacity_quantity_basis": (
            total_parcel_quantity
        ),
        "capacity_weight_basis_kg": (
            total_actual_weight_kg
        ),
        "capacity_volume_basis_m3": (
            total_volume_m3
        ),
    }


# =========================================================
# PARCEL SUMMARY RECORD
# =========================================================
def create_parcel_summary(
    parcel_assessment: dict[str, Any],
) -> dict[str, Any]:
    """
    Create a concise parcel summary for tables or reports.
    """

    return {
        "Parcel Type": parcel_assessment.get(
            "parcel_type",
            "",
        ),
        "Parcel Quantity": safe_int(
            parcel_assessment.get(
                "parcel_quantity",
                0,
            )
        ),
        "Weight per Parcel (kg)": safe_float(
            parcel_assessment.get(
                "weight_per_parcel_kg",
                0,
            )
        ),
        "Volume per Parcel (m³)": safe_float(
            parcel_assessment.get(
                "volume_per_parcel_m3",
                0,
            )
        ),
        "Volumetric Weight per Parcel (kg)": (
            safe_float(
                parcel_assessment.get(
                    "volumetric_weight_per_parcel_kg",
                    0,
                )
            )
        ),
        "Total Actual Weight (kg)": safe_float(
            parcel_assessment.get(
                "total_actual_weight_kg",
                0,
            )
        ),
        "Total Volumetric Weight (kg)": (
            safe_float(
                parcel_assessment.get(
                    "total_volumetric_weight_kg",
                    0,
                )
            )
        ),
        "Chargeable Weight (kg)": safe_float(
            parcel_assessment.get(
                "chargeable_weight_kg",
                0,
            )
        ),
        "Chargeable Weight Basis": (
            parcel_assessment.get(
                "chargeable_weight_basis",
                "",
            )
        ),
        "Total Volume (m³)": safe_float(
            parcel_assessment.get(
                "total_volume_m3",
                0,
            )
        ),
        "Density (kg/m³)": safe_float(
            parcel_assessment.get(
                "density_kg_per_m3",
                0,
            )
        ),
        "Compliance Status": (
            parcel_assessment.get(
                "compliance_status",
                "",
            )
        ),
    }