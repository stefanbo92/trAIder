import os
import feedparser
from datetime import datetime

# function for checking if a current title is already saved in news database
def news_already_saved(saved_news, title):
    for news in saved_news:
        news_array = news.split(",")
        curr_title = news_array[2]
        if(curr_title == title):
            return True

    return False


def scrape_news(name, url, use_summary = True):
    print("start scraping news...")

    # getting current date and time
    today = datetime.now()
    date_time = today.strftime("%Y_%m_%d_%H_%M")

    # database for saving RSS news
    pathname = 'data/'+name+'/news_'+date_time[:-6]+'.csv'
    saved_news = []
    if (os.path.isfile(pathname)):  # database for current date is available already
        print("file available :)")
        news_file = open(pathname, 'r')
        for line in news_file:
            saved_news.append(line)
        news_file.close()
    
    news_file = open(pathname, 'w')

    # getting RSS feed
    print("getting RSS feed...", url)
    rss_feed = feedparser.parse(url)
    print("received RSS feed")

    # going over all posts in newsfeed
    news_count = len(saved_news)
    for post in rss_feed.entries:
        #print(post)
        summary = "xxx"
        title = "xxx"
        # replaceing "," for .csv compability
        try:
            title = post.title.replace(", ", " ").replace(",", ".").replace(
            "&", " and ").replace("amp;", "").replace("\n", "")
        except:
            print("no title there")
        if(use_summary):
            try:
                summary = post.summary.replace(", ", " ").replace(",", ".").replace(
                    "&", " and ").replace("amp;", "").replace("\n", "")

                # removing html code in marketwatch
                if ("<div class" in summary):
                    summary = summary[:summary.find("<div class")]
                # removing html code in faz
                if ("<img alt" in summary):
                    summary = summary[summary.find("<p>")+3:-4]
            except:
                print("no summary there")

        print(title)
        print(summary)
        print("------------------")

        # check if news is already available
        if (not news_already_saved(saved_news, title)):
            saved_news.append(str(news_count)+","+date_time +
                              ","+title+","+summary+"\n")
            news_count += 1

    for news in saved_news:
        # write to file
        news_file.write(news)

    news_file.close()

    return(saved_news)

'''
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
# print(my_news)
'''
