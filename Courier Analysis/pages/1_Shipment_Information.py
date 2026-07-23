import streamlit as st

from utils.page_configuration import page_config, page_style
from utils.components import cost_basis


page_config()
page_style()


st.markdown(
    '<div class="main-title">📦 Shipment Information</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-subtitle">
        Enter the origin, destination, delivery requirement and shipment details.
    </div>
    """,
    unsafe_allow_html=True,
)


cost_basis(
    "Shipment Information Basis",
    """
    Origin and destination will be used to identify the shipment region and feasible
    transport modes. Final vehicle selection will also consider parcel quantity,
    weight, volume and delivery service level.
    """,
)

st.markdown(
    '<div class="section-title">Shipment Details</div>',
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:

    origin_region = st.selectbox(
        "Origin Region",
        [
            "Select Region",
            "Peninsular Malaysia",
            "Sabah",
            "Sarawak"
        ]
    )

    origin_state = st.selectbox(
        "Origin State",
        [
            "Select State"
        ]
    )

with col2:

    destination_region = st.selectbox(
        "Destination Region",
        [
            "Select Region",
            "Peninsular Malaysia",
            "Sabah",
            "Sarawak"
        ]
    )

    destination_state = st.selectbox(
        "Destination State",
        [
            "Select State"
        ]
    )