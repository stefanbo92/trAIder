import os
import numpy as np
from random import *

from get_train_data import *
from feature_engineering import *
from kfold_train_test import *


def get_random_hyperparam():
    # buy and sell times
    trade_times = [9, 11, 13, 15, 16, 18]
    rand_buy = randint(0, 4)
    rand_sell = randint(rand_buy+1, 5)
    buy_time = trade_times[rand_buy]
    sell_time = trade_times[rand_sell]

    # select index
    # indeces = ["dax", "sp500", "dow", "nasdaq", "nikkei"]
    indeces = ["dax", "sp500", "dow", "nasdaq", "dax", "dax", "dax"]
    rand_index = randint(0, 4)
    stock = indeces[rand_index]
    if stock != "dax": # only buy and sell when market is open
        buy_time = 16
        sell_time = 18

    # news
    news_sites = ["bbc_business", "cnbc_world", "faz_news", "investing_world", "wsj_markets",
                  "bbc_world",    "cnn_money",   "faz_wirtschaft",   "marketwatch_topstories",  "wsj_world",
                  "cnbc_business",  "cnn_news",    "spiegel_schlagzeilen",
                  "cnbc_economy", "cnn_world",   "investing_economy",  "spiegel_wirtschaft",
                  "cnbc_finance", "faz_finanzen",  "investing_stock",  "welt_wirtschaft"]
    num_news = randint(1, 10)
    news = []
    for i in range(num_news):
        rand_news = randint(0, len(news_sites)-1)
        news.append(news_sites[rand_news])
        news_sites.remove(news[-1])
    return [buy_time, sell_time, stock, news]


def train_random():
    best_gain = 0.15
    best_acc = 0.65
    total_accuracy = []
    total_gain = []
    for i in range(1000):
        print("training round", i)

        # getting hyper parameters
        hyp_param = get_random_hyperparam()
        # getting train data
        get_train_data(hyp_param[0], hyp_param[1], hyp_param[3], hyp_param[2])
        # training data and calculate average gain
        #gains, accuracy = train_test()
        gains, accuracy = kfold_train_test(7)
        if gains is None: # if no calculations could be performed
            continue
        average_gain = np.array(gains).sum()/len(gains)
        total_accuracy.append(accuracy)
        total_gain.append(average_gain)
        print("average total accuracy:",np.mean(np.array(total_accuracy)),"av. gain:",np.mean(np.array(total_gain)),"(",len(total_accuracy),"samples )")

        # save the best gains
        if average_gain > best_gain and accuracy > best_acc:
            # Open the file in write mode and write best gain with hyper params
            with open("best_hyp_param", 'a') as file_object:
                hyp_string = str(hyp_param[0])+", " + \
                    str(hyp_param[1])+', "'+str(hyp_param[2])+'", ['
                for news_site in hyp_param[3]:
                    hyp_string += '"'+news_site+'", '
                hyp_string = hyp_string[:-2]
                hyp_string += ']\n'
                file_object.write("Average Gain: "+str(round(average_gain,3)) +", Accuracy: "+str(round(accuracy,2))+
                                " ("+str(len(gains))+" days) --> Hyperparameters: "+hyp_string)

            #best_gain = average_gain
        print("----------------------------------------------------------")


train_random()

hyp_param = [13, 18, "sp500", ["cnbc_finance", "wsj_world", "bbc_business", "cnbc_business", "bbc_world", "faz_finanzen", "cnn_news", "investing_economy", "cnn_money", "investing_stock"]]
# getting train data
get_train_data(hyp_param[0], hyp_param[1], hyp_param[3], hyp_param[2])
# training data and calculate average gain
gains, accuracy = train_test()
gains, accuracy = kfold_train_test(7)