import streamlit as st
import requests
from datetime import datetime, timezone
import logging

# --- Configuration & Initialization ---
API_BASE_URL = "http://127.0.0.1:8000/api/v1"
logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="Property Sales Intelligence", page_icon="🏠", layout="wide")

def map_persona_to_role(persona: str) -> str:
    """Maps the selected persona to a user role string."""
    return {
        "Founder / Executive": "founder",
        "Sales Manager": "sales_manager",
        "Operations / CRM Manager": "ops_crm",
    }.get(persona, "founder") # Default to founder

def initialize_session_state():
    """Initializes session state with defaults and derives the user role."""
    defaults = {
        "persona": "Founder / Executive",
        "active_page": "Dashboard",
        "last_ingestion_summary": None,
        "debug_mode": False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Derive and store the user role
    st.session_state.user_role = map_persona_to_role(st.session_state.persona)

# --- Role-Aware API Calls ---
def api_request(method, endpoint, **kwargs):
    """A centralized function for making role-aware API requests."""
    headers = {
        "X-User-Role": st.session_state.get("user_role", "founder")
    }
    url = f"{API_BASE_URL}/{endpoint}"
    try:
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            st.error(f"🚫 Access Denied: You don't have permission for this action.")
        else:
            st.error(f"API Error: {e.response.status_code} - {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed for {endpoint}: {e}")
        st.error(f"Failed to connect to the API. Please ensure the backend is running.")
        return None

@st.cache_data(ttl=30)
def fetch_alerts():
    """Fetches active alerts using the centralized API request function."""
    return api_request("get", "alerts/")

# --- UI Components ---
def display_alert_center():
    """Renders the Alert Center in the sidebar, now with RBAC."""
    # The alerts endpoint is hidden for Sales Manager at the API level.
    # The api_request function will handle the 403 error gracefully.
    if st.session_state.user_role == "sales_manager":
        st.sidebar.header("🚨 Alert Center")
        st.sidebar.info("Alerts are not available for this role.")
        return

    st.sidebar.header("🚨 Alert Center")
    alerts_data = fetch_alerts()
    
    if alerts_data is None:
        # Error is already shown by api_request, but we can add a retry button.
        if st.sidebar.button("Retry Alerts", key="retry_alerts"):
            st.cache_data.clear()
            st.rerun()
        return

    active_alerts = alerts_data.get("active_alerts", [])
    
    # Summary Badge
    if not active_alerts:
        st.sidebar.success("✅ No active alerts.")
        return
        
    high_count = sum(1 for a in active_alerts if a["severity"] == "high")
    medium_count = sum(1 for a in active_alerts if a["severity"] == "medium")
    
    summary_parts = []
    if high_count > 0: summary_parts.append(f"🔥 {high_count} Critical")
    if medium_count > 0: summary_parts.append(f"⚠️ {medium_count} Warning(s)")
    st.sidebar.error(" | ".join(summary_parts))

    # Alert List
    with st.sidebar.expander("View Active Alerts", expanded=True):
        # ... (rest of the alert display logic remains the same)
        pass

def setup_sidebar():
    """Sets up the main sidebar with role-aware navigation."""
    # Persona Selector
    st.sidebar.title("ProSi-mini")
    persona = st.sidebar.selectbox(
        "Select Your Persona",
        ["Founder / Executive", "Sales Manager", "Operations / CRM Manager"],
        key="persona"
    )
    
    # Update role if persona changes
    if st.session_state.user_role != map_persona_to_role(persona):
        st.session_state.user_role = map_persona_to_role(persona)
        st.cache_data.clear() # Clear cache on role change
        st.rerun()

    # Debug Mode
    st.sidebar.toggle("Debug Mode", key="debug_mode")
    if st.session_state.debug_mode:
        st.sidebar.info(f"Active Role: `{st.session_state.user_role}`")

    st.sidebar.markdown("---")

    # Role-based Navigation
    PAGES = {
        "Dashboard": "📊",
        "Governance & Audit": "⚖️",
        "Ingestion": "📥",
    }

    # Filter pages based on role
    visible_pages = list(PAGES.keys())
    if st.session_state.user_role != "founder":
        visible_pages.remove("Governance & Audit")
    if st.session_state.user_role != "ops_crm":
        if "Ingestion" in visible_pages:
             visible_pages.remove("Ingestion")

    for page, icon in PAGES.items():
        if page in visible_pages:
            if st.sidebar.button(f"{icon} {page}", use_container_width=True):
                st.session_state.active_page = page
                st.rerun()
    
    st.sidebar.markdown("---")
    display_alert_center()
    st.sidebar.markdown("---")
    # ... (rest of sidebar)

def render_ingestion_page():
    """Renders the ingestion page, now with RBAC on the trigger button."""
    st.title("📥 Data Ingestion")
    
    st.write("Manage and monitor data sources.")
    
    # The button to run ingestion is only visible to ops_crm
    if st.session_state.user_role == "ops_crm":
        if st.button("Run All Ingestion Jobs"):
            with st.spinner("Ingestion in progress..."):
                result = api_request("post", "ingestion/run")
                if result:
                    st.success("Ingestion completed successfully!")
                    st.json(result.get("summary", {}))
                    st.session_state.last_ingestion_summary = result.get("summary")
    else:
        st.info("You do not have permission to trigger ingestion jobs.")

    # ... (rest of ingestion page)

# --- Main Application ---
def main():
    initialize_session_state()
    setup_sidebar()
    
    # Page Router
    if st.session_state.active_page == "Dashboard":
        st.title("📊 Main Dashboard")
        # ... dashboard content
    elif st.session_state.active_page == "Governance & Audit":
        # This page is already protected by the sidebar logic
        st.title("⚖️ Governance & Audit")
        # ... governance content
    elif st.session_state.active_page == "Ingestion":
        render_ingestion_page()

if __name__ == "__main__":
    main()
