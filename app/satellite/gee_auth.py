import ee
import os
import json

def initialize_gee():
    key_json = json.loads(os.environ["EE_KEY_JSON"])
    credentials = ee.ServiceAccountCredentials(
        key_json["client_email"],
        key_json
    )
    ee.Initialize(credentials)
