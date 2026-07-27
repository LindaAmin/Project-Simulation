"""
Vehicle capacity, fleet sizing and utilisation calculations for the
Courier Cost Analysis application.

Responsibilities
----------------
- Vehicle-master record matching
- Vehicle availability filtering
- Vehicle capacity validation
- Fleet requirement by parcel quantity
- Fleet requirement by weight
- Fleet requirement by volume
- Operational buffer calculation
- Required and planned fleet sizing
- Capacity-constraint identification
- Fleet utilisation
- Fleet availability and shortfall
- Vehicle recommendation
- Fleet summary generation

This module must not contain:
- Streamlit widgets
- Streamlit session state
- CSV loading
- CSS
- Page navigation
- Operating-cost calculations
"""

from __future__ import annotations

import math
from typing import Any, Iterable

from utils.calculations import (
    safe_float,
    safe_int,
    validate_positive,
)

from utils.formatting import (
    normalise_region_name,
    normalise_vehicle_type,
)


# =========================================================
# VEHICLE CONSTANTS
# =========================================================
DEFAULT_OPERATIONAL_BUFFER_PCT = 0.0

ACTIVE_STATUS_VALUES = {
    "active",
    "available",
    "operational",
    "in service",
    "in-service",
    "yes",
    "y",
    "1",
    "true",
}

INACTIVE_STATUS_VALUES = {
    "inactive",
    "unavailable",
    "out of service",
    "out-of-service",
    "maintenance",
    "no",
    "n",
    "0",
    "false",
}


# =========================================================
# GENERAL VEHICLE HELPERS
# =========================================================
def clean_vehicle_text(
    value: Any,
    default: str = "",
) -> str:
    """
    Convert vehicle-related values into clean text.
    """

    if value is None:
        return default

    text = " ".join(
        str(value).split()
    )

    return text or default


def normalise_vehicle_status(
    status: Any,
) -> str:
    """
    Standardise vehicle status.

    Returns:
    - Active
    - Inactive
    - Unknown
    """

    status_text = clean_vehicle_text(
        status
    ).lower()

    if status_text in ACTIVE_STATUS_VALUES:
        return "Active"

    if status_text in INACTIVE_STATUS_VALUES:
        return "Inactive"

    return "Unknown"


def parse_region_availability(
    region_availability: Any,
) -> list[str]:
    """
    Convert a region-availability field into a clean region list.

    Supported examples:
    - "Northern"
    - "Northern, Central"
    - "Northern / Central"
    - "All"
    - ["Northern", "Central"]
    """

    if region_availability is None:
        return []

    if isinstance(
        region_availability,
        (
            list,
            tuple,
            set,
        ),
    ):
        raw_regions = list(
            region_availability
        )

    else:
        availability_text = clean_vehicle_text(
            region_availability
        )

        if not availability_text:
            return []

        separators = [
            ",",
            "/",
            ";",
            "|",
        ]

        for separator in separators:
            availability_text = (
                availability_text.replace(
                    separator,
                    ",",
                )
            )

        raw_regions = availability_text.split(
            ","
        )

    normalised_regions = []

    for raw_region in raw_regions:
        region_text = clean_vehicle_text(
            raw_region
        )

        if not region_text:
            continue

        if region_text.lower() in {
            "all",
            "all regions",
            "nationwide",
            "national",
        }:
            return ["All"]

        normalised_region = normalise_region_name(
            region_text
        )

        if (
            normalised_region
            and normalised_region
            not in normalised_regions
        ):
            normalised_regions.append(
                normalised_region
            )

    return normalised_regions


def is_vehicle_available_in_region(
    region_availability: Any,
    required_region: str,
) -> bool:
    """
    Check whether a vehicle is available in the required region.
    """

    available_regions = parse_region_availability(
        region_availability
    )

    if not available_regions:
        return False

    if "All" in available_regions:
        return True

    region = normalise_region_name(
        required_region
    )

    return region in available_regions


# =========================================================
# VEHICLE-MASTER RECORD NORMALISATION
# =========================================================
def normalise_vehicle_record(
    vehicle_record: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert a vehicle-master record into standard field names.

    Supported source columns:
    - Vehicle ID
    - Vehicle Type
    - Category
    - Fuel Type
    - Max Weight (kg)
    - Max Volume (m³)
    - Max Parcels
    - Avg Speed (km/h)
    - State
    - Region Availability
    - Average Parcel Per Item
    - Status
    """

    vehicle_id = clean_vehicle_text(
        vehicle_record.get(
            "Vehicle ID",
            vehicle_record.get(
                "vehicle_id",
                "",
            ),
        )
    )

    vehicle_type = normalise_vehicle_type(
        vehicle_record.get(
            "Vehicle Type",
            vehicle_record.get(
                "vehicle_type",
                "",
            ),
        )
    )

    category = clean_vehicle_text(
        vehicle_record.get(
            "Category",
            vehicle_record.get(
                "category",
                "",
            ),
        )
    )

    fuel_type = clean_vehicle_text(
        vehicle_record.get(
            "Fuel Type",
            vehicle_record.get(
                "fuel_type",
                "",
            ),
        )
    )

    max_weight_kg = safe_float(
        vehicle_record.get(
            "Max Weight (kg)",
            vehicle_record.get(
                "max_weight_kg",
                0,
            ),
        )
    )

    max_volume_m3 = safe_float(
        vehicle_record.get(
            "Max Volume (m³)",
            vehicle_record.get(
                "Max Volume (m3)",
                vehicle_record.get(
                    "max_volume_m3",
                    0,
                ),
            ),
        )
    )

    max_parcels = safe_int(
        vehicle_record.get(
            "Max Parcels",
            vehicle_record.get(
                "max_parcels",
                0,
            ),
        )
    )

    average_speed_kmh = safe_float(
        vehicle_record.get(
            "Avg Speed (km/h)",
            vehicle_record.get(
                "Average Speed (km/h)",
                vehicle_record.get(
                    "average_speed_kmh",
                    0,
                ),
            ),
        )
    )

    state = clean_vehicle_text(
        vehicle_record.get(
            "State",
            vehicle_record.get(
                "state",
                "",
            ),
        )
    )

    region_availability = (
        parse_region_availability(
            vehicle_record.get(
                "Region Availability",
                vehicle_record.get(
                    "region_availability",
                    "",
                ),
            )
        )
    )

    average_parcel_per_item = safe_float(
        vehicle_record.get(
            "Average Parcel Per Item",
            vehicle_record.get(
                "average_parcel_per_item",
                0,
            ),
        )
    )

    status = normalise_vehicle_status(
        vehicle_record.get(
            "Status",
            vehicle_record.get(
                "status",
                "",
            ),
        )
    )

    return {
        "vehicle_id": vehicle_id,
        "vehicle_type": vehicle_type,
        "category": category,
        "fuel_type": fuel_type,
        "max_weight_kg": max_weight_kg,
        "max_volume_m3": max_volume_m3,
        "max_parcels": max_parcels,
        "average_speed_kmh": average_speed_kmh,
        "state": state,
        "region_availability": (
            region_availability
        ),
        "average_parcel_per_item": (
            average_parcel_per_item
        ),
        "status": status,
        "source_record": vehicle_record.copy(),
    }


# =========================================================
# VEHICLE-MASTER FILTERING
# =========================================================
def find_vehicle_records(
    vehicle_records: Iterable[dict[str, Any]],
    vehicle_type: str | None = None,
    required_region: str | None = None,
    active_only: bool = True,
) -> list[dict[str, Any]]:
    """
    Return matching vehicle-master records.
    """

    selected_vehicle_type = (
        normalise_vehicle_type(
            vehicle_type
        )
        if vehicle_type
        else None
    )

    selected_region = (
        normalise_region_name(
            required_region
        )
        if required_region
        else None
    )

    matching_records = []

    for raw_record in vehicle_records:
        record = normalise_vehicle_record(
            raw_record
        )

        if (
            selected_vehicle_type
            and record["vehicle_type"]
            != selected_vehicle_type
        ):
            continue

        if (
            active_only
            and record["status"] == "Inactive"
        ):
            continue

        if (
            selected_region
            and not is_vehicle_available_in_region(
                record[
                    "region_availability"
                ],
                selected_region,
            )
        ):
            continue

        matching_records.append(
            record
        )

    return matching_records


def match_vehicle_record(
    vehicle_type: str,
    vehicle_records: Iterable[dict[str, Any]],
    required_region: str | None = None,
    active_only: bool = True,
) -> dict[str, Any] | None:
    """
    Return the first matching vehicle-master record.
    """

    matching_records = find_vehicle_records(
        vehicle_records=vehicle_records,
        vehicle_type=vehicle_type,
        required_region=required_region,
        active_only=active_only,
    )

    if not matching_records:
        return None

    return matching_records[0]


def get_available_vehicle_types(
    vehicle_records: Iterable[dict[str, Any]],
    required_region: str | None = None,
    active_only: bool = True,
) -> list[str]:
    """
    Return unique available vehicle types.
    """

    records = find_vehicle_records(
        vehicle_records=vehicle_records,
        required_region=required_region,
        active_only=active_only,
    )

    vehicle_types = []

    for record in records:
        vehicle_type = record[
            "vehicle_type"
        ]

        if (
            vehicle_type
            and vehicle_type
            not in vehicle_types
        ):
            vehicle_types.append(
                vehicle_type
            )

    return vehicle_types


# =========================================================
# CAPACITY VALIDATION
# =========================================================
def validate_vehicle_capacity(
    vehicle_max_parcels: int,
    vehicle_max_weight_kg: float,
    vehicle_max_volume_m3: float,
) -> dict[str, float | int]:
    """
    Validate a vehicle's parcel, weight and volume capacities.
    """

    max_parcels = safe_int(
        vehicle_max_parcels
    )

    if max_parcels <= 0:
        raise ValueError(
            "Vehicle maximum parcel capacity must be greater "
            "than zero."
        )

    max_weight = validate_positive(
        vehicle_max_weight_kg,
        "Vehicle maximum weight",
    )

    max_volume = validate_positive(
        vehicle_max_volume_m3,
        "Vehicle maximum volume",
    )

    return {
        "vehicle_max_parcels": (
            max_parcels
        ),
        "vehicle_max_weight_kg": (
            max_weight
        ),
        "vehicle_max_volume_m3": (
            max_volume
        ),
    }


# =========================================================
# FLEET REQUIREMENT BY CAPACITY
# =========================================================
def calculate_vehicles_by_parcel(
    parcel_quantity: int,
    vehicle_max_parcels: int,
) -> int:
    """
    Calculate vehicles required based on parcel quantity.

    Formula
    -------
    Vehicles by parcel =
        Ceiling(Parcel quantity ÷ Max parcels per vehicle)
    """

    quantity = safe_int(
        parcel_quantity
    )

    if quantity <= 0:
        raise ValueError(
            "Parcel quantity must be greater than zero."
        )

    max_parcels = safe_int(
        vehicle_max_parcels
    )

    if max_parcels <= 0:
        raise ValueError(
            "Vehicle maximum parcel capacity must be greater "
            "than zero."
        )

    return math.ceil(
        quantity
        / max_parcels
    )


def calculate_vehicles_by_weight(
    total_actual_weight_kg: float,
    vehicle_max_weight_kg: float,
) -> int:
    """
    Calculate vehicles required based on actual shipment weight.

    Formula
    -------
    Vehicles by weight =
        Ceiling(Total actual weight ÷ Max vehicle weight)
    """

    total_weight = validate_positive(
        total_actual_weight_kg,
        "Total actual shipment weight",
    )

    max_weight = validate_positive(
        vehicle_max_weight_kg,
        "Vehicle maximum weight",
    )

    return math.ceil(
        total_weight
        / max_weight
    )


def calculate_vehicles_by_volume(
    total_volume_m3: float,
    vehicle_max_volume_m3: float,
) -> int:
    """
    Calculate vehicles required based on shipment volume.

    Formula
    -------
    Vehicles by volume =
        Ceiling(Total volume ÷ Max vehicle volume)
    """

    total_volume = validate_positive(
        total_volume_m3,
        "Total shipment volume",
    )

    max_volume = validate_positive(
        vehicle_max_volume_m3,
        "Vehicle maximum volume",
    )

    return math.ceil(
        total_volume
        / max_volume
    )


# =========================================================
# CAPACITY CONSTRAINT
# =========================================================
def identify_capacity_constraint(
    vehicles_by_parcel: int,
    vehicles_by_weight: int,
    vehicles_by_volume: int,
) -> dict[str, Any]:
    """
    Identify the main capacity constraint.

    Multiple constraints may tie for the highest requirement.
    """

    requirements = {
        "Parcel Capacity": safe_int(
            vehicles_by_parcel
        ),
        "Weight Capacity": safe_int(
            vehicles_by_weight
        ),
        "Volume Capacity": safe_int(
            vehicles_by_volume
        ),
    }

    required_vehicles = max(
        requirements.values()
    )

    tied_constraints = [
        constraint
        for constraint, requirement
        in requirements.items()
        if requirement == required_vehicles
    ]

    if len(tied_constraints) == 1:
        primary_constraint = (
            tied_constraints[0]
        )

    else:
        primary_constraint = (
            " and ".join(
                tied_constraints
            )
        )

    return {
        "required_vehicles": (
            required_vehicles
        ),
        "capacity_constraint": (
            primary_constraint
        ),
        "capacity_constraints": (
            tied_constraints
        ),
        "multiple_constraints": (
            len(tied_constraints) > 1
        ),
    }


# =========================================================
# OPERATIONAL BUFFER
# =========================================================
def calculate_buffer_vehicles(
    required_vehicles: int,
    operational_buffer_pct: float = (
        DEFAULT_OPERATIONAL_BUFFER_PCT
    ),
) -> dict[str, float | int]:
    """
    Calculate additional vehicles required as an operating buffer.

    Formula
    -------
    Buffer vehicles =
        Ceiling(Required vehicles × Buffer percentage)

    Planned fleet =
        Required vehicles + Buffer vehicles
    """

    required = safe_int(
        required_vehicles
    )

    if required <= 0:
        raise ValueError(
            "Required vehicles must be greater than zero."
        )

    buffer_pct = validate_positive(
        operational_buffer_pct,
        "Operational buffer percentage",
        allow_zero=True,
    )

    buffer_decimal = (
        buffer_pct
        / 100
    )

    additional_buffer_vehicles = (
        math.ceil(
            required
            * buffer_decimal
        )
        if buffer_pct > 0
        else 0
    )

    planned_fleet_size = (
        required
        + additional_buffer_vehicles
    )

    return {
        "operational_buffer_pct": (
            buffer_pct
        ),
        "additional_buffer_vehicles": (
            additional_buffer_vehicles
        ),
        "planned_fleet_size": (
            planned_fleet_size
        ),
    }


# =========================================================
# UTILISATION CALCULATIONS
# =========================================================
def calculate_utilisation_pct(
    utilised_capacity: float,
    total_available_capacity: float,
) -> float:
    """
    Calculate capacity utilisation percentage.
    """

    utilised = validate_positive(
        utilised_capacity,
        "Utilised capacity",
        allow_zero=True,
    )

    available = validate_positive(
        total_available_capacity,
        "Available capacity",
    )

    return (
        utilised
        / available
        * 100
    )


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
    Calculate parcel, weight, volume and overall fleet utilisation.

    Overall utilisation is the highest utilisation percentage,
    because that represents the controlling capacity dimension.
    """

    quantity = safe_int(
        parcel_quantity
    )

    if quantity <= 0:
        raise ValueError(
            "Parcel quantity must be greater than zero."
        )

    total_weight = validate_positive(
        total_actual_weight_kg,
        "Total actual shipment weight",
    )

    total_volume = validate_positive(
        total_volume_m3,
        "Total shipment volume",
    )

    fleet_size = safe_int(
        planned_fleet_size
    )

    if fleet_size <= 0:
        raise ValueError(
            "Planned fleet size must be greater than zero."
        )

    capacity = validate_vehicle_capacity(
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

    total_parcel_capacity = (
        fleet_size
        * capacity[
            "vehicle_max_parcels"
        ]
    )

    total_weight_capacity_kg = (
        fleet_size
        * capacity[
            "vehicle_max_weight_kg"
        ]
    )

    total_volume_capacity_m3 = (
        fleet_size
        * capacity[
            "vehicle_max_volume_m3"
        ]
    )

    parcel_utilisation_pct = (
        calculate_utilisation_pct(
            utilised_capacity=quantity,
            total_available_capacity=(
                total_parcel_capacity
            ),
        )
    )

    weight_utilisation_pct = (
        calculate_utilisation_pct(
            utilised_capacity=(
                total_weight
            ),
            total_available_capacity=(
                total_weight_capacity_kg
            ),
        )
    )

    volume_utilisation_pct = (
        calculate_utilisation_pct(
            utilised_capacity=(
                total_volume
            ),
            total_available_capacity=(
                total_volume_capacity_m3
            ),
        )
    )

    overall_utilisation_pct = max(
        parcel_utilisation_pct,
        weight_utilisation_pct,
        volume_utilisation_pct,
    )

    available_parcel_capacity = max(
        total_parcel_capacity
        - quantity,
        0,
    )

    available_weight_capacity_kg = max(
        total_weight_capacity_kg
        - total_weight,
        0,
    )

    available_volume_capacity_m3 = max(
        total_volume_capacity_m3
        - total_volume,
        0,
    )

    return {
        "total_parcel_capacity": (
            total_parcel_capacity
        ),
        "total_weight_capacity_kg": (
            total_weight_capacity_kg
        ),
        "total_volume_capacity_m3": (
            total_volume_capacity_m3
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

        "available_parcel_capacity": (
            available_parcel_capacity
        ),
        "available_weight_capacity_kg": (
            available_weight_capacity_kg
        ),
        "available_volume_capacity_m3": (
            available_volume_capacity_m3
        ),
    }


# =========================================================
# UTILISATION CLASSIFICATION
# =========================================================
def classify_fleet_utilisation(
    overall_utilisation_pct: float,
) -> dict[str, str]:
    """
    Classify fleet utilisation for management interpretation.
    """

    utilisation = validate_positive(
        overall_utilisation_pct,
        "Overall fleet utilisation",
        allow_zero=True,
    )

    if utilisation > 100:
        return {
            "utilisation_status": "Over Capacity",
            "utilisation_status_type": "error",
            "utilisation_message": (
                "The planned fleet cannot accommodate the shipment. "
                "Increase the fleet size or select a larger vehicle."
            ),
        }

    if utilisation >= 90:
        return {
            "utilisation_status": "Very High",
            "utilisation_status_type": "warning",
            "utilisation_message": (
                "The fleet is operating close to its capacity limit. "
                "A small change in parcel volume may cause a shortfall."
            ),
        }

    if utilisation >= 70:
        return {
            "utilisation_status": "Efficient",
            "utilisation_status_type": "success",
            "utilisation_message": (
                "The planned fleet provides efficient use of capacity "
                "with a reasonable operating allowance."
            ),
        }

    if utilisation >= 50:
        return {
            "utilisation_status": "Moderate",
            "utilisation_status_type": "info",
            "utilisation_message": (
                "The fleet has moderate spare capacity and may support "
                "additional parcel volume."
            ),
        }

    return {
        "utilisation_status": "Low",
        "utilisation_status_type": "warning",
        "utilisation_message": (
            "The planned fleet has substantial unused capacity. "
            "Review vehicle type, fleet size or shipment consolidation."
        ),
    }


# =========================================================
# FLEET AVAILABILITY
# =========================================================
def assess_fleet_availability(
    planned_fleet_size: int,
    active_vehicle_count: int | None,
) -> dict[str, Any]:
    """
    Compare the planned fleet requirement with available vehicles.

    When active_vehicle_count is None, availability is not assessed.
    """

    planned_fleet = safe_int(
        planned_fleet_size
    )

    if planned_fleet <= 0:
        raise ValueError(
            "Planned fleet size must be greater than zero."
        )

    if active_vehicle_count is None:
        return {
            "active_vehicle_count": None,
            "fleet_shortfall": 0,
            "surplus_vehicles": 0,
            "fleet_available": None,
            "fleet_availability_status": (
                "Not Assessed"
            ),
        }

    available_fleet = max(
        safe_int(
            active_vehicle_count
        ),
        0,
    )

    fleet_shortfall = max(
        planned_fleet
        - available_fleet,
        0,
    )

    surplus_vehicles = max(
        available_fleet
        - planned_fleet,
        0,
    )

    fleet_available = (
        fleet_shortfall == 0
    )

    if fleet_available:
        fleet_availability_status = (
            "Available"
        )

    else:
        fleet_availability_status = (
            "Insufficient Fleet"
        )

    return {
        "active_vehicle_count": (
            available_fleet
        ),
        "fleet_shortfall": (
            fleet_shortfall
        ),
        "surplus_vehicles": (
            surplus_vehicles
        ),
        "fleet_available": (
            fleet_available
        ),
        "fleet_availability_status": (
            fleet_availability_status
        ),
    }


# =========================================================
# COMPLETE FLEET-CAPACITY CALCULATION
# =========================================================
def calculate_fleet_capacity(
    parcel_quantity: int,
    total_actual_weight_kg: float,
    total_volume_m3: float,
    vehicle_max_parcels: int,
    vehicle_max_weight_kg: float,
    vehicle_max_volume_m3: float,
    operational_buffer_pct: float = (
        DEFAULT_OPERATIONAL_BUFFER_PCT
    ),
    active_vehicle_count: int | None = None,
) -> dict[str, Any]:
    """
    Run the complete Page 4 fleet-capacity calculation.

    Important
    ---------
    Fleet sizing uses actual shipment weight, not chargeable weight.
    """

    quantity = safe_int(
        parcel_quantity
    )

    if quantity <= 0:
        raise ValueError(
            "Parcel quantity must be greater than zero."
        )

    total_weight = validate_positive(
        total_actual_weight_kg,
        "Total actual shipment weight",
    )

    total_volume = validate_positive(
        total_volume_m3,
        "Total shipment volume",
    )

    capacity = validate_vehicle_capacity(
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

    vehicles_by_parcel = (
        calculate_vehicles_by_parcel(
            parcel_quantity=quantity,
            vehicle_max_parcels=(
                capacity[
                    "vehicle_max_parcels"
                ]
            ),
        )
    )

    vehicles_by_weight = (
        calculate_vehicles_by_weight(
            total_actual_weight_kg=(
                total_weight
            ),
            vehicle_max_weight_kg=(
                capacity[
                    "vehicle_max_weight_kg"
                ]
            ),
        )
    )

    vehicles_by_volume = (
        calculate_vehicles_by_volume(
            total_volume_m3=(
                total_volume
            ),
            vehicle_max_volume_m3=(
                capacity[
                    "vehicle_max_volume_m3"
                ]
            ),
        )
    )

    constraint_result = (
        identify_capacity_constraint(
            vehicles_by_parcel=(
                vehicles_by_parcel
            ),
            vehicles_by_weight=(
                vehicles_by_weight
            ),
            vehicles_by_volume=(
                vehicles_by_volume
            ),
        )
    )

    buffer_result = (
        calculate_buffer_vehicles(
            required_vehicles=(
                constraint_result[
                    "required_vehicles"
                ]
            ),
            operational_buffer_pct=(
                operational_buffer_pct
            ),
        )
    )

    utilisation_result = (
        calculate_fleet_utilisation(
            parcel_quantity=quantity,
            total_actual_weight_kg=(
                total_weight
            ),
            total_volume_m3=(
                total_volume
            ),
            planned_fleet_size=(
                buffer_result[
                    "planned_fleet_size"
                ]
            ),
            vehicle_max_parcels=(
                capacity[
                    "vehicle_max_parcels"
                ]
            ),
            vehicle_max_weight_kg=(
                capacity[
                    "vehicle_max_weight_kg"
                ]
            ),
            vehicle_max_volume_m3=(
                capacity[
                    "vehicle_max_volume_m3"
                ]
            ),
        )
    )

    utilisation_status = (
        classify_fleet_utilisation(
            overall_utilisation_pct=(
                utilisation_result[
                    "overall_utilisation_pct"
                ]
            )
        )
    )

    availability_result = (
        assess_fleet_availability(
            planned_fleet_size=(
                buffer_result[
                    "planned_fleet_size"
                ]
            ),
            active_vehicle_count=(
                active_vehicle_count
            ),
        )
    )

    return {
        "parcel_quantity": quantity,
        "total_actual_weight_kg": (
            total_weight
        ),
        "total_volume_m3": (
            total_volume
        ),

        **capacity,

        "vehicles_by_parcel": (
            vehicles_by_parcel
        ),
        "vehicles_by_weight": (
            vehicles_by_weight
        ),
        "vehicles_by_volume": (
            vehicles_by_volume
        ),

        **constraint_result,
        **buffer_result,
        **utilisation_result,
        **utilisation_status,
        **availability_result,
    }


# =========================================================
# VEHICLE CAPACITY FIT
# =========================================================
def assess_vehicle_capacity_fit(
    parcel_quantity: int,
    total_actual_weight_kg: float,
    total_volume_m3: float,
    vehicle_record: dict[str, Any],
    operational_buffer_pct: float = (
        DEFAULT_OPERATIONAL_BUFFER_PCT
    ),
    active_vehicle_count: int | None = None,
) -> dict[str, Any]:
    """
    Assess one vehicle type against the shipment.
    """

    vehicle = normalise_vehicle_record(
        vehicle_record
    )

    if not vehicle["vehicle_type"]:
        raise ValueError(
            "Vehicle type is missing from the vehicle record."
        )

    fleet_result = calculate_fleet_capacity(
        parcel_quantity=parcel_quantity,
        total_actual_weight_kg=(
            total_actual_weight_kg
        ),
        total_volume_m3=total_volume_m3,
        vehicle_max_parcels=(
            vehicle["max_parcels"]
        ),
        vehicle_max_weight_kg=(
            vehicle["max_weight_kg"]
        ),
        vehicle_max_volume_m3=(
            vehicle["max_volume_m3"]
        ),
        operational_buffer_pct=(
            operational_buffer_pct
        ),
        active_vehicle_count=(
            active_vehicle_count
        ),
    )

    return {
        **vehicle,
        **fleet_result,
    }


# =========================================================
# VEHICLE RECOMMENDATION
# =========================================================
def score_vehicle_option(
    fleet_result: dict[str, Any],
    preferred_vehicle_type: str | None = None,
) -> float:
    """
    Create a comparison score for a vehicle option.

    Lower score is better.

    The score prioritises:
    1. No fleet shortfall
    2. Fewer planned vehicles
    3. Higher useful utilisation
    4. Preferred route vehicle
    """

    planned_fleet_size = safe_int(
        fleet_result.get(
            "planned_fleet_size",
            0,
        )
    )

    fleet_shortfall = safe_int(
        fleet_result.get(
            "fleet_shortfall",
            0,
        )
    )

    utilisation_pct = safe_float(
        fleet_result.get(
            "overall_utilisation_pct",
            0,
        )
    )

    vehicle_type = normalise_vehicle_type(
        fleet_result.get(
            "vehicle_type",
            "",
        )
    )

    preferred_vehicle = (
        normalise_vehicle_type(
            preferred_vehicle_type
        )
        if preferred_vehicle_type
        else ""
    )

    shortfall_penalty = (
        fleet_shortfall
        * 10_000
    )

    fleet_size_penalty = (
        planned_fleet_size
        * 100
    )

    if utilisation_pct > 100:
        utilisation_penalty = 10_000

    elif utilisation_pct >= 70:
        utilisation_penalty = (
            100
            - utilisation_pct
        )

    else:
        utilisation_penalty = (
            100
            - utilisation_pct
        ) * 2

    preferred_vehicle_adjustment = (
        -25
        if (
            preferred_vehicle
            and vehicle_type
            == preferred_vehicle
        )
        else 0
    )

    return (
        shortfall_penalty
        + fleet_size_penalty
        + utilisation_penalty
        + preferred_vehicle_adjustment
    )


def recommend_vehicle(
    parcel_quantity: int,
    total_actual_weight_kg: float,
    total_volume_m3: float,
    vehicle_records: Iterable[dict[str, Any]],
    required_region: str | None = None,
    feasible_vehicle_types: Iterable[str] | None = None,
    preferred_vehicle_type: str | None = None,
    operational_buffer_pct: float = (
        DEFAULT_OPERATIONAL_BUFFER_PCT
    ),
    active_vehicle_counts: dict[str, int] | None = None,
) -> dict[str, Any]:
    """
    Assess available vehicle types and recommend the best option.

    Parameters
    ----------
    feasible_vehicle_types:
        Optional route-approved vehicle types.

    active_vehicle_counts:
        Optional mapping such as:
        {
            "Motorcycle": 20,
            "Van": 8,
            "1-Ton Lorry": 4
        }
    """

    allowed_vehicle_types = None

    if feasible_vehicle_types is not None:
        allowed_vehicle_types = {
            normalise_vehicle_type(
                vehicle
            )
            for vehicle in feasible_vehicle_types
            if clean_vehicle_text(
                vehicle
            )
        }

    available_records = find_vehicle_records(
        vehicle_records=vehicle_records,
        required_region=required_region,
        active_only=True,
    )

    assessment_results = []

    for vehicle_record in available_records:
        vehicle_type = vehicle_record[
            "vehicle_type"
        ]

        if (
            allowed_vehicle_types is not None
            and vehicle_type
            not in allowed_vehicle_types
        ):
            continue

        active_count = None

        if active_vehicle_counts:
            active_count = (
                active_vehicle_counts.get(
                    vehicle_type
                )
            )

        assessment = assess_vehicle_capacity_fit(
            parcel_quantity=parcel_quantity,
            total_actual_weight_kg=(
                total_actual_weight_kg
            ),
            total_volume_m3=total_volume_m3,
            vehicle_record=vehicle_record[
                "source_record"
            ],
            operational_buffer_pct=(
                operational_buffer_pct
            ),
            active_vehicle_count=active_count,
        )

        assessment[
            "recommendation_score"
        ] = score_vehicle_option(
            fleet_result=assessment,
            preferred_vehicle_type=(
                preferred_vehicle_type
            ),
        )

        assessment_results.append(
            assessment
        )

    if not assessment_results:
        return {
            "recommended_vehicle_type": "",
            "recommended_vehicle_id": "",
            "recommendation_status": (
                "No Suitable Vehicle"
            ),
            "recommendation_message": (
                "No active vehicle record matched the selected "
                "region and route requirements."
            ),
            "vehicle_assessments": [],
        }

    assessment_results.sort(
        key=lambda record: (
            record[
                "recommendation_score"
            ],
            record[
                "planned_fleet_size"
            ],
            -record[
                "overall_utilisation_pct"
            ],
        )
    )

    recommended = (
        assessment_results[0]
    )

    return {
        "recommended_vehicle_type": (
            recommended[
                "vehicle_type"
            ]
        ),
        "recommended_vehicle_id": (
            recommended[
                "vehicle_id"
            ]
        ),
        "recommendation_status": (
            "Recommended"
        ),
        "recommendation_message": (
            f'{recommended["vehicle_type"]} provides the best '
            "available capacity fit under the selected route "
            "and fleet assumptions."
        ),
        "recommended_vehicle": (
            recommended
        ),
        "vehicle_assessments": (
            assessment_results
        ),
    }


# =========================================================
# SELECTED-VEHICLE ASSESSMENT
# =========================================================
def calculate_selected_vehicle_fleet(
    selected_vehicle_type: str,
    vehicle_records: Iterable[dict[str, Any]],
    parcel_quantity: int,
    total_actual_weight_kg: float,
    total_volume_m3: float,
    required_region: str | None = None,
    operational_buffer_pct: float = (
        DEFAULT_OPERATIONAL_BUFFER_PCT
    ),
    active_vehicle_count: int | None = None,
) -> dict[str, Any]:
    """
    Match a selected vehicle and calculate its fleet requirement.
    """

    vehicle_record = match_vehicle_record(
        vehicle_type=selected_vehicle_type,
        vehicle_records=vehicle_records,
        required_region=required_region,
        active_only=True,
    )

    if vehicle_record is None:
        raise ValueError(
            "The selected vehicle type is not available in the "
            "required region or is not active."
        )

    fleet_result = assess_vehicle_capacity_fit(
        parcel_quantity=parcel_quantity,
        total_actual_weight_kg=(
            total_actual_weight_kg
        ),
        total_volume_m3=total_volume_m3,
        vehicle_record=vehicle_record[
            "source_record"
        ],
        operational_buffer_pct=(
            operational_buffer_pct
        ),
        active_vehicle_count=(
            active_vehicle_count
        ),
    )

    return {
        "selected_vehicle_type": (
            vehicle_record[
                "vehicle_type"
            ]
        ),
        "selected_vehicle_id": (
            vehicle_record[
                "vehicle_id"
            ]
        ),
        **fleet_result,
    }


# =========================================================
# FLEET COMPARISON TABLE
# =========================================================
def create_vehicle_comparison_records(
    vehicle_assessments: Iterable[
        dict[str, Any]
    ],
) -> list[dict[str, Any]]:
    """
    Create concise vehicle-comparison records for Page 4.
    """

    comparison_records = []

    for assessment in vehicle_assessments:
        comparison_records.append(
            {
                "Vehicle ID": assessment.get(
                    "vehicle_id",
                    "",
                ),
                "Vehicle Type": assessment.get(
                    "vehicle_type",
                    "",
                ),
                "Max Parcels": safe_int(
                    assessment.get(
                        "vehicle_max_parcels",
                        assessment.get(
                            "max_parcels",
                            0,
                        ),
                    )
                ),
                "Max Weight (kg)": safe_float(
                    assessment.get(
                        "vehicle_max_weight_kg",
                        assessment.get(
                            "max_weight_kg",
                            0,
                        ),
                    )
                ),
                "Max Volume (m³)": safe_float(
                    assessment.get(
                        "vehicle_max_volume_m3",
                        assessment.get(
                            "max_volume_m3",
                            0,
                        ),
                    )
                ),
                "Vehicles by Parcel": safe_int(
                    assessment.get(
                        "vehicles_by_parcel",
                        0,
                    )
                ),
                "Vehicles by Weight": safe_int(
                    assessment.get(
                        "vehicles_by_weight",
                        0,
                    )
                ),
                "Vehicles by Volume": safe_int(
                    assessment.get(
                        "vehicles_by_volume",
                        0,
                    )
                ),
                "Required Vehicles": safe_int(
                    assessment.get(
                        "required_vehicles",
                        0,
                    )
                ),
                "Buffer Vehicles": safe_int(
                    assessment.get(
                        "additional_buffer_vehicles",
                        0,
                    )
                ),
                "Planned Fleet Size": safe_int(
                    assessment.get(
                        "planned_fleet_size",
                        0,
                    )
                ),
                "Capacity Constraint": (
                    assessment.get(
                        "capacity_constraint",
                        "",
                    )
                ),
                "Overall Utilisation (%)": (
                    safe_float(
                        assessment.get(
                            "overall_utilisation_pct",
                            0,
                        )
                    )
                ),
                "Fleet Availability": (
                    assessment.get(
                        "fleet_availability_status",
                        "",
                    )
                ),
                "Fleet Shortfall": safe_int(
                    assessment.get(
                        "fleet_shortfall",
                        0,
                    )
                ),
                "Recommendation Score": (
                    safe_float(
                        assessment.get(
                            "recommendation_score",
                            0,
                        )
                    )
                ),
            }
        )

    return comparison_records


# =========================================================
# FLEET SUMMARY
# =========================================================
def create_fleet_summary(
    fleet_capacity: dict[str, Any],
) -> dict[str, Any]:
    """
    Create a concise fleet summary for reports and dashboards.
    """

    return {
        "Vehicle ID": fleet_capacity.get(
            "vehicle_id",
            fleet_capacity.get(
                "selected_vehicle_id",
                "",
            ),
        ),
        "Vehicle Type": fleet_capacity.get(
            "vehicle_type",
            fleet_capacity.get(
                "selected_vehicle_type",
                fleet_capacity.get(
                    "recommended_vehicle_type",
                    "",
                ),
            ),
        ),
        "Vehicle Category": fleet_capacity.get(
            "category",
            "",
        ),
        "Fuel Type": fleet_capacity.get(
            "fuel_type",
            "",
        ),

        "Parcel Quantity": safe_int(
            fleet_capacity.get(
                "parcel_quantity",
                0,
            )
        ),
        "Total Actual Weight (kg)": (
            safe_float(
                fleet_capacity.get(
                    "total_actual_weight_kg",
                    0,
                )
            )
        ),
        "Total Volume (m³)": safe_float(
            fleet_capacity.get(
                "total_volume_m3",
                0,
            )
        ),

        "Vehicles by Parcel": safe_int(
            fleet_capacity.get(
                "vehicles_by_parcel",
                0,
            )
        ),
        "Vehicles by Weight": safe_int(
            fleet_capacity.get(
                "vehicles_by_weight",
                0,
            )
        ),
        "Vehicles by Volume": safe_int(
            fleet_capacity.get(
                "vehicles_by_volume",
                0,
            )
        ),

        "Required Vehicles": safe_int(
            fleet_capacity.get(
                "required_vehicles",
                0,
            )
        ),
        "Buffer Vehicles": safe_int(
            fleet_capacity.get(
                "additional_buffer_vehicles",
                0,
            )
        ),
        "Planned Fleet Size": safe_int(
            fleet_capacity.get(
                "planned_fleet_size",
                0,
            )
        ),

        "Capacity Constraint": (
            fleet_capacity.get(
                "capacity_constraint",
                "",
            )
        ),

        "Parcel Utilisation (%)": (
            safe_float(
                fleet_capacity.get(
                    "parcel_utilisation_pct",
                    0,
                )
            )
        ),
        "Weight Utilisation (%)": (
            safe_float(
                fleet_capacity.get(
                    "weight_utilisation_pct",
                    0,
                )
            )
        ),
        "Volume Utilisation (%)": (
            safe_float(
                fleet_capacity.get(
                    "volume_utilisation_pct",
                    0,
                )
            )
        ),
        "Overall Utilisation (%)": (
            safe_float(
                fleet_capacity.get(
                    "overall_utilisation_pct",
                    0,
                )
            )
        ),

        "Utilisation Status": (
            fleet_capacity.get(
                "utilisation_status",
                "",
            )
        ),
        "Fleet Availability": (
            fleet_capacity.get(
                "fleet_availability_status",
                "",
            )
        ),
        "Fleet Shortfall": safe_int(
            fleet_capacity.get(
                "fleet_shortfall",
                0,
            )
        ),
        "Surplus Vehicles": safe_int(
            fleet_capacity.get(
                "surplus_vehicles",
                0,
            )
        ),
    }