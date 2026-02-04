def simulate_temperature(
    df,
    green_cover=0,
    cool_roof=False,
    green_roof=False,
    water_bodies=False,
    cool_pavement=False
):
    """
    Simulates temperature reduction based on selected cooling strategies.
    All values are planning-level estimates (°C).
    """

    # Start with original temperature
    temp = df["ST_B10"].copy()

    # Green cover impact (scaled)
    temp -= green_cover * 0.08   # 10% ≈ 0.8°C

    if cool_roof:
        temp -= 1.2

    if green_roof:
        temp -= 0.6

    if water_bodies:
        temp -= 1.0

    if cool_pavement:
        temp -= 0.7

    return temp
