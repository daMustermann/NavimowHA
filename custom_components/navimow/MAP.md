# Navimow Echtzeit Map - Super Einfach

## Eine Karte (Copy & Paste)

```yaml
type: map
title: Mäher Position
entities:
  - device_tracker.navimow_DEINE_ID_location
default_zoom: 19
```

Fertig!

---

## So findest du DEINE_ID

1. Home Assistant → **Entwicklerwerkzeuge** (unten links)
2. Tab **Zustände**
3. Suche `navimow`
4. Z.B. `sensor.navimow_ABC123_battery` → **ID = ABC123**

---

## Wichtig: Lokale Koordinaten

Die Position ist **lokal** (innerhalb des Mähbereichs in Metern), NICHT GPS!

- X = Position Ost-West (Meter)
- Y = Position Nord-Süd (Meter)
- Theta = Drehwinkel

Für echte GPS-Karte auf Weltkarte brauchst du die Ladestation als Referenzpunkt.

---

## Wenn Map-Karte nicht verfügbar

**Option 1:** HACS installieren → Map Card suchen
**Option 2:** Einfach Sensor-Karten nutzen:

```yaml
type: entities
title: Position
entities:
  - sensor.navimow_DEINE_ID_position_x
  - sensor.navimow_DEINE_ID_position_y
```

---

## Fertig! 🚜