import os
import numpy as np
import datetime


from feature_engineering import *
from get_train_data import *
from xtb.xtb_api import *

from datetime import datetime
import time


def get_fin_data(stock, curr_date, buy_time):
    # getting all stock prices from specified index and extracting features
    all_stock_data = get_stock_prizes()
    stock_features = get_stock_features(all_stock_data, stock, [curr_date], buy_time)[0]
    
    # create stock features by taking the diff of index prices
    stock_features = np.diff(np.array(stock_features))
    weekday_feat = curr_date.weekday()
    numeric_features = np.append(stock_features, weekday_feat)
 
    return np.reshape(numeric_features, (1,-1))


def train_classifier():
    # getting train features and labels from file
    text_features, numeric_features, lables, bin_labels = get_prepared_data()
    if(len(text_features)==0):
        return None, None, None

    _, countVector, drop_idx, ml_model = train_predict(text_features, numeric_features, lables, [], [])

    if USE_REGRESSOR: # regressor not yet implemented
        print("Regressor not implmented yet for daily predict")
        exit()

    return ml_model, countVector, drop_idx

def daily_predict(curr_date, ml_model, countVector, drop_idx, buy_time, stock, news_sites):
    # getting latest financial data
    latest_numeric_feat = get_fin_data(stock, curr_date, buy_time)

    # getting latest news
    latest_news = get_news(news_sites, [curr_date], buy_time)[0]
    latest_news = clean_text(latest_news)

    # getting count vector of latest news
    predDataset = countVector.transform([latest_news])
    predDataset = predDataset.toarray()
    # dropping features with low occurence
    predDataset = np.delete(predDataset, drop_idx, 1)

    # adding numerical features
    if ADD_NUMERICAL:
        predDataset = np.append(predDataset, latest_numeric_feat ,axis=1)
        # checking if financial features were found
        if latest_numeric_feat.shape[1] < NUM_FIN_HISTORY: 
            print("!!! ERROR !!! No financial data found for",curr_date)
            return [0]

    # predict daily
    prediction = ml_model.predict(predDataset)
    print("todays prediction:", prediction)

    return prediction


if __name__ == '__main__':
    print("start training")
    hyp_param = [13, 16, "dax", ["cnbc_finance", "investing_world"]]
    # getting train data
    get_train_data(hyp_param[0], hyp_param[1], hyp_param[3], hyp_param[2])
    # train classifier
    xgb_classifier, countVector, drop_idx = train_classifier()

    # looping every day until buy time is reached
    print("staring every day loop")
    buy_minutes = 3
    if (hyp_param[0]==9): # buy at 9:30
        buy_minutes+=30
    buy_time = [hyp_param[0],buy_minutes]
    sell_time = hyp_param[1]
    my_xtb = MyXTB()
    while(True):
        # getting current date and time
        today = datetime.now()
        print("getting datetime:", today)
        if today.weekday() > 4: # skip weekend
            time.sleep(9999)
            continue
        
        # buying
        if (buy_time[0]-int(today.hour) == 0) and (buy_time[1]-int(today.minute) <= 0):
            # make daily prediction
            prediction = daily_predict(today, xgb_classifier, countVector, drop_idx, hyp_param[0], hyp_param[2], hyp_param[3])
            if prediction[0] > 0:
                # buy long
                buy_sign = 1
                my_xtb.buy_stonks("long")
                print("buying long")
            else:
                # buy short
                buy_sign = -1
                my_xtb.buy_stonks("short")
                print("buying short")
            print("buying done, sleeping for 3999 seconds")
            time.sleep(3999) # sleep for one hour

        # selling
        #print("selling if",sell_time,"==", int(date_time_arr[3]))
        if sell_time-int(today.hour) == 0:
            # selling position
            print("selling position")
            my_xtb.sell_stonks_save()
            # logging results
            time.sleep(200) # wait until latest prices were written to fill
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
                out_str = all_stock_data["times"][-1].strftime("%Y_%m_%d_%H_%M") +": Win/Loss --> "+str(round(win_percent,3))+" "+str(buy_sign)+"\n"
                file_object.write(out_str)
            time.sleep(9999) # sleep for two hours

        # wait and loop
        #print("sleeping for 30s")
        time.sleep(60)




