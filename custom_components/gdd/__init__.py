"""GDD integration setup with improved error handling."""
from __future__ import annotations
import logging

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.event import async_track_state_change_event

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
    
    # Create control helpers for frontend interaction
    await _ensure_control_helpers(hass)

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
            hass.services.async_remove(DOMAIN, "record_mowing")
            _LOGGER.debug("GDD services removed")
    
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


async def _ensure_control_helpers(hass: HomeAssistant) -> None:
    """Ensure the GDD control helper entities exist."""
    
    # GDD Threshold Control Helper
    threshold_control_id = "input_number.gdd_threshold_control"
    if threshold_control_id not in hass.states.async_entity_ids("input_number"):
        try:
            await hass.services.async_call(
                "input_number",
                "create",
                {
                    "name": "GDD Threshold Control",
                    "min": 50,
                    "max": 5000,
                    "step": 10,
                    "mode": "slider",
                    "initial": 300,  # Good default for turf
                    "unit_of_measurement": "°C·day",
                    "icon": "mdi:target",
                },
                blocking=True
            )
            _LOGGER.info("Created GDD threshold control helper")
        except Exception as err:
            _LOGGER.warning(f"Could not create GDD threshold control helper: {err}")
    
    # Base Temperature Control Helper
    base_temp_control_id = "input_number.gdd_base_temp_control"
    if base_temp_control_id not in hass.states.async_entity_ids("input_number"):
        try:
            await hass.services.async_call(
                "input_number",
                "create",
                {
                    "name": "GDD Base Temperature Control",
                    "min": 0,
                    "max": 25,
                    "step": 0.5,
                    "mode": "slider",
                    "initial": 14,
                    "unit_of_measurement": "°C",
                    "icon": "mdi:thermometer",
                },
                blocking=True
            )
            _LOGGER.info("Created GDD base temperature control helper")
        except Exception as err:
            _LOGGER.warning(f"Could not create GDD base temperature control helper: {err}")
    
    # Turf Type Helper
    turf_type_id = "input_select.gdd_turf_type"
    if turf_type_id not in hass.states.async_entity_ids("input_select"):
        try:
            await hass.services.async_call(
                "input_select",
                "create",
                {
                    "name": "GDD Turf Type",
                    "options": ["cool_season", "warm_season"],
                    "initial": "cool_season",
                    "icon": "mdi:grass",
                },
                blocking=True
            )
            _LOGGER.info("Created GDD turf type helper")
        except Exception as err:
            _LOGGER.warning(f"Could not create GDD turf type helper: {err}")

    # Maintenance Level Helper
    maintenance_id = "input_select.gdd_maintenance_level"
    if maintenance_id not in hass.states.async_entity_ids("input_select"):
        try:
            await hass.services.async_call(
                "input_select",
                "create",
                {
                    "name": "GDD Maintenance Level",
                    "options": ["low_maintenance", "medium_maintenance", "high_maintenance"],
                    "initial": "medium_maintenance",
                    "icon": "mdi:cog",
                },
                blocking=True
            )
            _LOGGER.info("Created GDD maintenance level helper")
        except Exception as err:
            _LOGGER.warning(f"Could not create GDD maintenance level helper: {err}")
    
    # Setup sync automations
    await _setup_control_sync(hass)


async def _setup_control_sync(hass: HomeAssistant) -> None:
    """Setup synchronization between control helpers and integration."""
    
    async def sync_threshold_to_main(call):
        """Sync threshold control to main threshold."""
        control_state = hass.states.get("input_number.gdd_threshold_control")
        if control_state:
            try:
                await hass.services.async_call(
                    "input_number",
                    "set_value",
                    {
                        "entity_id": "input_number.gdd_threshold",
                        "value": float(control_state.state)
                    },
                    blocking=False
                )
            except Exception as err:
                _LOGGER.error(f"Error syncing threshold to main: {err}")

    async def sync_threshold_from_main(call):
        """Sync main threshold to control."""
        main_state = hass.states.get("input_number.gdd_threshold")
        if main_state:
            try:
                await hass.services.async_call(
                    "input_number",
                    "set_value",
                    {
                        "entity_id": "input_number.gdd_threshold_control", 
                        "value": float(main_state.state)
                    },
                    blocking=False
                )
            except Exception as err:
                _LOGGER.error(f"Error syncing threshold from main: {err}")

    async def sync_base_temperature(call):
        """Sync base temperature control to integration."""
        control_state = hass.states.get("input_number.gdd_base_temp_control")
        if control_state:
            try:
                # Find the GDD coordinator
                gdd_data = hass.data.get(DOMAIN, {})
                for coordinator in gdd_data.values():
                    if hasattr(coordinator, 'set_base_temperature'):
                        coordinator.set_base_temperature(float(control_state.state))
                        await coordinator.async_save()
                        await coordinator.async_request_refresh()
                        break
            except Exception as err:
                _LOGGER.error(f"Error syncing base temperature: {err}")

    # Register state change listeners
    async def threshold_control_changed(entity_id, old_state, new_state):
        if new_state and old_state and new_state.state != old_state.state:
            await sync_threshold_to_main(None)

    async def threshold_main_changed(entity_id, old_state, new_state):
        if new_state and old_state and new_state.state != old_state.state:
            await sync_threshold_from_main(None)

    async def base_temp_changed(entity_id, old_state, new_state):
        if new_state and old_state and new_state.state != old_state.state:
            await sync_base_temperature(None)

    # Setup listeners
    async_track_state_change_event(
        hass,
        "input_number.gdd_threshold_control",
        threshold_control_changed
    )
    
    async_track_state_change_event(
        hass,
        "input_number.gdd_threshold", 
        threshold_main_changed
    )
    
    async_track_state_change_event(
        hass,
        "input_number.gdd_base_temp_control",
        base_temp_changed
    )
    
    _LOGGER.debug("GDD control synchronization setup complete")


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

    async def record_mowing_service(call: ServiceCall):
        """Service to record mowing event."""
        try:
            coordinator.record_mowing()
            await coordinator.async_save()
            _LOGGER.info("Mowing event recorded via service call")
        except Exception as err:
            _LOGGER.error(f"Error recording mowing event: {err}")

    # Register services
    hass.services.async_register(DOMAIN, "reset_all", reset_all_service)
    hass.services.async_register(DOMAIN, "set_seasonal_gdd", set_seasonal_service)
    hass.services.async_register(DOMAIN, "set_base_temperature", set_base_temp_service)
    hass.services.async_register(DOMAIN, "record_mowing", record_mowing_service)
    
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
