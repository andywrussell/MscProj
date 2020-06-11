#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
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

movies_df = database_helper.select_query("movies", { "enabled" : "1" })
movies_df = movies_df.sort_values(by=['movieId'])

trailers_df = database_helper.select_query("trailers")

movie_hastags = ['#movies', '#film', '#movie', '#cinema', '#films']

movies = []
with tqdm(total=len(movies_df)) as pbar:
    for index, row in movies_df.iterrows(): 
        movie = Movie(row)
        movies.append(movie)
        pbar.update(1)
    
#testq = database_helper.select_lower_like("tweets2019", {"msg": "%" + movies[0].twitterHandle.lower() + "%"})
def jumanji():
    movie = movies[25]
    #params = {"msg": "%" + movie.title.lower() + "%"}
    #movieTweets = database_helper.select_lower_like("tweets2019", {"msg": "%" + movie.title.lower() + "%"})
    title = re.sub(r'[^\w\s]','',movie.title)
    search_terms =[ "%" + title.strip().lower() + "%"]
    if (movie.twitterHandle != None):
       # handleTweets = database_helper.select_lower_like("tweets2019", {"msg": "%" + movie.twitterHandle.lower() + "%"})
       # movieTweets.append(handleTweets) 
        search_terms.append("%" + movie.twitterHandle.strip().lower() + "%")
    
    for tag in movie.hashtags:
        #hashTweets = database_helper.select_lower_like("tweets2019", {"msg": "%#" + tag.lower() + "%"})
        #movieTweets.append(hashtweets)
        search_terms.append("%#" + tag.strip().lower() + "%")

    movieTweets = database_helper.search_tweets(search_terms, "OR")  
   # movieTweets = database_helper.search_tweets(search_terms, "OR") 

def get_movie_tweets():
    with tqdm(total=len(movies)) as pbar:
        #get by handle
        for movie in movies:
            
            #params = {"msg": "%" + movie.title.lower() + "%"}
            #movieTweets = database_helper.select_lower_like("tweets2019", {"msg": "%" + movie.title.lower() + "%"})
            title = re.sub(r'[^\w\s]','',movie.title)
            search_terms =[ "%" + title.strip().lower() + "%"]
            if (movie.twitterHandle != None):
               # handleTweets = database_helper.select_lower_like("tweets2019", {"msg": "%" + movie.twitterHandle.lower() + "%"})
               # movieTweets.append(handleTweets) 
                search_terms.append("%" + movie.twitterHandle.strip().lower() + "%")
            
            for tag in movie.hashtags:
                #hashTweets = database_helper.select_lower_like("tweets2019", {"msg": "%#" + tag.lower() + "%"})
                #movieTweets.append(hashtweets)
                search_terms.append("%#" + tag.strip().lower() + "%")
                
            movieTweets = database_helper.search_tweets(search_terms, "OR")    
            
            for index, row in movieTweets.iterrows(): 
                database_helper.insert_data("movie_tweets", {"movieId": movie.movieId, "tweetId": row['id']})                        
                    
            pbar.update(1)   
                
                
get_movie_tweets()
#jumanji()
#for movie in movies:
    
