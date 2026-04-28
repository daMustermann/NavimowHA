"""Config flow for Navimow integration."""
from __future__ import annotations
import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_entry_oauth2_flow

from .auth import NavimowOAuth2Implementation
from .const import (
    DOMAIN,
    CLIENT_ID,
    CLIENT_SECRET,
    API_BASE_URL,
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
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

    @property
    def oauth2_implementation(self) -> NavimowOAuth2Implementation:
        """Return the OAuth2 implementation."""
        _LOGGER.debug(
            "Creating OAuth2 implementation for domain=%s, client_id_set=%s, client_secret_set=%s",
            DOMAIN,
            bool(CLIENT_ID),
            bool(CLIENT_SECRET),
        )
        implementation = NavimowOAuth2Implementation(
            self.hass, DOMAIN, CLIENT_ID, CLIENT_SECRET
        )
        # Ensure HA has the implementation registered before redirect/callback.
        config_entry_oauth2_flow.async_register_implementation(
            self.hass, DOMAIN, implementation
        )
        _LOGGER.debug("OAuth2 implementation registered for domain=%s", DOMAIN)
        return implementation

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initiated by the user."""
        _LOGGER.debug("Starting OAuth2 flow: source=%s", self.source)
        # Ensure only a single integration instance is allowed.
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if not CLIENT_ID or not CLIENT_SECRET:
            _LOGGER.error(
                "Missing OAuth2 client configuration: client_id_set=%s, client_secret_set=%s",
                bool(CLIENT_ID),
                bool(CLIENT_SECRET),
            )
            return self.async_abort(
                reason="missing_config",
                description_placeholders={
                    "error": "CLIENT_ID or CLIENT_SECRET not configured. Please configure them in const.py."
                },
            )

        # Ensure the OAuth2 implementation is registered before starting the authorize step.
        _LOGGER.debug("Registering OAuth2 implementation before authorize step")
        _ = self.oauth2_implementation
        _LOGGER.debug("Proceeding to OAuth2 authorize step")
        return await super().async_step_user()

    async def async_step_oauth2_authorize(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Ensure implementation exists before redirect."""
        _LOGGER.debug("Entering oauth2_authorize step")
        # Force register implementation in case HA missed it.
        _ = self.oauth2_implementation
        return await super().async_step_oauth2_authorize(user_input)

    async def async_step_reauth(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Perform reauth upon an API authentication error."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Dialog that informs the user that reauth is required."""
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=None,
            )

        # Only one OAuth2 implementation - proceed directly to the authorize step.
        return await super().async_step_user()

    async def async_oauth_create_entry(self, data: dict[str, Any]) -> FlowResult:
        """Create or update the config entry after successful OAuth2 authorisation."""
        if self.source == config_entries.SOURCE_REAUTH:
            existing_entry = self.entry
            self.hass.config_entries.async_update_entry(
                existing_entry,
                data={
                    **existing_entry.data,
                    **data,
                },
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

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return NavimowOptionsFlowHandler(config_entry)


class NavimowOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Navimow options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=None,
        )
