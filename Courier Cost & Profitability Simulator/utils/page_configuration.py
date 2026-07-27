"""
Page configuration and visual styling for the
Courier Cost Analysis application.

Responsibilities
----------------
- Streamlit page configuration
- Global CSS
- Font and colour styling
- Main page layout
- Sidebar styling
- Input and button styling
- Metric-card styling
- DataFrame styling
- Responsive layout

This module must not contain:
- Business calculations
- CSV loading
- Session-state calculations
- Cost logic
- Page navigation logic
"""

from __future__ import annotations

import streamlit as st


# =========================================================
# DESIGN CONSTANTS
# =========================================================
APP_NAME = "Courier Cost Intelligence"

PAGE_ICON = "🚚"

PRIMARY_COLOUR = "#1E3A8A"
PRIMARY_DARK = "#172554"
PRIMARY_LIGHT = "#DBEAFE"

SECONDARY_COLOUR = "#0F766E"
SECONDARY_LIGHT = "#CCFBF1"

BACKGROUND_COLOUR = "#F8FAFC"
CARD_BACKGROUND = "#FFFFFF"
SIDEBAR_BACKGROUND = "#EFF6FF"

TEXT_PRIMARY = "#0F172A"
TEXT_SECONDARY = "#475569"
TEXT_MUTED = "#64748B"

BORDER_COLOUR = "#CBD5E1"
LIGHT_BORDER = "#E2E8F0"

SUCCESS_COLOUR = "#15803D"
SUCCESS_BACKGROUND = "#F0FDF4"

WARNING_COLOUR = "#B45309"
WARNING_BACKGROUND = "#FFFBEB"

ERROR_COLOUR = "#B91C1C"
ERROR_BACKGROUND = "#FEF2F2"

INFO_COLOUR = "#0369A1"
INFO_BACKGROUND = "#F0F9FF"

FONT_FAMILY = "Arial, Helvetica, sans-serif"


# =========================================================
# PAGE CONFIGURATION
# =========================================================
def page_config(
    page_title: str = APP_NAME,
    page_icon: str = PAGE_ICON,
    layout: str = "wide",
    initial_sidebar_state: str = "expanded",
) -> None:
    """
    Configure the Streamlit page.

    This function must be called before any other Streamlit
    command on each page.

    Parameters
    ----------
    page_title:
        Browser-tab title.

    page_icon:
        Browser-tab icon.

    layout:
        Streamlit page layout. Recommended value: "wide".

    initial_sidebar_state:
        Initial sidebar state:
        - expanded
        - collapsed
        - auto
    """

    st.set_page_config(
        page_title=page_title,
        page_icon=page_icon,
        layout=layout,
        initial_sidebar_state=initial_sidebar_state,
    )


# =========================================================
# GLOBAL PAGE STYLE
# =========================================================
def page_style() -> None:
    """
    Apply global CSS styling to the application.

    Call after page_config():

    page_config()
    page_style()
    """

    st.markdown(
        f"""
        <style>

        /* ==================================================
           GLOBAL PAGE
        ================================================== */

        html,
        body,
        [class*="css"] {{
            font-family: {FONT_FAMILY};
        }}

        .stApp {{
            background-color: {BACKGROUND_COLOUR};
            color: {TEXT_PRIMARY};
        }}

        .block-container {{
            max-width: 1450px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }}

        p,
        li,
        span,
        label,
        div {{
            font-family: {FONT_FAMILY};
        }}

        p {{
            color: {TEXT_PRIMARY};
            line-height: 1.55;
        }}


        /* ==================================================
           MAIN PAGE TITLES
        ================================================== */

        .main-title {{
            color: {PRIMARY_COLOUR};
            font-size: 34px;
            font-weight: 700;
            line-height: 1.2;
            text-align: left;
            margin-top: 0;
            margin-bottom: 6px;
            letter-spacing: -0.3px;
        }}

        .page-subtitle {{
            color: {TEXT_SECONDARY};
            font-size: 16px;
            font-weight: 400;
            line-height: 1.5;
            margin-bottom: 24px;
        }}

        .section-title {{
            color: {PRIMARY_COLOUR};
            font-size: 22px;
            font-weight: 700;
            line-height: 1.3;
            margin-top: 30px;
            margin-bottom: 14px;
            padding-bottom: 7px;
            border-bottom: 2px solid {PRIMARY_LIGHT};
        }}

        .subsection-title {{
            color: {PRIMARY_DARK};
            font-size: 18px;
            font-weight: 700;
            line-height: 1.3;
            margin-top: 20px;
            margin-bottom: 10px;
        }}


        /* ==================================================
           STREAMLIT DEFAULT HEADINGS
        ================================================== */

        h1 {{
            color: {PRIMARY_COLOUR};
            font-size: 34px !important;
            font-weight: 700 !important;
        }}

        h2 {{
            color: {PRIMARY_COLOUR};
            font-size: 24px !important;
            font-weight: 700 !important;
        }}

        h3 {{
            color: {PRIMARY_DARK};
            font-size: 20px !important;
            font-weight: 700 !important;
        }}


        /* ==================================================
           INPUT LABELS
        ================================================== */

        .stTextInput label,
        .stNumberInput label,
        .stSelectbox label,
        .stMultiSelect label,
        .stDateInput label,
        .stTimeInput label,
        .stTextArea label,
        .stRadio label,
        .stCheckbox label,
        .stSlider label {{
            color: {TEXT_PRIMARY} !important;
            font-size: 14px !important;
            font-weight: 600 !important;
        }}


        /* ==================================================
           INPUT FIELDS
        ================================================== */

        .stTextInput input,
        .stNumberInput input,
        .stDateInput input,
        .stTimeInput input,
        .stTextArea textarea {{
            background-color: {CARD_BACKGROUND};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER_COLOUR};
            border-radius: 7px;
            font-size: 14px;
        }}

        .stTextInput input:focus,
        .stNumberInput input:focus,
        .stDateInput input:focus,
        .stTimeInput input:focus,
        .stTextArea textarea:focus {{
            border-color: {PRIMARY_COLOUR};
            box-shadow: 0 0 0 1px {PRIMARY_COLOUR};
        }}

        div[data-baseweb="select"] > div {{
            background-color: {CARD_BACKGROUND};
            color: {TEXT_PRIMARY};
            border-color: {BORDER_COLOUR};
            border-radius: 7px;
            min-height: 40px;
        }}

        div[data-baseweb="select"] > div:focus-within {{
            border-color: {PRIMARY_COLOUR};
            box-shadow: 0 0 0 1px {PRIMARY_COLOUR};
        }}

        div[data-baseweb="popover"] {{
            font-family: {FONT_FAMILY};
        }}


        /* ==================================================
           RADIO BUTTONS AND CHECKBOXES
        ================================================== */

        .stRadio [role="radiogroup"] {{
            gap: 14px;
        }}

        .stRadio div[role="radiogroup"] label {{
            background-color: {CARD_BACKGROUND};
            border: 1px solid {LIGHT_BORDER};
            border-radius: 7px;
            padding: 6px 10px;
        }}

        .stCheckbox {{
            color: {TEXT_PRIMARY};
        }}


        /* ==================================================
           BUTTONS
        ================================================== */

        .stButton > button {{
            min-height: 40px;
            border-radius: 7px;
            border: 1px solid {PRIMARY_COLOUR};
            background-color: {CARD_BACKGROUND};
            color: {PRIMARY_COLOUR};
            font-family: {FONT_FAMILY};
            font-size: 14px;
            font-weight: 600;
            transition:
                background-color 0.2s ease,
                color 0.2s ease,
                border-color 0.2s ease,
                transform 0.1s ease;
        }}

        .stButton > button:hover {{
            background-color: {PRIMARY_LIGHT};
            color: {PRIMARY_DARK};
            border-color: {PRIMARY_DARK};
        }}

        .stButton > button:active {{
            transform: translateY(1px);
        }}

        .stButton > button:focus {{
            box-shadow: 0 0 0 2px {PRIMARY_LIGHT};
        }}

        .stButton > button[kind="primary"] {{
            background-color: {PRIMARY_COLOUR};
            color: #FFFFFF;
            border-color: {PRIMARY_COLOUR};
        }}

        .stButton > button[kind="primary"]:hover {{
            background-color: {PRIMARY_DARK};
            color: #FFFFFF;
            border-color: {PRIMARY_DARK};
        }}

        .stDownloadButton > button {{
            min-height: 42px;
            border-radius: 7px;
            border: 1px solid {SECONDARY_COLOUR};
            background-color: {SECONDARY_COLOUR};
            color: #FFFFFF;
            font-size: 14px;
            font-weight: 600;
        }}

        .stDownloadButton > button:hover {{
            background-color: #115E59;
            color: #FFFFFF;
            border-color: #115E59;
        }}

        button:disabled {{
            opacity: 0.55;
            cursor: not-allowed;
        }}


        /* ==================================================
           METRIC CARDS
        ================================================== */

        div[data-testid="stMetric"] {{
            background-color: {CARD_BACKGROUND};
            border: 1px solid {LIGHT_BORDER};
            border-radius: 10px;
            padding: 15px 17px;
            min-height: 112px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
        }}

        div[data-testid="stMetric"]:hover {{
            border-color: {BORDER_COLOUR};
            box-shadow: 0 3px 10px rgba(15, 23, 42, 0.08);
        }}

        div[data-testid="stMetricLabel"] {{
            color: {TEXT_SECONDARY};
            font-size: 13px;
            font-weight: 600;
        }}

        div[data-testid="stMetricValue"] {{
            color: {PRIMARY_COLOUR};
            font-size: 25px;
            font-weight: 700;
        }}

        div[data-testid="stMetricDelta"] {{
            font-size: 13px;
            font-weight: 600;
        }}


        /* ==================================================
           DATAFRAME AND TABLES
        ================================================== */

        div[data-testid="stDataFrame"] {{
            background-color: {CARD_BACKGROUND};
            border: 1px solid {LIGHT_BORDER};
            border-radius: 9px;
            overflow: hidden;
        }}

        div[data-testid="stDataFrame"] * {{
            font-family: {FONT_FAMILY};
            font-size: 13px;
        }}

        .stTable {{
            background-color: {CARD_BACKGROUND};
            border: 1px solid {LIGHT_BORDER};
            border-radius: 8px;
            overflow: hidden;
        }}

        .stTable table {{
            width: 100%;
            border-collapse: collapse;
        }}

        .stTable th {{
            background-color: {PRIMARY_LIGHT};
            color: {PRIMARY_DARK};
            font-weight: 700;
            padding: 9px;
        }}

        .stTable td {{
            color: {TEXT_PRIMARY};
            padding: 9px;
            border-bottom: 1px solid {LIGHT_BORDER};
        }}


        /* ==================================================
           TABS
        ================================================== */

        button[data-baseweb="tab"] {{
            color: {TEXT_SECONDARY};
            font-size: 14px;
            font-weight: 600;
            padding-left: 18px;
            padding-right: 18px;
        }}

        button[data-baseweb="tab"][aria-selected="true"] {{
            color: {PRIMARY_COLOUR};
            font-weight: 700;
        }}

        div[data-baseweb="tab-highlight"] {{
            background-color: {PRIMARY_COLOUR};
        }}

        div[data-baseweb="tab-border"] {{
            background-color: {LIGHT_BORDER};
        }}


        /* ==================================================
           EXPANDERS
        ================================================== */

        div[data-testid="stExpander"] {{
            background-color: {CARD_BACKGROUND};
            border: 1px solid {LIGHT_BORDER};
            border-radius: 9px;
            overflow: hidden;
            margin-bottom: 10px;
        }}

        div[data-testid="stExpander"] summary {{
            color: {PRIMARY_DARK};
            font-size: 14px;
            font-weight: 700;
            padding-top: 4px;
            padding-bottom: 4px;
        }}

        div[data-testid="stExpander"] summary:hover {{
            color: {PRIMARY_COLOUR};
        }}


        /* ==================================================
           ALERT BOXES
        ================================================== */

        div[data-testid="stAlert"] {{
            border-radius: 8px;
            font-size: 14px;
            line-height: 1.5;
        }}

        div[data-testid="stAlert"] p {{
            margin-bottom: 0;
        }}


        /* ==================================================
           CUSTOM NOTE BOX
        ================================================== */

        .custom-note-box {{
            background-color: {CARD_BACKGROUND};
            border: 1px solid {BORDER_COLOUR};
            border-left: 5px solid {PRIMARY_COLOUR};
            border-radius: 8px;
            padding: 15px 17px;
            margin-top: 10px;
            margin-bottom: 16px;
        }}

        .custom-box-title {{
            color: {PRIMARY_COLOUR};
            font-size: 15px;
            font-weight: 700;
            margin-bottom: 6px;
        }}

        .custom-box-text {{
            color: {TEXT_SECONDARY};
            font-size: 14px;
            line-height: 1.55;
        }}


        /* ==================================================
           EMPTY STATE
        ================================================== */

        .empty-state-box {{
            background-color: {CARD_BACKGROUND};
            border: 1px dashed {BORDER_COLOUR};
            border-radius: 10px;
            padding: 26px;
            text-align: center;
            margin-top: 14px;
            margin-bottom: 16px;
        }}

        .empty-state-title {{
            color: {PRIMARY_COLOUR};
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 7px;
        }}

        .empty-state-message {{
            color: {TEXT_MUTED};
            font-size: 14px;
            line-height: 1.5;
        }}


        /* ==================================================
           CARD COMPONENT
        ================================================== */

        .summary-card {{
            background-color: {CARD_BACKGROUND};
            border: 1px solid {LIGHT_BORDER};
            border-radius: 10px;
            padding: 16px 18px;
            margin-bottom: 12px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
        }}

        .summary-card-title {{
            color: {TEXT_SECONDARY};
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 5px;
        }}

        .summary-card-value {{
            color: {PRIMARY_COLOUR};
            font-size: 22px;
            font-weight: 700;
        }}

        .summary-card-note {{
            color: {TEXT_MUTED};
            font-size: 12px;
            margin-top: 5px;
        }}


        /* ==================================================
           STATUS BADGES
        ================================================== */

        .status-badge {{
            display: inline-block;
            border-radius: 999px;
            padding: 4px 10px;
            font-size: 12px;
            font-weight: 700;
        }}

        .status-success {{
            color: {SUCCESS_COLOUR};
            background-color: {SUCCESS_BACKGROUND};
            border: 1px solid #BBF7D0;
        }}

        .status-warning {{
            color: {WARNING_COLOUR};
            background-color: {WARNING_BACKGROUND};
            border: 1px solid #FDE68A;
        }}

        .status-error {{
            color: {ERROR_COLOUR};
            background-color: {ERROR_BACKGROUND};
            border: 1px solid #FECACA;
        }}

        .status-info {{
            color: {INFO_COLOUR};
            background-color: {INFO_BACKGROUND};
            border: 1px solid #BAE6FD;
        }}


        /* ==================================================
           SIDEBAR
        ================================================== */

        section[data-testid="stSidebar"] {{
            background-color: {SIDEBAR_BACKGROUND};
            border-right: 1px solid {LIGHT_BORDER};
        }}

        section[data-testid="stSidebar"] > div {{
            padding-top: 1rem;
        }}

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {{
            color: {PRIMARY_COLOUR};
        }}

        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label {{
            color: {TEXT_PRIMARY};
        }}

        section[data-testid="stSidebar"] .stButton > button {{
            background-color: {CARD_BACKGROUND};
        }}


        /* ==================================================
           SIDEBAR NAVIGATION LINKS
        ================================================== */

        section[data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"] {{
            border-radius: 7px;
            padding-top: 7px;
            padding-bottom: 7px;
            color: {TEXT_PRIMARY};
        }}

        section[data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"]:hover {{
            background-color: {PRIMARY_LIGHT};
            color: {PRIMARY_COLOUR};
        }}


        /* ==================================================
           CAPTIONS AND HELP TEXT
        ================================================== */

        .stCaption,
        div[data-testid="stCaptionContainer"] {{
            color: {TEXT_MUTED};
            font-size: 12px;
            line-height: 1.45;
        }}

        div[data-testid="InputInstructions"] {{
            color: {TEXT_MUTED};
            font-size: 12px;
        }}


        /* ==================================================
           DIVIDERS
        ================================================== */

        hr {{
            border: none;
            border-top: 1px solid {LIGHT_BORDER};
            margin-top: 18px;
            margin-bottom: 18px;
        }}


        /* ==================================================
           STREAMLIT TOOLBAR AND FOOTER
        ================================================== */

        footer {{
            visibility: hidden;
        }}

        #MainMenu {{
            visibility: hidden;
        }}

        div[data-testid="stToolbar"] {{
            visibility: hidden;
            height: 0;
        }}


        /* ==================================================
           SPINNER
        ================================================== */

        div[data-testid="stSpinner"] {{
            color: {PRIMARY_COLOUR};
        }}


        /* ==================================================
           RESPONSIVE DESIGN
        ================================================== */

        @media only screen and (max-width: 900px) {{

            .block-container {{
                padding-left: 1rem;
                padding-right: 1rem;
                padding-top: 1rem;
            }}

            .main-title {{
                font-size: 28px;
            }}

            .page-subtitle {{
                font-size: 14px;
            }}

            .section-title {{
                font-size: 20px;
            }}

            div[data-testid="stMetricValue"] {{
                font-size: 21px;
            }}

            div[data-testid="stMetric"] {{
                min-height: 100px;
            }}
        }}


        @media only screen and (max-width: 600px) {{

            .main-title {{
                font-size: 25px;
            }}

            .section-title {{
                font-size: 18px;
            }}

            .subsection-title {{
                font-size: 16px;
            }}

            .custom-note-box,
            .empty-state-box,
            .summary-card {{
                padding: 13px;
            }}
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# STANDARD PAGE SETUP
# =========================================================
def setup_page(
    page_title: str,
    page_icon: str = PAGE_ICON,
    layout: str = "wide",
    initial_sidebar_state: str = "expanded",
) -> None:
    """
    Configure and style a page in one function.

    Instead of:

    page_config(...)
    page_style()

    You may use:

    setup_page(
        page_title="Cost per Parcel"
    )
    """

    page_config(
        page_title=page_title,
        page_icon=page_icon,
        layout=layout,
        initial_sidebar_state=(
            initial_sidebar_state
        ),
    )

    page_style()