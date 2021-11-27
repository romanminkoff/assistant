import json

import assistant

def main():
    msg = {
        'job_name': 'example_job',
        'text': 'Whatever text is here'
    }
    assistant.api.send_message(json.dumps(msg))

if __name__ == '__main__':
    main()