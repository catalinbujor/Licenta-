from twilio.rest import Client


class SmsSender:
    def __init__(self, message, to):
        self.message = message
        self.to = to

    def send_SMS(self, message, to):
        account_sid = 'AC06d44c1010f0d101b561c0f833ec8888'
        auth_token = '5b054991766ca520b892b64745c2cb83'
        client = Client(account_sid, auth_token)
        print("Se trimite mesajul .. ")
        client.messages \
            .create(
            body=message,
            from_='+12063396544',
            to=to
        )