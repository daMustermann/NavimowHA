"""Constants for Navimow integration."""
from __future__ import annotations
from typing import Final

DOMAIN: Final = "navimow_ha"

# OAuth2 Configuration
# Authorization URL (user login page). The channel=homeassistant parameter
# is included so that the Navimow web app can redirect back properly.
OAUTH2_AUTHORIZE: Final = (
    "https://navimow-h5-fra.willand.com/smartHome/login?channel=homeassistant"
)

# Token exchange endpoint
OAUTH2_TOKEN: Final = "https://navimow-fra.ninebot.com/openapi/oauth/getAccessToken"

# Token refresh endpoint (Navimow does not support refresh tokens)
OAUTH2_REFRESH: Final | None = None

# OAuth2 client credentials (public, embedded in the official Navimow mobile app)
CLIENT_ID: Final = "homeassistant"
CLIENT_SECRET: Final = "57056e15-722e-42be-bbaa-b0cbfb208a52"

# REST API base URL
API_BASE_URL: Final = "https://navimow-fra.ninebot.com"

# MQTT broker settings (credentials are fetched dynamically from the API)
MQTT_BROKER: Final = "mqtt.navimow.com"
MQTT_PORT: Final = 1883
MQTT_USERNAME: Final | None = None
MQTT_PASSWORD: Final | None = None

# Coordinator polling interval in seconds
UPDATE_INTERVAL: Final = 30

# If no MQTT message has been received within this many seconds, fall back to HTTP polling
MQTT_STALE_SECONDS: Final = 300

# Minimum interval between HTTP fallback requests to avoid hammering the API
HTTP_FALLBACK_MIN_INTERVAL: Final = 3600

# Mapping from mower status strings to HA LawnMowerActivity values
MOWER_STATUS_TO_ACTIVITY = {
    "idle": "docked",
    "mowing": "mowing",
    "paused": "paused",
    "docked": "docked",
    "charging": "docked",
    "returning": "returning",
    "error": "error",
    "unknown": "error",
}
