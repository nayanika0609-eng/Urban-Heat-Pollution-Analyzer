import ee
import json
import streamlit as st

def initialize_gee():
    st.write("🔄 Initializing Google Earth Engine...")

    key_dict = json.loads(st.secrets["EE_KEY_JSON"])

    credentials = ee.ServiceAccountCredentials(
        key_dict["client_email"],
        key_dict
    )

    ee.Initialize(
        credentials=credentials,
        project=key_dict["project_id"]
    )

    st.success("✅ Google Earth Engine initialized")
