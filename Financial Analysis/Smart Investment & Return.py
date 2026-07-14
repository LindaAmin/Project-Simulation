import streamlit as st

st.title("📊 Smart Investment Planner")
st.caption("Compare investment options, calculate projected returns, and evaluate long-term wealth growth.")

st.header("Home")

st.page_link("pages/Cash_Investment.py",label="Cash Investment Calculator")
st.page_link("pages/Cash_Investment_V2.py", label= "Cash Investment Calculator_V02")
st.page_link("pages/Investment_Calculation.py", label= "Investment Calculator")

# keep page center and give the browser tabs
#st.set_page_config(page_title= "Assistant AI", layout = 'centered')

