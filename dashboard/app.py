"""Streamlit dashboard — Ethiopia Financial Inclusion Forecasting System.

Run with: streamlit run dashboard/app.py
"""

import sys
from pathlib import Path

import streamlit as st

# Make src/ importable when run via `streamlit run dashboard/app.py`
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

st.set_page_config(
    page_title="Ethiopia Financial Inclusion Forecast",
    page_icon="📊",
    layout="wide",
)

st.title("Ethiopia Financial Inclusion Forecasting System")
st.caption("Selam Analytics — tracking Ethiopia's digital financial transformation")

PAGES = ["Overview", "Trends", "Forecasts", "Inclusion Projections"]
page = st.sidebar.radio("Navigate", PAGES)

if page == "Overview":
    st.header("Overview")
    st.info(
        "Key metrics summary cards, P2P/ATM crossover ratio, and growth-rate "
        "highlights will appear here (Task 5)."
    )
elif page == "Trends":
    st.header("Trends")
    st.info(
        "Interactive time series with date range selection and channel "
        "comparison will appear here (Task 5)."
    )
elif page == "Forecasts":
    st.header("Forecasts")
    st.info(
        "Forecast visualizations with confidence intervals and model "
        "selection will appear here (Task 5)."
    )
else:
    st.header("Inclusion Projections")
    st.info(
        "Projections toward the 60% inclusion target with scenario selection "
        "will appear here (Task 5)."
    )
