import streamlit as st

from utils.page_configuration import page_config, page_style
from utils.components import cost_basis


page_config()
page_style()


st.markdown(
    '<div class="main-title">💰 Operating Cost</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-subtitle">
        Calculate transportation, vehicle, labour and operational costs.
    </div>
    """,
    unsafe_allow_html=True,
)


cost_basis(
    "Cost Basis & Assumptions",
    """
    Fuel rate, maintenance cost, tyre provision and toll assumptions are default
    planning values. Users may replace them with actual company rates.
    """,
)