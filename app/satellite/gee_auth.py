import json
import ee
import streamlit as st
import tempfile

def initialize_gee():
    st.write("🔄 Initializing Google Earth Engine...")

    if "EE_KEY_JSON" not in st.secrets:
        st.error("❌ EE_KEY_JSON not found in Streamlit secrets")
        st.stop()

    # Write secret JSON to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write(st.secrets["EE_KEY_JSON"])
        key_path = f.name

    try:
        credentials = ee.ServiceAccountCredentials(
            email=None,
            key_file=key_path
        )
        ee.Initialize(credentials)
        st.success("✅ Google Earth Engine initialized")
    except Exception as e:
        st.error("❌ Earth Engine init failed")
        st.exception(e)
        st.stop()
