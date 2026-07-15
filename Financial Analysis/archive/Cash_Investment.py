import streamlit as st
import pandas as pd
from datetime import date


st.title("💰 Potential Return - Cash")


# Session State Initialization
if "investments" not in st.session_state:
    st.session_state.investments = []

#if "investment_date" not in st.session_state:
    #st.session_state.investment_date = date.today()

if "amount" not in st.session_state:
    st.session_state.amount = 0.0

if "interest" not in st.session_state:
    st.session_state.interest = 0.0


# Add Investment Section
st.subheader("➕ Add Your Cash Investment")

col1, col2, col3, col4 = st.columns([2,2,2,1])

with col1:
    #investment_date = st.date_input("Investment Date",value=st.session_state.investment_date,key="investment_date")
    investment_date = st.date_input("Investment Date",value=date.today())
    formatted_date = investment_date.strftime("%d/%m/%Y")
    st.write("Selected Date:", formatted_date)

with col2:
    #amount = st.number_input("Investment Amount (RM)",min_value=0.0,value=st.session_state.amount,step=100.0,key="amount")
    amount = st.number_input("Investment Amount (RM)",min_value=0.0,step=100.0,key="amount_input")

with col3:
    #interest = st.number_input("Interest (%)",min_value=0.0,value=st.session_state.interest,step=0.1,key="interest")
    interest = st.number_input("Interest (%)",min_value=0.0,step=0.1,key="interest_input")

with col4:
    st.write("")
    st.write("")
    add = st.button("➕")
    #add = st.button("➕", help="Add Investment")

st.divider()

# Add investment / Record
if add:
    if amount > 0:
        st.session_state.investments.append({"Date": investment_date,"Investment Date": investment_date.strftime("%m/%y"),"Investment (RM)": amount,"Interest (%)": interest,})
        #st.session_state.amount_input = 0.0
        #st.session_state.interest_input = 0.0
        st.success("Investment added successfully!")
        st.rerun()


# Investment History with Investment Calculation
if st.session_state.investments:
    df = pd.DataFrame(st.session_state.investments)
    #st.write(df.columns)

    # Calculate return until December same year
    def calculate_return(row):
        investment_month = row["Date"].month
        
        # December = month 12
        months = 12 - investment_month + 1
        #monthly_interest = row["Interest (%)"] / 100 / 12
        return row["Investment (RM)"] * ((1 + row["Interest (%)"]/100/12) ** months - 1)

    df["Return (RM)"] = df.apply(calculate_return,axis=1)

    st.subheader("📋 Investment History")

    header = st.columns([2,2,2,2,1])
    header[0].markdown("**Investment Date**")
    header[1].markdown("**Amount**")
    header[2].markdown("**Interest**")
    header[3].markdown("**Return**")
    header[4].markdown("**Delete**")

    for index, row in df.iterrows():
    
    # Display each row with delete button
        col1, col2, col3, col4, col5 = st.columns([2,2,2,2,1])

        with col1:
            st.write(row["Investment Date"])

        with col2:
            st.write(f"RM {row['Investment (RM)']:,.2f}")

        with col3:
            st.write(f"{row['Interest (%)']}%")

        with col4:
            st.write(f"RM {row['Return (RM)']:,.2f}")

        with col5:
            if st.button("🗑️", key=f"delete_{index}"):
                st.session_state.delete_index = index
                st.rerun()
    
    # Add confirmation before delete
    if "delete_index" in st.session_state:
        st.warning("Are you sure you want to delete this investment?")
        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("Yes, Delete"):
                st.session_state.investments.pop(st.session_state.delete_index)
                del st.session_state.delete_index
                st.rerun()

        with col_b:
            if st.button("Cancel"):
                del st.session_state.delete_index
                st.rerun() 

    st.divider()

    # Investment Summary
    # Investment Summary with Carry Forward Calculation

    df = df.sort_values("Date")

    current_value = 0
    yearly_summary = []

    for i, (_, row) in enumerate(df.iterrows(), start=1):
        investment_year = row["Date"].strftime("%m/%y") #month # previously year
    
    # Add new investment
        current_value += row["Investment (RM)"]

    # Calculate dividend / interest
        interest_rate = row["Interest (%)"] / 100
        dividend = current_value * interest_rate

    # Carry forward value
        current_value += dividend

        yearly_summary.append({"No.": i, "Investment Date": investment_year,"Investment": round(row["Investment (RM)"], 2),"Interest (%)": round(row["Interest (%)"], 2),"Dividend": round(dividend, 2),"End Value": round(current_value, 2)})
        
    summary_df = pd.DataFrame(yearly_summary)

    st.subheader("📊 Investment Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Principal Invested",f"RM {df['Investment (RM)'].sum():,.2f}")

    with col2:
        total_dividend = summary_df["Dividend"].sum()
        st.metric("Total Dividend Earned", f"RM {total_dividend:,.2f}")

    with col3:
        st.metric("Current Investment Value",f"RM {current_value:,.2f}")

    #st.dataframe(summary_df)
    #st.dataframe(summary_df.style.format({"Investment": "RM {:,.2f}","Dividend": "RM {:,.2f}","End Value": "RM {:,.2f}","Interest (%)": "{:.2f}%"}))
    st.dataframe(summary_df.style.format({"Investment": "RM {:,.2f}","Dividend": "RM {:,.2f}","End Value": "RM {:,.2f}","Interest (%)": "{:.2f}%"}),hide_index=True)
    
    st.divider()

    # Reset Button
    
    if st.button("🔄 Reset All"):
        st.session_state.investments = []
        #st.session_state.investment_date = date.today()
        #st.session_state.amount_input = 0.0
        #st.session_state.interest_input = 0.0
        if "investment_date" in st.session_state:
            del st.session_state["investment_date"]

        if "delete_index" in st.session_state:
            del st.session_state["delete_index"]
        
        #if "delete_index" in st.session_state:
            #del st.session_state.delete_index
        st.rerun()

    st.divider()

# Withdraw with Dividend

    st.subheader("📊 Current Investment Value (Today)")

# Total investment
    total_investment = df["Investment (RM)"].sum()

    col1, col2, col3 = st.columns(3)

    with col2:
        dividend = st.number_input("Dividend (%)",min_value=0.0,step=0.1,key="dividend_input")

# Calculate dividend amount
    dividend_amount = total_investment * (dividend / 100)

# Current value
    current_value_investor = total_investment + dividend_amount

    with col1:
        st.metric("Total Cash Investment",f"RM {total_investment:,.2f}")

    with col2:
        st.metric("Dividend",f"{dividend:.2f}%")

    with col3:
        st.metric("Current Value with Dividend",f"RM {current_value_investor:,.2f}")

    st.divider()

# Profit & Loss After Investment

    st.subheader("📊 Profit or Loss of Investment (Today)")

# profit_loss = current_value_investor - final_value
    profit_loss = current_value_investor - current_value
#profit_loss = current_value_investor - total_investment

    st.metric("Profit / Loss",f"RM {profit_loss:,.2f}")

else:
    st.info("Please add at least one investment.")