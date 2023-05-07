# StromGedacht

> ⚠️ **UNTESTED AND IN DEVELOPMENT**

StromGedacht ist ein Home Assistant Plugin, das den Status des Stromnetzes basierend auf der "StromGedacht API" der Firma TransnetBW GmbH abfragt. Es zeigt den aktuellen Netzstatus sowie Informationen über zukünftige Netzphasen an. Weitere Informationen finden Sie auf der offiziellen Webseite: https://www.stromgedacht.de.

## Status Werte

Die Statuswerte repräsentieren die Netzphasen:

- Status 1 (Grüne Phase): Normalbetrieb, keine speziellen Berücksichtigungen
- Status 2 (Gelbe Phase): Angespannte Situation vorhergesagt; Anstehender Stromverbrauch sollte vorgezogen werden, um Verbrauch in Orange oder Rot zu vermeiden
- Status 3 (Orange Phase): Netzengpass und möglicherweise Strommangel; Verbrauch sollte reduziert werden, um Kosten und CO2 zu sparen
- Status 4 (Rote Phase): Größerer Netzengpass und möglicherweise unzureichende Kapazitäten; Stromverbrauch sollte soweit wie möglich reduziert werden, um die Versorgung abzusichern

## Installation

1. Laden Sie die Dateien `__init__.py` und `power_status.py` aus diesem Repository herunter und speichern Sie sie in einem Ordner namens stromgedacht innerhalb des custom_components Ordners in Ihrem Home Assistant-Konfigurationsverzeichnis. Die Verzeichnisstruktur sollte wie folgt aussehen:
    ```
    .config/
    └── custom_components/
        └── stromgedacht/
            ├── __init__.py
            └── power_status.py

    ```

2. Fügen Sie die folgende Konfiguration zu Ihrer `configuration.yaml`-Datei hinzu:
    ```conf
    sensor:
      - platform: stromgedacht
        zip: YOUR_ZIP_CODE
        next_hours: OPTIONAL_NUMBER_OF_HOURS
    ```
    Ersetzen Sie `YOUR_ZIP_CODE` durch Ihre Postleitzahl und `OPTIONAL_NUMBER_OF_HOURS` (optional) durch die Anzahl der Stunden, für die der höchste Status und die Zeit bis zur nächsten angespannten bzw. entspannten Situation berechnet werden sollen. Wenn `next_hours` nicht angegeben wird, wird der Standardwert von 2 Stunden verwendet.

3. Starten Sie Home Assistant neu.

## Sensor-Entitäten

Nach der Installation und Konfiguration der Integration sollten die folgenden Sensorentitäten in Home Assistant verfügbar sein:

1. `sensor.current_status`: Zeigt den aktuellen Netzstatus an (1-4)
2. `sensor.highest_status_in_next_x_hours`: Zeigt den höchsten Status in den nächsten X Stunden an, wobei X der in `next_hours` angegebene Wert ist
3. `sensor.time_until_next_stress_situation`: Zeigt die verbleibende Zeit (in Sekunden) bis zur nächsten angespannten Situation (Orange oder Rot) an
4. `sensor.time_until_next_relaxed_situation`: Zeigt die verbleibende Zeit (in Sekunden) bis zur nächsten entspannten Situation (Gelb oder Grün) an

## Unterstützung

Wenn Sie Fragen oder Probleme haben, erstellen Sie bitte ein Issue in diesem Repository oder treten Sie der Home Assistant Community bei und stellen Sie Ihre Frage im entsprechenden Forum.
