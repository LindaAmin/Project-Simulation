import streamlit as st


# =========================================================
# PAGE CONFIGURATION
# Must be the first Streamlit command
# =========================================================

st.set_page_config(
    page_title="Smart Investment Planner",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# HOME PAGE STYLE
# =========================================================

st.markdown(
    """
    <style>

    /* Page background */
    .stApp {
        background-color: #F8FAFC !important;
    }

    /* Main page container */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1200px !important;
    }

    /* Unique Home page title */
    .home-main-title {
        text-align: center !important;
        color: #1E3A8A !important;
        font-family: Arial, sans-serif !important;
        font-size: 38px !important;
        font-weight: 700 !important;
        margin-top: 0 !important;
        margin-bottom: 5px !important;
    }

    .home-main-title * {
        color: #1E3A8A !important;
    }

    /* Home page caption */
    .home-main-caption {
        text-align: center !important;
        color: #64748B !important;
        font-family: Arial, sans-serif !important;
        font-size: 16px !important;
        margin-top: 0 !important;
        margin-bottom: 35px !important;
    }

    /* Unique Home section title */
    .home-section-title {
        color: #1E3A8A !important;
        font-family: Arial, sans-serif !important;
        font-size: 24px !important;
        font-weight: 700 !important;
        margin-top: 10px !important;
        margin-bottom: 5px !important;
    }

    .home-section-title * {
        color: #1E3A8A !important;
    }

    /* Home section description */
    .home-section-note {
        color: #475569 !important;
        font-family: Arial, sans-serif !important;
        font-size: 15px !important;
        margin-top: 0 !important;
        margin-bottom: 15px !important;
    }

    /* Streamlit page-link container */
    div[data-testid="stPageLink"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        padding: 4px 8px !important;
    }

    /* Force page-link label to display */
    div[data-testid="stPageLink"] a,
    div[data-testid="stPageLink"] a p,
    div[data-testid="stPageLink"] p,
    div[data-testid="stPageLink"] span {
        color: #1E3A8A !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        text-decoration: none !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HOME PAGE TITLE
# =========================================================

st.markdown(
    """
    <h1 class="home-main-title">
        📊 Smart Investment Planner
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <p class="home-main-caption">
        Compare investment options, calculate projected returns,
        and evaluate long-term wealth growth.
    </p>
    """,
    unsafe_allow_html=True
)


# =========================================================
# LATEST INVESTMENT CALCULATOR
# =========================================================

st.markdown(
    """
    <h2 class="home-section-title">
        📈 Investment Return Simulator
    </h2>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <p class="home-section-note">
        Use the latest version to record investments, calculate
        yearly dividends, estimate withdrawal values and compare
        investment returns.
    </p>
    """,
    unsafe_allow_html=True
)


# =========================================================
# PAGE LINK
# =========================================================

st.page_link(
    "pages/Investment_Calculation.py",
    label="Open Smart Investment Return Simulator",
    icon="📈",
    use_container_width=True
)