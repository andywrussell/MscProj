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

import movie_helper
import database_helper
import mojo_helper
from datetime import datetime

#initialize imdb helper
ia = imdb.IMDb()

#get all movies from db
movies_df = movie_helper.get_movies_df()
#movies_df = movie_helper.get_movies_df()
#movies_df = database_helper.select_query("movies", {"enabled" : '1'})
#movies_df = database_helper.select_query("movies", { "movieId" : 72 })
#movies_df = database_helper.select_query("movies", { "movieId" : 128 })
#movies_df = database_helper.select_query("movies", { "movieId" : 122 })
# movies_df = database_helper.select_query("movies", { "movieId" : 85 })
#movies_df = database_helper.select_query("movies", { "movieId" : 233 })
#movies_df = database_helper.select_query("movies", { "movieId" : 63 })
#movies_df = database_helper.select_query("movies", { "movieId" : 137 })
#movies_df = database_helper.select_query("movies", { "movieId" : 143 })
#movies_df = database_helper.select_query("movies", { "movieId" : 262 })
#movies_df = database_helper.select_query("movies", {"enabled" : "1"})
#movies_df = database_helper.select_query("movies", { "movieId" : 234 })


def get_imdbIds():
    """
    Use movie title to get the imdb id from IMDb api
    """
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
            database_helper.update_data("movies", update_params = { "imdbId" : movie_id, "url" : movie_url}, select_params = { "movieId", row["movieId"]})
            
def get_metaData():
    """
    Use imdbId to retreive metadata from IMDb for each movie in movies_df
    """
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
                update_params = {
                        "year" : year,
                        "genres" : genres,
                        "rating" : rating,
                        "votes" : votes,
                        "certificates" : certificates
                    }
                select_params = { "movieId" : row["movieId"] }
                database_helper.update_data("movies", update_params = update_params, select_params = select_params)
            
            pbar.update(1)
            
def get_directors():
    """
    Use imdb to collect movie directors
    """
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
                            database_helper.insert_data("people", {"imdbId": imdb_id, "fullName": director["name"]})                        
                    
                        #add movie director link
                        database_helper.insert_data("directors", {"p_imdbId" : imdb_id, "m_imdbId" : row['imdbId']})
                
            pbar.update(1)
            
def get_actors():
    "Use imdb to collect movie actors"
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
                            database_helper.insert_data("people", {"imdbId": imdb_id, "fullName": cast_member["name"]})                        
                    
                        #add movie director link
                        database_helper.insert_data("actors", {"p_imdbId" : imdb_id, "m_imdbId" : row['imdbId'], "role": character_name})
                
            pbar.update(1)
    
def get_writers():
    """
    Use imdb to collect movie writers
    """
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            if (row['imdbId']):
                movie = ia.get_movie(str(row['imdbId']))
                writers = movie.get('writer')
                if (writers != None) :
                    for writer in writers:
                        #first check if the person exists
                        imdb_id = writer.personID  
                        person_df = database_helper.select_query("people", {'imdbId' : imdb_id})
                        if (person_df.empty):
                            database_helper.insert_data("people", {"imdbId": imdb_id, "fullName": writer["name"]})                        
                    
                        #add movie director link
                        database_helper.insert_data("writers", {"p_imdbId" : imdb_id, "m_imdbId" : row['imdbId']})
                
            pbar.update(1)
            
def get_keywords():
    """
    Use imdb to collect plot keywords
    """
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            if (row['imdbId']):
                movie = ia.get_movie(str(row['imdbId']), info='keywords')
                try:
                    keywords = ",".join(movie['keywords'])
                except:
                    keywords = None
                    
                database_helper.update_data("movies", update_params = {"keywords" : keywords}, select_params = {"movieId" : row["movieId"]})
            pbar.update(1)
            
def get_synopsis():
    """
    Use imdb to collect long from synopsis
    """
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            if (row['imdbId']):
                movie = ia.get_movie(str(row['imdbId']), info='synopsis')
                try:
                    synopsis = movie['synopsis']
                    database_helper.insert_data("synopsis", {"movieId" : row["movieId"], "summary" : synopsis})    
                except:
                    print(row['title'] + ' (' + row['imdbId'] + ')')
                
            pbar.update(1)
            
def get_release_dates():
    """
    Use imdb to collect long from synopsis
    """
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows():
            movie = ia.get_movie(str(row['imdbId']), info='release dates')
            release_dates = movie['release dates']
            uk  = [i for i in movie['release dates'] if 'UK' in i and not '(' in i]
            if (len(uk) > 0):
                date_string = uk[0].split('::')[1]
                date = datetime.strptime(date_string, '%d %B %Y')
                database_helper.update_data("movies", update_params = { "ukReleaseDate" : date }, select_params = {"movieId" : row["movieId"]})
            else: 
                print("No UK release for ", row.title)
                
            pbar.update(1)
            
def get_cast_notes():
    "Use imdb to collect movie actors"
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            if (row['imdbId']):
                movie = ia.get_movie(str(row['imdbId']))
                cast_list = movie.get('cast')
                if (cast_list != None) :
                    for cast_member in cast_list:                        
                        imdb_id = cast_member.personID
                        updates = { 'notes' : cast_member.notes }
                        selects = {"p_imdbId" : imdb_id, "m_imdbId" : row['imdbId'] }
                        database_helper.update_data("actors", update_params = updates, select_params = selects)
                
            pbar.update(1)
            
def get_mojo_data():
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            if (row['imdbId']):
                stats = mojo_helper.get_mojo_stats(row['imdbId'])
                updates = { "budget_usd" : stats["Budget"],
                           "uk_gross_usd" : stats["UK"],
                           "domestic_gross_usd" : stats["Domestic"],
                           "worldwide_gross_usd" : stats["Worldwide"],
                           "international_gross_usd" : stats["International"]
                           }
                selects = {"movieId" : row["movieId"]}
                database_helper.update_data("movies", update_params = updates, select_params = selects)
            pbar.update(1)
            
            
def get_mojo_box_office():
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            test = mojo_helper.get_uk_box_office_df(row['imdbId'])
            
            #fix dates
            
            
            pbar.update(1)
 
get_mojo_box_office()
#get_mojo_data()
#get_cast_notes()
#get_imdbIds()
#get_metaData()
#get_directors()
#get_actors()
#get_writers()
#get_keywords()
#get_synopsis()
#get_release_dates()
# movie = ia.get_movie('7590074', info='release dates')
# movie['release dates']
# uk  = [i for i in movie['release dates'] if 'UK' in i and not '(' in i]
# premiere = [i for i in movie['release dates'] if 'premiere' in i]

#test = ia.get_movie('3281548', info='synopsis')
            
#test = ia.get_movie(str(movies_df.iloc[0]['imdbId']), info='synopsis')
#synopsis = test['synopsis']    
    