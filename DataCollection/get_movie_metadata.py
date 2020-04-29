#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 14:30:50 2020

@author: andy
"""

import imdb
import pandas as pd
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Utils')

import database_helper

ia = imdb.IMDb()

#get all movies from db
get_movies_sql = "SELECT * FROM public.movies"
movies_df = database_helper.get_data(get_movies_sql)

def get_imdbIds():
    #find movies on imdb
    for index, row in movies_df.iterrows(): 
        search_results = ia.search_movie(row['title'])
        movie_results = list(filter(lambda x: x.get('kind') == 'movie', search_results))
        
        if (len(movie_results) > 0):
            movie = movie_results[0]
            
            #if there is more than one then get most recent?
            if (len(movie_results) > 1):
                print("Check: ", row['title'])
                #try to get the one from 2019
                year_results = list(filter(lambda x: x.get('year') == 2019, movie_results))
                if (len(year_results) > 0):
                    movie = year_results[0]
                         
            movie_url = ia.get_imdbURL(movie)
            movie_id = ia.get_imdbID(movie)
            
            #update database
            insert_sql = """
            UPDATE movies 
            SET "imdbId" = %s, "url" = %s
            WHERE "movieId" = %s;"""     
            insert_params = (movie_id, movie_url, row["movieId"])
            database_helper.run_query(insert_sql, insert_params)
        
get_imdbIds();

        
    