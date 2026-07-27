"""
Formatting utilities for the Courier Cost Analysis application.

Responsibilities
----------------
- Currency formatting
- Percentage formatting
- Weight formatting
- Volume formatting
- Distance formatting
- Duration formatting
- Integer and decimal formatting
- Date formatting
- Text normalisation

This module must not contain:
- Streamlit widgets
- Session-state logic
- CSV loading
- Business calculations
- Page navigation
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

import math

from utils.calculations import (
    safe_float,
    safe_int,
)


# =========================================================
# GENERAL NUMBER FORMATTING
# =========================================================
def format_number(
    value: Any,
    decimal_places: int = 2,
    default: str = "0.00",
    use_comma: bool = True,
) -> str:
    """
    Format a numeric value.

    Parameters
    ----------
    value:
        Value to format.

    decimal_places:
        Number of decimal places.

    default:
        Value returned when the input is invalid.

    use_comma:
        Whether to display thousand separators.

    Examples
    --------
    format_number(1234.567)
    returns:
    "1,234.57"

    format_number(1234.567, decimal_places=1)
    returns:
    "1,234.6"
    """

    try:
        numeric_value = float(value)

        if math.isnan(numeric_value):
            return default

        if use_comma:
            return (
                f"{numeric_value:,.{decimal_places}f}"
            )

        return (
            f"{numeric_value:.{decimal_places}f}"
        )

    except (TypeError, ValueError):
        return default


def format_integer(
    value: Any,
    default: str = "0",
    use_comma: bool = True,
) -> str:
    """
    Format a value as an integer.

    Examples
    --------
    format_integer(1500)
    returns:
    "1,500"
    """

    try:
        integer_value = int(
            round(
                float(value)
            )
        )

        if use_comma:
            return f"{integer_value:,}"

        return str(integer_value)

    except (TypeError, ValueError):
        return default


def format_decimal(
    value: Any,
    decimal_places: int = 2,
    default: str = "0.00",
) -> str:
    """
    Format a decimal without thousand separators.
    """

    return format_number(
        value=value,
        decimal_places=decimal_places,
        default=default,
        use_comma=False,
    )


# =========================================================
# CURRENCY FORMATTING
# =========================================================
def format_currency(
    value: Any,
    currency: str = "RM",
    decimal_places: int = 2,
    default: str | None = None,
    show_negative_parentheses: bool = False,
) -> str:
    """
    Format a value as currency.

    Parameters
    ----------
    value:
        Numeric value.

    currency:
        Currency symbol or code.

    decimal_places:
        Number of decimal places.

    default:
        Value returned when input is invalid.

    show_negative_parentheses:
        When True:
        -RM 100.00 becomes (RM 100.00)

    Examples
    --------
    format_currency(1250.5)
    returns:
    "RM 1,250.50"

    format_currency(-1250.5, show_negative_parentheses=True)
    returns:
    "(RM 1,250.50)"
    """

    if default is None:
        default = (
            f"{currency} "
            + format_number(
                0,
                decimal_places=decimal_places,
            )
        )

    try:
        numeric_value = float(value)

        if math.isnan(numeric_value):
            return default

        absolute_value = abs(
            numeric_value
        )

        formatted_amount = (
            f"{currency} "
            f"{absolute_value:,.{decimal_places}f}"
        )

        if numeric_value < 0:
            if show_negative_parentheses:
                return f"({formatted_amount})"

            return f"-{formatted_amount}"

        return formatted_amount

    except (TypeError, ValueError):
        return default


def format_rm(
    value: Any,
    decimal_places: int = 2,
    show_negative_parentheses: bool = False,
) -> str:
    """
    Shortcut for Malaysian Ringgit formatting.
    """

    return format_currency(
        value=value,
        currency="RM",
        decimal_places=decimal_places,
        show_negative_parentheses=(
            show_negative_parentheses
        ),
    )


def format_currency_delta(
    value: Any,
    currency: str = "RM",
    decimal_places: int = 2,
) -> str:
    """
    Format currency with an explicit plus or minus sign.

    Examples
    --------
    100 -> +RM 100.00
    -100 -> -RM 100.00
    """

    numeric_value = safe_float(
        value
    )

    sign = (
        "+"
        if numeric_value > 0
        else "-"
        if numeric_value < 0
        else ""
    )

    return (
        f"{sign}{currency} "
        f"{abs(numeric_value):,.{decimal_places}f}"
    )


# =========================================================
# PERCENTAGE FORMATTING
# =========================================================
def format_percentage(
    value: Any,
    decimal_places: int = 1,
    default: str = "0.0%",
) -> str:
    """
    Format a value as a percentage.

    The input should already be in percentage form.

    Example
    -------
    format_percentage(25.5)
    returns:
    "25.5%"
    """

    try:
        numeric_value = float(value)

        if math.isnan(numeric_value):
            return default

        return (
            f"{numeric_value:,.{decimal_places}f}%"
        )

    except (TypeError, ValueError):
        return default


def format_percentage_delta(
    value: Any,
    decimal_places: int = 1,
    suffix: str = "pts",
) -> str:
    """
    Format a percentage change with an explicit sign.

    Examples
    --------
    2.5 -> +2.5 pts
    -1.0 -> -1.0 pts
    """

    numeric_value = safe_float(
        value
    )

    sign = (
        "+"
        if numeric_value > 0
        else ""
    )

    return (
        f"{sign}"
        f"{numeric_value:,.{decimal_places}f} "
        f"{suffix}"
    )


def format_ratio_as_percentage(
    numerator: Any,
    denominator: Any,
    decimal_places: int = 1,
    default: str = "0.0%",
) -> str:
    """
    Calculate and format a ratio as a percentage.

    Example
    -------
    format_ratio_as_percentage(25, 100)
    returns:
    "25.0%"
    """

    numerator_value = safe_float(
        numerator
    )

    denominator_value = safe_float(
        denominator
    )

    if denominator_value == 0:
        return default

    percentage_value = (
        numerator_value
        / denominator_value
        * 100
    )

    return format_percentage(
        percentage_value,
        decimal_places=decimal_places,
        default=default,
    )


# =========================================================
# WEIGHT FORMATTING
# =========================================================
def format_weight(
    value_kg: Any,
    decimal_places: int = 2,
    auto_unit: bool = False,
) -> str:
    """
    Format weight in kilograms or tonnes.

    When auto_unit=True:
    - Below 1,000 kg: kg
    - 1,000 kg and above: tonnes

    Examples
    --------
    format_weight(650)
    returns:
    "650.00 kg"

    format_weight(1500, auto_unit=True)
    returns:
    "1.50 tonnes"
    """

    weight_kg = safe_float(
        value_kg
    )

    if auto_unit and abs(weight_kg) >= 1000:
        tonnes = weight_kg / 1000

        return (
            f"{tonnes:,.{decimal_places}f} "
            "tonnes"
        )

    return (
        f"{weight_kg:,.{decimal_places}f} kg"
    )


def format_tonnes(
    value_tonnes: Any,
    decimal_places: int = 2,
) -> str:
    """
    Format weight directly in tonnes.
    """

    tonnes = safe_float(
        value_tonnes
    )

    return (
        f"{tonnes:,.{decimal_places}f} "
        "tonnes"
    )


# =========================================================
# VOLUME FORMATTING
# =========================================================
def format_volume(
    value_m3: Any,
    decimal_places: int = 3,
) -> str:
    """
    Format volume in cubic metres.

    Example
    -------
    format_volume(2.34567)
    returns:
    "2.346 m³"
    """

    volume_m3 = safe_float(
        value_m3
    )

    return (
        f"{volume_m3:,.{decimal_places}f} m³"
    )


def format_cubic_centimetres(
    value_cm3: Any,
    decimal_places: int = 0,
) -> str:
    """
    Format volume in cubic centimetres.
    """

    volume_cm3 = safe_float(
        value_cm3
    )

    return (
        f"{volume_cm3:,.{decimal_places}f} cm³"
    )


# =========================================================
# DISTANCE FORMATTING
# =========================================================
def format_distance(
    value_km: Any,
    decimal_places: int = 1,
    auto_unit: bool = False,
) -> str:
    """
    Format distance in kilometres or metres.

    When auto_unit=True:
    - Less than 1 km: metres
    - 1 km and above: kilometres

    Examples
    --------
    format_distance(125.5)
    returns:
    "125.5 km"

    format_distance(0.8, auto_unit=True)
    returns:
    "800 m"
    """

    distance_km = safe_float(
        value_km
    )

    if auto_unit and abs(distance_km) < 1:
        distance_m = (
            distance_km
            * 1000
        )

        return f"{distance_m:,.0f} m"

    return (
        f"{distance_km:,.{decimal_places}f} km"
    )


def format_speed(
    value_kmh: Any,
    decimal_places: int = 1,
) -> str:
    """
    Format speed in kilometres per hour.
    """

    speed_kmh = safe_float(
        value_kmh
    )

    return (
        f"{speed_kmh:,.{decimal_places}f} km/h"
    )


def format_fuel_efficiency(
    value_km_per_litre: Any,
    decimal_places: int = 1,
) -> str:
    """
    Format fuel efficiency in km/L.
    """

    efficiency = safe_float(
        value_km_per_litre
    )

    return (
        f"{efficiency:,.{decimal_places}f} km/L"
    )


def format_fuel_volume(
    value_litres: Any,
    decimal_places: int = 2,
) -> str:
    """
    Format fuel volume in litres.
    """

    litres = safe_float(
        value_litres
    )

    return (
        f"{litres:,.{decimal_places}f} L"
    )


# =========================================================
# TIME AND DURATION FORMATTING
# =========================================================
def format_hours(
    value_hours: Any,
    decimal_places: int = 1,
) -> str:
    """
    Format a value as decimal hours.
    """

    hours = safe_float(
        value_hours
    )

    return (
        f"{hours:,.{decimal_places}f} hours"
    )


def format_duration(
    value_hours: Any,
    include_minutes: bool = True,
) -> str:
    """
    Convert decimal hours into hours and minutes.

    Examples
    --------
    format_duration(2.5)
    returns:
    "2 hr 30 min"

    format_duration(0.75)
    returns:
    "45 min"
    """

    total_hours = max(
        safe_float(value_hours),
        0,
    )

    whole_hours = int(
        total_hours
    )

    minutes = int(
        round(
            (
                total_hours
                - whole_hours
            )
            * 60
        )
    )

    if minutes == 60:
        whole_hours += 1
        minutes = 0

    if whole_hours == 0:
        return f"{minutes} min"

    if not include_minutes:
        return (
            f"{whole_hours} hr"
            if whole_hours == 1
            else f"{whole_hours} hrs"
        )

    hour_label = (
        "hr"
        if whole_hours == 1
        else "hrs"
    )

    if minutes == 0:
        return (
            f"{whole_hours} {hour_label}"
        )

    return (
        f"{whole_hours} {hour_label} "
        f"{minutes} min"
    )


def format_days(
    value_days: Any,
    decimal_places: int = 0,
) -> str:
    """
    Format a value as days.
    """

    days = safe_float(
        value_days
    )

    if decimal_places == 0:
        rounded_days = safe_int(
            days
        )

        label = (
            "day"
            if rounded_days == 1
            else "days"
        )

        return (
            f"{rounded_days:,} {label}"
        )

    return (
        f"{days:,.{decimal_places}f} days"
    )


# =========================================================
# CAPACITY FORMATTING
# =========================================================
def format_parcel_quantity(
    value: Any,
) -> str:
    """
    Format parcel quantity with a label.
    """

    quantity = safe_int(
        value
    )

    label = (
        "parcel"
        if quantity == 1
        else "parcels"
    )

    return (
        f"{quantity:,} {label}"
    )


def format_vehicle_count(
    value: Any,
) -> str:
    """
    Format a vehicle count.
    """

    vehicle_count = safe_int(
        value
    )

    label = (
        "vehicle"
        if vehicle_count == 1
        else "vehicles"
    )

    return (
        f"{vehicle_count:,} {label}"
    )


def format_shipments(
    value: Any,
) -> str:
    """
    Format a shipment count.
    """

    shipment_count = safe_int(
        value
    )

    label = (
        "shipment"
        if shipment_count == 1
        else "shipments"
    )

    return (
        f"{shipment_count:,} {label}"
    )


# =========================================================
# COST-RATE FORMATTING
# =========================================================
def format_cost_per_parcel(
    value: Any,
    decimal_places: int = 2,
) -> str:
    """
    Format cost per parcel.
    """

    return (
        f"{format_rm(value, decimal_places)} "
        "per parcel"
    )


def format_cost_per_kg(
    value: Any,
    decimal_places: int = 2,
) -> str:
    """
    Format cost per kilogram.
    """

    return (
        f"{format_rm(value, decimal_places)} "
        "per kg"
    )


def format_cost_per_km(
    value: Any,
    decimal_places: int = 2,
) -> str:
    """
    Format cost per kilometre.
    """

    return (
        f"{format_rm(value, decimal_places)} "
        "per km"
    )


def format_cost_per_m3(
    value: Any,
    decimal_places: int = 2,
) -> str:
    """
    Format cost per cubic metre.
    """

    return (
        f"{format_rm(value, decimal_places)} "
        "per m³"
    )


def format_rate(
    value: Any,
    unit: str,
    decimal_places: int = 2,
    currency: str = "RM",
) -> str:
    """
    Format a generic monetary rate.

    Example
    -------
    format_rate(0.25, "km")
    returns:
    "RM 0.25/km"
    """

    numeric_value = safe_float(
        value
    )

    clean_unit = str(
        unit
    ).strip()

    return (
        f"{currency} "
        f"{numeric_value:,.{decimal_places}f}"
        f"/{clean_unit}"
    )


# =========================================================
# DATE FORMATTING
# =========================================================
def format_date(
    value: Any,
    output_format: str = "%d/%m/%Y",
    default: str = "Not Available",
) -> str:
    """
    Format a date or datetime value.

    Supported input:
    - datetime
    - date
    - ISO-formatted date string
    - DD/MM/YYYY string
    """

    if value is None or value == "":
        return default

    if isinstance(
        value,
        datetime,
    ):
        return value.strftime(
            output_format
        )

    if isinstance(
        value,
        date,
    ):
        return value.strftime(
            output_format
        )

    date_text = str(
        value
    ).strip()

    input_formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M",
    ]

    for input_format in input_formats:
        try:
            parsed_date = datetime.strptime(
                date_text,
                input_format,
            )

            return parsed_date.strftime(
                output_format
            )

        except ValueError:
            continue

    return default


def format_datetime(
    value: Any,
    output_format: str = "%d/%m/%Y %H:%M",
    default: str = "Not Available",
) -> str:
    """
    Format a datetime value.
    """

    return format_date(
        value=value,
        output_format=output_format,
        default=default,
    )


def format_month_year(
    value: Any,
    default: str = "Not Available",
) -> str:
    """
    Format a date as month and year.

    Example
    -------
    July 2026
    """

    return format_date(
        value=value,
        output_format="%B %Y",
        default=default,
    )


# =========================================================
# TEXT FORMATTING
# =========================================================
def clean_text(
    value: Any,
    default: str = "",
) -> str:
    """
    Convert a value to clean text and remove extra spaces.
    """

    if value is None:
        return default

    text = " ".join(
        str(value).split()
    )

    return text or default


def title_case_text(
    value: Any,
    default: str = "",
) -> str:
    """
    Convert text to title case.
    """

    text = clean_text(
        value,
        default=default,
    )

    return text.title()


def normalise_region_name(
    region_name: Any,
) -> str:
    """
    Standardise Malaysian region names.

    Corrects common spelling differences.
    """

    region = clean_text(
        region_name
    ).lower()

    region_mapping = {
        "northern": "Northern",
        "north": "Northern",

        "southern": "Southern",
        "sourthern": "Southern",
        "south": "Southern",

        "central": "Central",

        "east coast": "East Coast",
        "east-coast": "East Coast",
        "eastcoast": "East Coast",

        "sabah": "Sabah",
        "sarawak": "Sarawak",
    }

    return region_mapping.get(
        region,
        title_case_text(region),
    )


def normalise_vehicle_type(
    vehicle_type: Any,
) -> str:
    """
    Standardise vehicle-type names.
    """

    vehicle = clean_text(
        vehicle_type
    ).lower()

    vehicle_mapping = {
        "motorbike": "Motorcycle",
        "motorcycle": "Motorcycle",
        "bike": "Motorcycle",

        "van": "Van",

        "1 ton lorry": "1-Ton Lorry",
        "1-ton lorry": "1-Ton Lorry",
        "1 tonne lorry": "1-Ton Lorry",

        "3 ton lorry": "3-Ton Lorry",
        "3-ton lorry": "3-Ton Lorry",
        "3 tonne lorry": "3-Ton Lorry",
    }

    return vehicle_mapping.get(
        vehicle,
        title_case_text(vehicle),
    )


def normalise_fuel_type(
    fuel_type: Any,
) -> str:
    """
    Standardise fuel-type names.
    """

    fuel = clean_text(
        fuel_type
    ).lower()

    fuel_mapping = {
        "petrol": "Petrol RON95",
        "petrol ron95": "Petrol RON95",
        "ron95": "Petrol RON95",
        "diesel": "Diesel",
    }

    return fuel_mapping.get(
        fuel,
        title_case_text(fuel),
    )


def format_route(
    origin: Any,
    destination: Any,
    separator: str = " → ",
) -> str:
    """
    Format an origin-to-destination route.
    """

    origin_text = clean_text(
        origin,
        default="Not Available",
    )

    destination_text = clean_text(
        destination,
        default="Not Available",
    )

    return (
        f"{origin_text}"
        f"{separator}"
        f"{destination_text}"
    )


# =========================================================
# STATUS FORMATTING
# =========================================================
def format_boolean_status(
    value: Any,
    true_text: str = "Yes",
    false_text: str = "No",
) -> str:
    """
    Format a boolean value as readable text.
    """

    return (
        true_text
        if bool(value)
        else false_text
    )


def format_compliance_status(
    compliant: Any,
) -> str:
    """
    Format parcel-compliance status.
    """

    return (
        "Compliant"
        if bool(compliant)
        else "Non-Compliant"
    )


def format_availability_status(
    shortfall: Any,
) -> str:
    """
    Format fleet availability based on shortfall.
    """

    fleet_shortfall = safe_int(
        shortfall
    )

    if fleet_shortfall > 0:
        return (
            f"Shortfall of "
            f"{fleet_shortfall:,} vehicle(s)"
        )

    return "Available"


# =========================================================
# TABLE FORMATTING
# =========================================================
def format_dataframe_currency(
    dataframe,
    columns: list[str],
    currency: str = "RM",
    decimal_places: int = 2,
):
    """
    Return a copy of a DataFrame with selected columns
    formatted as currency strings.

    Import pandas only in the page or caller.
    This function works with any DataFrame-like object that
    supports .copy(), column access and .map().
    """

    formatted_dataframe = (
        dataframe.copy()
    )

    for column in columns:
        if column in formatted_dataframe.columns:
            formatted_dataframe[column] = (
                formatted_dataframe[column]
                .map(
                    lambda value: format_currency(
                        value=value,
                        currency=currency,
                        decimal_places=(
                            decimal_places
                        ),
                    )
                )
            )

    return formatted_dataframe


def format_dataframe_percentage(
    dataframe,
    columns: list[str],
    decimal_places: int = 1,
):
    """
    Return a copy of a DataFrame with selected columns
    formatted as percentages.
    """

    formatted_dataframe = (
        dataframe.copy()
    )

    for column in columns:
        if column in formatted_dataframe.columns:
            formatted_dataframe[column] = (
                formatted_dataframe[column]
                .map(
                    lambda value: format_percentage(
                        value=value,
                        decimal_places=(
                            decimal_places
                        ),
                    )
                )
            )

    return formatted_dataframe


def format_dataframe_number(
    dataframe,
    columns: list[str],
    decimal_places: int = 2,
):
    """
    Return a copy of a DataFrame with selected numeric
    columns formatted as strings.
    """

    formatted_dataframe = (
        dataframe.copy()
    )

    for column in columns:
        if column in formatted_dataframe.columns:
            formatted_dataframe[column] = (
                formatted_dataframe[column]
                .map(
                    lambda value: format_number(
                        value=value,
                        decimal_places=(
                            decimal_places
                        ),
                    )
                )
            )

    return formatted_dataframe