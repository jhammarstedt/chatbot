from flask import Flask,request
import random
from pymessenger.bot import Bot
import json

with open('tokens.json') as f:
    data = json.load(f)


app = Flask(__name__)
ACCESS_TOKEN =data['tokens'][0]['Access']
VERIFY_TOKEN = data['tokens'][0]['Verify']
bot = Bot(ACCESS_TOKEN)

@app.route('/',methods= ['GET','POST'])
def receive_messeage():
    if request.method == 'GET':
        # confirms that all requests that your bot receives came from fb
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    else:  # if the request was not get, it will be a POST - fb is sending the bot a message sent by the user.

        # Get our message that the user sent the bot
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):  # if a message exists here
                    # Fb messenger ID for user so we know where to send reponse back to
                    recipient_id = message['sender']['id']
                    if message['message'].get('text'):  # if there is text here
                        response_sent_text = get_message()
                        send_message(recipient_id, response_sent_text)
                    # if users sends something else than text (gif, photo etc..)
                    if message['message'].get('attachments'):
                        response_sent_notext = get_message()
                        send_message(recipient_id, response_sent_notext)
        return "Message Processed"


def send_message(recipient_id,response):
    #sends user the text msg through response
    bot.send_text_message(recipient_id,response)
    return "success"

def get_message():
    samples = ['Great Job!','Keep being cool!','This actually works!']
    return random.choice(samples)

def verify_fb_token(token_sent):
    #take the token sent by fb and verify that it matches the verf token we sent
    # If match, we allow requests otherwise return error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Invalid verification token" #if they're not the same





if __name__=='__main__':
    app.debug = True
    app.run()
