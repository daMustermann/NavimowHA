# NavimowHA Agent Instructions

## Repo Structure

Single Home Assistant custom integration in `custom_components/navimow/`. No tests, no linting/typing config.

## Key Commands

- No standard dev commands (no `package.json`, no `pytest`)
- Install as HA custom component via HACS custom repository

## Architecture

- **Entry point**: `__init__.py` - registers OAuth2, sets up MQTT SDK, creates coordinators
- **Config flow**: `config_flow.py` - OAuth2 authentication flow
- **Dependency**: `navimow-sdk>=0.1.2` from PyPI (provides `MowerAPI`, `NavimowSDK`)
- **Platforms**: `lawn_mower` and `sensor` (battery)

## Important Quirks

1. **OAuth2 implementation registration**: Registered in both `async_setup` and `config_flow` due to HA version compatibility requirements
2. **Delayed SDK import**: `mower_sdk` is imported inside `async_setup_entry` to avoid triggering dependency during config_flow loading
3. **MQTT credential refresh**: Automatic on disconnect - the SDK refreshes MQTT credentials when token expires
4. **MQTT debug hooks**: Attached in `__init__.py:172-253` for logging (not a separate component)
5. **Reconnection logic**: SDK uses 40-min keepalive, auto-reconnect with exponential backoff (1-60s)

## HA Version Requirement

As per `hacs.json`: Home Assistant **2026.1.0** or newer

## Release Process

Uses release-please. Version updated in:
- `.release-please-manifest.json`
- `custom_components/navimow/manifest.json`

## Constants Location

All OAuth2/API/MQTT constants in `const.py`:
- `CLIENT_ID`: `homeassistant`
- `CLIENT_SECRET`: `57056e15-722e-42be-bbaa-b0cbfb208a52`
- `API_BASE_URL`: `https://navimow-fra.ninebot.com`
- `MQTT_BROKER`: `mqtt.navimow.com`