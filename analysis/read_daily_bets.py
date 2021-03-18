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

print("-----------------------------------")
print("Total days played:", len(all_results))
print("Win accuracy:", win_cnt/len(all_results))
print("Total gains in percent:", np.sum(np.array(all_results)))
print("In money:", play_money * lever * np.sum(np.array(all_results))/100, "€")
