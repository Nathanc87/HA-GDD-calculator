# GDD Dashboard Blueprints

## Complete GDD Dashboard Setup

### Automatic Helper Creation

The integration automatically creates all required helper entities:

1. **GDD Threshold Control** (`input_number.gdd_threshold_control`)
   - Range: 50-5000, Step: 10
   - Default: 300 (optimized for turf)
   - Automatically synchronized with main threshold

2. **Base Temperature Control** (`input_number.gdd_base_temp_control`)
   - Range: 0-25°C, Step: 0.5°C
   - Default: 14°C
   - Automatically updates integration settings

**No manual setup required!** Just install the integration and start using the dashboards.

### Dashboard Implementation

With all helpers created automatically, you can immediately use these dashboard examples:

## Master GDD Control Panel

```yaml
type: vertical-stack
title: GDD Management
cards:
  # Main Status
  - type: entities
    title: Current Status
    entities:
      - entity: sensor.gdd_calculator_seasonal_gdd
        name: Season Total
        icon: mdi:counter
      - entity: sensor.gdd_calculator_gdd_development_stage  
        name: Growth Stage
      - entity: sensor.gdd_calculator_gdd_progress
        name: Progress to Target
        
  # Visual Progress
  - type: gauge  
    entity: sensor.gdd_calculator_seasonal_gdd
    name: Season Progress
    min: 0
    max: 1500
    needle: true
    severity:
      green: 0
      yellow: 1200
      red: 1400
      
  # Controls
  - type: entities
    title: Controls
    entities:
      - entity: input_number.gdd_threshold_control
        name: Target GDD
        icon: mdi:target
      - entity: input_number.gdd_base_temp_control
        name: Base Temperature  
        icon: mdi:thermometer
      - type: button
        name: Reset All GDD Values
        icon: mdi:restore
        tap_action:
          action: call-service
          service: gdd.reset_all
          confirmation:
            text: "Reset all GDD values? This cannot be undone!"
            
  # Daily Details
  - type: horizontal-stack
    cards:
      - type: entity
        entity: sensor.gdd_calculator_daily_gdd
        name: Today's GDD
        icon: mdi:weather-sunny
      - type: entity
        entity: sensor.gdd_calculator_weekly_gdd  
        name: Week Total
        icon: mdi:fire
      - type: entity
        entity: sensor.gdd_calculator_current_temperature
        name: Current Temp
        icon: mdi:thermometer
```

## Compact GDD Card

```yaml
type: entities
title: GDD Monitor
entities:
  - entity: sensor.gdd_calculator_seasonal_gdd
    name: Season GDD
    secondary_info: last-updated
  - entity: input_number.gdd_threshold_control
    name: Target
  - entity: sensor.gdd_calculator_gdd_development_stage
    name: Stage
  - type: divider
  - type: button
    name: Reset Season
    icon: mdi:restart
    tap_action:
      action: call-service  
      service: gdd.reset_all
```

## History & Trends Card

```yaml
type: vertical-stack
title: GDD Trends
cards:
  - type: history-graph
    entities:
      - sensor.gdd_calculator_daily_gdd
    hours_to_show: 168
    title: Daily GDD (Past Week)
    
  - type: statistics-graph
    entities:
      - sensor.gdd_calculator_seasonal_gdd
    stat_types:
      - mean
      - change
    period: day
    title: Season Progress
```

## Mobile-Friendly Compact View

```yaml
type: vertical-stack
cards:
  - type: glance
    entities:
      - entity: sensor.gdd_calculator_seasonal_gdd
        name: Season
      - entity: sensor.gdd_calculator_daily_gdd
        name: Today  
      - entity: sensor.gdd_calculator_gdd_development_stage
        name: Stage
    title: GDD Status
    
  - type: entities
    entities:
      - entity: input_number.gdd_threshold_control
        name: Target
      - entity: input_number.gdd_base_temp_control
        name: Base °C
```

## Turf Management Dashboard

Perfect for lawn and turf monitoring:

```yaml
type: vertical-stack
title: Turf Management
cards:
  # Turf Status Overview
  - type: entities
    title: Turf Growth Status
    entities:
      - entity: sensor.gdd_calculator_seasonal_gdd
        name: Season GDD
        icon: mdi:grass
      - entity: sensor.gdd_calculator_gdd_development_stage
        name: Growth Stage
      - entity: sensor.gdd_calculator_gdd_progress  
        name: Progress to Target (300 GDD)
        
  # Turf Progress Gauge (optimized for 200-400 GDD range)
  - type: gauge
    entity: sensor.gdd_calculator_seasonal_gdd
    name: Turf Growth Progress
    min: 0
    max: 400
    needle: true
    severity:
      green: 0      # Early growth
      yellow: 200   # Active growth period  
      red: 350      # Near maturity
      
  # Turf Controls
  - type: entities
    title: Turf Settings
    entities:
      - entity: input_number.gdd_threshold_control
        name: Target GDD (Cool: 250, Warm: 350)
      - entity: input_number.gdd_base_temp_control
        name: Base Temperature (Typically 10°C)
      - entity: sensor.gdd_calculator_current_temperature
        name: Current Temperature
      - type: button
        name: Reset for New Season
        icon: mdi:grass
        tap_action:
          action: call-service
          service: gdd.reset_all
          confirmation:
            text: "Reset GDD for new growing season?"
```

## Advanced Multi-Crop Dashboard

If you're tracking multiple crops:

```yaml
type: horizontal-stack
cards:
  - type: vertical-stack
    title: Turf Management (Base 10°C)
    cards:
      - type: gauge
        entity: sensor.turf_gdd_seasonal_gdd
        min: 0
        max: 400
        name: Turf GDD
      - type: entities
        entities:
          - sensor.turf_gdd_development_stage
          - input_number.turf_gdd_threshold
          
  - type: vertical-stack  
    title: Tomatoes (Base 10°C)
    cards:
      - type: gauge
        entity: sensor.tomato_gdd_seasonal_gdd
        min: 0
        max: 1200
        name: Tomato GDD
      - type: entities
        entities:
          - sensor.tomato_gdd_development_stage
          - input_number.tomato_gdd_threshold
```

## Automatic Setup - No Manual Work Required!

Everything is created and configured automatically when you install the integration:

✅ **Main threshold helper** (`input_number.gdd_threshold`)
✅ **Interactive control sliders** (`input_number.gdd_threshold_control` & `input_number.gdd_base_temp_control`)
✅ **Automatic synchronization** between controls and integration
✅ **Turf-optimized defaults** (300 GDD threshold, 14°C base temperature)

Just install, configure your weather entity and base temperature, then start using the dashboards!

These blueprints give you everything from simple monitoring to advanced multi-crop management dashboards!
