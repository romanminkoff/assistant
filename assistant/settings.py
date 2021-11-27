import json
import os

SETTINGS_FILE = 'settings.json'
SETTINGS_DEFAULT = {
    'messenger': {
        'name': 'slack',
        'token': None,
        'user_id': None
    }
}

def messenger_cfg(s):
    if msgr := s.get('messenger'):
        return msgr
    else:
        print(f'Messenger is not configured. Check {SETTINGS_FILE}.')

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
