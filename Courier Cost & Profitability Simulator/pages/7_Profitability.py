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

operating_cost = st.session_state.get(
    "operating_cost",
    {},
)

cost_per_parcel = st.session_state.get(
    "cost_per_parcel",
    {},
)


required_pages = {
    "Shipment Information": shipment,
    "Route Intelligence": route,
    "Parcel Assessment": parcel,
    "Fleet Capacity": fleet,
    "Operating Cost": operating_cost,
    "Cost per Parcel": cost_per_parcel,
}

incomplete_pages = [
    page_name
    for page_name, page_data in required_pages.items()
    if not page_data
]

if incomplete_pages:
    st.warning(
        "Complete and save the following pages before calculating "
        "profitability: "
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

route_id = route.get(
    "route_id",
    "",
)

route_category = route.get(
    "route_category",
    "",
)

parcel_type = parcel.get(
    "parcel_type",
    "",
)

parcel_quantity = int(
    cost_per_parcel.get(
        "parcel_quantity",
        0,
    )
)

monthly_parcel_quantity = int(
    cost_per_parcel.get(
        "monthly_parcel_quantity",
        0,
    )
)

shipments_per_month = int(
    cost_per_parcel.get(
        "shipments_per_month",
        0,
    )
)

vehicle_type = cost_per_parcel.get(
    "vehicle_type",
    "",
)

planned_fleet_size = int(
    cost_per_parcel.get(
        "planned_fleet_size",
        0,
    )
)

overall_utilisation_pct = float(
    cost_per_parcel.get(
        "overall_utilisation_pct",
        0,
    )
)

direct_cost_per_parcel = float(
    cost_per_parcel.get(
        "direct_cost_per_parcel",
        0,
    )
)

fixed_cost_per_parcel = float(
    cost_per_parcel.get(
        "fixed_cost_per_parcel",
        0,
    )
)

total_cost_per_parcel = float(
    cost_per_parcel.get(
        "total_cost_per_parcel",
        0,
    )
)

total_cost_per_shipment = float(
    cost_per_parcel.get(
        "total_cost_per_shipment",
        0,
    )
)

total_monthly_operating_cost = float(
    cost_per_parcel.get(
        "total_monthly_operating_cost",
        0,
    )
)

cost_per_actual_kg = float(
    cost_per_parcel.get(
        "cost_per_actual_kg",
        0,
    )
)

cost_per_chargeable_kg = float(
    cost_per_parcel.get(
        "cost_per_chargeable_kg",
        0,
    )
)

chargeable_weight_kg = float(
    cost_per_parcel.get(
        "chargeable_weight_kg",
        0,
    )
)


# =========================================================
# VALIDATION
# =========================================================
required_numeric_values = {
    "Parcel quantity": parcel_quantity,
    "Monthly parcel quantity": monthly_parcel_quantity,
    "Shipments per month": shipments_per_month,
    "Total cost per parcel": total_cost_per_parcel,
    "Total cost per shipment": total_cost_per_shipment,
}

invalid_values = [
    field_name
    for field_name, field_value in required_numeric_values.items()
    if field_value is None or float(field_value) <= 0
]

if invalid_values:
    st.error(
        "The following profitability inputs are missing or invalid: "
        + ", ".join(invalid_values)
    )

    st.info(
        "Return to Page 6 and review the saved cost-per-parcel "
        "assessment."
    )

    st.stop()


# =========================================================
# SESSION STATE
# =========================================================
if "profitability" not in st.session_state:
    st.session_state.profitability = {}


# =========================================================
# PAGE TITLE
# =========================================================
st.markdown(
    '<div class="main-title">📈 Profitability Analysis</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-subtitle">
        Assess selling price, revenue, profit, margin and
        break-even requirements for the selected courier service.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# PROFITABILITY BASIS
# =========================================================
cost_basis(
    "Profitability Basis",
    """
    Revenue is calculated using the selected selling-price method
    and the total number of parcels.

    Profit equals revenue less total operating cost. Profit margin
    measures profit as a percentage of revenue, while mark-up measures
    profit as a percentage of cost.

    The break-even selling price is equal to the total cost per parcel.
    A target-margin selling price is calculated using the selected
    profit-margin objective.
    """,
)


# =========================================================
# SHIPMENT SUMMARY
# =========================================================
st.markdown(
    '<div class="section-title">Commercial Summary</div>',
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
    st.markdown("**Vehicle Type**")
    st.write(vehicle_type)

with summary_col4:
    st.markdown("**Parcel Type**")
    st.write(parcel_type)


cost_summary_col1, cost_summary_col2, cost_summary_col3 = (
    st.columns(3)
)

with cost_summary_col1:
    st.metric(
        "Cost per Parcel",
        f"RM {total_cost_per_parcel:,.2f}",
    )

with cost_summary_col2:
    st.metric(
        "Cost per Shipment",
        f"RM {total_cost_per_shipment:,.2f}",
    )

with cost_summary_col3:
    st.metric(
        "Monthly Operating Cost",
        f"RM {total_monthly_operating_cost:,.2f}",
    )


# =========================================================
# PRICING METHOD
# =========================================================
st.markdown(
    '<div class="section-title">Pricing Assumptions</div>',
    unsafe_allow_html=True,
)

pricing_method = st.radio(
    "Selling Price Method",
    options=[
        "Price per Parcel",
        "Mark-up on Cost",
        "Target Profit Margin",
        "Price per Chargeable kg",
    ],
    horizontal=True,
    key="profit_pricing_method",
)


# =========================================================
# DEFAULT ASSUMPTIONS
# =========================================================
default_markup_pct = 25.0
default_target_margin_pct = 20.0
default_price_per_chargeable_kg = max(
    cost_per_chargeable_kg * 1.25,
    0.01,
)


# =========================================================
# SELLING PRICE CALCULATION
# =========================================================
selling_price_per_parcel = total_cost_per_parcel
markup_pct_input = 0.0
target_margin_pct_input = 0.0
price_per_chargeable_kg = 0.0


if pricing_method == "Price per Parcel":
    pricing_col1, pricing_col2 = st.columns(2)

    with pricing_col1:
        selling_price_per_parcel = st.number_input(
            "Selling Price per Parcel (RM)",
            min_value=0.01,
            value=float(
                round(
                    total_cost_per_parcel * 1.25,
                    2,
                )
            ),
            step=0.10,
            key="profit_selling_price_per_parcel",
        )

    with pricing_col2:
        implied_markup_pct = (
            (
                selling_price_per_parcel
                - total_cost_per_parcel
            )
            / total_cost_per_parcel
            * 100
        )

        st.metric(
            "Implied Mark-up",
            f"{implied_markup_pct:,.1f}%",
        )


elif pricing_method == "Mark-up on Cost":
    pricing_col1, pricing_col2 = st.columns(2)

    with pricing_col1:
        markup_pct_input = st.number_input(
            "Mark-up on Cost (%)",
            min_value=-100.0,
            max_value=500.0,
            value=default_markup_pct,
            step=1.0,
            key="profit_markup_pct",
        )

    selling_price_per_parcel = (
        total_cost_per_parcel
        * (
            1
            + markup_pct_input / 100
        )
    )

    with pricing_col2:
        st.metric(
            "Calculated Selling Price",
            f"RM {selling_price_per_parcel:,.2f}",
        )


elif pricing_method == "Target Profit Margin":
    pricing_col1, pricing_col2 = st.columns(2)

    with pricing_col1:
        target_margin_pct_input = st.number_input(
            "Target Profit Margin (%)",
            min_value=-100.0,
            max_value=99.0,
            value=default_target_margin_pct,
            step=1.0,
            key="profit_target_margin_pct",
            help=(
                "Profit margin is calculated as profit divided "
                "by revenue. A margin of 100% cannot be used."
            ),
        )

    margin_decimal = (
        target_margin_pct_input
        / 100
    )

    if margin_decimal >= 1:
        selling_price_per_parcel = 0.0

    else:
        selling_price_per_parcel = (
            total_cost_per_parcel
            / (
                1
                - margin_decimal
            )
        )

    with pricing_col2:
        st.metric(
            "Calculated Selling Price",
            f"RM {selling_price_per_parcel:,.2f}",
        )


else:
    pricing_col1, pricing_col2, pricing_col3 = (
        st.columns(3)
    )

    with pricing_col1:
        price_per_chargeable_kg = st.number_input(
            "Selling Price per Chargeable kg (RM)",
            min_value=0.01,
            value=float(
                round(
                    default_price_per_chargeable_kg,
                    2,
                )
            ),
            step=0.10,
            key="profit_price_per_chargeable_kg",
        )

    chargeable_weight_per_parcel = (
        chargeable_weight_kg
        / parcel_quantity
        if parcel_quantity > 0
        else 0
    )

    selling_price_per_parcel = (
        price_per_chargeable_kg
        * chargeable_weight_per_parcel
    )

    with pricing_col2:
        st.metric(
            "Chargeable Weight per Parcel",
            f"{chargeable_weight_per_parcel:,.2f} kg",
        )

    with pricing_col3:
        st.metric(
            "Selling Price per Parcel",
            f"RM {selling_price_per_parcel:,.2f}",
        )


# =========================================================
# OPTIONAL COMMERCIAL ADJUSTMENTS
# =========================================================
st.markdown(
    '<div class="section-title">Commercial Adjustments</div>',
    unsafe_allow_html=True,
)

adjustment_col1, adjustment_col2, adjustment_col3 = (
    st.columns(3)
)

with adjustment_col1:
    discount_pct = st.number_input(
        "Customer Discount (%)",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=1.0,
        key="profit_discount_pct",
    )

with adjustment_col2:
    surcharge_pct = st.number_input(
        "Service Surcharge (%)",
        min_value=0.0,
        max_value=500.0,
        value=0.0,
        step=1.0,
        key="profit_surcharge_pct",
        help=(
            "Examples include fast-delivery, remote-area or "
            "special-handling surcharges."
        ),
    )

with adjustment_col3:
    additional_fee_per_shipment = st.number_input(
        "Additional Fee per Shipment (RM)",
        min_value=0.0,
        value=0.0,
        step=10.0,
        key="profit_additional_fee",
    )


gross_price_per_parcel = selling_price_per_parcel

discount_amount_per_parcel = (
    gross_price_per_parcel
    * discount_pct
    / 100
)

price_after_discount = (
    gross_price_per_parcel
    - discount_amount_per_parcel
)

surcharge_amount_per_parcel = (
    price_after_discount
    * surcharge_pct
    / 100
)

net_selling_price_per_parcel = (
    price_after_discount
    + surcharge_amount_per_parcel
)


# =========================================================
# REVENUE CALCULATION
# =========================================================
parcel_revenue_per_shipment = (
    net_selling_price_per_parcel
    * parcel_quantity
)

total_revenue_per_shipment = (
    parcel_revenue_per_shipment
    + additional_fee_per_shipment
)

monthly_revenue = (
    total_revenue_per_shipment
    * shipments_per_month
)


# =========================================================
# PROFIT CALCULATION
# =========================================================
profit_per_parcel = (
    net_selling_price_per_parcel
    - total_cost_per_parcel
)

profit_per_shipment = (
    total_revenue_per_shipment
    - total_cost_per_shipment
)

monthly_profit = (
    monthly_revenue
    - total_monthly_operating_cost
)


# =========================================================
# MARGIN AND MARK-UP
# =========================================================
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

monthly_profit_margin_pct = (
    monthly_profit
    / monthly_revenue
    * 100
    if monthly_revenue > 0
    else 0
)


# =========================================================
# BREAK-EVEN CALCULATIONS
# =========================================================
break_even_price_per_parcel = (
    total_cost_per_parcel
)

break_even_revenue_per_shipment = (
    total_cost_per_shipment
)

break_even_monthly_revenue = (
    total_monthly_operating_cost
)


# Break-even parcel quantity based on current net price,
# assuming shipment cost remains unchanged.
break_even_parcel_quantity = (
    math.ceil(
        (
            total_cost_per_shipment
            - additional_fee_per_shipment
        )
        / net_selling_price_per_parcel
    )
    if net_selling_price_per_parcel > 0
    else 0
)


# =========================================================
# TARGET-MARGIN SELLING PRICES
# =========================================================
st.markdown(
    '<div class="section-title">Target Margin Analysis</div>',
    unsafe_allow_html=True,
)

target_analysis_col1, target_analysis_col2 = (
    st.columns(2)
)

with target_analysis_col1:
    analysis_target_margin_pct = st.slider(
        "Target Margin for Comparison (%)",
        min_value=0,
        max_value=80,
        value=20,
        step=5,
        key="profit_analysis_target_margin",
    )

with target_analysis_col2:
    target_margin_decimal = (
        analysis_target_margin_pct
        / 100
    )

    target_selling_price_per_parcel = (
        total_cost_per_parcel
        / (
            1
            - target_margin_decimal
        )
        if target_margin_decimal < 1
        else 0
    )

    st.metric(
        "Required Price per Parcel",
        f"RM {target_selling_price_per_parcel:,.2f}",
    )


target_price_difference = (
    net_selling_price_per_parcel
    - target_selling_price_per_parcel
)

target_price_difference_pct = (
    target_price_difference
    / target_selling_price_per_parcel
    * 100
    if target_selling_price_per_parcel > 0
    else 0
)


# =========================================================
# PROFITABILITY RESULTS
# =========================================================
st.markdown(
    '<div class="section-title">Profitability Results</div>',
    unsafe_allow_html=True,
)

result_col1, result_col2, result_col3, result_col4 = (
    st.columns(4)
)

with result_col1:
    st.metric(
        "Net Selling Price per Parcel",
        f"RM {net_selling_price_per_parcel:,.2f}",
    )

with result_col2:
    st.metric(
        "Profit per Parcel",
        f"RM {profit_per_parcel:,.2f}",
        delta=f"RM {profit_per_parcel:,.2f}",
    )

with result_col3:
    st.metric(
        "Profit Margin",
        f"{profit_margin_pct:,.1f}%",
    )

with result_col4:
    st.metric(
        "Mark-up on Cost",
        f"{markup_on_cost_pct:,.1f}%",
    )


shipment_result_col1, shipment_result_col2, shipment_result_col3 = (
    st.columns(3)
)

with shipment_result_col1:
    st.metric(
        "Revenue per Shipment",
        f"RM {total_revenue_per_shipment:,.2f}",
    )

with shipment_result_col2:
    st.metric(
        "Cost per Shipment",
        f"RM {total_cost_per_shipment:,.2f}",
    )

with shipment_result_col3:
    st.metric(
        "Profit per Shipment",
        f"RM {profit_per_shipment:,.2f}",
        delta=f"RM {profit_per_shipment:,.2f}",
    )


# =========================================================
# MONTHLY PROFITABILITY
# =========================================================
st.markdown(
    '<div class="section-title">Monthly Profitability Projection</div>',
    unsafe_allow_html=True,
)

monthly_col1, monthly_col2, monthly_col3, monthly_col4 = (
    st.columns(4)
)

with monthly_col1:
    st.metric(
        "Monthly Parcel Volume",
        f"{monthly_parcel_quantity:,}",
    )

with monthly_col2:
    st.metric(
        "Monthly Revenue",
        f"RM {monthly_revenue:,.2f}",
    )

with monthly_col3:
    st.metric(
        "Monthly Cost",
        f"RM {total_monthly_operating_cost:,.2f}",
    )

with monthly_col4:
    st.metric(
        "Monthly Profit",
        f"RM {monthly_profit:,.2f}",
        delta=f"{monthly_profit_margin_pct:,.1f}% margin",
    )


# =========================================================
# PROFITABILITY STATUS
# =========================================================
st.markdown(
    '<div class="section-title">Profitability Assessment</div>',
    unsafe_allow_html=True,
)


def classify_profitability(
    profit_value: float,
    margin_pct: float,
) -> tuple[str, str]:
    """
    Return profitability classification and explanation.
    """

    if profit_value < 0:
        return (
            "Loss-Making",
            (
                "Revenue does not cover the total operating cost. "
                "Increase the selling price, improve fleet utilisation, "
                "reduce cost or consolidate more parcels."
            ),
        )

    if margin_pct < 5:
        return (
            "Low Margin",
            (
                "The service is profitable, but the margin provides "
                "limited protection against fuel, labour or volume "
                "changes."
            ),
        )

    if margin_pct < 15:
        return (
            "Moderate Margin",
            (
                "The service is profitable with a reasonable margin, "
                "but pricing and cost assumptions should continue to "
                "be monitored."
            ),
        )

    if margin_pct < 30:
        return (
            "Healthy Margin",
            (
                "The service generates a healthy profit margin under "
                "the selected operating and pricing assumptions."
            ),
        )

    return (
        "High Margin",
        (
            "The service generates a strong margin. Confirm that the "
            "selling price remains commercially competitive and that "
            "all relevant operating costs have been included."
        ),
    )


profitability_status, profitability_message = (
    classify_profitability(
        profit_per_shipment,
        profit_margin_pct,
    )
)


status_col1, status_col2 = st.columns(2)

with status_col1:
    st.markdown("**Profitability Status**")

    if profitability_status in {
        "Healthy Margin",
        "High Margin",
    }:
        st.success(
            f"{profitability_status}: "
            f"{profitability_message}"
        )

    elif profitability_status in {
        "Moderate Margin",
        "Low Margin",
    }:
        st.warning(
            f"{profitability_status}: "
            f"{profitability_message}"
        )

    else:
        st.error(
            f"{profitability_status}: "
            f"{profitability_message}"
        )


with status_col2:
    st.markdown("**Target Margin Position**")

    if target_price_difference >= 0:
        st.success(
            f"The current net price is RM "
            f"{target_price_difference:,.2f} per parcel above "
            f"the price required for a "
            f"{analysis_target_margin_pct}% target margin."
        )

    else:
        st.warning(
            f"The current net price is RM "
            f"{abs(target_price_difference):,.2f} per parcel below "
            f"the price required for a "
            f"{analysis_target_margin_pct}% target margin."
        )


# =========================================================
# BREAK-EVEN ANALYSIS
# =========================================================
st.markdown(
    '<div class="section-title">Break-Even Analysis</div>',
    unsafe_allow_html=True,
)

break_even_col1, break_even_col2, break_even_col3 = (
    st.columns(3)
)

with break_even_col1:
    st.metric(
        "Break-Even Price per Parcel",
        f"RM {break_even_price_per_parcel:,.2f}",
    )

with break_even_col2:
    st.metric(
        "Break-Even Revenue per Shipment",
        f"RM {break_even_revenue_per_shipment:,.2f}",
    )

with break_even_col3:
    st.metric(
        "Break-Even Parcel Quantity",
        f"{break_even_parcel_quantity:,}",
    )


if (
    net_selling_price_per_parcel
    < break_even_price_per_parcel
):
    st.error(
        "The selected selling price is below the break-even "
        "cost per parcel."
    )

elif (
    net_selling_price_per_parcel
    == break_even_price_per_parcel
):
    st.warning(
        "The selected selling price is equal to the break-even "
        "cost per parcel. No profit is generated."
    )

else:
    st.success(
        "The selected selling price is above the break-even "
        "cost per parcel."
    )


# =========================================================
# PRICE SENSITIVITY
# =========================================================
st.markdown(
    '<div class="section-title">Selling Price Sensitivity</div>',
    unsafe_allow_html=True,
)

sensitivity_col1, sensitivity_col2 = st.columns(2)

with sensitivity_col1:
    price_change_pct = st.slider(
        "Selling Price Change (%)",
        min_value=-50,
        max_value=100,
        value=0,
        step=5,
        key="profit_price_change_pct",
    )

with sensitivity_col2:
    adjusted_selling_price_per_parcel = (
        net_selling_price_per_parcel
        * (
            1
            + price_change_pct / 100
        )
    )

    st.metric(
        "Adjusted Selling Price",
        f"RM {adjusted_selling_price_per_parcel:,.2f}",
    )


adjusted_revenue_per_shipment = (
    adjusted_selling_price_per_parcel
    * parcel_quantity
    + additional_fee_per_shipment
)

adjusted_profit_per_shipment = (
    adjusted_revenue_per_shipment
    - total_cost_per_shipment
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
    * shipments_per_month
)

adjusted_monthly_profit = (
    adjusted_monthly_revenue
    - total_monthly_operating_cost
)


sensitivity_result_col1, sensitivity_result_col2, sensitivity_result_col3 = (
    st.columns(3)
)

with sensitivity_result_col1:
    st.metric(
        "Adjusted Revenue per Shipment",
        f"RM {adjusted_revenue_per_shipment:,.2f}",
    )

with sensitivity_result_col2:
    st.metric(
        "Adjusted Profit per Shipment",
        f"RM {adjusted_profit_per_shipment:,.2f}",
        delta=(
            f"RM "
            f"{adjusted_profit_per_shipment - profit_per_shipment:,.2f}"
        ),
    )

with sensitivity_result_col3:
    st.metric(
        "Adjusted Profit Margin",
        f"{adjusted_profit_margin_pct:,.1f}%",
    )


# =========================================================
# PROFITABILITY BREAKDOWN TABLE
# =========================================================
st.markdown(
    '<div class="section-title">Profitability Breakdown</div>',
    unsafe_allow_html=True,
)

profitability_breakdown = pd.DataFrame(
    [
        {
            "Measure": "Gross price per parcel",
            "Per Parcel (RM)": gross_price_per_parcel,
            "Per Shipment (RM)": (
                gross_price_per_parcel
                * parcel_quantity
            ),
            "Monthly (RM)": (
                gross_price_per_parcel
                * monthly_parcel_quantity
            ),
        },
        {
            "Measure": "Customer discount",
            "Per Parcel (RM)": (
                -discount_amount_per_parcel
            ),
            "Per Shipment (RM)": (
                -discount_amount_per_parcel
                * parcel_quantity
            ),
            "Monthly (RM)": (
                -discount_amount_per_parcel
                * monthly_parcel_quantity
            ),
        },
        {
            "Measure": "Service surcharge",
            "Per Parcel (RM)": (
                surcharge_amount_per_parcel
            ),
            "Per Shipment (RM)": (
                surcharge_amount_per_parcel
                * parcel_quantity
            ),
            "Monthly (RM)": (
                surcharge_amount_per_parcel
                * monthly_parcel_quantity
            ),
        },
        {
            "Measure": "Additional shipment fee",
            "Per Parcel (RM)": (
                additional_fee_per_shipment
                / parcel_quantity
            ),
            "Per Shipment (RM)": (
                additional_fee_per_shipment
            ),
            "Monthly (RM)": (
                additional_fee_per_shipment
                * shipments_per_month
            ),
        },
        {
            "Measure": "Total revenue",
            "Per Parcel (RM)": (
                total_revenue_per_shipment
                / parcel_quantity
            ),
            "Per Shipment (RM)": (
                total_revenue_per_shipment
            ),
            "Monthly (RM)": monthly_revenue,
        },
        {
            "Measure": "Direct operating cost",
            "Per Parcel (RM)": (
                direct_cost_per_parcel
            ),
            "Per Shipment (RM)": (
                direct_cost_per_parcel
                * parcel_quantity
            ),
            "Monthly (RM)": (
                direct_cost_per_parcel
                * monthly_parcel_quantity
            ),
        },
        {
            "Measure": "Fixed operating cost",
            "Per Parcel (RM)": (
                fixed_cost_per_parcel
            ),
            "Per Shipment (RM)": (
                fixed_cost_per_parcel
                * parcel_quantity
            ),
            "Monthly (RM)": (
                fixed_cost_per_parcel
                * monthly_parcel_quantity
            ),
        },
        {
            "Measure": "Total operating cost",
            "Per Parcel (RM)": (
                total_cost_per_parcel
            ),
            "Per Shipment (RM)": (
                total_cost_per_shipment
            ),
            "Monthly (RM)": (
                total_monthly_operating_cost
            ),
        },
        {
            "Measure": "Profit",
            "Per Parcel (RM)": profit_per_parcel,
            "Per Shipment (RM)": (
                profit_per_shipment
            ),
            "Monthly (RM)": monthly_profit,
        },
    ]
)


display_profitability_breakdown = (
    profitability_breakdown.copy()
)

for column in [
    "Per Parcel (RM)",
    "Per Shipment (RM)",
    "Monthly (RM)",
]:
    display_profitability_breakdown[column] = (
        display_profitability_breakdown[column]
        .map(
            lambda value: f"{value:,.2f}"
        )
    )


st.dataframe(
    display_profitability_breakdown,
    hide_index=True,
    use_container_width=True,
)


# =========================================================
# PRICING REFERENCE TABLE
# =========================================================
with st.expander(
    "View Pricing Reference",
    expanded=False,
):
    pricing_reference = pd.DataFrame(
        {
            "Pricing Measure": [
                "Total cost per parcel",
                "Break-even selling price",
                "Current gross selling price",
                "Discount per parcel",
                "Surcharge per parcel",
                "Current net selling price",
                (
                    f"Price required for "
                    f"{analysis_target_margin_pct}% margin"
                ),
                "Profit per parcel",
                "Profit margin",
                "Mark-up on cost",
            ],
            "Value": [
                f"RM {total_cost_per_parcel:,.2f}",
                f"RM {break_even_price_per_parcel:,.2f}",
                f"RM {gross_price_per_parcel:,.2f}",
                f"RM {discount_amount_per_parcel:,.2f}",
                f"RM {surcharge_amount_per_parcel:,.2f}",
                f"RM {net_selling_price_per_parcel:,.2f}",
                (
                    f"RM "
                    f"{target_selling_price_per_parcel:,.2f}"
                ),
                f"RM {profit_per_parcel:,.2f}",
                f"{profit_margin_pct:,.1f}%",
                f"{markup_on_cost_pct:,.1f}%",
            ],
        }
    )

    st.dataframe(
        pricing_reference,
        hide_index=True,
        use_container_width=True,
    )


# =========================================================
# SAVE PROFITABILITY
# =========================================================
st.markdown(
    "<br>",
    unsafe_allow_html=True,
)

button_col1, button_col2, button_col3 = (
    st.columns([1, 1, 2])
)

with button_col1:
    save_profitability = st.button(
        "💾 Save Profitability",
        type="primary",
        use_container_width=True,
    )

with button_col2:
    clear_profitability = st.button(
        "🗑️ Clear",
        use_container_width=True,
    )


if save_profitability:
    st.session_state.profitability = {
        "route_id": route_id,
        "route_category": route_category,
        "origin_region": origin_region,
        "origin_state": origin_state,
        "destination_region": destination_region,
        "destination_state": destination_state,
        "service_level": service_level,

        "parcel_type": parcel_type,
        "parcel_quantity": int(
            parcel_quantity
        ),
        "monthly_parcel_quantity": int(
            monthly_parcel_quantity
        ),
        "shipments_per_month": int(
            shipments_per_month
        ),

        "vehicle_type": vehicle_type,
        "planned_fleet_size": int(
            planned_fleet_size
        ),
        "overall_utilisation_pct": float(
            overall_utilisation_pct
        ),

        "pricing_method": pricing_method,
        "gross_price_per_parcel": float(
            gross_price_per_parcel
        ),
        "discount_pct": float(
            discount_pct
        ),
        "discount_amount_per_parcel": float(
            discount_amount_per_parcel
        ),
        "surcharge_pct": float(
            surcharge_pct
        ),
        "surcharge_amount_per_parcel": float(
            surcharge_amount_per_parcel
        ),
        "net_selling_price_per_parcel": float(
            net_selling_price_per_parcel
        ),
        "additional_fee_per_shipment": float(
            additional_fee_per_shipment
        ),

        "price_per_chargeable_kg": float(
            price_per_chargeable_kg
        ),
        "markup_pct_input": float(
            markup_pct_input
        ),
        "target_margin_pct_input": float(
            target_margin_pct_input
        ),

        "direct_cost_per_parcel": float(
            direct_cost_per_parcel
        ),
        "fixed_cost_per_parcel": float(
            fixed_cost_per_parcel
        ),
        "total_cost_per_parcel": float(
            total_cost_per_parcel
        ),
        "total_cost_per_shipment": float(
            total_cost_per_shipment
        ),
        "total_monthly_operating_cost": float(
            total_monthly_operating_cost
        ),

        "parcel_revenue_per_shipment": float(
            parcel_revenue_per_shipment
        ),
        "total_revenue_per_shipment": float(
            total_revenue_per_shipment
        ),
        "monthly_revenue": float(
            monthly_revenue
        ),

        "profit_per_parcel": float(
            profit_per_parcel
        ),
        "profit_per_shipment": float(
            profit_per_shipment
        ),
        "monthly_profit": float(
            monthly_profit
        ),

        "profit_margin_pct": float(
            profit_margin_pct
        ),
        "markup_on_cost_pct": float(
            markup_on_cost_pct
        ),
        "monthly_profit_margin_pct": float(
            monthly_profit_margin_pct
        ),

        "profitability_status": (
            profitability_status
        ),
        "profitability_message": (
            profitability_message
        ),

        "break_even_price_per_parcel": float(
            break_even_price_per_parcel
        ),
        "break_even_revenue_per_shipment": float(
            break_even_revenue_per_shipment
        ),
        "break_even_monthly_revenue": float(
            break_even_monthly_revenue
        ),
        "break_even_parcel_quantity": int(
            break_even_parcel_quantity
        ),

        "analysis_target_margin_pct": float(
            analysis_target_margin_pct
        ),
        "target_selling_price_per_parcel": float(
            target_selling_price_per_parcel
        ),
        "target_price_difference": float(
            target_price_difference
        ),
        "target_price_difference_pct": float(
            target_price_difference_pct
        ),

        "price_change_pct": float(
            price_change_pct
        ),
        "adjusted_selling_price_per_parcel": float(
            adjusted_selling_price_per_parcel
        ),
        "adjusted_revenue_per_shipment": float(
            adjusted_revenue_per_shipment
        ),
        "adjusted_profit_per_shipment": float(
            adjusted_profit_per_shipment
        ),
        "adjusted_profit_margin_pct": float(
            adjusted_profit_margin_pct
        ),
        "adjusted_monthly_revenue": float(
            adjusted_monthly_revenue
        ),
        "adjusted_monthly_profit": float(
            adjusted_monthly_profit
        ),

        "profitability_breakdown": (
            profitability_breakdown.to_dict(
                orient="records"
            )
        ),
    }

    st.success(
        "Profitability assessment has been saved successfully."
    )


if clear_profitability:
    st.session_state.profitability = {}

    keys_to_clear = [
        "profit_pricing_method",
        "profit_selling_price_per_parcel",
        "profit_markup_pct",
        "profit_target_margin_pct",
        "profit_price_per_chargeable_kg",
        "profit_discount_pct",
        "profit_surcharge_pct",
        "profit_additional_fee",
        "profit_analysis_target_margin",
        "profit_price_change_pct",
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
    "profitability"
):
    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )

    if st.button(
        "Continue to Scenario Simulation ➡",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/8_Scenario_Simulation.py"
        )