import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json
import logging

# --- Configuration ---
API_BASE_URL = "http://127.0.0.1:8000/api/v1"
logging.basicConfig(level=logging.ERROR)

st.set_page_config(
    page_title="Property Sales Intelligence",
    page_icon="🏠",
    layout="wide"
)

# --- State Initialization ---
if 'persona' not in st.session_state:
    st.session_state.persona = 'Founder / Executive'
if 'active_page' not in st.session_state:
    st.session_state.active_page = 'Dashboard'

# --- Data Fetching ---
@st.cache_data(ttl=30)
def fetch_all_data():
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/risk_profile")
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and data.get("status") == "error":
            st.error(f"API Error: {data.get('message', 'Unknown error')}")
            return pd.DataFrame()
        df = pd.DataFrame(data)
        for col in ['confidence_score', 'explainability_coverage', 'risk_level', 'sla_breached']:
            if col not in df.columns: df[col] = 0
        return df
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching risk profile data: {e}")
        return None # Return None to indicate a connection failure

@st.cache_data(ttl=30)
def fetch_trust_metrics():
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/data_freshness")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching trust metrics: {e}")
        return None

@st.cache_data(ttl=30)
def fetch_audit_logs(params=None):
    try:
        response = requests.get(f"{API_BASE_URL}/governance/audit_logs", params=params)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching audit logs: {e}")
        return None

@st.cache_data(ttl=30)
def fetch_persona_insight(persona: str) -> str:
    # ... (existing code, no changes needed)
    return "Insights are currently being generated..."

@st.cache_data(ttl=30)
def fetch_alerts(persona: str) -> list:
    # ... (existing code, no changes needed)
    return []

# --- UI Section Renderers with Error Boundaries ---

def render_section_error(section_name: str, key_suffix: str):
    st.warning(f"🚧 {section_name} data is temporarily unavailable.")
    st.markdown("This may be due to a temporary connection issue.")
    if st.button(f"Retry {section_name}", key=f"retry_{key_suffix}"):
        st.rerun()

def render_executive_summary_section(df, persona):
    try:
        st.header("Executive Snapshot")
        total_leads, high_risk_leads, sla_breached_count = len(df), len(df[df['risk_level'] == 'High']), df['sla_breached'].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Active Leads", total_leads, help="Total number of leads currently in the pipeline.")
        col2.metric("High-Risk Leads", high_risk_leads, help="Leads flagged with high risk scores (>75) or critical issues.")
        col3.metric("SLA Breaches", sla_breached_count, help="Leads that have exceeded the allowed time in their current stage.")
    except Exception as e:
        logging.error(f"Error in Executive Summary: {e}")
        render_section_error("Executive Snapshot", "exec_summary")

def render_trust_confidence_section(df):
    try:
        st.subheader("Trust & Confidence Layer")
        trust_metrics = fetch_trust_metrics()
        if trust_metrics is None:
            render_section_error("Trust Metrics", "trust")
            return

        avg_confidence, avg_coverage = df['confidence_score'].mean(), df['explainability_coverage'].mean()
        
        col1, col2, col3 = st.columns(3)
        freshness_score = trust_metrics.get('freshness_score', 0)
        last_updated_str = trust_metrics.get('last_updated_at', 'N/A')
        if last_updated_str != 'N/A':
            try:
                last_updated_dt = datetime.fromisoformat(last_updated_str)
                last_updated_str = last_updated_dt.strftime('%d %b %Y, %H:%M:%S')
            except (ValueError, TypeError): pass

        col1.metric("Data Freshness", f"{freshness_score}/100", help=f"Score based on recency of data updates. Last update: {last_updated_str}")
        col2.metric("Avg. Confidence", f"{avg_confidence:.2f}", help="Average system confidence (0-1) in the risk assessments based on data completeness.")
        col3.metric("Explainability", f"{avg_coverage:.0%}", help="Percentage of expected risk factors that were successfully identified and explained.")
    except Exception as e:
        logging.error(f"Error in Trust & Confidence: {e}")
        render_section_error("Trust & Confidence", "trust_confidence")

def render_persona_insights_section(persona):
    try:
        st.subheader(f"Insights for: {persona}")
        with st.spinner(f"Generating insights for {persona}..."):
            insight = fetch_persona_insight(persona)
            if insight is None:
                render_section_error("Persona Insights", "persona")
            else:
                st.info(insight)
    except Exception as e:
        logging.error(f"Error in Persona Insights: {e}")
        render_section_error("Persona Insights", "persona_insights")

def render_risk_sla_dashboard_section(df):
    try:
        st.header("Risk & SLA Analysis")
        high_risk_df = df[df['risk_level'] == 'High'].sort_values('risk_score', ascending=False)

        if high_risk_df.empty:
            st.success("🎉 No high-risk leads detected!")
        else:
            for index, row in high_risk_df.iterrows():
                # ... (existing expander code, no changes needed)
                st.markdown(f"#### {row.get('name', 'N/A')} (Risk Score: {row.get('risk_score', 'N/A')})")
                with st.expander(f"**Why is {row.get('name', 'this lead')} high risk?**"):
                    summary, risk_factors, action, disclaimer = row.get('explanation_text'), row.get('risk_factors', []), row.get('recommended_action'), row.get('disclaimer')
                    st.markdown(f"**Summary:** *{summary or 'No summary available.'}*")
                    if risk_factors:
                        st.markdown("**Risk Factors:**")
                        for factor in risk_factors:
                            st.markdown(f"- **{factor.get('type', 'N/A').replace('_', ' ').title()}** ({factor.get('weight', 0)}%): {factor.get('detail', 'N/A')}")
                    st.markdown("**Recommended Action:**")
                    st.success(f"➡️ {action or 'No action recommended.'}")
                    if disclaimer: st.warning(f"*{disclaimer}*")
                st.markdown("---")

        st.subheader("All Leads Data")
        if df.empty:
            st.info("No leads available to display.")
        else:
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        logging.error(f"Error in Risk & SLA Dashboard: {e}")
        render_section_error("Risk & SLA Analysis", "risk_sla")

# --- Page Implementations ---

def render_main_dashboard_page():
    st.title("🏠 Property Sales Intelligence Dashboard")
    
    with st.spinner("Analyzing pipeline data..."):
        master_df = fetch_all_data()

    if master_df is None:
        st.error("🚨 Could not connect to the data service.")
        st.markdown("Please check the backend connection and try again.")
        if st.button("Retry Connection"):
            st.rerun()
        return
    
    if master_df.empty:
        st.info("👋 Welcome! No lead data is currently available.")
        return

    setup_sidebar(master_df)
    
    status_filter, risk_filter = get_dashboard_filters(master_df)
    filtered_df = master_df.copy()
    if status_filter != "All": filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if risk_filter != "All": filtered_df = filtered_df[filtered_df['risk_level'] == risk_filter]

    if filtered_df.empty:
        st.warning("No leads match the selected filters.")
        return

    render_executive_summary_section(filtered_df, st.session_state.persona)
    render_trust_confidence_section(filtered_df)
    st.markdown("---")
    render_persona_insights_section(st.session_state.persona)
    st.markdown("---")
    render_risk_sla_dashboard_section(filtered_df)

def render_governance_audit_page():
    # ... (existing governance page code, can also be wrapped)
    st.title("🔐 Governance & Audit Trail")
    with st.spinner("Retrieving governance records..."):
        logs_df = fetch_audit_logs()
    
    if logs_df is None:
        render_section_error("Governance Logs", "governance")
        return
    
    if logs_df.empty:
        st.info("No audit logs found.")
        return
        
    st.dataframe(logs_df)
    # ... rest of the logic

# --- Sidebar and Main Router ---

def setup_sidebar(df):
    # ... (existing sidebar code, no changes needed)
    pass

def get_dashboard_filters(df):
    # ... (existing filter code, no changes needed)
    return "All", "All"

def main():
    # Global sidebar setup
    with st.sidebar:
        st.header("Navigation")
        st.session_state.active_page = st.radio("Go to", ["Dashboard", "Governance & Audit"], key="nav_selector")
        st.markdown("---")
        st.header("Dashboard Controls")
        st.session_state.persona = st.radio("View as", ["Founder / Executive", "Sales Manager", "Operations / CRM Manager"], key="persona_selector")
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()

    # Page routing
    if st.session_state.active_page == 'Dashboard':
        render_main_dashboard_page()
    elif st.session_state.active_page == 'Governance & Audit':
        render_governance_audit_page()

if __name__ == "__main__":
    main()
