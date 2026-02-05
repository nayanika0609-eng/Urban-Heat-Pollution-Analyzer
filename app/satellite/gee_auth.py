import ee
import streamlit as st

def initialize_gee():
    st.write("🔄 Initializing Google Earth Engine...")

    credentials = ee.ServiceAccountCredentials(
        st.secrets["gcp_service_account"]
    )

    ee.Initialize(
        credentials=credentials,
        project=st.secrets["gcp_service_account"]["project_id"]
    )

    st.success("✅ Google Earth Engine initialized")
