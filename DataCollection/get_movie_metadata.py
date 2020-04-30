#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 14:30:50 2020

@author: andy
"""

import imdb
from tqdm import tqdm
import pandas as pd
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Utils')

import database_helper

ia = imdb.IMDb()

#get all movies from db
get_movies_sql = "SELECT * FROM public.movies"
movies_df = database_helper.get_data(get_movies_sql)
cast_test = None

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
            
def get_metaData():
    #get movie meta data
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            if (row['imdbId']):
                movie = ia.get_movie(str(row['imdbId']))
                year = movie['year']
                if (movie.get('genres')):     
                    genres = ','.join(movie.get('genres'))  
                rating = movie.get('rating')
                votes = movie.get('votes')
                certificates = None
                if (movie.get('certificates')):     
                    certificates = ','.join(movie.get('certificates'))
                
                #update database
                insert_sql = """
                UPDATE movies 
                SET "year" = %s, "genres" = %s, "rating" = %s, "votes" = %s, "certificates" = %s
                WHERE "movieId" = %s;"""     
                insert_params = (year, genres, rating, votes, certificates, row["movieId"])
                database_helper.run_query(insert_sql, insert_params)
            
            pbar.update(1)
            
def get_directors():
    #get movie meta data
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            if (row['imdbId']):
                movie = ia.get_movie(str(row['imdbId']))
                directors = movie.get('director')
                if (directors != None) :
                    for director in directors:
                        #first check if the person exists
                        imdb_id = director.personID  
                        person_df = database_helper.select_query("people", {'imdbId' : imdb_id})
                        if (person_df.empty):
                            database_helper.insert_data("people", {"imdbId": imdb_id, "name": director["name"]})                        
                    
                        #add movie director link
                        database_helper.insert_data("directors", {"p_imdbId" : imdb_id, "m_imdbId" : row['imdbId']})
                
            pbar.update(1)
            
def get_actors():
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            if (row['imdbId']):
                movie = ia.get_movie(str(row['imdbId']))
                cast_list = movie.get('cast')
                if (cast_list != None) :
                    for cast_member in cast_list:
                        character_name = ""
                        if (isinstance(cast_member.currentRole, list)):
                            character_name = ','.join([x['name'] for x in cast_member.currentRole])
                        else:
                            try:
                                character_name = cast_member.currentRole['name']
                            except:   
                                 character_name = "Unknown"
                        
                        #first check if the person exists
                        imdb_id = cast_member.personID  
                        person_df = database_helper.select_query("people", {'imdbId' : imdb_id})
                        if (person_df.empty):
                            database_helper.insert_data("people", {"imdbId": imdb_id, "name": cast_member["name"]})                        
                    
                        #add movie director link
                        database_helper.insert_data("actors", {"p_imdbId" : imdb_id, "m_imdbId" : row['imdbId'], "role": character_name})
                
            pbar.update(1)
    
        
#get_imdbIds()
#get_metaData()
#get_directors()
get_actors()

        
    