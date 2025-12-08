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
