import ee
import json
import streamlit as st

def initialize_gee():
    try:
        # Streamlit Cloud safe access
        ee_json = st.secrets["EE_KEY_JSON"]
        key_dict = json.loads(ee_json)

        credentials = ee.ServiceAccountCredentials(
            key_dict["client_email"],
            key_dict
        )

        ee.Initialize(credentials)

    except KeyError:
        raise RuntimeError(
            "EE_KEY_JSON not found in Streamlit Secrets. "
            "Please add it under App → Settings → Secrets."
        )

    except Exception as e:
        raise RuntimeError(f"Earth Engine init failed: {e}")
