import pandas as pd

# ==========================================================
# INVESTMENT PROJECTION 
# ==========================================================

st.markdown("Yearly Investment Projection Table")
projection = []
opening_value = investment_amount
for item in dividend_rates:
    year = item["Dividend Year"]
    rate = item["Dividend Rate"]

    dividend = opening_value * rate / 100

    closing_value = opening_value + dividend

    projection.append({"Investment": 1,"Year": year,"Opening": opening_value,"Dividend": dividend,"Closing": closing_value})

    # carry forward
    opening_value = closing_value

projection_df = pd.DataFrame(projection)

# Formatting RM
projection_df["Opening"] = projection_df["Opening"].round(2)
projection_df["Dividend"] = projection_df["Dividend"].round(2)
projection_df["Closing"] = projection_df["Closing"].round(2)


st.dataframe(projection_df,use_container_width=True)