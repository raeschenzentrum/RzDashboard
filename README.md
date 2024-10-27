
---

# RzDashboard

**RzDashboard** ist ein leistungsfähiges Dashboard-Projekt, das für die Echtzeit-Datenvisualisierung und Datenverwaltung entwickelt wurde. Die Anwendung basiert auf FastAPI als Web-Framework und bietet Funktionen wie benutzerdefinierte Diagramme, dynamische Dashboards, Datenbankabfragen und erweiterte Authentifizierungsoptionen.

## Inhalt

- [Features](#features)
- [Voraussetzungen](#voraussetzungen)
- [Installation](#installation)
- [Konfiguration](#konfiguration)
- [Starten der Anwendung](#starten-der-anwendung)
- [Deployment](#deployment)
- [Entwicklung](#entwicklung)
- [Lizenz](#lizenz)

## Features

- **Dynamische Dashboards**: Konfigurierbare Tab-Bereiche mit Diagrammen und Tabellen für Echtzeitdaten.
- **Datenbankabfragen**: Echtzeit-Abfragen und -Darstellung von Daten über benutzerdefinierte SQL-Statements.
- **Benutzeranmeldung**: Authentifizierung und Autorisierung basierend auf dem Betriebssystem.
- **Diagrammtypen**: Unterstützt Balkendiagramme, Tortendiagramme, Tabellen und weitere Visualisierungsoptionen.
- **HTTPS-Unterstützung**: Sicherer Zugriff durch HTTPS und SSL-Konfiguration.

## Voraussetzungen

- **Python** >= 3.8
- **Git**
- **Teradata SQL Driver** (falls für Datenbankabfragen benötigt)

## Installation

1. **Repository klonen**:
   ```bash
   git clone https://github.com/raeschenzentrum/RzDashboard.git
   cd RzDashboard
   ```

2. **Virtuelle Umgebung erstellen**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Abhängigkeiten installieren**:
   ```bash
   pip install -r requirements.txt
   ```

## Konfiguration

Die Konfigurationen werden in den YAML-Dateien `config.yaml` und `settings.yaml` gespeichert:

- **config.yaml**: Enthält die Abfragekonfigurationen und Dashboard-Einstellungen, einschließlich SQL-Statements und Diagrammtypen.
- **settings.yaml**: Beinhaltet grundlegende Servereinstellungen wie Host, Port und SSL-Konfigurationen.

### SSL-Einrichtung
Um die Anwendung über HTTPS zu betreiben, müssen die SSL-Zertifikate und -Schlüssel im Verzeichnis `/etc/ssh` hinterlegt werden. Die Pfade zu den Zertifikaten und Schlüsseln werden in der Datei `settings.yaml` konfiguriert. Ein Beispiel:
```yaml
server:
  host: "0.0.0.0"
  port: 8111
  ssl:
    certfile: "/etc/ssh/cert.pem"
    keyfile: "/etc/ssh/key.pem"
directories:
  logon_dir: "/app/.keys"
```

### Beispiel für `config.yaml`:
```yaml
queries:
  CreateKeyfiles:
    type: "CreateKeyfiles"
    url: "/create_keyfiles"
    sql: ""
    template: "create_keyfiles.html"
    system: "TD1720"
    user: "dbc"
    jscript: "create_keyfiles.js"
    container_id: "create-keyfiles-container"
  
  Example(DashBoard):
    type: "Dashboard"
    url: "/dashboard/Example"
    template: "dboard.html"
    container_id: "dboard-Example-container"
    rows:
      - columns:
          - ChartType: "Bar"
            orientation: "horizontal"
            sql: |
              SELECT TRIM(DatabaseName) AS DatabaseName, 
                     SUM(CurrentPerm)/1024/1024 AS DatabaseSize_MB
              FROM DBC.AllSpace 
              WHERE DatabaseName NOT IN ('DBC')
              GROUP BY DatabaseName
              ORDER BY DatabaseSize_MB DESC    
            system: "TD1720"
            user: "dbc"
          - ChartType: "Pie"
            sql: |
              SELECT TRIM(DatabaseName) AS DatabaseName, 
                     SUM(CurrentPerm)/1024/1024 AS DatabaseSize_MB
              FROM DBC.AllSpace 
              WHERE DatabaseName NOT IN ('DBC')
              GROUP BY DatabaseName
              ORDER BY DatabaseSize_MB DESC
            system: "TD1720"
            user: "dbc"
```

### Erläuterung des Dashboard-Beispiels: `Example(DashBoard)`

Dieser Abschnitt konfiguriert das **Example**-Dashboard, das eine visuelle Übersicht der Datenbanknutzung als Beispiel bietet. Das Dashboard beinhaltet eine Zeile (`row`), die zwei Spalten (`columns`) enthält:

- **Erste Spalte**: Ein Balkendiagramm (`ChartType: "Bar"`) zur Anzeige der Speicherplatznutzung der Datenbanken in Megabyte. Der Balken ist horizontal ausgerichtet (`orientation: "horizontal"`).
- **Zweite Spalte**: Ein Tortendiagramm (`ChartType: "Pie"`) zur Darstellung des Speicherplatzanteils pro Datenbank.

## Starten der Anwendung

1. **Lokalen Server starten**:
   ```bash
   python app/main.py
   ```

2. **Zugriff auf die Anwendung**:
   Gehe zu `https://localhost:8111/dashboard` in deinem Webbrowser.

## Menüpunkt `CreateKeyfiles`

Der Menüpunkt `CreateKeyfiles` ermöglicht es, eine Verbindung zur Datenbank herzustellen und Login-Keys zu erstellen. Die gespeicherten Keys ermöglichen später einen schnellen Zugriff auf die Datenbank. Zur Konfiguration dieser Keys:

1. Trage die Verbindungsinformationen (Datenbank-Benutzer und Passwort) im Formular ein und wähle das gewünschte System.
2. Übermittle die Daten, um die Login- und Key-Dateien in dem in `settings.yaml` definierten Verzeichnis `logon_dir` zu speichern.

**Erstellung der Keys**:
- Schlüssel werden erstellt und in dem unter `directories.logon_dir` konfigurierten Verzeichnis gespeichert.

## Deployment

Für das Deployment auf einem Produktionsserver können die folgenden Schritte unternommen werden:

1. Konfiguriere die SSL-Zertifikate in `settings.yaml`.
2. Starte die Anwendung mit einem WSGI-Server (z.B. `gunicorn`):
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --certfile=/etc/ssh/cert.pem --keyfile=/etc/ssh/key.pem
   ```

## Entwicklung

1. **Entwicklungszweig erstellen**:
   ```bash
   git checkout -b develop
   ```

2. **Änderungen committen und pushen**:
   ```bash
   git add .
   git commit -m "Beschreibung der Änderungen"
   git push origin develop
   ```

3. **Neues Release erstellen**:
   Sobald die Entwicklung abgeschlossen ist, kannst du ein neues Release mit einem Tag erstellen:
   ```bash
   git tag -a v1.0.1 -m "Release v1.0.1"
   git push origin v1.0.1
   ```

## Lizenz

Dieses Projekt steht unter der [AGPL-Lizenz](LICENSE).

---

**Hinweis**: Weitere Dokumentation zu spezifischen Abfragen, Benutzerrollen und erweiterten Konfigurationen findest du in der Wiki-Sektion des Repositories.
``` 

