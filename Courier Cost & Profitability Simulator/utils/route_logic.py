"""
Route intelligence and journey calculations for the
Courier Cost Analysis application.

Responsibilities
----------------
- Route identification
- Region and state matching
- Route-category classification
- One-way and return-trip distance
- Estimated driving time
- Loading and unloading time
- Total journey time
- Delivery-feasibility assessment
- Vehicle recommendation support
- Route summary generation

This module must not contain:
- Streamlit widgets
- Streamlit session state
- CSV loading
- CSS
- Page navigation
"""

from __future__ import annotations

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
# ROUTE CONSTANTS
# =========================================================
DEFAULT_DISTANCE_MULTIPLIER_ONE_WAY = 1.0
DEFAULT_DISTANCE_MULTIPLIER_RETURN = 2.0

DEFAULT_LOADING_UNLOADING_HOURS = 1.0

PENINSULAR_REGIONS = {
    "Northern",
    "Central",
    "Southern",
    "East Coast",
}

EAST_MALAYSIA_REGIONS = {
    "Sabah",
    "Sarawak",
}


# =========================================================
# GENERAL TEXT HELPERS
# =========================================================
def clean_route_text(
    value: Any,
    default: str = "",
) -> str:
    """
    Convert route-related values into clean text.
    """

    if value is None:
        return default

    text = " ".join(
        str(value).split()
    )

    return text or default


def normalise_service_level(
    service_level: Any,
) -> str:
    """
    Standardise service-level names.

    Supported examples:
    - Normal
    - Fast
    - Express
    - Same Day
    - Next Day
    """

    service = clean_route_text(
        service_level
    ).lower()

    service_mapping = {
        "normal": "Normal",
        "standard": "Normal",
        "regular": "Normal",

        "fast": "Fast",
        "express": "Fast",
        "expedited": "Fast",

        "same day": "Same Day",
        "same-day": "Same Day",
        "sameday": "Same Day",

        "next day": "Next Day",
        "next-day": "Next Day",
        "nextday": "Next Day",
    }

    return service_mapping.get(
        service,
        clean_route_text(
            service_level
        ).title(),
    )


# =========================================================
# REGION AND STATE MATCHING
# =========================================================
def get_state_region(
    state_name: str,
    state_records: Iterable[dict[str, Any]],
) -> str:
    """
    Find the region assigned to a state.

    Expected possible keys:
    - State
    - State Name
    - Region
    """

    target_state = clean_route_text(
        state_name
    ).lower()

    if not target_state:
        return ""

    for record in state_records:
        record_state = clean_route_text(
            record.get(
                "State",
                record.get(
                    "State Name",
                    "",
                ),
            )
        ).lower()

        if record_state == target_state:
            return normalise_region_name(
                record.get(
                    "Region",
                    "",
                )
            )

    return ""


def validate_state_region_pair(
    state_name: str,
    region_name: str,
    state_records: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    """
    Check whether a state belongs to the selected region.
    """

    expected_region = get_state_region(
        state_name=state_name,
        state_records=state_records,
    )

    selected_region = normalise_region_name(
        region_name
    )

    is_valid = (
        bool(expected_region)
        and expected_region == selected_region
    )

    return {
        "state": clean_route_text(
            state_name
        ),
        "selected_region": selected_region,
        "expected_region": expected_region,
        "is_valid": is_valid,
        "validation_status": (
            "Valid"
            if is_valid
            else "Invalid"
        ),
    }


# =========================================================
# ROUTE CATEGORY
# =========================================================
def classify_route_category(
    origin_region: str,
    destination_region: str,
) -> str:
    """
    Classify a route based on origin and destination regions.

    Possible outputs:
    - Intra-Region
    - Inter-Region
    - Peninsular to Sabah
    - Peninsular to Sarawak
    - Sabah to Peninsular
    - Sarawak to Peninsular
    - Sabah to Sarawak
    - Sarawak to Sabah
    - East Malaysia Domestic
    """

    origin = normalise_region_name(
        origin_region
    )

    destination = normalise_region_name(
        destination_region
    )

    if not origin or not destination:
        return "Unclassified"

    if origin == destination:
        return "Intra-Region"

    if (
        origin in PENINSULAR_REGIONS
        and destination in PENINSULAR_REGIONS
    ):
        return "Inter-Region"

    if (
        origin in PENINSULAR_REGIONS
        and destination == "Sabah"
    ):
        return "Peninsular to Sabah"

    if (
        origin in PENINSULAR_REGIONS
        and destination == "Sarawak"
    ):
        return "Peninsular to Sarawak"

    if (
        origin == "Sabah"
        and destination in PENINSULAR_REGIONS
    ):
        return "Sabah to Peninsular"

    if (
        origin == "Sarawak"
        and destination in PENINSULAR_REGIONS
    ):
        return "Sarawak to Peninsular"

    if (
        origin == "Sabah"
        and destination == "Sarawak"
    ):
        return "Sabah to Sarawak"

    if (
        origin == "Sarawak"
        and destination == "Sabah"
    ):
        return "Sarawak to Sabah"

    if (
        origin in EAST_MALAYSIA_REGIONS
        and destination in EAST_MALAYSIA_REGIONS
    ):
        return "East Malaysia Domestic"

    return "Other Route"


def identify_geographical_scope(
    origin_region: str,
    destination_region: str,
) -> str:
    """
    Identify the broad geographical scope.

    Possible outputs:
    - Peninsular
    - Sabah
    - Sarawak
    - Cross-Region
    """

    origin = normalise_region_name(
        origin_region
    )

    destination = normalise_region_name(
        destination_region
    )

    if (
        origin in PENINSULAR_REGIONS
        and destination in PENINSULAR_REGIONS
    ):
        return "Peninsular"

    if origin == "Sabah" and destination == "Sabah":
        return "Sabah"

    if origin == "Sarawak" and destination == "Sarawak":
        return "Sarawak"

    return "Cross-Region"


# =========================================================
# ROUTE RECORD MATCHING
# =========================================================
def match_route_record(
    origin_region: str,
    destination_region: str,
    service_level: str,
    route_records: Iterable[dict[str, Any]],
    vehicle_type: str | None = None,
) -> dict[str, Any] | None:
    """
    Find the best route-master record.

    Expected possible keys:
    - Route ID
    - Origin Region
    - Destination Region
    - Vehicle Type
    - Service Level
    - Target Delivery (Days)
    - Priority
    """

    origin = normalise_region_name(
        origin_region
    )

    destination = normalise_region_name(
        destination_region
    )

    service = normalise_service_level(
        service_level
    )

    selected_vehicle = (
        normalise_vehicle_type(vehicle_type)
        if vehicle_type
        else None
    )

    matching_records = []

    for record in route_records:
        record_origin = normalise_region_name(
            record.get(
                "Origin Region",
                "",
            )
        )

        record_destination = normalise_region_name(
            record.get(
                "Destination Region",
                "",
            )
        )

        record_service = normalise_service_level(
            record.get(
                "Service Level",
                "",
            )
        )

        record_vehicle = normalise_vehicle_type(
            record.get(
                "Vehicle Type",
                "",
            )
        )

        if (
            record_origin == origin
            and record_destination == destination
            and record_service == service
        ):
            if (
                selected_vehicle is None
                or record_vehicle == selected_vehicle
            ):
                matching_records.append(
                    record
                )

    if not matching_records:
        return None

    matching_records.sort(
        key=lambda record: safe_int(
            record.get(
                "Priority",
                999,
            ),
            default=999,
        )
    )

    return matching_records[0].copy()


def find_feasible_route_records(
    origin_region: str,
    destination_region: str,
    service_level: str,
    route_records: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Return all matching route records ordered by priority.
    """

    origin = normalise_region_name(
        origin_region
    )

    destination = normalise_region_name(
        destination_region
    )

    service = normalise_service_level(
        service_level
    )

    matching_records = []

    for record in route_records:
        if (
            normalise_region_name(
                record.get(
                    "Origin Region",
                    "",
                )
            )
            == origin
            and normalise_region_name(
                record.get(
                    "Destination Region",
                    "",
                )
            )
            == destination
            and normalise_service_level(
                record.get(
                    "Service Level",
                    "",
                )
            )
            == service
        ):
            matching_records.append(
                record.copy()
            )

    matching_records.sort(
        key=lambda record: safe_int(
            record.get(
                "Priority",
                999,
            ),
            default=999,
        )
    )

    return matching_records


def get_feasible_vehicle_types(
    origin_region: str,
    destination_region: str,
    service_level: str,
    route_records: Iterable[dict[str, Any]],
) -> list[str]:
    """
    Return unique feasible vehicle types for a route.
    """

    matching_records = find_feasible_route_records(
        origin_region=origin_region,
        destination_region=destination_region,
        service_level=service_level,
        route_records=route_records,
    )

    vehicle_types = []

    for record in matching_records:
        vehicle = normalise_vehicle_type(
            record.get(
                "Vehicle Type",
                "",
            )
        )

        if (
            vehicle
            and vehicle not in vehicle_types
        ):
            vehicle_types.append(
                vehicle
            )

    return vehicle_types


def recommend_preferred_vehicle(
    origin_region: str,
    destination_region: str,
    service_level: str,
    route_records: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    """
    Recommend the highest-priority vehicle from route records.
    """

    matching_records = find_feasible_route_records(
        origin_region=origin_region,
        destination_region=destination_region,
        service_level=service_level,
        route_records=route_records,
    )

    if not matching_records:
        return {
            "preferred_vehicle_type": "",
            "priority": None,
            "route_id": "",
            "recommendation_status": (
                "No Matching Route"
            ),
        }

    preferred_record = matching_records[0]

    return {
        "preferred_vehicle_type": (
            normalise_vehicle_type(
                preferred_record.get(
                    "Vehicle Type",
                    "",
                )
            )
        ),
        "priority": safe_int(
            preferred_record.get(
                "Priority",
                0,
            )
        ),
        "route_id": clean_route_text(
            preferred_record.get(
                "Route ID",
                "",
            )
        ),
        "recommendation_status": (
            "Recommended"
        ),
    }


# =========================================================
# DISTANCE CALCULATIONS
# =========================================================
def calculate_distance_multiplier(
    return_trip_required: bool,
    custom_multiplier: float | None = None,
) -> float:
    """
    Determine the journey-distance multiplier.

    Default:
    - One-way only: 1.0
    - Return trip: 2.0
    """

    if custom_multiplier is not None:
        return validate_positive(
            custom_multiplier,
            "Distance multiplier",
        )

    if return_trip_required:
        return DEFAULT_DISTANCE_MULTIPLIER_RETURN

    return DEFAULT_DISTANCE_MULTIPLIER_ONE_WAY


def calculate_total_trip_distance(
    estimated_one_way_distance_km: float,
    return_trip_required: bool = True,
    distance_multiplier: float | None = None,
) -> dict[str, float | bool]:
    """
    Calculate total trip distance.

    Formula
    -------
    Total trip distance =
        One-way distance × Distance multiplier
    """

    one_way_distance = validate_positive(
        estimated_one_way_distance_km,
        "Estimated one-way distance",
    )

    multiplier = calculate_distance_multiplier(
        return_trip_required=(
            return_trip_required
        ),
        custom_multiplier=(
            distance_multiplier
        ),
    )

    total_trip_distance = (
        one_way_distance
        * multiplier
    )

    return {
        "estimated_one_way_distance_km": (
            one_way_distance
        ),
        "return_trip_required": (
            bool(return_trip_required)
        ),
        "distance_multiplier": multiplier,
        "total_trip_distance_km": (
            total_trip_distance
        ),
    }


# =========================================================
# JOURNEY-TIME CALCULATIONS
# =========================================================
def calculate_driving_hours(
    total_trip_distance_km: float,
    average_speed_kmh: float,
) -> float:
    """
    Calculate estimated driving time.

    Formula
    -------
    Driving hours =
        Total distance ÷ Average speed
    """

    total_distance = validate_positive(
        total_trip_distance_km,
        "Total trip distance",
    )

    average_speed = validate_positive(
        average_speed_kmh,
        "Average speed",
    )

    return (
        total_distance
        / average_speed
    )


def calculate_handling_hours(
    loading_hours: float = 0,
    unloading_hours: float = 0,
    combined_loading_unloading_hours: float | None = None,
) -> float:
    """
    Calculate total loading and unloading time.

    When combined_loading_unloading_hours is supplied,
    it takes precedence.
    """

    if combined_loading_unloading_hours is not None:
        return validate_positive(
            combined_loading_unloading_hours,
            "Loading and unloading hours",
            allow_zero=True,
        )

    loading = validate_positive(
        loading_hours,
        "Loading hours",
        allow_zero=True,
    )

    unloading = validate_positive(
        unloading_hours,
        "Unloading hours",
        allow_zero=True,
    )

    return loading + unloading


def calculate_total_journey_time(
    total_trip_distance_km: float,
    average_speed_kmh: float,
    loading_unloading_hours: float = (
        DEFAULT_LOADING_UNLOADING_HOURS
    ),
    waiting_time_hours: float = 0,
    rest_time_hours: float = 0,
    other_delay_hours: float = 0,
) -> dict[str, float]:
    """
    Calculate complete estimated journey time.
    """

    estimated_driving_hours = (
        calculate_driving_hours(
            total_trip_distance_km=(
                total_trip_distance_km
            ),
            average_speed_kmh=(
                average_speed_kmh
            ),
        )
    )

    handling_hours = validate_positive(
        loading_unloading_hours,
        "Loading and unloading hours",
        allow_zero=True,
    )

    waiting_hours = validate_positive(
        waiting_time_hours,
        "Waiting time",
        allow_zero=True,
    )

    rest_hours = validate_positive(
        rest_time_hours,
        "Rest time",
        allow_zero=True,
    )

    delay_hours = validate_positive(
        other_delay_hours,
        "Other delay hours",
        allow_zero=True,
    )

    estimated_total_journey_hours = (
        estimated_driving_hours
        + handling_hours
        + waiting_hours
        + rest_hours
        + delay_hours
    )

    return {
        "average_speed_kmh": (
            safe_float(average_speed_kmh)
        ),
        "estimated_driving_hours": (
            estimated_driving_hours
        ),
        "loading_unloading_hours": (
            handling_hours
        ),
        "waiting_time_hours": waiting_hours,
        "rest_time_hours": rest_hours,
        "other_delay_hours": delay_hours,
        "estimated_total_journey_hours": (
            estimated_total_journey_hours
        ),
    }


# =========================================================
# DELIVERY FEASIBILITY
# =========================================================
def convert_target_delivery_to_hours(
    target_delivery_days: float,
    operating_hours_per_day: float = 24,
) -> float:
    """
    Convert target-delivery days into hours.
    """

    delivery_days = validate_positive(
        target_delivery_days,
        "Target delivery days",
    )

    operating_hours = validate_positive(
        operating_hours_per_day,
        "Operating hours per day",
    )

    return (
        delivery_days
        * operating_hours
    )


def assess_delivery_feasibility(
    estimated_total_journey_hours: float,
    target_delivery_days: float,
    operating_hours_per_day: float = 24,
) -> dict[str, Any]:
    """
    Compare estimated journey time with target delivery.
    """

    journey_hours = validate_positive(
        estimated_total_journey_hours,
        "Estimated journey hours",
        allow_zero=True,
    )

    target_delivery_hours = (
        convert_target_delivery_to_hours(
            target_delivery_days=(
                target_delivery_days
            ),
            operating_hours_per_day=(
                operating_hours_per_day
            ),
        )
    )

    time_buffer_hours = (
        target_delivery_hours
        - journey_hours
    )

    feasible = time_buffer_hours >= 0

    utilisation_pct = (
        journey_hours
        / target_delivery_hours
        * 100
        if target_delivery_hours > 0
        else 0
    )

    if feasible and utilisation_pct <= 70:
        feasibility_status = "Comfortable"

    elif feasible and utilisation_pct <= 90:
        feasibility_status = "Feasible"

    elif feasible:
        feasibility_status = "Tight"

    else:
        feasibility_status = "Not Feasible"

    return {
        "target_delivery_days": (
            safe_float(
                target_delivery_days
            )
        ),
        "target_delivery_hours": (
            target_delivery_hours
        ),
        "estimated_total_journey_hours": (
            journey_hours
        ),
        "time_buffer_hours": (
            time_buffer_hours
        ),
        "delivery_time_utilisation_pct": (
            utilisation_pct
        ),
        "delivery_feasible": feasible,
        "delivery_feasibility_status": (
            feasibility_status
        ),
    }


def classify_journey_duration(
    estimated_total_journey_hours: float,
) -> dict[str, str]:
    """
    Classify route duration for management interpretation.
    """

    journey_hours = validate_positive(
        estimated_total_journey_hours,
        "Estimated journey hours",
        allow_zero=True,
    )

    if journey_hours <= 4:
        return {
            "journey_classification": "Short-Haul",
            "journey_message": (
                "The journey can generally be completed within "
                "a short operating shift."
            ),
        }

    if journey_hours <= 8:
        return {
            "journey_classification": "Medium-Haul",
            "journey_message": (
                "The journey can generally be completed within "
                "one standard operating shift."
            ),
        }

    if journey_hours <= 12:
        return {
            "journey_classification": "Long-Haul",
            "journey_message": (
                "The journey may require overtime, extended "
                "working hours or driver-rest planning."
            ),
        }

    return {
        "journey_classification": "Extended-Haul",
        "journey_message": (
            "The journey exceeds a normal operating shift and "
            "may require staged delivery, overnight planning or "
            "multiple drivers."
        ),
    }


# =========================================================
# COMPLETE ROUTE INTELLIGENCE
# =========================================================
def calculate_route_intelligence(
    origin_region: str,
    origin_state: str,
    destination_region: str,
    destination_state: str,
    service_level: str,
    estimated_one_way_distance_km: float,
    average_speed_kmh: float,
    return_trip_required: bool = True,
    loading_unloading_hours: float = (
        DEFAULT_LOADING_UNLOADING_HOURS
    ),
    waiting_time_hours: float = 0,
    rest_time_hours: float = 0,
    other_delay_hours: float = 0,
    distance_multiplier: float | None = None,
    target_delivery_days: float | None = None,
    route_id: str = "",
    priority: int | None = None,
    preferred_vehicle_type: str = "",
    feasible_vehicle_types: list[str] | None = None,
) -> dict[str, Any]:
    """
    Run the complete Page 2 route-intelligence calculation.
    """

    normalised_origin_region = (
        normalise_region_name(
            origin_region
        )
    )

    normalised_destination_region = (
        normalise_region_name(
            destination_region
        )
    )

    normalised_service_level = (
        normalise_service_level(
            service_level
        )
    )

    route_category = classify_route_category(
        origin_region=(
            normalised_origin_region
        ),
        destination_region=(
            normalised_destination_region
        ),
    )

    geographical_scope = identify_geographical_scope(
        origin_region=(
            normalised_origin_region
        ),
        destination_region=(
            normalised_destination_region
        ),
    )

    distance_result = (
        calculate_total_trip_distance(
            estimated_one_way_distance_km=(
                estimated_one_way_distance_km
            ),
            return_trip_required=(
                return_trip_required
            ),
            distance_multiplier=(
                distance_multiplier
            ),
        )
    )

    journey_result = (
        calculate_total_journey_time(
            total_trip_distance_km=(
                distance_result[
                    "total_trip_distance_km"
                ]
            ),
            average_speed_kmh=(
                average_speed_kmh
            ),
            loading_unloading_hours=(
                loading_unloading_hours
            ),
            waiting_time_hours=(
                waiting_time_hours
            ),
            rest_time_hours=(
                rest_time_hours
            ),
            other_delay_hours=(
                other_delay_hours
            ),
        )
    )

    duration_result = classify_journey_duration(
        estimated_total_journey_hours=(
            journey_result[
                "estimated_total_journey_hours"
            ]
        )
    )

    delivery_result: dict[str, Any] = {
        "target_delivery_days": (
            safe_float(
                target_delivery_days
            )
            if target_delivery_days is not None
            else 0
        ),
        "target_delivery_hours": 0,
        "time_buffer_hours": 0,
        "delivery_time_utilisation_pct": 0,
        "delivery_feasible": None,
        "delivery_feasibility_status": (
            "Not Assessed"
        ),
    }

    if (
        target_delivery_days is not None
        and safe_float(
            target_delivery_days
        ) > 0
    ):
        delivery_result = (
            assess_delivery_feasibility(
                estimated_total_journey_hours=(
                    journey_result[
                        "estimated_total_journey_hours"
                    ]
                ),
                target_delivery_days=(
                    safe_float(
                        target_delivery_days
                    )
                ),
            )
        )

    normalised_vehicle_types = []

    for vehicle in (
        feasible_vehicle_types or []
    ):
        normalised_vehicle = (
            normalise_vehicle_type(
                vehicle
            )
        )

        if (
            normalised_vehicle
            and normalised_vehicle
            not in normalised_vehicle_types
        ):
            normalised_vehicle_types.append(
                normalised_vehicle
            )

    return {
        "route_id": clean_route_text(
            route_id
        ),

        "origin_region": (
            normalised_origin_region
        ),
        "origin_state": clean_route_text(
            origin_state
        ),
        "destination_region": (
            normalised_destination_region
        ),
        "destination_state": (
            clean_route_text(
                destination_state
            )
        ),

        "route_category": route_category,
        "geographical_scope": (
            geographical_scope
        ),
        "service_level": (
            normalised_service_level
        ),

        "target_delivery": (
            target_delivery_days
        ),
        "priority": (
            safe_int(priority)
            if priority is not None
            else None
        ),

        "preferred_vehicle_type": (
            normalise_vehicle_type(
                preferred_vehicle_type
            )
            if preferred_vehicle_type
            else ""
        ),
        "feasible_vehicle_types": (
            normalised_vehicle_types
        ),

        **distance_result,
        **journey_result,
        **duration_result,
        **delivery_result,
    }


# =========================================================
# BUILD ROUTE INTELLIGENCE FROM MASTER RECORDS
# =========================================================
def build_route_from_master(
    origin_region: str,
    origin_state: str,
    destination_region: str,
    destination_state: str,
    service_level: str,
    route_records: Iterable[dict[str, Any]],
    estimated_one_way_distance_km: float,
    average_speed_kmh: float,
    return_trip_required: bool = True,
    loading_unloading_hours: float = (
        DEFAULT_LOADING_UNLOADING_HOURS
    ),
    waiting_time_hours: float = 0,
    rest_time_hours: float = 0,
    other_delay_hours: float = 0,
) -> dict[str, Any]:
    """
    Match route-master records and calculate complete
    route intelligence.
    """

    feasible_records = (
        find_feasible_route_records(
            origin_region=origin_region,
            destination_region=(
                destination_region
            ),
            service_level=service_level,
            route_records=route_records,
        )
    )

    if not feasible_records:
        raise ValueError(
            "No matching route was found for the selected "
            "origin, destination and service level."
        )

    preferred_record = feasible_records[0]

    feasible_vehicle_types = [
        normalise_vehicle_type(
            record.get(
                "Vehicle Type",
                "",
            )
        )
        for record in feasible_records
        if record.get(
            "Vehicle Type",
            "",
        )
    ]

    target_delivery_days = safe_float(
        preferred_record.get(
            "Target Delivery (Days)",
            preferred_record.get(
                "Target Delivery",
                0,
            ),
        )
    )

    return calculate_route_intelligence(
        origin_region=origin_region,
        origin_state=origin_state,
        destination_region=destination_region,
        destination_state=destination_state,
        service_level=service_level,
        estimated_one_way_distance_km=(
            estimated_one_way_distance_km
        ),
        average_speed_kmh=average_speed_kmh,
        return_trip_required=(
            return_trip_required
        ),
        loading_unloading_hours=(
            loading_unloading_hours
        ),
        waiting_time_hours=(
            waiting_time_hours
        ),
        rest_time_hours=(
            rest_time_hours
        ),
        other_delay_hours=(
            other_delay_hours
        ),
        target_delivery_days=(
            target_delivery_days
        ),
        route_id=clean_route_text(
            preferred_record.get(
                "Route ID",
                "",
            )
        ),
        priority=safe_int(
            preferred_record.get(
                "Priority",
                0,
            )
        ),
        preferred_vehicle_type=(
            preferred_record.get(
                "Vehicle Type",
                "",
            )
        ),
        feasible_vehicle_types=(
            feasible_vehicle_types
        ),
    )


# =========================================================
# ROUTE SUMMARY
# =========================================================
def create_route_summary(
    route_intelligence: dict[str, Any],
) -> dict[str, Any]:
    """
    Create a concise route summary for reports and tables.
    """

    return {
        "Route ID": route_intelligence.get(
            "route_id",
            "",
        ),
        "Origin Region": route_intelligence.get(
            "origin_region",
            "",
        ),
        "Origin State": route_intelligence.get(
            "origin_state",
            "",
        ),
        "Destination Region": route_intelligence.get(
            "destination_region",
            "",
        ),
        "Destination State": route_intelligence.get(
            "destination_state",
            "",
        ),
        "Route Category": route_intelligence.get(
            "route_category",
            "",
        ),
        "Geographical Scope": route_intelligence.get(
            "geographical_scope",
            "",
        ),
        "Service Level": route_intelligence.get(
            "service_level",
            "",
        ),
        "Target Delivery (Days)": safe_float(
            route_intelligence.get(
                "target_delivery_days",
                route_intelligence.get(
                    "target_delivery",
                    0,
                ),
            )
        ),
        "Priority": safe_int(
            route_intelligence.get(
                "priority",
                0,
            )
        ),
        "Preferred Vehicle": (
            route_intelligence.get(
                "preferred_vehicle_type",
                "",
            )
        ),
        "One-Way Distance (km)": safe_float(
            route_intelligence.get(
                "estimated_one_way_distance_km",
                0,
            )
        ),
        "Total Trip Distance (km)": safe_float(
            route_intelligence.get(
                "total_trip_distance_km",
                0,
            )
        ),
        "Average Speed (km/h)": safe_float(
            route_intelligence.get(
                "average_speed_kmh",
                0,
            )
        ),
        "Driving Hours": safe_float(
            route_intelligence.get(
                "estimated_driving_hours",
                0,
            )
        ),
        "Total Journey Hours": safe_float(
            route_intelligence.get(
                "estimated_total_journey_hours",
                0,
            )
        ),
        "Journey Classification": (
            route_intelligence.get(
                "journey_classification",
                "",
            )
        ),
        "Delivery Feasibility": (
            route_intelligence.get(
                "delivery_feasibility_status",
                "",
            )
        ),
    }