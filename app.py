import sys,os,json,requests,time
from flask import Flask, request, abort
import pprint as pp
from ClassificationProcess import SVMMode
from rivescript import RiveScript
from Option import *
import pandas as pd
from crontab import CronTab

from datetime import datetime
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
bot.load_file("HOTEL.rive")
bot.sort_replies()

app = Flask(__name__)
dataqueue = {}

# line_bot_api = LineBotApi('DQj5+Q/4jomyAxECOKGwvXX0v5LGSnbG43DubRvXYKlp3PNGqL/n70r7Ju4nsIcWpWWbDhJy02yUyBILFFZxnciKxLYI37V3euSSJ0o/aLRETZ2bS63mHC0cACQ4X6TXz16T9Bw1mXQI66/3wKw/0gdB04t89/1O/w1cDnyilFU=')
# handler = WebhookHandler('4c48925038eb080a095f04658f6765f4')
# access_token_bearer = 'Bearer DQj5+Q/4jomyAxECOKGwvXX0v5LGSnbG43DubRvXYKlp3PNGqL/n70r7Ju4nsIcWpWWbDhJy02yUyBILFFZxnciKxLYI37V3euSSJ0o/aLRETZ2bS63mHC0cACQ4X6TXz16T9Bw1mXQI66/3wKw/0gdB04t89/1O/w1cDnyilFU='

# Developer Trial Mode
line_bot_api = LineBotApi('ca7M0CHLjlE6Lz7xu7MAb8NKm2HdHqQ5sfCU25DCO2/KePgbxruIFiV1C8g4tnlmyn+YqLLQg4DzR7zQ69Hlx/V4IkZ6VpHOpSJRfWno4mlTO0LNbsbfuzEJxas01IP18/6BSXO5ef9kpEeBPkenkgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('1dd65fab1df91ad26400faa771ed952c')
access_token_bearer = 'Bearer ca7M0CHLjlE6Lz7xu7MAb8NKm2HdHqQ5sfCU25DCO2/KePgbxruIFiV1C8g4tnlmyn+YqLLQg4DzR7zQ69Hlx/V4IkZ6VpHOpSJRfWno4mlTO0LNbsbfuzEJxas01IP18/6BSXO5ef9kpEeBPkenkgdB04t89/1O/w1cDnyilFU='
url_img_1 = 'https://explorewisata.com/wp-content/uploads/2018/01/kolam-renang-di-semarang.jpg'
url_img_2 = 'http://tangerangsatu.co.id/wp-content/uploads/2018/03/Kolam-Renang-Aladin-Aquaplay-Karawaci-Binong-Tangerang.jpg'
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

@app.route("/check-user-response", methods=['GET'])
def send_response():
    user_last_response_json = None

    with open('dataset/scheduler.json','r') as f:
        user_last_response_json = f.read()
        f.close()

    try:
        if user_last_response_json:
            user_last_response = json.loads(user_last_response_json)

            for user_id, t in user_last_response.items():
                now_time = time.time()
                end_time = time_to_int(t['waktu_limit'])
                end_time_end = time_to_int(t['waktu_end'])
                
                if now_time >= end_time and user_last_response[user_id]["status"]=="aktif":
                    line_bot_api.push_message(user_id, TextSendMessage(text='Halo apakah anda masih aktif?'))
                    user_last_response[user_id]["status"] = "warning"
                    with open('dataset/scheduler.json','w+') as f:
                        json.dump(user_last_response,f)
                        f.close()


                with open('dataset/scheduler.json','r') as f:
                    datas = json.load(f)
                    f.close()
                print(datas)

                if now_time >= end_time_end and user_last_response[user_id]["status"]=="warning":
                    reply = bot.reply("localuser", "akhiri umum")
                    line_bot_api.push_message(user_id, 
                        [TextSendMessage(text='Terimakasih telah menghubungi Cika'),
                        TextSendMessage(text=reply),
                        TextSendMessage(text='Sampai Jumpa Lagi :)')
                        ]
                        )
                    user_last_response[user_id]["status"] = "off"
                    with open('dataset/scheduler.json','w+') as f:
                        json.dump(user_last_response,f)
                        f.close()


    except LineBotApiError as e:
    #    line_bot_api.push_message(user_id, TextSendMessage(text="errorrrr {}".format(str(e))))
        print("errorrrr {}".format(str(e)))

    return "Hello there~"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    text = event.message.text
    timestamp = event.timestamp
    if isinstance(event.source, SourceUser):
        userId = event.source.user_id
        print(userId)
    print(timestamp)
    if timestamp != 0:
        timeline = timestamp
        sender_id = userId
        # recipient_id = message["recipient"]["id"]
        # 1542639851917
        unix_timestamp  = int(timeline)/1000
        unix_timestamp_limit = unix_timestamp + 30
        unix_timestamp_end = unix_timestamp + 60

        os.environ['TZ'] = 'Asia/Jakarta'
        time.tzset()
        utc_time = time.gmtime(unix_timestamp)

        local_time = time.localtime(unix_timestamp)
        local_time_limit = time.localtime(unix_timestamp_limit)
        local_time_end = time.localtime(unix_timestamp_end)

        waktu = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
        waktu_limit = time.strftime("%Y-%m-%d %H:%M:%S", local_time_limit)
        waktu_end = time.strftime("%Y-%m-%d %H:%M:%S", local_time_end)
        # print(time.strftime("%Y-%m-%d %H:%M:%S", local_time))

        dataqueue[sender_id] = {
            "waktu":waktu,
            "waktu_limit":waktu_limit,
            "waktu_end":waktu_end,
            "status":"aktif"
        }

        # print(dataqueue)
        with open('dataset/scheduler.json','w+') as f:
            json.dump(dataqueue,f)
            f.close()

        with open('dataset/scheduler.json','r') as f:
            schedule = json.load(f)
            f.close()

        print(schedule)

    print(event)
    reply = bot.reply("localuser", text)
    print(reply)
    
    if reply == 'decision':
        line_bot_api.reply_message(
        event.reply_token, list_bot_button)
    elif reply == 'gambar1':
        data_json_img = {
                "type": "image",
                "originalContentUrl": url_img_1,
                "previewImageUrl": url_img_1
            }

        requests.post('https://api.line.me/v2/bot/message/reply',
            data=json.dumps({
                'replyToken': event.reply_token,
                'messages': [data_json_img]
            }),
            headers={
                'Authorization': access_token_bearer,
                'Content-Type': 'application/json'
            }
        )
    elif reply == 'gambar2':
        data_json_img = {
                "type": "image",
                "originalContentUrl": url_img_2,
                "previewImageUrl": url_img_2
            }

        requests.post('https://api.line.me/v2/bot/message/reply',
            data=json.dumps({
                'replyToken': event.reply_token,
                'messages': [data_json_img]
            }),
            headers={
                'Authorization': access_token_bearer,
                'Content-Type': 'application/json'
            }
        )
    elif reply == 'gambar3':
        data_json_img = {
                "type": "image",
                "originalContentUrl": url_img_1,
                "previewImageUrl": url_img_1
            }

        requests.post('https://api.line.me/v2/bot/message/reply',
            data=json.dumps({
                'replyToken': event.reply_token,
                'messages': [data_json_img]
            }),
            headers={
                'Authorization': access_token_bearer,
                'Content-Type': 'application/json'
            }
        )
    elif reply == 'hoho':
        line_bot_api.reply_message(
        event.reply_token, image_carousel_template)
    elif reply == 'akhiri umum':
        user_last_response_json = None
        with open('dataset/scheduler.json','r') as f:
            user_last_response_json = f.read()
            f.close()
        if user_last_response_json:
            
            user_last_response = json.loads(user_last_response_json)
            for user_id, t in user_last_response.items():
                end_time = time_to_int(t['waktu_limit']) - 35
                end_time_end = time_to_int(t['waktu_end']) - 65

                os.environ['TZ'] = 'Asia/Jakarta'
                time.tzset()
                utc_time = time.gmtime(unix_timestamp)

                local_time_limit = time.localtime(end_time)
                local_time_end = time.localtime(end_time_end)

                waktu_limit = time.strftime("%Y-%m-%d %H:%M:%S", local_time_limit)
                waktu_end = time.strftime("%Y-%m-%d %H:%M:%S", local_time_end)
                user_last_response[user_id]["waktu_limit"] = waktu_limit
                user_last_response[user_id]["waktu_end"] = waktu_end
                user_last_response[user_id]["status"] = "off"
                with open('dataset/scheduler.json','w+') as f:
                    json.dump(user_last_response,f)
                    f.close()
        text = "akhiri umum"
        reply = bot.reply("localuser", text)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply))
    elif reply == 'akhiri hotel':
        user_last_response_json = None
        with open('dataset/scheduler.json','r') as f:
            user_last_response_json = f.read()
            f.close()
        if user_last_response_json:
            user_last_response = json.loads(user_last_response_json)
            for user_id, t in user_last_response.items():
                end_time = time_to_int(t['waktu_limit']) - 35
                end_time_end = time_to_int(t['waktu_end']) - 65

                os.environ['TZ'] = 'Asia/Jakarta'
                time.tzset()
                utc_time = time.gmtime(unix_timestamp)

                local_time_limit = time.localtime(end_time)
                local_time_end = time.localtime(end_time_end)

                waktu_limit = time.strftime("%Y-%m-%d %H:%M:%S", local_time_limit)
                waktu_end = time.strftime("%Y-%m-%d %H:%M:%S", local_time_end)
                
                user_last_response[user_id]["waktu_limit"] = waktu_limit
                user_last_response[user_id]["waktu_end"] = waktu_end
                user_last_response[user_id]["status"] = "off"
                with open('dataset/scheduler.json','w+') as f:
                    json.dump(user_last_response,f)
                    f.close()
        text = "akhiri umum"
        reply = bot.reply("localuser", text)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply))
    elif reply == 'waalaikumussalam decision':
        line_bot_api.reply_message(
            event.reply_token, list_bot_button)
    elif reply == 'sayhai':
        say_hai_msg(event)
    elif reply == 'selamat datang cika':
        say_hai_msg(event)
    elif reply == 'restoran_dekat':
        # print(get_restaurant_nearby())
        text = ""
        n = 0
        for i in get_restaurant_nearby()["results"]:
            # print(i["geometry"]["location"])
            # print(i["name"])
            # print("---")
            n+=1
            name = i["name"]
            link = "https://maps.google.com/?q="+str(i["geometry"]["location"]["lat"])+","+str(i["geometry"]["location"]["lng"])
            textnya = str(n)+". "+name+"\n -"+link
            text += textnya+"\n"
        print(text)

        # line_bot_api.reply_message(
        #     event.reply_token, location_restaurant_message)
        line_bot_api.reply_message(
            event.reply_token,
            [TextSendMessage(text='Berikut list Restoran terdekat dari Hotel Kami'),
                TextSendMessage(text=text)])
    elif reply == 'lokasi':
        data_json_location = {
            "type": "location",
            "title": "Shangri-La Hotel, Jakarta",
            "address": "Jakarta Pusat",
            "latitude": -6.202738,
            "longitude": 106.8187219
        }
        requests.post('https://api.line.me/v2/bot/message/reply',
            data=json.dumps({
                'replyToken': event.reply_token,
                'messages': [data_json_location]
            }),
            headers={
                'Authorization': access_token_bearer,
                'Content-Type': 'application/json'
            }
        )
    elif reply == '[ERR: No Reply Matched]':
        obj = SVMMode()
        process = obj.ClassificationProcess(text)
        print(process)
        result = bot.reply("localuser", process)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply))

if __name__ == "__main__":
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port)
