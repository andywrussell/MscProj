#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 09:33:06 2020

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

def get_movies():
    #movies_df = database_helper.select_query("movies", { "enabled" : "1" })
    movies_df = database_helper.select_query("movies", {"investigate" : "1"})
    movies_df = movies_df.sort_values(by=['movieId'])  
    return gen_movies(movies_df)

def gen_movies(movies_df):
    movies = []
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            movie = Movie(row)
            movies.append(movie)
            pbar.update(1)
    return movies

def get_movie_by_id(movieId): 
    movies_df = database_helper.select_query("movies", { "movieId" : movieId })
    if (not df.empty):
        return Movie(df.iloc[0])
    
    return None

def get_movie_by_title(title):
    movies_df = database_helper.select_query("movies", { "title" : title })
    if (not df.empty):
        return Movie(df.iloc[0])
    
    return None
    
def set_total_revenue_for_movies():
    movies = get_movies();
    with tqdm(total=len(movies)) as pbar:
        for movie in movies:
            total_rev = movie.box_office_df.iloc[movie.box_office_df['weeksOnRelease'].idxmax()]['grossToDate']
            update_params = { "totalRevenue" : total_rev }
            select_params = { "movieId" : movie.movieId }
            database_helper.update_data("movies", update_params = update_params, select_params = select_params)
            pbar.update(1)
            
def get_top_earning(max_movies = 20):
    sql = """SELECT * FROM public.movies 
             WHERE "enabled" = '1'
             ORDER BY "totalRevenue" DESC LIMIT {0}""".format(max_movies)
    top_df = database_helper.get_data(sql)
    return gen_movies(top_df) 

def count_tweets(movieId):
    sql = """
          SELECT "movieid", COUNT(*) 
          FROM movie_tweets2019 
          WHERE "movieid" = {0}
          GROUP BY "movieid"
          """.format(movieId)        
    tweet_count = database_helper.get_data(sql)
    return tweet_count


    

