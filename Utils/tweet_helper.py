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
import geopandas as gpd
from geopandas.tools import sjoin
import re
import numpy as np

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

def get_tweet_sentiment_scores_clean(movieId):
    analyser = SentimentIntensityAnalyzer()
    tweets =  database_helper.select_geo_tweets(movieId)
    sent_lst = []
    for index, row in tweets.iterrows(): 
        clean_msg = clean_tweet(row['msg'])
        sentiment = analyser.polarity_scores(clean_msg)
        lst_row = {
                    "id" : row["id"],
                    "negative_scr" : sentiment["neg"],
                   "positive_scr" : sentiment["pos"],
                   "neutral_scr" : sentiment["neu"],
                   "compound_scr" : sentiment["compound"],
                   "senti_class" : classify_sentiment(sentiment),
                   "msg" : row["msg"],
                   "clean_msg" : clean_msg
            } 
        sent_lst.append(lst_row)
     
    return pd.DataFrame(sent_lst)
       
 
def classify_sentiment(sentiment):
    if sentiment["compound"] <= -0.05:
        return "negative"
    elif sentiment["compound"] >= 0.05:
        return "positive"
    else:
        return "neutral"
    

def get_tweet_regions(movieId):
    tweets =  database_helper.select_geo_tweets(movieId)
    tweets.dropna(subset=["geombng"], inplace=True)
    gb = gpd.read_file("../../ProjectData/Data/GB/european_region_region.shp")
    gb_tweets = sjoin(tweets, gb, how='inner')
    gb_tweets["region"] = gb_tweets["NAME"].str.replace("Euro Region", "").str.strip()
    return gb_tweets


def get_genre_region_tweets(genre):
    
    gb = gpd.read_file("../../ProjectData/Data/GB/european_region_region.shp")
    output_df = pd.DataFrame(columns=['senti_class', 'counts', 'genre'])

    genre_movies = database_helper.select_movies_by_genre(genre)
    
    region_tweets = get_tweet_regions(genre_movies.iloc[0]['movieId'])
    
    for index, row in genre_movies.iterrows():
        if index > 0:
            my_region_tweets = get_tweet_regions(row["movieId"])
            region_tweets = region_tweets.append(my_region_tweets)
        
    return region_tweets


#https://towardsdatascience.com/almost-real-time-twitter-sentiment-analysis-with-tweep-vader-f88ed5b93b1c
def remove_pattern(input_txt, pattern):
    r = re.findall(pattern, input_txt)
    for i in r:
        input_txt = re.sub(i, '', input_txt)        
    return input_txt

def clean_tweet(msg):
    # remove twitter Return handles (RT @xxx:)
    msg = remove_pattern(msg, "RT @[\w]*:")
    # remove twitter handles (@xxx)
    msg = remove_pattern(msg, "@[\w]*")
    # remove URL links (httpxxx)
    msg = remove_pattern(msg, "https?://[A-Za-z0-9./]*")
    # remove special characters, numbers, punctuations (except for #)
    #msg = msg.replace(msg, "[^a-zA-Z#]", " ")
   # msg = np.core.defchararray.replace(msg, "[^a-zA-Z#]", " ")
    
    return str(msg).strip()
    
def get_max_date():
    sql = """
            SELECT MAX (created_at)
            FROM tweets2019;"""
          
    max_date = database_helper.get_data(sql)
    return max_date.iloc[0]['max']
    