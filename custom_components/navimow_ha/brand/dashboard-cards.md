# Navimow Dashboard Cards

Home Assistant Dashboard Card examples for Navimow mower.

## Quick Setup

Copy the card YAML into your Lovelace dashboard (Edit Dashboard → Add Card → Manual).

## Recommended Cards

### 1. Main Control Card
```yaml
type: entities
title: Navimow
entities:
  - entity: lawn_mower.navimow
  - entity: sensor.navimow_battery
  - entity: sensor.navimow_status
  - type: divider
  - entity: select.navimow_cutting_height
```

### 2. Battery Gauge
```yaml
type: gauge
entity: sensor.navimow_battery
min: 0
max: 100
unit: '%'
```

### 3. Map Position
```yaml
type: map
default_zoom: 18
entities:
  - entity: device_tracker.navimow_location
```

### 4. Controls
```yaml
type: entities
entities:
  - entity: switch.navimow_edge_mowing
  - entity: switch.navimow_rain_mode
  - entity: switch.navimow_anti_theft
  - type: divider
  - entity: button.navimow_locate
  - entity: button.navimow_restart
```

### 5. All Status
```yaml
type: entities
entities:
  - entity: sensor.navimow_status
  - entity: sensor.navimow_signal_strength
  - entity: sensor.navimow_work_time
  - entity: sensor.navimow_work_area
  - entity: binary_sensor.navimow_error
```

## Full Dashboard Example

```yaml
title: Garden
views:
  - title: Garden
    cards:
      - type: gauge
        entity: sensor.navimow_battery
        name: Battery
        min: 0
        max: 100
        unit: '%'
      - type: entities
        title: Mower
        entities:
          - entity: lawn_mower.navimow
          - entity: sensor.navimow_status
          - entity: select.navimow_cutting_height
      - type: map
        title: Position
        default_zoom: 18
        entities:
          - entity: device_tracker.navimow_location
      - type: entities
        title: Settings
        entities:
          - entity: switch.navimow_edge_mowing
          - entity: switch.navimow_rain_mode
          - entity: switch.navimow_anti_theft
```

## Notes

- Replace entity IDs with your actual device ID
- Use **custom:card-modder** card for styling (if available)
- Map card requires `map` card from HA or HACS