from datetime import datetime
from scrape_index_prices import *
from scrape_news import *
import time


def run_scraping():

    # getting news
    my_news = scrape_news("bbc_business", "http://feeds.bbci.co.uk/news/business/rss.xml")
    my_news = scrape_news("bbc_world", "http://feeds.bbci.co.uk/news/world/rss.xml")
    my_news = scrape_news("cnbc_world", "https://www.cnbc.com/id/100727362/device/rss/rss.html")
    my_news = scrape_news("cnbc_business", "https://www.cnbc.com/id/10001147/device/rss/rss.html")
    my_news = scrape_news("cnbc_economy", "https://www.cnbc.com/id/20910258/device/rss/rss.html")
    my_news = scrape_news("cnbc_finance", "https://www.cnbc.com/id/10000664/device/rss/rss.html")
    my_news = scrape_news("wsj_world", "https://feeds.a.dj.com/rss/RSSWorldNews.xml")
    my_news = scrape_news("wsj_markets", "https://feeds.a.dj.com/rss/RSSMarketsMain.xml")
    my_news = scrape_news("marketwatch_topstories", "http://feeds.marketwatch.com/marketwatch/topstories/")
    my_news = scrape_news("investing_world", "https://www.investing.com/rss/news_287.rss", False)
    my_news = scrape_news("investing_economy", "https://www.investing.com/rss/news_14.rss", False)
    my_news = scrape_news("investing_stock", "https://www.investing.com/rss/news_25.rss", False)
    my_news = scrape_news("cnn_news", "http://rss.cnn.com/rss/edition.rss", False)
    my_news = scrape_news("cnn_world", "http://rss.cnn.com/rss/edition_world.rss", False)
    my_news = scrape_news("cnn_money", "http://rss.cnn.com/rss/money_news_international.rss", False)
    my_news = scrape_news("faz_wirtschaft", "https://www.faz.net/rss/aktuell/wirtschaft/")
    my_news = scrape_news("faz_finanzen", "https://www.faz.net/rss/aktuell/finanzen/")
    my_news = scrape_news("faz_news", "https://www.faz.net/rss/aktuell/")
    my_news = scrape_news("spiegel_schlagzeilen", "https://www.spiegel.de/schlagzeilen/tops/index.rss")
    my_news = scrape_news("spiegel_wirtschaft", "https://www.spiegel.de/wirtschaft/unternehmen/index.rss")
    my_news = scrape_news("welt_wirtschaft", "https://www.welt.de/feeds/section/wirtschaft.rss")

    # getting financial data
    get_index_prices()
    


print("start scraping everything")
times_arr = ["01_00", "3_00", "5_00", "7_00", "09_30", "11_00", "13_00", "15_00", "16_00", "18_00", "20_00", "22_00"]
arr_idx = 0

# find current arr_idx
curr_hour = datetime.now().strftime("%Y_%m_%d_%H_%M").split("_")[3]
for idx, time_str in enumerate(times_arr):
    if( int(curr_hour) >= int(time_str.split("_")[0])):
        arr_idx = idx+1
        if (arr_idx==len(times_arr)):
            arr_idx=0

while(True):
    # getting current date and time
    today = datetime.now()
    date_time = today.strftime("%Y_%m_%d_%H_%M")
    print("getting datetime:", date_time)
    date_time_arr = date_time.split("_")
    times_trigger_next = times_arr[arr_idx].split("_")
    print("running if...")
    print(int(times_trigger_next[0]), int(date_time_arr[3]), int(
        times_trigger_next[1]), int(date_time_arr[4]))
    if (int(times_trigger_next[0])-int(date_time_arr[3]) == 0) and (int(times_trigger_next[1])-int(date_time_arr[4]) < 0):
        arr_idx += 1
        if (arr_idx == len(times_arr)):
            arr_idx = 0
        run_scraping()
    print("sleeping for 30s")
    time.sleep(30)
run_scraping()
