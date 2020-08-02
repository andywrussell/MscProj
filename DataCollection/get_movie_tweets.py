#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contains functions used to identify movie tweets and assign sentiment

Created on Mon May 11 11:19:15 2020

@author: andy
"""

from tqdm import tqdm
import pandas as pd
import sys
import re
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Entities')
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Utils')

from movie import Movie
import database_helper
import movie_helper
import tweet_helper



def get_movie_tweets():
    """Function to search the tweets2019 table for all movie related tweets. Tweets are bulk inserted per movie for huge speed improvement"""
    
    movies = movie_helper.get_movies()
    with tqdm(total=len(movies)) as pbar:
        for movie in movies:
            
            #build list of tweet search terms out of twitter handles and hashtags
            search_terms = []
            if (movie.twitterHandle != None):
                search_terms.append("%" + movie.twitterHandle.strip().lower() + "%")
            
            for tag in movie.hashtags:
                search_terms.append("%#" + tag.strip().lower() + "%")
              
            if len(search_terms) > 0:
                #search tweets in db using list of terms
                movieTweets = database_helper.search_tweets(search_terms, "OR") 
                
                #assign tweets with movie id and insert into movie_tweets2019 table
                movieTweets['movieid'] = movie.movieId
                movieTweets = movieTweets.drop(columns=['geomwgs', 'inuk'])
                database_helper.bulk_insert_df("movie_tweets2019", movieTweets, movieTweets.columns.values.tolist())
            else:
                #if no handles or hastags print to console 
                print("SEARCH ON TITLE FOR " + movie.title)
        
            pbar.update(1)   
         
        
def update_tweet_sentiments():
    """Function to assign sentiment socres and classification to all tweets in the movie_tweets2019 table"""
    
    with tqdm(total=len(movies)) as pbar:
        
        #assign tweet sentiment to tweets for each movie 
        for movie in movies:
            sentiment_df = tweet_helper.get_tweet_sentiments_scores(movie.movieId)
            
            #update the db with newly assigned tweet sentiment and classes
            for index, row in sentiment_df.iterrows(): 
                
                update_params = {
                        "negative_scr" : row["negative_scr"],
                        "positive_scr" : row["positive_scr"],
                        "neutral_scr" : row["neutral_scr"],
                        "compound_scr" :  row["compound_scr"],
                        "senti_class" : row["senti_class"]
                    }
                select_params = { "id" : row["id"] }
                database_helper.update_data("movie_tweets2019", update_params = update_params, select_params = select_params)
            pbar.update(1)  
        
