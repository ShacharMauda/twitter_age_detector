import pandas as pd
import tweepy
from tweepy import Cursor
import time
from datetime import datetime, date, timedelta

import json
import os


# TODO: change the error detection method
# TODO: find a better data structure for multiple users

# TODO: Get the api key through config file, 
class Search:
    def __init__(self,consumer_key,consumer_secret):
        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        # auth.set_access_token(access_token, access_token_secret)
        # api = access_token

    def test(self):
        print("search says:", self.auth)
        pass

class User(Search):
    def __init__(self,consumer_key,consumer_secret,screen_names=None):
        super().__init__(consumer_key,consumer_secret)
        if screen_names == None:
            self.screen_names = []
        else:
            self.screen_names = screen_names

    def define_tweets_amount(self, max_tweets=5, max_days_back=30, include_retweets = False):
    # recive a user screen name and iterate its tweets from the most recent back using Cursor
        self.max_tweets = max_tweets
        self.max_days_back = max_days_back
        self.include_retweets = include_retweets

    def test(self):
        super(User,self).test()
        print("screen name = ", self.screen_names)

    def retrive_tweets_json(self):
        """
        recive a list of users screen names and iterate on each users tweets 
        from the most recent back using Cursor
        """
        api = tweepy.API(self.auth)
        end_date = datetime.utcnow() - timedelta(days=int(self.max_days_back))
        user_tweets = []
        tweet_count = 0

        for user in self.screen_names:    
            while True:
                try:
                    for status in Cursor(api.user_timeline, id=user).items():
                        if self.include_retweets == False:
                            if "retweeted_status" not in status._json:
                                user_tweets.append(status._json)
                                tweet_count += 1
                        else:
                            user_tweets.append(status._json)
                            tweet_count += 1

                        if status.created_at < end_date:  # limit by no of days back in time
                            break

                        if tweet_count >= int(self.max_tweets):  # limit to max number of tweets
                            break

                except Exception as err:
                    if '429' in err.reason: # in case rate limit reached try a cooldown
                        print("5 min API cool down")
                        time.sleep(5 * 60)
                        continue
                    else:
                        print(user, " error = ", err.reason) # any other error would result in skipping to the next tweet
                        break
                break
        return user_tweets



