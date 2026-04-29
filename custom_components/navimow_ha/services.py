"""Services for Navimow integration."""

import logging
from typing import Any

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SERVICE_SET_BLADE_HEIGHT = "set_blade_height"

SERVICE_SCHEMA_SET_BLADE_HEIGHT = vol.Schema(
    {
        vol.Required("device_id"): cv.string,
        vol.Required("height"): vol.Coerce(int),
    }
)


def async_setup_services(hass: HomeAssistant, _api: Any) -> None:
    async def _handle_set_blade_height(call: ServiceCall) -> None:
        device_id = call.data["device_id"]
        height = call.data["height"]
        _LOGGER.warning(
            "Blade height change requested via service but REST API does not support it "
            "(device %s, height %s). Use the number entity instead.",
            device_id,
            height,
        )
        raise HomeAssistantError(
            "Setting blade height via the REST API is not supported. "
            "Use the 'Cutting Height' number entity instead."
        )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_BLADE_HEIGHT,
        _handle_set_blade_height,
        schema=SERVICE_SCHEMA_SET_BLADE_HEIGHT,
    )
