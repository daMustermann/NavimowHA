# NavimowHA Agent Instructions

## Repo Location

**Fork**: https://github.com/daMustermann/NavimowHA (original: segwaynavimow/NavimowHA)

## Repo Structure

Single Home Assistant custom integration in `custom_components/navimow_ha/`. No tests, no linting/typing config.

## Key Commands

- No standard dev commands (no `package.json`, no `pytest`)
- Install as HA custom component via HACS custom repository

## Architecture

- **Entry point**: `__init__.py` - registers OAuth2, sets up MQTT SDK, creates coordinators
- **Config flow**: `config_flow.py` - OAuth2 authentication flow
- **Dependency**: `navimow-sdk>=0.1.2` from PyPI — imports as `mower_sdk` (e.g. `from mower_sdk.api import MowerAPI`)
- **Platforms**: `lawn_mower`, `sensor`, `device_tracker`, `binary_sensor`, `number`, `select`, `switch`, `button`

## Important Quirks

1. **OAuth2 implementation registration**: Registered in `async_setup` (for existing entries on restart) and also in `config_flow.py:async_step_user` (for first-time setup before `async_setup` runs)
2. **Delayed SDK import**: `mower_sdk` is imported inside `async_setup_entry` to avoid triggering dependency during config_flow loading
3. **MQTT credential refresh**: On disconnect, `_on_disconnected` in `__init__.py` re-fetches OAuth token and MQTT credentials from the API and calls `sdk.update_mqtt_credentials()`
4. **MQTT debug hooks**: `_attach_mqtt_debug_hooks()` in `__init__.py` patches `on_connected`, `on_ready`, `on_disconnected`, `on_message`, `on_subscribe`, `on_log` onto the SDK's MQTT client for logging
5. **Reconnection logic**: SDK uses 40-min keepalive (`keepalive_seconds=2400`), auto-reconnect with exponential backoff (`reconnect_min_delay=1`, `reconnect_max_delay=60`)

## HA Version Requirement

As per `hacs.json`: Home Assistant **2026.1.0** or newer

## Release Process

Uses release-please. Version updated in:
- `.release-please-manifest.json`
- `custom_components/navimow_ha/manifest.json`

## Constants Location

All OAuth2/API/MQTT constants in `const.py`:
- `CLIENT_ID`: `homeassistant`
- `CLIENT_SECRET`: `57056e15-722e-42be-bbaa-b0cbfb208a52`
- `API_BASE_URL`: `https://navimow-fra.ninebot.com`
- `MQTT_BROKER`: `mqtt.navimow.com`