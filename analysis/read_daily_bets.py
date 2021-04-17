import numpy as np 

# opening daily_bets.txt
daily_bets = open("daily_bets.txt", 'r')
all_results = []
for line in daily_bets:
    if ("Win" in line):
        line_arr = line.split(" ")
        all_results.append(float(line_arr[3]))
        print(all_results[-1])

end_result = 0
win_cnt = 0
for result in all_results:
    end_result+=result
    if(result>0):
        win_cnt+=1

play_money = 1000
lever = 20
cost = play_money * lever / 10000

print("-----------------------------------")
print("Total days played:", len(all_results))
print("Win accuracy:", round(win_cnt/len(all_results),3))
print("Total gains in percent:", round(np.sum(np.array(all_results)),3), "average per day:", round(np.sum(np.array(all_results))/len(all_results),3))
print("In money:", play_money * lever * np.sum(np.array(all_results))/100, "€ (approx cost:",len(all_results) * cost,")")
