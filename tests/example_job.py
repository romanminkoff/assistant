import assistant

def main():
    msg = {'job_name': 'example_job', 'text': None}

    try:
        # Do stuff
        msg['text'] = 'Whatever text is here'
    except:
        msg['text'] = 'Failed to run'
    
    assistant.api.send_message(msg)

if __name__ == '__main__':
    main()