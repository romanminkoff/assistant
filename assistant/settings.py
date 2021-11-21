import json
import os

SETTINGS_FILE = "settings.json"
SETTINGS_DEFAULT = {
    "messenger": {
        "name": "slack",
        "url": None
    }
}

def messenger_cfg(s):
    msgr = s.get("messenger")
    if not msgr:
        print("Messenger is not configured. Check settings.json.")
    return msgr

class SettingsFileExists(Exception):
    pass

def create_settings_file(fname=SETTINGS_FILE):
    path = os.path.join(os.getcwd(), fname)
    if os.path.exists(path):
        raise SettingsFileExists()
    with open(path, "wt") as f:
        json.dump(SETTINGS_DEFAULT, f, indent=4)
    return path

def from_file(fname=SETTINGS_FILE):
    path = os.path.join(os.getcwd(), fname)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
