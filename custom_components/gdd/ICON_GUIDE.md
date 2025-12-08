# GDD Integration Icon Setup

## 🎨 Custom Icon Implementation

The GDD integration now includes a custom icon that combines sun and grass elements, representing the agricultural temperature monitoring concept of Growing Degree Days.

## 🔧 How the Icon Works

### **Automatic Integration Icon**
The icon is embedded directly in the `manifest.json` file as a base64-encoded SVG, which means:

✅ **Device page visibility** - Shows up on Home Assistant's Devices & Services page
✅ **Integration branding** - Appears in the integrations list  
✅ **No external files needed** - Everything is self-contained
✅ **Theme compatible** - Uses `currentColor` for automatic light/dark theme support

### **Individual Sensor Icons**
Each sensor type has its own contextual icon:

| Sensor | Icon | Purpose |
|--------|------|---------|
| Current Temperature | `mdi:thermometer` | Standard temperature reading |
| Daily Min/Max | `mdi:thermometer` | Temperature extremes |
| Estimated Daily GDD | `mdi:calculator-variant` | Live calculation |
| Daily GDD | `mdi:calendar-today` | Today's accumulation |
| Weekly GDD | `mdi:calendar-week` | Weekly accumulation |
| Seasonal GDD | `mdi:calendar-range` | Season total |
| GDD Progress | `mdi:progress-check` | Progress toward target |
| Development Stage | Dynamic icons | Growth phase indicators |
| Data Source | Dynamic icons | Data quality indicators |

### **Development Stage Icons**
The Development Stage sensor uses progressive plant icons:
- 🌰 `mdi:seed` - Early Development
- 🌱 `mdi:seedling` - Active Growth  
- 🍃 `mdi:leaf` - Advanced Growth
- 🌸 `mdi:flower-outline` - Near Target
- 🌺 `mdi:flower` - Target Reached
- 🌿 `mdi:sprout` - Target Exceeded

## 🎯 Icon Design Elements

The custom integration icon features:
- **Sun with rays** - Represents temperature and heat accumulation
- **Grass blades** - Represents agricultural growth and crops
- **Clean lines** - Professional appearance in Home Assistant UI
- **SVG format** - Scalable and crisp at any size
- **Theme adaptive** - Uses currentColor for automatic theming

## 📁 Available Icon Files

If you want to use the icons elsewhere, these files are available:

1. **`gdd_icon_simple.svg`** - Used in the integration (recommended)
2. **`gdd_icon.svg`** - Detailed version with more elements
3. **`gdd_icon_thermometer.svg`** - Version with thermometer element

## 🔧 Manual Icon Installation (Optional)

If you want to use the icons in other parts of Home Assistant:

1. Copy any SVG file to `/config/www/icons/`
2. Reference in Lovelace cards as: `/local/icons/gdd_icon_simple.svg`
3. Use in custom cards or dashboards

## ✨ Benefits

- **Professional appearance** - Custom branding for your GDD monitoring
- **Visual consistency** - Unified icon theme across all sensors
- **Easy identification** - Quickly spot GDD entities in your dashboard
- **Agricultural context** - Icons that make sense for crop monitoring

The icons are now fully integrated and will appear automatically when you install the integration!
