import streamlit as st

from utils.page_configuration import page_config, page_style
from utils.components import cost_basis


page_config()
page_style()


st.markdown(
    '<div class="main-title">📊 Cost per Parcel</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-subtitle">
        Determine the unit cost of delivering each parcel.
    </div>
    """,
    unsafe_allow_html=True,
)


cost_basis(
    "Calculation Basis",
    """
    Cost per Parcel = Total Allocated Operating Cost ÷ Total Number of Chargeable Parcels.
    The calculation may include transportation, vehicle, manpower and overhead costs.
    """,
)