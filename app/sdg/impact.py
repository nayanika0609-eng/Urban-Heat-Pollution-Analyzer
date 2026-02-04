def sdg_mapping(temp_change):
    if temp_change > 1.5:
        return "High SDG Impact"
    elif temp_change > 0.7:
        return "Moderate SDG Impact"
    return "Low SDG Impact"
