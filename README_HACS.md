# Growing Degree Days (GDD) Calculator for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/Nathanc87/HA-GDD-calculator.svg)](https://github.com/Nathanc87/HA-GDD-calculator/releases)
[![GitHub Activity](https://img.shields.io/github/commit-activity/y/Nathanc87/HA-GDD-calculator.svg)](https://github.com/Nathanc87/HA-GDD-calculator/commits/main)

A comprehensive Home Assistant integration for calculating and monitoring **Growing Degree Days (GDD)** - essential for agricultural timing, crop monitoring, and garden management.

## 🌱 What are Growing Degree Days?

Growing Degree Days measure the accumulated heat units above a base temperature that plants need for development. This integration helps you:

- **Time agricultural activities** (planting, fertilizing, harvesting)
- **Monitor crop development** stages
- **Predict pest emergence** and disease pressure
- **Optimize irrigation** and management decisions
- **Track seasonal progress** toward maturity targets

## ✨ Features

### 📊 **Comprehensive Sensors**
- **Current Temperature** - Live weather monitoring
- **Daily Min/Max** - Automatic temperature extremes
- **Estimated Daily GDD** - Real-time calculation preview
- **Daily GDD** - Completed day calculations
- **Weekly GDD** - Rolling weekly totals
- **Seasonal GDD** - Cumulative season progress
- **GDD Progress** - Distance from your target
- **Development Stage** - Agricultural growth phases

### 🎯 **Smart Calculation Methods**
- **Simple Average**: `(Tmax + Tmin)/2 - base_temp`
- **Modified Average**: Caps temperatures at base temp
- **Single Sine Method**: Most accurate for variable conditions

### 🌡️ **Enhanced Temperature Data**
- **Weather Forecast Integration** - Uses official daily min/max when available
- **Hourly Tracking Fallback** - Monitors temperature throughout the day
- **Combined Approach** - Uses most extreme values for accuracy
- **Data Source Diagnostics** - Shows which method is being used

### 🔧 **Easy Management**
- **Config Flow Setup** - No YAML configuration needed
- **Automatic Threshold Helper** - Creates input_number for your GDD target
- **Service Calls** - Reset values and adjust settings
- **Persistent Storage** - Survives Home Assistant restarts

## 🚀 Installation

### Via HACS (Recommended)

1. **Add Custom Repository**:
   - Open HACS
   - Go to "Integrations"
   - Click the three dots (⋮) → "Custom repositories"
   - Add: `https://github.com/Nathanc87/HA-GDD-calculator`
   - Category: "Integration"

2. **Install Integration**:
   - Search for "Growing Degree Days"
   - Click "Download"
   - Restart Home Assistant

3. **Add Integration**:
   - Go to Settings → Devices & Services
   - Click "Add Integration"
   - Search for "Growing Degree Days"
   - Follow the setup wizard

### Manual Installation

1. Download the latest release from [GitHub](https://github.com/Nathanc87/HA-GDD-calculator/releases)
2. Copy `custom_components/gdd/` to your `custom_components/` directory
3. Restart Home Assistant
4. Add the integration via Settings → Devices & Services

## ⚙️ Configuration

### Initial Setup
1. **Select Weather Entity** - Choose your weather integration
2. **Set Base Temperature** - Typically 10-15°C for most crops
3. **Choose Calculation Method** - Simple Average recommended for most uses
4. **Set GDD Target** - Use the automatically created helper

### Common Crop Targets

| Crop | GDD Target | Base Temp | Notes |
|------|------------|-----------|-------|
| Corn (Silage) | 800-1000 | 10°C | To physiological maturity |
| Tomatoes | 1000-1200 | 10°C | To fruit harvest |
| Wheat | 1400-1700 | 4°C | To grain harvest |
| Soybeans | 1200-1500 | 10°C | To maturity |
| Potatoes | 1200-1400 | 7°C | To harvest |
| Apple Trees | 200-300 | 4°C | To bloom |

## 📊 Dashboard Examples

### Basic GDD Card
```yaml
type: entities
title: GDD Monitoring
entities:
  - entity: input_number.gdd_threshold
    name: Target GDD
  - entity: sensor.gdd_seasonal
    name: Current GDD
  - entity: sensor.gdd_progress
    name: Progress
  - entity: sensor.gdd_development_stage
    name: Growth Stage
```

### Advanced GDD Dashboard
```yaml
type: vertical-stack
cards:
  - type: gauge
    entity: sensor.gdd_seasonal
    min: 0
    max: 1500
    name: Seasonal GDD Progress
    needle: true
    
  - type: entities
    entities:
      - sensor.gdd_daily
      - sensor.gdd_weekly
      - sensor.gdd_development_stage
      - sensor.gdd_data_source
      
  - type: history-graph
    entities:
      - sensor.gdd_daily
    hours_to_show: 168
    title: Daily GDD Trend
```

## 🛠️ Services

### Reset All Values
```yaml
service: gdd.reset_all
```

### Set Seasonal GDD
```yaml
service: gdd.set_seasonal_gdd
data:
  value: 250.5
```

### Update Base Temperature
```yaml
service: gdd.set_base_temperature
data:
  temperature: 12.0
```

## 🧪 Development Stages

The integration provides meaningful agricultural development stages:

- 🌰 **Early Development** (0-25%) - Germination & Early Emergence
- 🌱 **Active Growth** (25-50%) - Vegetative Growth
- 🍃 **Advanced Growth** (50-75%) - Reproductive Development
- 🌸 **Near Target** (75-100%) - Maturation Phase
- 🌺 **Target Reached** - Ready for action
- 🌿 **Target Exceeded** - Harvest Ready

## 📈 Data Sources

The integration intelligently uses the best available temperature data:

1. **Weather Forecast** (Priority 1) - Official daily min/max from your weather service
2. **Hourly Tracking** (Priority 2) - Continuous monitoring fallback
3. **Combined Data** (Priority 3) - Most extreme values from both sources

Check the "GDD Data Source" sensor to see which method is active.

## 🔧 Troubleshooting

### Common Issues

**GDD values too high/low:**
- Verify your base temperature is correct for your crop
- Check that the weather entity provides accurate temperatures
- Review the calculation method selection

**Missing threshold helper:**
- The integration creates `input_number.gdd_threshold` automatically
- If missing, create manually in Settings → Helpers
- Use the Number helper with range 50-5000

**Temperature data gaps:**
- Check that your weather integration is working
- The system will use tracked temperatures as fallback
- Monitor the "GDD Data Source" sensor

### Debug Information

Enable debug logging:
```yaml
logger:
  logs:
    custom_components.gdd: debug
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Home Assistant community for the excellent platform
- Agricultural extension services for GDD calculation methods
- Weather service providers for temperature data

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Nathanc87/HA-GDD-calculator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Nathanc87/HA-GDD-calculator/discussions)
- **Home Assistant Community**: [Community Forum](https://community.home-assistant.io/)

---

*Perfect for farmers, gardeners, and agricultural enthusiasts who want to leverage the power of Home Assistant for crop management!* 🌾
