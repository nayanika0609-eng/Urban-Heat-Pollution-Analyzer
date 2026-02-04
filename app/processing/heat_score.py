def calculate_heat_risk(df):
    df["heat_risk"] = (
        0.5 * df["temp_norm"] +
        0.3 * df["ndbi_norm"] +
        0.2 * df["ndvi_norm"]
    )
    return df
