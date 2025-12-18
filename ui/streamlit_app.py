import streamlit as st
import requests
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
    }.get(persona, "founder")

def initialize_session_state():
    """Initializes session state for authentication and navigation."""
    defaults = {
        "is_authenticated": False,
        "access_token": None,
        "user_role": "founder", # Default role before login
        "persona": "Founder / Executive",
        "active_page": "Dashboard",
        "debug_mode": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# --- API Calls ---
def api_request(method, endpoint, **kwargs):
    """Centralized function for making authenticated API requests."""
    headers = kwargs.pop("headers", {})
    
    # Prioritize JWT, fallback to role header
    if st.session_state.get("access_token"):
        headers["Authorization"] = f"Bearer {st.session_state.access_token}"
    else:
        headers["X-User-Role"] = st.session_state.get("user_role", "founder")

    url = f"{API_BASE_URL}/{endpoint}"
    try:
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        # Handle responses with no content
        return response.json() if response.content else None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            st.error("🚫 Access Denied: Your role does not have permission for this action.")
        elif e.response.status_code == 401:
             st.error("🚫 Authentication failed. Please log out and log back in.")
             handle_logout()
        else:
            st.error(f"API Error: {e.response.status_code} - {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to the API: {e}")
        return None

def handle_login():
    """Attempts to log in using the selected persona."""
    persona = st.session_state.persona
    with st.spinner("Authenticating..."):
        response = api_request(
            "post",
            "auth/login",
            json={"persona": persona}
        )
        if response and "access_token" in response:
            st.session_state.is_authenticated = True
            st.session_state.access_token = response["access_token"]
            st.session_state.user_role = map_persona_to_role(persona)
            st.cache_data.clear()
            st.rerun()
        else:
            st.error("Login failed. Please check the backend and try again.")

def handle_logout():
    """Logs the user out and resets the session."""
    st.session_state.is_authenticated = False
    st.session_state.access_token = None
    st.session_state.user_role = "founder" # Reset to default
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()

# --- UI Components ---
def setup_sidebar():
    """Sets up the sidebar for either login or navigation."""
    st.sidebar.title("ProSi-mini")

    if not st.session_state.is_authenticated:
        st.sidebar.header("Login")
        st.sidebar.selectbox(
            "Select Your Persona",
            ["Founder / Executive", "Sales Manager", "Operations / CRM Manager"],
            key="persona"
        )
        st.sidebar.button("Login", on_click=handle_login, use_container_width=True)
    else:
        st.sidebar.success(f"Logged in as: **{st.session_state.user_role.replace('_', ' ').title()}**")
        st.sidebar.button("Logout", on_click=handle_logout, use_container_width=True)
        
        st.sidebar.markdown("---")
        render_navigation()
        
        st.sidebar.markdown("---")
        # display_alert_center() # This can be added back if needed

def render_navigation():
    """Renders the main navigation buttons based on user role."""
    PAGES = {
        "Dashboard": "📊",
        "Governance & Audit": "⚖️",
        "Ingestion": "📥",
    }
    
    # Filter pages based on role
    visible_pages = list(PAGES.keys())
    if st.session_state.user_role != "founder":
        if "Governance & Audit" in visible_pages: visible_pages.remove("Governance & Audit")
    if st.session_state.user_role != "ops_crm":
        if "Ingestion" in visible_pages: visible_pages.remove("Ingestion")

    for page in visible_pages:
        if st.sidebar.button(f"{PAGES[page]} {page}", use_container_width=True):
            st.session_state.active_page = page
            st.rerun()

# --- Main Application ---
def main():
    initialize_session_state()
    setup_sidebar()

    if st.session_state.is_authenticated:
        # Page Router
        if st.session_state.active_page == "Dashboard":
            st.title("📊 Main Dashboard")
            st.write("Welcome to your personalized dashboard.")
        elif st.session_state.active_page == "Governance & Audit":
            st.title("⚖️ Governance & Audit")
            st.write("This page is for founders only.")
        elif st.session_state.active_page == "Ingestion":
            st.title("📥 Data Ingestion")
            st.write("This page is for Ops/CRM managers only.")
    else:
        st.info("Please log in using the sidebar to continue.")

if __name__ == "__main__":
    main()
