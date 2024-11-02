import os
import json
import binascii
from Crypto.Cipher import AES
from Crypto.Hash import HMAC, SHA256
from Crypto.Util.Padding import unpad
from pathlib import Path
import teradatasql
from datetime import date, datetime
#from keyfiles import get_tdenv
import config 
import pandas as pd

def fetch_data_as_dataframe(query, system, user):
    """
    Führt eine Abfrage auf der Teradata-Datenbank aus und gibt das Ergebnis als pandas DataFrame zurück.
    
    :param query: Die SQL-Abfrage, die auf der Datenbank ausgeführt werden soll
    :param system: Das Teradata-System, mit dem eine Verbindung hergestellt werden soll
    :param user: Der Benutzername für die Datenbankverbindung
    :return: Ein pandas DataFrame mit dem Abfrageergebnis
    """
    # Direkter Aufruf der Funktion `get_connection_with_keyfiles`, die bereits in db.py existiert
    with get_connection_with_keyfiles(system, user).cursor() as cursor:
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        return pd.DataFrame(data, columns=columns)


# Funktion zum Entschlüsseln des Passworts
def decrypt_password(encrypted_password, iv, key, mac, mac_key):
    """Entschlüsselt das Passwort und überprüft den MAC"""
    # MAC überprüfen
    hmac = HMAC.new(mac_key, encrypted_password, digestmod=SHA256)
    try:
        hmac.verify(mac)
    except ValueError:
        raise ValueError("MAC verification failed, file may have been tampered with")

    # Passwort entschlüsseln
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_password = cipher.decrypt(encrypted_password)
    password = unpad(padded_password, AES.block_size)
    return password.decode()

# Funktion zum Lesen der Schlüssel- und Passwortdateien
def read_keyfiles(system, user):
    print(f"Reading keyfiles for {user} on {system}")
    # LOGON_DIR = os.path.join(Path.home(), ".keys")
    LOGON_DIR = config.get_logon_dir()
    key_file = os.path.join(LOGON_DIR, f"{user}-{system}-key.json")
    password_file = os.path.join(LOGON_DIR, f"{user}-{system}-password.json")

    # Lies den Schlüssel, MAC-Schlüssel und Host aus der key.json Datei
    with open(key_file, 'r') as f:
        key_data = json.load(f)
        key = binascii.unhexlify(key_data['key'])
        mac_key = binascii.unhexlify(key_data['mac_key'])
        system = key_data['system']
        host = config.get_tdenv(system)
        username = user

    # Lies die verschlüsselten Passwortdaten aus der password.json Datei
    with open(password_file, 'r') as f:
        password_data = json.load(f)
        iv = binascii.unhexlify(password_data['iv'])
        encrypted_password = binascii.unhexlify(password_data['encrypted_password'])
        mac = binascii.unhexlify(password_data['mac'])

    # Entschlüssele das Passwort
    decrypted_password = decrypt_password(encrypted_password, iv, key, mac, mac_key)

    return host, username, decrypted_password

# Verbindung zur Teradata-Datenbank mit Keyfiles und System
def get_connection_with_keyfiles(system, user):
    host, username, password = read_keyfiles(system, user)
    print(f"Connecting to {system} at host {host} with user {username}")

    # Verwende username, host und entschlüsseltes Passwort zur Verbindung
    return teradatasql.connect(
        host=host,  # Der Host wird jetzt aus der Datei gelesen
        user=username,
        password=password
    )

# Dynamische Abfrage, um Daten und Spaltennamen zurückzugeben
def fetch_data_dynamically(query, system, user):
    with get_connection_with_keyfiles(system, user).cursor() as cursor:
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]  # Spaltennamen extrahieren
        rows = cursor.fetchall()  # Alle Zeilen abrufen
        
        # Serialisieren von Daten: datetime, date und bytes umwandeln
        serialized_rows = []
        for row in rows:
            serialized_row = [
                value.isoformat() if isinstance(value, (date, datetime)) else
                value.decode('utf-8') if isinstance(value, bytes) else value
                for value in row
            ]
            serialized_rows.append(serialized_row)
            # print(serialized_row)

    return {"columns": columns, "rows": serialized_rows}

# Statische Abfrage mit Schlüsseldateien
def fetch_data_static(query, system, user):
    with get_connection_with_keyfiles(system, user).cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()

# Beispielprogramm
if __name__ == "__main__":
    user = input("Enter your DB User: ")
    system = input("Enter your System (e.g. CHBIT01, CHBIT02): ")

    try:
        # Testabfrage, wenn eine Verbindung besteht
        query = "SELECT * FROM DBC.Databases"
        result = fetch_data_dynamically(query, system, user)
        print(result)
    except Exception as e:
        print(f"Error: {e}")


