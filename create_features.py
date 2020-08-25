import pandas as pd
import retrieve_user_info
import json
from emoji import UNICODE_EMOJI
import os
import ktrain
import warnings

def get_features(json_data,use_bert = False):
    """
    recives list of tweets (from a single user) in tweety json format and return a panda series of features
    """
    warnings.simplefilter("ignore")

    def json_to_pandas(json):
        """
        recives a list of jsons (as dict object) and returned pandas dataframe where each row is a json array
        """
        tweets_list = []
        for tweet in json:
            df = pd.DataFrame(tweet,index=[None]) # convert the tweet dict to pandas
            user = pd.DataFrame(data = tweet['user'], index=[None]) # get the 'user' dict as pandas df
            user.rename(columns=lambda x: 'user_' + x, inplace=True) # mark user columns
            df = pd.concat([df,user],axis=1) # join user df to tweet df 
            tweets_list.append(df) 
        return pd.concat(tweets_list).reset_index(drop=True)

    def extract_features(data):
        """
        recives a pandas data frame of tweets and return a panda series of features
        """
        def count_upper(text):
            """
            count number of capital latters in the tweet
            """
            return sum(1 for char in text if char.isupper())

        def count_patterns(text,patterns=['.','!','?',',','#']):
            """
            rate of selected char in the tweet
            """
            if len(text) != 0:
                return sum([text.lower().count(pattern)/len(text) for pattern in patterns])
            else:
                return 0
        
        def contain_emoji(s):
            """
            dos the tweet contain emoji's
            """
            if len(s) == 1:
                return s in UNICODE_EMOJI
            else:
                total = sum([1 for i in s if contain_emoji(i)])
                if total > 0:
                    return True
                else:
                    return False

        def emoji_to_words_ratio(s):
            """
            ratio of emojies in relation to number of words
            """
            total = sum([1 for i in s if contain_emoji(i)])/len(s.split(" "))
            if total > 0:
                return total
            else:
                return 0

        if use_bert == True:
            # loading the bert ktrain predictor 
            bio_predictor = ktrain.load_predictor('model_files/bert_bio_regression/predictor_bert_reg_bio_15epoch')
            tweet_predictor = ktrain.load_predictor('model_files/bert_tweet_regression/predictor_bert_reg_tweet_model_1epoch')

            # create a mean age prediction using the BERT prediction for the user bio and tweets
            bert_bio_pred = bio_predictor.predict(data.user_description.values).mean()
            bert_tweet_pred = bio_predictor.predict(data.text.values).mean()

        # rate of tweets which are replay tweets
        data['in_reply_to_status_id'][data.in_reply_to_status_id.isna() == False] = int(1)
        data['in_reply_to_status_id'][data.in_reply_to_status_id.isna() == True] = int(0)
        user_rep_rate = (data.groupby('user_screen_name').in_reply_to_status_id.sum()/data.groupby('user_screen_name').in_reply_to_status_id.count()).values[0]
        
        # rate of tweets which are quate tweets
        data.is_quote_status[data.is_quote_status.isna() == True] = int(0)
        data.is_quote_status[data.is_quote_status != 0 ] = int(1)
        user_quoted_rate = (data.groupby('user_screen_name').is_quote_status.sum()/data.groupby('user_screen_name').is_quote_status.count()).values[0]

        # avrage length of a tweet for this user
        users_all_texts = data.groupby(data.user_screen_name).text.transform(lambda x: ','.join(x)).drop_duplicates().values[0]
        avg_tweet_len = (len(users_all_texts) / data.groupby(data.user_screen_name).text.count()).values[0]
        
        # 
        emojies_in_all_text = contain_emoji(users_all_texts) / data.groupby(data.user_screen_name).text.count().values[0]
        emoji_to_words_ratio = [emoji_to_words_ratio(i) for i in data.user_description]
        emojies_in_bio = [contain_emoji(i) for i in data.user_description]
        tweets_count = data.groupby(data.user_screen_name).text.count().values[0]

        # create a pandas data frame contaning the feature values. (here some of them are also being averaged  across all tweets)
        df = data[['user_followers_count','user_friends_count']]
        df['user_rep_rate'] = user_rep_rate
        df['user_quoted_rate'] = user_quoted_rate
        df['bio_capital_num'] = data.user_description.apply(count_upper)
        df['user_name_capital_num'] = data.user_name.apply(count_upper)
        df['user_screen_name_capital_num'] = data.user_screen_name.apply(count_upper)
        df['text_count_patterns'] = data.text.apply(count_patterns).mean()
        df['text_capital_num'] = data.text.apply(count_upper).mean()
        df['bio_count_patterns'] = data.user_description.apply(count_patterns)
        df['avg_tweet_len'] = avg_tweet_len
        df['emojies_in_all_text'] = emojies_in_all_text
        df['emojies_in_all_text_count'] = emoji_to_words_ratio
        df['emojies_in_bio'] = emojies_in_bio
        df['tweets_count'] = tweets_count

        if use_bert == True:
            df['bert_bio_pred'] = bert_bio_pred
            df['bert_tweet_pred'] = bert_tweet_pred

        # return the first row of the dataframe as a pnad series
        return df.iloc[0]


    data = json_to_pandas(json_data)
    extracted_features = extract_features(data)

    return extracted_features

if __name__ == '__main__':
    pass

