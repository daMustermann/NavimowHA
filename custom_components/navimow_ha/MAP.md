# Navimow Live-Karte

## Koordinatensystem

Die Position (X/Y) vom Navimow ist **lokal** in Metern ab der Ladestation — **kein GPS**.

| Wert | Bedeutung |
|------|-----------|
| X | Ost (+) / West (-) in Metern |
| Y | Nord (+) / Süd (-) in Metern |
| θ (Theta) | Ausrichtung in Radiant |

Ursprung (0, 0) = Ladestation.

## SVG Live-Karte (in dashboard-cards.yaml)

Die enthaltene SVG-Karte zeigt:
- Ladestation als goldenen ⚡-Punkt in der Mitte
- Mäher als farbigen Kreis mit Richtungspfeil
- Pulsierende Animation während des Mähens
- Rotierende Klinge während des Mähens
- Batterie-Balken und Positionsanzeige direkt auf der Karte

### RANGE anpassen

In \dashboard-cards.yaml\ (ca. Zeile 80):

\\\javascript
const RANGE = 12;  // Radius in Metern
\\\

Wähle den Wert passend zu deinem Rasen:
- Kleiner Rasen (< 100 m²): \RANGE = 6\
- Mittlerer Rasen (~300 m²): \RANGE = 12\
- Großer Rasen (> 500 m²): \RANGE = 20\

## Echte GPS-Karte

Falls der Mäher echte GPS-Koordinaten liefert (zukünftige SDK-Version),
wird der Standard-HA-Kartentyp automatisch funktionieren:

\\\yaml
type: map
entities:
  - device_tracker.navimow_[DEVICE_ID]_location
default_zoom: 19
\\\

Aktuell meldet \device_tracker\ die lokalen X/Y-Werte als Lat/Lon — 
dies platziert den Mäher zwar an einem willkürlichen Weltkartenort,
ist aber für die native HA-Karte funktional (Bewegung ist sichtbar).
