import os
from pathlib import Path
import libraries.rZEncryptPassword as rz
import config 


# Hauptfunktion zur Erstellung des Logonfiles mit der neuen RZEncryptPassword-Bibliothek
def create_logon_file(tduser, tdpwd, system):
    tdenv = config.get_tdenv(system)
    filename = f"{tduser}-{system}"

    # LogonDir sicherstellen
    logon_dir = config.get_logon_dir()
    Path(logon_dir).mkdir(parents=True, exist_ok=True)

    # Pfade für die Schlüsseldateien definieren
    key_filename = f"{filename}-key.json"
    password_filename = f"{filename}-password.json"
    
    # RZEncryptPassword-Funktionen verwenden, um die Dateien zu erstellen
    key, mac_key = rz.create_key()
    iv, encrypted_password, mac = rz.encrypt_password(tdpwd, key, mac_key)

    # Dateien speichern
    rz.save_keyfile(key_filename, key, mac_key,system)
    rz.save_passwordfile(password_filename, iv, encrypted_password, mac,system)

    # Erfolgsmeldung
    print(f"Keyfiles successfully created in {logon_dir}")

    return True

# Beispielaufruf der Funktion (dies könnte in FastAPI später durch eine API-Route ersetzt werden)
if __name__ == "__main__":
    tduser = input("Enter your DB User: ")
    tdpwd = input("Enter your Password: ")
    system = input("Enter the System (CHBIT01, CHBIT02, CHBIT07, CHBIT08, TD1720): ")

    success = create_logon_file(tduser, tdpwd, system)
    if success:
        print("Keyfile creation successful.")
    else:
        print("Keyfile creation failed.")
