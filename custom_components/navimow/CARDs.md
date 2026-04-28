# Navimow Cards - Simple Copy & Paste

## Quick Add (5 Minutes)

### Card 1: Battery
```yaml
type: gauge
entity: sensor.navimow_[DEVICE_ID]_battery
min: 0
max: 100
unit: '%'
```

### Card 2: Status
```yaml
type: entities
title: Status
entities:
  - sensor.navimow_[DEVICE_ID]_status
  - sensor.navimow_[DEVICE_ID]_battery
  - sensor.navimow_[DEVICE_ID]_signal_strength
```

### Card 3: Map
```yaml
type: map
entities:
  - device_tracker.navimow_[DEVICE_ID]_location
```

### Card 4: Controls
```yaml
type: entities
title: Controls
entities:
  - select.navimow_[DEVICE_ID]_cutting_height
  - switch.navimow_[DEVICE_ID]_edge_mowing
  - switch.navimow_[DEVICE_ID]_rain_mode
  - button.navimow_[DEVICE_ID]_locate
```

### Card 5: Stats
```yaml
type: entities
title: Stats
entities:
  - sensor.navimow_[DEVICE_ID]_work_time
  - sensor.navimow_[DEVICE_ID]_work_area
```

---

## Find Your Device ID

1. **HA → Developer Tools** (bottom left)
2. **States** tab
3. Search `navimow`
4. Pick any sensor - the middle part = your ID

Example: `sensor.navimow_ABC123456_battery` → **ID = ABC123456**

---

## Replace [DEVICE_ID] with Your ID

| Entity | Replace [DEVICE_ID] with |
|--------|----------------------|
| Battery | `ABC123456_battery` |
| Status | `ABC123456_status` |
| Map | `ABC123456_location` |
| etc... | ... |

That's it! 🎉