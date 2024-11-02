from weasyprint import HTML, CSS
import smtplib
import ssl
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
css_path = os.path.join( "static", "css")
import requests
import yaml
from urllib.parse import urljoin
from db import read_keyfiles

# import concurrent.futures
base_url = "https://devine:8441"  # Basis-URL für dein Dashboard

with open("app/settings.yaml", "r") as f:
    service = yaml.safe_load(f)

base_url = service["smtp_server"]["base_url"]
    
# Konfigurationen für den E-Mail-Versand

#os.getenv("EMAIL_PASSWORD")  # Setze Passwort als Umgebungsvariable für Sicherheit
# dashboard_url = "https://devine:8441/dashboard/OpsShiftEarly"  # URL zum Dashboard, das in PDF konvertiert wird

# app.mount("/static", StaticFiles(directory="app/static"), name="static")

def create_dashboard_mail(dashboard_url,
    recipient_email,
    subject,
    body):
    if not dashboard_url.startswith("http"):
        dashboard_url = urljoin(base_url, dashboard_url)
    smtp_server=service["smtp_server"]["smtp_host"]
    smtp_port=service["smtp_server"]["smtp_port"]
    # port = 465  # SMTP-SSL-Port
    smtp_user = service["smtp_server"]["smtp_user"]
    print(f"Reading keys for {smtp_user} on {smtp_server}")
    host, username, decrypted_password = read_keyfiles("smtp_server", smtp_user)
    send_dashboard_pdf_smtp(
        smtp_server=smtp_server,
        port=smtp_port,
        username=smtp_user,
        password=decrypted_password,
        recipient_email=recipient_email,
        subject=subject,
        body=body,
        dashboard_url=dashboard_url
        )

def fetch_with_disabled_ssl(url, output_pdf, output_html):

    
    
    # URL des Dashboards
    # url = "https://devine:8441/dashboard"

    response = requests.get(url, verify=False)
    if response.status_code == 200:
        # Speichere den HTML-Inhalt lokal
        with open(output_html, "wb") as file:
            file.write(response.content)
    else:
        print(f"Fehler beim Abrufen der URL: {response.status_code}")
        return
    css_path = os.path.join(os.path.dirname(__file__), "../static/css/pdf_style_OPS-Shift(Early).css")

    # Konvertiere die lokale HTML-Datei in eine PDF-Datei
    HTML(output_html).write_pdf(
        output_pdf,
        stylesheets=[CSS(css_path)]  # CSS-Datei anwenden
    )
    # HTML(url).write_pdf(output_pdf, presentational_hints=True, url_fetcher=lambda url: {'verify': False})
    # # HTML(string=response.text).write_pdf(output_pdf)
    
def send_dashboard_pdf_smtp(smtp_server, port, username, password, recipient_email, subject, body, dashboard_url):
    # Pfad für die generierte PDF-Datei
    output_pdf = '/tmp/dashboard.pdf'
    output_html = os.path.splitext(output_pdf)[0] + ".html"
#     options = {
#     'ssl_verify_peer': False
# }
    fetch_with_disabled_ssl(dashboard_url, output_pdf, output_html)
    # Dashboard-URL in PDF konvertieren
    # HTML(dashboard_url).write_pdf(output_pdf, presentational_hints=True, **options)
    with open(output_html, "r") as file:
            html_content = file.read()

    # E-Mail erstellen
    message = MIMEMultipart("alternative")
    message["From"] = username
    message["To"] = recipient_email
    message["Subject"] = subject

    # E-Mail-Textinhalt hinzufügen
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)

    # PDF als Anhang hinzufügen
    with open(output_pdf, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {os.path.basename(output_pdf)}",
    )
    message.attach(part)

    # SMTP-Verbindung herstellen und E-Mail senden
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(username, password)
        server.sendmail(username, recipient_email, message.as_string())
    
    print("E-Mail erfolgreich gesendet")    


# Beispielkonfiguration (diese Daten sollten in einer sicheren Konfigurationsdatei gespeichert werden)
# smtp_server = "mail.webkeeper.ch"
# port = 465  # SMTP-SSL-Port
# username = "raesch@raesch.ch"
# password = "dein_passwort"
# recipient_email = "ziel@beispiel.com"
# subject = "Dashboard PDF"
# body = "Im Anhang findest du das aktuelle Dashboard als PDF."
# dashboard_url = "http://your_dashboard_url"

# send_dashboard_pdf_smtp(smtp_server, port, username, password, recipient_email, subject, body, dashboard_url)
