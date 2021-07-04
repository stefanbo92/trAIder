import os
import numpy as np
from matplotlib import pyplot as plt
import datetime


def plot_stock():
    # finding all folders in data
    files = os.listdir("../data/index_prices")
    files = np.array(files)
    files = np.sort(files)

    saved_prices_all = []
    times=[]
    dax_prices=[]
    sp500_prices=[]
    dow_prices=[]
    nasdaq_prices=[]
    nikkei_prices=[]
    for f in files:
        if ("csv" in f):
            print(f)
            pathname = "../data/index_prices/"+f
            if (os.path.isfile(pathname)):  # database for current date is available already
                prices_file = open(pathname, 'r+')
                for line in prices_file:
                    saved_prices_all.append(line)
                    line_arr=line.split(",")
                    curr_time=line_arr[1].split("_")
                    customdate = datetime.datetime(int(curr_time[0]), int(curr_time[1]), int(curr_time[2]), int(curr_time[3]), int(curr_time[4]))
                    times.append(customdate)
                    dax_prices.append(float(line_arr[2]))
                    sp500_prices.append(float(line_arr[7]))
                    dow_prices.append(float(line_arr[12]))
                    nasdaq_prices.append(float(line_arr[17]))
                    nikkei_prices.append(float(line_arr[22]))

    dax_prices = np.array(dax_prices)/dax_prices[0]*100
    sp500_prices = np.array(sp500_prices)/sp500_prices[0]*100
    dow_prices = np.array(dow_prices)/dow_prices[0]*100
    nasdaq_prices = np.array(nasdaq_prices)/nasdaq_prices[0]*100
    nikkei_prices = np.array(nikkei_prices)/nikkei_prices[0]*100

    plt.plot(times,dax_prices,label="DAX Kurs")
    plt.scatter(times,dax_prices)
    #plt.plot(times,sp500_prices,label="S&P500 Kurs")
    #plt.scatter(times,sp500_prices)
    #plt.plot(times,dow_prices,label="Dow Jones Kurs")
    #plt.scatter(times,dow_prices)
    plt.plot(times,nasdaq_prices,label="NASDAQ Kurs")
    plt.scatter(times,nasdaq_prices)
    #plt.plot(times,nikkei_prices,label="NIKKEI Kurs")
    #plt.scatter(times,nikkei_prices)
    plt.legend()
    plt.show()



plot_stock()
