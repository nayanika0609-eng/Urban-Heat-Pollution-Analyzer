# Urban Heat & Pollution Analyzer
Urban Heat & Pollution Analyzer is a web-based decision support system that analyzes urban heat stress and air pollution using satellite data and real-time AQI data. It helps identify high-risk zones in a city and evaluates sustainable cooling strategies for climate-resilient urban planning.

# 🚀 Features
Uses satellite imagery (Google Earth Engine – Landsat) to compute:

Land Surface Temperature (LST)

Vegetation Index (NDVI)

Built-up Index (NDBI)

Integrates real-time air quality data (PM2.5 / AQI).

AI-based risk modeling for:

Heat risk

Health risk (heat + pollution)

# Simulation of cooling strategies:

Green cover

Cool roofs

Green roofs

Water bodies

Cool pavements

# Budget vs cooling impact analysis.

Interactive maps and charts.

Generates policy-ready PDF action plans.

# 🛠️ Technologies Used
Python

Google Earth Engine

Streamlit

Pandas, NumPy

Folium, Matplotlib

ReportLab

AQI APIs (PM2.5)

# 📂 Project Structure
app/
 ├── main.py
 ├── satellite/
 ├── processing/
 ├── simulation/
 ├── visualization/
 ├── reporting/
 └── utils/

▶️ How to Run

Clone the repository

Create and activate a virtual environment

Install dependencies:

pip install -r requirements.txt
Run the app:

streamlit run app/main.py
# 🌱 Sustainability Impact
Promotes nature-based cooling solutions (trees, green roofs, water bodies).

Reduces urban heat and energy demand for air conditioning.

Helps improve air quality and public health.

Supports climate-resilient and sustainable city planning.
