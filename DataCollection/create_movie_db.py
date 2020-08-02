#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions used to create the initial db based from the BFI box office data

Created on Mon Apr 27 14:58:04 2020

@author: andy
"""

import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Utils')

import bfi_helper
import database_helper
from tqdm import tqdm


def add_movies_to_db():
    """Function which creates a unique list of movies from BFI data and inserts into DB"""
    
    #get full film set 
    film_df = bfi_helper.get_raw_data()
    film_df_sub = film_df[['Film', 'Country of Origin', 'Distributor']].drop_duplicates()
    film_df_unq = film_df.drop_duplicates()
    
    with tqdm(total=len(film_df_unq)) as pbar:
        for index, row in film_df_unq.iterrows(): 
            
            #check that the movie has not been added yet
            existing = database_helper.select_query("movies", {"title" : row["Film"]})
            if (existing.empty):
                #insert into db
                database_helper.insert_data("movies", {"title" : row['Film'], "distributor" : row['Distributor'], "country" : row['Country of Origin']})
            pbar.update(1)

def add_box_office():
    """Function which adds the weekend box office data from the BFI into the db"""
    
    #get full film set 
    film_df = bfi_helper.get_raw_data()
    film_df_sub = film_df[['Film', 'Country of Origin', 'Distributor']].drop_duplicates()
    film_df_unq = film_df.drop_duplicates()
    
    with tqdm(total=len(film_df)) as pbar:
        for index, row in film_df.iterrows(): 
            
            #get the movie id and use it to insert weekend data into the db
            movie_df = database_helper.select_query("movies", {"title" : row['Film']})
            movie_id = int(movie_df.iloc[0]['movieId'])
      
            percentage_change = None
            try:
                percentage_change = float(row['% change on last week'])
            except ValueError:
                percentage_change = None
                
            insert_params = {
                "movieId" : movie_id, 
                "weeksOnRelease" : row['Weeks on release'], 
                "noOfcinemas" : row['Number of cinemas'], 
                "weekendGross" : row['Weekend Gross'], 
                "percentageChange" : percentage_change, 
                "siteAverage" : row['Site average'], 
                "grossToDate" : row['Total Gross to date'], 
                "weekendStart" : row['weekendStart'], 
                "weekendEnd" : row['weekendEnd'], 
                "rank" : row['Rank']
                }
            database_helper.insert_data("weekend_box_office", insert_params)

            pbar.update(1)

