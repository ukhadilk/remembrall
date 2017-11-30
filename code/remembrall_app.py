from flask import Flask, request, jsonify
from flask import send_from_directory
from remembrall_core import Message, BestMatcher
import os
import json
import requests
import remembrall_util

app = Flask(__name__)
config_dict = remembrall_util.get_configs()


# T=Thanks
# I=Insult
# C=compliment
# K=known QA
# B=bot specific question
# N=invalid
# L=list


@app.route('/privacy/', methods=['GET'])
def return_privacy_page():
    print "In here"
    static_dir = config_dict['PARENT_DIR'] + '/static'
    print static_dir
    return send_from_directory(directory=static_dir, filename='remembrall_privacy.html')


@app.route('/facebook/', methods=['GET'])
def verification_get_method():
    if request.args.get('hub.verify_token', '') == \
            config_dict['VERIFICATION_TOKEN']:
        print "Verification successful!"
        return request.args.get('hub.challenge', '')
    else:
        print "Verification failed!"
        return 'Error, wrong validation token'


@app.route('/facebook/', methods=['POST'])
def read_respond_facebook_messages():
    print "Handling Google Messages"
    payload = request.get_data()
    print payload
    fb_interpreter = FBInterpreter()
    fb_interpreter.chat(payload=payload)
    return "ok"


@app.route('/google/', methods=['POST'])
def read_respond_google_messages():
    print "Handling Google Messages"
    payload = request.get_data()
    print payload
    google_interpreter = GoogleInterpreter()
    response_message_text = google_interpreter.chat(payload=payload)
    response_message_speech = response_message_text.replace(":)", ".")
    return jsonify({"speech": response_message_speech, "displayText": response_message_text,
                    "source": "Remembrall"})

class MessageInterpreter(object):

    def __init__(self):
        self.msg = None
        self.response_message_text = ""

    def get_message(self, message_text, usr_id):
        pass

    def send_response(self, token, recipient):
        pass

    def chat(self, payload):
        pass

    def messaging_events(self, payload):
        pass

    def process_message(self):

        self.msg.identify_message_type()
        self.msg.insert_in_log_table()
        print self.msg.message_type

        if self.msg.message_type in {'T', 'I', 'C', 'K', 'B', 'N', 'L'}:
            try:
                self.response_message_text=self.msg.get_response_message()
            except LookupError:
                self.response_message_text = self.msg.remember()

        elif self.msg.message_type =='Q':
            self.response_message_text = self.msg.seek()

        else:
            self.response_message_text = self.msg.remember()


class FBInterpreter(MessageInterpreter):

    def get_message(self, message_text, usr_id):
        self.msg = Message(message_text=message_text, usr_id=usr_id)
        self.msg.get_profile()

    def send_response(self, token, recipient):
        print "Sending Message: ", self.response_message_text, "recipient: " + recipient
        r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                          params={"access_token": token},
                          data=json.dumps({
                              "recipient": {"id": recipient},
                              "message": {"text": self.response_message_text.decode('unicode_escape')}
                          }),
                          headers={'Content-type': 'application/json'})
        if r.status_code != requests.codes.ok:
            print r.text

    def chat(self, payload):
        for usr_id, message_text in self.messaging_events(payload):
            self.get_message(message_text, usr_id)
            self.process_message()
            self.send_response(config_dict['PAGE_ACCESS_TOKEN'],
                         usr_id)

    def messaging_events(self, payload):
        """Generate tuples of (sender_id, message_text) from the
        provided payload.
        """
        data = json.loads(payload)
        message_cluster = data["entry"][0]["messaging"]
        for message_data in message_cluster:
            if "message" in message_data and "text" in message_data["message"]:
                yield message_data["sender"]["id"], \
                      message_data["message"]["text"].encode('unicode_escape')
            else:
                yield message_data["sender"]["id"], ""


class GoogleInterpreter(MessageInterpreter):

    def chat(self, payload):
        usr_id, message_text = self.messaging_events(payload=payload)
        self.get_message(message_text, usr_id)
        self.process_message()
        return self.response_message_text

    def messaging_events(self, payload):
        data = json.loads(payload)
        message_text = data["originalRequest"]["data"]["inputs"][0]["rawInputs"][0]["query"]
        usr_id = data["originalRequest"]["data"]["user"]["userId"]
        return usr_id, message_text.encode('unicode_escape')


    def get_message(self, message_text, usr_id):
        self.msg = Message(message_text=message_text, usr_id=usr_id)



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


