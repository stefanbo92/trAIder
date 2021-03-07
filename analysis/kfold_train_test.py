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



def kfold_train_test(k_folds):
    # getting features and labels from file
    text_features, numeric_features, lables, bin_labels = get_prepared_data()
    if(len(text_features)==0):
        return None, None

    predictions_combined = []
    for train_round in range(k_folds):
        #print("Training round", train_round, "of", k_folds)

        # split training and test set
        n_data = len(lables)
        slice_len = int(1/k_folds * n_data)
        curr_slice_start = train_round * slice_len
        slice_index = np.arange(n_data)[curr_slice_start:curr_slice_start+slice_len]

        train_text_features = np.delete(text_features, slice_index)
        train_numeric_features = np.delete(numeric_features, slice_index, axis=0)
        train_lables = np.delete(bin_labels, slice_index)
        val_text_features = text_features[slice_index]
        val_numeric_features = numeric_features[slice_index]
        val_lables = bin_labels[slice_index]

        # train on data and predict
        predictions = train_predict(train_text_features, train_numeric_features, train_lables, \
                                    val_text_features, val_numeric_features, val_lables)

        predictions_combined.append(predictions)

        # evaluation
        #print("Val label      :", val_lables)
        #print("Val predictions:", predictions)
        wrong_samples = np.sum(np.abs(np.subtract(val_lables, predictions)))
        accuracy = (len(val_lables)-wrong_samples)/len(val_lables)
        print("Accuracy round",train_round,":", accuracy)
        #report = classification_report(val_lables, predictions)
        #print(report)
    
    # calculate gains
    gains=[]
    total_gain=0
    predictions_combined = np.array(predictions_combined).reshape(-1)
    bin_labels = bin_labels[:predictions_combined.shape[0]]
    print("Combined Performance: ")
    
    wrong_samples = np.sum(np.abs(np.subtract(bin_labels, predictions_combined)))
    accuracy = (len(bin_labels)-wrong_samples)/len(bin_labels)
    print("Accuracy:", round(accuracy,2))
    report = classification_report(bin_labels, predictions_combined)
    print(report)
    for idx, pred in enumerate(predictions_combined):
        if pred==bin_labels[idx]:
            gains.append(abs(lables[idx]))
        else:
            gains.append(-abs(lables[idx]))
        total_gain+=gains[-1]
    print("Total Gain:", round(total_gain,2),"in",len(gains),"days (avg",round(total_gain/len(gains),3),"per day)")
    return gains, accuracy
    

#kfold_train_test(5)


