import streamlit as st

def init_state():
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
