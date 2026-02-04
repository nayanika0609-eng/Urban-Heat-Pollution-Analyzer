import ee

def initialize_gee():
    project_id = "uhi-analyzer".strip()
    ee.Initialize(project=project_id)
