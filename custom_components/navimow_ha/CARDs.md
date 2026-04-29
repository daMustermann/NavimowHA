# Navimow Dashboard Cards

Ein komplettes, visuell ansprechendes Lovelace-Dashboard für den Navimow Rasenmäher.

## Enthaltene Karten

| Karte | Beschreibung |
|-------|-------------|
| **Titel + Chips** | Status, Batterie, Signal auf einen Blick |
| **SVG Live-Karte** | Animierter Mäher auf dunkel-grünem Rasenhintergrund |
| **Batterie-Gauge** | Nadel-Anzeige + 24h Verlauf (Mini Graph) |
| **Steuerung** | Mähen / Pause / Zurück / Orten — farblich aktiv |
| **Einstellungen** | Schnitthöhe, Kantenmähen, Regenmodus, Diebstahlschutz |
| **Statistiken** | Mähzeit, Fläche, Status, Signal |
| **Fehlerkarte** | Pulsierend sichtbar, nur wenn Fehler aktiv |

## Voraussetzungen (HACS Frontend)

Folgende Cards über **HACS → Frontend** installieren:

| Card | HACS-Name |
|------|-----------|
| Mushroom Cards | \lovelace-mushroom\ |
| Button Card | \lovelace-button-card\ |
| Mini Graph Card | \mini-graph-card\ |
| Card Mod | \lovelace-card-mod\ |

## Installation

1. HACS-Cards installieren und HA neu laden  
2. Geräte-ID herausfinden:  
   **Entwicklerwerkzeuge → Zustände → "navimow" suchen**  
   Beispiel: \sensor.navimow_m550_battery\ → ID = \m550\  
3. In \dashboard-cards.yaml\ alle **\[DEVICE_ID]\** durch deine ID ersetzen  
4. Dashboard → ⋮ → Dashboard bearbeiten → ＋ Ansicht → RAW-Editor  
5. Gesamten Inhalt von \dashboard-cards.yaml\ einfügen → Speichern

## Live-Karte: RANGE anpassen

Die Live-Karte nutzt **lokale Koordinaten** (Meter ab Ladestation, kein GPS).  
Passe den \RANGE\-Wert (Zeile ~80 in \dashboard-cards.yaml\) auf den Radius deines Rasens an:

\\\javascript
const RANGE = 12;  // ← z.B. 8 für kleinen Rasen, 20 für großen Rasen
\\\

## Darstellung der Live-Karte

- 🟡 **Goldener Punkt** = Ladestation (Koordinaten-Ursprung)
- 🟢 **Grüner Kreis** = Mäher → pulsiert beim Mähen
- **Weißes Dreieck** = Fahrtrichtung (basiert auf θ)
- **Kreuzblatt** = rotiert beim Mähen animiert
- **Batterie-Balken** oben rechts auf der Karte
- **Status-Badge** unten auf der Karte
