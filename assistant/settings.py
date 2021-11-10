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

def _create_settings_file(path):
    with open(path, "wt") as f:
        json.dump(SETTINGS_DEFAULT, f, indent=4)

def from_file(fname=SETTINGS_FILE):
    path = os.path.join(os.getcwd(), fname)
    if not os.path.exists(path):
        _create_settings_file(path)
    with open(path) as f:
        return json.load(f)
