"""Constants for the GDD integration."""

DOMAIN = "gdd"

CONF_WEATHER = "weather_entity"
CONF_BASE_TEMP = "base_temperature"
CONF_CALCULATION_METHOD = "calculation_method"

DEFAULT_BASE = 14
DEFAULT_THRESHOLD = 250

# Calculation methods
METHOD_SINGLE_SINE = "single_sine"
METHOD_SIMPLE_AVERAGE = "simple_average"
METHOD_MODIFIED_AVERAGE = "modified_average"

CALCULATION_METHODS = {
    METHOD_SIMPLE_AVERAGE: "Simple Average (Tmax + Tmin) / 2",
    METHOD_MODIFIED_AVERAGE: "Modified Average (cap at base temp)",
    METHOD_SINGLE_SINE: "Single Sine Method"
}

STORAGE_VERSION = 2
STORAGE_KEY = f"{DOMAIN}_storage"

# Update intervals
UPDATE_INTERVAL_HOURS = 1
DAILY_UPDATE_TIME = "00:30"  # Daily calculations at 12:30 AM

# Turf Management Constants
TURF_GROWTH_RATES = {
    "base_growth_rate": 0.3,  # mm per GDD (realistic: ~3-5mm/day peak)
    "optimal_gdd_range": (8, 20),  # Daily GDD for optimal growth
    "dormancy_threshold": 3,  # GDD below which grass goes dormant
    "stress_threshold": 25,  # GDD above which grass is stressed
}

# Mowing recommendations
MOWING_THRESHOLDS = {
    "low_maintenance": 25,    # mm before mowing needed (was 1.0 inch)
    "medium_maintenance": 19, # mm before mowing needed (was 0.75 inch)
    "high_maintenance": 13,   # mm before mowing needed (was 0.5 inch)
}

# PGR application thresholds (cumulative weekly GDD)
PGR_THRESHOLDS = {
    "preventive": 35,    # Apply before heavy growth period
    "active": 50,        # Apply during active growth
    "rescue": 70,        # Apply when growth is excessive
}
