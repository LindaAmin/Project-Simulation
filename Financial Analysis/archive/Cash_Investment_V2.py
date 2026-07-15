import streamlit as st
import pandas as pd
from datetime import date

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(page_title="Potential Return - Cash",page_icon="💰",layout="wide")

# ==========================================================
# PAGE TITLE
# ==========================================================

st.title("💰 Potential Return - Cash")

# ==========================================================
# SESSION STATE
# ==========================================================

if "cash_investments" not in st.session_state:
    st.session_state.cash_investments = []

if "dividend_rates" not in st.session_state:
    st.session_state.dividend_rates = []

#next_no = len(st.session_state.dividend_rates) + 1

if "withdrawals" not in st.session_state:
    st.session_state.withdrawals = []

# temporary reset
#if "dividend_rates" in st.session_state:
    #if not isinstance(st.session_state.dividend_rates, list):
        #st.session_state.dividend_rates = []

# ==========================================================
# FORMAT FUNCTIONS
# ==========================================================

def format_rm(value):
    return f"RM {value:,.2f}"

def format_percent(value):
    return f"{value:.2f}%"

# ==========================================================
# 1. ADD CASH INVESTMENT SECTION
# ==========================================================

st.subheader("➕ Add Cash Investment Section")
next_no = len(st.session_state.cash_investments) + 1
col1, col2, col3, col4 = st.columns([1, 2, 2, 1])

with col1:
    st.text_input("No.",value=str(next_no),disabled=True)

with col2:
    investment_date = st.date_input("Investment Date",value=date.today(),format="DD/MM/YYYY")

with col3:
    investment_amount = st.number_input("Investment Amount (RM)",min_value=0.00,step=100.00,format="%.2f")

with col4:
    st.write("")
    st.write("")
    add_investment = st.button("➕ Add",use_container_width=True,type="primary")

st.caption("""
Note: Enter each investment separately.
You may add multiple investments with different dates.
The system will automatically combine them into a single investment portfolio.""")


# ==========================================================
# ADD INVESTMENT
# ==========================================================

if add_investment:
    if investment_amount <= 0:
        st.warning("Investment Amount must be greater than RM 0.00")

    else:
        st.session_state.cash_investments.append({"Investment Date": investment_date,"Investment Amount": investment_amount})
        st.success("Investment added successfully.")
        st.rerun()

st.divider()

# ==========================================================
# 2. INVESTMENT HISTORY SECTION
# ==========================================================

st.subheader("📋 Investment History Section")

if len(st.session_state.cash_investments) == 0:
    st.info("No investment has been added.")

else:
    investment_df = pd.DataFrame(st.session_state.cash_investments)
    header = st.columns([1, 3, 3, 1])
    header[0].markdown("**No.**")
    header[1].markdown("**Investment Date**")
    header[2].markdown("**Investment Amount**")
    header[3].markdown("**Delete**")
    for index, row in investment_df.iterrows():
        c1, c2, c3, c4 = st.columns([1, 3, 3, 1])

        with c1:
            st.write(index + 1)

        with c2:
            st.write(row["Investment Date"].strftime("%b/%Y"))

        with c3:
            st.write(format_rm(row["Investment Amount"]))

        with c4:
            if st.button("🗑️",key=f"delete_investment_{index}",use_container_width=True):
                st.session_state.delete_investment = index
                st.rerun()

# ==========================================================
# DELETE CONFIRMATION
# ==========================================================

if "delete_investment" in st.session_state:

    st.warning("Are you sure you want to delete this investment?")
    yes_col, no_col = st.columns(2)

    with yes_col:
        if st.button("✅ Yes, Delete",use_container_width=True):
            st.session_state.cash_investments.pop(st.session_state.delete_investment)
            del st.session_state.delete_investment
            st.success("Investment deleted successfully.")
            st.rerun()

    with no_col:
        if st.button("❌ Cancel",use_container_width=True):
            del st.session_state.delete_investment
            st.rerun()

st.divider()

# ==========================================================
# 3. WITHDRAWAL INFORMATION SECTION
# ==========================================================

st.subheader("📅 Withdrawal Information Section")

total_investment = 0.00

if len(st.session_state.cash_investments) > 0:
    investment_df = pd.DataFrame(st.session_state.cash_investments)

    total_investment = investment_df["Investment Amount"].sum()
    # replace with this to eliminate error during a blank info
    #if not investment_df.empty:
        #total_investment = investment_df["Investment"].sum()
        #total_return = investment_df["Return"].sum()
    #else:
        #total_investment = 0
        #total_return = 0

withdraw_col1, withdraw_col2 = st.columns(2)

with withdraw_col1:
    withdrawal_date = st.date_input("Withdrawal Date",value=date.today(),format="DD/MM/YYYY",key="withdrawal_date") # add info for format="DD/MM/YYYY"
    withdrawal_year = withdrawal_date.year
    withdrawal_month = withdrawal_date.month

with withdraw_col2:
    st.metric("Total Investment",format_rm(total_investment))

estimate_col1, estimate_col2 = st.columns(2)

with estimate_col1:

    estimated_dividend = st.number_input("Estimated Dividend (%)",min_value=0.00,step=0.10,format="%.2f",key="estimated_dividend")

with estimate_col2:

    estimated_withdrawal = (total_investment *(1 + estimated_dividend / 100))

    st.metric("Total Withdrawal with Dividend",format_rm(estimated_withdrawal))

# add info for yr end dividend calculation
#withdrawal_year = withdrawal_date.year
#withdrawal_month = withdrawal_date.month

st.divider()

st.caption("Please enter the withdrawal date and the dividend rate received from your investment institution.")

# ==========================================================
# 4. PROJECTION CALCULATION ENGINE SECTION
# ==========================================================

st.subheader("📊 Projection Calculation Engine Section")

st.markdown("📊 Dividend Rates History Section")
# ==========================================================
# DIVIDEND INPUT
# ==========================================================

next_no = len(st.session_state.dividend_rates) + 1
col1, col2, col3, col4 = st.columns([1, 2, 2, 1])

with col1:
    #st.text_input("No.",value=str(next_no),disabled=True, key="dividend_no")
    st.text_input("No.",value=str(next_no),disabled=True,key=f"dividend_no_{next_no}")

with col2:
    dividend_year = st.date_input("Dividend Year",value=date.today(),format="DD/MM/YYYY").year
    
with col3:
    dividend_rate = st.number_input("Dividend Rates (%)",min_value=0.00,step=100.00,format="%.2f")

with col4:
    st.write("")
    st.write("")
    add_dividend = st.button("➕ Add", key="add_dividend",use_container_width=True,type="primary")

st.caption("""Note: Please enter one dividend rate for each calendar year.
    The dividend rate is assigned on a yearly basis and will apply to all investments
    made during that calendar year, regardless of the investment month or date.""")

# ==========================================================
# ADD DIVIDEND
# ==========================================================

if add_dividend:
    if dividend_rate <= 0:
        st.warning("Dividend Rates must be greater than 0%")

    else:
        st.session_state.dividend_rates.append({"Dividend Year": dividend_year,"Dividend Rates": dividend_rate})
        st.success("Dividend rates added successfully.")
        st.rerun()

st.divider()

# ==========================================================
# DIVIDEND RATES HISTORY SECTION
# ==========================================================

st.markdown("📋 Dividend Rates History Section")

if len(st.session_state.dividend_rates) == 0:
    st.info("No dividend rates has been added.")

else:
    dividend_rate_df = pd.DataFrame(st.session_state.dividend_rates)
    header = st.columns([1, 3, 3, 1])
    header[0].markdown("**No.**")
    header[1].markdown("**Dividend Year**")
    header[2].markdown("**Dividend Rates**")
    header[3].markdown("**Delete**")

    for index, row in dividend_rate_df.iterrows():
        c1, c2, c3, c4 = st.columns([1, 3, 3, 1])

        with c1:
            st.write(index + 1)

        with c2:
            st.write(int(row["Dividend Year"]))
            #st.write(row["Dividend Year"].strftime("%b/%Y")).year

        with c3:
            st.write(format_percent(row["Dividend Rates"]))

        with c4:
            if st.button("🗑️",key=f"delete_dividend_{index}",use_container_width=True):
                st.session_state.dividend_rates = index
                st.rerun()

# ==========================================================
# DELETE DIVIDEND CONFIRMATION
# ==========================================================

if "delete_dividend" in st.session_state:

    st.warning("Are you sure you want to delete this dividend rates?")
    yes_col, no_col = st.columns(2)

    with yes_col:
        if st.button("✅ Yes, Delete",key="confirm_delete_dividend",use_container_width=True):
            st.session_state.dividend_rates.pop(st.session_state.delete_dividend)
            del st.session_state.delete_dividend
            st.success("Dividend Rates deleted successfully.")
            st.rerun()

    with no_col:
        if st.button("❌ Cancel",key="cancel_delete_dividend",use_container_width=True):
            del st.session_state.delete_dividend
            st.rerun()

st.divider()

# ==========================================================
# INVESTMENT PROJECTION 
# ==========================================================

st.markdown("Yearly Investment Projection Table")

# ==========================================================
# ADD DIVIDEND
# ==========================================================

if add_dividend:
    st.session_state.dividend_rates.append(
        {
            "Dividend Year": dividend_year,
            "Dividend Rates": dividend_rate,
        }
    )
    st.success("Dividend rate added successfully.")
    st.rerun()

# ==========================================================
# RESET DIVIDEND
# ==========================================================

if st.button("Reset Dividend Data"):
    st.session_state.dividend_rates = []
    st.rerun()

# ==========================================================
# YEARLY INVESTMENT PROJECTION
# ==========================================================

st.markdown("📊 Yearly Investment Projection")
projection = []
opening_value = 0

# Sort investments by date
investments = sorted(st.session_state.cash_investments,key=lambda x: x["Investment Date"])

for dividend in sorted(st.session_state.dividend_rates, key=lambda x: x["Dividend Year"]):

    year = dividend["Dividend Year"]
    rate = dividend["Dividend Rates"]

    new_investment = 0
    dividend_value = 0
   
    # Add investments made in this year
    for investment in investments:

        if investment["Investment Date"].year == year:
            new_investment += investment["Investment Amount"]

            months = (12 - investment["Investment Date"].month + 1)

            dividend_value += (investment["Investment Amount"] * rate / 100 * months / 12)

    # Existing balance from previous year
    if year < withdrawal_year:
        if opening_value > 0:
            dividend_value += opening_value * rate / 100

    elif year == withdrawal_year:
        if opening_value > 0:
            dividend_value += (opening_value * rate / 100 / 12 * withdrawal_month )

    else:
        break

    # Opening + new money + dividend
    closing_value = (opening_value + new_investment + dividend_value)

    projection.append({"No.": len(projection) + 1,"Year": year,"Opening": opening_value,"New Investment": new_investment,"Dividend": dividend_value,"Closing": closing_value})
    
    # Carry forward
    opening_value = closing_value

projection_df = pd.DataFrame(projection)

# Summary
#total_dividend = projection_df["Dividend"].sum()
if not projection_df.empty and "Dividend" in projection_df.columns:
    total_dividend = projection_df["Dividend"].sum()
else:
    total_dividend = 0

st.dataframe(projection_df.style.format({"Opening": "RM {:,.2f}","New Investment": "RM {:,.2f}","Dividend": "RM {:,.2f}","Closing": "RM {:,.2f}"}),use_container_width=True,hide_index=True)

st.caption("Note: The dividend shown for the withdrawal year is an **estimated dividend** based on the selected withdrawal month. Estimated Dividend = Annual Dividend ÷ 12 × Withdrawal Month. This estimate is provided because the final market dividend for the withdrawal year has not yet been declared.")

# ==========================================================
# 5. INVESTMENT SUMMARY SECTION
# ==========================================================

st.subheader("📈 Investment Summary Section")

# Total Principal (all cash invested)
total_principal = sum(item["Investment Amount"]for item in st.session_state.cash_investments)

# Total Dividend Earned (all years)
# total_dividend = projection_df["Dividend"].sum()
total_dividend = projection_df.get("Dividend", pd.Series(dtype=float)).sum()

# Estimated Earned Value
estimated_value = total_principal + total_dividend

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("💰 Total Principal",f"RM {total_principal:,.2f}")

with col2:
    st.metric("📈 Total Dividend Earned",f"RM {total_dividend:,.2f}")

with col3:
    st.metric("🏦 Estimated Earned Value",f"RM {estimated_value:,.2f}")














# ==========================================================
# 5. COMPARISON SECTION
# ==========================================================

st.subheader("📊 Profit / Loss of Investment Section")

# Keep Money in Savings (last Closing value)
if len(projection_df) > 0:
    savings_value = projection_df.iloc[-1]["Closing"]
else:
    savings_value = 0

# Invest in Agency B (from Withdrawal Section)
agency_b_value = estimated_withdrawal

# Difference
difference = savings_value - agency_b_value

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🏦 Keep Money in Savings",f"RM {savings_value:,.2f}")

with col2:
    st.metric("📈 Invest in Agency B",f"RM {agency_b_value:,.2f}")

with col3:
    if difference >= 0:
        st.metric("❌ Loss",f"RM {difference:,.2f}")
    else:
        st.metric("✅ Profit",f"RM {abs(difference):,.2f}")

st.caption("Note: This summary is based on the investment projection calculated from the dividend rates entered.")