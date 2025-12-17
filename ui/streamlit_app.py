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

# --- UI Components ---
def display_ingestion_summary():
    if not st.session_state.last_ingestion_summary:
        return

    summary = st.session_state.last_ingestion_summary
    run_at_str = summary.get('run_at')
    run_at_dt = datetime.fromisoformat(run_at_str)
    
    st.sidebar.subheader(f"Last Ingestion: {run_at_dt.strftime('%H:%M:%S')}")

    # --- Overall Health Summary ---
    source_statuses = []
    for source, results in summary.get('sources', {}).items():
        inserted = results.get('inserted', 0)
        updated = results.get('updated', 0)
        failed = results.get('failed', 0)
        
        if failed > 0 and (inserted == 0 and updated == 0):
            source_statuses.append("failed")
        elif failed > 0:
            source_statuses.append("partial")
        else:
            source_statuses.append("success")

    if "failed" in source_statuses:
        st.sidebar.error("🔴 Ingestion failed for one or more sources.")
    elif "partial" in source_statuses:
        st.sidebar.warning("🟡 Ingestion partially succeeded.")
    else:
        st.sidebar.success("🟢 All sources ingested successfully.")

    # --- Per-Source Cards ---
    for source, results in summary.get('sources', {}).items():
        inserted = results.get('inserted', 0)
        updated = results.get('updated', 0)
        failed = results.get('failed', 0)
        
        if failed == 0:
            status, icon = "SUCCESS", "🟢"
        elif failed > 0 and (inserted > 0 or updated > 0):
            status, icon = "PARTIAL", "🟡"
        else:
            status, icon = "FAILED", "🔴"
            
        with st.sidebar.container(border=True):
            st.markdown(f"**{icon} {source.upper()}** - {status}")
            col1, col2, col3 = st.columns(3)
            col1.markdown(f"**{inserted}** Inserted")
            col2.markdown(f"{updated} Updated")
            col3.markdown(f"**{failed}** Failed")

def setup_sidebar():
    with st.sidebar:
        st.header("Navigation")
        st.radio("Go to", ["Dashboard", "Governance & Audit"], key="active_page")
        st.markdown("---")
        st.header("Dashboard Controls")
        st.radio("View as", ["Founder / Executive", "Sales Manager", "Operations / CRM Manager"], key="persona")
        
        if st.button("🔄 Refresh Data", key="refresh_button"):
            clear_all_caches()
            st.rerun()
        
        st.header("Ingestion")
        if st.button("Run Mock Ingestion", key="ingest_button"):
            with st.spinner("Ingesting data from all sources..."):
                try:
                    response = requests.post(f"{API_BASE_URL}/ingestion/run", timeout=10)
                    response.raise_for_status()
                    st.session_state.last_ingestion_summary = response.json().get("summary")
                    st.toast("Ingestion complete!", icon="🎉")
                    clear_all_caches()
                    st.rerun()
                except requests.exceptions.RequestException as e:
                    st.error(f"Ingestion failed: {e}")
        
        display_ingestion_summary()

def get_dashboard_filters(df):
    # ...
    pass

def render_main_dashboard_page():
    st.title("🏠 Property Sales Intelligence Dashboard")
    
    # Fetch data
    master_df = pd.DataFrame() # Placeholder
    
    # ... (rest of dashboard rendering logic)

def main():
    # The sidebar is now rendered once, and only once, here.
    setup_sidebar()

    # Page routing
    if st.session_state.active_page == 'Dashboard':
        render_main_dashboard_page()
    # ... (other pages)

if __name__ == "__main__":
    main()
