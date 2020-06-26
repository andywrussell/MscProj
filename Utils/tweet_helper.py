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
    
    