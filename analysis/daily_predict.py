import os
import numpy as np
from matplotlib import pyplot as plt
import datetime
import pickle
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.feature_extraction.text import CountVectorizer

from xgboost import XGBClassifier

from feature_engineering import *
from get_train_data import *

from datetime import datetime
import time


def get_latest_news(news_sites, buy_time):
    # getting todays datetime
    today = datetime.now()
    day_news = ""
    # going over all required newssites
    for news_site in news_sites:
        # getting correct file name accoring to date time
        file_name = "../data/"+news_site+"/news_" + \
            str(today.year)+"_"+str(today.month).zfill(2) + \
            "_"+str(today.day).zfill(2)+".csv"
        print("opening", file_name)
        if (os.path.isfile(file_name)):  # database for current date is available already
            news_file = open(file_name, 'r+')
            for line in news_file:
                line_arr = line.split(",")
                if len(line_arr)<2: # faulty line
                    continue
                # only get news until buy time
                curr_hour = line_arr[1].split("_")[-2]
                if(buy_time-int(curr_hour) < 0):
                    break
                day_news += line_arr[2]+" [NL] "+line_arr[3]+" [NL] "
        else:
            print("Caution: no news found for", time, "in", news_site)
        # remove bad characters
        day_news = day_news.lower()
        day_news = day_news.replace(".", "")
        day_news = day_news.replace("\n", "")
        day_news = day_news.replace('“', '').replace('„', '')
        day_news = day_news.replace('[nl]', '')
        day_news = day_news.replace(':', '').replace('-', ' ').replace('–', '')
        day_news = day_news.replace('  ', ' ').replace('?', '')
        day_news = day_news.replace('»', '').replace('«', '')
        day_news = day_news.replace('!', '').replace('"', '')
        day_news = day_news.replace('+', '').replace('+', '')
        #print(day_news)
        return day_news


def get_fin_data(stock, buy_time):
    # getting todays datetime
    today = datetime.now()

    # getting all stock prices from specified index
    all_stock_data = get_stock_prizes()
    stock_prices = all_stock_data[stock]
    stock_features = []
    num_backwards = 21

    # check if current buy time is already in current data
    if True:
        pass # TODO

    # go backwards and save previous stock prices
    print("Buy stock:",stock_prices[-1])
    for back_idx in range(len(stock_prices)-1, len(stock_prices)-num_backwards, -1):
        stock_features.append(stock_prices[back_idx])
    
    # create stock features by taking the diff of index prices
    stock_features = np.diff(np.array(stock_features))
    weekday_feat = today.weekday()
    numeric_features = np.append(stock_features, weekday_feat)
 
    return np.reshape(numeric_features, (1,-1))


def train_classifier(buy_time, stock, news_sites):
    
    # getting train features and labels from file
    text_features, numeric_features, lables, bin_labels = get_prepared_data()
    if(len(text_features)==0):
        return None, None, None

    # creating CountVectorizer
    countVector = CountVectorizer(ngram_range=(2, 2))
    # ngram(2,2) means it will combine the 2 words together and assign the value
    trainDataset = countVector.fit_transform(text_features)
    trainDataset = trainDataset.toarray()

    # dropping features with low occurence
    drop_thresh = 3
    drop_idx = []
    for col_idx in range(trainDataset.shape[1]):
        curr_col = trainDataset[:, col_idx]
        if(np.sum(curr_col) < drop_thresh):
            drop_idx.append(col_idx)
    print("dropping", len(drop_idx), "features of", trainDataset.shape[1])
    trainDataset = np.delete(trainDataset, drop_idx, 1)

    # adding numerical features
    add_numerical = True
    if add_numerical:
        trainDataset = np.append(trainDataset, numeric_features ,axis=1)

    # training random forest classifier
    xgb_classifier = XGBClassifier()
    xgb_classifier.fit(trainDataset, bin_labels)

    return xgb_classifier, countVector, drop_idx

def daily_predict(xgb_classifier, countVector, drop_idx, buy_time, stock, news_sites):
    # getting current date and time
    today = datetime.now()
    date_time = today.strftime("%Y_%m_%d_%H_%M")
    
    # getting train features and labels from file
    text_features, numeric_features, lables, bin_labels = get_prepared_data()
    if(len(text_features)==0):
        return None, None

    # getting latest financial data
    latest_numeric_feat = get_fin_data(stock, buy_time)

    # getting latest news
    latest_news = get_latest_news(news_sites, buy_time)

    # prediction classifier
    predDataset = countVector.transform([latest_news])
    predDataset = predDataset.toarray()

    # dropping features with low occurence
    predDataset = np.delete(predDataset, drop_idx, 1)

    # adding numerical features
    add_numerical = True
    if add_numerical:
        predDataset = np.append(predDataset, latest_numeric_feat ,axis=1)

    # predict daily
    prediction = xgb_classifier.predict(predDataset)
    print("todays prediction:", prediction)

    return prediction

    
print("start training")
#hyp_param = [9, 13, "dax", ["cnbc_finance"]]
hyp_param = [13, 18, "nasdaq", ["cnn_news", "investing_economy", "faz_wirtschaft", "bbc_world", "faz_finanzen", "investing_world"]]
# getting train data
get_train_data(hyp_param[0], hyp_param[1], hyp_param[3], hyp_param[2])
# train classifier
xgb_classifier, countVector, drop_idx = train_classifier(hyp_param[0], hyp_param[2], hyp_param[3])

# looping every day until buy time is reached
print("staring every day loop")
buy_time = [13,5]
sell_time = hyp_param[1]
while(True):
    # getting current date and time
    today = datetime.now()
    if today.weekday() > 4: # skip weekend
        time.sleep(9999)
        continue
    date_time = today.strftime("%Y_%m_%d_%H_%M")
    date_time_arr = date_time.split("_")
    print("getting datetime:", date_time)

    # buying
    #print("buying if", int(buy_time[0]),"==", int(date_time_arr[3]),"and", int(
    #    buy_time[1]), "==", int(date_time_arr[4]))
    if (buy_time[0]-int(date_time_arr[3]) == 0) and (buy_time[1]-int(date_time_arr[4]) <= 0):
        # make daily prediction
        prediction = daily_predict(xgb_classifier, countVector, drop_idx, hyp_param[0], hyp_param[2], hyp_param[3])
        if prediction[0] > 0:
            # buy long
            buy_sign = 1
            print("buying long")
        else:
            # buy short
            buy_sign = -1
            print("buying short")
        print("buying done, sleeping for 3999 seconds")
        time.sleep(3999) # sleep for one hour

    # selling
    #print("selling if",sell_time,"==", int(date_time_arr[3]))
    if sell_time-int(date_time_arr[3]) == 0:
        # selling position
	    print("selling position")
        # logging results
	    time.sleep(200) # wait until latest prices were written to file 
        all_stock_data = get_stock_prizes()
        curr_stock = all_stock_data[hyp_param[2]]
        # getting actual buy and sell price
        for back_idx in range(len(curr_stock)-1, len(curr_stock)-10, -1):
            print("curr_stock_price:",back_idx, all_stock_data["times"][back_idx],curr_stock[back_idx])
            if(all_stock_data["times"][back_idx].hour==hyp_param[1]):
                sell_price = curr_stock[back_idx]
                print("sell_stock", sell_price)
            if(all_stock_data["times"][back_idx].hour==hyp_param[0]):
                buy_price = curr_stock[back_idx]
                print("buy_price recalc", buy_price)
                break
        win_percent = ((sell_price - buy_price)/buy_price) * buy_sign * 100
        with open("daily_bets.txt", 'a') as file_object:
            out_str = all_stock_data["times"][-1].strftime("%Y_%m_%d_%H_%M") +": Win/Loss --> "+str(round(win_percent,3))+"\n"
            file_object.write(out_str)
        time.sleep(9999) # sleep for two hours

    # wait and loop
    #print("sleeping for 30s")
    time.sleep(60)




