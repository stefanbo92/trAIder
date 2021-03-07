import os
from collections import Counter

skip_list = ["die", "der", "und", "–", "das", "in", "mit", "für", "den", "ist", "zu", "ein",
             "sie", "sich", "im", "auf", "von", "an", "es", "eine", "wird", "sind", "dem", "doch", "nicht", "auch",
             "wie", "hat", "was", "vor", "so", "des", "aus", "als", "werden", "müssen", "welt", "noch",
             "um", "einen", "", "bei", "einer", "jetzt", "nur", "nun", "über", "am", "er", "kann",
             "einem", "diese", "haben", "gegen", "bis", "durch", "stehen", "schon", "ihre", "wer", "oder",
             "muss", "alles", "gibt", "diesen", "wir", "nach", "dabei", "alle", "jeden", "können", "will",
             "viele", "bereits", "denn", "ende", "beim", "warum", "unter", "the", "to", "of", "xxx", "a",
             "and", "for", "on", "as", "is", "us", "are", "with", "from", "after", "more", "that"]

def wordFrequency(string):
    # converting the string into lowercase and remove dots
    string = string.lower()
    string = string.replace(".", "")
    string = string.replace("\n", "")
    # Whenever we encounter a space, break the string
    string = string.split(" ")
    print("total of",len(string),"words")
    # Initializing a dictionary to store the frequency of words
    word_frequency = {}
    # Iterating through the string
    for i in string:
        if i in skip_list:
            continue
        if len(i)<7:
            #continue
            pass
        if i in word_frequency:  # If the word is already in the keys, increment its frequency
            word_frequency[i] += 1
        else:  # It means that this is the first occurence of the word
            word_frequency[i] = 1

    # sort word frequency
    word_counter = Counter(word_frequency)
    print(word_counter)
    return(word_frequency)


def count_words(news_site):
    # finding all files in news_site
    files = os.listdir("../data/"+news_site+"/")
    saved_news = []
    all_news = ""

    for f in files:
        if ("csv" in f):
            # print(f)
            pathname = "../data/"+news_site+"/"+f
            if (os.path.isfile(pathname)):  # database for current date is available already
                prices_file = open(pathname, 'r+')
                for line in prices_file:
                    saved_news.append(line)
                    line_arr = line.split(",")
                    all_news += line_arr[2]+" "+line_arr[3]+" "

    word_freq = wordFrequency(all_news)
    return word_freq

def count_all_words():
    # finding all folders and files in data
    saved_news = []
    all_news = ""
    folders = os.listdir("../data/")
    for folder in folders:
        if ("csv" in folder) or ("index_prices" in folder):
            continue
        files = os.listdir("../data/"+folder+"/")

        # looping over all files in folder
        for f in files:
            if ("csv" in f):
                #print(f)
                pathname = "../data/"+folder+"/"+f
                if (os.path.isfile(pathname)):  # database for current date is available already
                    prices_file = open(pathname, 'r+')
                    for line in prices_file:
                        saved_news.append(line)
                        line_arr = line.split(",")
                        all_news += line_arr[2]+" "+line_arr[3]+" "

    word_freq = wordFrequency(all_news)
    return word_freq

def get_mentions(news_site, word):
    if(news_site=="all"):
        word_freq=count_all_words()
    else:
        word_freq=count_words(news_site)
    
    num=0
    if(word in word_freq):
        num=word_freq[word]
    print("Mentions of",word,"in",news_site+":",num)

    


#count_words("welt_wirtschaft")
#count_words("spiegel_schlagzeilen")
#count_words("bbc_business")
count_all_words()

#get_mentions("spiegel_schlagzeilen", "corona")