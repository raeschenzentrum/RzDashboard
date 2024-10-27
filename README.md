
# RzDashboard

**RzDashboard** ist ein leistungsstarkes und konfigurierbares Dashboard-Projekt, das Echtzeit-Datenvisualisierung und Datenbankverwaltung ermöglicht. Entwickelt mit FastAPI, unterstützt es die Darstellung von Diagrammen, Tabellen und dynamischen Dashboards basierend auf SQL-Abfragen und erlaubt eine einfache Konfiguration durch YAML-Dateien.

## Inhalt

- [Features](#features)
- [Voraussetzungen](#voraussetzungen)
- [Installation](#installation)
- [Konfiguration](#konfiguration)
  - [Dashboards Beispiel](#dashboards-beispiel)
- [Starten der Anwendung](#starten-der-anwendung)
- [Deployment](#deployment)
- [Entwicklung](#entwicklung)
- [Lizenz](#lizenz)

## Features

- **Dynamische Dashboards**: Konfigurierbare Tabs und individuelle Daten-Dashboards.
- **Datenbankabfragen**: SQL-basierte Datenabfragen zur Echtzeit-Datenvisualisierung.
- **Mehrere Diagrammtypen**: Darstellung von Balken- und Tortendiagrammen sowie Tabellen.
- **Benutzeranmeldung**: Authentifizierung über Betriebssystem-Logins.
- **HTTPS-Unterstützung**: Sichere Verbindungen über HTTPS mit benutzerdefinierbaren SSL-Zertifikaten.

## Voraussetzungen

- **Python** >= 3.8
- **Git**
- **Teradata SQL Driver** (für die Teradata-Integration)
- **SSL-Schlüssel** für HTTPS

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

Das Dashboard und die Anwendungsparameter werden über die Konfigurationsdateien `config.yaml` und `settings.yaml` gesteuert.

### `settings.yaml` Beispiel:

- **server**: Legt die Netzwerkkonfiguration und den Speicherort der SSL-Zertifikate fest.
- **directories**: Gibt den Ordner für zusätzliche Konfigurationsdateien und Schlüssel an.

```yaml
server:
  host: "0.0.0.0"
  port: 8111
  ssl:
    certfile: "/etc/ssh/cert.pem"
    keyfile: "/etc/ssh/key.pem"

directories:
  logon_dir: "/etc/rzdashboard/.keys"
```

> **Hinweis**: Die in `settings.yaml` definierten SSL-Zertifikate sollten in `/etc/ssh` gespeichert und für die Anwendung konfiguriert werden. Alternativ können die SSL-Dateien an einem anderen Ort gespeichert werden; dieser Speicherort muss dann in `settings.yaml` angepasst werden.

### `config.yaml` Beispiel für Dashboards

In der `config.yaml`-Datei werden die verschiedenen Tabs und Dashboards definiert. Jeder Eintrag kann verschiedene Typen von Datenvisualisierungen umfassen, wie z. B. Diagramme oder Tabellen, sowie SQL-Abfragen zur Datenbeschaffung.

```yaml
dashboards:
  Example:
    type: "Dashboard"
    url: "/dashboard/Example"
    template: "dboard.html"
    container_id: "dboard-Example-container"
    rows:
      - rownbr: 1
        columns:
          - columnnbr: 1
            ChartType: "Bar"
            options:
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
          - columnnbr: 2
            ChartType: "Pie"
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

In diesem Beispiel wird ein **Dashboard**-Tab mit zwei Spalten konfiguriert:
- **Spalte 1** zeigt ein horizontales Balkendiagramm der Datenbankgrößen an.
- **Spalte 2** zeigt ein Tortendiagramm an.

Die Spalten- und Zeilenanzahl sowie der Diagrammtyp sind flexibel und können für jeden Eintrag individuell angepasst werden.

## Starten der Anwendung

1. **Lokalen Server starten**:
   ```bash
   python app/main.py
   ```

2. **Zugriff auf die Anwendung**:
   Öffne `https://localhost:8111/dashboard` im Webbrowser.

## Deployment

Für die Bereitstellung in einer Produktionsumgebung sollten die SSL-Zertifikate für eine sichere HTTPS-Verbindung aktiviert und konfiguriert werden.

1. **SSL-Zertifikate sicherstellen**: Stelle sicher, dass die in `settings.yaml` angegebenen Zertifikate existieren und lesbar sind.

2. **Start mit WSGI-Server (z. B. `gunicorn`)**:
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --certfile=/etc/ssh/cert.pem --keyfile=/etc/ssh/key.pem
   ```

## Entwicklung

1. **Neuen Entwicklungszweig erstellen**:
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
   Sobald die Entwicklung abgeschlossen ist, kann ein neues Release erstellt werden:
   ```bash
   git tag -a v1.0.1 -m "Release v1.0.1"
   git push origin v1.0.1
   ```

## Lizenz

Dieses Projekt steht unter der [AGPL-Lizenz](LICENSE).

---

**Hinweis**: Für spezifische Abfragen, Benutzerrollen und erweiterte Konfigurationen wird die Dokumentation im Wiki des Repositories weiter detailliert.
``` 

Diese Datei gibt einen umfassenden Überblick über das Projekt, die Konfiguration, und die Schritte für die Entwicklung und Bereitstellung.RzDashboard