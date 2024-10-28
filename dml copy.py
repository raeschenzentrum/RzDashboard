import pandas as pd
from db import fetch_data_as_dataframe, get_connection_with_keyfiles
from datetime import datetime

def manipulate_data():
    # Variablen für Teradata-System und User
    system = "TD1710"
    user = "dbc"

    # Namen der Tabellen
    original_table = "DEVOPS_CONTROL.PROZ_Prozess"
    backup_table = f"{original_table}_backup_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Verbindung zu Teradata herstellen
    con = get_connection_with_keyfiles(system, user)

    # Erstellen der Backuptabelle
    with con.cursor() as cursor:
        cursor.execute(f"CREATE TABLE {backup_table} AS {original_table} WITH DATA;")
        print(f"Backup table '{backup_table}' created successfully.")

    # Daten der Originaltabelle als DataFrame laden
    query = f"SELECT * FROM {original_table};"
    data = fetch_data_as_dataframe(query, system, user)

    # Dictionary für konsistente Ersetzung von Großbuchstabenkombinationen
    replacements = {}

    def transform_text(text):
        # Behalten des ersten Teils (vor dem ersten Unterstrich) und iterieren durch die Unterstrich-getrennten Teile
        parts = text.split('_')
        transformed_parts = [parts[0]]

        for part in parts[1:]:
            # Prüfen, ob Teil nur Großbuchstaben enthält und konsistente Ersetzung
            if part.isupper():
                if part not in replacements:
                    # Erzeugen einer Ersetzung durch Rotation der Buchstaben
                    replacements[part] = ''.join(chr(((ord(c) - 65 + 3) % 26) + 65) for c in part)  # Buchstaben um 3 Positionen rotieren
                transformed_parts.append(replacements[part])
            else:
                transformed_parts.append(part)

        return '_'.join(transformed_parts)

    # Transformation auf die benötigte Spalte anwenden, wenn kein "Loadverrechung" enthalten ist
    data['PROZ_Prozessname'] = data['PROZ_Prozessname'].apply(lambda x: x if 'Loadverrechung' in x else transform_text(x))

    # Originaltabelle leeren
    delete_query = f"DELETE FROM {original_table};"
    with con.cursor() as cursor:
        cursor.execute(delete_query)

    # Konvertiere DataFrame-Zeilen in Listen von Tupeln für das Einfügen
    rows_to_insert = data.to_records(index=False).tolist()
    
    # Generiere das INSERT-Statement
    columns = ', '.join(data.columns)
    placeholders = ', '.join(['?'] * len(data.columns))  # Platzhalter für Teradata
    insert_query = f"INSERT INTO {original_table} ({columns}) VALUES ({placeholders});"
    
    # Füge Daten mit `executemany` ein
    with con.cursor() as cursor:
        cursor.executemany(insert_query, rows_to_insert)
    print(f"Table '{original_table}' updated successfully.")
