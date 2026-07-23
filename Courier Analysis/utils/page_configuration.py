import streamlit as st


def page_config():
    st.set_page_config(
        page_title="Courier Cost & Profitability Analyzer",
        page_icon="📦",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def page_style():
    st.markdown(
        """
        <style>

        /* ===========================
           General Page
        =========================== */

        .stApp {
            background-color: #F8FAFC;
            font-family: Arial, sans-serif;
        }

        /* ===========================
           Main Title
        =========================== */

        .main-title {
            text-align: center;
            color: #1E3A8A;
            font-size: 34px;
            font-weight: 700;
            margin-bottom: 4px;
        }

        .page-subtitle {
            text-align: center;
            color: #64748B;
            font-size: 15px;
            margin-bottom: 24px;
        }

        /* ===========================
           Section Title
        =========================== */

        .section-title {
            color: #1E3A8A;
            font-size: 22px;
            font-weight: 700;
            margin-top: 20px;
            margin-bottom: 10px;
        }

        /* ===========================
           Cost Basis Box
        =========================== */

        .cost-basis-box {
            background-color: #F1F5F9;
            border-left: 4px solid #1E3A8A;
            padding: 10px 12px;
            border-radius: 5px;
            margin-top: 10px;
            margin-bottom: 10px;
        }

        .cost-basis-title {
            font-size: 12px;
            font-weight: 700;
            color: #1E3A8A;
            margin-bottom: 5px;
        }

        .cost-basis-text {
            font-size: 11px;
            color: #64748B;
            line-height: 1.5;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
    