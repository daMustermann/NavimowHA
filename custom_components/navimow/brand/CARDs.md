# Navimow Dashboard Cards - Simple & Ready to Use

## Install Steps

1. Open Home Assistant
2. Go to **Dashboard** (or **Overview**)
3. Click **Edit Dashboard** (3 dots → Edit Dashboard)
4. Click **Add Card** → Search **Manual**
5. Copy the card YAML below

---

## Card 1: Battery (Quick View)
```yaml
type: gauge
entity: sensor.navimow_[YOUR_ID]_battery
min: 0
max: 100
unit: '%'
```

---

## Card 2: Status Overview
```yaml
type: entities
title: Mower Status
entities:
  - entity: sensor.navimow_[YOUR_ID]_status
  - entity: sensor.navimow_[YOUR_ID]_battery
  - entity: sensor.navimow_[YOUR_ID]_signal_strength
```

---

## Card 3: Live Map Position
```yaml
type: map
title: Position
default_zoom: 19
entities:
  - entity: device_tracker.navimow_[YOUR_ID]_location
```

---

## Card 4: All Controls
```yaml
type: entities
title: Controls
entities:
  - entity: select.navimow_[YOUR_ID]_cutting_height
  - entity: switch.navimow_[YOUR_ID]_edge_mowing
  - entity: switch.navimow_[YOUR_ID]_rain_mode
  - entity: switch.navimow_[YOUR_ID]_anti_theft
  - type: divider
  - entity: button.navimow_[YOUR_ID]_locate
```

---

## Card 5: Stats
```yaml
type: entities
title: Statistics
entities:
  - entity: sensor.navimow_[YOUR_ID]_work_time
  - entity: sensor.navimow_[YOUR_ID]_work_area
  - entity: binary_sensor.navimow_[YOUR_ID]_mowing
  - entity: binary_sensor.navimow_[YOUR_ID]_charging
```

---

## How to Find Your Device ID

1. Go to **Developer Tools** → **States**
2. Search for `navimow`
3. Look for `sensor.navimow_..._battery`
4. The middle part is your device ID

Example: `sensor.navimow_AB123XYZ_battery` → Device ID = `AB123XYZ`

---

## Entity List (Replace YOUR_ID)

| What | Entity |
|------|--------|
| Main Control | `lawn_mower.navimow_YOUR_ID` |
| Battery | `sensor.navimow_YOUR_ID_battery` |
| Status | `sensor.navimow_YOUR_ID_status` |
| Signal | `sensor.navimow_YOUR_ID_signal_strength` |
| Position X | `sensor.navimow_YOUR_ID_position_x` |
| Position Y | `sensor.navimow_YOUR_ID_position_y` |
| Work Time | `sensor.navimow_YOUR_ID_work_time` |
| Work Area | `sensor.navimow_YOUR_ID_work_area` |
| Mowing | `binary_sensor.navimow_YOUR_ID_mowing` |
| Charging | `binary_sensor.navimow_YOUR_ID_charging` |
| Docked | `binary_sensor.navimow_YOUR_ID_docked` |
| Error | `binary_sensor.navimow_YOUR_ID_error` |
| Cut Height | `select.navimow_YOUR_ID_cutting_height` |
| Edge | `switch.navimow_YOUR_ID_edge_mowing` |
| Rain | `switch.navimow_YOUR_ID_rain_mode` |
| Anti-Theft | `switch.navimow_YOUR_ID_anti_theft` |
| Locate | `button.navimow_YOUR_ID_locate` |
| Restart | `button.navimow_YOUR_ID_restart` |
| Tracker | `device_tracker.navimow_YOUR_ID_location` |

---

## Note
Replace `YOUR_ID` with your actual device ID (found in Developer Tools → States)