import ee
from datetime import datetime, timedelta


# --------------------------------------------------
# FETCH NEAR-REAL-TIME LANDSAT IMAGE
# --------------------------------------------------
def fetch_landsat(roi, start_date=None, end_date=None):
    """
    Fetch the most recent Landsat 8 surface reflectance image
    (near-real-time, last 30 days).
    """

    # Use Python datetime (Earth Engine does NOT support ee.Date.now())
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)

    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    collection = (
        ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
        .filterBounds(roi)
        .filterDate(start_str, end_str)
        .filter(ee.Filter.lt("CLOUD_COVER", 30))
        .sort("system:time_start", False)
    )

    image = collection.first()
    return image


# --------------------------------------------------
# CALCULATE LAND SURFACE TEMPERATURE (LST)
# --------------------------------------------------
def calculate_lst(image):
    """
    Calculate Land Surface Temperature (°C)
    using Landsat 8 thermal band.
    """

    # Thermal band (Kelvin)
    thermal = image.select("ST_B10")

    # Convert Kelvin to Celsius
    lst_celsius = thermal.multiply(0.00341802).add(149.0).subtract(273.15)

    return lst_celsius.rename("ST_B10")


# --------------------------------------------------
# FETCH NEAR-REAL-TIME AIR POLLUTION (NO2)
# --------------------------------------------------
def fetch_pollution(roi):
    """
    Fetch near-real-time NO2 concentration
    from Sentinel-5P (last 14 days average).
    """

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=14)

    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    no2 = (
        ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_NO2")
        .filterBounds(roi)
        .filterDate(start_str, end_str)
        .select("NO2_column_number_density")
        .mean()
        .rename("NO2")
    )

    return no2
