import numpy as np
import pickle
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.feature_extraction.text import CountVectorizer

from xgboost import XGBClassifier, XGBRegressor

# PARAMETERS
DROP_THRESH = 3
USE_REGRESSOR = False
ADD_NUMERICAL = True

def get_financial_features(raw_financial_features):
    fin_feat=np.array(raw_financial_features)
    fin_feat=np.diff(fin_feat,axis=1)
    return fin_feat

def clean_text(text):
    text = text.replace('“', '').replace('„', '')
    text = text.replace('[nl]', '')
    text = text.replace(':', '').replace('-', ' ').replace('–', '')
    text = text.replace('  ', ' ').replace('?', '')
    text = text.replace('»', '').replace('«', '')
    text = text.replace('!', '').replace('"', '')
    text = text.replace('+', '').replace('+', '')
    text = text.replace('xxx', '').replace('\'s', '')
    return text

def get_prepared_data():
    # reading raw features and labels
    with open('ml_data/features_raw.data', 'rb') as filehandle:
        # read the data as binary data stream
        features_raw = pickle.load(filehandle)
    with open('ml_data/label.data', 'rb') as filehandle:
        # read the data as binary data stream
        lables = pickle.load(filehandle)
        if len(lables)==0:
            print("Error: No data available to train")
            return np.zeros(0), np.zeros(0), np.zeros(0), np.zeros(0)

    # writing only text features to list
    text_features = []
    raw_financial_features = []
    weekday_feat = []
    for raw_feat in features_raw:
        # removing unneccessary characters from text
        curr_text = clean_text(raw_feat[3])
        text_features.append(curr_text)
        raw_financial_features.append(raw_feat[2])
        weekday_feat.append(raw_feat[1].weekday())

    # getting numerical features
    fin_feat = get_financial_features(raw_financial_features)
    weekday_feat = np.array(weekday_feat).reshape((fin_feat.shape[0],1))
    numeric_features = np.append(fin_feat, weekday_feat, axis=1)

    # creating binary labels
    lables = np.array(lables)
    bin_labels = np.copy(lables)
    bin_labels[lables > 0] = 1
    bin_labels[lables <= 0] = 0

    return np.array(text_features), numeric_features, lables, bin_labels

def train_predict(train_text_features, train_numeric_features, train_lables, \
                   val_text_features, val_numeric_features):

    # creating CountVectorizer
    countVector = CountVectorizer(ngram_range=(2, 2))
    # ngram(2,2) means it will combine the 2 words together and assign the value
    trainDataset = countVector.fit_transform(train_text_features)
    trainDataset = trainDataset.toarray()

    # validation classifier
    valDataset = countVector.transform(val_text_features)
    valDataset = valDataset.toarray()

    # dropping features with low occurence
    drop_idx = []
    for col_idx in range(trainDataset.shape[1]):
        curr_col = trainDataset[:, col_idx]
        if(np.sum(curr_col) < DROP_THRESH):
            drop_idx.append(col_idx)
    print("dropping", len(drop_idx), "features of", trainDataset.shape[1])
    trainDataset = np.delete(trainDataset, drop_idx, 1)
    valDataset = np.delete(valDataset, drop_idx, 1)

    # making labels binary
    train_bin_lables = np.copy(train_lables)
    train_bin_lables[train_lables > 0] = 1
    train_bin_lables[train_lables <= 0] = 0

    # adding numerical features
    if ADD_NUMERICAL:
        trainDataset = np.append(trainDataset, train_numeric_features ,axis=1)
        if (len(val_text_features)>0):
            valDataset = np.append(valDataset, val_numeric_features ,axis=1)

    # training random forstes classifier
    ml_model = None
    predictions = None
    if(USE_REGRESSOR==False):
        xgb_classifier = XGBClassifier(objective='binary:logistic') # , max_depth=10
        xgb_classifier.fit(trainDataset, train_bin_lables, eval_metric='logloss') # sample_weight=np.abs(train_lables)
        ml_model = xgb_classifier
        # performing predictions on validation dataset
        if len(val_text_features):
            predictions = xgb_classifier.predict(valDataset)
    else: # regressor
        xgb_regressor = XGBRegressor(objective='reg:squarederror') 
        xgb_regressor.fit(trainDataset, train_lables)
        ml_model = xgb_regressor
        if len(val_text_features):
            predictions = xgb_regressor.predict(valDataset)
    return predictions, countVector, drop_idx, ml_model

def train_test():
    text_features, numeric_features, lables, bin_labels = get_prepared_data()
    if(len(text_features)==0):
        return None, None

    # split training and test set
    train_split = 0.7
    n_data = len(bin_labels)
    train_text_features = text_features[:int(n_data*train_split)]
    train_numeric_features = numeric_features[:int(n_data*train_split)]
    train_lables = lables[:int(n_data*train_split)]
    val_text_features = text_features[int(n_data*train_split):]
    val_numeric_features = numeric_features[int(n_data*train_split):]
    val_bin_lables = bin_labels[int(n_data*train_split):]
    val_lables = lables[int(n_data*train_split):]

    # train on data and predict
    predictions, _, _,_ = train_predict(train_text_features, train_numeric_features, train_lables, \
                                    val_text_features, val_numeric_features)

    # evaluation statistics
    print("Val predictions:", predictions)
    if(USE_REGRESSOR):
        print("Regressor mean abs error:", np.mean(np.abs(np.subtract(val_lables, predictions))))
        predictions[predictions>0] = 1
        predictions[predictions<=0] = 0
        print("Val label      :", val_lables)
        
    else:
        print("Val label      :", val_bin_lables)
    wrong_samples = np.sum(np.abs(np.subtract(val_bin_lables, predictions)))
    accuracy = (len(val_bin_lables)-wrong_samples)/len(val_bin_lables)
    print("Accuracy:", accuracy)
    report = classification_report(val_bin_lables, predictions)
    print(report)

    # calculate gains
    gains=[]
    total_gain=0
    for idx, pred in enumerate(predictions):
        if pred==val_bin_lables[idx]:
            gains.append(abs(val_lables[idx]))
        else:
            gains.append(-abs(val_lables[idx]))
        total_gain+=gains[-1]
    print("Total Gain:", total_gain,"in",len(gains),"days (avg",total_gain/len(gains),"per day)")
    return gains, accuracy

#train_test()

'''
# use Tfidf
print("use Tfidf")
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
tfidfVector = TfidfVectorizer(ngram_range=(2,2))
trainDataset = tfidfVector.fit_transform(train_text_features)
randomClassifier = RandomForestClassifier(n_estimators=200, criterion='entropy')
randomClassifier.fit(trainDataset, train_lables)
valDataset = tfidfVector.transform(val_text_features)
predictions = randomClassifier.predict(valDataset)
print("Val label      :", val_lables)
print("Val predictions:", predictions)
wrong_samples=np.sum(np.abs(np.subtract(val_lables,predictions)))
accuracy=(len(val_lables)-wrong_samples)/len(val_lables)
print("Accuracy:", accuracy)
report = classification_report(val_lables, predictions)
print(report)
'''
