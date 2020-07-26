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
import movie_helper
import tweet_helper


# movies_df = database_helper.select_query("movies", { "enabled" : "1" })
# movies_df = movies_df.sort_values(by=['movieId'])

# trailers_df = database_helper.select_query("trailers")

# movie_hastags = ['#movies', '#film', '#movie', '#cinema', '#films']

# movies = []
# with tqdm(total=len(movies_df)) as pbar:
#     for index, row in movies_df.iterrows(): 
#         movie = Movie(row)
#         movies.append(movie)
#         pbar.update(1)
    
#testq = database_helper.select_lower_like("tweets2019", {"msg": "%" + movies[0].twitterHandle.lower() + "%"})
# def jumanji():
#     movie = movies[25]
#     #params = {"msg": "%" + movie.title.lower() + "%"}
#     #movieTweets = database_helper.select_lower_like("tweets2019", {"msg": "%" + movie.title.lower() + "%"})
#     title = re.sub(r'[^\w\s]','',movie.title)
#     search_terms =[ "%" + title.strip().lower() + "%"]
#     if (movie.twitterHandle != None):
#        # handleTweets = database_helper.select_lower_like("tweets2019", {"msg": "%" + movie.twitterHandle.lower() + "%"})
#        # movieTweets.append(handleTweets) 
#         search_terms.append("%" + movie.twitterHandle.strip().lower() + "%")
    
#     for tag in movie.hashtags:
#         #hashTweets = database_helper.select_lower_like("tweets2019", {"msg": "%#" + tag.lower() + "%"})
#         #movieTweets.append(hashtweets)
#         search_terms.append("%#" + tag.strip().lower() + "%")

#     movieTweets = database_helper.search_tweets(search_terms, "OR")  
#    # movieTweets = database_helper.search_tweets(search_terms, "OR") 

#movies = movie_helper.get_top_earning()
movies = movie_helper.get_movies()

#aladdin = movie_helper.get_movie_by_id(254)
#movies = [aladdin]

def get_movie_tweets():
    with tqdm(total=len(movies)) as pbar:
        #get by handle
        for movie in movies:
            
            #params = {"msg": "%" + movie.title.lower() + "%"}
            #movieTweets = database_helper.select_lower_like("tweets2019", {"msg": "%" + movie.title.lower() + "%"})
          #  title = re.sub(r'[^\w\s]','',movie.title)
          #  search_terms =[ "%" + title.strip().lower() + "%"]
            search_terms = []
            if (movie.twitterHandle != None):
               # handleTweets = database_helper.select_lower_like("tweets2019", {"msg": "%" + movie.twitterHandle.lower() + "%"})
               # movieTweets.append(handleTweets) 
                search_terms.append("%" + movie.twitterHandle.strip().lower() + "%")
            
            for tag in movie.hashtags:
                #hashTweets = database_helper.select_lower_like("tweets2019", {"msg": "%#" + tag.lower() + "%"})
                #movieTweets.append(hashtweets)
                search_terms.append("%#" + tag.strip().lower() + "%")
              
            if len(search_terms) > 0:
                movieTweets = database_helper.search_tweets(search_terms, "OR") 
                movieTweets['movieid'] = movie.movieId
                movieTweets = movieTweets.drop(columns=['geomwgs', 'inuk'])
                database_helper.bulk_insert_df("movie_tweets2019", movieTweets, movieTweets.columns.values.tolist())
            else:
                print("SEARCH ON TITLE FOR " + movie.title)
        
            pbar.update(1)   
         
        
def update_tweet_sentiments():
    with tqdm(total=len(movies)) as pbar:
        #get by handle
        for movie in movies:
            sentiment_df = tweet_helper.get_tweet_sentiments_scores(movie.movieId)
            for index, row in sentiment_df.iterrows(): 
                #update database
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
            


#update_tweet_sentiments()    

# for movie in movies:
#     count_df = movie_helper.count_tweets(movie.movieId)
#     count = count_df.iloc[0]['count'] if not count_df.empty else 0
#     print(movie.title + " (" + str(movie.movieId) +"): " + str(count))
    
# movie = movie_helper.get_movie_by_id(1)
# search_terms = []
# if (movie.twitterHandle != None):
#    # handleTweets = database_helper.select_lower_like("tweets2019", {"msg": "%" + movie.twitterHandle.lower() + "%"})
#    # movieTweets.append(handleTweets) 
#     search_terms.append("%" + movie.twitterHandle.strip().lower() + "%")

# for tag in movie.hashtags:
#     #hashTweets = database_helper.select_lower_like("tweets2019", {"msg": "%#" + tag.lower() + "%"})
#     #movieTweets.append(hashtweets)
#     search_terms.append("%#" + tag.strip().lower() + "%")
  
# if len(search_terms) > 0:
#     movieTweets = database_helper.search_tweets(search_terms, "OR") 
#     movieTweets['movieid'] = movie.movieId
#     database_helper.bulk_insert_df("movie_tweets2019", movieTweets, movieTweets.columns.values.tolist())
# else:
#     print("SEARCH ON TITLE FOR " + movie.title)
