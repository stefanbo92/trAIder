import numpy as np
from datetime import datetime, timedelta

from feature_engineering import *
from get_train_data import *
from daily_predict import train_classifier, daily_predict

# resim dates
delta = timedelta(days=1)
start_date = datetime(2021, 8, 1)
end_date = datetime.now() - delta

# train predictor
print("start training")
hyp_param = [13, 16, "dax", ["spiegel_schlagzeilen", "investing_economy", "cnn_world", "bbc_world", "cnbc_world"]]

buy_minutes = 3
if (hyp_param[0]==9): # buy at 9:30
    buy_minutes+=30
buy_time = [hyp_param[0],buy_minutes]
sell_time = hyp_param[1]
# getting train data
get_train_data(hyp_param[0], hyp_param[1], hyp_param[3], hyp_param[2], start_date)
# train classifier
xgb_classifier, countVector, drop_idx = train_classifier(hyp_param[0], hyp_param[2], hyp_param[3])

# loop from start day until today
print("staring every day loop")
out_str=""
total_win = []
while start_date <= end_date:
    # getting current date and time
    today = start_date

    # retrain model on sunday
    if today.weekday() == 7:
        get_train_data(hyp_param[0], hyp_param[1], hyp_param[3], hyp_param[2], (today - delta))
        xgb_classifier, countVector, drop_idx = train_classifier(hyp_param[0], hyp_param[2], hyp_param[3])

    if today.weekday() > 4: # skip weekend
        start_date += delta
        continue

    date_time = today.strftime("%Y_%m_%d_%H_%M")
    date_time_arr = date_time.split("_")
    # faking buy time
    date_time_arr[3]=buy_time[0]
    date_time_arr[4]=buy_time[1]
    print("Current datetime:", date_time)

    # buying
    if (buy_time[0]-int(date_time_arr[3]) == 0) and (buy_time[1]-int(date_time_arr[4]) <= 0):
        # make daily prediction
        prediction = daily_predict(date_time_arr, xgb_classifier, countVector, drop_idx, hyp_param[0], hyp_param[2], hyp_param[3])
        if prediction[0] > 0:
            # buy long
            buy_sign = 1
            print("buying long")
        else:
            # buy short
            buy_sign = -1
            print("buying short")

    # selling
    # faking sell time now
    date_time_arr[3]=sell_time
    if sell_time-int(date_time_arr[3]) == 0:
        # selling position
        print("selling position")
        # logging results
        all_stock_data = get_stock_prizes()
        curr_stock = all_stock_data[hyp_param[2]]
        # getting actual buy and sell price
        today_idx = 0
        sell_price = 0
        for idx in range(len(curr_stock)):
            #print("curr_stock_price:",idx, all_stock_data["times"][idx],curr_stock[idx])
            if(all_stock_data["times"][idx].year == today.year) and \
                (all_stock_data["times"][idx].month == today.month) and \
                    (all_stock_data["times"][idx].day == today.day):
                # found correct day
                today_idx = idx
                if(all_stock_data["times"][idx].hour == hyp_param[1]):
                    sell_price = curr_stock[idx]
                    print("sell_stock", sell_price)
                    break
                if(all_stock_data["times"][idx].hour==hyp_param[0]):
                    buy_price = curr_stock[idx]
                    print("buy_price recalc", buy_price)
        win_percent = ((sell_price - buy_price)/buy_price) * buy_sign * 100
        if (sell_price < 1): # did not find data for selling
            win_percent = 0

        out_str += all_stock_data["times"][today_idx].strftime("%Y_%m_%d_%H_%M") +": Win/Loss --> "+str(round(win_percent,3))+" "+str(buy_sign)+"\n"
        total_win.append(win_percent)

    start_date += delta
print(out_str)
print("average win per day: ", np.mean(np.array(total_win)))




