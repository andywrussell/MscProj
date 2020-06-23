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

def get_movies_df():
    movies_df = database_helper.select_query("movies", {"investigate" : "1"})
    movies_df = movies_df.sort_values(by=['movieId'])   
    return movies_df

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
             WHERE "investigate" = '1'
             ORDER BY "totalRevenue" DESC LIMIT {0}""".format(max_movies)
    top_df = database_helper.get_data(sql)
    return gen_movies(top_df) 

def get_lowest_earning(max_movies = 20):
    sql = """SELECT * FROM public.movies 
             WHERE "investigate" = '1'
             ORDER BY "totalRevenue" ASC LIMIT {0}""".format(max_movies)
    bottom_df = database_helper.get_data(sql)
    return gen_movies(bottom_df) 

def count_tweets(movieId):
    sql = """
          SELECT "movieid", COUNT(*) 
          FROM movie_tweets2019 
          WHERE "movieid" = {0}
          GROUP BY "movieid"
          """.format(movieId)        
    tweet_count = database_helper.get_data(sql)
    return tweet_count

def categorize_by_gross_profit():
    movies_df = get_movies_df()
    
    #calculate gross profit based on budget and worldwide gross
    movies_df["worldwide_gross_usd_norm"] = movies_df['worldwide_gross_usd'].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["budget_usd_norm"] = movies_df['budget_usd'].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["gross_profit_usd_norm"] = movies_df["worldwide_gross_usd_norm"] - movies_df["budget_usd_norm"]
    movies_df["gross_profit_usd"] = movies_df["worldwide_gross_usd"].replace('[\£,]', '', regex=True).astype(float) - movies_df["budget_usd"].replace('[\£,]', '', regex=True).astype(float)
    
    custom_bucket_array =[-50, 0, 50, 150, 300, 2500]
    bucket_labels = ['< $0 (Flop)', '$0 < $50m', '$50m < $150m', '$150m < $300m', ' > $300m (BlockBuster)' ]
    
    movies_df['class'] = pd.cut(movies_df['gross_profit_usd_norm'], custom_bucket_array,labels= bucket_labels)
    
    for index, row in movies_df.iterrows(): 
            updates = { "gross_profit_usd" : row["gross_profit_usd"],
                    "profit_class" : row["class"]
                    }
            selects = {"movieId" : row["movieId"]}
            database_helper.update_data("movies", update_params = updates, select_params = selects)
    
    return movies_df

    

