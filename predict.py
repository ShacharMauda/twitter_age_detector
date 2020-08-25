from create_features import get_features
from retrieve_user_info import User
import pickle
import sys
import configparser

def predict(screen_name):
    """
    """
    api_info = [] # use args/kwargs
    a = User(api_info[0],api_info[1], screen_name)
    a.define_tweets_amount()
    results = (get_features(a.retrive_tweets_json()))
    reg_model = pickle.load(open('age_predictor_GradientBoostingRegressor_noBERT.pkl', 'rb')) #load the boosting model which dos the final prediction
    clf_model = pickle.load(open('age_predictor_GradientBoostingClassifier_3_equal_bins_noBERT.pkl', 'rb'))
    print('age regression prediction:')
    print(reg_model.predict([results])[0])
    print('age group classification:')
    age_groups = {1:"14 - 22",2:"22-34",3:"34+"}
    print(age_groups[clf_model.predict([results])[0]])
    return

if __name__ == '__main__':
    # TODO: Get the api key through config file, 
    predict([sys.argv[1]])
"""
    # predict a user's age (not iterable for several users) by providing screen name handle. using tweepy to retrive data.
    user = retrieve_user_info.retrive_json(sys.argv[1])
    data = features.get_features(user) # create pandas dataframe
    reg_model = pickle.load(open('age_predictor_GradientBoostingRegressor_noBERT.pkl', 'rb')) #load the boosting model which dos the final prediction
    clf_model = pickle.load(open('age_predictor_GradientBoostingClassifier_3_equal_bins_noBERT.pkl', 'rb'))
    print('age regression prediction:')
    print(reg_model.predict([data])[0])
    print('age group classification:')
    print(clf_model.predict([data])[0])
    file_transfer.remove_bert_models() #delete the bert models
"""