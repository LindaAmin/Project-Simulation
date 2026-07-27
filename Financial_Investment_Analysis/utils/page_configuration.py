import streamlit as st


# =========================================================
# INVESTMENT CALCULATION PAGE CONFIGURATION
# =========================================================
def page_config():
    st.set_page_config(page_title="Smart Investment Return Simulator",page_icon="📈",layout="wide")


# =========================================================
# PAGE STYLE
# =========================================================


def page_style():

    st.markdown(
        """
        <style>

        /* Page background */
        .stApp {
            background-color: #F8FAFC;
            color: #0F172A;
        }

        /* Main content spacing */
        .block-container {
            padding-top: 1.50rem;
            padding-bottom: 3rem;
            max-width: 1400px;
        }

        /* Main page title */
        .main-title {
            text-align: center !important;
            color: #1E3A8A !important;
            font-family: Arial, sans-serif !important;
            font-size: 38px !important;
            font-weight: 700 !important;
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }

        /* Secondary page title */
        .second-title {
            text-align: left !important;
            color: #334155 !important;
            font-family: Arial, sans-serif !important;
            font-size: 22px !important;
            font-weight: 600 !important;
            margin-top: 8px !important;
            margin-bottom: 0 !important;
        }

        /* Subtitle */
        .sub-title {
            text-align: center !important;
            color: #64748B !important;
            font-family: Arial, sans-serif !important;
            font-size: 15px !important;
            margin-top: 5px !important;
            margin-bottom: 25px !important;
        }

        /* Information note */
        .information-note {
            background-color: #EFF6FF;
            border-left: 4px solid #2563EB;
            border-radius: 6px;
            color: #334155;
            font-family: Arial, sans-serif;
            font-size: 14px;
            padding: 10px 14px;
            margin-bottom: 15px;
        }

        /* Metric boxes */
        div[data-testid="stMetric"] {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 14px;
        }

        /* Compact Investment History divider */
        .compact-divider {
            border: none !important;
            border-top: 1px solid #CBD5E1 !important;
            margin-top: 2px !important;
            margin-bottom: 2px !important;
        }

        /* Reduce paragraph spacing inside history rows */
        .history-cell p {
            margin-top: 4px !important;
            margin-bottom: 4px !important;
            line-height: 1.15 !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# PAGE TITLES
# =========================================================
def page_title():
    st.markdown(
        """
        <h1 class="main-title">
            📈 Smart Investment Return Simulator
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <h2 class="second-title">
            💰 Potential Investment Return Analysis
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <p class="sub-title">
            Compare potential returns from different investment strategies
        </p>
        """,
        unsafe_allow_html=True
    )