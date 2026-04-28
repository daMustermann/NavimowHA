# Navimow for Home Assistant (Enhanced Fork)

<p align="center">
  <img src="https://fra-navimow-prod.s3.eu-central-1.amazonaws.com/img/navimowhomeassistant.png" width="600">
</p>

Monitor and control Navimow robotic mowers in Home Assistant with extended features.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=daMustermann&repository=NavimowHA&category=Integration)

---

## What's the Difference?

### Official Integration vs. This Fork

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
| Action buttons | - | ✅ |

This fork adds **12 new sensors**, **4 binary sensors**, **3 switches**, **1 select**, **2 buttons**, and **real-time position tracking**!

---

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Home Assistant                             │
│  ┌─────────────────────────────────────────────┐   │
│  │          Navimow Integration                  │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │ Sensor   │ │ Switch   │ │ Select   │  │   │  │
│  │  │ Platform │ │ Platform │ │ Platform │  │   │  │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘  │   │
│  │       │            │            │         │   │   │
│  │  ┌────┴────────────┴────────────┴────┐   │   │
│  │  │        Coordinator                 │   │   │
│  │  │   (Data Update & Caching)         │   │   │
│  │  └────────────────┬────────────────┘   │   │
│  └───────────────────┼┴─────────────────────────┘   │
│                      │                              │
│  ┌───────────────────▼───────────────────────────┐   │
│  │         NavimowSDK (MQTT + REST)            │   │
│  │  ┌──────────┐   ┌──────────┐                │   │
│  │  │ MQTT    │◄─►│ REST API │                │   │
│  │  │ (live)  │   │ (fallback)│                │   │
│  │  └──────────┘   └──────────┘                │   │
│  └───────────────────┬───────────────────────────┘   │
└──────────────────────┼──────────────────────────────┘
                       │
         ┌──────────────▼──────────���───┐
         │    Navimow Cloud           │
         │  ─────────────────────    │
         │  /openapi/*   MQTT        │
         └──────────────┬──────────────┘
                        │
         ┌──────────────▼──────────┐
         │    Your Mower           │
         │  (local position)       │
         └────────────────────────┘
```

### Data Flow

1. **MQTT (Primary)**: Real-time updates via WebSocket
   - Position (postureX, postureY, postureTheta)
   - Status (mowing, docked, charging, etc.)
   - Battery, signal strength
   - Automatic reconnection

2. **HTTP Fallback**: Polling if MQTT stale (>5 min)
   - API calls to `/openapi/smarthome/getVehicleStatus`
   - Rate limited to once per hour

3. **Controls**: REST API commands
   - Start, Pause, Resume, Dock
   - Set cutting height, switches
   - Locate, Restart

### Key Features Explained

#### Real-Time Position
- Coordinates are **local** to the mowing area (meters from charging station)
- Updates via MQTT every few seconds
- Displayed on HA map card

#### Sensors
All data from MQTT + HTTP is exposed as sensors:
- **Battery** - Current charge level
- **Signal** - GNSS signal quality (%)
- **Status** - Current mower state
- **Position X/Y** - Local coordinates
- **Work Time/Area** - Total statistics
- **Error** - Any active errors

#### Controls
- **Switch**: Edge cutting, Rain mode, Anti-theft
- **Select**: Cutting height (25-80mm)
- **Button**: Locate (beep), Restart

---

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
- Automatic credential refresh on disconnect

---

## Installation

This fork is installed as a custom repository in HACS:

1. HACS → Integrations → top-right menu → **Custom repositories**
2. Repository: `https://github.com/daMustermann/NavimowHA`
3. Category: Integration
4. Search for `Navimow` in HACS and install it
5. Restart Home Assistant
6. Settings → Devices & Services → Add Integration → search `Navimow`

---

## Usage

Once the integration is set up, you will see:

- A `lawn_mower` entity (start/pause/dock/resume)
- **11 sensors** (battery, status, position, signal, work stats, etc.)
- **4 binary sensors** (error, charging, mowing, docked)
- **3 switches** (edge_mowing, rain_mode, anti_theft)
- **1 select** (cutting_height)
- **2 buttons** (locate, restart)
- **Device tracker** for map visualization

---

## Dashboard Cards

Simple card examples:

### Battery Gauge
```yaml
type: gauge
entity: sensor.navimow_YOUR_ID_battery
min: 0
max: 100
unit: '%'
```

### Live Map
```yaml
type: map
entities:
  - device_tracker.navimow_YOUR_ID_location
```

Find your ID in **Developer Tools → States** (search `navimow`).

---

## Troubleshooting

- Check HA logs for errors
- Ensure mower is online and connected
- Restart HA after updates

issues: `https://github.com/daMustermann/NavimowHA/issues`

---

## Navimow SDK

This integration uses `navimow-sdk` from PyPI for MQTT and REST communication.