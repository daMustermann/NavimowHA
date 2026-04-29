"""Config flow for Navimow integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.helpers import config_entry_oauth2_flow

from .auth import NavimowOAuth2Implementation
from .const import (
    API_BASE_URL,
    CLIENT_ID,
    CLIENT_SECRET,
    DOMAIN,
    MQTT_BROKER,
    MQTT_PASSWORD,
    MQTT_PORT,
    MQTT_USERNAME,
)

_LOGGER = logging.getLogger(__name__)


class NavimowOAuth2FlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Handle a Navimow OAuth2 config flow."""

    DOMAIN = DOMAIN
    VERSION = 1

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return _LOGGER

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initiated by the user."""
        # Register the OAuth2 implementation so pick_implementation can find it.
        # This is necessary for first-time setup before async_setup has run.
        config_entry_oauth2_flow.async_register_implementation(
            self.hass,
            DOMAIN,
            NavimowOAuth2Implementation(self.hass, DOMAIN, CLIENT_ID, CLIENT_SECRET),
        )
        return await self.async_step_pick_implementation(user_input)

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> ConfigFlowResult:
        """Perform reauth upon an API authentication error."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Dialog that informs the user that reauth is required."""
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=None,
            )
        return await self.async_step_user()

    async def async_oauth_create_entry(self, data: dict[str, Any]) -> ConfigFlowResult:
        """Create or update the config entry after successful OAuth2 authorisation."""
        if self.source == config_entries.SOURCE_REAUTH:
            existing_entry = self._get_reauth_entry()
            self.hass.config_entries.async_update_entry(
                existing_entry,
                data={**existing_entry.data, **data},
            )
            await self.hass.config_entries.async_reload(existing_entry.entry_id)
            return self.async_abort(reason="reauth_successful")

        return self.async_create_entry(
            title="Navimow",
            data={
                "auth_implementation": DOMAIN,
                **data,
                "api_base_url": API_BASE_URL,
                "mqtt_broker": MQTT_BROKER,
                "mqtt_port": MQTT_PORT,
                "mqtt_username": MQTT_USERNAME,
                "mqtt_password": MQTT_PASSWORD,
            },
        )
