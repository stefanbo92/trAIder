import os
import re
from datetime import datetime
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup


# function for getting the current index price
def get_index_price(url):
    # getting html of url
    print("getting html of", url)
    uClient = uReq(url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")
    containers = page_soup.findAll("div", {"class": "quotedataBox"})
    current_div = str(containers[0])

    # price
    price_pos = current_div.find("mleft-10")
    end_pos = current_div.find("<", price_pos)
    price = current_div[price_pos +
                        10:end_pos].replace(".", "").replace(",", ".").strip()
    # opening
    opening_pos = current_div.find("<strong>Eröffnung")+86
    end_pos = current_div.find("/", opening_pos)
    opening = current_div[opening_pos:end_pos].replace(
        ".", "").replace(",", ".").strip()
    # day low
    low_pos = current_div.find("<strong>Tagestief")+89
    end_pos = current_div.find("/", low_pos)
    low = current_div[low_pos:end_pos].replace(
        ".", "").replace(",", ".").strip()
    # day high
    high_pos = end_pos+1
    end_pos = current_div.find("</td>", high_pos)
    high = current_div[high_pos:end_pos].replace(
        ".", "").replace(",", ".").strip()
    # volume
    volume_pos = current_div.find("<strong>Marktkapitalisierung")
    if (volume_pos < 0):
        volume = "1"
    else:
        volume_pos += re.search(r'\d', current_div[volume_pos:]).start()
        end_pos = current_div.find("€", volume_pos)
        volume = current_div[volume_pos:end_pos].replace(
            ".", "").replace(",", ".").strip()
    return [price, opening, low, high, volume]


def write_price(price_list):
    return price_list[0]+","+price_list[1]+","+price_list[2]+","+price_list[3]+","+price_list[4]


def get_index_prices():
    print("start scraping index prices...")

    # getting current index prices (price, opening position, day low, day high, volume)
    dax_price = get_index_price('https://www.finanzen.net/index/dax')
    sp500_price = get_index_price('https://www.finanzen.net/index/s&p_500')
    dow_price = get_index_price('https://www.finanzen.net/index/dow_jones')
    nasdaq_price = get_index_price(
        'https://www.finanzen.net/index/nasdaq_composite')
    nikkei_price = get_index_price('https://www.finanzen.net/index/nikkei_225')

    # getting current date and time
    today = datetime.now()
    date_time = today.strftime("%Y_%m_%d_%H_%M")

    # database for saving price data
    pathname = 'data/index_prices/prices_'+date_time[:-6]+'.csv'
    saved_prices = []
    if (os.path.isfile(pathname)):  # database for current date is available already
        print("file available :)")
        prices_file = open(pathname, 'r+')
        for line in prices_file:
            saved_prices.append(line)
    else:
        print("create new file")  # creating new database
        prices_file = open(pathname, 'w')

    price_string = str(len(saved_prices))+","+date_time+","+write_price(dax_price)+","+write_price(
        sp500_price)+","+write_price(dow_price)+","+write_price(nasdaq_price)+","+write_price(nikkei_price)+"\n"
    print("writing line:")
    print(price_string)

    prices_file.write(price_string)

    prices_file.close()


#get_index_prices()
