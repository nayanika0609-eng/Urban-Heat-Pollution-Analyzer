import ee
import streamlit as st
import tempfile

def initialize_gee():
    st.write("🔄 Initializing Google Earth Engine...")

    # Get raw key text from Streamlit secrets
    key_text = st.secrets["EE_KEY_JSON"]

    # Write key to a temporary file
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as f:
        f.write(key_text)
        key_path = f.name

    # Initialize EE using key file (no JSON parsing)
    credentials = ee.ServiceAccountCredentials(
        None,
        key_path
    )

    ee.Initialize(credentials)

    st.success("✅ Google Earth Engine initialized")
