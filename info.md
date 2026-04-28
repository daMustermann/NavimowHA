# Navimow for Home Assistant (Enhanced Fork)

Monitor and control Navimow robotic mowers in Home Assistant with extended features.

## What's Different?

| Feature | Official | This Fork |
|---------|----------|----------|
| `lawn_mower` entity | ✅ | ✅ |
| Battery sensor | ✅ | ✅ |
| Status sensor | - | ✅ |
| Signal strength | - | ✅ |
| Position tracking | - | ✅ |
| Map visualization | - | ✅ |
| Binary sensors | - | ✅ |
| Switch controls | - | ✅ |
| Cutting height | - | ✅ |
| Buttons | - | ✅ |

## Features

- **Extended Sensors**: 11 sensors (battery, status, position, signal, work time/area, etc.)
- **Binary Sensors**: Error, charging, mowing, docked
- **Switches**: Edge mowing, rain mode, anti-theft
- **Select**: Cutting height (25-80mm)
- **Buttons**: Locate (beep), restart
- **Device Tracker**: Live position on map

## Architecture

```
HA → Navimow Integration → NavimowSDK → MQTT ←→ REST API ←→ Navimow Cloud ←→ Mower
```

- **MQTT**: Real-time updates (primary)
- **HTTP**: Fallback when MQTT stale

## Prerequisites

- Home Assistant **2026.1.0** or newer
- Navimow account

## Installation

1. HACS → Integrations → Custom repositories
2. Add: `https://github.com/daMustermann/NavimowHA`, Category: **Integration**
3. Search **Navimow** in HACS and install
4. Restart Home Assistant
5. Settings → Devices & Services → Add Integration → search **Navimow**

## How It Works

1. **OAuth2**: Authenticate with Navimow cloud
2. **MQTT**: Real-time WebSocket connection for live updates
3. **HTTP Fallback**: Polls API if MQTT connection lost >5 min
4. **Controls**: Send commands via REST API

## Troubleshooting

- Check HA logs
- Restart HA after updates
- Issues: https://github.com/daMustermann/NavimowHA/issues

---

*Enhanced fork of the official Navimow integration.*