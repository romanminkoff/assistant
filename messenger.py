import slack_sdk

class SlackConnectionException(Exception):
    pass

def _test_slack_connection():
    api_response = slack_sdk.WebClient(token="", ).api_test()
    if api_response:
        return api_response.data["ok"]

class MessengerClientAuthSetupException(Exception):
    pass

def slack_send_txt(cfg, text):
    if not _test_slack_connection():
        raise SlackConnectionException()
    if not "url" in cfg:
        raise MessengerClientAuthSetupException(cfg["name"])
    client = slack_sdk.webhook.WebhookClient(cfg["url"])
    resp = client.send(text=text)
    return True if resp.status_code == 200 else False

class UnsupportedMessengerException(Exception):
    pass

def send_text_msg(msgr_cfg, text):
    if msgr_cfg["name"] == "slack":
        slack_send_txt(msgr_cfg, text)
    else:
        raise UnsupportedMessengerException(msgr_cfg["name"])
