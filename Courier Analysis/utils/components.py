import streamlit as st


def cost_basis(title, text):
    st.markdown(
        f"""
        <div class="cost-basis-box">
            <div class="cost-basis-title">{title}</div>
            <div class="cost-basis-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )