import sys,os,json,requests,time
from flask import Flask, request, abort
import pprint as pp
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from rivescript import RiveScript
from dictionary_match import *
from datetime import datetime
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton
)
from linebot.exceptions import LineBotApiError

bot = RiveScript()
bot.load_file("data.rive")
bot.sort_replies()

app = Flask(__name__)

# create stemmer
factory = StemmerFactory()
stemmer = factory.create_stemmer()


# Developer Trial Mode
line_bot_api = LineBotApi('API_KEY')
handler = WebhookHandler('Channel')

def time_to_int(t):
        t = t.replace(' ', '').replace('-', '').replace(':', '')
        return time.mktime(datetime.strptime(t, "%Y%m%d%H%M%S").timetuple())

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
        
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    text = event.message.text
    timestamp = event.timestamp

    msg_stem = stemmer.stem(text)
    print(event)
    print(msg_stem)

    fuzzy_result = process.extractOne(msg_stem, matching)

    if isinstance(event.source, SourceUser):
        userId = event.source.user_id
        print(userId)
    print(timestamp)

    reply = bot.reply("localuser", fuzzy_result[0])
    print(reply)
    
    if reply == '[ERR: No Reply Matched]':
        reply = 'Maaf Saat ini IslamicBot belum faham apa yang anda maksud, silahkan gunakan pertanyaan yang benar'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply))
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply))

if __name__ == "__main__":
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port)
