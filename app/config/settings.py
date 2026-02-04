# ----------------------------------------
# SATELLITE DATA SETTINGS
# ----------------------------------------

START_DATE = "2024-01-01"
END_DATE = "2024-12-31"

GRID_SCALE = 500          # meters
ROI_BUFFER = 15000        # meters

# ----------------------------------------
# HEAT RISK WEIGHTS
# ----------------------------------------

TEMP_WEIGHT = 0.5
NDBI_WEIGHT = 0.3
NDVI_WEIGHT = 0.2

# ----------------------------------------
# SIMULATION PARAMETERS
# ----------------------------------------

GREEN_COVER_REDUCTION_PER_10 = 0.08   # °C per 10% green increase
COOL_ROOF_REDUCTION = 1.2             # °C

# ----------------------------------------
# THRESHOLDS
# ----------------------------------------

HIGH_RISK_THRESHOLD = 0.7
MODERATE_RISK_THRESHOLD = 0.4
SDG_HIGH_IMPACT = 1.5
SDG_MODERATE_IMPACT = 0.7
