import ee
import os
import tempfile

def initialize_gee():
    ee_json = os.environ["EE_KEY_JSON"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
        f.write(ee_json.encode("utf-8"))
        key_path = f.name

    credentials = ee.ServiceAccountCredentials(
        None,  # email auto-read from json
        key_path
    )
    ee.Initialize(credentials)
