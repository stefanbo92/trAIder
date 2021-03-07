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

def get_daily_data():
    return [["lol"], [2]]

def daily_predict():
    # getting train features and labels from file
    text_features, numeric_features, lables, bin_labels = get_prepared_data()
    if(len(text_features)==0):
        return None, None

    #getting daily features
    daily_text, daily_numeric = get_daily_data()

    # creating CountVectorizer
    countVector = CountVectorizer(ngram_range=(2, 2))
    # ngram(2,2) means it will combine the 2 words together and assign the value
    trainDataset = countVector.fit_transform(text_features)
    trainDataset = trainDataset.toarray()

    # prediction classifier
    predDataset = countVector.transform(daily_text)
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
        predDataset = np.append(predDataset, daily_numeric ,axis=1)

    # training random forest classifier
    xgb_classifier = XGBClassifier()
    xgb_classifier.fit(trainDataset, train_lables)

    

hyp_param = [13, 18, "sp500", ["cnbc_finance", "wsj_world", "bbc_business", "cnbc_business", "bbc_world", "faz_finanzen", "cnn_news", "investing_economy", "cnn_money", "investing_stock"]]
# getting train data
get_train_data(hyp_param[0], hyp_param[1], hyp_param[3], hyp_param[2])
daily_predict()


