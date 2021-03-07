import os
import numpy as np
from matplotlib import pyplot as plt
import datetime


def stock_analysis():
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

    def calc_times_change_rate(index_price):
        # calculating changes in percent over time
        price_changes = []
        times_changes = []
        time_change_dict = {'9': [], '11': [],
                            '13': [], '15': [], '16': [], '18': []}
        for idx, price in enumerate(index_price):
            if idx > 0:
                change_percent = (
                    index_price[idx]-index_price[idx-1])/index_price[idx-1]*100
                if (abs(change_percent) > 0.001):
                    price_changes.append(change_percent)
                    times_changes.append(times[idx])
                    if (str(times[idx].hour) in time_change_dict):
                        time_change_dict[str(times[idx].hour)].append(
                            change_percent)
                    #print(times[idx], change_percent)

        for time in time_change_dict:
            curr_mean = 0
            if(len(time_change_dict[time]) > 0):
                curr_mean = np.mean(np.absolute(
                    np.array(time_change_dict[time])))
            print("mean change rate for", time, "o'clock:", curr_mean)

    def calc_custom_change_rate(index_price, t1, t2):
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
            return

        curr_mean = np.mean(np.absolute(np.array(price_changes)))
        print("mean change rate for time", t1, "-", t2, ":",
              curr_mean, "(found", len(price_changes), "values)")

    print("DAX:")
    calc_times_change_rate(dax_prices)
    calc_custom_change_rate(dax_prices, 9, 18)

    print("S&P:")
    calc_times_change_rate(sp500_prices)
    calc_custom_change_rate(sp500_prices, 15, 16)

    print("Dow Jones:")
    calc_times_change_rate(dow_prices)
    calc_custom_change_rate(dow_prices, 15, 16)

    print("NASDAQ:")
    calc_times_change_rate(nasdaq_prices)
    calc_custom_change_rate(nasdaq_prices, 15, 16)

    print("NIKKEI:")
    calc_times_change_rate(nikkei_prices)
    calc_custom_change_rate(nikkei_prices, 9, 18)


stock_analysis()
