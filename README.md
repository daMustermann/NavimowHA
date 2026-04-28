# Navimow for Home Assistant

<p align="center">
  <img src="https://fra-navimow-prod.s3.eu-central-1.amazonaws.com/img/navimowhomeassistant.png" width="600">
</p>

Monitor and control Navimow robotic mowers in Home Assistant.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=segwaynavimow&repository=NavimowHA&category=Integration)

## Features

### Mower Control

Control your mower directly from Home Assistant:

- Start mowing
- Pause mowing
- Resume mowing
- Send mower to dock
- Locate mower (beep)
- Restart mower

### Sensors

Keep track of mower status and health:

| Sensor | Unit | Description |
|--------|------|------------|
| Battery | % | Battery level |
| Signal Strength | % | GNSS signal strength |
| Status | text | Current mower status |
| Position X | m | Local map X coordinate |
| Position Y | m | Local map Y coordinate |
| Position Theta | rad | Rotation angle |
| Error Code | text | Error code if any |
| Error Message | text | Error message |
| Work Time | s | Total work time |
| Work Area | m² | Total mowed area |
| Timestamp | time | Last update time |

### Binary Sensors

| Sensor | Description |
|--------|--------------|
| Error | Error active |
| Charging | Currently charging |
| Mowing | Currently mowing |
| Docked | At charging station |

### Switches

| Switch | Description |
|--------|--------------|
| Edge Mowing | Enable edge cutting |
| Rain Mode | Enable rain detection |
| Anti-Theft | Enable theft protection |

### Select

- Cutting Height: 25-80 mm

### Device Tracker

- Real-time position on Home Assistant map (local map coordinates)

### Real-Time Communication

- **MQTT-based real-time communication**
- Fast state updates and reliable device synchronization

### Native Home Assistant Integration

- Native **`lawn_mower` entity**
- Fully compatible with **Home Assistant automations**
- Device and entity model aligned with HA standards

## Prerequisites

- **Warning**: Home Assistant minimum version **2026.1.0**
- **Account**: your Navimow account can sign in to the official app (used for authorization)

## Installation

This integration is not in the default HACS store. You must add it as a custom repository.

This integration will be installed as a custom repository in HACS:

1. HACS → Integrations → top-right menu → **Custom repositories**
2. Repository: `https://github.com/segwaynavimow/NavimowHA`
3. Category: Integration
4. Search for `Navimow` in HACS and install it
5. Restart Home Assistant
6. Settings → Devices & Services → Add Integration → search `Navimow`

## Usage

See the [Getting Started](https://github.com/segwaynavimow/NavimowHA/wiki/Getting-Started).

Once the integration is set up, you can control and monitor your Navimow mower using Home Assistant!

After setup, you will see:

- A `lawn_mower` entity (start/pause/dock/resume)
- Multiple sensors (battery, status, position, etc.)
- Binary sensors (error, charging, mowing, docked)
- Switches (edge_mowing, rain_mode, anti_theft)
- Select (cutting_height)
- Device tracker for map visualization

## Troubleshooting

If you encounter issues with the Navimow integration, please check the Home Assistant logs for error messages. You can also try the following steps:

- Ensure that your mower is connected to your home network and accessible from Home Assistant.
- Restart Home Assistant and check if the issue persists.
- Make sure you are not blocking network access to services in China (if applicable to your environment).
- If you are using DNS filtering/ad-blocking, try disabling it temporarily.

If the problem continues, please file an issue on GitHub and include relevant log snippets:

- `https://github.com/segwaynavimow/NavimowHA/issues`

## Navimow SDK Library

This integration uses `navimow-sdk` to communicate with Navimow mowers. `navimow-sdk` provides the Python API used by this integration (details will be expanded in the SDK documentation).

## Dashboard Cards

Example card configurations for your Home Assistant dashboard:

### Main Control
```yaml
type: entities
entities:
  - entity: lawn_mower.navimow
  - entity: sensor.navimow_battery
  - entity: sensor.navimow_status
  - entity: select.navimow_cutting_height
```

### Map Position
```yaml
type: map
default_zoom: 18
entities:
  - entity: device_tracker.navimow_location
```

### Battery Gauge
```yaml
type: gauge
entity: sensor.navimow_battery
min: 0
max: 100
unit: '%'
```

Full card examples: See `dashboard-cards.yaml` in the component folder.