"""
Cost, pricing, profitability and scenario calculations for the
Courier Cost Analysis application.

Responsibilities
----------------
Page 5:
- Fuel cost
- Toll cost
- Maintenance cost
- Tyre cost
- Manpower cost
- Overtime cost
- Financing cost
- Insurance cost
- Overhead allocation
- Total operating cost

Page 6:
- Cost per parcel
- Cost per kilogram
- Cost per cubic metre
- Cost per vehicle
- Cost per kilometre
- Volume sensitivity

Page 7:
- Selling-price calculations
- Discount and surcharge
- Revenue
- Profit
- Profit margin
- Mark-up
- Break-even
- Pricing sensitivity

Page 8:
- Scenario cost and profitability simulation

This module must not contain:
- Streamlit widgets
- Streamlit session state
- CSV loading
- CSS
- Page navigation
"""

from __future__ import annotations

import math
from typing import Any

from utils.calculations import (
    apply_percentage_change,
    percentage_change,
    safe_float,
    safe_int,
    validate_positive,
)

from utils.vehicle_master import calculate_fleet_capacity


# =========================================================
# COST CATEGORY CONSTANTS
# =========================================================
DIRECT_COST_ITEMS = {
    "Fuel",
    "Toll",
    "Maintenance",
    "Tyres",
    "Overtime",
}

FIXED_COST_ITEMS = {
    "Manpower",
    "Vehicle Financing",
    "Vehicle Insurance",
    "Regional Overhead",
}


# =========================================================
# FUEL COST
# =========================================================
def calculate_fuel_cost(
    total_trip_distance_km: float,
    planned_fleet_size: int,
    fuel_efficiency_km_per_litre: float,
    fuel_rate_rm_per_litre: float,
) -> dict[str, float]:
    """
    Calculate fuel consumption and fuel cost per shipment.

    Formula
    -------
    Litres per vehicle =
        Total trip distance ÷ Fuel efficiency

    Total litres =
        Litres per vehicle × Planned fleet size

    Fuel cost =
        Total litres × Fuel rate
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
            "Planned fleet size must be greater than zero."
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

    fuel_cost_per_vehicle = (
        fuel_litres_per_vehicle
        * fuel_rate
    )

    fuel_cost_per_shipment = (
        total_fuel_litres
        * fuel_rate
    )

    return {
        "total_trip_distance_km": distance,
        "planned_fleet_size": fleet_size,
        "fuel_efficiency_km_per_litre": (
            fuel_efficiency
        ),
        "fuel_rate_rm_per_litre": fuel_rate,
        "fuel_litres_per_vehicle": (
            fuel_litres_per_vehicle
        ),
        "total_fuel_litres": total_fuel_litres,
        "fuel_cost_per_vehicle": (
            fuel_cost_per_vehicle
        ),
        "fuel_cost_per_shipment": (
            fuel_cost_per_shipment
        ),
    }


# =========================================================
# TOLL COST
# =========================================================
def calculate_toll_cost(
    total_trip_distance_km: float,
    planned_fleet_size: int,
    toll_rate_rm_per_km: float,
) -> dict[str, float]:
    """
    Calculate toll cost per shipment.

    Formula
    -------
    Toll per vehicle =
        Distance × Toll rate

    Toll per shipment =
        Toll per vehicle × Fleet size
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
            "Planned fleet size must be greater than zero."
        )

    toll_rate = validate_positive(
        toll_rate_rm_per_km,
        "Toll rate",
        allow_zero=True,
    )

    toll_cost_per_vehicle = (
        distance
        * toll_rate
    )

    toll_cost_per_shipment = (
        toll_cost_per_vehicle
        * fleet_size
    )

    return {
        "toll_rate_rm_per_km": toll_rate,
        "toll_cost_per_vehicle": (
            toll_cost_per_vehicle
        ),
        "toll_cost_per_shipment": (
            toll_cost_per_shipment
        ),
    }


# =========================================================
# MAINTENANCE COST
# =========================================================
def calculate_maintenance_cost(
    total_trip_distance_km: float,
    planned_fleet_size: int,
    service_interval_km: float,
    service_cost_rm: float,
) -> dict[str, float]:
    """
    Allocate maintenance cost based on distance travelled.

    Formula
    -------
    Maintenance cost per km =
        Service cost ÷ Service interval

    Maintenance cost per shipment =
        Cost per km × Distance × Fleet size
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
            "Planned fleet size must be greater than zero."
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

    maintenance_cost_per_vehicle = (
        maintenance_cost_per_km
        * distance
    )

    maintenance_cost_per_shipment = (
        maintenance_cost_per_vehicle
        * fleet_size
    )

    return {
        "service_interval_km": service_interval,
        "service_cost_rm": service_cost,
        "maintenance_cost_per_km": (
            maintenance_cost_per_km
        ),
        "maintenance_cost_per_vehicle": (
            maintenance_cost_per_vehicle
        ),
        "maintenance_cost_per_shipment": (
            maintenance_cost_per_shipment
        ),
    }


# =========================================================
# TYRE COST
# =========================================================
def calculate_tyre_cost(
    total_trip_distance_km: float,
    planned_fleet_size: int,
    tyre_change_interval_km: float,
    tyre_cost_rm: float,
) -> dict[str, float]:
    """
    Allocate tyre cost based on distance travelled.

    Formula
    -------
    Tyre cost per km =
        Tyre cost ÷ Tyre replacement interval
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
            "Planned fleet size must be greater than zero."
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

    tyre_cost_per_vehicle = (
        tyre_cost_per_km
        * distance
    )

    tyre_cost_per_shipment = (
        tyre_cost_per_vehicle
        * fleet_size
    )

    return {
        "tyre_change_interval_km": (
            tyre_interval
        ),
        "tyre_cost_rm": tyre_cost,
        "tyre_cost_per_km": tyre_cost_per_km,
        "tyre_cost_per_vehicle": (
            tyre_cost_per_vehicle
        ),
        "tyre_cost_per_shipment": (
            tyre_cost_per_shipment
        ),
    }


# =========================================================
# EMPLOYEE COST
# =========================================================
def calculate_monthly_employee_cost(
    monthly_salary_rm: float,
    epf_rate_pct: float = 0,
    socso_rm: float = 0,
    eis_rm: float = 0,
    other_cost_rm: float = 0,
) -> dict[str, float]:
    """
    Calculate total monthly cost for one employee.
    """

    monthly_salary = validate_positive(
        monthly_salary_rm,
        "Monthly salary",
        allow_zero=True,
    )

    epf_rate = validate_positive(
        epf_rate_pct,
        "EPF rate",
        allow_zero=True,
    )

    socso_cost = validate_positive(
        socso_rm,
        "SOCSO cost",
        allow_zero=True,
    )

    eis_cost = validate_positive(
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
        monthly_salary
        * epf_rate
        / 100
    )

    total_monthly_employee_cost = (
        monthly_salary
        + epf_cost
        + socso_cost
        + eis_cost
        + other_cost
    )

    return {
        "monthly_salary_rm": monthly_salary,
        "epf_rate_pct": epf_rate,
        "monthly_epf_rm": epf_cost,
        "monthly_socso_rm": socso_cost,
        "monthly_eis_rm": eis_cost,
        "monthly_other_cost_rm": other_cost,
        "total_monthly_employee_cost": (
            total_monthly_employee_cost
        ),
    }


def calculate_total_monthly_manpower_cost(
    monthly_cost_per_driver_rm: float,
    driver_count: int,
    operations_executive_monthly_cost_rm: float = 0,
    include_operations_executive: bool = False,
) -> dict[str, float]:
    """
    Calculate monthly driver and operations manpower cost.
    """

    driver_cost = validate_positive(
        monthly_cost_per_driver_rm,
        "Monthly driver cost",
        allow_zero=True,
    )

    number_of_drivers = max(
        safe_int(driver_count),
        0,
    )

    total_monthly_driver_cost = (
        driver_cost
        * number_of_drivers
    )

    operations_executive_cost = 0.0

    if include_operations_executive:
        operations_executive_cost = (
            validate_positive(
                operations_executive_monthly_cost_rm,
                "Operations executive cost",
                allow_zero=True,
            )
        )

    total_monthly_manpower_cost = (
        total_monthly_driver_cost
        + operations_executive_cost
    )

    return {
        "monthly_cost_per_driver_rm": (
            driver_cost
        ),
        "driver_count": number_of_drivers,
        "total_monthly_driver_cost": (
            total_monthly_driver_cost
        ),
        "include_operations_executive": (
            include_operations_executive
        ),
        "operations_executive_monthly_cost_rm": (
            operations_executive_cost
        ),
        "total_monthly_manpower_cost": (
            total_monthly_manpower_cost
        ),
    }


# =========================================================
# OVERTIME COST
# =========================================================
def calculate_overtime_cost(
    estimated_journey_hours: float,
    normal_working_hours: float,
    overtime_rate_rm_per_hour: float,
    driver_count: int,
) -> dict[str, float]:
    """
    Calculate overtime hours and cost per shipment.
    """

    journey_hours = validate_positive(
        estimated_journey_hours,
        "Estimated journey hours",
        allow_zero=True,
    )

    normal_hours = validate_positive(
        normal_working_hours,
        "Normal working hours",
        allow_zero=True,
    )

    overtime_rate = validate_positive(
        overtime_rate_rm_per_hour,
        "Overtime rate",
        allow_zero=True,
    )

    number_of_drivers = max(
        safe_int(driver_count),
        0,
    )

    overtime_hours_per_driver = max(
        journey_hours - normal_hours,
        0,
    )

    overtime_cost_per_driver = (
        overtime_hours_per_driver
        * overtime_rate
    )

    overtime_cost_per_shipment = (
        overtime_cost_per_driver
        * number_of_drivers
    )

    return {
        "estimated_journey_hours": (
            journey_hours
        ),
        "normal_working_hours": normal_hours,
        "overtime_hours_per_driver": (
            overtime_hours_per_driver
        ),
        "overtime_rate_rm_per_hour": (
            overtime_rate
        ),
        "overtime_cost_per_driver": (
            overtime_cost_per_driver
        ),
        "overtime_cost_per_shipment": (
            overtime_cost_per_shipment
        ),
    }


# =========================================================
# FINANCING AND INSURANCE
# =========================================================
def calculate_monthly_vehicle_financing(
    monthly_instalment_per_vehicle_rm: float,
    planned_fleet_size: int,
    include_financing_cost: bool = True,
) -> dict[str, float]:
    """
    Calculate total monthly financing cost.
    """

    instalment = validate_positive(
        monthly_instalment_per_vehicle_rm,
        "Monthly vehicle instalment",
        allow_zero=True,
    )

    fleet_size = max(
        safe_int(planned_fleet_size),
        0,
    )

    monthly_financing_cost = 0.0

    if include_financing_cost:
        monthly_financing_cost = (
            instalment
            * fleet_size
        )

    return {
        "include_financing_cost": (
            include_financing_cost
        ),
        "monthly_instalment_per_vehicle_rm": (
            instalment
        ),
        "monthly_financing_cost": (
            monthly_financing_cost
        ),
    }


def calculate_monthly_vehicle_insurance(
    annual_insurance_per_vehicle_rm: float,
    planned_fleet_size: int,
    include_insurance_cost: bool = True,
) -> dict[str, float]:
    """
    Convert annual vehicle insurance into monthly fleet cost.
    """

    annual_insurance = validate_positive(
        annual_insurance_per_vehicle_rm,
        "Annual vehicle insurance",
        allow_zero=True,
    )

    fleet_size = max(
        safe_int(planned_fleet_size),
        0,
    )

    monthly_insurance_per_vehicle = (
        annual_insurance
        / 12
    )

    monthly_insurance_cost = 0.0

    if include_insurance_cost:
        monthly_insurance_cost = (
            monthly_insurance_per_vehicle
            * fleet_size
        )

    return {
        "include_insurance_cost": (
            include_insurance_cost
        ),
        "annual_insurance_per_vehicle_rm": (
            annual_insurance
        ),
        "monthly_insurance_per_vehicle_rm": (
            monthly_insurance_per_vehicle
        ),
        "monthly_insurance_cost": (
            monthly_insurance_cost
        ),
    }


# =========================================================
# MONTHLY COST ALLOCATION
# =========================================================
def allocate_monthly_cost_per_shipment(
    monthly_cost_rm: float,
    shipments_per_month: int,
) -> float:
    """
    Allocate monthly cost across monthly shipments.
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
            "Shipments per month must be greater than zero."
        )

    return (
        monthly_cost
        / shipment_count
    )


# =========================================================
# REGIONAL OVERHEAD
# =========================================================
def calculate_regional_overhead(
    overhead_items: dict[str, float],
    shipments_per_month: int,
    excluded_items: set[str] | None = None,
) -> dict[str, Any]:
    """
    Calculate total regional overhead and allocation per shipment.

    Parameters
    ----------
    overhead_items:
        Dictionary containing overhead names and monthly costs.

    shipments_per_month:
        Number of shipments per month.

    excluded_items:
        Items excluded from overhead totals, for example:
        {"Warehouse Size", "Rental Rate"}
    """

    shipment_count = safe_int(
        shipments_per_month
    )

    if shipment_count <= 0:
        raise ValueError(
            "Shipments per month must be greater than zero."
        )

    excluded = excluded_items or {
        "Warehouse Size",
        "Rental Rate",
    }

    included_items = {}
    excluded_records = {}

    for item_name, item_value in overhead_items.items():
        numeric_value = max(
            safe_float(item_value),
            0,
        )

        if item_name in excluded:
            excluded_records[item_name] = (
                numeric_value
            )

        else:
            included_items[item_name] = (
                numeric_value
            )

    monthly_regional_overhead = sum(
        included_items.values()
    )

    allocated_overhead_per_shipment = (
        monthly_regional_overhead
        / shipment_count
    )

    return {
        "included_overhead_items": (
            included_items
        ),
        "excluded_overhead_items": (
            excluded_records
        ),
        "monthly_regional_overhead": (
            monthly_regional_overhead
        ),
        "allocated_overhead_per_shipment": (
            allocated_overhead_per_shipment
        ),
    }


# =========================================================
# TOTAL OPERATING COST
# =========================================================
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
) -> dict[str, Any]:
    """
    Calculate direct, fixed and total operating costs.
    """

    shipment_count = safe_int(
        shipments_per_month
    )

    if shipment_count <= 0:
        raise ValueError(
            "Shipments per month must be greater than zero."
        )

    direct_cost_items = {
        "Fuel": max(
            safe_float(
                fuel_cost_per_shipment
            ),
            0,
        ),
        "Toll": max(
            safe_float(
                toll_cost_per_shipment
            ),
            0,
        ),
        "Maintenance": max(
            safe_float(
                maintenance_cost_per_shipment
            ),
            0,
        ),
        "Tyres": max(
            safe_float(
                tyre_cost_per_shipment
            ),
            0,
        ),
        "Overtime": max(
            safe_float(
                overtime_cost_per_shipment
            ),
            0,
        ),
    }

    monthly_fixed_cost_items = {
        "Manpower": max(
            safe_float(
                monthly_manpower_cost
            ),
            0,
        ),
        "Vehicle Financing": max(
            safe_float(
                monthly_financing_cost
            ),
            0,
        ),
        "Vehicle Insurance": max(
            safe_float(
                monthly_insurance_cost
            ),
            0,
        ),
        "Regional Overhead": max(
            safe_float(
                monthly_regional_overhead
            ),
            0,
        ),
    }

    direct_trip_cost = sum(
        direct_cost_items.values()
    )

    total_monthly_fixed_cost = sum(
        monthly_fixed_cost_items.values()
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

    cost_breakdown = []

    for item_name, cost_value in (
        direct_cost_items.items()
    ):
        cost_breakdown.append(
            {
                "Cost Category": "Direct Cost",
                "Cost Item": item_name,
                "Monthly Cost (RM)": (
                    cost_value
                    * shipment_count
                ),
                "Cost per Shipment (RM)": (
                    cost_value
                ),
            }
        )

    for item_name, monthly_cost in (
        monthly_fixed_cost_items.items()
    ):
        cost_breakdown.append(
            {
                "Cost Category": "Fixed Cost",
                "Cost Item": item_name,
                "Monthly Cost (RM)": monthly_cost,
                "Cost per Shipment (RM)": (
                    monthly_cost
                    / shipment_count
                ),
            }
        )

    for record in cost_breakdown:
        record["Share of Total (%)"] = (
            record["Cost per Shipment (RM)"]
            / total_operating_cost_per_shipment
            * 100
            if total_operating_cost_per_shipment > 0
            else 0
        )

    return {
        "shipments_per_month": shipment_count,

        "direct_cost_items": direct_cost_items,
        "monthly_fixed_cost_items": (
            monthly_fixed_cost_items
        ),

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

        "cost_breakdown": cost_breakdown,
    }


# =========================================================
# COMPLETE OPERATING COST ASSESSMENT
# =========================================================
def calculate_complete_operating_cost(
    total_trip_distance_km: float,
    planned_fleet_size: int,
    fuel_efficiency_km_per_litre: float,
    fuel_rate_rm_per_litre: float,
    toll_rate_rm_per_km: float,
    service_interval_km: float,
    service_cost_rm: float,
    tyre_change_interval_km: float,
    tyre_cost_rm: float,
    estimated_journey_hours: float,
    normal_working_hours: float,
    overtime_rate_rm_per_hour: float,
    monthly_driver_cost_per_person_rm: float,
    operations_executive_monthly_cost_rm: float,
    include_operations_executive: bool,
    monthly_instalment_per_vehicle_rm: float,
    include_financing_cost: bool,
    annual_insurance_per_vehicle_rm: float,
    include_insurance_cost: bool,
    monthly_regional_overhead: float,
    shipments_per_month: int,
) -> dict[str, Any]:
    """
    Run the complete Page 5 operating-cost calculation.
    """

    fuel_result = calculate_fuel_cost(
        total_trip_distance_km=(
            total_trip_distance_km
        ),
        planned_fleet_size=(
            planned_fleet_size
        ),
        fuel_efficiency_km_per_litre=(
            fuel_efficiency_km_per_litre
        ),
        fuel_rate_rm_per_litre=(
            fuel_rate_rm_per_litre
        ),
    )

    toll_result = calculate_toll_cost(
        total_trip_distance_km=(
            total_trip_distance_km
        ),
        planned_fleet_size=(
            planned_fleet_size
        ),
        toll_rate_rm_per_km=(
            toll_rate_rm_per_km
        ),
    )

    maintenance_result = (
        calculate_maintenance_cost(
            total_trip_distance_km=(
                total_trip_distance_km
            ),
            planned_fleet_size=(
                planned_fleet_size
            ),
            service_interval_km=(
                service_interval_km
            ),
            service_cost_rm=service_cost_rm,
        )
    )

    tyre_result = calculate_tyre_cost(
        total_trip_distance_km=(
            total_trip_distance_km
        ),
        planned_fleet_size=(
            planned_fleet_size
        ),
        tyre_change_interval_km=(
            tyre_change_interval_km
        ),
        tyre_cost_rm=tyre_cost_rm,
    )

    overtime_result = (
        calculate_overtime_cost(
            estimated_journey_hours=(
                estimated_journey_hours
            ),
            normal_working_hours=(
                normal_working_hours
            ),
            overtime_rate_rm_per_hour=(
                overtime_rate_rm_per_hour
            ),
            driver_count=planned_fleet_size,
        )
    )

    manpower_result = (
        calculate_total_monthly_manpower_cost(
            monthly_cost_per_driver_rm=(
                monthly_driver_cost_per_person_rm
            ),
            driver_count=planned_fleet_size,
            operations_executive_monthly_cost_rm=(
                operations_executive_monthly_cost_rm
            ),
            include_operations_executive=(
                include_operations_executive
            ),
        )
    )

    financing_result = (
        calculate_monthly_vehicle_financing(
            monthly_instalment_per_vehicle_rm=(
                monthly_instalment_per_vehicle_rm
            ),
            planned_fleet_size=(
                planned_fleet_size
            ),
            include_financing_cost=(
                include_financing_cost
            ),
        )
    )

    insurance_result = (
        calculate_monthly_vehicle_insurance(
            annual_insurance_per_vehicle_rm=(
                annual_insurance_per_vehicle_rm
            ),
            planned_fleet_size=(
                planned_fleet_size
            ),
            include_insurance_cost=(
                include_insurance_cost
            ),
        )
    )

    operating_cost_result = (
        calculate_operating_cost(
            fuel_cost_per_shipment=(
                fuel_result[
                    "fuel_cost_per_shipment"
                ]
            ),
            toll_cost_per_shipment=(
                toll_result[
                    "toll_cost_per_shipment"
                ]
            ),
            maintenance_cost_per_shipment=(
                maintenance_result[
                    "maintenance_cost_per_shipment"
                ]
            ),
            tyre_cost_per_shipment=(
                tyre_result[
                    "tyre_cost_per_shipment"
                ]
            ),
            overtime_cost_per_shipment=(
                overtime_result[
                    "overtime_cost_per_shipment"
                ]
            ),
            monthly_manpower_cost=(
                manpower_result[
                    "total_monthly_manpower_cost"
                ]
            ),
            monthly_financing_cost=(
                financing_result[
                    "monthly_financing_cost"
                ]
            ),
            monthly_insurance_cost=(
                insurance_result[
                    "monthly_insurance_cost"
                ]
            ),
            monthly_regional_overhead=(
                monthly_regional_overhead
            ),
            shipments_per_month=(
                shipments_per_month
            ),
        )
    )

    return {
        **fuel_result,
        **toll_result,
        **maintenance_result,
        **tyre_result,
        **overtime_result,
        **manpower_result,
        **financing_result,
        **insurance_result,
        **operating_cost_result,
    }


# =========================================================
# COST PER PARCEL
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
    Calculate Page 6 unit-cost measures.
    """

    quantity = safe_int(
        parcel_quantity
    )

    if quantity <= 0:
        raise ValueError(
            "Parcel quantity must be greater than zero."
        )

    actual_weight = validate_positive(
        total_actual_weight_kg,
        "Total actual weight",
    )

    chargeable_weight = validate_positive(
        chargeable_weight_kg,
        "Chargeable weight",
    )

    shipment_volume = validate_positive(
        total_volume_m3,
        "Shipment volume",
    )

    fleet_size = safe_int(
        planned_fleet_size
    )

    if fleet_size <= 0:
        raise ValueError(
            "Planned fleet size must be greater than zero."
        )

    trip_distance = validate_positive(
        total_trip_distance_km,
        "Total trip distance",
    )

    shipment_count = safe_int(
        shipments_per_month
    )

    if shipment_count <= 0:
        raise ValueError(
            "Shipments per month must be greater than zero."
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

    return {
        "parcel_quantity": quantity,
        "shipments_per_month": shipment_count,
        "monthly_parcel_quantity": (
            monthly_parcel_quantity
        ),

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
            direct_cost
            / total_cost_per_shipment
            * 100
            if total_cost_per_shipment > 0
            else 0
        ),
        "fixed_cost_share_pct": (
            fixed_cost
            / total_cost_per_shipment
            * 100
            if total_cost_per_shipment > 0
            else 0
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
            / shipment_volume
        ),
        "cost_per_vehicle": (
            total_cost_per_shipment
            / fleet_size
        ),
        "cost_per_trip_km": (
            total_cost_per_shipment
            / trip_distance
        ),
        "cost_per_vehicle_km": (
            total_cost_per_shipment
            / (
                trip_distance
                * fleet_size
            )
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


# =========================================================
# VOLUME SENSITIVITY
# =========================================================
def calculate_volume_sensitivity(
    total_cost_per_shipment: float,
    baseline_parcel_quantity: int,
    parcel_volume_change_pct: float,
) -> dict[str, float | int]:
    """
    Calculate cost-per-parcel sensitivity while shipment cost
    remains unchanged.
    """

    shipment_cost = validate_positive(
        total_cost_per_shipment,
        "Total shipment cost",
    )

    baseline_quantity = safe_int(
        baseline_parcel_quantity
    )

    if baseline_quantity <= 0:
        raise ValueError(
            "Baseline parcel quantity must be greater than zero."
        )

    adjusted_parcel_quantity = max(
        safe_int(
            apply_percentage_change(
                baseline_quantity,
                parcel_volume_change_pct,
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
        / adjusted_parcel_quantity
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
        "parcel_volume_change_pct": (
            safe_float(
                parcel_volume_change_pct
            )
        ),
        "baseline_parcel_quantity": (
            baseline_quantity
        ),
        "adjusted_parcel_quantity": (
            adjusted_parcel_quantity
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
        "cost_change_pct": cost_change_pct,
    }


# =========================================================
# SELLING-PRICE CALCULATIONS
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
    Calculate selling price required for a target margin.

    Formula
    -------
    Price = Cost ÷ (1 - Target margin)
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
            "Target margin must be below 100%."
        )

    return (
        cost
        / (
            1
            - margin_pct / 100
        )
    )


def calculate_price_per_chargeable_kg(
    price_per_chargeable_kg_rm: float,
    chargeable_weight_kg: float,
    parcel_quantity: int,
) -> dict[str, float]:
    """
    Convert chargeable-weight pricing into a parcel selling price.
    """

    price_per_kg = validate_positive(
        price_per_chargeable_kg_rm,
        "Price per chargeable kilogram",
        allow_zero=True,
    )

    chargeable_weight = validate_positive(
        chargeable_weight_kg,
        "Chargeable weight",
    )

    quantity = safe_int(
        parcel_quantity
    )

    if quantity <= 0:
        raise ValueError(
            "Parcel quantity must be greater than zero."
        )

    chargeable_weight_per_parcel = (
        chargeable_weight
        / quantity
    )

    selling_price_per_parcel = (
        chargeable_weight_per_parcel
        * price_per_kg
    )

    return {
        "price_per_chargeable_kg_rm": (
            price_per_kg
        ),
        "chargeable_weight_per_parcel_kg": (
            chargeable_weight_per_parcel
        ),
        "selling_price_per_parcel": (
            selling_price_per_parcel
        ),
    }


# =========================================================
# DISCOUNT AND SURCHARGE
# =========================================================
def calculate_net_selling_price(
    gross_price_per_parcel: float,
    discount_pct: float = 0,
    surcharge_pct: float = 0,
) -> dict[str, float]:
    """
    Apply customer discount followed by service surcharge.
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

    discount_amount_per_parcel = (
        gross_price
        * discount_rate
        / 100
    )

    price_after_discount = (
        gross_price
        - discount_amount_per_parcel
    )

    surcharge_amount_per_parcel = (
        price_after_discount
        * surcharge_rate
        / 100
    )

    net_selling_price_per_parcel = (
        price_after_discount
        + surcharge_amount_per_parcel
    )

    return {
        "gross_price_per_parcel": gross_price,
        "discount_pct": discount_rate,
        "discount_amount_per_parcel": (
            discount_amount_per_parcel
        ),
        "price_after_discount": (
            price_after_discount
        ),
        "surcharge_pct": surcharge_rate,
        "surcharge_amount_per_parcel": (
            surcharge_amount_per_parcel
        ),
        "net_selling_price_per_parcel": (
            net_selling_price_per_parcel
        ),
    }


# =========================================================
# PROFITABILITY
# =========================================================
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

    quantity = safe_int(
        parcel_quantity
    )

    if quantity <= 0:
        raise ValueError(
            "Parcel quantity must be greater than zero."
        )

    shipment_count = safe_int(
        shipments_per_month
    )

    if shipment_count <= 0:
        raise ValueError(
            "Shipments per month must be greater than zero."
        )

    net_price = validate_positive(
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
        net_price
        * quantity
    )

    total_revenue_per_shipment = (
        parcel_revenue_per_shipment
        + additional_fee
    )

    effective_revenue_per_parcel = (
        total_revenue_per_shipment
        / quantity
    )

    profit_per_parcel = (
        effective_revenue_per_parcel
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
        "parcel_quantity": quantity,
        "shipments_per_month": shipment_count,
        "monthly_parcel_quantity": (
            monthly_parcel_quantity
        ),

        "net_selling_price_per_parcel": (
            net_price
        ),
        "additional_fee_per_shipment": (
            additional_fee
        ),
        "effective_revenue_per_parcel": (
            effective_revenue_per_parcel
        ),

        "total_cost_per_parcel": (
            cost_per_parcel
        ),
        "total_cost_per_shipment": (
            total_cost_per_shipment
        ),
        "total_monthly_operating_cost": (
            total_monthly_operating_cost
        ),

        "parcel_revenue_per_shipment": (
            parcel_revenue_per_shipment
        ),
        "total_revenue_per_shipment": (
            total_revenue_per_shipment
        ),
        "monthly_revenue": monthly_revenue,

        "profit_per_parcel": profit_per_parcel,
        "profit_per_shipment": (
            profit_per_shipment
        ),
        "monthly_profit": monthly_profit,

        "profit_margin_pct": (
            profit_margin_pct
        ),
        "markup_on_cost_pct": (
            markup_on_cost_pct
        ),
        "monthly_profit_margin_pct": (
            monthly_profit_margin_pct
        ),
    }


# =========================================================
# BREAK-EVEN
# =========================================================
def calculate_break_even(
    total_cost_per_parcel: float,
    total_cost_per_shipment: float,
    net_selling_price_per_parcel: float,
    additional_fee_per_shipment: float = 0,
    shipments_per_month: int | None = None,
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

    net_price = validate_positive(
        net_selling_price_per_parcel,
        "Net selling price",
        allow_zero=True,
    )

    additional_fee = validate_positive(
        additional_fee_per_shipment,
        "Additional shipment fee",
        allow_zero=True,
    )

    cost_to_recover_from_parcels = max(
        shipment_cost - additional_fee,
        0,
    )

    break_even_parcel_quantity = (
        math.ceil(
            cost_to_recover_from_parcels
            / net_price
        )
        if net_price > 0
        else 0
    )

    results: dict[str, float | int] = {
        "break_even_price_per_parcel": (
            cost_per_parcel
        ),
        "break_even_revenue_per_shipment": (
            shipment_cost
        ),
        "break_even_parcel_quantity": (
            break_even_parcel_quantity
        ),
    }

    if shipments_per_month is not None:
        shipment_count = max(
            safe_int(shipments_per_month),
            0,
        )

        results[
            "break_even_monthly_revenue"
        ] = (
            shipment_cost
            * shipment_count
        )

    return results


# =========================================================
# PRICE SENSITIVITY
# =========================================================
def calculate_price_sensitivity(
    baseline_selling_price_per_parcel: float,
    price_change_pct: float,
    parcel_quantity: int,
    total_cost_per_shipment: float,
    shipments_per_month: int,
    additional_fee_per_shipment: float = 0,
) -> dict[str, float]:
    """
    Calculate profitability after changing selling price.
    """

    adjusted_price = apply_percentage_change(
        baseline_selling_price_per_parcel,
        price_change_pct,
    )

    quantity = safe_int(
        parcel_quantity
    )

    shipment_count = safe_int(
        shipments_per_month
    )

    if quantity <= 0:
        raise ValueError(
            "Parcel quantity must be greater than zero."
        )

    if shipment_count <= 0:
        raise ValueError(
            "Shipments per month must be greater than zero."
        )

    shipment_cost = validate_positive(
        total_cost_per_shipment,
        "Total cost per shipment",
    )

    additional_fee = validate_positive(
        additional_fee_per_shipment,
        "Additional shipment fee",
        allow_zero=True,
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
# PROFITABILITY CLASSIFICATION
# =========================================================
def classify_profitability(
    profit_per_shipment: float,
    profit_margin_pct: float,
) -> dict[str, str]:
    """
    Classify profitability for Page 7 and Page 9.
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
            "status_type": "error",
            "message": (
                "Revenue does not recover total operating cost."
            ),
        }

    if margin < 5:
        return {
            "status": "Low Margin",
            "status_type": "warning",
            "message": (
                "The margin provides limited protection against "
                "cost increases or lower shipment volume."
            ),
        }

    if margin < 15:
        return {
            "status": "Moderate Margin",
            "status_type": "warning",
            "message": (
                "The service is profitable with a moderate "
                "commercial margin."
            ),
        }

    if margin < 30:
        return {
            "status": "Healthy Margin",
            "status_type": "success",
            "message": (
                "The service generates a healthy profit margin "
                "under the selected assumptions."
            ),
        }

    return {
        "status": "High Margin",
        "status_type": "success",
        "message": (
            "The service generates a strong margin. Confirm that "
            "the selling price remains commercially competitive."
        ),
    }


# =========================================================
# SCENARIO SIMULATION
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
    Calculate one complete Page 8 scenario.
    """

    simulated_parcel_quantity = max(
        safe_int(
            apply_percentage_change(
                baseline_parcel_quantity,
                parcel_change_pct,
            )
        ),
        1,
    )

    simulated_shipments_per_month = max(
        safe_int(
            apply_percentage_change(
                baseline_shipments_per_month,
                shipment_change_pct,
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

    simulated_planned_fleet_size = (
        fleet_result[
            "planned_fleet_size"
        ]
    )

    baseline_fleet_size = safe_int(
        baseline_planned_fleet_size
    )

    if baseline_fleet_size <= 0:
        raise ValueError(
            "Baseline planned fleet size must be greater "
            "than zero."
        )

    fleet_scaling_ratio = (
        simulated_planned_fleet_size
        / baseline_fleet_size
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
        shipments_per_month=(
            simulated_shipments_per_month
        ),
    )

    profitability_status = (
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
            safe_float(
                fuel_cost_change_pct
            )
        ),
        "Toll Cost Change (%)": (
            safe_float(
                toll_cost_change_pct
            )
        ),
        "Other Direct Cost Change (%)": (
            safe_float(
                other_direct_cost_change_pct
            )
        ),
        "Fixed Cost Change (%)": (
            safe_float(
                fixed_cost_change_pct
            )
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
            simulated_parcel_quantity
            * simulated_shipments_per_month
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
            simulated_planned_fleet_size
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
        "Break-Even Monthly Revenue (RM)": (
            break_even_result.get(
                "break_even_monthly_revenue",
                0,
            )
        ),

        "Scenario Status": (
            profitability_status[
                "status"
            ]
        ),
        "Scenario Status Type": (
            profitability_status[
                "status_type"
            ]
        ),
        "Scenario Message": (
            profitability_status[
                "message"
            ]
        ),
    }