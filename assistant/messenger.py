import slack_sdk

class SlackConnectionException(Exception):
    pass

def _is_slack_connection_ok():
    if api_response := slack_sdk.WebClient(token="").api_test():
        return api_response.data["ok"]

def _slack_channels(client):
    try:
        res = client.conversations_list()
        if res.data['ok']:
            return [ch['name'] for ch in res.data['channels']]
    except:
        pass

def _slack_invite(client, channel, users):
    client.conversations_invite(channel=channel, users=users)

class MessengerClientAuthSetupException(Exception):
    pass

def _to_slack_channel_name(job_name):
    return job_name.lower().replace(' ', '_')

def _slack_prepare_channel(client, user_id, job_name):
    name = _to_slack_channel_name(job_name)
    channels = _slack_channels(client)
    if not name in channels:
        res = client.conversations_create(name=name, is_private=False)
        ch_id = res.data['channel']['id']
        _slack_invite(client, channel=ch_id, users=[user_id])
    return name

def _slack_send(client, user_id, payload):
    job_name = payload.get('job_name')
    text = payload.get('text')
    channel = _slack_prepare_channel(client, user_id, job_name)
    client.chat_postMessage(channel=channel, text=text)

def _slack_send_message_main(cfg, payload):
    if not _is_slack_connection_ok():
        raise SlackConnectionException()
    if token := cfg.get('token'):
        client = slack_sdk.WebClient(token)
        _slack_send(client, cfg.get('user_id'), payload)
    else:
        raise MessengerClientAuthSetupException('Missing messanger token')

class UnsupportedMessengerException(Exception):
    pass

def send_message(msgr_cfg, payload):
    msg_client = msgr_cfg.get('name')
    if msg_client == 'slack':
        _slack_send_message_main(msgr_cfg, payload)
    else:
        raise UnsupportedMessengerException(msg_client)
