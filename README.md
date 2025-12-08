# GDD Integration v2.0 - Major Calculation Fix

## 🚨 CRITICAL FIX: GDD Calculation Error

### The Problem
Your original integration was calculating GDD incorrectly, which explains why it was 5x faster than online calculators:

**Original (Wrong) Logic:**
- Calculated GDD every hour using current temperature
- Added hourly GDD to daily, weekly, AND seasonal totals
- Result: If hourly GDD was 2.0°C·day, after 24 hours you'd have 48°C·day for that day

**Correct Logic:**
- Calculate GDD once per day using daily min/max temperatures  
- Daily GDD = max((Tmax + Tmin)/2 - base_temp, 0)
- Accumulate daily values into weekly/seasonal totals

### How GDD Should Work
Growing Degree Days represent **accumulated heat units over time**:
- 1 day at 20°C with base 10°C = 10 GDD for that day
- NOT 10 GDD × 24 hours = 240 GDD

## 🔧 Major Improvements Made

### 1. **Fixed Calculation Logic**
- Now calculates daily GDD using proper min/max methodology
- Three calculation methods available:
  - Simple Average: `(Tmax + Tmin)/2 - base_temp`
  - Modified Average: Caps temperatures at base temp before averaging
  - Single Sine: More accurate method for temperatures crossing base threshold

### 2. **Better Temperature Tracking**
- Tracks daily min/max temperatures throughout the day
- Shows current temperature, daily min/max, and estimated daily GDD
- Proper daily reset at midnight

### 3. **Enhanced Sensors**
- Current Temperature sensor
- Daily Min/Max Temperature sensors
- Estimated Daily GDD (live calculation based on current min/max)
- Improved deficit/excess sensor with percentage completion
- Status sensor with meaningful icons

### 4. **Improved Error Handling**
- Comprehensive logging for troubleshooting
- Graceful handling of missing weather data
- Better validation in config flow

### 5. **Enhanced Features**
- Options flow for updating settings
- Additional service to set base temperature
- Better device information with software version
- Proper state classes for Home Assistant energy dashboard

### 6. **Data Migration**
- Storage version bumped to v2
- Will preserve existing seasonal data when upgrading

## 📊 Expected Results After Fix

**Before (wrong):** Daily GDD accumulating 24x too fast
**After (correct):** Daily GDD matching online calculators

For example, with base temp 14°C:
- Day with min 12°C, max 22°C
- **Correct GDD:** (22 + 12)/2 - 14 = 3°C·day
- **Your old calculation:** Was adding ~3°C·day every hour = 72°C·day per day

## 🛠 Installation Notes

1. **Backup your data** before upgrading (seasonal totals will be preserved)
2. The integration will automatically migrate to the new calculation method
3. You may want to reset seasonal GDD after installation to start fresh with correct calculations
4. Monitor daily calculations for a few days to ensure they match expected values

## 🌡 Calculation Method Comparison

### Simple Average (Default)
- Formula: `max((Tmax + Tmin)/2 - base_temp, 0)`
- Best for: Most general use cases
- Pro: Simple, widely used
- Con: Can overestimate when temperatures dip below base

### Modified Average  
- Formula: Caps min/max at base temp before averaging
- Best for: When you want to ignore temperatures below base temp
- Pro: Conservative approach
- Con: May underestimate in some conditions

### Single Sine Method
- Formula: Uses sine wave approximation for temperature curve
- Best for: Research applications requiring precision
- Pro: Most accurate for variable temperature days
- Con: More complex calculation

Choose the method that matches your agricultural reference sources.

## 🔍 Monitoring Your Fix

Watch these sensors to verify correct operation:
1. **Daily Min/Max Temperature** - Should reset each day
2. **Estimated Daily GDD** - Live calculation, should be reasonable
3. **Daily GDD** - Should match hand calculations
4. **Weekly GDD** - Should be sum of daily values
5. **Seasonal GDD** - Should grow at expected rate

Your GDD values should now match online calculators for your location!
