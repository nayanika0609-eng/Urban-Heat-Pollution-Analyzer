import folium
from folium.plugins import HeatMap

def create_heatmap(df):
    center = [df["latitude"].mean(), df["longitude"].mean()]
    m = folium.Map(location=center, zoom_start=11, tiles="cartodbpositron")

    heat_data = [
        [row["latitude"], row["longitude"], row["ST_B10"]]
        for _, row in df.iterrows()
    ]

    HeatMap(
        heat_data,
        radius=25,
        blur=30,
        min_opacity=0.4,
    ).add_to(m)

    # Simple legend
    legend_html = """
    <div style="
        position: fixed;
        bottom: 40px;
        left: 40px;
        width: 220px;
        background-color: white;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        font-size: 14px;
    ">
    <b>Heat Map Guide</b><br>
    🔴 Hotter areas<br>
    🟡 Moderate areas<br>
    🟢 Cooler areas<br><br>
    This map shows surface heat intensity.
    </div>
    """

    m.get_root().html.add_child(folium.Element(legend_html))

    return m
