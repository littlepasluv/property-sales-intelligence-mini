import streamlit as st
import requests
import pandas as pd

# --- Configuration ---
API_URL = "http://127.0.0.1:8000/api/v1/analytics/dashboard"

st.set_page_config(
    page_title="Property Sales Intelligence (Mini)",
    page_icon="🏠",
    layout="wide"
)

# --- Data Fetching ---
@st.cache_data(ttl=60)  # Cache data for 60 seconds to avoid spamming the API
def fetch_dashboard_analytics():
    """
    Fetches analytics data from the backend API.
    Returns None if the API call fails.
    """
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Raise exception for 4xx/5xx errors
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Error connecting to backend: {e}")
        return None

# --- Main Application ---
st.title("🏠 Property Sales Intelligence (Mini)")
st.markdown("### Data-driven insights for property sales")
st.markdown("---")

# Fetch data
analytics_data = fetch_dashboard_analytics()

if analytics_data:
    # Extract data for easier access
    leads_data = analytics_data.get("leads", {})
    followups_data = analytics_data.get("followups", {})

    # --- Key Metrics Section ---
    st.header("📊 Key Metrics")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Leads", value=leads_data.get("total_leads", 0))
    with col2:
        st.metric(label="Total Follow-ups", value=followups_data.get("total_followups", 0))
    with col3:
        # Calculate pending follow-ups safely
        pending_count = followups_data.get("by_status", {}).get("pending", 0)
        st.metric(label="Pending Actions", value=pending_count)

    st.markdown("---")

    # --- Lead Overview Section ---
    st.header("👥 Lead Overview")
    
    lead_status = leads_data.get("by_status", {})
    if lead_status:
        st.write("Leads by Status:")
        st.bar_chart(lead_status)
    else:
        st.info("No lead data available yet.")

    st.markdown("---")

    # --- Follow-up Overview Section ---
    st.header("📅 Follow-up Overview")
    
    followup_status = followups_data.get("by_status", {})
    if followup_status:
        st.write("Follow-ups by Status:")
        st.bar_chart(followup_status)
    else:
        st.info("No follow-up data available yet.")

else:
    # Fallback if API is down
    st.warning("Could not load dashboard data. Please ensure the backend server is running.")
