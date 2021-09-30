from os import getenv
import requests
import json

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


# Format {0} as partNbrs
BASE_URI = "https://www.apple.com/hk-zh/shop/fulfillment-messages?pl=true&mt=compact{0}&searchNearby=true&store={1}"

IP_LOOKUP_URI = "http://ip-api.com/json/"
NEAR_BY_STORE_URI = "https://www.apple.com/rsp-web/store-search?locale={0}&lat={1}&long={2}"


class Configuration:

    def __init__(self, filename):
        if filename:

            with open(filename) as json_raw:
                self.__json_loaded = json.loads(json_raw.read())

        else:
            print("No configuration was provided.")
            exit(0)

    def get_item(self, name):
        if name in self.__json_loaded:
            return self.__json_loaded[name]
        raise KeyError("No such config item:", name)

    def set_item(self, name, val):
        self.__json_loaded[name] = val


def cut_string(input_str, head, tail):
    if isinstance(head, str) and isinstance(tail, str) and isinstance(input_str, str):
        start = input_str.find(head) + len(head)
        end = input_str.find(tail, start)

        if start == -1:
            raise AttributeError("Head not found in target.")
        if end == -1:
            raise AttributeError("Tail not found in target.")

        rt_str = ""
        for index in range(start, end):
            rt_str += input_str[index]
        return rt_str
    else:
        raise TypeError("Inputs are not string!")


def get_locale(store_region):
    uri = "https://www.apple.com/" + store_region
    content = requests.get(uri).text
    return cut_string(cut_string(content, "<html", ">"), 'lang="', '"').replace('-', '_')


def get_nearest_store_nbr(config):
    loc = json.loads(requests.get(IP_LOOKUP_URI).text)
    # print(loc)

    near_by_stores = json.loads(requests.get(NEAR_BY_STORE_URI.format(
        config.get_item("locale"), loc['lat'], loc['lon'])).text)

    # print(NEAR_BY_STORE_URI.format(config.get_item("locale"), loc['lat'], loc['lon']))

    nbs_number = near_by_stores['results'][0]['storeNumber']

    # print(nbs_number)
    return nbs_number


def gen_part_nbr_format(partNbrs):
    ret_str = ""
    index = 0
    for partNbr in partNbrs:
        ret_str += '&parts.{0}={1}'.format(index, partNbrs[index])
        index += 1
    return ret_str


def fetch():
    config = Configuration("config.json")
    config.set_item('locale', get_locale(config.get_item('store_region')))

    partNbrs = config.get_item('partNames')

    nbs_number = get_nearest_store_nbr(config)

    stock_query_uri = BASE_URI.format(
        gen_part_nbr_format(partNbrs), nbs_number)
    stock_result = json.loads(requests.get(stock_query_uri).text)

    # print(stock_query_uri)
    stores = stock_result['body']['content']['pickupMessage']['stores']

    availability = {}
    partNames = {}
    displayText = {}

    for partNbr in partNbrs:

        availability[partNbr] = {}
        partNames[partNbr] = stores[0]['partsAvailability'][partNbr]['storePickupProductTitle']
        displayText[partNbr] = {}

        for store in stores:
            availability[partNbr][store['storeName']] = (
                store['partsAvailability'][partNbr]['pickupDisplay'] == 'available')
            displayText[partNbr][store['storeName']
                                 ] = store['partsAvailability'][partNbr]['pickupSearchQuote']

    return partNbrs, partNames, availability, displayText


if __name__ == '__main__':

    partNbrs, partNames, result,displayText = fetch()

    for partNbr in partNbrs:

        no_stock = True
        for storeName in result[partNbr]:
            if result[partNbr][storeName]:
                no_stock = False

        print(partNames[partNbr], '🈚️'if no_stock else '✅')

        if not no_stock:
            for storeName in result[partNbr]:

                if result[partNbr][storeName]:
                    print('    ', storeName,
                         displayText[partNbr][storeName])

 # print('    ', store['storeName'], store['partsAvailability'][partNbr]['pickupSearchQuote'])
            #
            #print('      > ', store['pickupEncodedUpperDateString'])
