"""Enhanced GDD coordinator that uses weather forecast data when available."""
from __future__ import annotations
import logging
import math
from datetime import datetime, timedelta, date
from typing import Dict, Any, Optional, List

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN, CONF_WEATHER, CONF_BASE_TEMP, CONF_CALCULATION_METHOD,
    STORAGE_KEY, STORAGE_VERSION, UPDATE_INTERVAL_HOURS,
    METHOD_SIMPLE_AVERAGE, METHOD_MODIFIED_AVERAGE, METHOD_SINGLE_SINE
)

_LOGGER = logging.getLogger(__name__)


class GDDCoordinator(DataUpdateCoordinator):
    """Enhanced coordinator that uses weather forecast data when available."""

    def __init__(self, hass: HomeAssistant, config: Dict[str, Any]):
        self.hass = hass
        self.weather_entity = config[CONF_WEATHER]
        self.base_temp = float(config[CONF_BASE_TEMP])
        self.calculation_method = config.get(CONF_CALCULATION_METHOD, METHOD_SIMPLE_AVERAGE)

        # Current values
        self.current_temp: Optional[float] = None
        
        # Daily temperature tracking - multiple sources
        self.tracked_daily_min: Optional[float] = None  # From hourly monitoring
        self.tracked_daily_max: Optional[float] = None  # From hourly monitoring
        self.forecast_daily_min: Optional[float] = None  # From weather forecast
        self.forecast_daily_max: Optional[float] = None  # From weather forecast
        
        # Final values used for calculation
        self.daily_min: Optional[float] = None
        self.daily_max: Optional[float] = None
        
        # Accumulated values
        self.daily_gdd = 0.0
        self.weekly_gdd = 0.0
        self.seasonal_gdd = 0.0
        
        # Tracking variables
        self.last_calculation_date: Optional[str] = None
        self.last_week_number: Optional[int] = None
        self.daily_temps: list = []  # Store temps throughout the day
        
        # Storage
        self.store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self.last_known_data: Dict[str, Any] = {}

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=UPDATE_INTERVAL_HOURS),
        )

    async def async_load(self):
        """Load stored values on startup."""
        try:
            data = await self.store.async_load()
            if data:
                self.daily_gdd = data.get("daily_gdd", 0.0)
                self.weekly_gdd = data.get("weekly_gdd", 0.0)
                self.seasonal_gdd = data.get("seasonal_gdd", 0.0)
                self.last_calculation_date = data.get("last_calculation_date")
                self.last_week_number = data.get("last_week_number")
                self.tracked_daily_min = data.get("tracked_daily_min")
                self.tracked_daily_max = data.get("tracked_daily_max")
                self.daily_temps = data.get("daily_temps", [])
                _LOGGER.info(f"Loaded GDD data: seasonal={self.seasonal_gdd}")
        except Exception as err:
            _LOGGER.error(f"Error loading GDD data: {err}")

    async def async_save(self):
        """Persist values to storage."""
        try:
            data = {
                "daily_gdd": self.daily_gdd,
                "weekly_gdd": self.weekly_gdd,
                "seasonal_gdd": self.seasonal_gdd,
                "last_calculation_date": self.last_calculation_date,
                "last_week_number": self.last_week_number,
                "tracked_daily_min": self.tracked_daily_min,
                "tracked_daily_max": self.tracked_daily_max,
                "daily_temps": self.daily_temps[-48:],  # Keep last 48 hours
            }
            await self.store.async_save(data)
        except Exception as err:
            _LOGGER.error(f"Error saving GDD data: {err}")

    def _get_forecast_temps(self) -> tuple[Optional[float], Optional[float]]:
        """Extract today's min/max from weather forecast if available."""
        try:
            state = self.hass.states.get(self.weather_entity)
            if not state:
                return None, None
                
            # Try to get forecast data
            forecast = state.attributes.get("forecast")
            if not forecast:
                _LOGGER.debug("No forecast data available")
                return None, None
                
            # Look for today's forecast
            today = dt_util.now().date()
            for day_forecast in forecast[:3]:  # Check today and next 2 days
                forecast_date_str = day_forecast.get("datetime")
                if not forecast_date_str:
                    continue
                    
                # Parse forecast date
                try:
                    if "T" in forecast_date_str:
                        forecast_date = datetime.fromisoformat(forecast_date_str.replace("Z", "+00:00")).date()
                    else:
                        forecast_date = datetime.fromisoformat(forecast_date_str).date()
                except ValueError:
                    continue
                
                if forecast_date == today:
                    min_temp = day_forecast.get("templow")
                    max_temp = day_forecast.get("temperature")
                    
                    if min_temp is not None and max_temp is not None:
                        _LOGGER.debug(f"Found forecast temps: min={min_temp}°C, max={max_temp}°C")
                        return float(min_temp), float(max_temp)
                    break
                    
        except Exception as err:
            _LOGGER.debug(f"Error getting forecast temps: {err}")
            
        return None, None

    def _determine_best_min_max(self) -> tuple[Optional[float], Optional[float]]:
        """Determine the best min/max temperatures to use for calculation."""
        
        # Priority 1: Use forecast data if available for today
        forecast_min, forecast_max = self._get_forecast_temps()
        
        # Priority 2: Use tracked temperatures from hourly monitoring
        tracked_min = self.tracked_daily_min
        tracked_max = self.tracked_daily_max
        
        # Decision logic
        if forecast_min is not None and forecast_max is not None:
            # We have good forecast data
            if tracked_min is not None and tracked_max is not None:
                # We have both - use the more extreme values for accuracy
                final_min = min(forecast_min, tracked_min)
                final_max = max(forecast_max, tracked_max)
                _LOGGER.info(f"Using combined forecast+tracked temps: min={final_min}°C, max={final_max}°C")
                return final_min, final_max
            else:
                # Only forecast available
                _LOGGER.info(f"Using forecast temps: min={forecast_min}°C, max={forecast_max}°C")
                return forecast_min, forecast_max
                
        elif tracked_min is not None and tracked_max is not None:
            # Only tracked temperatures available
            _LOGGER.info(f"Using tracked temps: min={tracked_min}°C, max={tracked_max}°C")
            return tracked_min, tracked_max
            
        else:
            # No reliable min/max data
            _LOGGER.warning("No reliable min/max temperature data available")
            return None, None

    def _calculate_gdd_simple_average(self, min_temp: float, max_temp: float) -> float:
        """Calculate GDD using simple average method."""
        avg_temp = (max_temp + min_temp) / 2
        return max(avg_temp - self.base_temp, 0.0)

    def _calculate_gdd_modified_average(self, min_temp: float, max_temp: float) -> float:
        """Calculate GDD using modified average method (cap temps at base)."""
        capped_min = max(min_temp, self.base_temp)
        capped_max = max(max_temp, self.base_temp)
        avg_temp = (capped_max + capped_min) / 2
        return max(avg_temp - self.base_temp, 0.0)

    def _calculate_gdd_single_sine(self, min_temp: float, max_temp: float) -> float:
        """Calculate GDD using single sine method."""
        if max_temp <= self.base_temp:
            return 0.0
        
        if min_temp >= self.base_temp:
            return (max_temp + min_temp) / 2 - self.base_temp
        
        # Sine wave calculation when crossing base temperature
        temp_range = max_temp - min_temp
        if temp_range <= 0:
            return 0.0
            
        theta = math.asin((self.base_temp - min_temp) / temp_range)
        gdd = ((max_temp + min_temp) / 2 - self.base_temp) * (1 - theta / (math.pi / 2)) + \
              (temp_range * math.cos(theta)) / (math.pi / 2)
        
        return max(gdd, 0.0)

    def _calculate_daily_gdd(self, min_temp: float, max_temp: float) -> float:
        """Calculate daily GDD based on selected method."""
        if self.calculation_method == METHOD_SINGLE_SINE:
            return self._calculate_gdd_single_sine(min_temp, max_temp)
        elif self.calculation_method == METHOD_MODIFIED_AVERAGE:
            return self._calculate_gdd_modified_average(min_temp, max_temp)
        else:  # Default to simple average
            return self._calculate_gdd_simple_average(min_temp, max_temp)

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update current temperature and perform daily calculations if needed."""
        try:
            # Get current weather state
            state = self.hass.states.get(self.weather_entity)
            if not state:
                _LOGGER.warning(f"Weather entity {self.weather_entity} not found")
                return self.last_known_data or {}

            # Extract current temperature
            temp = state.attributes.get("temperature")
            if temp is None:
                _LOGGER.warning(f"No temperature attribute in {self.weather_entity}")
                return self.last_known_data or {}

            self.current_temp = float(temp)
            self.daily_temps.append(self.current_temp)
            
            # Update tracked daily min/max from hourly monitoring
            if self.tracked_daily_min is None or self.current_temp < self.tracked_daily_min:
                self.tracked_daily_min = self.current_temp
            if self.tracked_daily_max is None or self.current_temp > self.tracked_daily_max:
                self.tracked_daily_max = self.current_temp

            # Determine best min/max to use
            best_min, best_max = self._determine_best_min_max()
            self.daily_min = best_min
            self.daily_max = best_max

            # Check if we need to do daily calculation
            now = dt_util.now()
            today_str = now.date().isoformat()
            current_week = now.isocalendar().week
            current_year = now.year

            # If it's a new day, calculate yesterday's GDD
            if self.last_calculation_date and today_str != self.last_calculation_date:
                await self._perform_daily_calculation()

            # Weekly reset check
            week_key = f"{current_year}-W{current_week}"
            last_week_key = f"{current_year}-W{self.last_week_number}" if self.last_week_number else None
            
            if last_week_key and week_key != last_week_key:
                _LOGGER.info(f"New week detected: {week_key}, resetting weekly GDD")
                self.weekly_gdd = 0.0

            self.last_calculation_date = today_str
            self.last_week_number = current_week

            # Save data
            await self.async_save()

            # Prepare return data
            data = {
                "current_temp": self.current_temp,
                "tracked_daily_min": self.tracked_daily_min,
                "tracked_daily_max": self.tracked_daily_max,
                "forecast_daily_min": self.forecast_daily_min,
                "forecast_daily_max": self.forecast_daily_max,
                "daily_min": self.daily_min,
                "daily_max": self.daily_max,
                "daily_gdd": self.daily_gdd,
                "weekly_gdd": self.weekly_gdd,
                "seasonal_gdd": self.seasonal_gdd,
            }
            
            self.last_known_data = data
            return data

        except Exception as err:
            _LOGGER.error(f"Error updating GDD data: {err}")
            raise UpdateFailed(f"Error updating GDD data: {err}") from err

    async def _perform_daily_calculation(self):
        """Perform the daily GDD calculation."""
        if self.daily_min is None or self.daily_max is None:
            _LOGGER.warning("No min/max temperature data available for daily calculation")
            return

        # Calculate daily GDD
        daily_gdd = self._calculate_daily_gdd(self.daily_min, self.daily_max)
        
        _LOGGER.info(
            f"Daily GDD calculation: min={self.daily_min:.1f}°C, "
            f"max={self.daily_max:.1f}°C, base={self.base_temp}°C, "
            f"method={self.calculation_method}, result={daily_gdd:.2f}"
        )

        # Update totals
        self.daily_gdd = daily_gdd
        self.weekly_gdd += daily_gdd
        self.seasonal_gdd += daily_gdd

        # Reset daily tracking for new day
        self.tracked_daily_min = self.current_temp
        self.tracked_daily_max = self.current_temp
        self.daily_temps = []

    def reset_all(self):
        """Reset all GDD values."""
        self.daily_gdd = 0.0
        self.weekly_gdd = 0.0
        self.seasonal_gdd = 0.0
        self.tracked_daily_min = None
        self.tracked_daily_max = None
        self.daily_temps = []
        _LOGGER.info("All GDD values reset")

    def set_seasonal_gdd(self, value: float):
        """Manually set seasonal GDD value."""
        self.seasonal_gdd = float(value)
        _LOGGER.info(f"Seasonal GDD manually set to {self.seasonal_gdd}")

    def set_base_temperature(self, base_temp: float):
        """Update base temperature."""
        self.base_temp = float(base_temp)
        _LOGGER.info(f"Base temperature updated to {self.base_temp}°C")

    @property
    def estimated_daily_gdd(self) -> float:
        """Estimate today's GDD based on current best min/max."""
        if self.daily_min is None or self.daily_max is None:
            return 0.0
        return self._calculate_daily_gdd(self.daily_min, self.daily_max)

    @property
    def data_source_info(self) -> dict:
        """Return information about data sources being used."""
        forecast_min, forecast_max = self._get_forecast_temps()
        return {
            "has_forecast_data": forecast_min is not None and forecast_max is not None,
            "has_tracked_data": self.tracked_daily_min is not None and self.tracked_daily_max is not None,
            "using_forecast": self.daily_min == forecast_min if forecast_min is not None else False,
            "using_tracked": self.daily_min == self.tracked_daily_min if self.tracked_daily_min is not None else False,
            "using_combined": self.daily_min not in [forecast_min, self.tracked_daily_min] if all(x is not None for x in [forecast_min, self.tracked_daily_min, self.daily_min]) else False
        }
