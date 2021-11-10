import json

import assistant

if __name__ == "__main__":
    msg = {"text": "Whatever text is here"}
    assistant.api.send_message(json.dumps(msg))
