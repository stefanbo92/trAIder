import os
from datetime import datetime


def check_news_available():
    today = datetime.now()
    date_time = today.strftime("%Y_%m_%d_%H_%M")

    # finding all folders in data
    files = os.listdir("data/")
    news_folders = []

    for f in files:
        if ("csv" in f) or ("index_prices" in f):
            continue
        #print(f)
        news_folders.append(f)

    total_news_count = 0

    # database for saving RSS news
    for folder in news_folders:
        pathname = 'data/'+folder+'/news_'+date_time[:-6]+'.csv'
        saved_news = []
        if (os.path.isfile(pathname)):  # database for current date is available already
            news_file = open(pathname, 'r')
            for line in news_file:
                saved_news.append(line)
                if (len(line.split(",")) != 4):
                    print("Warning:", pathname,
                          "has more/less than four columns")
                    return -1
            if (len(saved_news) == 0):
                print("Warning:", pathname, "no saved news")
                return -1
        else:
            print("Warning:", pathname, "not created")
            return -1
        total_news_count += len(saved_news)
    return total_news_count

def check_index_prices():
    today = datetime.now()
    date_time = today.strftime("%Y_%m_%d_%H_%M")

    pathname = 'data/index_prices/prices_'+date_time[:-6]+'.csv'
    saved_prices = []
    if (os.path.isfile(pathname)):  # database for current date is available already
        news_file = open(pathname, 'r')
        for line in news_file:
            saved_prices.append(line)
            prices_arr=line.split(",")
            if (len(prices_arr) != 27):
                print("Warning:", pathname,
                        "has more/less than 27 columns")
                return -1
        if (len(saved_prices) == 0):
            print("Warning:", pathname, "no saved prices")
            return -1
    else:
        print("folling file not available:",pathname)

    return len(saved_prices)

    total_news_count = 0



#number_news = check_news_available()
#number_prices = check_index_prices()
#print("News available:", number_news)
#print("Prices available:", number_prices)
