import telegram
import data_parser
import time
import random

config = data_parser.Configuration("config.json")
BOT_TOKEN = config.get_item("tg_bot_token")
CHAT_ID = config.get_item("tg_chat_id")


bot = telegram.Bot(token=BOT_TOKEN)

available_start = {}

partNbrs, partNames, result, displayText = data_parser.fetch()

prev_availibility = {}
current_availibility = {}

for partNbr in partNbrs:
    prev_availibility[partNbr] = False
    current_availibility[partNbr] = False


while 1:
    try:

        partNbrs, partNames, result, displayText = data_parser.fetch()
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), ':')

        for partNbr in partNbrs:

            current_availibility[partNbr] = False
            available_duration = 0

            for storeName in result[partNbr]:
                if result[partNbr][storeName]:
                    current_availibility[partNbr] = True

            if not prev_availibility[partNbr] and current_availibility[partNbr]:
                available_start[partNbr] = time.time()

            if prev_availibility[partNbr] and not current_availibility[partNbr]:
                available_duration = time.time()-available_start[partNbr]

                msgToSend = time.strftime(
                    '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))+'\n'
                msgToSend += '🈚️ ' + \
                    partNames[partNbr]+'已售罄，耗时' + \
                    "%.2f" % available_duration+'秒。'
                bot.send_message(chat_id=CHAT_ID,
                                 text=msgToSend, parse_mode=telegram.ParseMode.HTML)

            print('  >', partNames[partNbr],
                  '✅'if current_availibility[partNbr] else '🈚️')

            if not prev_availibility[partNbr] and current_availibility[partNbr]:

                msgToSend = partNames[partNbr]+' 上新啦！✅\n'
                msgToSend += '----------------------------\n'

                for storeName in result[partNbr]:

                    if result[partNbr][storeName]:

                        msgToSend += storeName + \
                            displayText[partNbr][storeName]+'\n'

                bot.send_message(chat_id=CHAT_ID,
                                 text=msgToSend, parse_mode=telegram.ParseMode.HTML)

            prev_availibility[partNbr] = current_availibility[partNbr]

        fast_refresh = False

        for partNbr in partNbrs:
            if current_availibility[partNbr]:
                fast_refresh = True

        if fast_refresh:
            randTime = 0.5
        else:
            preSharpTimeRange = 60
            afterSharpTimeRange = 480
            if time.time() % 1800 > (1800-preSharpTimeRange) or time.time() % 1800 < afterSharpTimeRange:
                randTime = random.randint(4, 8)
            else:
                randTime = random.randint(15, 30)
        print('  > Sleep For', randTime, 's')
        time.sleep(randTime)

    except Exception as e:
        print("ERROR", e.args)
        pass
