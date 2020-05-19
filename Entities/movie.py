#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 11 14:12:31 2020

@author: andy
"""

import json
import jsonpickle
from json import JSONEncoder

import sys
import re
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Utils')

import database_helper
from person import Actor, Director, Writer
from trailers import Trailer
from weekend_box_office import WeekendBoxOffice

class Movie:
    def __init__(self, db_row):
        self.movieId = db_row.movieId
        self.imdbId = db_row.imdbId
        self.title = db_row.title
        self.distributor = db_row.distributor
        self.country = db_row.country
        self.url = db_row.url
        self.year = db_row.year
        self.genres = db_row.genres.split(',') if db_row.genres != None else []
        self.rating = db_row.rating
        self.votes = db_row.votes
        self.certificates = db_row.certificates.split(',') if db_row.certificates != None else []
        self.keywords = db_row.keywords.split(',') if db_row.keywords != None else []
        self.get_cast()
        self.get_directors()
        self.get_writers()
        self.get_trailers()
        self.get_synopsis()
        self.get_box_office()
        
        
    def get_cast(self):
        actors_df = database_helper.select_query("actors", {"m_imdbId" : self.imdbId})
        self.actors = []
        self.actors_df = actors_df
        for index, row in actors_df.iterrows(): 
            actor = Actor(row)
            self.actors.append(actor)
    
    def get_directors(self):
        directors_df = database_helper.select_query("directors", {"m_imdbId" : self.imdbId})
        self.directors = []
        self.directors_df = directors_df
        for index, row in directors_df.iterrows(): 
            director = Director(row)
            self.directors.append(director)
    
    def get_writers(self):
        writers_df = database_helper.select_query("writers", {"m_imdbId" : self.imdbId})
        self.writers = []
        self.writers_df = writers_df
        for index, row in writers_df.iterrows(): 
            writer = Writer(row)
            self.writers.append(writer)
    
    def get_trailers(self):
        trailers_df = database_helper.select_query("trailers", { "movieId" : self.movieId })
        self.trailers = []
        self.trailers_df = trailers_df
        for index, row in trailers_df.iterrows(): 
            trailer = Trailer(row)
            self.trailers.append(trailer)    
        return
        
    def get_synopsis(self):
        synopsis_df = database_helper.select_query("synopsis", {"movieId" : self.movieId })
        self.synopsis_df = synopsis_df
        self.synopsis = ''
        if (not synopsis_df.empty):
            self.synopsis = synopsis_df.iloc[0].summary
        #get synopsis
        return
        
    def get_tweets(self):
        #get tweets
        return
        
    def get_box_office(self):
        box_office_df = database_helper.select_query("weekend_box_office", {"movieId" : self.movieId })
        self.box_office = []
        self.box_office_df = box_office_df
        for index, row in box_office_df.iterrows(): 
            box_office = WeekendBoxOffice(row)
            self.box_office.append(box_office)   
        return
    
    def toJSON(self):
        return jsonpickle.encode(self, unpicklable=False)
        #return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    