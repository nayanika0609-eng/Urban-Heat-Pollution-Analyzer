# ==================================================
# IMPORTS
# ==================================================
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

# ==================================================
# STREAMLIT PAGE CONFIG (MUST BE FIRST)
# ==================================================
st.set_page_config(
    page_title="Urban Heat & Pollution Analyzer",
    layout="wide"
)

# ==================================================
# STYLING
# ==================================================
plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 9

# ==================================================
# APP HEADER
# ==================================================
st.title("🌆 Urban Heat & Pollution Analyzer")
st.markdown(
    """
    A decision-support dashboard combining **satellite-derived urban heat**
    with **real-time ground air quality data** to support
    public health and government planning.
    """
)

# ==================================================
# INITIALIZE GOOGLE EARTH ENGINE
# ==================================================
initialize_gee()

# ==================================================
# CITY SELECTION
# ==================================================
st.sidebar.header("🌍 Select City")

city = st.sidebar.selectbox("City", ["Pune", "Mumbai", "Delhi"])

city_coords = {
    "Pune": [73.8567, 18.5204],
    "Mumbai": [72.8777, 19.0760],
    "Delhi": [77.1025, 28.7041],
}

lon, lat = city_coords[city]
roi = ee.Geometry.Point([lon, lat]).buffer(15000)

# ==================================================
# REAL-TIME AQI
# ==================================================
st.subheader("🌫️ Real-Time Air Quality Index (AQI)")

aqi_df = fetch_city_aqi(city)

if aqi_df is None or aqi_df.empty:
    st.error("AQI data unavailable.")
    use_ground_aqi = False
    avg_pm25 = None
else:
    use_ground_aqi = True
    avg_aqi = aqi_df["aqi"].iloc[0]
    avg_pm25 = aqi_df["pm25"].iloc[0]

    col1, col2 = st.columns(2)
    col1.metric("AQI", avg_aqi)
    col2.metric("PM2.5 (µg/m³)", avg_pm25)
# ==================================================
# AQI CATEGORY LABEL
# ==================================================
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

if use_ground_aqi:
    aqi_status = aqi_category(avg_aqi)
    st.success(f"Air Quality Status: **{aqi_status}**")

# ==================================================
# COOLING INTERVENTIONS
# ==================================================
st.sidebar.header("🌱 Cooling Interventions")

green_cover = st.sidebar.slider("Increase green cover (%)", 0, 50, 20)
cool_roof = st.sidebar.checkbox("Cool roofs")
green_roof = st.sidebar.checkbox("Green roofs")
water_bodies = st.sidebar.checkbox("Restore water bodies")
cool_pavement = st.sidebar.checkbox("Cool pavements")

# ==================================================
# POLICY BUDGET
# ==================================================
st.sidebar.header("💰 Policy Budget")
budget = st.sidebar.slider("Available budget (₹ crore)", 1, 10, 5)

actions = {
    "green_cover_10": green_cover >= 10,
    "cool_roof": cool_roof,
    "green_roof": green_roof,
    "water_bodies": water_bodies,
    "cool_pavement": cool_pavement,
}

# ==================================================
# FETCH SATELLITE DATA
# ==================================================
with st.spinner("🔄 Fetching satellite data..."):
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

# ==================================================
# GRID ANALYSIS
# ==================================================
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

# ==================================================
# HEAT RISK
# ==================================================
df["temp_norm"] = (df["ST_B10"] - df["ST_B10"].min()) / (df["ST_B10"].max() - df["ST_B10"].min())
df["ndvi_norm"] = 1 - df["NDVI"]
df["ndbi_norm"] = df["NDBI"]

df["heat_risk"] = 0.5 * df["temp_norm"] + 0.3 * df["ndbi_norm"] + 0.2 * df["ndvi_norm"]

df["risk_level"] = df["heat_risk"].apply(
    lambda x: "High" if x > 0.7 else "Moderate" if x > 0.4 else "Low"
)

# ==================================================
# HEALTH RISK (HEAT + REAL AQI)
# ==================================================
if use_ground_aqi and avg_pm25 is not None:
    pm_norm = min(avg_pm25 / 250, 1)
else:
    pm_norm = 0

df["health_risk"] = 0.6 * df["heat_risk"] + 0.4 * pm_norm

df["health_risk_level"] = df["health_risk"].apply(
    lambda x: "Severe" if x > 0.75 else
              "High" if x > 0.55 else
              "Moderate" if x > 0.35 else
              "Low"
)
# ==================================================
# POLLUTION LEVEL CLASSIFICATION (PM2.5)
# ==================================================
def pm25_to_level(pm):
    if pm <= 30:
        return "Low"
    elif pm <= 60:
        return "Moderate"
    else:
        return "High"

if use_ground_aqi and avg_pm25 is not None:
    df["pollution_level"] = pm25_to_level(avg_pm25)
else:
    df["pollution_level"] = "Unknown"

# ==================================================
# HEALTH RISK HOTSPOTS MAP
# ==================================================
st.subheader("🗺️ Health Risk Hotspots (Heat + Air Pollution)")

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

# ==================================================
# URBAN HEAT HOTSPOTS HEATMAP
# ==================================================
st.subheader("🔥 Urban Heat Hotspots")
heatmap = create_heatmap(df)
components.html(heatmap._repr_html_(), height=600)
# ==================================================
# 🌫️ POLLUTION LEVEL DISTRIBUTION
# ==================================================
st.subheader("🌫️ Pollution Level Distribution (PM2.5)")

pollution_counts = df["pollution_level"].value_counts().reindex(
    ["Low", "Moderate", "High"], fill_value=0
)

fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(
    pollution_counts.index,
    pollution_counts.values,
    color=["#2ecc71", "#f1c40f", "#e74c3c"],
    edgecolor="black"
)

ax.set_ylabel("Number of Locations")
ax.set_xlabel("Pollution Level")
ax.set_title("Ground-Level Air Pollution (PM2.5)")
ax.grid(axis="y", linestyle="--", alpha=0.4)

st.pyplot(fig)

st.caption(
    "🟢 Low (≤30 µg/m³)   🟡 Moderate (31–60 µg/m³)   🔴 High (>60 µg/m³)"
)

# ==================================================
# COMBINED HEAT–POLLUTION VULNERABILITY MAP
# ==================================================
st.subheader("🧭 Combined Heat–Pollution Vulnerability")

vul_map = folium.Map(location=[lat, lon], zoom_start=11)

for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=6,
        color="purple" if row["health_risk"] > 0.6 else "blue",
        fill=True,
        fill_opacity=0.6,
        popup=f"""
        Heat Risk: {row['risk_level']}<br>
        Health Risk: {row['health_risk_level']}
        """
    ).add_to(vul_map)

components.html(vul_map._repr_html_(), height=500)
st.markdown("### 🗺️ Map Interpretation")

st.info(
    """
    **🟣 Purple areas** indicate **high combined heat–pollution vulnerability**, 
    where elevated land surface temperature coincides with poor air quality (PM2.5).

    **🔵 Blue areas** represent **lower vulnerability zones**, with relatively lower
    heat stress and/or better air quality.

    These maps help identify **priority regions for targeted cooling and pollution mitigation measures**.
    """
)

# ==================================================
# COOLING SIMULATION + SDG IMPACT
# ==================================================
df["temp_after"] = simulate_temperature(
    df,
    green_cover,
    cool_roof,
    green_roof,
    water_bodies,
    cool_pavement
)

df["temp_change"] = df["ST_B10"] - df["temp_after"]
df["sdg_impact"] = df["temp_change"].apply(sdg_mapping)

# ==================================================
# BUDGET VS COOLING IMPACT
# ==================================================
used_budget, estimated_cooling, selected_actions = estimate_budget_impact(
    budget, actions
)

st.subheader("💰 Budget vs Cooling Impact")
st.info(
    f"""
    Budget: ₹{budget} crore  
    Utilized: ₹{used_budget:.1f} crore  
    Expected cooling: ~{estimated_cooling:.1f} °C
    """
)

# ==================================================
# HEAT & POLLUTION ACTION PLAN
# ==================================================
st.subheader("📊 Heat & Pollution Action Plan")

st.markdown(
    f"""
    **City:** {city}  
    **Average Surface Temperature:** {df['ST_B10'].mean():.1f} °C  
    **High Heat Risk Areas:** {(df['risk_level'] == 'High').mean() * 100:.1f}%  
    **Average PM2.5:** {avg_pm25 if avg_pm25 else 'N/A'} µg/m³
    """
)

st.markdown("### 🌱 Impact of Selected Mitigation Measures")

st.write(
    f"""
    The selected interventions are expected to reduce
    average surface temperature by **~{estimated_cooling:.1f} °C**,
    primarily benefiting high-risk urban zones and improving
    public health outcomes.
    """
)


st.markdown("### 🏛️ Policy Recommendations")
st.write(
    """
    - Expand urban green cover in high-risk wards  
    - Implement cool roofs on public and low-income housing  
    - Restore urban water bodies  
    - Integrate heat mitigation with air quality planning
    """
)

# ==================================================
# PDF EXPORT
# ==================================================
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

# ==================================================
# CSV DOWNLOAD
# ==================================================
st.download_button(
    "📥 Download policy-ready dataset (CSV)",
    df.to_csv(index=False),
    "urban_heat_policy_report.csv",
    "text/csv",
)
