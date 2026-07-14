import streamlit as st


def page_config():

    st.set_page_config(
        page_title="Potential Return - Cash",
        page_icon="💰",
        layout="wide"
    )


def page_style():

    st.markdown("""
    <style>

    .stApp{
        background:red !important;
    }

    h1{
        color:#1E3A8A !important;
        font-size:34px !important;
    }

    </style>
    """, unsafe_allow_html=True)