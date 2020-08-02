#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file contains a set of methods used to check the movies table for missing data

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
        
def check_actors():
    """Check the database to make sure actors have been collected for every movie."""
    
    movies_df = database_helper.select_query("movies", {"enabled" : '1'})
    movies = []
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            movie = Movie(row)
            movies.append(movie)
            
            #if there are no actors print movie to command line
            if (len(movie.actors) == 0): 
                print (movie.title + " (" + movie.imdbId + ") no actors")
            pbar.update(1) 
            
def check_writers():
    """Check the database to make sure writers have been collected for every movie."""
    
    movies_df = database_helper.select_query("movies", {"enabled" : '1'})
    movies = []
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            movie = Movie(row)
            movies.append(movie)
            
            #if there are no writers print movie to command line
            if (len(movie.writers) == 0):
                print (movie.title + " (" + movie.imdbId + ") no writers")
            pbar.update(1) 
            
def check_directors():
    """Check the database to make sure directors have been collected for every movie."""
    
    movies_df = database_helper.select_query("movies", {"enabled" : '1'})
    movies = []
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            movie = Movie(row)
            movies.append(movie)
            
            #if there are no directors print movie to command line
            if (len(movie.directors) == 0):
                print (movie.title + " (" + movie.imdbId + ") no writers")
            pbar.update(1) 
            
def check_synopsis():
    """Check the database to make sure synopsis have been collected for every movie."""
    
    movies_df = database_helper.select_query("movies", {"enabled" : '1'})
    movies = []
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            movie = Movie(row)
            movies.append(movie)
            
            #if there is no synopsis print movie to command line
            if (movie.synopsis == ''):
                print (movie.title + " (" + movie.imdbId + ") no synopsis")
            pbar.update(1) 




