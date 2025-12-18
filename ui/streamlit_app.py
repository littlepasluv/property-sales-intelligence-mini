import streamlit as st
import requests
import logging

# --- Configuration & Initialization ---
API_BASE_URL = "http://127.0.0.1:8000/api/v1"
logging.basicConfig(level=logging.INFO)

# --- DEV AUTH BYPASS – REMOVE BEFORE PRODUCTION ---
DEV_MODE_BYPASS_AUTH = True
# --- END DEV AUTH BYPASS ---

st.set_page_config(page_title="Property Sales Intelligence", page_icon="🏠", layout="wide")

def init_dashboard_state():
    """
    Initializes all required keys in st.session_state for the dashboard.
    This function is called once at the start of the script.
    """
    defaults = {
        "is_authenticated": False,
        "access_token": None,
        "user_role": "founder",
        "persona": "Founder / Executive",
        "active_page": "Dashboard",
        "debug_mode": False,
        "dashboard_loaded": False,
        "recommendations_data": None,
        "confidence_data": None,
        "simulation_result": None,
        "last_error": None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
            
    if DEV_MODE_BYPASS_AUTH:
        st.session_state.is_authenticated = True
        st.session_state.access_token = "dev-token-do-not-use-in-prod"
        st.session_state.user_role = "founder"

def api_request(method, endpoint, **kwargs):
    """Centralized function for making authenticated API requests."""
    headers = kwargs.pop("headers", {})
    if st.session_state.get("access_token"):
        headers["Authorization"] = f"Bearer {st.session_state.access_token}"
    else:
        headers["X-User-Role"] = st.session_state.get("user_role", "founder")
    url = f"{API_BASE_URL}/{endpoint}"
    try:
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else None
    except requests.exceptions.RequestException as e:
        st.session_state.last_error = f"API Error: {e}"
        return None

def load_dashboard_data():
    """
    Fetches all necessary data for the dashboard in a single, one-time load.
    """
    try:
        st.session_state.recommendations_data = api_request("get", "decisions/recommendations")
        st.session_state.confidence_data = api_request("get", "analytics/confidence")
        st.session_state.dashboard_loaded = True
        st.session_state.last_error = None
    except Exception as e:
        st.session_state.last_error = str(e)
        st.session_state.dashboard_loaded = False

def render_recommendations(recommendations):
    """Renders the 'Recommended Actions' section from session state."""
    st.header("Recommended Actions")
    if not recommendations:
        st.info("✅ No critical actions needed at this time. System is operating within normal parameters.")
        return

    priority_map = {
        "critical": {"icon": "🚨", "color": "red"},
        "high": {"icon": "🔥", "color": "orange"},
        "medium": {"icon": "🔵", "color": "blue"},
        "low": {"icon": "⚪️", "color": "gray"}
    }
    for rec in sorted(recommendations, key=lambda r: list(priority_map.keys()).index(r['priority'])):
        priority_config = priority_map.get(rec['priority'], {"icon": "❓", "color": "gray"})
        with st.container(border=True):
            col1, col2 = st.columns([1, 9])
            with col1:
                st.markdown(f"<h1 style='text-align: center; color: {priority_config['color']};'>{priority_config['icon']}</h1>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"**{rec['title']}**")
                st.caption(f"Confidence: {rec['confidence']}% | Suggested Owner: {rec['suggested_owner']}")
            st.write(rec['recommendation'])
            with st.expander("View Rationale & Impact"):
                st.markdown(f"**Rationale:** {rec['rationale']}")
                st.markdown(f"**Impacted Metrics:** `{'`, `'.join(rec['impacted_metrics'])}`")
            if rec['governance_flags']:
                st.warning(f"**Governance Warning:** {', '.join(rec['governance_flags'])}", icon="⚠️")

def render_trust_confidence(confidence_data):
    """Renders the 'Trust & Confidence' section from session state."""
    st.header("Trust & Confidence")
    if not confidence_data:
        st.warning("Confidence data unavailable.")
        return

    level = confidence_data.get("level", "Unknown")
    score = confidence_data.get("score", 0)
    guidance = confidence_data.get("decision_guidance", "Guidance unavailable.")
    icon_map = {"HIGH": "✅", "MEDIUM": "⚠️", "LOW": "⛔️"}
    st.metric(label="Confidence Level", value=level, delta=f"{score}%", delta_color="off")
    st.write(f"**{icon_map.get(level, '⚪️')} {guidance}**")
    with st.expander("Why am I seeing this?"):
        summary = confidence_data.get("explanation_summary")
        details = confidence_data.get("explanation_details", [])
        if summary:
            st.markdown(f"**Summary:** {summary}")
            st.markdown("---")
        if details:
            st.markdown("**Key Drivers:**")
            for bullet in details:
                st.markdown(f"- {bullet}")
        elif not summary:
            st.info("Detailed explanation is currently unavailable.")

def render_scenario_simulator():
    """Renders the 'What-If Scenario Simulator' section."""
    st.header("🔮 What-If Scenario Simulator")
    
    with st.container(border=True):
        st.subheader("Adjust Metrics")
        col1, col2 = st.columns(2)
        with col1:
            sla_delta = st.slider("SLA Breach Improvement (%)", -50, 50, 0, 5, key="sim_sla")
        with col2:
            rt_delta = st.slider("Response Time Improvement (%)", -50, 50, 0, 5, key="sim_rt")

        if st.button("Run Simulation", use_container_width=True, type="primary"):
            payload = {
                "overrides": {
                    "duplicate_rate": sla_delta / 100,
                    "avg_response_time": rt_delta / 100
                }
            }
            with st.spinner("Calculating impact..."):
                st.session_state.simulation_result = api_request("post", "analytics/simulate", json=payload)

    with st.container():
        if not st.session_state.simulation_result:
            st.info("Run simulation to see results.")
        else:
            res = st.session_state.simulation_result
            st.subheader("Simulation Impact")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("##### Baseline")
                st.metric(label=f"Risk Score ({res['baseline']['decision']})", value=res['baseline']['risk_score'])
            with col2:
                st.markdown("##### Simulated")
                st.metric(label=f"Risk Score ({res['simulated']['decision']})", value=res['simulated']['risk_score'], delta=res['impact']['risk_delta'], delta_color="inverse")
            if res['impact']['decision_changed']:
                st.success(f"✅ Decision level improved from **{res['baseline']['decision']}** to **{res['simulated']['decision']}**.")
            else:
                st.info("No change in overall decision level.")

def render_navigation():
    PAGES = {"Dashboard": "📊", "Governance & Audit": "⚖️", "Ingestion": "📥"}
    visible_pages = list(PAGES.keys())
    if st.session_state.user_role != "founder":
        if "Governance & Audit" in visible_pages: visible_pages.remove("Governance & Audit")
    if st.session_state.user_role != "ops_crm":
        if "Ingestion" in visible_pages: visible_pages.remove("Ingestion")
    for page in visible_pages:
        if st.sidebar.button(f"{PAGES[page]} {page}", use_container_width=True):
            st.session_state.active_page = page
            st.rerun()

def setup_sidebar():
    st.sidebar.title("ProSi-mini")
    if DEV_MODE_BYPASS_AUTH:
        st.sidebar.warning("Auth Bypassed (DEV)")
        st.sidebar.info(f"Role: **{st.session_state.user_role.replace('_', ' ').title()}**")
        st.sidebar.markdown("---")
        render_navigation()

def main():
    init_dashboard_state()
    setup_sidebar()

    if not st.session_state.is_authenticated:
        st.info("Please log in to continue.")
        st.stop()

    if not st.session_state.dashboard_loaded:
        with st.spinner("Loading dashboard..."):
            load_dashboard_data()
        st.rerun()

    if st.session_state.last_error:
        st.error(f"An error occurred: {st.session_state.last_error}")
        st.stop()

    if st.session_state.active_page == "Dashboard":
        st.title("📊 Main Dashboard")
        render_recommendations(st.session_state.recommendations_data)
        st.markdown("---")
        render_trust_confidence(st.session_state.confidence_data)
        st.markdown("---")
        render_scenario_simulator()
    elif st.session_state.active_page == "Governance & Audit":
        st.title("⚖️ Governance & Audit")
    elif st.session_state.active_page == "Ingestion":
        st.title("📥 Data Ingestion")

if __name__ == "__main__":
    main()
