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
    for back_idx in range(len(stock_prices)-1, len(stock_prices)-num_backwards, -1):
        stock_features.append(stock_prices[back_idx])
    
    # create stock features by taking the diff of index prices
    stock_features = np.diff(np.array(stock_features))
    weekday_feat = today.weekday()
    numeric_features = np.append(stock_features, weekday_feat)
 
    return np.reshape(numeric_features, (1,-1))


def daily_predict(buy_time, stock, news_sites):
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

    # creating CountVectorizer
    countVector = CountVectorizer(ngram_range=(2, 2))
    # ngram(2,2) means it will combine the 2 words together and assign the value
    trainDataset = countVector.fit_transform(text_features)
    trainDataset = trainDataset.toarray()

    # prediction classifier
    predDataset = countVector.transform([latest_news])
    predDataset = predDataset.toarray()

    # dropping features with low occurence
    drop_thresh = 3
    drop_idx = []
    for col_idx in range(trainDataset.shape[1]):
        curr_col = trainDataset[:, col_idx]
        if(np.sum(curr_col) < drop_thresh):
            drop_idx.append(col_idx)
    print("dropping", len(drop_idx), "features of", trainDataset.shape[1])
    trainDataset = np.delete(trainDataset, drop_idx, 1)
    predDataset = np.delete(predDataset, drop_idx, 1)

    # adding numerical features
    add_numerical = True
    if add_numerical:
        trainDataset = np.append(trainDataset, numeric_features ,axis=1)
        predDataset = np.append(predDataset, latest_numeric_feat ,axis=1)

    # training random forest classifier
    xgb_classifier = XGBClassifier()
    xgb_classifier.fit(trainDataset, bin_labels)

    # predict daily
    prediction = xgb_classifier.predict(predDataset)
    print("todays prediction:", prediction)

    

hyp_param = [9, 13, "dax", ["cnbc_finance"]]
# getting train data
get_train_data(hyp_param[0], hyp_param[1], hyp_param[3], hyp_param[2])
daily_predict(hyp_param[0], hyp_param[2], hyp_param[3])


