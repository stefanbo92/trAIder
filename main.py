import os
import feedparser
from datetime import datetime
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

# function for getting the current index price


def get_index_price(url):
    uClient = uReq(url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")
    containers = page_soup.findAll("div", {"class": "quotedataBox"})
    current_div = str(containers[0])
    price_pos = current_div.find("mleft-10")
    end_pos = current_div.find("<", price_pos)
    price = current_div[price_pos +
                        10:end_pos].replace(".", "").replace(",", ".")
    #price = float(price)
    return price

# function for checking if a current title is already saved in news database


def news_already_saved(saved_news, title):
    for news in saved_news:
        news_array = news.split(",")
        curr_title = news_array[2]
        if(curr_title == title):
            return True

    return False


def main():
    print("start scraping...")

    # getting current date and time
    today = datetime.now()
    date_time = today.strftime("%d_%m_%Y_%H_%M")

    # getting current index prices
    dax_price = get_index_price('https://www.finanzen.net/index/dax')
    sp500_price = get_index_price('https://www.finanzen.net/index/s&p_500')
    dow_price = get_index_price('https://www.finanzen.net/index/dow_jones')
    nasdaq_price = get_index_price(
        'https://www.finanzen.net/index/nasdaq_composite')
    nikkei_price = get_index_price('https://www.finanzen.net/index/nikkei_225')

    # database for saving RSS and price data
    pathname = 'data/welt_wirtschaft_'+date_time[:-6]+'.csv'
    saved_news = []
    if (os.path.isfile(pathname)):  # database for current date is available already
        print("file available :)")
        news_file = open(pathname, 'r+')
        for line in news_file:
            saved_news.append(line)
    else:
        print("create new file")  # creating new database
        news_file = open(pathname, 'w')


    # getting RSS feed
    print("getting RSS feed...")
    url_welt = 'https://www.welt.de/feeds/section/wirtschaft.rss'
    rss_feed = feedparser.parse(url_welt)
    print("received RSS feed")

    # going over all posts in newsfeed
    news_count = len(saved_news)
    for post in rss_feed.entries:
        # replaceing "," for .csv compability
        title = post.title.replace(", ", " ").replace(",", ".").replace(
            "&", " and ").replace("amp;", "")
        summary = post.summary.replace(", ", " ").replace(",", ".").replace(
            "&", " and ").replace("amp;", "")
        print(title)
        # print(summary)
        print("------------------")

        # check if news is already available
        if (not news_already_saved(saved_news, title)):
            saved_news.append(str(news_count)+","+date_time +
                              ","+title+","+summary+","+dax_price +
                              ","+sp500_price+","+dow_price +
                              ","+nasdaq_price+","+nikkei_price+"\n")
            news_count += 1

    for news in saved_news:
        # write to file
        news_file.write(news)

    news_file.close()
    print("im gonna get rich")


main()
