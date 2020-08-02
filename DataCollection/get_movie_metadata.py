#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Set of untility functions used to gather movie meta data from imdb and other sources

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


def get_imdbIds():
    """
    Function which uses the movie title from BFI to get the imdb id from IMDb api
    """
    
    #get all movies from db
    movies_df = movie_helper.get_movies_df()
    
    for index, row in movies_df.iterrows(): 
        
        #use the api to search imdb for films with the the title
        search_results = ia.search_movie(row['title'])
        
        #only interested in movie objects
        movie_results = list(filter(lambda x: x.get('kind') == 'movie', search_results))
        
        if (len(movie_results) > 0):
            #take the first results by default
            movie = movie_results[0]
            
            #if there is more than one then get most recent?
            if (len(movie_results) > 1):
                #flag issue to console so movie can be manually checked
                print("Check: ", row['title'])
                
                #try to get the one from 2019
                year_results = list(filter(lambda x: x.get('year') == 2019, movie_results))
                if (len(year_results) > 0):
                    movie = year_results[0]
              
            #extract imdb url and id using API
            movie_url = ia.get_imdbURL(movie)
            movie_id = ia.get_imdbID(movie)
            
            #update database
            database_helper.update_data("movies", update_params = { "imdbId" : movie_id, "url" : movie_url}, select_params = { "movieId", row["movieId"]})
            
def get_metaData():
    """
    Function which uses imdbId to retreive metadata from IMDb for each movie
    """
    #get all movies from db
    movies_df = movie_helper.get_movies_df()
      
    #get movie meta data
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            
            #if an imdbid exists use it to look up the API
            if (row['imdbId']):
                
                #get base meta data from imdb
                movie = ia.get_movie(str(row['imdbId']))
                year = movie['year']
                
                #created delimited list of genre strings
                if (movie.get('genres')):     
                    genres = ','.join(movie.get('genres'))  
                    
                rating = movie.get('rating')
                votes = movie.get('votes')
                
                #create delimited list of movie certificates
                certificates = None
                if (movie.get('certificates')):     
                    certificates = ','.join(movie.get('certificates'))
                
                #update database with collected meta data
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
    Function which uses imdb to collect movie directors
    """
    #get all movies from db
    movies_df = movie_helper.get_movies_df()
    
    #get movie meta data
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            
            #if imdbid exists user it to look up the API
            if (row['imdbId']):
                movie = ia.get_movie(str(row['imdbId']))
                
                #get list of directors
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
    """Function which uses imdb to collect movie actors"""
    
    #get all movies from db
    movies_df = movie_helper.get_movies_df()    
    
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            
            #if imdbid exists user it to look up the API
            if (row['imdbId']):
                movie = ia.get_movie(str(row['imdbId']))
                
                #get list of cast
                cast_list = movie.get('cast')
                if (cast_list != None) :
                    for cast_member in cast_list:
                        
                        #Try to get the name of the character
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
    Function which uses imdb id to get list of writers
    """
    
    #get all movies from db
    movies_df = movie_helper.get_movies_df()    
    
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows():
            
             #if imdbid exists user it to look up the API
            if (row['imdbId']):
                movie = ia.get_movie(str(row['imdbId']))
                
                #get list of writers
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
    Function which uses imdb id to collect plot keywords
    """
    
    #get all movies from db
    movies_df = movie_helper.get_movies_df()    
    
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            
            #if imbdid exists use it to look up the API
            if (row['imdbId']):
                
                #get list of keywords and created delimted string
                movie = ia.get_movie(str(row['imdbId']), info='keywords')
                try:
                    keywords = ",".join(movie['keywords'])
                except:
                    keywords = None
                 
                #update the movies table in the db
                database_helper.update_data("movies", update_params = {"keywords" : keywords}, select_params = {"movieId" : row["movieId"]})
            pbar.update(1)
            
def get_synopsis():
    """
    Function which uses imdb to collect long from synopsis.
    """
    #get all movies from db
    movies_df = movie_helper.get_movies_df()    
    
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            
            #if imdb id exists use it to look up the API
            if (row['imdbId']):
                
                #get synponsis and update the db
                movie = ia.get_movie(str(row['imdbId']), info='synopsis')
                try:
                    synopsis = movie['synopsis']
                    database_helper.insert_data("synopsis", {"movieId" : row["movieId"], "summary" : synopsis})    
                except:
                    #throw exception and print to console if synopsis does not exist
                    print(row['title'] + ' (' + row['imdbId'] + ')')
                
            pbar.update(1)
            
def get_release_dates():
    """
    Funciton which uses imdb to collect uk release date of films.
    """
    #get all movies from db
    movies_df = movie_helper.get_movies_df()    
    
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows():
            
            #get list of release dates from API
            movie = ia.get_movie(str(row['imdbId']), info='release dates')
            release_dates = movie['release dates']
            
            #try to extract UK release dates (string from imdb is a mess)
            uk  = [i for i in movie['release dates'] if 'UK' in i and not '(' in i]
            if (len(uk) > 0):
                #if successful update the db with the release date
                date_string = uk[0].split('::')[1]
                date = datetime.strptime(date_string, '%d %B %Y')
                database_helper.update_data("movies", update_params = { "ukReleaseDate" : date }, select_params = {"movieId" : row["movieId"]})
            else: 
                #if no uk release date found print to console
                print("No UK release for ", row.title)
                
            pbar.update(1)
            
def get_cast_notes():
    """Function which uses imdb to collect cast notes eg Credited/Uncredited"""
    
    #get all movies from db
    movies_df = movie_helper.get_movies_df()    
    
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            
            #if imdbid exists use it to collect cast notes
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
    """
    Function which uses imdb id to scrape movie financial summary from BoxOfficeMojo
    """
    
    #get all movies from db
    movies_df = movie_helper.get_movies_df()    
    
    
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            
            #if imdb id exists use it to scrape info from box office mojo
            if (row['imdbId']):
                
                #get stats and update the db
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
    """
    Function which uses imdb id to scrape movie weekend box office data from BoxOfficeMojo
    """
    
    #get movies from db
    movies_df = movie_helper.get_movies_df()
    
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            #get df of box office info for each weekend
            weekend_df = mojo_helper.get_uk_box_office_df(row['imdbId'])
            weekend_df["movieId"] = row["movieId"]
            
            #insert into the database 
            database_helper.bulk_insert_df("weekend_box_office_mojo", weekend_df, weekend_df.columns.values.tolist())
            pbar.update(1)
            
def get_mojo_run_info():
    """
    Function to calculate weekend box office summaries from mojo info
    """
    
    #get movies from the db and calulate run info
    run_info_df = movie_helper.get_movie_run_info()
    
    with tqdm(total=len(run_info_df)) as pbar:
        for index, row in run_info_df.iterrows():
            #update the database
            updates =   {"end_weekend" : row['end_weekend'], 
                   "total_weekends" : row['total_weekends'], 
                   "total_release_weeks" : row['total_release_weeks'], 
                   "first_run_end" : row['first_run_end'],
                   "first_run_weeks" : row['first_run_weeks']}
            
            selects = {"movieId" : row["movieId"]}
            database_helper.update_data("movies", update_params = updates, select_params = selects)
            
            pbar.update(1)
            
def get_mojo_rank_info():
    """
    Function to calculate weekend box office rank summaries from mojo info
    """
    
    #get movies from the db and calulate rank info
    rank_info_df = movie_helper.get_highest_mojo_rank()
    
    with tqdm(total=len(rank_info_df)) as pbar:
        for index, row in rank_info_df.iterrows():   
            
            #update the database
            updates =   {"best_rank" : int(row['best_rank']), 
                          'weekends_at_best_rank' : int(row['weekends_at_best_rank']), 
                          'weekends_in_top_3' : int(row['weekends_in_top_3']), 
                          'weekends_in_top_5' : int(row['weekends_in_top_5']), 
                          'weekends_in_top_10' : int(row['weekends_in_top_10']), 
                          'weekends_in_top_15' : int(row['weekends_in_top_15'])}
            selects = {"movieId" : int(row["movieId"])}
            database_helper.update_data("movies", update_params = updates, select_params = selects)
            
            pbar.update(1)
    
def get_critical_period():
    """
    Function to calculate the film critical period based on the release date and weekend box office info
    """
    
    #get movies from df and calculate crticial period
    movies_df = movie_helper.get_critical_period()
    
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            
            #update the database            
            updates =   {"critical_start" : row['critical_start'], 
                          'critical_end' : row['critical_end']}
            selects = {"movieId" : int(row["movieId"])}
            database_helper.update_data("movies", update_params = updates, select_params = selects)
            
            pbar.update(1)
 

    