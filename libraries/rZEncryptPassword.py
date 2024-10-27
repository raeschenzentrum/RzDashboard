import os
import binascii
from Crypto.Cipher import AES
from Crypto.Hash import HMAC, SHA256
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import json
from pathlib import Path
from datetime import datetime

# Pfad für Schlüsseldateien
LOGON_DIR = os.path.join(Path.home(), ".keys")
os.makedirs(LOGON_DIR, exist_ok=True)

# AES-256 Verschlüsselung
def create_key():
    """Erstellt einen zufälligen 256-Bit-Schlüssel und einen MAC-Schlüssel"""
    key = get_random_bytes(32)  # 256-Bit-Schlüssel
    mac_key = get_random_bytes(SHA256.block_size)
    return key, mac_key

def encrypt_password(password, key, mac_key):
    """Verschlüsselt das Passwort mit AES und berechnet einen MAC"""
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv
    padded_password = pad(password.encode(), AES.block_size)
    encrypted_password = cipher.encrypt(padded_password)

    # MAC berechnen
    hmac = HMAC.new(mac_key, encrypted_password, digestmod=SHA256)
    mac = hmac.digest()

    return iv, encrypted_password, mac

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

def save_keyfile(filename, key, mac_key, system):
    """Speichert den Schlüssel, MAC-Schlüssel und das System in einer Datei"""
    key_data = {
        "version": 1,
        "algorithm": "AES",
        "key": binascii.hexlify(key).decode(),
        "mac_key": binascii.hexlify(mac_key).decode(),
        "system": system,  # System speichern
        "match": str(datetime.now())
    }
    filepath = os.path.join(LOGON_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(key_data, f)

def save_passwordfile(filename, iv, encrypted_password, mac, system):
    """Speichert das verschlüsselte Passwort, IV, MAC und System in einer Datei"""
    password_data = {
        "version": 1,
        "iv": binascii.hexlify(iv).decode(),
        "encrypted_password": binascii.hexlify(encrypted_password).decode(),
        "mac": binascii.hexlify(mac).decode(),
        "system": system,  # System speichern
        "match": str(datetime.now())
    }
    filepath = os.path.join(LOGON_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(password_data, f)

def load_keyfile(filename):
    """Lädt den Schlüssel und den MAC-Schlüssel aus einer Datei"""
    filepath = os.path.join(LOGON_DIR, filename)
    with open(filepath, 'r') as f:
        key_data = json.load(f)
    key = binascii.unhexlify(key_data["key"])
    mac_key = binascii.unhexlify(key_data["mac_key"])
    system = key_data["system"]
    return key, mac_key, system

def load_passwordfile(filename):
    """Lädt das verschlüsselte Passwort, IV und MAC aus einer Datei"""
    filepath = os.path.join(LOGON_DIR, filename)
    with open(filepath, 'r') as f:
        password_data = json.load(f)
    iv = binascii.unhexlify(password_data["iv"])
    encrypted_password = binascii.unhexlify(password_data["encrypted_password"])
    mac = binascii.unhexlify(password_data["mac"])
    system = password_data["system"]
    return iv, encrypted_password, mac, system

# Hauptprogramm
if __name__ == "__main__":
    username = input("Enter username: ")
    password = input("Enter password: ")
    system = input("Enter system: ")

    # Erstelle Key und MAC
    key, mac_key = create_key()

    # Passwort verschlüsseln
    iv, encrypted_password, mac = encrypt_password(password, key, mac_key)

    # Dateinamen basierend auf Benutzer und System
    key_filename = f"{username}-{system}-key.json"
    password_filename = f"{username}-{system}-password.json"

    # Speichere Schlüssel und Passwortdateien
    save_keyfile(key_filename, key, mac_key, system)
    save_passwordfile(password_filename, iv, encrypted_password, mac, system)

    print(f"Key file saved as {key_filename}")
    print(f"Password file saved as {password_filename}")

    # Zum Test: Passwort entschlüsseln
    key, mac_key, system_from_key = load_keyfile(key_filename)
    iv, encrypted_password, mac, system_from_password = load_passwordfile(password_filename)
    decrypted_password = decrypt_password(encrypted_password, iv, key, mac, mac_key)
    print(f"Decrypted password: {decrypted_password}")
    print(f"System from key file: {system_from_key}")
    print(f"System from password file: {system_from_password}")
