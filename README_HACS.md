# Growing Degree Days Calculator for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/Nathanc87/HA-GDD-calculator.svg)](https://github.com/Nathanc87/HA-GDD-calculator/releases)
[![GitHub Activity](https://img.shields.io/github/commit-activity/y/Nathanc87/HA-GDD-calculator.svg)](https://github.com/Nathanc87/HA-GDD-calculator/commits/main)

Track growing degree days for better crop timing and agricultural decisions directly in Home Assistant.

## What is this?

If you grow crops, manage orchards, or just want to time your garden better, this integration calculates Growing Degree Days (GDD) using your local weather data. GDD helps predict when to plant, when pests might emerge, and when crops will be ready to harvest.

Think of it as a heat accumulation meter for your plants. Different crops need different amounts of accumulated heat to reach maturity, and this helps you track that progress.

## Features

- **Real-time tracking** of daily, weekly, and seasonal heat accumulation
- **Multiple calculation methods** (simple average, modified average, single sine)
- **Smart temperature handling** - uses weather forecast data when available, falls back to hourly tracking
- **Crop development stages** - see where your plants are in their growth cycle
- **Progress tracking** - know exactly how close you are to harvest time
- **Persistent data** - survives Home Assistant restarts and keeps your season totals

## Installation

### Via HACS

1. Add this repository to HACS as a custom integration:
   - HACS → Integrations → ⋮ → Custom repositories
   - Add: `https://github.com/Nathanc87/HA-GDD-calculator`
   - Category: Integration

2. Search for "Growing Degree Days" in HACS and install
3. Restart Home Assistant
4. Go to Settings → Integrations → Add Integration
5. Search for "Growing Degree Days" and configure

### Manual Installation

Download the [latest release](https://github.com/Nathanc87/HA-GDD-calculator/releases) and copy the `custom_components/gdd` folder to your Home Assistant `custom_components` directory.

## Setup

You'll need:
1. A weather integration (like OpenWeatherMap, Met.no, etc.)
2. To know your crop's base temperature (usually 10°C for warm season crops, 4-7°C for cool season)
3. Your target GDD for harvest (see table below)

The integration automatically creates a helper to set your GDD target.

## Calculation Methods Explained

The integration offers three different methods for calculating daily GDD, each with specific use cases:

### **Simple Average (Default - Recommended)**
**Formula:** `(daily_max + daily_min) ÷ 2 - base_temperature`

**When to use:** Most situations - it's the industry standard
**Pros:** 
- Widely used and accepted
- Easy to understand and verify
- Matches most agricultural extension recommendations
**Cons:** 
- Can overestimate GDD when temperatures dip significantly below base temp
- Doesn't account for the actual temperature curve throughout the day

**Example:** Max 25°C, Min 5°C, Base 10°C = `(25 + 5) ÷ 2 - 10 = 5 GDD`

### **Modified Average** 
**Formula:** `(capped_max + capped_min) ÷ 2 - base_temperature`
*(Caps both min and max temperatures at the base temperature before averaging)*

**When to use:** Cool climates or when you want conservative estimates
**Pros:**
- More conservative approach
- Eliminates negative contributions from cold temperatures
- Better for crops sensitive to cold stress
**Cons:**
- May underestimate in variable temperature conditions
- Less commonly used in agricultural research

**Example:** Max 25°C, Min 5°C, Base 10°C = `(25 + 10) ÷ 2 - 10 = 7.5 GDD`
*(Min temperature raised to base temp of 10°C)*

### **Single Sine Method**
**Formula:** Uses trigonometric functions to model the daily temperature curve as a sine wave

**When to use:** Research applications, precision agriculture, or when you need maximum accuracy
**Pros:**
- Most mathematically accurate
- Accounts for the actual temperature curve throughout the day
- Handles temperature crossing base threshold more precisely
**Cons:**
- More complex to understand and verify
- Overkill for most practical applications
- Requires more computational resources

**Example:** Creates a sine wave between daily min/max and calculates the area above the base temperature

### **Which Method Should You Choose?**

- **Most users:** Simple Average (default)
- **Cool climates/conservative estimates:** Modified Average  
- **Research/precision farming:** Single Sine Method
- **Matching extension data:** Check which method your local agricultural extension uses

## Common Crop Targets

| Crop | Base Temp | GDD to Maturity | Notes |
|------|-----------|-----------------|-------|
| **Turf Grass** | **10°C** | **200-400** | **Cool season: 200-300, Warm season: 300-400** |
| Corn | 10°C | 800-1400 | Depends on variety |
| Tomatoes | 10°C | 1000-1200 | From transplant |
| Soybeans | 10°C | 1200-1500 | To harvest |
| Wheat | 4°C | 1400-1700 | Winter varieties |
| Potatoes | 7°C | 1200-1400 | From planting |
| Peas | 4°C | 500-700 | Cool season crop |

*These are starting points - check with your local extension office for variety-specific recommendations*

## Dashboard Example

### Basic GDD Monitoring
```yaml
type: entities
title: Crop Progress
entities:
  - entity: input_number.gdd_threshold
    name: Target GDD
  - entity: sensor.gdd_calculator_seasonal_gdd
    name: Accumulated GDD
  - entity: sensor.gdd_calculator_gdd_development_stage
    name: Growth Stage
  - entity: sensor.gdd_calculator_gdd_progress
    name: Progress to Target
```

### Interactive GDD Control Panel
```yaml
type: entities
title: GDD Controls
entities:
  - type: button
    name: Reset GDD Values
    icon: mdi:restore
    tap_action:
      action: call-service
      service: gdd.reset_all
      confirmation:
        text: "Are you sure you want to reset all GDD values? This cannot be undone."
  - entity: input_number.gdd_threshold_control
    name: GDD Target
    icon: mdi:target
  - entity: input_number.gdd_base_temp_control  
    name: Base Temperature
    icon: mdi:thermometer
  - entity: sensor.gdd_calculator_seasonal_gdd
    name: Current GDD
    icon: mdi:counter
```

### Visual Progress Dashboard
```yaml
type: vertical-stack
cards:
  - type: gauge
    entity: sensor.gdd_calculator_seasonal_gdd
    min: 0
    max: 1500
    name: Season Progress
    needle: true
    severity:
      green: 0
      yellow: 75
      red: 90
      
  - type: horizontal-stack
    cards:
      - type: entity
        entity: sensor.gdd_calculator_daily_gdd
        name: Today
        icon: mdi:weather-sunny
      - type: entity  
        entity: sensor.gdd_calculator_weekly_gdd
        name: This Week
        icon: mdi:fire
        
  - type: entities
    entities:
      - entity: sensor.gdd_calculator_gdd_development_stage
      - entity: sensor.gdd_calculator_current_temperature
      - entity: sensor.gdd_calculator_gdd_data_source
```

### Required Input Number Helpers

To use the interactive controls, create these helpers in **Settings → Helpers**:

**GDD Threshold Control:**
- **Name:** GDD Threshold Control
- **Entity ID:** `gdd_threshold_control`
- **Min:** 50
- **Max:** 5000
- **Step:** 10
- **Unit:** °C·day
- **Icon:** mdi:target

**Base Temperature Control:** 
- **Name:** GDD Base Temperature Control
- **Entity ID:** `gdd_base_temp_control`
- **Min:** 0
- **Max:** 25
- **Step:** 0.5
- **Unit:** °C
- **Icon:** mdi:thermometer
- **Initial:** 14

### Automation for Control Sync

Add these automations to sync your controls with the integration:

```yaml
# Sync threshold control to integration
- alias: "GDD: Update Threshold from Control"
  trigger:
    - platform: state
      entity_id: input_number.gdd_threshold_control
  action:
    - service: input_number.set_value
      target:
        entity_id: input_number.gdd_threshold
      data:
        value: "{{ states('input_number.gdd_threshold_control') }}"

# Sync base temperature control to integration  
- alias: "GDD: Update Base Temperature from Control"
  trigger:
    - platform: state
      entity_id: input_number.gdd_base_temp_control
  action:
    - service: gdd.set_base_temperature
      data:
        temperature: "{{ states('input_number.gdd_base_temp_control') | float }}"

# Sync main threshold to control (keeps them in sync)
- alias: "GDD: Sync Main Threshold to Control"
  trigger:
    - platform: state
      entity_id: input_number.gdd_threshold
  action:
    - service: input_number.set_value
      target:
        entity_id: input_number.gdd_threshold_control
      data:
        value: "{{ states('input_number.gdd_threshold') }}"
```

### All Available Entities

Replace `gdd_calculator` with your actual device name:

- `sensor.gdd_calculator_current_temperature`
- `sensor.gdd_calculator_daily_min_temperature` 
- `sensor.gdd_calculator_daily_max_temperature`
- `sensor.gdd_calculator_estimated_daily_gdd`
- `sensor.gdd_calculator_daily_gdd`
- `sensor.gdd_calculator_weekly_gdd`
- `sensor.gdd_calculator_seasonal_gdd`
- `sensor.gdd_calculator_gdd_progress`
- `sensor.gdd_calculator_gdd_development_stage`
- `sensor.gdd_calculator_gdd_data_source`
- `input_number.gdd_threshold`

### Quick Helper Setup

To quickly create the control helpers, use Developer Tools → Services:

**Create GDD Threshold Control:**
```yaml
service: input_number.create
data:
  name: "GDD Threshold Control"
  min: 50
  max: 5000
  step: 10
  initial: 300
  unit_of_measurement: "°C·day"
  icon: "mdi:target"
```

**Create Base Temperature Control:**
```yaml
service: input_number.create  
data:
  name: "GDD Base Temperature Control"
  min: 0
  max: 25
  step: 0.5
  initial: 14
  unit_of_measurement: "°C"
  icon: "mdi:thermometer"
```

## How It Works

The integration monitors your weather entity and:
1. Calculates daily GDD using min/max temperatures: `(max_temp + min_temp)/2 - base_temp`
2. Only counts positive values (cold days don't subtract)
3. Accumulates daily totals into weekly and seasonal sums
4. Compares against your target to show development stages

It prioritizes forecast data when available (more accurate than hourly sampling) but falls back to tracking temperatures throughout the day if needed.

## Services

Reset everything at the start of a new season:
```yaml
service: gdd.reset_all
```

Manually adjust if you have historical data:
```yaml
service: gdd.set_seasonal_gdd
data:
  value: 345.2
```

Change base temperature without reconfiguring:
```yaml
service: gdd.set_base_temperature
data:
  temperature: 12.0
```

## Troubleshooting

**Values seem too high/low?**
- Double-check your base temperature for your specific crop
- Verify your weather integration is reporting accurate temperatures
- Try a different calculation method in the options

**Missing the threshold helper?**
- It should auto-create as `input_number.gdd_threshold`
- If not, manually create a Number helper with min: 50, max: 5000

**Want more detail?**
Enable debug logging:
```yaml
logger:
  logs:
    custom_components.gdd: debug
```

## Contributing

Found a bug or want to add a feature? Open an issue or submit a pull request. Agricultural knowledge welcome - I'm always learning about better GDD applications.

## License

MIT License - use it however helps your growing operation.

---

*Built for the Home Assistant community by someone who believes good data leads to better harvests.*
