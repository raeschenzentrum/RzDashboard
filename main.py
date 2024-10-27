from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import yaml
import matplotlib.pyplot as plt
import io
import base64
import sys
import os
from pathlib import Path

# Dynamisch das Hauptverzeichnis hinzufügen
project_root = Path(__file__).resolve().parent.parent
print (project_root)
sys.path.append(str(project_root))

#from app 
import  config
from auth import router as auth_router, get_current_user
from db import fetch_data_dynamically, fetch_data_static
from keyfiles import create_logon_file

app = FastAPI()

# Auth-Router integrieren
app.include_router(auth_router)

# Initialisierung von Templates
templates = Jinja2Templates(directory="app/templates")

# Statische Dateien einbinden
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Konfigurationsdaten laden
tabs_config = config.config['queries']
# HTML login page with JavaScript for authentication
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# Dynamische Dashboard-Route
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "tabs": tabs_config})

# Route zum Erstellen von Key- und Passwortdateien
@app.get("/create_keyfiles", response_class=HTMLResponse)
async def create_keyfiles_page(request: Request):
    systems = config.systems_map.keys()
    return templates.TemplateResponse("create_keyfiles_content.html", {"request": request, "systems": systems})

@app.post("/create_keyfiles", response_class=HTMLResponse)
async def create_keyfiles(tduser: str = Form(...), tdpwd: str = Form(...), system: str = Form(...)):
    success = create_logon_file(tduser, tdpwd, system)
    return HTMLResponse("Keyfile creation successful." if success else "Keyfile creation failed.")

# Dynamische Abfrage-Route
@app.get("/fetch_data", response_class=HTMLResponse)
async def fetch_data(query: str, request: Request, current_user: str = Depends(get_current_user)):
    # Query aus der Konfiguration laden
    query_info = tabs_config.get(query)
    if not query_info:
        return JSONResponse(content={"error": "Invalid query"}, status_code=400)

    # Extrahiere SQL, Template und System/User
    dashboard_type = query_info['type']
    query_string = query_info['sql']
    template_name = query_info['template']
    database_system = query_info['system']
    database_user = query_info['user']
    template_name_content = template_name.replace(".html", "_content.html")
    print(query_string, database_system, database_user)
    # Abfrage je nach Konfiguration statisch oder dynamisch
    if dashboard_type == "Chart":
        data = fetch_data_static(query_string, database_system, database_user)
        # Generiere Diagramme, falls erforderlich
        
        return render_chart_response(data, request)
    else:
        
        data = fetch_data_dynamically(query_string, database_system, database_user)
        if not data['rows']:
            raise HTTPException(status_code=404, detail="No data found")
        
        # Daten im entsprechenden Template rendern
        # template_name_content = template_name + ".html"
        # print(template_name)
        # template_name = "user_sessions.html"

        print("request:",request   )
        # print(templates.TemplateResponse(template_name, {"request": request, "data": data}).body)
        return templates.TemplateResponse(template_name_content, {"request": request, "data": data})

def render_chart_response(data, request):
    print(data)
    if not data:
        raise HTTPException(status_code=404, detail="No data found")

    # Datenbanknamen und -größen für Diagramme extrahieren
    db_names = [row[0] for row in data]
    db_sizes = [row[1] for row in data]

    # Bar Chart generieren
    plt.figure(figsize=(10, 6))
    plt.barh(db_names, db_sizes, color='skyblue')
    plt.xlabel('Database Size (MB)')
    plt.title('Size of DEV Databases (Bar Chart)')
    plt.gca().invert_yaxis()

    # Bar Chart als base64 speichern
    buf_bar = io.BytesIO()
    plt.savefig(buf_bar, format="png")
    plt.close()
    buf_bar.seek(0)
    img_bar = base64.b64encode(buf_bar.read()).decode("utf-8")

    # Pie Chart generieren
    plt.figure(figsize=(8, 8))
    plt.pie(db_sizes, labels=db_names, autopct='%1.1f%%', startangle=140)
    plt.title('Size Distribution of DEV Databases (Pie Chart)')

    # Pie Chart als base64 speichern
    buf_pie = io.BytesIO()
    plt.savefig(buf_pie, format="png")
    plt.close()
    buf_pie.seek(0)
    img_pie = base64.b64encode(buf_pie.read()).decode("utf-8")

    # HTML mit beiden Diagrammen zurückgeben
    html = f"""
    <div>
        <h2>Bar Chart</h2>
        <img src="data:image/png;base64,{img_bar}" />
    </div>
    <div>
        <h2>Pie Chart</h2>
        <img src="data:image/png;base64,{img_pie}" />
    </div>
    """
    print("request:" ,request)
    return HTMLResponse(content=html)

# Funktion zum Erstellen von Diagrammen als Base64-Bilder
def render_chart2(data, chart_type):
    plt.figure(figsize=(6, 4))

    labels = [row[0] for row in data]
    values = [row[1] for row in data]

    # Überprüfe und bereinige die Werte auf numerische Daten
    try:
        values = [float(value) for value in values]  # Konvertiere in float
    except ValueError:
        print("Fehlerhafte Werte in den Daten:", values)
        return None  # Keine Rückgabe, wenn die Daten fehlerhaft sind

    if chart_type == "Bar":
        plt.bar(labels, values)
    elif chart_type == "Pie":
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def render_chart(data, chart_type_config):
    # Nehme an, dass die erste Spalte die Labels und die zweite Spalte die Werte enthält
    labels = [row[0] for row in data]
    values = [row[1] for row in data]
    print("chart_type_config:",chart_type_config)
    chart_type = chart_type_config["Chart"]["ChartType"]

    plt.figure()
    if chart_type == "Bar":
        orientation = chart_type_config["Chart"].get("orientation", "horizontal")
        # orientation =chart_type_config["Chart"]["orientation"]
        color = chart_type_config["Chart"].get("color", "skyblue")
        bar_width = chart_type_config["Chart"].get("bar_width", 0.8)

        if orientation == "horizontal":
            plt.barh(labels, values, color=color, height=bar_width)
            plt.xlabel("Values")
            plt.ylabel("Labels")
        else:
            plt.bar(labels, values, color=color, width=bar_width)
            plt.ylabel("Values")
            plt.xlabel("Labels")
        plt.xticks(rotation=45)  # Optional: Labels schräg setzen
    elif chart_type == "Pie":
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


# def render_chart(data, chart_type_config):
#     labels, values = zip(*data)
#     chart_type = chart_type_config["type"]

#     plt.figure()
#     if chart_type == "Bar":
#         orientation = chart_type_config.get("orientation", "horizontal")
#         color = chart_type_config.get("color", "skyblue")
#         bar_width = chart_type_config.get("bar_width", 0.8)

#         if orientation == "horizontal":
#             plt.barh(labels, values, color=color, height=bar_width)
#             plt.xlabel("Values")
#             plt.ylabel("Labels")
#         else:
#             plt.bar(labels, values, color=color, width=bar_width)
#             plt.ylabel("Values")
#             plt.xlabel("Labels")
#         plt.xticks(rotation=45)  # Optional: Labels schräg setzen
#     elif chart_type == "Pie":
#         plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)

#     buf = io.BytesIO()
#     plt.savefig(buf, format="png")
#     plt.close()
#     buf.seek(0)
#     return base64.b64encode(buf.read()).decode("utf-8")


# def render_chart(data, chart_type):
#     plt.figure(figsize=(6, 4))

#     labels = [row[0] for row in data]
#     values = [float(row[1]) for row in data]  # Werte in Float konvertieren


#     if chart_type == "Bar":
#         plt.bar(labels, values)
#         plt.xticks(rotation=20, ha="right")  # Rotation und Ausrichtung setzen
#     elif chart_type == "Pie":
#         plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)



#     # Speicher das Bild als Base64-encoded string
#     buf = io.BytesIO()
#     plt.savefig(buf, format="png")
#     plt.close()
#     buf.seek(0)
#     return base64.b64encode(buf.getvalue()).decode("utf-8")

def render_table(data):
    # Wenn `data` leer ist, gib eine Meldung zurück
    if not data or 'columns' not in data or 'rows' not in data:
        return "<p>No data available.</p>"

    try:
        # HTML-Tabelle erstellen
        table_html = "<table><thead><tr>"
        # Spaltenüberschriften aus dem `columns`-Schlüssel holen
        for header in data['columns']:
            table_html += f"<th>{header}</th>"
        table_html += "</tr></thead><tbody>"

        # Zeilen aus dem `rows`-Schlüssel holen
        for row in data['rows']:
            table_html += "<tr>"
            for cell in row:
                table_html += f"<td>{cell if cell is not None else ''}</td>"  # None-Werte als leeren String anzeigen
            table_html += "</tr>"

        table_html += "</tbody></table>"
        return table_html

    except (IndexError, AttributeError, TypeError) as e:
        # Bei Fehlern eine Meldung anzeigen und Fehler loggen
        print("Error in render_table:", e)
        return "<p>Error displaying table data.</p>"


    except (IndexError, AttributeError, TypeError) as e:
        # Falls das Format unerwartet ist, Fehlermeldung loggen und anzeigen
        print("Error in render_table:", e)
        return "<p>Error displaying table data.</p>"


# Route für das dynamische Dashboard
@app.get("/dashboard/{board_name}", response_class=HTMLResponse)
async def dynamic_dashboard(request: Request, board_name: str):
    dashboard_config = config.config["dashboards"].get(board_name)
    print ("dashboard_config",dashboard_config)
    # chart_type_config = dashboard_config["ChartType"]
    # print ("chart_type_config",dashboard_config.get("ChartType"))
    # dashboard_config = config.config["dashboards"].get(board_name)
    chart_type = dashboard_config.get("type")
    
    if not dashboard_config or dashboard_config["type"] != "DashBoard":
        return HTMLResponse("Dashboard nicht gefunden oder falscher Typ", status_code=404)

    # Initialisiere die Zeilen und Spalten
    rows = []
    for row_config in dashboard_config["rows"]:
        row_data = []
        for column_config in row_config["columns"]:
            chart_type = column_config["Chart"]["ChartType"]  # Chart-Typ extrahieren
        
            print ("column_config:",column_config)
            if chart_type== "Table":
                # Tabellendaten abrufen und als HTML rendern
                data = fetch_data_dynamically(
                    column_config["sql"], 
                    column_config["system"], 
                    column_config["user"]
                )
                # print (data)
                table_html = render_table(data)
                print (table_html)
                # print (table_html)
                row_data.append({
                    "chartType": chart_type,
                    "container_id": f"{board_name}-{row_config['rownbr']}-{column_config['columnnbr']}",
                    # "img_src": table_html ,
                    "html_content": table_html
                })
            else:
                data = fetch_data_static(column_config["sql"], column_config["system"], column_config["user"])  # Ersetzt dies durch deine Datenabruflogik
                img_src = render_chart(data, column_config)
                row_data.append({
                    "chartType": chart_type,
                    "container_id": f"{board_name}-{row_config['rownbr']}-{column_config['columnnbr']}",
                    "img_src": f"data:image/png;base64,{img_src}"
                })
        rows.append(row_data)

    # Template mit den erstellten Zeilen und Spalten rendern
    return templates.TemplateResponse("dboard.html", {"request": request, "rows": rows})



# if __name__ == "__main__":
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8111, reload=True)

# Laden der Konfiguration aus setup.yaml
with open("app/settings.yaml", "r") as f:
    service = yaml.safe_load(f)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=service["server"]["host"],
        port=service["server"]["port"],
        reload=service["server"]["reload"],
        ssl_keyfile=service["server"]["ssl_keyfile"],
        ssl_certfile=service["server"]["ssl_certfile"]
    )