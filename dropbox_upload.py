import os
from datetime import datetime
import subprocess
import time

def upload_news():
    today = datetime.now()
    date_time = today.strftime("%Y_%m_%d_%H_%M")
    print("start upload on", date_time)
    
    # finding all folders in data
    files = os.listdir("data/")
    news_folders = []
    pathnames = []

    for f in files:
        if ("csv" in f):
            continue
        #print(f)
        news_folders.append(f)
    for folder in news_folders:
        pathname = 'data/'+folder+'/news_'+date_time[:-6]+'.csv'
        if("index_prices" in folder):
            pathname = 'data/'+folder+'/prices_'+date_time[:-6]+'.csv'
        saved_news = []
        if (os.path.isfile(pathname)):
            bashCommand = "/home/pi/Dropbox-Uploader/dropbox_uploader.sh upload /home/pi/trAIder/trAIder/"+pathname+" "+pathname
            print("uploading file:", pathname)
            process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            

print("start uploading loop")
upload_time = "20_00"
two_hours = 60 * 60 * 2

while(True):
    # getting current date and time
    today = datetime.now()
    date_time = today.strftime("%Y_%m_%d_%H_%M")
    print("getting datetime:", date_time)
    date_time_arr = date_time.split("_")
    times_trigger_next = upload_time.split("_")
    print("running if...")
    print(int(times_trigger_next[0]), int(date_time_arr[3]), int(
        times_trigger_next[1]), int(date_time_arr[4]))
    if (int(times_trigger_next[0])-int(date_time_arr[3]) == 0) and (int(times_trigger_next[1])-int(date_time_arr[4]) < 0):
        upload_news()
        print("uploading done, sleeping for", two_hours,"seconds")
        time.sleep(two_hours)
    print("sleeping for 30s")
    time.sleep(30)