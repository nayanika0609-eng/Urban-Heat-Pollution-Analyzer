from geopy.geocoders import Nominatim
import time

geolocator = Nominatim(user_agent="uhi-analyzer")

def get_area_name(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), zoom=14)
        time.sleep(1)  # important: avoid rate limit
        if location and location.raw:
            address = location.raw.get("address", {})
            return (
                address.get("suburb")
                or address.get("neighbourhood")
                or address.get("city_district")
                or address.get("city")
            )
    except:
        return None
