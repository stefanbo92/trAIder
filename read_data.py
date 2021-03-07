file_name = 'data/welt_wirtschaft_24_12_2020.csv'

news_file = open(file_name, 'r+')
saved_news = []
for line in news_file:
    line_array = line.split(",")
    saved_news.append(line_array)

date = saved_news[0][1].split("_")
print("News from", date[0]+"."+date[1]+"."+date[2]+":")
print("")
for line_array in saved_news:
    print("No", line_array[0]+":", line_array[2])
    print(line_array[3])
    print("")

print("Index Prices:")
print("DAX30 -->", saved_news[0][4])
print("S&P500 -->", saved_news[0][5])
print("DowJones30 -->", saved_news[0][6])
print("NASDAQ Composite -->", saved_news[0][7])
print("Nikkei225 -->", saved_news[0][8])
