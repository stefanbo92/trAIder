import os
import numpy as np
from matplotlib import pyplot as plt
import datetime
import pickle

NUM_FIN_HISTORY = 20

def get_stock_prizes():
    # finding all folders in data
    files = os.listdir("../data/index_prices")
    files = np.array(files)
    files = np.sort(files)

    saved_prices_all = []
    times = []
    dax_prices = []
    sp500_prices = []
    dow_prices = []
    nasdaq_prices = []
    nikkei_prices = []
    for f in files:
        if ("csv" in f):
            # print(f)
            pathname = "../data/index_prices/"+f
            if (os.path.isfile(pathname)):  # database for current date is available already
                prices_file = open(pathname, 'r+')
                for line in prices_file:
                    saved_prices_all.append(line)
                    line_arr = line.split(",")
                    curr_time = line_arr[1].split("_")
                    customdate = datetime.datetime(int(curr_time[0]), int(curr_time[1]), int(
                        curr_time[2]), int(curr_time[3]), int(curr_time[4]))
                    times.append(customdate)
                    dax_prices.append(float(line_arr[2]))
                    sp500_prices.append(float(line_arr[7]))
                    dow_prices.append(float(line_arr[12]))
                    nasdaq_prices.append(float(line_arr[17]))
                    nikkei_prices.append(float(line_arr[22]))

    # normalizing data to 100 points
    dax_prices = np.array(dax_prices)/dax_prices[0]*100
    sp500_prices = np.array(sp500_prices)/sp500_prices[0]*100
    dow_prices = np.array(dow_prices)/dow_prices[0]*100
    nasdaq_prices = np.array(nasdaq_prices)/nasdaq_prices[0]*100
    nikkei_prices = np.array(nikkei_prices)/nikkei_prices[0]*100

    return {'times': times, 'dax': dax_prices, 'sp500': sp500_prices,
            'dow': dow_prices, 'nasdaq': nasdaq_prices, 'nikkei': nikkei_prices}


def calc_custom_change_rate(index_price, times, t1, t2):
    # calculating changes in percent over time
    if(t2-t1 < 0):
        print("Error, t2 must be larger than t1")
        return
    price_changes = []
    times_changes = []
    for idx, price in enumerate(index_price):
        if idx > 0:
            if(times[idx].hour == t2):  # going over all prices with t2
                for back_idx in range(1, 10):
                    curr_date = times[idx-back_idx]
                    if(times[idx].day != curr_date.day):  # old day
                        break
                    if(curr_date.hour == t1):  # found corresponding price
                        change_percent = (
                            index_price[idx]-index_price[idx-back_idx])/index_price[idx-back_idx]*100
                        if (abs(change_percent) > 0.001):
                            price_changes.append(change_percent)
                            times_changes.append(times[idx])
                        break

    if(len(price_changes) == 0):
        print("error: no stock prices found for that time slot")
        return times_changes, price_changes

    return times_changes, price_changes


def get_news(news_sites, times_changes, buy_time):
    # looping over all times
    saved_news = []
    for time in times_changes:
        day_news = ""
        for news_site in news_sites:
            # getting correct file name accoring to date time
            file_name = "../data/"+news_site+"/news_" + \
                str(time.year)+"_"+str(time.month).zfill(2) + \
                "_"+str(time.day).zfill(2)+".csv"
            #print("opening", file_name)
            if (os.path.isfile(file_name)):  # database for current date is available already
                prices_file = open(file_name, 'r+')
                for line in prices_file:
                    line_arr = line.split(",")
                    if len(line_arr)<2: # faulty line
                        continue
                    # only get news until buy time
                    curr_hour = line_arr[1].split("_")[-2]
                    if(buy_time-int(curr_hour) < 0):
                        break
                    day_news += line_arr[2]+" [NL] "+line_arr[3]+" [NL] "
                # remove bad characters
                day_news = day_news.lower()
                day_news = day_news.replace(".", "")
                day_news = day_news.replace("\n", "")
                # print(day_news)
            else:
                print("Caution: no news found for", time, "in", news_site)

        # save all formatted day news in list
        saved_news.append(day_news)

    return saved_news


def get_stock_features(stock_data, stock_name, times_changes, buy_time):
    # looping over all times from labels
    saved_features = []
    stock_prices = stock_data[stock_name]
    stock_times = stock_data["times"]
    for label_time in times_changes:
        # getting time of the stock price
        feature = []
        for idx, stock_time in enumerate(stock_times):
            if label_time.year == stock_time.year and \
                label_time.month == stock_time.month and \
                    label_time.day == stock_time.day and \
                        stock_time.hour == buy_time:
                #print("stock time", stock_time, "price:", stock_prices[idx])
                # go backwards and save previous stock prices
                for back_idx in range(idx, idx-NUM_FIN_HISTORY, -1):
                    feature.append(stock_prices[back_idx])
                break
        saved_features.append(feature)

    return saved_features

def get_train_data(buy_time, sell_time, news_sites, stock, last_date = None):
    # specify when you want to buy stock and when to sell it
    print("Writing features and lables from",
          news_sites, "and", stock, "to file... (Buy/Sell: ",buy_time,sell_time,")")

    # getting stock prizes and changes between buy and sell as labels
    stock_data = get_stock_prizes()
    times_changes, price_changes = calc_custom_change_rate(
        stock_data[stock], stock_data["times"], buy_time, sell_time)

    # getting news data
    news = get_news(news_sites, times_changes, buy_time)

    # getting stock features 
    stock_features = get_stock_features(
        stock_data, stock, times_changes, buy_time)

    # creating feature vector
    feature_vec = []
    for idx, time in enumerate(times_changes):
        #print(idx, time, stock_features[idx][0], len(news[idx]))

        # if last date is given only save data up until given date
        if last_date is not None:
            if last_date.year <= time.year and last_date.month <= time.month and last_date.day <= time.day:
                price_changes = price_changes[:idx]
                break

        curr_feature = [idx, time, stock_features[idx], news[idx]]
        feature_vec.append(curr_feature)

    # writing features and labels to file
    with open('ml_data/features_raw.data', 'wb') as filehandle:
        pickle.dump(feature_vec, filehandle)
    with open('ml_data/label.data', 'wb') as filehandle:
        pickle.dump(price_changes, filehandle)


buy_time = 9
sell_time = 18
news_sites = ["welt_wirtschaft", "faz_finanzen", "faz_news",
              "faz_wirtschaft", "spiegel_schlagzeilen", "spiegel_wirtschaft"]
stock = "dax"

#get_train_data(buy_time, sell_time, news_sites, stock)

#get_train_data(15, 16, ["bbc_business","bbc_world","cnbc_business","cnbc_economy","cnbc_finance","cnbc_world","wsj_markets"], "sp500")
