#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 15 10:40:34 2020

@author: andy
"""
from tqdm import tqdm
import sys
import re
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Entities')
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Utils')

from movie import Movie
import database_helper

# movies_df = database_helper.select_query("movies", {"enabled" : '1'})
# movies = []
# with tqdm(total=len(movies_df)) as pbar:
#     for index, row in movies_df.iterrows(): 
#         movies.append(Movie(row))
#         pbar.update(1)
        
def check_actors():
    movies_df = database_helper.select_query("movies", {"enabled" : '1'})
    movies = []
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            movie = Movie(row)
            movies.append(movie)
            if (len(movie.actors) == 0):
                print (movie.title + " (" + movie.imdbId + ") no actors")
            pbar.update(1) 
            
def check_writers():
    movies_df = database_helper.select_query("movies", {"enabled" : '1'})
    movies = []
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            movie = Movie(row)
            movies.append(movie)
            if (len(movie.writers) == 0):
                print (movie.title + " (" + movie.imdbId + ") no writers")
            pbar.update(1) 
            
def check_directors():
    movies_df = database_helper.select_query("movies", {"enabled" : '1'})
    movies = []
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            movie = Movie(row)
            movies.append(movie)
            if (len(movie.directors) == 0):
                print (movie.title + " (" + movie.imdbId + ") no writers")
            pbar.update(1) 
            
def check_synopsis():
    movies_df = database_helper.select_query("movies", {"enabled" : '1'})
    movies = []
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            movie = Movie(row)
            movies.append(movie)
            if (movie.synopsis == ''):
                print (movie.title + " (" + movie.imdbId + ") no synopsis")
            pbar.update(1) 
               
            
#check_actors()
#check_writers()
#check_directors()
check_synopsis()





