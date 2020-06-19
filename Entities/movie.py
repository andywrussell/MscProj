#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 11 14:12:31 2020

@author: andy
"""

import json
import jsonpickle
from json import JSONEncoder
from decimal import Decimal
import matplotlib.pyplot as plt
import pandas as pd
import sys
import re
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Utils')

import database_helper
from person import Actor, Director, Writer
from trailers import Trailer
from weekend_box_office import WeekendBoxOffice
import geopandas as gpd
from geopandas.tools import sjoin
import matplotlib.dates as mdates
import scipy.signal
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


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
        self.hashtags = db_row.hashtags.split(',') if db_row.hashtags != None else []
        self.twitterHandle = db_row.twitterHandle
        self.totalRevenue = db_row.totalRevenue
        self.ukReleaseDate = db_row.ukReleaseDate
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
    
    def plot_weekend_revenues(self):
        self.box_office_df['weekendGross_thou'] = self.box_office_df['weekendGross'].replace('[\£,]', '', regex=True).astype(float) / 1000
        self.box_office_df['weekendStart'] = pd.to_datetime(self.box_office_df['weekendStart']) 
        self.box_office_df.set_index('weekendStart')['weekendGross_thou'].plot()
        plt.xticks(self.box_office_df['weekendStart'])
        plt.xlabel("Weekend Starting")
        plt.ylabel("Weekend Gross (£0000)")
        plt.title(self.title + " Weekend Takings")
        plt.show()
        plt.clf()
        plt.cla()
        plt.close()
        return
    
    def plot_weekend_vs_total(self):
        self.box_office_df['weekendGross_thou'] = self.box_office_df['weekendGross'].replace('[\£,]', '', regex=True).astype(float) / 1000
        self.box_office_df['grossToDate_thou'] = self.box_office_df['grossToDate'].replace('[\£,]', '', regex=True).astype(float) / 1000    
        self.box_office_df['weekendStart'] = pd.to_datetime(self.box_office_df['weekendStart']) 
        self.box_office_df.set_index('weekendStart')['weekendGross_thou'].plot()
        self.box_office_df.set_index('weekendStart')['grossToDate_thou'].plot()
        plt.xticks(self.box_office_df['weekendStart'])
        plt.xlabel("Weekend Starting")
        plt.ylabel("Weekend Gross (£0000)")
        plt.title(self.title + " Weekend Takings")
        plt.show()
        plt.clf()
        plt.cla()
        plt.close()
        
    def plot_geotweets(self, normalize = True):
        #NB TIDY THIS UP
        regional_pop = { 'Scotland Euro Region' :  5463300,  
                'East Midlands Euro Region' : 4835928, 
                'London Euro Region' : 8961989, 
                'North West Euro Region' : 7341196, 
                'West Midlands Euro Region' : 5934037,
                'Yorkshire and the Humber Euro Region' : 5502967,
                'South East Euro Region' : 9180135, 
                'North East Euro Region' : 2669941,
                'Wales Euro Region' : 3152879, 
                'Eastern Euro Region' : 6236072,
                'South West Euro Region' : 5624696} 
  
        title = "{0} tweets per region".format(self.title)
        map_col = 'counts'
        gb = gpd.read_file("../../ProjectData/Data/GB/european_region_region.shp")
        tweets =  database_helper.select_geo_tweets(self.movieId)
        gb_tweets = sjoin(tweets, gb, how='inner')
        tweet_freq = gb_tweets.groupby('NAME').size().reset_index(name='counts')
        if normalize:
            tweet_freq['population'] = tweet_freq['NAME'].map(regional_pop)
            tweet_freq["norm_count"] = tweet_freq['counts'] / tweet_freq['population']
            tweet_freq["norm_count"] = (tweet_freq['counts'] / tweet_freq['population']) * 1000000
            map_col = 'norm_count'
        map_freq = gb.merge(tweet_freq, left_on='NAME', right_on='NAME')
        fig, ax = plt.subplots(1, 1)
        ax.axis('off')
        ax.set_title(title)
        fig.set_dpi(100)
        map_freq.plot(column=map_col, ax=ax, legend=True, cmap='OrRd')
        
    def plot_tweets_over_time(self):
        releaseDate = self.ukReleaseDate
        endWeekend = self.box_office_df.iloc[self.box_office_df['weeksOnRelease'].idxmax()].weekendEnd
        fig, ax = plt.subplots()
        ax.axvspan(*mdates.datestr2num([str(releaseDate), str(endWeekend)]), color='skyblue', alpha=0.5)
        tweets =  database_helper.select_geo_tweets(self.movieId)
        tweets['date'] = tweets['created_at'].dt.date
        date_freq = tweets.groupby('date').size().reset_index(name='count') 
        date_freq.sort_values('date')
        date_freq['date'] = pd.to_datetime(date_freq['date'], errors='coerce')
        indexes, _ = scipy.signal.find_peaks(date_freq['count'], height=7, distance=2.1)
        #date_freq.set_index('date')['count'].plot(markevery=indexes.tolist())
        plt.plot(date_freq['date'], date_freq['count'], marker='D',markerfacecolor='r', markevery=indexes.tolist())
        
        print('Peaks are: %s' % (indexes))
        #plt.xticks(date_freq['date'])
        plt.xlabel("Date")
        plt.ylabel("Tweet Count")
        plt.title(self.title + " Tweets over time")
        plt.show()
        
    def plot_tweet_sentiment_over_time(self, avg = False):
        analyser = SentimentIntensityAnalyzer()
        tweets =  database_helper.select_geo_tweets(self.movieId)
        tweet_sentiment = []
        for index, row in tweets.iterrows(): 
            sentiment = analyser.polarity_scores(row['msg'])
            tweet_sentiment.append(sentiment['compound'])
            
        tweets['compound_sentiment'] = tweet_sentiment
        tweets['date'] = tweets['created_at'].dt.date
        date_sentiment = tweets.groupby(['date'], as_index = False).sum()
        date_sentiment.sort_values('date')
        date_sentiment['date'] = pd.to_datetime(date_sentiment['date'], errors='coerce')
        date_sentiment['count'] = tweets.groupby('date').size().reset_index(name='count')['count']
        date_sentiment["compound_norm"] = date_sentiment['compound_sentiment'] / date_sentiment['count']
        
        y_col = 'compound_norm' if avg else 'compound_sentiment'
        
        indexes, _ = scipy.signal.find_peaks(date_sentiment[y_col], height=7, distance=2.1)
        #date_freq.set_index('date')['count'].plot(markevery=indexes.tolist())
        plt.plot(date_sentiment['date'], date_sentiment[y_col], marker='D',markerfacecolor='r', markevery=indexes.tolist())
        
        print('Peaks are: %s' % (indexes))
        #plt.xticks(date_freq['date'])
        plt.xlabel("Date")
        plt.ylabel("Tweet Sentiment")
        plt.title(self.title + " Tweet sentiment over time")
        plt.show()
