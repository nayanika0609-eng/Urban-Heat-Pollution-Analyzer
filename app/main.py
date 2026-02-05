import streamlit as st
import streamlit.components.v1 as components
import ee
import geemap.foliumap as geemap
import pandas as pd
import folium
import matplotlib.pyplot as plt

from satellite.gee_auth import initialize_gee
from satellite.fetch_data import fetch_landsat, calculate_lst, fetch_pollution
from satellite.fetch_aqi import fetch_city_aqi
from processing.indices import calculate_ndvi, calculate_ndbi
from simulation.mitigation import simulate_temperature
from simulation.budget_impact import estimate_budget_impact
from visualization.heatmap import create_heatmap
from sdg.impact import sdg_mapping
from reporting.heat_action_plan import generate_heat_pollution_action_plan
plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 9
plt.rcParams["axes.titlesize"] = 10
plt.rcParams["axes.labelsize"] = 11


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Urban Heat & Pollution Analyzer", layout="wide")

st.title("🌆 Urban Heat & Pollution Analyzer")
st.markdown(
    """
    A decision-support dashboard combining satellite-derived urban heat with near real-time ground air quality data to support public health & government planning.
    """
)

# --------------------------------------------------
# INITIALIZE GOOGLE EARTH ENGINE
# --------------------------------------------------
initialize_gee()

# --------------------------------------------------
# CITY SELECTION
# --------------------------------------------------
st.sidebar.header("🌍 Select City")

city = st.sidebar.selectbox("City", ["Pune", "Mumbai", "Delhi"])

city_coords = {
    "Pune": [73.8567, 18.5204],
    "Mumbai": [72.8777, 19.0760],
    "Delhi": [77.1025, 28.7041],
}

lon, lat = city_coords[city]
roi = ee.Geometry.Point([lon, lat]).buffer(15000)

# --------------------------------------------------
# REAL-TIME AQI (CPCB)
# --------------------------------------------------
st.subheader("🌫️ Real-Time Air Quality Index (AQI)")

aqi_df = fetch_city_aqi(city)
if aqi_df is not None and not aqi_df.empty:
    # Convert PM2.5 to pollution level
    def pm25_to_level(pm):
        if pm <= 30:
            return "Low"
        elif pm <= 60:
            return "Moderate"
        else:
            return "High"

    aqi_df["AQI_Level"] = aqi_df["pm25"].apply(pm25_to_level)


if aqi_df is None or aqi_df.empty:
    st.error("AQI data unavailable from external sources.")
    use_ground_aqi = False
    avg_pm25 = None
else:
    use_ground_aqi = True
    avg_aqi = aqi_df["aqi"].iloc[0]
    avg_pm25 = aqi_df["pm25"].iloc[0]

    col1, col2 = st.columns(2)
    col1.metric("AQI", avg_aqi)
    col2.metric("PM2.5 (µg/m³)", avg_pm25)

    def aqi_category(aqi):
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Moderate"
        elif aqi <= 200:
            return "Poor"
        elif aqi <= 300:
            return "Very Poor"
        else:
            return "Severe"

    st.success(f"Air Quality Category: **{aqi_category(avg_aqi)}**")


aqi_counts = aqi_df["AQI_Level"].value_counts().reindex(
    ["Low", "Moderate", "High"],
    fill_value=0
)
fig, ax = plt.subplots(figsize=(6, 4), facecolor="#f9fafb")
ax.set_facecolor("#f9fafb")

ax.bar(
    aqi_counts.index,
    aqi_counts.values,
    color=["#2ecc71", "#f1c40f", "#e74c3c"],  # Low, Moderate, High
    edgecolor="black",
    linewidth=0.6
)

ax.set_title(
    "Ground-Level Air Pollution (PM2.5)",
    fontsize=14,
    fontweight="bold",
    pad=10
)
ax.set_ylabel("Number of Monitoring Stations", fontsize=11)
ax.set_xlabel("Pollution Level", fontsize=11)

ax.grid(axis="y", linestyle="--", alpha=0.4)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

st.pyplot(fig)
st.caption(
    "🟢 Low (≤30 µg/m³)   🟡 Moderate (31–60 µg/m³)   🔴 High (>60 µg/m³)"
)

# --------------------------------------------------
# COOLING INTERVENTIONS
# --------------------------------------------------
st.sidebar.header("🌱 Cooling Interventions")

green_cover = st.sidebar.slider("Increase green cover (%)", 0, 50, 20)
cool_roof = st.sidebar.checkbox("Cool / reflective roofs")
green_roof = st.sidebar.checkbox("Green roofs on public buildings")
water_bodies = st.sidebar.checkbox("Restore water bodies")
cool_pavement = st.sidebar.checkbox("Cool pavements & shaded roads")

# --------------------------------------------------
# POLICY BUDGET
# --------------------------------------------------
st.sidebar.header("💰 Policy Budget")
budget = st.sidebar.slider("Available budget (₹ crore)", 1, 10, 5)

actions = {
    "green_cover_10": green_cover >= 10,
    "cool_roof": cool_roof,
    "green_roof": green_roof,
    "water_bodies": water_bodies,
    "cool_pavement": cool_pavement,
}

# --------------------------------------------------
# FETCH SATELLITE DATA
# --------------------------------------------------
with st.spinner("🔄 Fetching near-real-time satellite data..."):
    image = fetch_landsat(roi)

if image is None:
    st.error("Satellite data could not be loaded.")
    st.stop()

lst = calculate_lst(image).rename("ST_B10")
ndvi = calculate_ndvi(image)
ndbi = calculate_ndbi(image)
pollution = fetch_pollution(roi)

final_image = lst.addBands([ndvi, ndbi])
if pollution is not None:
    final_image = final_image.addBands(pollution)

# --------------------------------------------------
# GRID ANALYSIS
# --------------------------------------------------
grid = geemap.create_grid(roi, scale=500)

def add_lat_lon(feature):
    centroid = feature.geometry().centroid(100)
    coords = centroid.coordinates()
    return feature.set({
        "longitude": coords.get(0),
        "latitude": coords.get(1)
    })

stats = (
    final_image
    .reduceRegions(grid, ee.Reducer.mean(), 500)
    .map(add_lat_lon)
)

df = geemap.ee_to_df(stats).dropna()

# --------------------------------------------------
# HEAT RISK
# --------------------------------------------------
df["temp_norm"] = (df["ST_B10"] - df["ST_B10"].min()) / (df["ST_B10"].max() - df["ST_B10"].min())
df["ndvi_norm"] = 1 - df["NDVI"]
df["ndbi_norm"] = df["NDBI"]

df["heat_risk"] = 0.5 * df["temp_norm"] + 0.3 * df["ndbi_norm"] + 0.2 * df["ndvi_norm"]

df["risk_level"] = df["heat_risk"].apply(
    lambda x: "High" if x > 0.7 else "Moderate" if x > 0.4 else "Low"
)

# --------------------------------------------------
# HEALTH RISK (HEAT + AQI)
# --------------------------------------------------
if use_ground_aqi and avg_pm25 is not None:
    pm_norm = min(avg_pm25 / 250, 1)
else:
    pm_norm = 0

df["health_risk"] = 0.6 * df["temp_norm"] + 0.4 * pm_norm

df["health_risk_level"] = df["health_risk"].apply(
    lambda x: "Severe" if x > 0.75 else
              "High" if x > 0.55 else
              "Moderate" if x > 0.35 else
              "Low"
)

# --------------------------------------------------
# HEALTH RISK DISTRIBUTION
# --------------------------------------------------
st.subheader("🏥 Public Health Risk Distribution")

health_counts = df["health_risk_level"].value_counts().reindex(
    ["Low", "Moderate", "High", "Severe"], fill_value=0
)

fig, ax = plt.subplots(facecolor="#f9fafb")
ax.bar(
    health_counts.index,
    health_counts.values,
    color=["#2ecc71", "#f1c40f", "#e74c3c", "#8e0000"]
)
ax.set_ylabel("Number of Locations")
ax.set_title("Health Risk Levels Across City")
ax.grid(axis="y", linestyle="--", alpha=0.4)
st.pyplot(fig)
# --------------------------------------------------
# HEALTH RISK SCATTER MAP
# --------------------------------------------------
st.subheader("🗺️ Health Risk Hotspots (Heat + Pollution)")

health_map = folium.Map(location=[lat, lon], zoom_start=11)

color_map = {
    "Low": "green",
    "Moderate": "orange",
    "High": "red",
    "Severe": "darkred"
}

for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=5,
        color=color_map[row["health_risk_level"]],
        fill=True,
        fill_opacity=0.7,
        popup=f"""
        Heat risk: {row['risk_level']}<br>
        Health risk: {row['health_risk_level']}<br>
        Temp: {row['ST_B10']:.1f} °C
        """
    ).add_to(health_map)

components.html(health_map._repr_html_(), height=500)

# --------------------------------------------------
# HEAT MAP
# --------------------------------------------------
st.subheader("🔥 Urban Heat Hotspots")
heatmap = create_heatmap(df)
components.html(heatmap._repr_html_(), height=600)

# --------------------------------------------------
# COOLING SIMULATION
# --------------------------------------------------
df["temp_after"] = simulate_temperature(
    df, green_cover, cool_roof, green_roof, water_bodies, cool_pavement
)

df["temp_change"] = df["ST_B10"] - df["temp_after"]
df["sdg_impact"] = df["temp_change"].apply(sdg_mapping)

# --------------------------------------------------
# BUDGET vs IMPACT
# --------------------------------------------------
used_budget, estimated_cooling, selected_actions = estimate_budget_impact(budget, actions)

st.subheader("💰 Budget vs Cooling Impact")
st.info(
    f"""
    Budget: ₹{budget} crore  
    Utilized: ₹{used_budget:.1f} crore  
    Expected cooling: ~{estimated_cooling:.1f} °C
    """
)

# --------------------------------------------------
# PDF EXPORT
# --------------------------------------------------
if st.button("📄 Generate Heat & Pollution Action Plan (PDF)"):
    pdf_path = generate_heat_pollution_action_plan(
        city,
        df["ST_B10"].mean(),
        (df["risk_level"] == "High").mean() * 100,
        avg_pm25,
        budget,
        estimated_cooling,
        selected_actions
    )

    with open(pdf_path, "rb") as f:
        st.download_button(
            "⬇️ Download Heat & Pollution Action Plan",
            f,
            file_name="Heat_Pollution_Action_Plan.pdf",
            mime="application/pdf"
        )

# --------------------------------------------------
# DOWNLOAD DATA
# --------------------------------------------------
st.download_button(
    "📥 Download policy-ready dataset (CSV)",
    df.to_csv(index=False),
    "urban_heat_policy_report.csv",
    "text/csv",
)


