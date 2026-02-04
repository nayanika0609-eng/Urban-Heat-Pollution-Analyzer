import requests
import pandas as pd


AQICN_TOKEN = "bf7a2a4705829975685ffd7847fa1ed86548e272"


def fetch_city_aqi(city):
    """
    Fetch real-time AQI & PM2.5 using AQICN (waqi.info)
    """

    url = f"https://api.waqi.info/feed/{city}/"
    params = {"token": AQICN_TOKEN}

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return None

    if data.get("status") != "ok":
        return None

    d = data["data"]

    aqi = d.get("aqi")
    iaqi = d.get("iaqi", {})
    pm25 = iaqi.get("pm25", {}).get("v")

    city_info = d.get("city", {})
    geo = city_info.get("geo", [])

    if not aqi or not pm25 or len(geo) != 2:
        return None

    return pd.DataFrame([{
        "city": city,
        "latitude": geo[0],
        "longitude": geo[1],
        "aqi": aqi,
        "pm25": pm25
    }])
