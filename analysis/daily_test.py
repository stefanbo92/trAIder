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
from xtb.xtb_api import *

from datetime import datetime
import time


def get_latest_news(news_sites, date_arr, buy_time):
    day_news = ""
    # going over all required newssites
    for news_site in news_sites:
        # getting correct file name accoring to date time
        file_name = "../data/"+news_site+"/news_" + \
            str(date_arr[0])+"_"+str(date_arr[1]).zfill(2) + \
            "_"+str(date_arr[2]).zfill(2)+".csv"
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


def get_fin_data(stock, date_arr, buy_time):
    # getting all stock prices from specified index
    all_stock_data = get_stock_prizes()
    stock_prices = all_stock_data[stock]
    stock_times = all_stock_data["times"]
    stock_features = []

    print("CAUTION, DATEARR:",date_arr)
    # find correct stock time
    curr_stock_idx = -1
    for idx in range(len(stock_times)-1,0,-1):
        if int(date_arr[0]) == stock_times[idx].year and \
            int(date_arr[1]) == stock_times[idx].month and \
            int(date_arr[2]) == stock_times[idx].day and \
            buy_time == stock_times[idx].hour:
            curr_stock_idx = idx
            break

    # check if current buy time is already in current data
    if idx<0:
        print("ERROR: buy time data not found!!!")

    # go backwards and save previous stock prices
    print("Buy stock:", stock_prices[curr_stock_idx])
    for back_idx in range(curr_stock_idx, curr_stock_idx-NUM_FIN_HISTORY, -1):
        stock_features.append(stock_prices[back_idx])
    
    # create stock features by taking the diff of index prices
    stock_features = np.diff(np.array(stock_features))
    weekday_feat = stock_times[curr_stock_idx].weekday()
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
    drop_idx = []
    for col_idx in range(trainDataset.shape[1]):
        curr_col = trainDataset[:, col_idx]
        if(np.sum(curr_col) < DROP_THRESH):
            drop_idx.append(col_idx)
    print("dropping", len(drop_idx), "features of", trainDataset.shape[1])
    trainDataset = np.delete(trainDataset, drop_idx, 1)

    # adding numerical features
    if ADD_NUMERICAL:
        trainDataset = np.append(trainDataset, numeric_features ,axis=1)

    # training random forest classifier
    xgb_classifier = XGBClassifier()
    if USE_REGRESSOR:
        xgb_classifier = XGBRegressor(objective='reg:squarederror') 
        print("Regressor not implmented yet for daily predict")
        exit()
    xgb_classifier.fit(trainDataset, bin_labels)

    return xgb_classifier, countVector, drop_idx

def daily_predict(date_arr, xgb_classifier, countVector, drop_idx, buy_time, stock, news_sites):
    # getting latest financial data
    latest_numeric_feat = get_fin_data(stock, date_arr, buy_time)

    # getting latest news
    latest_news = get_latest_news(news_sites, date_arr, buy_time)

    # prediction classifier
    predDataset = countVector.transform([latest_news])
    predDataset = predDataset.toarray()

    # dropping features with low occurence
    predDataset = np.delete(predDataset, drop_idx, 1)

    # adding numerical features
    if ADD_NUMERICAL:
        predDataset = np.append(predDataset, latest_numeric_feat ,axis=1)

    # predict daily
    prediction = xgb_classifier.predict(predDataset)
    print("todays prediction:", prediction)

    return prediction


print("start training")
hyp_param = [11, 13, "dax", ["cnbc_finance"]]
#hyp_param = [15, 18, "dax", ["investing_world", "faz_news", "cnn_money", "spiegel_schlagzeilen", "cnbc_world", "spiegel_wirtschaft", "faz_wirtschaft", "bbc_business", "faz_finanzen"]]
# getting train data
get_train_data(hyp_param[0], hyp_param[1], hyp_param[3], hyp_param[2])
# train classifier
xgb_classifier, countVector, drop_idx = train_classifier(hyp_param[0], hyp_param[2], hyp_param[3])

# looping every day until buy time is reached
print("staring every day loop")
buy_minutes = 3
if (hyp_param[0]==9): # buy at 9:30
    buy_minutes+=30
buy_time = [hyp_param[0],3]
sell_time = hyp_param[1]

for day_idx in range(4,21):
    print("day", day_idx)
    # getting current date and time
    today = datetime.now()
    date_time = today.strftime("%Y_%m_%d_%H_%M")
    date_time_arr = date_time.split("_")
    date_time_arr[2]=day_idx
    print("getting date_time_arr:", date_time_arr)

    prediction = daily_predict(date_time_arr, xgb_classifier, countVector, drop_idx, hyp_param[0], hyp_param[2], hyp_param[3])

    



