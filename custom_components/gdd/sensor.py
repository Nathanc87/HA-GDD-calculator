"""GDD sensor entities with proper state management."""
from __future__ import annotations
from typing import Optional

from homeassistant.components.sensor import SensorEntity, SensorStateClass, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.const import UnitOfTemperature

from .const import DOMAIN
from .coordinator import GDDCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up GDD sensors."""
    coordinator: GDDCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        GDDCurrentTempSensor(coordinator, entry),
        GDDDailyMinSensor(coordinator, entry),
        GDDDailyMaxSensor(coordinator, entry),
        GDDEstimatedDailySensor(coordinator, entry),
        GDDDailySensor(coordinator, entry),
        GDDWeeklySensor(coordinator, entry),
        GDDSeasonalSensor(coordinator, entry),
        GDDProgressSensor(coordinator, entry, hass),
        GDDStatusSensor(coordinator, entry, hass),
        GDDDataSourceSensor(coordinator, entry),
        GDDGrowthRateSensor(coordinator, entry),
        GDDMowingRecommendationSensor(coordinator, entry, hass),
        GDDPGRRecommendationSensor(coordinator, entry),
        GDDGrowthForecastSensor(coordinator, entry),
        GDDAccumulatedGrowthSensor(coordinator, entry),
    ]

    async_add_entities(sensors)


class GDDBaseSensor(SensorEntity, RestoreEntity):
    """Base class for GDD sensors."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, coordinator: GDDCoordinator, entry: ConfigEntry):
        self.coordinator = coordinator
        self._entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            manufacturer="Custom",
            name="GDD Calculator",
            model="Growing Degree Day Engine",
            sw_version="1.1.1",
            suggested_area="Garden",
        )

    @property
    def unique_id(self) -> str:
        """Return unique ID for the sensor."""
        return f"{self._entry.entry_id}_{self._attr_unique_id}"

    async def async_added_to_hass(self):
        """Handle entity added to hass."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success


class GDDCurrentTempSensor(GDDBaseSensor):
    """Current temperature sensor."""
    
    _attr_name = "Current Temperature"
    _attr_unique_id = "gdd_current_temp"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> Optional[float]:
        """Return current temperature."""
        if hasattr(self.coordinator, 'current_temp') and self.coordinator.current_temp is not None:
            return round(self.coordinator.current_temp, 1)
        return None


class GDDDailyMinSensor(GDDBaseSensor):
    """Daily minimum temperature sensor."""
    
    _attr_name = "Daily Min Temperature"
    _attr_unique_id = "gdd_daily_min"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> Optional[float]:
        """Return daily minimum temperature."""
        if hasattr(self.coordinator, 'daily_min') and self.coordinator.daily_min is not None:
            return round(self.coordinator.daily_min, 1)
        return None


class GDDDailyMaxSensor(GDDBaseSensor):
    """Daily maximum temperature sensor."""
    
    _attr_name = "Daily Max Temperature"
    _attr_unique_id = "gdd_daily_max"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> Optional[float]:
        """Return daily maximum temperature."""
        if hasattr(self.coordinator, 'daily_max') and self.coordinator.daily_max is not None:
            return round(self.coordinator.daily_max, 1)
        return None


class GDDEstimatedDailySensor(GDDBaseSensor):
    """Estimated daily GDD based on current min/max."""
    
    _attr_name = "Estimated Daily GDD"
    _attr_unique_id = "gdd_estimated_daily"
    _attr_native_unit_of_measurement = "°C·day"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:calculator-variant"

    @property
    def native_value(self) -> Optional[float]:
        """Return estimated daily GDD."""
        if hasattr(self.coordinator, 'estimated_daily_gdd'):
            return round(self.coordinator.estimated_daily_gdd, 2)
        return None


class GDDDailySensor(GDDBaseSensor):
    """Daily GDD accumulation sensor."""
    
    _attr_name = "Daily GDD"
    _attr_unique_id = "gdd_daily"
    _attr_native_unit_of_measurement = "°C·day"
    _attr_state_class = SensorStateClass.TOTAL
    _attr_icon = "mdi:weather-sunny"

    @property
    def native_value(self) -> Optional[float]:
        """Return daily GDD."""
        if hasattr(self.coordinator, 'daily_gdd'):
            return round(self.coordinator.daily_gdd, 2)
        return None


class GDDWeeklySensor(GDDBaseSensor):
    """Weekly GDD accumulation sensor."""
    
    _attr_name = "Weekly GDD"
    _attr_unique_id = "gdd_weekly"
    _attr_native_unit_of_measurement = "°C·day"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:fire"

    @property
    def native_value(self) -> Optional[float]:
        """Return weekly GDD."""
        if hasattr(self.coordinator, 'weekly_gdd'):
            return round(self.coordinator.weekly_gdd, 2)
        return None


class GDDSeasonalSensor(GDDBaseSensor):
    """Seasonal GDD accumulation sensor."""
    
    _attr_name = "Seasonal GDD"
    _attr_unique_id = "gdd_seasonal"
    _attr_native_unit_of_measurement = "°C·day"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:sun"

    @property
    def native_value(self) -> Optional[float]:
        """Return seasonal GDD."""
        if hasattr(self.coordinator, 'seasonal_gdd'):
            return round(self.coordinator.seasonal_gdd, 2)
        return None


class GDDProgressSensor(GDDBaseSensor):
    """GDD progress toward threshold sensor."""
    
    _attr_name = "GDD Progress"
    _attr_unique_id = "gdd_progress"
    _attr_native_unit_of_measurement = "°C·day"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:trending-up"

    def __init__(self, coordinator: GDDCoordinator, entry: ConfigEntry, hass: HomeAssistant):
        super().__init__(coordinator, entry)
        self.hass = hass

    @property
    def native_value(self) -> Optional[float]:
        """Return GDD progress (positive = above threshold, negative = below)."""
        threshold_entity = self.hass.states.get("input_number.gdd_threshold")
        if not threshold_entity or not hasattr(self.coordinator, 'seasonal_gdd'):
            return None
        
        try:
            threshold = float(threshold_entity.state)
            seasonal = self.coordinator.seasonal_gdd
            return round(seasonal - threshold, 1)  # Positive = above, negative = below
        except (ValueError, TypeError):
            return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional state attributes."""
        threshold_entity = self.hass.states.get("input_number.gdd_threshold")
        attrs = {}
        
        if threshold_entity and hasattr(self.coordinator, 'seasonal_gdd'):
            try:
                threshold = float(threshold_entity.state)
                seasonal = self.coordinator.seasonal_gdd
                attrs['threshold'] = threshold
                attrs['seasonal_gdd'] = seasonal
                attrs['percentage_complete'] = round((seasonal / threshold) * 100, 1) if threshold > 0 else 0
                attrs['gdd_remaining'] = round(threshold - seasonal, 1) if seasonal < threshold else 0
                attrs['status'] = "Above Threshold" if seasonal >= threshold else "Below Threshold"
            except (ValueError, TypeError):
                pass
                
        return attrs

    @property
    def icon(self) -> str:
        """Return icon based on progress."""
        if self.native_value is None:
            return "mdi:thermometer-alert"
        
        progress = self.native_value
        if progress >= 0:
            return "mdi:thermometer-chevron-up"  # Above threshold
        else:
            return "mdi:thermometer-chevron-down"  # Below threshold


class GDDStatusSensor(GDDBaseSensor):
    """GDD development stage indicator sensor."""
    
    _attr_name = "GDD Development Stage"
    _attr_unique_id = "gdd_status"
    _attr_native_unit_of_measurement = None

    def __init__(self, coordinator: GDDCoordinator, entry: ConfigEntry, hass: HomeAssistant):
        super().__init__(coordinator, entry)
        self.hass = hass

    @property
    def native_value(self) -> str:
        """Return GDD development stage."""
        threshold_entity = self.hass.states.get("input_number.gdd_threshold")
        if not threshold_entity or not hasattr(self.coordinator, 'seasonal_gdd'):
            return "No Target Set"

        try:
            threshold = float(threshold_entity.state)
            seasonal = self.coordinator.seasonal_gdd

            if seasonal < threshold * 0.25:
                return "Early Development"
            elif seasonal < threshold * 0.5:
                return "Active Growth"
            elif seasonal < threshold * 0.75:
                return "Advanced Growth"
            elif seasonal < threshold:
                percentage = round((seasonal / threshold) * 100, 1) if threshold > 0 else 0
                return f"Near Target ({percentage}%)"
            elif abs(seasonal - threshold) < 5:  # Within 5 GDD
                return "Target Reached"
            else:
                return "Target Exceeded"
        except (ValueError, TypeError):
            return "Invalid Target"

    @property
    def icon(self) -> str:
        """Return icon based on development stage."""
        status = self.native_value
        if "Exceeded" in status:
            return "mdi:sprout"
        elif "Target Reached" in status:
            return "mdi:flower"
        elif "Near Target" in status:
            return "mdi:flower-outline"
        elif "Advanced" in status:
            return "mdi:leaf"
        elif "Active" in status:
            return "mdi:seedling"
        elif "Early" in status:
            return "mdi:seed"
        else:
            return "mdi:thermometer-alert"

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional state attributes."""
        threshold_entity = self.hass.states.get("input_number.gdd_threshold")
        attrs = {}
        
        if threshold_entity and hasattr(self.coordinator, 'seasonal_gdd'):
            try:
                threshold = float(threshold_entity.state)
                seasonal = self.coordinator.seasonal_gdd
                attrs['target_gdd'] = threshold
                attrs['current_gdd'] = seasonal
                attrs['completion_percentage'] = round((seasonal / threshold) * 100, 1) if threshold > 0 else 0
                attrs['gdd_remaining'] = round(threshold - seasonal, 1) if seasonal < threshold else 0
                attrs['development_phase'] = self._get_development_phase(seasonal, threshold)
            except (ValueError, TypeError):
                pass
                
        return attrs
    
    def _get_development_phase(self, seasonal: float, threshold: float) -> str:
        """Get a more detailed development phase description."""
        if seasonal < threshold * 0.25:
            return "Germination & Early Emergence"
        elif seasonal < threshold * 0.5:
            return "Vegetative Growth"
        elif seasonal < threshold * 0.75:
            return "Reproductive Development"
        elif seasonal < threshold:
            return "Maturation Phase"
        else:
            return "Harvest Ready"


class GDDDataSourceSensor(GDDBaseSensor):
    """Diagnostic sensor showing temperature data source."""
    
    _attr_name = "GDD Data Source"
    _attr_unique_id = "gdd_data_source"
    _attr_native_unit_of_measurement = None
    _attr_entity_category = "diagnostic"

    @property
    def native_value(self) -> str:
        """Return the current data source being used."""
        if hasattr(self.coordinator, 'data_source_info'):
            info = self.coordinator.data_source_info
            if info.get('using_combined'):
                return "Combined Forecast + Tracked"
            elif info.get('using_forecast'):
                return "Weather Forecast"
            elif info.get('using_tracked'):
                return "Hourly Tracking"
            else:
                return "No Data"
        return "Unknown"

    @property
    def extra_state_attributes(self) -> dict:
        """Return detailed data source information."""
        attrs = {}
        if hasattr(self.coordinator, 'data_source_info'):
            info = self.coordinator.data_source_info
            attrs.update(info)
            
        # Add current temperature values for debugging
        if hasattr(self.coordinator, 'tracked_daily_min'):
            attrs['tracked_min'] = self.coordinator.tracked_daily_min
        if hasattr(self.coordinator, 'tracked_daily_max'):
            attrs['tracked_max'] = self.coordinator.tracked_daily_max
        if hasattr(self.coordinator, 'daily_min'):
            attrs['final_min'] = self.coordinator.daily_min
        if hasattr(self.coordinator, 'daily_max'):
            attrs['final_max'] = self.coordinator.daily_max
            
        return attrs

    @property
    def icon(self) -> str:
        """Return icon based on data source."""
        source = self.native_value
        if "Combined" in source:
            return "mdi:weather-cloudy"
        elif "Forecast" in source:
            return "mdi:weather-partly-cloudy"
        elif "Tracking" in source:
            return "mdi:thermometer"
        else:
            return "mdi:alert-circle"


class GDDGrowthRateSensor(GDDBaseSensor):
    """Turf growth rate multiplier sensor."""
    
    _attr_name = "Growth Rate Multiplier"
    _attr_unique_id = "gdd_growth_rate"
    _attr_native_unit_of_measurement = "×"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:trending-up"

    @property
    def native_value(self) -> Optional[float]:
        """Return growth rate multiplier."""
        if hasattr(self.coordinator, 'growth_rate_multiplier'):
            return round(self.coordinator.growth_rate_multiplier, 2)
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        attrs = {}
        if hasattr(self.coordinator, 'estimated_growth_mm'):
            attrs['daily_growth_mm'] = round(self.coordinator.estimated_growth_mm, 1)
        if hasattr(self.coordinator, 'weekly_gdd'):
            attrs['weekly_gdd'] = self.coordinator.weekly_gdd
        return attrs


class GDDMowingRecommendationSensor(GDDBaseSensor):
    """Mowing recommendation sensor."""
    
    _attr_name = "Mowing Recommendation"
    _attr_unique_id = "gdd_mowing_recommendation"
    _attr_native_unit_of_measurement = None
    _attr_icon = "mdi:lawn-mower"

    def __init__(self, coordinator: GDDCoordinator, entry: ConfigEntry, hass: HomeAssistant):
        super().__init__(coordinator, entry)
        self.hass = hass

    @property
    def native_value(self) -> str:
        """Return mowing recommendation."""
        if hasattr(self.coordinator, 'mowing_recommendation'):
            return self.coordinator.mowing_recommendation
        return "Unknown"

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional mowing info."""
        attrs = {}
        if hasattr(self.coordinator, 'accumulated_growth'):
            attrs['accumulated_growth_mm'] = round(self.coordinator.accumulated_growth, 1)
        if hasattr(self.coordinator, 'days_since_mow'):
            attrs['days_since_mow'] = self.coordinator.days_since_mow
        if hasattr(self.coordinator, 'days_to_next_mow'):
            attrs['estimated_days_to_mow'] = self.coordinator.days_to_next_mow
        return attrs

    @property
    def icon(self) -> str:
        """Return icon based on recommendation urgency."""
        recommendation = self.native_value
        if "critical" in recommendation.lower():
            return "mdi:lawn-mower-alert"
        elif "overdue" in recommendation.lower():
            return "mdi:lawn-mower-outline"
        elif "recommended" in recommendation.lower():
            return "mdi:lawn-mower"
        elif "soon" in recommendation.lower():
            return "mdi:timer-sand"
        else:
            return "mdi:check-circle"


class GDDPGRRecommendationSensor(GDDBaseSensor):
    """PGR application recommendation sensor."""
    
    _attr_name = "PGR Recommendation"
    _attr_unique_id = "gdd_pgr_recommendation"
    _attr_native_unit_of_measurement = None
    _attr_icon = "mdi:spray"

    @property
    def native_value(self) -> str:
        """Return PGR recommendation."""
        if hasattr(self.coordinator, 'pgr_recommendation'):
            return self.coordinator.pgr_recommendation
        return "Unknown"

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional PGR info."""
        attrs = {}
        if hasattr(self.coordinator, 'weekly_gdd'):
            attrs['weekly_gdd'] = self.coordinator.weekly_gdd
        if hasattr(self.coordinator, 'weekly_gdd_history') and self.coordinator.weekly_gdd_history:
            attrs['average_weekly_gdd'] = round(
                sum(self.coordinator.weekly_gdd_history) / len(self.coordinator.weekly_gdd_history), 1
            )
        return attrs

    @property
    def icon(self) -> str:
        """Return icon based on PGR urgency."""
        recommendation = self.native_value
        if "rescue" in recommendation.lower():
            return "mdi:spray-bottle"
        elif "active" in recommendation.lower():
            return "mdi:spray"
        elif "preventive" in recommendation.lower():
            return "mdi:shield-outline"
        else:
            return "mdi:check-circle-outline"


class GDDGrowthForecastSensor(GDDBaseSensor):
    """Growth forecast sensor."""
    
    _attr_name = "Growth Forecast"
    _attr_unique_id = "gdd_growth_forecast"
    _attr_native_unit_of_measurement = None
    _attr_icon = "mdi:chart-line-variant"

    @property
    def native_value(self) -> str:
        """Return growth forecast."""
        if hasattr(self.coordinator, 'growth_forecast'):
            return self.coordinator.growth_forecast
        return "Unknown"

    @property
    def extra_state_attributes(self) -> dict:
        """Return forecast details."""
        attrs = {}
        if hasattr(self.coordinator, 'growth_rate_multiplier'):
            attrs['growth_multiplier'] = self.coordinator.growth_rate_multiplier
        if hasattr(self.coordinator, 'estimated_daily_gdd'):
            attrs['estimated_daily_gdd'] = self.coordinator.estimated_daily_gdd
        return attrs


class GDDAccumulatedGrowthSensor(GDDBaseSensor):
    """Accumulated turf growth sensor."""
    
    _attr_name = "Accumulated Growth"
    _attr_unique_id = "gdd_accumulated_growth"
    _attr_native_unit_of_measurement = "mm"
    _attr_state_class = SensorStateClass.TOTAL
    _attr_device_class = "distance"
    _attr_icon = "mdi:ruler"

    @property
    def native_value(self) -> Optional[float]:
        """Return accumulated growth in millimeters."""
        if hasattr(self.coordinator, 'accumulated_growth'):
            return round(self.coordinator.accumulated_growth, 1)
        return None
