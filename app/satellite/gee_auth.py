import ee

def initialize_gee():
    try:
        ee.Initialize()
    except Exception:
        ee.Authenticate()
        ee.Initialize()
