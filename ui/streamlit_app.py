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

def initialize_session_state():
    """Initializes session state for authentication and navigation."""
    defaults = {
        "is_authenticated": False,
        "access_token": None,
        "user_role": "founder",
        "persona": "Founder / Executive",
        "active_page": "Dashboard",
        "debug_mode": False,
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
    except requests.exceptions.RequestException:
        st.error("Failed to connect to the API.")
        return None

def display_trust_confidence():
    """
    Fetches and displays the Trust & Confidence score, with an
    expandable explanation and guidance section.
    """
    st.header("Trust & Confidence")
    confidence_data = api_request("get", "analytics/confidence")

    if confidence_data is None:
        st.warning("Could not retrieve confidence score.")
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
    initialize_session_state()
    setup_sidebar()

    if st.session_state.is_authenticated:
        if st.session_state.active_page == "Dashboard":
            st.title("📊 Main Dashboard")
            display_trust_confidence()
        elif st.session_state.active_page == "Governance & Audit":
            st.title("⚖️ Governance & Audit")
        elif st.session_state.active_page == "Ingestion":
            st.title("📥 Data Ingestion")
    else:
        st.info("Please log in to continue.")

if __name__ == "__main__":
    main()
