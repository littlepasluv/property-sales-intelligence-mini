import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# --- Configuration ---
API_BASE_URL = "http://127.0.0.1:8000/api/v1"

st.set_page_config(
    page_title="Property Sales Intelligence",
    page_icon="🏠",
    layout="wide"
)

# --- State Initialization ---
if 'persona' not in st.session_state:
    st.session_state.persona = 'Founder / Executive'

# --- Data Fetching ---
@st.cache_data(ttl=30)
def fetch_all_data():
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/risk_profile")
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Error fetching data: {e}")
        return None

@st.cache_data(ttl=30)
def fetch_persona_insight(persona: str) -> str:
    persona_map = {"Founder / Executive": "founder", "Sales Manager": "sales", "Operations / CRM Manager": "ops"}
    api_persona = persona_map.get(persona, "founder")
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/persona_insights?persona={api_persona}")
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f"⚠️ Error fetching insights: {e}"

@st.cache_data(ttl=30)
def fetch_alerts(persona: str) -> list:
    persona_map = {"Founder / Executive": "founder", "Sales Manager": "sales", "Operations / CRM Manager": "ops"}
    api_persona = persona_map.get(persona, "sales")
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/alerts?persona={api_persona}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return []

# --- UI Components ---
def render_alerts_panel(persona: str):
    alerts = fetch_alerts(persona)
    if not alerts: return
    with st.sidebar:
        with st.expander("🚨 Alerts & Notifications", expanded=True):
            for alert in sorted(alerts, key=lambda x: x['severity'], reverse=True):
                st.markdown(f"**{alert.get('icon', '⚠️')} {alert['title']}**")
                st.caption(alert['message'])
                if 'action_hint' in alert:
                    st.markdown(f"<small>_Action: {alert['action_hint']}_</small>", unsafe_allow_html=True)
                st.markdown("---")

def setup_sidebar(df):
    with st.sidebar:
        st.header("Dashboard Controls")
        persona_options = ["Founder / Executive", "Sales Manager", "Operations / CRM Manager"]
        st.session_state.persona = st.radio("View as", persona_options, key="persona_selector")
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    
    render_alerts_panel(st.session_state.persona)

    with st.sidebar:
        st.header("Filters")
        status_options = ["All"] + df['status'].unique().tolist()
        status_filter = st.selectbox("Filter by Status", status_options)
        risk_options = ["All"] + df['risk_level'].unique().tolist()
        risk_filter = st.selectbox("Filter by Risk Level", risk_options)
    return status_filter, risk_filter

def render_executive_summary(df, persona):
    st.header("Executive Snapshot")
    total_leads, high_risk_leads, sla_breached_count = len(df), len(df[df['risk_level'] == 'High']), df['sla_breached'].sum()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Active Leads", total_leads)
    col2.metric("High-Risk Leads", high_risk_leads)
    col3.metric("SLA Breaches", sla_breached_count)
    st.markdown("---")
    st.subheader(f"Insights for: {persona}")
    st.info(fetch_persona_insight(persona))

def render_risk_sla_dashboard(df):
    st.header("Risk & SLA Analysis")
    
    high_risk_df = df[df['risk_level'] == 'High'].sort_values('risk_score', ascending=False)

    for index, row in high_risk_df.iterrows():
        st.markdown(f"#### {row['name']} (Risk Score: {row['risk_score']})")
        
        with st.expander("**Why is this lead high risk?**"):
            # Defensively access explanation fields
            summary = row.get('explanation_text', 'No summary available.')
            risk_factors = row.get('risk_factors', [])
            recommended_action = row.get('recommended_action', 'No action recommended.')
            disclaimer = row.get('disclaimer')

            st.markdown(f"**Summary:** *{summary}*")
            
            if risk_factors:
                st.markdown("**Risk Factors:**")
                for factor in risk_factors:
                    st.markdown(f"- **{factor.get('type', 'N/A').replace('_', ' ').title()}** ({factor.get('weight', 0)}%): {factor.get('detail', 'N/A')}")
            
            st.markdown("**Recommended Action:**")
            st.success(f"➡️ {recommended_action}")

            if disclaimer:
                st.warning(f"*{disclaimer}*")
        st.markdown("---")

    st.subheader("All Leads Data")
    st.dataframe(df[["name", "status", "age_days", "risk_score", "risk_level", "sla_breached"]], use_container_width=True)

# --- Main Application ---
st.title("🏠 Property Sales Intelligence")
master_df = fetch_all_data()

if master_df is not None and not master_df.empty:
    status_filter, risk_filter = setup_sidebar(master_df)

    filtered_df = master_df.copy()
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if risk_filter != "All":
        filtered_df = filtered_df[filtered_df['risk_level'] == risk_filter]

    render_executive_summary(filtered_df, st.session_state.persona)
    render_risk_sla_dashboard(filtered_df)
else:
    st.warning("Could not load dashboard data. Ensure the backend is running.")
