import yaml, os
from pathlib import Path
# Lese Konfigurationsdatei ein
config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
# def load_config():
#     with open("config.yaml", "r") as f:
#         return yaml.safe_load(f)
# def load_config():
#     config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
#     with open(config_path, "r") as f:
#         return yaml.safe_load(f)
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
        
config = load_config()
# database_system = config["database"]["system"]
# database_user = config["database"]["user"]
systems_map = config["systems"]

# Funktion zum Abrufen der Umgebungsadresse basierend auf dem System
def get_tdenv(system):
    return systems_map.get(system, "UNKNOWN_SYSTEM")

def get_logon_dir(): 
# Konfigurationsdatei laden
    settings_path = os.path.join(os.path.dirname(__file__), "settings.yaml")
    with open(settings_path, "r") as f:
        settings = yaml.safe_load(f)

# Verzeichnis aus config oder Fallback auf ".keys" im Home-Verzeichnis
    default_logon_subdir = settings.get("directories", {}).get("logon_dir", ".keys")
    logon_dir = os.environ.get("LogonDir", os.path.join(Path.home(), default_logon_subdir))
    return logon_dir       
    # return os.environ.get('LogonDir', os.path.join(os.path.expanduser("~"), '.keys'))
