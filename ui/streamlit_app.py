import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timezone
import json
import logging
import time

# --- Configuration ---
API_BASE_URL = "http://127.0.0.1:8000/api/v1"
logging.basicConfig(level=logging.ERROR)

st.set_page_config(page_title="Property Sales Intelligence", page_icon="🏠", layout="wide")

# --- State and Cache Management ---
if 'persona' not in st.session_state: st.session_state.persona = 'Founder / Executive'
if 'active_page' not in st.session_state: st.session_state.active_page = 'Dashboard'
if 'last_fetch_time' not in st.session_state: st.session_state.last_fetch_time = 0

def clear_all_caches():
    """Clears both Streamlit and backend caches."""
    st.cache_data.clear()
    try:
        requests.post(f"{API_BASE_URL}/governance/cache/clear")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to clear backend cache: {e}")
    st.session_state.last_fetch_time = 0
    st.toast("Cache cleared!", icon="✅")

# --- Data Fetching with Caching ---
@st.cache_data(ttl=120)
def fetch_all_data():
    st.session_state.last_fetch_time = time.time()
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/risk_profile")
        response.raise_for_status()
        # ... (error handling)
        return pd.DataFrame(response.json())
    except requests.exceptions.RequestException:
        return None

@st.cache_data(ttl=300)
def fetch_trust_metrics():
    # ... (fetch logic)
    pass

@st.cache_data(ttl=60)
def fetch_audit_logs(params=None):
    # ... (fetch logic)
    pass

@st.cache_data(ttl=300)
def fetch_persona_insight(persona: str):
    # ... (fetch logic)
    pass

@st.cache_data(ttl=120)
def fetch_alerts(persona: str):
    # ... (fetch logic)
    pass

# --- UI Components ---
def display_cache_status():
    if st.session_state.last_fetch_time > 0:
        age = time.time() - st.session_state.last_fetch_time
        st.sidebar.caption(f"Cached • updated {int(age)}s ago")
    else:
        st.sidebar.caption("Cache is fresh")

def setup_sidebar():
    with st.sidebar:
        st.header("Navigation")
        st.session_state.active_page = st.radio("Go to", ["Dashboard", "Governance & Audit"], key="nav_selector")
        st.markdown("---")
        st.header("Dashboard Controls")
        st.session_state.persona = st.radio("View as", ["Founder / Executive", "Sales Manager", "Operations / CRM Manager"], key="persona_selector")
        if st.button("🔄 Refresh Data"):
            clear_all_caches()
            st.rerun()
        display_cache_status()
    # ... (rest of sidebar)

# --- Page Implementations with Error Boundaries ---
def render_section_error(section_name: str, key_suffix: str):
    st.warning(f"🚧 {section_name} data is temporarily unavailable.")
    if st.button(f"Retry {section_name}", key=f"retry_{key_suffix}"):
        st.rerun()

def render_executive_summary_section(df, persona):
    try:
        # ... (metric calculations)
        st.header("Executive Snapshot")
        total_leads, high_risk_leads, sla_breached_count = len(df), len(df[df['risk_level'] == 'High']), df['sla_breached'].sum()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Active Leads", total_leads)
        col2.metric("High-Risk Leads", high_risk_leads)
        col3.metric("SLA Breaches", sla_breached_count)
    except Exception as e:
        render_section_error("Executive Snapshot", "exec_summary")

# ... (other render functions with error boundaries)

def render_main_dashboard_page():
    st.title("🏠 Property Sales Intelligence Dashboard")
    
    with st.spinner("Analyzing pipeline data..."):
        master_df = fetch_all_data()

    if master_df is None:
        st.error("🚨 Could not connect to the data service.")
        if st.button("Retry Connection"): st.rerun()
        return
    
    # ... (rest of dashboard rendering)

def render_governance_audit_page():
    st.title("🔐 Governance & Audit Trail")
    with st.spinner("Retrieving governance records..."):
        logs_df = fetch_audit_logs()
    # ... (rest of governance page rendering)

# --- Main Application Router ---
def main():
    setup_sidebar()
    if st.session_state.active_page == 'Dashboard':
        render_main_dashboard_page()
    elif st.session_state.active_page == 'Governance & Audit':
        render_governance_audit_page()

if __name__ == "__main__":
    main()
