"""
Shared calculation functions for the Courier Cost Analysis application.

This module contains calculation logic only.

It should not contain:
- Streamlit widgets
- Streamlit session state
- Page navigation
- CSV loading
- CSS or page styling

Pages should collect inputs, call these functions and store the returned
results in st.session_state.
"""

from __future__ import annotations

import math
from typing import Any


# =========================================================
# GENERAL VALIDATION
# =========================================================
def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Safely convert a value to float.

    Parameters
    ----------
    value:
        Value to convert.

    default:
        Value returned when conversion fails.

    Returns
    -------
    float
    """

    try:
        if value is None:
            return default

        converted_value = float(value)

        if math.isnan(converted_value):
            return default

        return converted_value

    except (TypeError, ValueError):
        return default


def safe_int(
    value: Any,
    default: int = 0,
) -> int:
    """
    Safely convert a value to integer.

    Decimal values are rounded to the nearest integer.
    """

    try:
        if value is None:
            return default

        converted_value = float(value)

        if math.isnan(converted_value):
            return default

        return int(round(converted_value))

    except (TypeError, ValueError):
        return default


def validate_positive(
    value: float,
    field_name: str,
    allow_zero: bool = False,
) -> float:
    """
    Validate that a numeric value is positive.

    Raises
    ------
    ValueError
        When the value is invalid.
    """

    numeric_value = safe_float(value)

    if allow_zero:
        if numeric_value < 0:
            raise ValueError(
                f"{field_name} cannot be negative."
            )

    elif numeric_value <= 0:
        raise ValueError(
            f"{field_name} must be greater than zero."
        )

    return numeric_value


def percentage_change(
    baseline_value: float,
    new_value: float,
) -> float:
    """
    Calculate percentage change from baseline to new value.
    """

    baseline = safe_float(baseline_value)
    new = safe_float(new_value)

    if baseline == 0:
        return 0.0

    return (
        (new - baseline)
        / baseline
        * 100
    )


def apply_percentage_change(
    baseline_value: float,
    change_pct: float,
) -> float:
    """
    Apply a percentage increase or decrease to a baseline value.

    Example
    -------
    apply_percentage_change(100, 10) = 110
    apply_percentage_change(100, -10) = 90
    """

    return safe_float(
        baseline_value
    ) * (
        1
        + safe_float(change_pct) / 100
    )


# =========================================================
# PARCEL CALCULATIONS
# =========================================================
def calculate_parcel_volume_m3(
    length_cm: float,
    width_cm: float,
    height_cm: float,
) -> float:
    """
    Calculate parcel volume in cubic metres.

    Formula
    -------
    length × width × height ÷ 1,000,000
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
        / 1_000_000
    )


def calculate_volumetric_weight_kg(
    length_cm: float,
    width_cm: float,
    height_cm: float,
    volumetric_divisor: float = 5000,
) -> float:
    """
    Calculate volumetric weight in kilograms.

    Formula
    -------
    length × width × height ÷ volumetric divisor
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

    divisor = validate_positive(
        volumetric_divisor,
        "Volumetric divisor",
    )

    return (
        length
        * width
        * height
        / divisor
    )


def calculate_chargeable_weight_kg(
    actual_weight_kg: float,
    volumetric_weight_kg: float,
) -> dict[str, Any]:
    """
    Determine the chargeable weight.

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
        basis = "Actual Weight"
        chargeable_weight = actual_weight

    else:
        basis = "Volumetric Weight"
        chargeable_weight = volumetric_weight

    return {
        "chargeable_weight_kg": (
            chargeable_weight
        ),
        "chargeable_weight_basis": basis,
    }


def calculate_parcel_density(
    actual_weight_kg: float,
    parcel_volume_m3: float,
) -> float:
    """
    Calculate parcel density in kilograms per cubic metre.
    """

    actual_weight = validate_positive(
        actual_weight_kg,
        "Actual weight",
    )

    volume = validate_positive(
        parcel_volume_m3,
        "Parcel volume",
    )

    return actual_weight / volume


def assess_parcel_compliance(
    length_cm: float,
    width_cm: float,
    height_cm: float,
    actual_weight_kg: float,
    max_length_cm: float,
    max_width_cm: float,
    max_height_cm: float,
    max_weight_kg: float,
) -> dict[str, Any]:
    """
    Assess whether a parcel complies with selected parcel limits.
    """

    dimensions = {
        "Length": (
            safe_float(length_cm),
            safe_float(max_length_cm),
        ),
        "Width": (
            safe_float(width_cm),
            safe_float(max_width_cm),
        ),
        "Height": (
            safe_float(height_cm),
            safe_float(max_height_cm),
        ),
        "Weight": (
            safe_float(actual_weight_kg),
            safe_float(max_weight_kg),
        ),
    }

    failed_checks = []

    for field_name, (
        actual_value,
        maximum_value,
    ) in dimensions.items():

        if maximum_value > 0 and (
            actual_value > maximum_value
        ):
            failed_checks.append(field_name)

    return {
        "parcel_standard_compliant": (
            len(failed_checks) == 0
        ),
        "failed_compliance_checks": (
            failed_checks
        ),
        "compliance_status": (
            "Compliant"
            if not failed_checks
            else "Non-Compliant"
        ),
    }


def calculate_parcel_assessment(
    parcel_quantity: int,
    length_cm: float,
    width_cm: float,
    height_cm: float,
    weight_per_parcel_kg: float,
    volumetric_divisor: float = 5000,
    max_length_cm: float | None = None,
    max_width_cm: float | None = None,
    max_height_cm: float | None = None,
    max_weight_kg: float | None = None,
) -> dict[str, Any]:
    """
    Run a complete parcel assessment.

    Returns shipment-level parcel volume, actual weight,
    volumetric weight and chargeable weight.
    """

    quantity = safe_int(parcel_quantity)

    if quantity <= 0:
        raise ValueError(
            "Parcel quantity must be greater than zero."
        )

    weight_per_parcel = validate_positive(
        weight_per_parcel_kg,
        "Weight per parcel",
    )

    volume_per_parcel = (
        calculate_parcel_volume_m3(
            length_cm=length_cm,
            width_cm=width_cm,
            height_cm=height_cm,
        )
    )

    volumetric_weight_per_parcel = (
        calculate_volumetric_weight_kg(
            length_cm=length_cm,
            width_cm=width_cm,
            height_cm=height_cm,
            volumetric_divisor=(
                volumetric_divisor
            ),
        )
    )

    total_actual_weight = (
        weight_per_parcel
        * quantity
    )

    total_volumetric_weight = (
        volumetric_weight_per_parcel
        * quantity
    )

    total_volume = (
        volume_per_parcel
        * quantity
    )

    chargeable_result = (
        calculate_chargeable_weight_kg(
            actual_weight_kg=(
                total_actual_weight
            ),
            volumetric_weight_kg=(
                total_volumetric_weight
            ),
        )
    )

    density = calculate_parcel_density(
        actual_weight_kg=weight_per_parcel,
        parcel_volume_m3=volume_per_parcel,
    )

    compliance_result = {
        "parcel_standard_compliant": True,
        "failed_compliance_checks": [],
        "compliance_status": "Not Assessed",
    }

    compliance_limits = [
        max_length_cm,
        max_width_cm,
        max_height_cm,
        max_weight_kg,
    ]

    if all(
        limit is not None
        for limit in compliance_limits
    ):
        compliance_result = (
            assess_parcel_compliance(
                length_cm=length_cm,
                width_cm=width_cm,
                height_cm=height_cm,
                actual_weight_kg=(
                    weight_per_parcel
                ),
                max_length_cm=safe_float(
                    max_length_cm
                ),
                max_width_cm=safe_float(
                    max_width_cm
                ),
                max_height_cm=safe_float(
                    max_height_cm
                ),
                max_weight_kg=safe_float(
                    max_weight_kg
                ),
            )
        )

    return {
        "parcel_quantity": quantity,
        "length_cm": safe_float(length_cm),
        "width_cm": safe_float(width_cm),
        "height_cm": safe_float(height_cm),

        "weight_per_parcel_kg": (
            weight_per_parcel
        ),
        "volume_per_parcel_m3": (
            volume_per_parcel
        ),
        "volumetric_weight_per_parcel_kg": (
            volumetric_weight_per_parcel
        ),
        "density_kg_per_m3": density,

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
# ROUTE CALCULATIONS
# =========================================================
def calculate_total_trip_distance(
    one_way_distance_km: float,
    return_trip_required: bool = True,
    distance_multiplier: float | None = None,
) -> float:
    """
    Calculate total journey distance.

    When distance_multiplier is supplied, it takes precedence.
    Otherwise:
    - Return trip = 2
    - One-way trip = 1
    """

    one_way_distance = validate_positive(
        one_way_distance_km,
        "One-way distance",
    )

    if distance_multiplier is None:
        multiplier = (
            2.0
            if return_trip_required
            else 1.0
        )

    else:
        multiplier = validate_positive(
            distance_multiplier,
            "Distance multiplier",
        )

    return one_way_distance * multiplier


def calculate_driving_hours(
    total_distance_km: float,
    average_speed_kmh: float,
) -> float:
    """
    Calculate estimated driving time.
    """

    distance = validate_positive(
        total_distance_km,
        "Total trip distance",
    )

    speed = validate_positive(
        average_speed_kmh,
        "Average speed",
    )

    return distance / speed


def calculate_total_journey_hours(
    total_distance_km: float,
    average_speed_kmh: float,
    loading_unloading_hours: float = 0,
    other_delay_hours: float = 0,
) -> dict[str, float]:
    """
    Calculate total journey time including handling and delays.
    """

    driving_hours = calculate_driving_hours(
        total_distance_km=total_distance_km,
        average_speed_kmh=average_speed_kmh,
    )

    loading_hours = validate_positive(
        loading_unloading_hours,
        "Loading and unloading hours",
        allow_zero=True,
    )

    delay_hours = validate_positive(
        other_delay_hours,
        "Other delay hours",
        allow_zero=True,
    )

    total_journey_hours = (
        driving_hours
        + loading_hours
        + delay_hours
    )

    return {
        "estimated_driving_hours": (
            driving_hours
        ),
        "loading_unloading_hours": (
            loading_hours
        ),
        "other_delay_hours": delay_hours,
        "estimated_total_journey_hours": (
            total_journey_hours
        ),
    }


# =========================================================
# FLEET-CAPACITY CALCULATIONS
# =========================================================
def calculate_vehicles_by_capacity(
    parcel_quantity: int,
    total_actual_weight_kg: float,
    total_volume_m3: float,
    vehicle_max_parcels: int,
    vehicle_max_weight_kg: float,
    vehicle_max_volume_m3: float,
) -> dict[str, Any]:
    """
    Calculate fleet requirement using parcel quantity,
    actual weight and shipment volume.

    Fleet sizing uses actual weight, not chargeable weight.
    """

    quantity = safe_int(parcel_quantity)
    maximum_parcels = safe_int(
        vehicle_max_parcels
    )

    actual_weight = validate_positive(
        total_actual_weight_kg,
        "Total actual weight",
    )

    shipment_volume = validate_positive(
        total_volume_m3,
        "Total shipment volume",
    )

    maximum_weight = validate_positive(
        vehicle_max_weight_kg,
        "Vehicle maximum weight",
    )

    maximum_volume = validate_positive(
        vehicle_max_volume_m3,
        "Vehicle maximum volume",
    )

    if quantity <= 0:
        raise ValueError(
            "Parcel quantity must be greater than zero."
        )

    if maximum_parcels <= 0:
        raise ValueError(
            "Vehicle maximum parcel capacity must "
            "be greater than zero."
        )

    vehicles_by_parcel = math.ceil(
        quantity / maximum_parcels
    )

    vehicles_by_weight = math.ceil(
        actual_weight / maximum_weight
    )

    vehicles_by_volume = math.ceil(
        shipment_volume / maximum_volume
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

    controlling_value = max(
        constraint_values.values()
    )

    controlling_constraints = [
        constraint
        for constraint, value
        in constraint_values.items()
        if value == controlling_value
    ]

    return {
        "vehicles_by_parcel": (
            vehicles_by_parcel
        ),
        "vehicles_by_weight": (
            vehicles_by_weight
        ),
        "vehicles_by_volume": (
            vehicles_by_volume
        ),
        "required_vehicles": (
            required_vehicles
        ),
        "capacity_constraint": " and ".join(
            controlling_constraints
        ),
    }


def calculate_buffer_vehicles(
    required_vehicles: int,
    operational_buffer_pct: float,
) -> dict[str, int]:
    """
    Calculate additional vehicles required as an
    operational buffer.
    """

    required = safe_int(required_vehicles)

    if required <= 0:
        raise ValueError(
            "Required vehicles must be greater "
            "than zero."
        )

    buffer_pct = validate_positive(
        operational_buffer_pct,
        "Operational buffer",
        allow_zero=True,
    )

    additional_buffer_vehicles = math.ceil(
        required
        * buffer_pct
        / 100
    )

    planned_fleet_size = (
        required
        + additional_buffer_vehicles
    )

    return {
        "additional_buffer_vehicles": (
            additional_buffer_vehicles
        ),
        "planned_fleet_size": (
            planned_fleet_size
        ),
    }


def calculate_fleet_utilisation(
    parcel_quantity: int,
    total_actual_weight_kg: float,
    total_volume_m3: float,
    planned_fleet_size: int,
    vehicle_max_parcels: int,
    vehicle_max_weight_kg: float,
    vehicle_max_volume_m3: float,
) -> dict[str, float]:
    """
    Calculate parcel, weight and volume utilisation.
    """

    fleet_size = safe_int(
        planned_fleet_size
    )

    if fleet_size <= 0:
        raise ValueError(
            "Planned fleet size must be greater "
            "than zero."
        )

    total_parcel_capacity = (
        fleet_size
        * safe_int(vehicle_max_parcels)
    )

    total_weight_capacity = (
        fleet_size
        * safe_float(
            vehicle_max_weight_kg
        )
    )

    total_volume_capacity = (
        fleet_size
        * safe_float(
            vehicle_max_volume_m3
        )
    )

    if (
        total_parcel_capacity <= 0
        or total_weight_capacity <= 0
        or total_volume_capacity <= 0
    ):
        raise ValueError(
            "Vehicle capacity values must be "
            "greater than zero."
        )

    parcel_utilisation_pct = (
        safe_int(parcel_quantity)
        / total_parcel_capacity
        * 100
    )

    weight_utilisation_pct = (
        safe_float(total_actual_weight_kg)
        / total_weight_capacity
        * 100
    )

    volume_utilisation_pct = (
        safe_float(total_volume_m3)
        / total_volume_capacity
        * 100
    )

    overall_utilisation_pct = max(
        parcel_utilisation_pct,
        weight_utilisation_pct,
        volume_utilisation_pct,
    )

    return {
        "total_parcel_capacity": (
            total_parcel_capacity
        ),
        "total_weight_capacity_kg": (
            total_weight_capacity
        ),
        "total_volume_capacity_m3": (
            total_volume_capacity
        ),
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


def calculate_fleet_availability(
    active_vehicle_count: int,
    required_vehicles: int,
    planned_fleet_size: int,
) -> dict[str, Any]:
    """
    Compare available vehicles with required and planned fleet.
    """

    available = max(
        safe_int(active_vehicle_count),
        0,
    )

    required = max(
        safe_int(required_vehicles),
        0,
    )

    planned = max(
        safe_int(planned_fleet_size),
        0,
    )

    fleet_shortfall = max(
        required - available,
        0,
    )

    planned_fleet_shortfall = max(
        planned - available,
        0,
    )

    if available >= planned:
        status = "Available"

    elif available >= required:
        status = "Required Fleet Available, Buffer Shortfall"

    else:
        status = "Fleet Shortfall"

    return {
        "active_vehicle_count": available,
        "fleet_shortfall": fleet_shortfall,
        "planned_fleet_shortfall": (
            planned_fleet_shortfall
        ),
        "availability_status": status,
    }


def calculate_fleet_capacity(
    parcel_quantity: int,
    total_actual_weight_kg: float,
    total_volume_m3: float,
    vehicle_max_parcels: int,
    vehicle_max_weight_kg: float,
    vehicle_max_volume_m3: float,
    operational_buffer_pct: float = 0,
    active_vehicle_count: int | None = None,
) -> dict[str, Any]:
    """
    Run a complete fleet-capacity assessment.
    """

    capacity_result = (
        calculate_vehicles_by_capacity(
            parcel_quantity=parcel_quantity,
            total_actual_weight_kg=(
                total_actual_weight_kg
            ),
            total_volume_m3=total_volume_m3,
            vehicle_max_parcels=(
                vehicle_max_parcels
            ),
            vehicle_max_weight_kg=(
                vehicle_max_weight_kg
            ),
            vehicle_max_volume_m3=(
                vehicle_max_volume_m3
            ),
        )
    )

    buffer_result = calculate_buffer_vehicles(
        required_vehicles=(
            capacity_result[
                "required_vehicles"
            ]
        ),
        operational_buffer_pct=(
            operational_buffer_pct
        ),
    )

    utilisation_result = (
        calculate_fleet_utilisation(
            parcel_quantity=parcel_quantity,
            total_actual_weight_kg=(
                total_actual_weight_kg
            ),
            total_volume_m3=total_volume_m3,
            planned_fleet_size=(
                buffer_result[
                    "planned_fleet_size"
                ]
            ),
            vehicle_max_parcels=(
                vehicle_max_parcels
            ),
            vehicle_max_weight_kg=(
                vehicle_max_weight_kg
            ),
            vehicle_max_volume_m3=(
                vehicle_max_volume_m3
            ),
        )
    )

    results = {
        **capacity_result,
        **buffer_result,
        **utilisation_result,
        "operational_buffer_pct": (
            safe_float(
                operational_buffer_pct
            )
        ),
    }

    if active_vehicle_count is not None:
        availability_result = (
            calculate_fleet_availability(
                active_vehicle_count=(
                    active_vehicle_count
                ),
                required_vehicles=(
                    capacity_result[
                        "required_vehicles"
                    ]
                ),
                planned_fleet_size=(
                    buffer_result[
                        "planned_fleet_size"
                    ]
                ),
            )
        )

        results.update(
            availability_result
        )

    return results


# =========================================================
# OPERATING-COST CALCULATIONS
# =========================================================
def calculate_fuel_cost(
    total_trip_distance_km: float,
    planned_fleet_size: int,
    fuel_efficiency_km_per_litre: float,
    fuel_rate_rm_per_litre: float,
) -> dict[str, float]:
    """
    Calculate shipment fuel consumption and cost.
    """

    distance = validate_positive(
        total_trip_distance_km,
        "Total trip distance",
    )

    fleet_size = safe_int(
        planned_fleet_size
    )

    if fleet_size <= 0:
        raise ValueError(
            "Planned fleet size must be greater "
            "than zero."
        )

    fuel_efficiency = validate_positive(
        fuel_efficiency_km_per_litre,
        "Fuel efficiency",
    )

    fuel_rate = validate_positive(
        fuel_rate_rm_per_litre,
        "Fuel rate",
        allow_zero=True,
    )

    fuel_litres_per_vehicle = (
        distance / fuel_efficiency
    )

    total_fuel_litres = (
        fuel_litres_per_vehicle
        * fleet_size
    )

    fuel_cost = (
        total_fuel_litres
        * fuel_rate
    )

    return {
        "fuel_litres_per_vehicle": (
            fuel_litres_per_vehicle
        ),
        "total_fuel_litres": (
            total_fuel_litres
        ),
        "fuel_cost_per_shipment": (
            fuel_cost
        ),
    }


def calculate_toll_cost(
    total_trip_distance_km: float,
    planned_fleet_size: int,
    toll_rate_rm_per_km: float,
) -> float:
    """
    Calculate total toll cost for the shipment.
    """

    distance = validate_positive(
        total_trip_distance_km,
        "Total trip distance",
    )

    fleet_size = safe_int(
        planned_fleet_size
    )

    if fleet_size <= 0:
        raise ValueError(
            "Planned fleet size must be greater "
            "than zero."
        )

    toll_rate = validate_positive(
        toll_rate_rm_per_km,
        "Toll rate",
        allow_zero=True,
    )

    return (
        distance
        * fleet_size
        * toll_rate
    )


def calculate_maintenance_cost(
    total_trip_distance_km: float,
    planned_fleet_size: int,
    service_interval_km: float,
    service_cost_rm: float,
) -> dict[str, float]:
    """
    Allocate maintenance cost based on distance travelled.
    """

    distance = validate_positive(
        total_trip_distance_km,
        "Total trip distance",
    )

    fleet_size = safe_int(
        planned_fleet_size
    )

    if fleet_size <= 0:
        raise ValueError(
            "Planned fleet size must be greater "
            "than zero."
        )

    service_interval = validate_positive(
        service_interval_km,
        "Service interval",
    )

    service_cost = validate_positive(
        service_cost_rm,
        "Service cost",
        allow_zero=True,
    )

    maintenance_cost_per_km = (
        service_cost
        / service_interval
    )

    maintenance_cost_per_shipment = (
        maintenance_cost_per_km
        * distance
        * fleet_size
    )

    return {
        "maintenance_cost_per_km": (
            maintenance_cost_per_km
        ),
        "maintenance_cost_per_shipment": (
            maintenance_cost_per_shipment
        ),
    }


def calculate_tyre_cost(
    total_trip_distance_km: float,
    planned_fleet_size: int,
    tyre_change_interval_km: float,
    tyre_cost_rm: float,
) -> dict[str, float]:
    """
    Allocate tyre replacement cost based on distance travelled.
    """

    distance = validate_positive(
        total_trip_distance_km,
        "Total trip distance",
    )

    fleet_size = safe_int(
        planned_fleet_size
    )

    if fleet_size <= 0:
        raise ValueError(
            "Planned fleet size must be greater "
            "than zero."
        )

    tyre_interval = validate_positive(
        tyre_change_interval_km,
        "Tyre replacement interval",
    )

    tyre_cost = validate_positive(
        tyre_cost_rm,
        "Tyre cost",
        allow_zero=True,
    )

    tyre_cost_per_km = (
        tyre_cost
        / tyre_interval
    )

    tyre_cost_per_shipment = (
        tyre_cost_per_km
        * distance
        * fleet_size
    )

    return {
        "tyre_cost_per_km": (
            tyre_cost_per_km
        ),
        "tyre_cost_per_shipment": (
            tyre_cost_per_shipment
        ),
    }


def calculate_monthly_employee_cost(
    monthly_salary_rm: float,
    epf_rate_pct: float = 0,
    socso_rm: float = 0,
    eis_rm: float = 0,
    other_cost_rm: float = 0,
) -> dict[str, float]:
    """
    Calculate total monthly employee cost.
    """

    salary = validate_positive(
        monthly_salary_rm,
        "Monthly salary",
        allow_zero=True,
    )

    epf_rate = validate_positive(
        epf_rate_pct,
        "EPF rate",
        allow_zero=True,
    )

    socso = validate_positive(
        socso_rm,
        "SOCSO cost",
        allow_zero=True,
    )

    eis = validate_positive(
        eis_rm,
        "EIS cost",
        allow_zero=True,
    )

    other_cost = validate_positive(
        other_cost_rm,
        "Other employee cost",
        allow_zero=True,
    )

    epf_cost = (
        salary
        * epf_rate
        / 100
    )

    total_monthly_employee_cost = (
        salary
        + epf_cost
        + socso
        + eis
        + other_cost
    )

    return {
        "monthly_salary_rm": salary,
        "monthly_epf_rm": epf_cost,
        "monthly_socso_rm": socso,
        "monthly_eis_rm": eis,
        "monthly_other_cost_rm": (
            other_cost
        ),
        "total_monthly_employee_cost": (
            total_monthly_employee_cost
        ),
    }


def calculate_overtime_cost(
    overtime_hours_per_employee: float,
    overtime_rate_rm_per_hour: float,
    employee_count: int,
) -> float:
    """
    Calculate overtime cost per shipment.
    """

    overtime_hours = validate_positive(
        overtime_hours_per_employee,
        "Overtime hours",
        allow_zero=True,
    )

    overtime_rate = validate_positive(
        overtime_rate_rm_per_hour,
        "Overtime rate",
        allow_zero=True,
    )

    employees = max(
        safe_int(employee_count),
        0,
    )

    return (
        overtime_hours
        * overtime_rate
        * employees
    )


def calculate_monthly_vehicle_financing(
    monthly_instalment_per_vehicle_rm: float,
    planned_fleet_size: int,
) -> float:
    """
    Calculate total monthly vehicle financing cost.
    """

    instalment = validate_positive(
        monthly_instalment_per_vehicle_rm,
        "Monthly instalment",
        allow_zero=True,
    )

    fleet_size = max(
        safe_int(planned_fleet_size),
        0,
    )

    return instalment * fleet_size


def calculate_monthly_vehicle_insurance(
    annual_insurance_per_vehicle_rm: float,
    planned_fleet_size: int,
) -> float:
    """
    Convert annual vehicle insurance to monthly fleet cost.
    """

    annual_insurance = validate_positive(
        annual_insurance_per_vehicle_rm,
        "Annual insurance",
        allow_zero=True,
    )

    fleet_size = max(
        safe_int(planned_fleet_size),
        0,
    )

    return (
        annual_insurance
        / 12
        * fleet_size
    )


def allocate_monthly_cost_per_shipment(
    monthly_cost_rm: float,
    shipments_per_month: int,
) -> float:
    """
    Allocate a monthly cost across monthly shipments.
    """

    monthly_cost = validate_positive(
        monthly_cost_rm,
        "Monthly cost",
        allow_zero=True,
    )

    shipment_count = safe_int(
        shipments_per_month
    )

    if shipment_count <= 0:
        raise ValueError(
            "Shipments per month must be greater "
            "than zero."
        )

    return monthly_cost / shipment_count


def calculate_operating_cost(
    fuel_cost_per_shipment: float,
    toll_cost_per_shipment: float,
    maintenance_cost_per_shipment: float,
    tyre_cost_per_shipment: float,
    overtime_cost_per_shipment: float,
    monthly_manpower_cost: float,
    monthly_financing_cost: float,
    monthly_insurance_cost: float,
    monthly_regional_overhead: float,
    shipments_per_month: int,
) -> dict[str, float]:
    """
    Calculate direct, allocated fixed and total operating cost.
    """

    shipment_count = safe_int(
        shipments_per_month
    )

    if shipment_count <= 0:
        raise ValueError(
            "Shipments per month must be greater "
            "than zero."
        )

    fuel_cost = max(
        safe_float(
            fuel_cost_per_shipment
        ),
        0,
    )

    toll_cost = max(
        safe_float(
            toll_cost_per_shipment
        ),
        0,
    )

    maintenance_cost = max(
        safe_float(
            maintenance_cost_per_shipment
        ),
        0,
    )

    tyre_cost = max(
        safe_float(
            tyre_cost_per_shipment
        ),
        0,
    )

    overtime_cost = max(
        safe_float(
            overtime_cost_per_shipment
        ),
        0,
    )

    direct_trip_cost = (
        fuel_cost
        + toll_cost
        + maintenance_cost
        + tyre_cost
        + overtime_cost
    )

    total_monthly_fixed_cost = (
        max(
            safe_float(monthly_manpower_cost),
            0,
        )
        + max(
            safe_float(monthly_financing_cost),
            0,
        )
        + max(
            safe_float(monthly_insurance_cost),
            0,
        )
        + max(
            safe_float(
                monthly_regional_overhead
            ),
            0,
        )
    )

    allocated_fixed_cost_per_shipment = (
        total_monthly_fixed_cost
        / shipment_count
    )

    total_operating_cost_per_shipment = (
        direct_trip_cost
        + allocated_fixed_cost_per_shipment
    )

    monthly_direct_operating_cost = (
        direct_trip_cost
        * shipment_count
    )

    total_monthly_operating_cost = (
        monthly_direct_operating_cost
        + total_monthly_fixed_cost
    )

    return {
        "direct_trip_cost": direct_trip_cost,
        "total_monthly_fixed_cost": (
            total_monthly_fixed_cost
        ),
        "allocated_fixed_cost_per_shipment": (
            allocated_fixed_cost_per_shipment
        ),
        "total_operating_cost_per_shipment": (
            total_operating_cost_per_shipment
        ),
        "monthly_direct_operating_cost": (
            monthly_direct_operating_cost
        ),
        "total_monthly_operating_cost": (
            total_monthly_operating_cost
        ),
    }


# =========================================================
# COST-PER-PARCEL CALCULATIONS
# =========================================================
def calculate_cost_per_parcel(
    direct_cost_per_shipment: float,
    fixed_cost_per_shipment: float,
    parcel_quantity: int,
    total_actual_weight_kg: float,
    chargeable_weight_kg: float,
    total_volume_m3: float,
    planned_fleet_size: int,
    total_trip_distance_km: float,
    shipments_per_month: int,
) -> dict[str, float]:
    """
    Calculate parcel, weight, volume and fleet unit costs.
    """

    quantity = safe_int(parcel_quantity)

    if quantity <= 0:
        raise ValueError(
            "Parcel quantity must be greater "
            "than zero."
        )

    actual_weight = validate_positive(
        total_actual_weight_kg,
        "Total actual weight",
    )

    chargeable_weight = validate_positive(
        chargeable_weight_kg,
        "Chargeable weight",
    )

    volume = validate_positive(
        total_volume_m3,
        "Total volume",
    )

    fleet_size = safe_int(
        planned_fleet_size
    )

    if fleet_size <= 0:
        raise ValueError(
            "Planned fleet size must be greater "
            "than zero."
        )

    distance = validate_positive(
        total_trip_distance_km,
        "Total trip distance",
    )

    shipment_count = safe_int(
        shipments_per_month
    )

    if shipment_count <= 0:
        raise ValueError(
            "Shipments per month must be greater "
            "than zero."
        )

    direct_cost = max(
        safe_float(
            direct_cost_per_shipment
        ),
        0,
    )

    fixed_cost = max(
        safe_float(
            fixed_cost_per_shipment
        ),
        0,
    )

    total_cost_per_shipment = (
        direct_cost
        + fixed_cost
    )

    direct_cost_per_parcel = (
        direct_cost / quantity
    )

    fixed_cost_per_parcel = (
        fixed_cost / quantity
    )

    total_cost_per_parcel = (
        total_cost_per_shipment
        / quantity
    )

    monthly_parcel_quantity = (
        quantity
        * shipment_count
    )

    total_monthly_operating_cost = (
        total_cost_per_shipment
        * shipment_count
    )

    direct_cost_share_pct = (
        direct_cost
        / total_cost_per_shipment
        * 100
        if total_cost_per_shipment > 0
        else 0
    )

    fixed_cost_share_pct = (
        fixed_cost
        / total_cost_per_shipment
        * 100
        if total_cost_per_shipment > 0
        else 0
    )

    return {
        "direct_cost_per_shipment": (
            direct_cost
        ),
        "fixed_cost_per_shipment": (
            fixed_cost
        ),
        "total_cost_per_shipment": (
            total_cost_per_shipment
        ),

        "direct_cost_per_parcel": (
            direct_cost_per_parcel
        ),
        "fixed_cost_per_parcel": (
            fixed_cost_per_parcel
        ),
        "total_cost_per_parcel": (
            total_cost_per_parcel
        ),

        "direct_cost_share_pct": (
            direct_cost_share_pct
        ),
        "fixed_cost_share_pct": (
            fixed_cost_share_pct
        ),

        "cost_per_actual_kg": (
            total_cost_per_shipment
            / actual_weight
        ),
        "cost_per_chargeable_kg": (
            total_cost_per_shipment
            / chargeable_weight
        ),
        "cost_per_cubic_metre": (
            total_cost_per_shipment
            / volume
        ),
        "cost_per_vehicle": (
            total_cost_per_shipment
            / fleet_size
        ),
        "cost_per_trip_km": (
            total_cost_per_shipment
            / distance
        ),
        "cost_per_vehicle_km": (
            total_cost_per_shipment
            / (
                distance
                * fleet_size
            )
        ),

        "monthly_parcel_quantity": (
            monthly_parcel_quantity
        ),
        "monthly_direct_cost_per_parcel": (
            direct_cost_per_parcel
        ),
        "monthly_fixed_cost_per_parcel": (
            fixed_cost_per_parcel
        ),
        "monthly_total_cost_per_parcel": (
            total_cost_per_parcel
        ),
        "total_monthly_operating_cost": (
            total_monthly_operating_cost
        ),
    }


def calculate_volume_sensitivity(
    total_cost_per_shipment: float,
    baseline_parcel_quantity: int,
    volume_change_pct: float,
) -> dict[str, float]:
    """
    Calculate cost-per-parcel sensitivity when parcel
    volume changes but shipment cost remains constant.
    """

    baseline_quantity = safe_int(
        baseline_parcel_quantity
    )

    if baseline_quantity <= 0:
        raise ValueError(
            "Baseline parcel quantity must be "
            "greater than zero."
        )

    shipment_cost = validate_positive(
        total_cost_per_shipment,
        "Total shipment cost",
    )

    adjusted_quantity = max(
        int(
            round(
                apply_percentage_change(
                    baseline_quantity,
                    volume_change_pct,
                )
            )
        ),
        1,
    )

    current_cost_per_parcel = (
        shipment_cost
        / baseline_quantity
    )

    adjusted_cost_per_parcel = (
        shipment_cost
        / adjusted_quantity
    )

    cost_change_per_parcel = (
        adjusted_cost_per_parcel
        - current_cost_per_parcel
    )

    cost_change_pct = percentage_change(
        current_cost_per_parcel,
        adjusted_cost_per_parcel,
    )

    return {
        "volume_adjustment_pct": (
            safe_float(volume_change_pct)
        ),
        "adjusted_parcel_quantity": (
            adjusted_quantity
        ),
        "current_cost_per_parcel": (
            current_cost_per_parcel
        ),
        "adjusted_cost_per_parcel": (
            adjusted_cost_per_parcel
        ),
        "cost_change_per_parcel": (
            cost_change_per_parcel
        ),
        "cost_change_pct": (
            cost_change_pct
        ),
    }


# =========================================================
# PROFITABILITY CALCULATIONS
# =========================================================
def calculate_price_from_markup(
    cost_per_parcel: float,
    markup_pct: float,
) -> float:
    """
    Calculate selling price using mark-up on cost.
    """

    cost = validate_positive(
        cost_per_parcel,
        "Cost per parcel",
    )

    return cost * (
        1
        + safe_float(markup_pct) / 100
    )


def calculate_price_for_target_margin(
    cost_per_parcel: float,
    target_margin_pct: float,
) -> float:
    """
    Calculate selling price required to achieve
    a target profit margin.

    Formula
    -------
    Price = Cost ÷ (1 - Margin)
    """

    cost = validate_positive(
        cost_per_parcel,
        "Cost per parcel",
    )

    margin_pct = safe_float(
        target_margin_pct
    )

    if margin_pct >= 100:
        raise ValueError(
            "Target profit margin must be below 100%."
        )

    margin_decimal = margin_pct / 100

    return cost / (
        1 - margin_decimal
    )


def calculate_net_selling_price(
    gross_price_per_parcel: float,
    discount_pct: float = 0,
    surcharge_pct: float = 0,
) -> dict[str, float]:
    """
    Apply discount followed by surcharge.

    The surcharge is applied after the discount.
    """

    gross_price = validate_positive(
        gross_price_per_parcel,
        "Gross selling price",
        allow_zero=True,
    )

    discount_rate = validate_positive(
        discount_pct,
        "Discount percentage",
        allow_zero=True,
    )

    surcharge_rate = validate_positive(
        surcharge_pct,
        "Surcharge percentage",
        allow_zero=True,
    )

    discount_amount = (
        gross_price
        * discount_rate
        / 100
    )

    price_after_discount = (
        gross_price
        - discount_amount
    )

    surcharge_amount = (
        price_after_discount
        * surcharge_rate
        / 100
    )

    net_price = (
        price_after_discount
        + surcharge_amount
    )

    return {
        "gross_price_per_parcel": (
            gross_price
        ),
        "discount_amount_per_parcel": (
            discount_amount
        ),
        "price_after_discount": (
            price_after_discount
        ),
        "surcharge_amount_per_parcel": (
            surcharge_amount
        ),
        "net_selling_price_per_parcel": (
            net_price
        ),
    }


def calculate_profitability(
    total_cost_per_parcel: float,
    parcel_quantity: int,
    shipments_per_month: int,
    net_selling_price_per_parcel: float,
    additional_fee_per_shipment: float = 0,
) -> dict[str, float]:
    """
    Calculate shipment and monthly profitability.
    """

    cost_per_parcel = validate_positive(
        total_cost_per_parcel,
        "Total cost per parcel",
    )

    quantity = safe_int(parcel_quantity)

    if quantity <= 0:
        raise ValueError(
            "Parcel quantity must be greater "
            "than zero."
        )

    shipment_count = safe_int(
        shipments_per_month
    )

    if shipment_count <= 0:
        raise ValueError(
            "Shipments per month must be greater "
            "than zero."
        )

    selling_price = validate_positive(
        net_selling_price_per_parcel,
        "Net selling price",
        allow_zero=True,
    )

    additional_fee = validate_positive(
        additional_fee_per_shipment,
        "Additional shipment fee",
        allow_zero=True,
    )

    total_cost_per_shipment = (
        cost_per_parcel
        * quantity
    )

    parcel_revenue_per_shipment = (
        selling_price
        * quantity
    )

    total_revenue_per_shipment = (
        parcel_revenue_per_shipment
        + additional_fee
    )

    profit_per_parcel = (
        selling_price
        - cost_per_parcel
    )

    profit_per_shipment = (
        total_revenue_per_shipment
        - total_cost_per_shipment
    )

    profit_margin_pct = (
        profit_per_shipment
        / total_revenue_per_shipment
        * 100
        if total_revenue_per_shipment > 0
        else 0
    )

    markup_on_cost_pct = (
        profit_per_shipment
        / total_cost_per_shipment
        * 100
        if total_cost_per_shipment > 0
        else 0
    )

    monthly_parcel_quantity = (
        quantity
        * shipment_count
    )

    monthly_revenue = (
        total_revenue_per_shipment
        * shipment_count
    )

    total_monthly_operating_cost = (
        total_cost_per_shipment
        * shipment_count
    )

    monthly_profit = (
        monthly_revenue
        - total_monthly_operating_cost
    )

    monthly_profit_margin_pct = (
        monthly_profit
        / monthly_revenue
        * 100
        if monthly_revenue > 0
        else 0
    )

    return {
        "total_cost_per_shipment": (
            total_cost_per_shipment
        ),
        "parcel_revenue_per_shipment": (
            parcel_revenue_per_shipment
        ),
        "total_revenue_per_shipment": (
            total_revenue_per_shipment
        ),
        "profit_per_parcel": (
            profit_per_parcel
        ),
        "profit_per_shipment": (
            profit_per_shipment
        ),
        "profit_margin_pct": (
            profit_margin_pct
        ),
        "markup_on_cost_pct": (
            markup_on_cost_pct
        ),
        "monthly_parcel_quantity": (
            monthly_parcel_quantity
        ),
        "monthly_revenue": (
            monthly_revenue
        ),
        "total_monthly_operating_cost": (
            total_monthly_operating_cost
        ),
        "monthly_profit": monthly_profit,
        "monthly_profit_margin_pct": (
            monthly_profit_margin_pct
        ),
    }


def calculate_break_even(
    total_cost_per_parcel: float,
    total_cost_per_shipment: float,
    net_selling_price_per_parcel: float,
    additional_fee_per_shipment: float = 0,
) -> dict[str, float | int]:
    """
    Calculate break-even price, revenue and parcel quantity.
    """

    cost_per_parcel = validate_positive(
        total_cost_per_parcel,
        "Total cost per parcel",
    )

    shipment_cost = validate_positive(
        total_cost_per_shipment,
        "Total cost per shipment",
    )

    selling_price = validate_positive(
        net_selling_price_per_parcel,
        "Net selling price",
        allow_zero=True,
    )

    additional_fee = validate_positive(
        additional_fee_per_shipment,
        "Additional shipment fee",
        allow_zero=True,
    )

    recoverable_cost_from_parcels = max(
        shipment_cost
        - additional_fee,
        0,
    )

    break_even_quantity = (
        math.ceil(
            recoverable_cost_from_parcels
            / selling_price
        )
        if selling_price > 0
        else 0
    )

    return {
        "break_even_price_per_parcel": (
            cost_per_parcel
        ),
        "break_even_revenue_per_shipment": (
            shipment_cost
        ),
        "break_even_parcel_quantity": (
            break_even_quantity
        ),
    }


def calculate_price_sensitivity(
    baseline_selling_price_per_parcel: float,
    parcel_quantity: int,
    total_cost_per_shipment: float,
    shipments_per_month: int,
    price_change_pct: float,
    additional_fee_per_shipment: float = 0,
) -> dict[str, float]:
    """
    Calculate profitability after changing the selling price.
    """

    adjusted_price = apply_percentage_change(
        baseline_selling_price_per_parcel,
        price_change_pct,
    )

    quantity = safe_int(parcel_quantity)
    shipment_count = safe_int(
        shipments_per_month
    )

    if quantity <= 0:
        raise ValueError(
            "Parcel quantity must be greater "
            "than zero."
        )

    if shipment_count <= 0:
        raise ValueError(
            "Shipments per month must be greater "
            "than zero."
        )

    shipment_cost = validate_positive(
        total_cost_per_shipment,
        "Total cost per shipment",
    )

    additional_fee = max(
        safe_float(
            additional_fee_per_shipment
        ),
        0,
    )

    adjusted_revenue_per_shipment = (
        adjusted_price
        * quantity
        + additional_fee
    )

    adjusted_profit_per_shipment = (
        adjusted_revenue_per_shipment
        - shipment_cost
    )

    adjusted_profit_margin_pct = (
        adjusted_profit_per_shipment
        / adjusted_revenue_per_shipment
        * 100
        if adjusted_revenue_per_shipment > 0
        else 0
    )

    adjusted_monthly_revenue = (
        adjusted_revenue_per_shipment
        * shipment_count
    )

    adjusted_monthly_profit = (
        adjusted_profit_per_shipment
        * shipment_count
    )

    return {
        "price_change_pct": (
            safe_float(price_change_pct)
        ),
        "adjusted_selling_price_per_parcel": (
            adjusted_price
        ),
        "adjusted_revenue_per_shipment": (
            adjusted_revenue_per_shipment
        ),
        "adjusted_profit_per_shipment": (
            adjusted_profit_per_shipment
        ),
        "adjusted_profit_margin_pct": (
            adjusted_profit_margin_pct
        ),
        "adjusted_monthly_revenue": (
            adjusted_monthly_revenue
        ),
        "adjusted_monthly_profit": (
            adjusted_monthly_profit
        ),
    }


# =========================================================
# CLASSIFICATION FUNCTIONS
# =========================================================
def classify_fleet_utilisation(
    utilisation_pct: float,
) -> dict[str, str]:
    """
    Classify overall fleet utilisation.
    """

    utilisation = safe_float(
        utilisation_pct
    )

    if utilisation >= 85:
        return {
            "status": "High Utilisation",
            "message": (
                "The fleet is highly utilised with "
                "limited spare operating capacity."
            ),
        }

    if utilisation >= 65:
        return {
            "status": "Efficient Utilisation",
            "message": (
                "The fleet has a reasonable balance "
                "between capacity usage and operational "
                "flexibility."
            ),
        }

    if utilisation >= 40:
        return {
            "status": "Moderate Utilisation",
            "message": (
                "The fleet has available capacity. "
                "Additional parcel consolidation may "
                "reduce unit cost."
            ),
        }

    return {
        "status": "Low Utilisation",
        "message": (
            "The fleet is underutilised. Review "
            "vehicle type, buffer requirement or "
            "shipment consolidation."
        ),
    }


def classify_profitability(
    profit_per_shipment: float,
    profit_margin_pct: float,
) -> dict[str, str]:
    """
    Classify service profitability.
    """

    profit = safe_float(
        profit_per_shipment
    )

    margin = safe_float(
        profit_margin_pct
    )

    if profit < 0:
        return {
            "status": "Loss-Making",
            "message": (
                "Revenue does not recover total "
                "operating cost."
            ),
        }

    if margin < 5:
        return {
            "status": "Low Margin",
            "message": (
                "The service is profitable, but the "
                "margin provides limited protection "
                "against cost increases."
            ),
        }

    if margin < 15:
        return {
            "status": "Moderate Margin",
            "message": (
                "The service is profitable with a "
                "moderate commercial margin."
            ),
        }

    if margin < 30:
        return {
            "status": "Healthy Margin",
            "message": (
                "The service generates a healthy "
                "profit margin under the selected "
                "assumptions."
            ),
        }

    return {
        "status": "High Margin",
        "message": (
            "The service generates a strong margin. "
            "Confirm that the selling price remains "
            "commercially competitive."
        ),
    }


def determine_management_recommendation(
    profit_per_shipment: float,
    profit_margin_pct: float,
    net_selling_price_per_parcel: float,
    break_even_price_per_parcel: float,
    fleet_shortfall: int = 0,
    parcel_standard_compliant: bool = True,
    overall_utilisation_pct: float = 0,
) -> dict[str, Any]:
    """
    Determine the high-level management recommendation.
    """

    critical_issues = []
    high_priority_issues = []

    if safe_float(profit_per_shipment) < 0:
        critical_issues.append(
            "The service is loss-making."
        )

    if (
        safe_float(
            net_selling_price_per_parcel
        )
        < safe_float(
            break_even_price_per_parcel
        )
    ):
        critical_issues.append(
            "The selling price is below break-even."
        )

    if safe_int(fleet_shortfall) > 0:
        critical_issues.append(
            "The planned fleet exceeds available capacity."
        )

    if not parcel_standard_compliant:
        high_priority_issues.append(
            "The parcel does not comply with the "
            "selected parcel standard."
        )

    utilisation = safe_float(
        overall_utilisation_pct
    )

    if utilisation < 40:
        high_priority_issues.append(
            "Fleet utilisation is low."
        )

    elif utilisation > 90:
        high_priority_issues.append(
            "Fleet utilisation is close to maximum capacity."
        )

    margin = safe_float(
        profit_margin_pct
    )

    if (
        safe_float(profit_per_shipment) >= 0
        and margin < 5
    ):
        high_priority_issues.append(
            "The profit margin is below 5%."
        )

    if critical_issues:
        recommendation = "Do Not Proceed"
        message = (
            "Resolve the critical commercial or "
            "operational issues before approval."
        )

    elif high_priority_issues:
        recommendation = "Proceed with Conditions"
        message = (
            "The service may proceed after the "
            "identified high-priority issues are "
            "addressed."
        )

    else:
        recommendation = "Proceed"
        message = (
            "The service is operationally feasible "
            "and commercially profitable under the "
            "selected assumptions."
        )

    return {
        "recommendation": recommendation,
        "message": message,
        "critical_issues": critical_issues,
        "high_priority_issues": (
            high_priority_issues
        ),
    }


# =========================================================
# SCENARIO CALCULATIONS
# =========================================================
def calculate_scenario(
    scenario_name: str,
    baseline_parcel_quantity: int,
    baseline_shipments_per_month: int,
    baseline_weight_per_parcel_kg: float,
    baseline_volume_per_parcel_m3: float,
    vehicle_max_parcels: int,
    vehicle_max_weight_kg: float,
    vehicle_max_volume_m3: float,
    baseline_planned_fleet_size: int,
    baseline_fuel_cost_per_shipment: float,
    baseline_toll_cost_per_shipment: float,
    baseline_other_direct_cost_per_shipment: float,
    baseline_monthly_fixed_cost: float,
    baseline_selling_price_per_parcel: float,
    additional_fee_per_shipment: float = 0,
    parcel_change_pct: float = 0,
    shipment_change_pct: float = 0,
    selling_price_change_pct: float = 0,
    fuel_cost_change_pct: float = 0,
    toll_cost_change_pct: float = 0,
    other_direct_cost_change_pct: float = 0,
    fixed_cost_change_pct: float = 0,
    operational_buffer_pct: float = 0,
) -> dict[str, Any]:
    """
    Calculate one complete operating scenario.
    """

    simulated_parcel_quantity = max(
        int(
            round(
                apply_percentage_change(
                    baseline_parcel_quantity,
                    parcel_change_pct,
                )
            )
        ),
        1,
    )

    simulated_shipments_per_month = max(
        int(
            round(
                apply_percentage_change(
                    baseline_shipments_per_month,
                    shipment_change_pct,
                )
            )
        ),
        1,
    )

    simulated_weight_kg = (
        safe_float(
            baseline_weight_per_parcel_kg
        )
        * simulated_parcel_quantity
    )

    simulated_volume_m3 = (
        safe_float(
            baseline_volume_per_parcel_m3
        )
        * simulated_parcel_quantity
    )

    fleet_result = calculate_fleet_capacity(
        parcel_quantity=(
            simulated_parcel_quantity
        ),
        total_actual_weight_kg=(
            simulated_weight_kg
        ),
        total_volume_m3=(
            simulated_volume_m3
        ),
        vehicle_max_parcels=(
            vehicle_max_parcels
        ),
        vehicle_max_weight_kg=(
            vehicle_max_weight_kg
        ),
        vehicle_max_volume_m3=(
            vehicle_max_volume_m3
        ),
        operational_buffer_pct=(
            operational_buffer_pct
        ),
    )

    simulated_planned_fleet = (
        fleet_result[
            "planned_fleet_size"
        ]
    )

    baseline_fleet = safe_int(
        baseline_planned_fleet_size
    )

    if baseline_fleet <= 0:
        raise ValueError(
            "Baseline planned fleet size must be "
            "greater than zero."
        )

    fleet_scaling_ratio = (
        simulated_planned_fleet
        / baseline_fleet
    )

    simulated_fuel_cost = (
        apply_percentage_change(
            baseline_fuel_cost_per_shipment,
            fuel_cost_change_pct,
        )
        * fleet_scaling_ratio
    )

    simulated_toll_cost = (
        apply_percentage_change(
            baseline_toll_cost_per_shipment,
            toll_cost_change_pct,
        )
        * fleet_scaling_ratio
    )

    simulated_other_direct_cost = (
        apply_percentage_change(
            baseline_other_direct_cost_per_shipment,
            other_direct_cost_change_pct,
        )
        * fleet_scaling_ratio
    )

    simulated_direct_cost_per_shipment = (
        simulated_fuel_cost
        + simulated_toll_cost
        + simulated_other_direct_cost
    )

    simulated_monthly_fixed_cost = (
        apply_percentage_change(
            baseline_monthly_fixed_cost,
            fixed_cost_change_pct,
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
        apply_percentage_change(
            baseline_selling_price_per_parcel,
            selling_price_change_pct,
        )
    )

    profitability_result = (
        calculate_profitability(
            total_cost_per_parcel=(
                simulated_cost_per_parcel
            ),
            parcel_quantity=(
                simulated_parcel_quantity
            ),
            shipments_per_month=(
                simulated_shipments_per_month
            ),
            net_selling_price_per_parcel=(
                simulated_selling_price_per_parcel
            ),
            additional_fee_per_shipment=(
                additional_fee_per_shipment
            ),
        )
    )

    break_even_result = calculate_break_even(
        total_cost_per_parcel=(
            simulated_cost_per_parcel
        ),
        total_cost_per_shipment=(
            simulated_total_cost_per_shipment
        ),
        net_selling_price_per_parcel=(
            simulated_selling_price_per_parcel
        ),
        additional_fee_per_shipment=(
            additional_fee_per_shipment
        ),
    )

    profitability_classification = (
        classify_profitability(
            profit_per_shipment=(
                profitability_result[
                    "profit_per_shipment"
                ]
            ),
            profit_margin_pct=(
                profitability_result[
                    "profit_margin_pct"
                ]
            ),
        )
    )

    return {
        "Scenario": scenario_name,

        "Parcel Change (%)": (
            safe_float(parcel_change_pct)
        ),
        "Shipment Change (%)": (
            safe_float(shipment_change_pct)
        ),
        "Price Change (%)": (
            safe_float(
                selling_price_change_pct
            )
        ),
        "Fuel Cost Change (%)": (
            safe_float(fuel_cost_change_pct)
        ),
        "Toll Cost Change (%)": (
            safe_float(toll_cost_change_pct)
        ),
        "Other Direct Cost Change (%)": (
            safe_float(
                other_direct_cost_change_pct
            )
        ),
        "Fixed Cost Change (%)": (
            safe_float(fixed_cost_change_pct)
        ),
        "Operational Buffer (%)": (
            safe_float(
                operational_buffer_pct
            )
        ),

        "Parcels per Shipment": (
            simulated_parcel_quantity
        ),
        "Shipments per Month": (
            simulated_shipments_per_month
        ),
        "Monthly Parcel Volume": (
            profitability_result[
                "monthly_parcel_quantity"
            ]
        ),

        "Shipment Weight (kg)": (
            simulated_weight_kg
        ),
        "Shipment Volume (m³)": (
            simulated_volume_m3
        ),

        "Vehicles by Parcel": (
            fleet_result[
                "vehicles_by_parcel"
            ]
        ),
        "Vehicles by Weight": (
            fleet_result[
                "vehicles_by_weight"
            ]
        ),
        "Vehicles by Volume": (
            fleet_result[
                "vehicles_by_volume"
            ]
        ),
        "Required Vehicles": (
            fleet_result[
                "required_vehicles"
            ]
        ),
        "Buffer Vehicles": (
            fleet_result[
                "additional_buffer_vehicles"
            ]
        ),
        "Planned Fleet Size": (
            simulated_planned_fleet
        ),
        "Capacity Constraint": (
            fleet_result[
                "capacity_constraint"
            ]
        ),
        "Fleet Utilisation (%)": (
            fleet_result[
                "overall_utilisation_pct"
            ]
        ),
        "Fleet Scaling Ratio": (
            fleet_scaling_ratio
        ),

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
            profitability_result[
                "total_revenue_per_shipment"
            ]
        ),
        "Profit per Shipment (RM)": (
            profitability_result[
                "profit_per_shipment"
            ]
        ),
        "Profit Margin (%)": (
            profitability_result[
                "profit_margin_pct"
            ]
        ),
        "Mark-up on Cost (%)": (
            profitability_result[
                "markup_on_cost_pct"
            ]
        ),

        "Monthly Revenue (RM)": (
            profitability_result[
                "monthly_revenue"
            ]
        ),
        "Monthly Cost (RM)": (
            profitability_result[
                "total_monthly_operating_cost"
            ]
        ),
        "Monthly Profit (RM)": (
            profitability_result[
                "monthly_profit"
            ]
        ),

        "Break-Even Price per Parcel (RM)": (
            break_even_result[
                "break_even_price_per_parcel"
            ]
        ),
        "Break-Even Parcel Quantity": (
            break_even_result[
                "break_even_parcel_quantity"
            ]
        ),

        "Scenario Status": (
            profitability_classification[
                "status"
            ]
        ),
        "Scenario Message": (
            profitability_classification[
                "message"
            ]
        ),
    }