def calculate_ndvi(image):
    return image.normalizedDifference(["SR_B5", "SR_B4"]).rename("NDVI")

def calculate_ndbi(image):
    return image.normalizedDifference(["SR_B6", "SR_B5"]).rename("NDBI")
