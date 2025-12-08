"""Config flow for GDD integration."""
import voluptuous as vol
from typing import Any, Dict, Optional

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    DOMAIN, CONF_WEATHER, CONF_BASE_TEMP, CONF_CALCULATION_METHOD,
    DEFAULT_BASE, CALCULATION_METHODS, METHOD_SIMPLE_AVERAGE
)


class GDDConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GDD integration."""

    VERSION = 2

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate weather entity exists
            weather_entity = user_input[CONF_WEATHER]
            if weather_entity not in self.hass.states.async_entity_ids("weather"):
                errors[CONF_WEATHER] = "weather_entity_not_found"
            else:
                # Check if weather entity has temperature attribute
                state = self.hass.states.get(weather_entity)
                if state and state.attributes.get("temperature") is None:
                    errors[CONF_WEATHER] = "no_temperature_attribute"
                else:
                    return self.async_create_entry(
                        title="GDD Calculator",
                        data=user_input
                    )

        # Build form schema
        schema = vol.Schema({
            vol.Required(CONF_WEATHER): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain="weather",
                    multiple=False
                )
            ),
            vol.Required(CONF_BASE_TEMP, default=DEFAULT_BASE): vol.All(
                vol.Coerce(float),
                vol.Range(min=-10.0, max=50.0)
            ),
            vol.Required(CONF_CALCULATION_METHOD, default=METHOD_SIMPLE_AVERAGE): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"value": method, "label": label}
                        for method, label in CALCULATION_METHODS.items()
                    ]
                )
            ),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "base_temp_info": "Base temperature is the minimum temperature for plant growth (typically 10-15°C for most crops)"
            }
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow."""
        return GDDOptionsFlow(config_entry)


class GDDOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for GDD integration."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: Optional[Dict[str, Any]] = None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            # Validate weather entity if changed
            weather_entity = user_input.get(CONF_WEATHER, self.config_entry.data[CONF_WEATHER])
            if weather_entity not in self.hass.states.async_entity_ids("weather"):
                errors[CONF_WEATHER] = "weather_entity_not_found"
            else:
                state = self.hass.states.get(weather_entity)
                if state and state.attributes.get("temperature") is None:
                    errors[CONF_WEATHER] = "no_temperature_attribute"
                else:
                    # Update config entry data
                    new_data = {**self.config_entry.data, **user_input}
                    self.hass.config_entries.async_update_entry(
                        self.config_entry,
                        data=new_data
                    )
                    return self.async_create_entry(title="", data={})

        # Current values
        current_weather = self.config_entry.data.get(CONF_WEATHER, "")
        current_base = self.config_entry.data.get(CONF_BASE_TEMP, DEFAULT_BASE)
        current_method = self.config_entry.data.get(CONF_CALCULATION_METHOD, METHOD_SIMPLE_AVERAGE)

        schema = vol.Schema({
            vol.Required(CONF_WEATHER, default=current_weather): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain="weather",
                    multiple=False
                )
            ),
            vol.Required(CONF_BASE_TEMP, default=current_base): vol.All(
                vol.Coerce(float),
                vol.Range(min=-10.0, max=50.0)
            ),
            vol.Required(CONF_CALCULATION_METHOD, default=current_method): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"value": method, "label": label}
                        for method, label in CALCULATION_METHODS.items()
                    ]
                )
            ),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "current_values": f"Current: Base={current_base}°C, Method={CALCULATION_METHODS.get(current_method, 'Unknown')}"
            }
        )
