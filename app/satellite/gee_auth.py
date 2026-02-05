import ee
import os
import json
import tempfile

def initialize_gee():
    # Write secret JSON to a temp file (safest method)
    ee_json = os.environ["EE_KEY_JSON"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
        f.write(ee_json.encode("utf-8"))
        key_path = f.name

    credentials = ee.ServiceAccountCredentials(
        json.loads(ee_json)["client_email"],
        key_path
    )
    ee.Initialize(credentials)
