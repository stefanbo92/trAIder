import numpy as np 
import os


def get_daily_bets_str():
    out_str = ""
    out_arr = []
    # opening daily_bets.txt
    daily_bets = open(os.path.dirname(os.path.abspath(__file__))+"/daily_bets.txt", 'r')
    all_results = []
    for line in daily_bets:
        if ("Win" in line):
            line_arr = line.split(" ")
            all_results.append(float(line_arr[3]))
            out_arr.append(line_arr[0][:-1] + " -> " + str(all_results[-1]) + "\n")

    end_result = 0
    win_cnt = 0
    for result in all_results:
        end_result+=result
        if(result>0):
            win_cnt+=1

    play_money = 1000
    lever = 20
    cost = play_money * lever / 10000

    # if there are more than 6 entries, remove old ones
    if (len(out_arr) > 6):
        out_arr = out_arr[len(out_arr)-6:]
        out_arr[0] = "... \n"
    out_str = out_str.join(out_arr)

    out_str += "----------------------------------- \n"
    out_str += "Total days played: " + str(len(all_results)) + "\n"
    out_str += "Win accuracy: " + str(round(win_cnt/len(all_results),3)) + "\n"
    out_str += "Total gains in percent: " + str(round(np.sum(np.array(all_results)),3)) + " average per day:" + str(round(np.sum(np.array(all_results))/len(all_results),3)) + "\n"
    out_str += "In money: "+ str(play_money * lever * np.sum(np.array(all_results))/100) + "€ (approx cost:" + str(len(all_results) * cost)+ ") \n"
    return out_str

print(get_daily_bets_str())