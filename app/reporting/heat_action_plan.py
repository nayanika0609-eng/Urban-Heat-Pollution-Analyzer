from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

import matplotlib.pyplot as plt
import os

# --------------------------------------------------
# GENERATE BUDGET vs COOLING CHART
# --------------------------------------------------
def generate_budget_chart(budget, cooling):
    chart_path = "budget_vs_cooling.png"

    plt.figure(figsize=(5, 3))
    plt.bar(["Budget (₹ Cr)"], [budget], color="#3498db")
    plt.bar(["Cooling (°C)"], [cooling], color="#2ecc71")
    plt.title("Budget vs Temperature Reduction")
    plt.ylabel("Impact")
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    return chart_path


# --------------------------------------------------
# GENERATE POLLUTION CHART
# --------------------------------------------------
def generate_pollution_chart(pm25):
    chart_path = "pollution_level.png"

    plt.figure(figsize=(5, 3))
    plt.bar(["PM2.5"], [pm25], color="#e74c3c")
    plt.axhline(60, color="orange", linestyle="--", label="Moderate limit")
    plt.axhline(30, color="green", linestyle="--", label="Good limit")
    plt.ylabel("µg/m³")
    plt.title("Ground Air Pollution (PM2.5)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    return chart_path


# --------------------------------------------------
# ACTION PLAN TABLE DATA
# --------------------------------------------------
def build_action_plan_table(selected_actions):
    header = ["Intervention", "Estimated Cost (₹ Cr)", "Cooling Impact (°C)"]

    cost_impact_map = {
        "Green Cover Expansion": (2.0, 0.8),
        "Cool Roof": (1.5, 1.2),
        "Green Roof": (1.2, 0.6),
        "Water Bodies": (2.5, 1.0),
        "Cool Pavement": (1.8, 0.7),
    }

    table_data = [header]

    for action in selected_actions:
        name = action.replace("_", " ").title()
        cost, impact = cost_impact_map.get(name, (1.0, 0.5))
        table_data.append([name, cost, impact])

    return table_data


# --------------------------------------------------
# CITY-SPECIFIC GUIDELINES
# --------------------------------------------------
def get_city_guidelines(city):
    if city.lower() == "delhi":
        return """
<b>City-Specific Focus (Delhi)</b><br/><br/>
• Prioritize dust suppression and traffic emission control<br/>
• Expand urban forests along highways and industrial zones<br/>
• Cool roofs for slum clusters and government schools<br/>
• Strengthen Heatwave + Smog early warning integration
"""
    elif city.lower() == "mumbai":
        return """
<b>City-Specific Focus (Mumbai)</b><br/><br/>
• Focus on coastal heat stress and dense slum redevelopment<br/>
• Increase shaded corridors and waterfront cooling zones<br/>
• Reflective roofing in Dharavi and transit hubs<br/>
• Integrate drainage + cooling for monsoon resilience
"""
    elif city.lower() == "pune":
        return """
<b>City-Specific Focus (Pune)</b><br/><br/>
• Protect hill slopes and green buffers from construction<br/>
• Promote rooftop gardens in IT corridors<br/>
• Increase tree cover along major roads<br/>
• Target industrial PM2.5 hotspots
"""
    else:
        return ""


# --------------------------------------------------
# MAIN PDF GENERATOR
# --------------------------------------------------
def generate_heat_pollution_action_plan(
    city,
    avg_temp,
    hot_pct,
    avg_pm25,
    budget,
    estimated_cooling,
    selected_actions
):
    file_path = f"{city}_Heat_Pollution_Action_Plan.pdf"
    styles = getSampleStyleSheet()

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []

    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------
    story.append(Paragraph(f"<b>{city} Heat & Pollution Action Plan</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    # --------------------------------------------------
    # EXECUTIVE SUMMARY
    # --------------------------------------------------
    summary_text = f"""
<b>Executive Summary</b><br/><br/>
This plan integrates satellite-based urban heat assessment with
ground-level air pollution monitoring to guide climate and health policy
for <b>{city}</b>.<br/><br/>

• Average surface temperature: <b>{avg_temp:.1f} °C</b><br/>
• High-risk heat zones: <b>{hot_pct:.0f}%</b> of the city<br/>
• Average PM2.5 level: <b>{avg_pm25:.1f} µg/m³</b><br/>
• Proposed policy budget: <b>₹{budget} crore</b><br/>
• Expected average cooling: <b>{estimated_cooling:.1f} °C</b>
"""
    story.append(Paragraph(summary_text, styles["Normal"]))
    story.append(Spacer(1, 16))

    # --------------------------------------------------
    # BUDGET vs COOLING VISUAL
    # --------------------------------------------------
    story.append(Paragraph("<b>Budget vs Cooling Impact</b>", styles["Heading2"]))
    story.append(Spacer(1, 8))
    chart_path = generate_budget_chart(budget, estimated_cooling)
    story.append(Image(chart_path, width=320, height=200))
    story.append(Spacer(1, 16))

    # --------------------------------------------------
    # POLLUTION VISUAL
    # --------------------------------------------------
    story.append(Paragraph("<b>Air Pollution Status</b>", styles["Heading2"]))
    story.append(Spacer(1, 8))
    pollution_chart = generate_pollution_chart(avg_pm25)
    story.append(Image(pollution_chart, width=320, height=200))
    story.append(Spacer(1, 16))

    # --------------------------------------------------
    # ACTION PLAN TABLE
    # --------------------------------------------------
    story.append(Paragraph("<b>Recommended Cooling Interventions</b>", styles["Heading2"]))
    story.append(Spacer(1, 8))

    table_data = build_action_plan_table(selected_actions)
    table = Table(table_data, colWidths=[200, 150, 150])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))

    story.append(table)
    story.append(Spacer(1, 16))

    # --------------------------------------------------
    # CITY GUIDELINES
    # --------------------------------------------------
    story.append(Paragraph(get_city_guidelines(city), styles["Normal"]))
    story.append(Spacer(1, 16))

    # --------------------------------------------------
    # IMPLEMENTATION GUIDELINES
    # --------------------------------------------------
    guidelines = """
<b>Implementation Guidelines</b><br/><br/>
1. Focus interventions in wards with highest heat & pollution overlap<br/>
2. Prioritize schools, hospitals, and slum areas<br/>
3. Integrate heat action plans with AQI advisories<br/>
4. Use satellite data annually to update hotspots<br/>
5. Track health impacts during summer seasons
"""
    story.append(Paragraph(guidelines, styles["Normal"]))

    # --------------------------------------------------
    # BUILD PDF
    # --------------------------------------------------
    doc.build(story)

    if os.path.exists(chart_path):
        os.remove(chart_path)
    if os.path.exists(pollution_chart):
        os.remove(pollution_chart)

    return file_path
