import telegram
import data_parser
import time
import random

config = data_parser.Configuration("config.json")
BOT_TOKEN = config.get_item("tg_bot_token")
CHAT_ID = config.get_item("tg_chat_id")


bot = telegram.Bot(token=BOT_TOKEN)

prev_no_stock = {}
available_start = {}

partNbrs, partNames, result, displayText = data_parser.fetch()


for partNbr in partNbrs:
    prev_no_stock[partNbr] = True


while 1:
    try:

        partNbrs, partNames, result, displayText = data_parser.fetch()
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), ':')

        for partNbr in partNbrs:

            no_stock = True
            available_duration = 0

            for storeName in result[partNbr]:
                if result[partNbr][storeName]:
                    no_stock = False

            if prev_no_stock[partNbr] and not no_stock:
                available_start[partNbr] = time.time()

            if not prev_no_stock[partNbr] and no_stock:
                available_duration = time.time()-available_start[partNbr]

                msgToSend = time.strftime(
                    '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))+'\n'
                msgToSend += '🈚️ ' + \
                    partNames[partNbr]+'已售罄，耗时'+str(available_duration)+'秒。'
                bot.send_message(chat_id=CHAT_ID,
                                 text=msgToSend, parse_mode=telegram.ParseMode.HTML)

            print('  >', partNames[partNbr], '🈚️'if no_stock else '✅')

            if prev_no_stock[partNbr] and not no_stock:

                msgToSend = partNames[partNbr]+' 上新啦！✅\n'
                msgToSend += '----------------------------\n'

                for storeName in result[partNbr]:

                    if result[partNbr][storeName]:

                        msgToSend += storeName + \
                            displayText[partNbr][storeName]+'\n'

                bot.send_message(chat_id=CHAT_ID,
                                 text=msgToSend, parse_mode=telegram.ParseMode.HTML)

            prev_no_stock[partNbr] = no_stock

        if no_stock:
            randTime = random.randint(15, 30)
        else:
            randTime = 1

        print('  > Sleep For', randTime, 's')
        time.sleep(randTime)

    except Exception as e:
        print("ERROR", e.args)
        pass
