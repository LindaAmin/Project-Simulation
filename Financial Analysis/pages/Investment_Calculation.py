import streamlit as st
import pandas as pd
from datetime import date

from utils.page_configuration import page_config, page_style, page_title


# Must be the first Streamlit calls on this page.
page_config()
page_style()
page_title()


# ==========================================================
# SESSION STATE
# ==========================================================
DEFAULT_STATE = {
    "investments": [],
    "custom_rates": [],
    "pending_investment_delete": None,
    "pending_rate_delete": None,
}

for state_key, default_value in DEFAULT_STATE.items():
    if state_key not in st.session_state:
        st.session_state[state_key] = default_value


# ==========================================================
# CONSTANTS AND FORMATTING
# ==========================================================
INVESTMENT_SOURCES = [
    "Cash",
    "EPF",
    "ASB",
    "Bank – Fixed Deposit",
    "Others",
]

INVESTMENT_DESTINATIONS = [
    "Investment Agency A",
    "Investment Agency B",
    "Others",
]

STANDARD_DIVIDEND_RATES = {
    2020: {"Cash": 0.00, "EPF": 5.20, "ASB": 5.00, "Bank – Fixed Deposit": 2.15},
    2021: {"Cash": 0.00, "EPF": 6.10, "ASB": 4.60, "Bank – Fixed Deposit": 2.05},
    2022: {"Cash": 0.00, "EPF": 5.35, "ASB": 4.60, "Bank – Fixed Deposit": 2.75},
    2023: {"Cash": 0.00, "EPF": 5.50, "ASB": 5.25, "Bank – Fixed Deposit": 3.40},
    2024: {"Cash": 0.00, "EPF": 6.30, "ASB": 5.50, "Bank – Fixed Deposit": 3.30},
    2025: {"Cash": 0.00, "EPF": 6.15, "ASB": 5.75, "Bank – Fixed Deposit": 3.00},
    2026: {"Cash": 0.00, "EPF": 5.77, "ASB": 5.12, "Bank – Fixed Deposit": 2.80},
}


def format_rm(value):
    return f"RM {float(value):,.2f}"


def format_percent(value):
    return f"{float(value):.2f}%"


def compact_line():
    st.markdown('<hr class="compact-divider">', unsafe_allow_html=True)


def history_cell(container, value):
    container.markdown(
        f'<div class="history-cell"><p>{value}</p></div>',
        unsafe_allow_html=True,
    )


def get_dividend_rate(year, source):
    """Use a user-entered rate first, then the standard reference rate."""
    for record in st.session_state.custom_rates:
        if record["Dividend Year"] == year and record["Investment Source"] == source:
            return float(record["Dividend Rate"])
    return STANDARD_DIVIDEND_RATES.get(year, {}).get(source)


def investment_start_month(investment_date):
    """On/before the 15th includes the month; after the 15th starts next month."""
    return investment_date.month if investment_date.day <= 15 else investment_date.month + 1


def withdrawal_end_month(withdrawal_date):
    """On/before the 15th includes the month; after the 15th excludes the month."""
    return withdrawal_date.month if withdrawal_date.day <= 15 else withdrawal_date.month - 1


def eligible_new_investment_months(investment_date, withdrawal_date=None):
    start_month = investment_start_month(investment_date)
    end_month = 12 if withdrawal_date is None else withdrawal_end_month(withdrawal_date)
    return max(0, end_month - start_month + 1)


def build_projection(withdrawal_date):
    """Project each agency/source independently and compound yearly balances."""
    projection_rows = []
    missing = []

    valid_investments = sorted(
        [
            record
            for record in st.session_state.investments
            if record["Investment Date"] <= withdrawal_date
        ],
        key=lambda record: record["Investment Date"],
    )

    groups = sorted(
        {
            (record["Investment Destination"], record["Investment Source"])
            for record in valid_investments
        }
    )

    for destination, source in groups:
        group_investments = [
            record
            for record in valid_investments
            if record["Investment Destination"] == destination
            and record["Investment Source"] == source
        ]
        first_year = min(record["Investment Date"].year for record in group_investments)
        opening = 0.0

        for year in range(first_year, withdrawal_date.year + 1):
            annual_rate = get_dividend_rate(year, source)
            if annual_rate is None:
                missing.append(f"{source} – {year}")
                annual_rate = 0.0

            yearly_investments = [
                record
                for record in group_investments
                if record["Investment Date"].year == year
            ]
            new_investment = sum(record["Investment Amount"] for record in yearly_investments)

            if year < withdrawal_date.year:
                opening_months = 12
            else:
                opening_months = max(0, withdrawal_end_month(withdrawal_date))

            dividend = opening * annual_rate / 100 * opening_months / 12

            for record in yearly_investments:
                same_year_withdrawal = withdrawal_date if year == withdrawal_date.year else None
                months = eligible_new_investment_months(
                    record["Investment Date"], same_year_withdrawal
                )
                dividend += record["Investment Amount"] * annual_rate / 100 * months / 12

            closing = opening + new_investment + dividend
            projection_rows.append(
                {
                    "Investment Agency": destination,
                    "Investment Source": source,
                    "Year": year,
                    "Opening": opening,
                    "New Investment": new_investment,
                    "Dividend Rate": annual_rate,
                    "Dividend": dividend,
                    "Closing": closing,
                }
            )
            opening = closing

    projection_df = pd.DataFrame(
        projection_rows,
        columns=[
            "Investment Agency",
            "Investment Source",
            "Year",
            "Opening",
            "New Investment",
            "Dividend Rate",
            "Dividend",
            "Closing",
        ],
    )
    return projection_df, sorted(set(missing))


def final_agency_summary(projection_df, withdrawal_date):
    columns = ["Investment Agency", "Total Principal", "Estimated Dividend", "Final Value"]
    if projection_df.empty:
        return pd.DataFrame(columns=columns)

    final_rows = (
        projection_df.sort_values(["Investment Agency", "Investment Source", "Year"])
        .groupby(["Investment Agency", "Investment Source"], as_index=False)
        .tail(1)
    )
    closing_by_agency = final_rows.groupby("Investment Agency")["Closing"].sum()
    principal_by_agency = {
        agency: sum(
            record["Investment Amount"]
            for record in st.session_state.investments
            if record["Investment Destination"] == agency
            and record["Investment Date"] <= withdrawal_date
        )
        for agency in closing_by_agency.index
    }

    rows = []
    for agency, closing in closing_by_agency.items():
        principal = principal_by_agency[agency]
        rows.append(
            {
                "Investment Agency": agency,
                "Total Principal": principal,
                "Estimated Dividend": closing - principal,
                "Final Value": closing,
            }
        )
    return pd.DataFrame(rows, columns=columns)


# ==========================================================
# 1. ADD INVESTMENT
# ==========================================================
st.header("➕ Add Investment")
st.markdown(
    """
    <div class="information-note"><b>Note:</b> Enter each investment separately.
    You may add multiple investments with different dates. The system will
    automatically combine them into a single investment portfolio.</div>
    """,
    unsafe_allow_html=True,
)

next_no = len(st.session_state.investments) + 1
with st.form("add_investment_form", clear_on_submit=True):
    c1, c2, c3, c4, c5 = st.columns([0.7, 1.5, 1.5, 1.7, 1.7])
    with c1:
        st.text_input("No.", value=str(next_no), disabled=True)
    with c2:
        investment_date = st.date_input("Investment Date", value=date.today(), format="DD/MM/YYYY")
    with c3:
        investment_amount = st.number_input(
            "Investment Amount (RM)", min_value=0.00, step=100.00, format="%.2f"
        )
    with c4:
        investment_source = st.selectbox("Investment Source", INVESTMENT_SOURCES)
    with c5:
        investment_destination = st.selectbox("Investment Destination", INVESTMENT_DESTINATIONS)
    add_investment = st.form_submit_button(
        "➕ Add Investment", type="primary", use_container_width=True
    )

if add_investment:
    if investment_amount <= 0:
        st.warning("Please enter an investment amount greater than RM 0.00.")
    else:
        st.session_state.investments.append(
            {
                "Investment Date": investment_date,
                "Investment Amount": float(investment_amount),
                "Investment Source": investment_source,
                "Investment Destination": investment_destination,
            }
        )
        st.rerun()


# ==========================================================
# 2. INVESTMENT HISTORY WITH DELETE CONFIRMATION
# ==========================================================
st.header("📜 Investment History")

if not st.session_state.investments:
    st.info("No investment records are available. Please add an investment above.")
else:
    widths = [0.5, 1.5, 1.7, 1.6, 1.9, 0.9]
    header = st.columns(widths, gap="small", vertical_alignment="center")
    for column, label in zip(
        header,
        ["No.", "Investment Date", "Investment Amount (RM)", "Investment Source", "Investment Destination", "Action"],
    ):
        column.markdown(f"**{label}**")
    compact_line()

    for index, investment in enumerate(st.session_state.investments):
        row = st.columns(widths, gap="small", vertical_alignment="center")
        history_cell(row[0], index + 1)
        history_cell(row[1], investment["Investment Date"].strftime("%d/%b/%Y"))
        history_cell(row[2], format_rm(investment["Investment Amount"]))
        history_cell(row[3], investment["Investment Source"])
        history_cell(row[4], investment["Investment Destination"])
        if row[5].button("🗑️ Delete", key=f"request_investment_delete_{index}", use_container_width=True):
            st.session_state.pending_investment_delete = index
            st.rerun()
        compact_line()

if st.session_state.pending_investment_delete is not None:
    delete_index = st.session_state.pending_investment_delete
    if 0 <= delete_index < len(st.session_state.investments):
        record = st.session_state.investments[delete_index]
        st.warning(
            f"Delete Investment No. {delete_index + 1}: "
            f"{record['Investment Source']} – {format_rm(record['Investment Amount'])}?"
        )
        yes_col, no_col = st.columns(2)
        if yes_col.button("✅ Yes, Delete", key="confirm_investment_delete", use_container_width=True):
            st.session_state.investments.pop(delete_index)
            st.session_state.pending_investment_delete = None
            st.rerun()
        if no_col.button("❌ Cancel", key="cancel_investment_delete", use_container_width=True):
            st.session_state.pending_investment_delete = None
            st.rerun()
    else:
        st.session_state.pending_investment_delete = None


# ==========================================================
# 3. PROJECTION CALCULATION ENGINE
# ==========================================================
st.header("📊 Projection Calculation Engine")
st.subheader("💹 A. Dividend Rate Information")
st.markdown(
    """
    <div class="information-note"><b>Note:</b> Standard dividend rates for
    Cash, EPF, ASB and Fixed Deposit will be populated automatically after you
    enter the dividend year. For Others, please enter the dividend rate
    manually. You may also use this form to override any standard rate.</div>
    """,
    unsafe_allow_html=True,
)

with st.form("dividend_rate_form", clear_on_submit=True):
    r1, r2, r3, r4 = st.columns([0.7, 1.5, 1.8, 1.5])
    with r1:
        st.text_input("No.", value=str(len(st.session_state.custom_rates) + 1), disabled=True)
    with r2:
        dividend_year = st.number_input(
            "Dividend Year", min_value=2000, max_value=2100, value=date.today().year, step=1, format="%d"
        )
    with r3:
        dividend_source = st.selectbox("Investment Source", INVESTMENT_SOURCES, key="dividend_source")
    with r4:
        suggested_rate = get_dividend_rate(int(dividend_year), dividend_source)
        dividend_rate = st.number_input(
            "Dividend Rate (%)",
            min_value=0.00,
            max_value=100.00,
            value=float(suggested_rate if suggested_rate is not None else 0.00),
            step=0.01,
            format="%.2f",
        )
    add_rate = st.form_submit_button("➕ Add or Update Dividend Rate", type="primary", use_container_width=True)

if add_rate:
    year = int(dividend_year)
    if dividend_source == "Others" and dividend_rate <= 0:
        st.warning("Please enter a dividend rate greater than 0.00% for Others.")
    else:
        st.session_state.custom_rates = [
            record
            for record in st.session_state.custom_rates
            if not (
                record["Dividend Year"] == year
                and record["Investment Source"] == dividend_source
            )
        ]
        st.session_state.custom_rates.append(
            {
                "Dividend Year": year,
                "Investment Source": dividend_source,
                "Dividend Rate": float(dividend_rate),
            }
        )
        st.rerun()


# ==========================================================
# DIVIDEND RATE HISTORY WITH DELETE CONFIRMATION
# ==========================================================
st.subheader("📋 B. Dividend Rate History")

if not st.session_state.custom_rates:
    st.info("No manual dividend rates have been added. Standard rates will be used where available.")
else:
    sorted_rates = sorted(
        st.session_state.custom_rates,
        key=lambda record: (record["Dividend Year"], record["Investment Source"]),
    )
    widths = [0.5, 1.4, 2.1, 1.5, 0.9]
    header = st.columns(widths, gap="small", vertical_alignment="center")
    for column, label in zip(header, ["No.", "Dividend Year", "Investment Source", "Dividend Rate", "Action"]):
        column.markdown(f"**{label}**")
    compact_line()

    for display_no, rate_record in enumerate(sorted_rates, start=1):
        row = st.columns(widths, gap="small", vertical_alignment="center")
        history_cell(row[0], display_no)
        history_cell(row[1], rate_record["Dividend Year"])
        history_cell(row[2], rate_record["Investment Source"])
        history_cell(row[3], format_percent(rate_record["Dividend Rate"]))
        delete_key = (rate_record["Dividend Year"], rate_record["Investment Source"])
        if row[4].button(
            "🗑️ Delete",
            key=f"request_rate_delete_{delete_key[0]}_{delete_key[1]}",
            use_container_width=True,
        ):
            st.session_state.pending_rate_delete = delete_key
            st.rerun()
        compact_line()

if st.session_state.pending_rate_delete is not None:
    delete_year, delete_source = st.session_state.pending_rate_delete
    st.warning(f"Delete the {delete_source} dividend rate for {delete_year}?")
    yes_col, no_col = st.columns(2)
    if yes_col.button("✅ Yes, Delete", key="confirm_rate_delete", use_container_width=True):
        st.session_state.custom_rates = [
            record
            for record in st.session_state.custom_rates
            if not (
                record["Dividend Year"] == delete_year
                and record["Investment Source"] == delete_source
            )
        ]
        st.session_state.pending_rate_delete = None
        st.rerun()
    if no_col.button("❌ Cancel", key="cancel_rate_delete", use_container_width=True):
        st.session_state.pending_rate_delete = None
        st.rerun()


# ==========================================================
# 4. YEARLY INVESTMENT PROJECTION BY AGENCY
# ==========================================================
st.header("📅 Yearly Investment Projection")

latest_investment_date = max(
    (record["Investment Date"] for record in st.session_state.investments),
    default=date.today(),
)
withdrawal_date = st.date_input(
    "Withdrawal Date",
    value=max(date.today(), latest_investment_date),
    min_value=latest_investment_date,
    format="DD/MM/YYYY",
    key="projection_withdrawal_date",
)

st.markdown(
    """
    <div class="information-note"><b>Note:</b> The withdrawal-year dividend
    is estimated using eligible months up to the selected withdrawal date.
    Each closing balance is carried forward to the following year.</div>
    """,
    unsafe_allow_html=True,
)

projection_df, missing_rates = build_projection(withdrawal_date)
if missing_rates:
    st.warning("Please enter dividend rates for: " + ", ".join(missing_rates))

agency_projection_summary = final_agency_summary(projection_df, withdrawal_date)

# The Overall Total is the single source for all portfolio-level values.
# These totals are also used by the Profit / Loss Analysis below.
total_principal = float(agency_projection_summary["Total Principal"].sum())
total_estimated_dividend = float(agency_projection_summary["Estimated Dividend"].sum())
total_estimated_earned_value = float(agency_projection_summary["Final Value"].sum())

if projection_df.empty:
    st.info("Add at least one investment to generate the yearly projection.")
else:
    for agency in INVESTMENT_DESTINATIONS:
        agency_df = projection_df[projection_df["Investment Agency"] == agency].copy()
        if agency_df.empty:
            continue

        st.markdown(f"#### {agency}")
        display_df = agency_df.copy()
        display_df.insert(0, "No.", range(1, len(display_df) + 1))
        for column in ["Opening", "New Investment", "Dividend", "Closing"]:
            display_df[column] = display_df[column].map(format_rm)
        display_df["Dividend Rate"] = display_df["Dividend Rate"].map(format_percent)
        st.dataframe(display_df, hide_index=True, use_container_width=True)

        subtotal = agency_projection_summary[
            agency_projection_summary["Investment Agency"] == agency
        ].iloc[0]
        s1, s2, s3 = st.columns(3)
        s1.metric(f"{agency} – Principal", format_rm(subtotal["Total Principal"]))
        s2.metric(f"{agency} – Dividend", format_rm(subtotal["Estimated Dividend"]))
        s3.metric(f"{agency} – Subtotal", format_rm(subtotal["Final Value"]))

    st.markdown("#### Overall Total")
    t1, t2, t3 = st.columns(3)
    t1.metric("Total Principal", format_rm(total_principal))
    t2.metric("Total Estimated Dividend", format_rm(total_estimated_dividend))
    t3.metric("Total Estimated Earned Value", format_rm(total_estimated_earned_value))


# ==========================================================
# 5. WITHDRAWAL INFORMATION
# ==========================================================
st.header("💵 Withdrawal Information")
st.subheader("A. Withdrawal with Dividend Rate")
st.markdown(
    """
    <div class="information-note"><b>Note:</b> Enter the estimated dividend
    rate received from each investment institution. The estimated dividend is
    calculated directly based on the total investment amount.</div>
    """,
    unsafe_allow_html=True,
)

withdrawal_rows = []
if agency_projection_summary.empty:
    st.info("Add at least one investment to calculate withdrawal values.")
else:
    widths = [0.5, 2.0, 1.4, 1.5, 1.5, 1.7]
    header = st.columns(widths, gap="small", vertical_alignment="center")
    for column, label in zip(
        header,
        ["No.", "Investment Institution", "Withdrawal Date", "Total Investment", "Estimated Dividend (%)", "Total Withdrawal"],
    ):
        column.markdown(f"**{label}**")
    compact_line()

    for row_no, agency_record in enumerate(agency_projection_summary.to_dict("records"), start=1):
        agency = agency_record["Investment Agency"]
        principal = float(agency_record["Total Principal"])
        row = st.columns(widths, gap="small", vertical_alignment="center")
        history_cell(row[0], row_no)
        history_cell(row[1], agency)
        history_cell(row[2], withdrawal_date.strftime("%d/%b/%Y"))
        history_cell(row[3], format_rm(principal))
        estimated_rate = row[4].number_input(
            "Estimated Dividend (%)",
            min_value=0.00,
            max_value=100.00,
            step=0.01,
            format="%.2f",
            key=f"estimated_withdrawal_rate_{agency}",
            label_visibility="collapsed",
        )
        estimated_dividend = principal * estimated_rate / 100
        total_withdrawal = principal + estimated_dividend
        history_cell(row[5], format_rm(total_withdrawal))
        withdrawal_rows.append(
            {
                "Investment Agency": agency,
                "Total Principal": principal,
                "Estimated Dividend": estimated_dividend,
                "Total Withdrawal": total_withdrawal,
            }
        )
        compact_line()

withdrawal_summary_df = pd.DataFrame(
    withdrawal_rows,
    columns=["Investment Agency", "Total Principal", "Estimated Dividend", "Total Withdrawal"],
)
total_withdrawal_principal = float(withdrawal_summary_df["Total Principal"].sum()) if not withdrawal_summary_df.empty else 0.0
total_withdrawal_dividend = float(withdrawal_summary_df["Estimated Dividend"].sum()) if not withdrawal_summary_df.empty else 0.0
total_withdrawal_value = float(withdrawal_summary_df["Total Withdrawal"].sum()) if not withdrawal_summary_df.empty else 0.0

st.subheader("B. Withdrawal Summary with Dividend")
w1, w2, w3 = st.columns(3)
w1.metric("Total Principal", format_rm(total_withdrawal_principal))
w2.metric("Total Estimated Dividend Earned", format_rm(total_withdrawal_dividend))
w3.metric("Total Withdrawal with Dividend", format_rm(total_withdrawal_value))


# ==========================================================
# 6. PROFIT / LOSS BY AGENCY AND OVERALL
# ==========================================================
st.header("💹 Profit / Loss Analysis")
st.markdown(
    """
    <div class="information-note"><b>Note:</b> Profit/Loss compares each
    agency's manually estimated withdrawal value with its projected final value.</div>
    """,
    unsafe_allow_html=True,
)

projection_lookup = {
    row["Investment Agency"]: float(row["Final Value"])
    for row in agency_projection_summary.to_dict("records")
}
withdrawal_lookup = {
    row["Investment Agency"]: float(row["Total Withdrawal"])
    for row in withdrawal_summary_df.to_dict("records")
}

comparison_rows = []
for agency in INVESTMENT_DESTINATIONS:
    if agency not in projection_lookup and agency not in withdrawal_lookup:
        continue
    projected = projection_lookup.get(agency, 0.0)
    withdrawal_value = withdrawal_lookup.get(agency, 0.0)
    difference = withdrawal_value - projected
    comparison_rows.append((agency, projected, withdrawal_value, difference))

overall_difference = sum(row[3] for row in comparison_rows)
if comparison_rows:
    comparison_rows.append(
        ("Overall", sum(row[1] for row in comparison_rows), sum(row[2] for row in comparison_rows), overall_difference)
    )

if not comparison_rows:
    st.info("Add investment and withdrawal information to generate the comparison.")
else:
    st.markdown(
        """
        <style>
        .result-card {background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px;
                      padding:12px 15px; margin:5px 0 10px;}
        .result-title {font-size:15px; font-weight:700; color:#334155; margin-bottom:4px;}
        .result-profit {font-size:22px; font-weight:750; color:#16A34A;}
        .result-loss {font-size:22px; font-weight:750; color:#DC2626;}
        .result-even {font-size:22px; font-weight:750; color:#64748B;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    for agency, projected, withdrawal_value, difference in comparison_rows:
        st.markdown(f"#### {agency}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Projected Final Value", format_rm(projected))
        c2.metric("Agency Withdrawal Value", format_rm(withdrawal_value))
        if difference > 0:
            result_html = f'<div class="result-card"><div class="result-title">Profit</div><div class="result-profit">↑ {format_rm(difference)}</div></div>'
        elif difference < 0:
            result_html = f'<div class="result-card"><div class="result-title">Loss</div><div class="result-loss">↓ {format_rm(abs(difference))}</div></div>'
        else:
            result_html = f'<div class="result-card"><div class="result-title">No Difference</div><div class="result-even">— {format_rm(0)}</div></div>'
        c3.markdown(result_html, unsafe_allow_html=True)

