from flask import Flask, request
from flask import send_from_directory
from remembrall_core import Message, BestMatcher
import os
import json
import requests
import remembrall_util
import logging as log

app = Flask(__name__)
config_dict = remembrall_util.get_configs()


@app.route('/privacy/', methods=['GET'])
def return_privacy_page():
    print "In here"
    static_dir = config_dict['PARENT_DIR'] + '/static'
    print static_dir
    return send_from_directory(directory=static_dir, filename='remembrall_privacy.html')


@app.route('/', methods=['GET'])
def verification_get_method():
    if request.args.get('hub.verify_token', '') == \
            config_dict['VERIFICATION_TOKEN']:
        print "Verification successful!"
        return request.args.get('hub.challenge', '')
    else:
        print "Verification failed!"
        return 'Error, wrong validation token'


@app.route('/', methods=['POST'])
def read_respond_messages():
    print "Handling Messages"
    payload = request.get_data()
    print payload
    for usr_id, message_text in messaging_events(payload):
        print "Incoming from %s: %s" % (usr_id, message_text)
        msg = Message(message_text=message_text, usr_id=usr_id)
        #msg.identify_rule_based()
        msg.identify_message_type()
        msg.insert_in_log_table()
        msg.get_profile()
        print msg.message_type
        #T=Thanks
        #I=Insult
        #C=compliment
        #K=known QA
        #B=bot specific question
        #N=invalid
        if msg.message_type in {'T', 'I', 'C', 'K', 'B', 'N'}:
            try:
                response_message_text=msg.get_response_message()
            except LookupError:
                response_message_text = msg.remember()

        elif msg.message_type =='Q':
            response_message_text = msg.seek()

        else:
            response_message_text = msg.remember()
        print "Now calling send message: "
        send_message(config_dict['PAGE_ACCESS_TOKEN'],
                     usr_id,
                     response_message_text)
    return "ok"

def messaging_events(payload):
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


def send_message(token, recipient, text):
  """Send the message text to recipient with id recipient.
  """
  print "Sending Message: ", text, "recipient: " + recipient
  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"text": text.decode('unicode_escape')}
    }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
