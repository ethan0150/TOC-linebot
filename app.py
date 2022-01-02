import os
import sys
import requests

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from functools import partial
from utils import send_text_message
from relation import *

load_dotenv()

userMachine = {}
DBurl = 'https://gitlab.com/ethan0150/toc-linebot-crawler/-/jobs/artifacts/main/raw/db.sqlite?job=test'
if os.path.isfile("./db.sqlite"):
        os.remove("./db.sqlite")
with open('./db.sqlite', 'wb') as f:
    f.write(requests.get(DBurl, allow_redirects=True).content)

app = Flask(__name__, static_url_path="")
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
port = os.getenv("PORT", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)
    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text)
        )

    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        
        uid = event.source.user_id

        if uid not in userMachine:
            userMachine[uid] = createMachine(uid=uid)

        print(f"\nFSM STATE: {userMachine[uid].state}")
        print(f"REQUEST BODY: \n{body}")
        print(f'\n{event} {type(event)}')

        response = userMachine[uid].advance(event)
        if response == False:
            send_text_message(event.reply_token, "Not Entering any State")

    return "OK"

@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    #createMachine(uid=None).get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")

if __name__ == "__main__":
    from fsm import TocMachine
    global createMachine
    createMachine = partial(TocMachine, 
    states=["init", "coll", "dept", "mand", "result"],
    transitions=[
        {
            "trigger": "advance",
            "source": "init",
            "dest": "coll",
            "conditions": "is_entering_coll",
        },
        {
            "trigger": "advance",
            "source": "coll",
            "dest": "dept",
            "conditions": "is_entering_dept",
        },
        {
            "trigger": "advance",
            "source": "dept",
            "dest": "mand",
            "conditions": "is_entering_mand",
        },
        {
            "trigger": "advance",
            "source": ["coll", "dept", "mand"], 
            "dest": "init",
            "conditions": "is_returing_init"
        },
        {
            "trigger": "advance",
            "source": "mand",
            "dest": "result",
            "conditions": "is_entering_result",
        },
        {
            "trigger": "go_init",
            "source": "result",
            "dest": "init",
        },
    ],
    initial="init",
    auto_transitions=False,
    show_conditions=True
)
    app.run(host="0.0.0.0", port=port, debug=False)
