import streamlit as st

from utils.page_configuration import page_config, page_style
from utils.components import cost_basis


page_config()
page_style()


st.markdown(
    '<div class="main-title">🗺️ Route Intelligence</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-subtitle">
        Identify feasible transport modes based on the shipment route.
    </div>
    """,
    unsafe_allow_html=True,
)


cost_basis(
    "Route Determination",
    """
    Transport mode is determined based on origin, destination, geographical region,
    delivery service level, parcel weight and total shipment volume.
    """,
)