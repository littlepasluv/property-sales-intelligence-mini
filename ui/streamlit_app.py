import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json
import logging
import time
from threading import Thread

# --- Configuration ---
API_BASE_URL = "http://127.0.0.1:8000/api/v1"
logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="Property Sales Intelligence", page_icon="🏠", layout="wide")

# --- State and Cache Management ---
if 'persona' not in st.session_state: st.session_state.persona = 'Founder / Executive'
if 'active_page' not in st.session_state: st.session_state.active_page = 'Dashboard'
if 'last_ingestion_summary' not in st.session_state: st.session_state.last_ingestion_summary = None

def clear_all_caches():
    st.cache_data.clear()
    # ... (existing cache clearing logic)

# --- Data Fetching ---
@st.cache_data(ttl=60)
def fetch_data_quality_report():
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/data_quality")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch data quality report: {e}")
        return None

# --- UI Components ---
def display_data_quality_section():
    report = fetch_data_quality_report()
    if not report:
        st.warning("Data Quality report is currently unavailable.")
        return

    level = report.get("confidence_level", "Low")
    completeness = report.get("avg_completeness", 0)
    
    color_map = {"High": "green", "Medium": "orange", "Low": "red"}
    icon_map = {"High": "✅", "Medium": "⚠️", "Low": "🔥"}
    
    st.subheader("Data Quality & Confidence")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"<h5>Confidence Level: <span style='color:{color_map[level]};'>{level.upper()} {icon_map[level]}</span></h5>",
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(f"<h5>Avg. Completeness: **{completeness:.1f}%**</h5>", unsafe_allow_html=True)

    if level != "High":
        with st.expander("Show Warnings", expanded=False):
            for warning in report.get("warnings", []):
                st.warning(warning)

def display_ingestion_summary():
    # ... (existing ingestion summary logic)
    pass

def setup_sidebar():
    with st.sidebar:
        st.header("Navigation")
        # ... (nav controls)
        st.markdown("---")
        st.header("Dashboard Controls")
        # ... (persona controls)
        if st.button("🔄 Refresh Data", key="refresh_button"):
            clear_all_caches()
            st.rerun()
        
        st.header("Ingestion")
        # ... (ingestion button)
        
        display_ingestion_summary()

def render_main_dashboard_page():
    st.title("🏠 Property Sales Intelligence Dashboard")
    
    # Display Data Quality section at the top
    display_data_quality_section()
    st.markdown("---")

    # ... (rest of the dashboard rendering logic)
    
def main():
    setup_sidebar()
    if st.session_state.active_page == 'Dashboard':
        render_main_dashboard_page()
    # ... (other pages)

if __name__ == "__main__":
    main()
