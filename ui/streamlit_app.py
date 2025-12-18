import streamlit as st
import requests
import logging

API_BASE_URL = "http://127.0.0.1:8000/api/v1"
logging.basicConfig(level=logging.INFO)

DEV_MODE_BYPASS_AUTH = True

st.set_page_config(page_title="Property Sales Intelligence", page_icon="🏠", layout="wide")

def initialize_session_state():
    defaults = {
        "is_authenticated": False,
        "access_token": None,
        "user_role": "founder",
        "persona": "Founder / Executive",
        "active_page": "Dashboard",
        "debug_mode": False,
        "simulation_result": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
            
    if DEV_MODE_BYPASS_AUTH:
        st.session_state.is_authenticated = True
        st.session_state.access_token = "dev-token-do-not-use-in-prod"
        st.session_state.user_role = "founder" 

def api_request(method, endpoint, **kwargs):
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
        st.error(f"API Error: {e}")
        return None

def display_scenario_simulator():
    st.header("🔮 What-If Scenario Simulator")
    
    with st.container(border=True):
        st.subheader("Adjust Metrics")
        
        col1, col2 = st.columns(2)
        with col1:
            sla_improvement = st.slider(
                "SLA Breach Improvement (%)", 
                min_value=-50, max_value=50, value=0, step=5,
                help="Positive values mean fewer breaches."
            )
        with col2:
            response_time_improvement = st.slider(
                "Response Time Improvement (%)", 
                min_value=-50, max_value=50, value=0, step=5,
                help="Positive values mean faster response times."
            )

        if st.button("Run Simulation", use_container_width=True, type="primary"):
            with st.spinner("Calculating impact..."):
                payload = {
                    "overrides": {
                        # Note: These keys must match the keys in analytics_service.py
                        "duplicate_rate": sla_improvement / 100, # Assuming breach rate is linked to duplicates for this dummy model
                        "avg_response_time": response_time_improvement / 100
                    }
                }
                st.session_state.simulation_result = api_request("post", "analytics/simulate", json=payload)

    if st.session_state.simulation_result:
        res = st.session_state.simulation_result
        st.subheader("Simulation Impact")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### Baseline")
            st.metric(
                label=f"Risk Score ({res['baseline']['decision']})",
                value=res['baseline']['risk_score'],
            )
        with col2:
            st.markdown("##### Simulated")
            st.metric(
                label=f"Risk Score ({res['simulated']['decision']})",
                value=res['simulated']['risk_score'],
                delta=res['impact']['risk_delta'],
                delta_color="inverse"
            )
        
        if res['impact']['decision_changed']:
            st.success(f"✅ Decision level improved from **{res['baseline']['decision']}** to **{res['simulated']['decision']}**.")
        else:
            st.info("No change in overall decision level.")

def display_recommendations():
    # ... (existing function remains the same)
    pass

def display_trust_confidence():
    # ... (existing function remains the same)
    pass

def render_navigation():
    # ... (existing function remains the same)
    pass

def setup_sidebar():
    # ... (existing function remains the same)
    pass

def main():
    initialize_session_state()
    setup_sidebar()
    if st.session_state.is_authenticated:
        if st.session_state.active_page == "Dashboard":
            st.title("📊 Main Dashboard")
            display_recommendations()
            st.markdown("---")
            display_scenario_simulator()
            st.markdown("---")
            display_trust_confidence()
        elif st.session_state.active_page == "Governance & Audit":
            st.title("⚖️ Governance & Audit")
        elif st.session_state.active_page == "Ingestion":
            st.title("📥 Data Ingestion")
    else:
        st.info("Please log in to continue.")

if __name__ == "__main__":
    main()
