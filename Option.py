import sys,os,json,requests,time
import pprint as pp
from flask import Flask, request
from rivescript import RiveScript
import urllib

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
# line_bot_api = LineBotApi('DQj5+Q/4jomyAxECOKGwvXX0v5LGSnbG43DubRvXYKlp3PNGqL/n70r7Ju4nsIcWpWWbDhJy02yUyBILFFZxnciKxLYI37V3euSSJ0o/aLRETZ2bS63mHC0cACQ4X6TXz16T9Bw1mXQI66/3wKw/0gdB04t89/1O/w1cDnyilFU=')
# handler = WebhookHandler('4c48925038eb080a095f04658f6765f4')
line_bot_api = LineBotApi('ca7M0CHLjlE6Lz7xu7MAb8NKm2HdHqQ5sfCU25DCO2/KePgbxruIFiV1C8g4tnlmyn+YqLLQg4DzR7zQ69Hlx/V4IkZ6VpHOpSJRfWno4mlTO0LNbsbfuzEJxas01IP18/6BSXO5ef9kpEeBPkenkgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('1dd65fab1df91ad26400faa771ed952c')

list_bot_button = TemplateSendMessage(
    alt_text='Buttons template',
    template=ButtonsTemplate(
        # thumbnail_image_url='https://explorewisata.com/wp-content/uploads/2018/01/kolam-renang-di-semarang.jpg',
        title='Daftar Bot',
        text='Silahkan tekan tombol dibawah untuk melanjutkan',
        actions=[
            PostbackAction(
                label='Hotel',
                text='hotel',
                data='action=buy&itemid=1'
            ),
            # MessageAction(
            #     label='message',
            #     text='message text'
            # ),
            # URIAction(
            #     label='uri',
            #     uri='http://example.com/'
            # )
        ]
         )
    )

image_carousel_template = TemplateSendMessage(
    alt_text='Buttons template',
    template=ImageCarouselTemplate(
        columns=[
            ImageCarouselColumn(image_url='https://via.placeholder.com/1024x1024',
                                action=URIAction(
                                    label='Kunjungi',
                                    uri='https://via.placeholder.com/1024x1024'
                                )),
            ImageCarouselColumn(image_url='https://via.placeholder.com/1024x1024',
                               action=URIAction(
                                    label='Kunjungi',
                                    uri='https://via.placeholder.com/1024x1024'
                                )),
        ])
    )
location_restaurant_message = TemplateSendMessage(
    alt_text='Buttons template',
    template=ButtonsTemplate(
        thumbnail_image_url='https://maps.googleapis.com/maps/api/staticmap?zoom=14&size=500x300&maptype=roadmap&markers=color:red|label:R|-6.202699700000001,106.8186391&markers=color:red|label:R|-6.196727999999999,106.822582&markers=color:red|label:R|-6.1974609,106.8238203&markers=color:red|label:R|-6.1948222,106.820222&key=AIzaSyCcgwM27TrSD7r_HGUZRORsCfhU96k5VBw',
        # title='Daftar Bot',
        # text='Location',
        actions=[
            PostbackAction(
                label='Hotel',
                text='hotel',
                data='action=buy&itemid=1'
            ),
            # MessageAction(
            #     label='message',
            #     text='message text'
            # ),
            # URIAction(
            #     label='location',
            #     uri='https://www.google.com/maps/search/Restaurants/@-6.203021,106.818003,18z/data=!4m8!2m7!3m6!1sRestaurants!2sShangri-La+Hotel,+Jakarta,+No.Kav+1,+Kota+BNI,+Jl.+Jend.+Sudirman,+RT.10%2FRW.9,+Karet+Tengsin,+Tanahabang,+Kota+Jakarta+Pusat,+Daerah+Khusus+Ibukota+Jakarta+10220!3s0x2e69f41defc50881:0x8220ffb74a693deb!4m2!1d106.8187219!2d-6.2027383'
            # )
        ]
         )
    )
def get_restaurant_nearby():
    data = requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=-6.202738,106.8187219&radius=1500&type=restaurant&key=AIzaSyCcgwM27TrSD7r_HGUZRORsCfhU96k5VBw")
    return data.json()

def say_hai_msg(event):
    if isinstance(event.source, SourceUser):
        profile = line_bot_api.get_profile(event.source.user_id)
        username = profile.display_name

        sayhaifirst = "Hai "+username+''' salam kenal. Saya Cika asisten virtual kamu, selamat datang di layanan digital Hotel Shangri-La.\n
    Untuk informasi lebih lengkap kamu bisa pilih menu dibawah ya\n\n1. PROMO untuk Informasi promo menarik apa saja yang sedang berlangsung
        \n2. PRODUK untuk Informasi Produk Hotel Shangri-La
        \n3. LOKASI untuk lokasi jaringan hotel kami
        \n4. BANTUAN untuk Contact Center Hotel Shangri-La

    Untuk keluar mengakhiri percakapan dengan bot anda cukup mengetik akhiri.
        '''
        return line_bot_api.reply_message(
            event.reply_token,TextSendMessage(text=sayhaifirst))
    else:
        sayhaifirst = ''' Hai, Salam kenal. Saya Cika asisten virtual kamu, selamat datang di layanan digital Hotel Shangri-La\n.
    Untuk informasi lebih lengkap kamu bisa pilih menu dibawah ya\n\n1. PROMO untuk Informasi promo menarik apa saja yang sedang berlangsung
        \n2. PRODUK untuk Informasi Produk Hotel Shangri-La
        \n3. LOKASI untuk lokasi jaringan hotel kami
        \n4. BANTUAN untuk Contact Center Hotel Shangri-La
            
    Untuk keluar mengakhiri percakapan dengan bot anda cukup mengetik akhiri.
        '''
        return line_bot_api.reply_message(
            event.reply_token,TextSendMessage(text=sayhaifirst))