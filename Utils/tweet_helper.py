#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 17:34:14 2020

@author: andy
"""

import sys
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Utils')

import database_helper
import pandas as pd

def get_tweet_sentiments_scores(movieId):
    analyser = SentimentIntensityAnalyzer()
    tweets =  database_helper.select_geo_tweets(movieId)
    sent_lst = []
    for index, row in tweets.iterrows(): 
        sentiment = analyser.polarity_scores(row['msg'])
        lst_row = {
                    "id" : row["id"],
                    "negative_scr" : sentiment["neg"],
                   "positive_scr" : sentiment["pos"],
                   "neutral_scr" : sentiment["neu"],
                   "compound_scr" : sentiment["compound"],
                   "senti_class" : classify_sentiment(sentiment)
            } 
        sent_lst.append(lst_row)
     
    return pd.DataFrame(sent_lst)
        
def classify_sentiment(sentiment):
    if sentiment["compound"] < -0.05:
        return "negative"
    elif sentiment["compound"] > 0.05:
        return "positive"
    else:
        return "neutral"
    