"""GDD integration setup with improved error handling."""
from __future__ import annotations
import logging

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, DEFAULT_THRESHOLD
from .coordinator import GDDCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up GDD from a config entry."""
    coordinator = GDDCoordinator(hass, entry.data)

    # Load persistent GDD values before first refresh
    await coordinator.async_load()

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error(f"Failed to refresh GDD coordinator: {err}")
        raise ConfigEntryNotReady from err

    # Store coordinator in hass data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Create threshold input_number if it doesn't exist
    await _ensure_threshold_entity(hass)

    # Register services
    await _register_services(hass, coordinator)

    # Forward setup to sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    
    _LOGGER.info(f"GDD integration setup complete for entry {entry.entry_id}")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        
        # Remove services if this was the last entry
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, "reset_all")
            hass.services.async_remove(DOMAIN, "set_seasonal_gdd")
            hass.services.async_remove(DOMAIN, "set_base_temperature")
    
    return unload_ok


async def _ensure_threshold_entity(hass: HomeAssistant) -> None:
    """Ensure the GDD threshold input_number exists."""
    entity_id = "input_number.gdd_threshold"
    
    # Check if entity already exists
    if entity_id in hass.states.async_entity_ids("input_number"):
        _LOGGER.debug("GDD threshold entity already exists")
        return

    try:
        # Create the input_number entity
        await hass.services.async_call(
            "input_number",
            "create",
            {
                "name": "Seasonal GDD Threshold",
                "min": 50,
                "max": 5000,
                "step": 1,
                "mode": "box",
                "initial": DEFAULT_THRESHOLD,
                "unit_of_measurement": "°C·day",
                "icon": "mdi:thermometer",
            },
            blocking=True
        )
        _LOGGER.info(f"Created GDD threshold input_number with default value {DEFAULT_THRESHOLD}")
        
    except Exception as err:
        _LOGGER.warning(f"Could not create GDD threshold input_number: {err}")
        _LOGGER.info("You can manually create input_number.gdd_threshold to set custom thresholds")


async def _register_services(hass: HomeAssistant, coordinator: GDDCoordinator) -> None:
    """Register GDD services."""
    
    async def reset_all_service(call: ServiceCall):
        """Service to reset all GDD values."""
        try:
            coordinator.reset_all()
            await coordinator.async_save()
            await coordinator.async_request_refresh()
            _LOGGER.info("GDD values reset via service call")
        except Exception as err:
            _LOGGER.error(f"Error resetting GDD values: {err}")

    async def set_seasonal_service(call: ServiceCall):
        """Service to manually set seasonal GDD."""
        try:
            value = call.data.get("value")
            if value is None:
                _LOGGER.error("No value provided for set_seasonal_gdd service")
                return
                
            coordinator.set_seasonal_gdd(value)
            await coordinator.async_save()
            await coordinator.async_request_refresh()
            _LOGGER.info(f"Seasonal GDD set to {value} via service call")
        except Exception as err:
            _LOGGER.error(f"Error setting seasonal GDD: {err}")

    async def set_base_temp_service(call: ServiceCall):
        """Service to update base temperature."""
        try:
            value = call.data.get("temperature")
            if value is None:
                _LOGGER.error("No temperature provided for set_base_temperature service")
                return
                
            coordinator.set_base_temperature(value)
            await coordinator.async_save()
            await coordinator.async_request_refresh()
            _LOGGER.info(f"Base temperature set to {value}°C via service call")
        except Exception as err:
            _LOGGER.error(f"Error setting base temperature: {err}")

    # Register services
    hass.services.async_register(DOMAIN, "reset_all", reset_all_service)
    hass.services.async_register(DOMAIN, "set_seasonal_gdd", set_seasonal_service)
    hass.services.async_register(DOMAIN, "set_base_temperature", set_base_temp_service)
    
    _LOGGER.debug("GDD services registered")


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle removal of an entry."""
    # Clean up device registry entry
    device_registry = dr.async_get(hass)
    device = device_registry.async_get_device(
        identifiers={(DOMAIN, entry.entry_id)}
    )
    if device:
        device_registry.async_remove_device(device.id)
        _LOGGER.info(f"Removed GDD device for entry {entry.entry_id}")
