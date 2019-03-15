from rivescript import RiveScript
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from dictionary_match import *

# create stemmer
factory = StemmerFactory()
stemmer = factory.create_stemmer()


# load RiveScript
bot = RiveScript()
bot.load_file("data.rive")
bot.sort_replies()

while True:
    msg = input("You> ")
    msg_stem = stemmer.stem(msg)

    print(msg_stem)

    fuzzy_result = process.extractOne(msg_stem, matching)

    if msg == '/quit':
        quit()

    reply = bot.reply("localuser",fuzzy_result[0])
    print("Bot>", reply)




