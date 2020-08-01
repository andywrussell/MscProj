#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 17:03:01 2020

@author: andy
"""

#http://darribas.org/gds_scipy16/ipynb_md/04_esda.html
#testing some spatial analysis techniques

import matplotlib.pyplot as plt
import pysal as ps
import pandas as pd
import numpy as np
import geopandas as gpd
from geopandas.tools import sjoin
import sys
import math
import matplotlib.colors as colors
from datetime import datetime
from datetime import timedelta

sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Entities')
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Utils')

from movie import Movie
import database_helper
from matplotlib.lines import Line2D

def calc_surface_expectation(total_pop, total_samp, square_pop, square_samp):
    obs = (total_pop/total_samp) * square_samp
    exp = square_pop
    
    surface = (obs - exp) / math.sqrt(exp)
    
    return surface

def get_cell_color(surface_val):
    if surface_val >= 5:
        return "red"
    
    if surface_val <= -5:
        return "blue"
            
    return "white"

def get_cell_label(surface_val):
    if surface_val >= 5:
        return "Above Expected"
    
    if surface_val <= -5:
        return "Below Expected"
    
    return "Expected"

def plot_chi_sqrd_surface(movieId = 0, normalize_by="All", start_date = None, end_date = None, critical_period=False):
    #fix dates so we include start of start and end of end
    if not start_date == None:
        start_date = datetime.combine(start_date.date(), datetime.min.time())
        
    if not end_date == None:
        end_date = datetime.combine(end_date.date(), datetime.max.time())
    
    #use gb regions for normalizing and for plotting
    #Ordanance survey data contained only the shape files for GB so need to normalize populations by this rather than fishnet which also uses NI
    gb_regions = database_helper.get_geo_data("select * from uk_regions", "geombng")
    gb_regions_count = database_helper.select_region_tweets(start_date=start_date, end_date=end_date)
    
    #check if we are using the entire population of tweets or just the movie populaiton
    if normalize_by == "Movies":
        #normalize by movie tweets
        gb_regions_count = database_helper.select_movie_region_tweets(start_date=start_date, end_date=end_date)
        gb_regions_count = gb_regions_count.drop(columns=['movieid'])
        gb_regions_count = gb_regions_count.groupby(by="cellid").size().reset_index(name="tweet_count")
        
    total_gb_tweets = gb_regions_count["tweet_count"].sum()

    #first step get total tweets in uk fishnet
    uk_fishnet_count = database_helper.select_fishnet_count(start_date=start_date, end_date=end_date)
        
    #now get total movie tweets in uk fishnet
    movie_fishnet_tweets = database_helper.select_movie_fishnet_tweets(movieId, start_date=start_date, end_date=end_date)
    
    #now get movie tweets per cell
    movie_cell_tweets = movie_fishnet_tweets.groupby(by="cellid").size().reset_index(name="movie_tweets")
    
    #now group with total fishnet counts 
    fishnet_movie_comb = uk_fishnet_count.merge(movie_cell_tweets, how='left', on='cellid')
    
    #attach results to geodataframe so it can be plotted 
    uk_fishnet = database_helper.get_geo_data("select * from uk_fishnet", "geombng")
    uk_fishnet = uk_fishnet.rename(columns = {"id" : "cellid"})
    
    uk_fishnet = uk_fishnet.merge(fishnet_movie_comb, how='left', on='cellid')
    
    #replace na with 0
    uk_fishnet = uk_fishnet.fillna(0)
    
    ##get total gb tweets for movie
    gb_movie_fishnet = sjoin(gb_regions, uk_fishnet, how='inner')
    gb_movie_fishnet = gb_movie_fishnet[["cellid", "movie_tweets"]].drop_duplicates().reset_index(drop=True)
    gb_movie_total = gb_movie_fishnet["movie_tweets"].sum()
    
    
    #do expecation calculation
    uk_fishnet['surf_expectation'] = uk_fishnet.apply(lambda row: calc_surface_expectation(total_gb_tweets, gb_movie_total, row["tweet_count"], row["movie_tweets"]), axis = 1)
    
    #replace na with 0 (not all fishnet cells have tweets)
    uk_fishnet = uk_fishnet.fillna(0)
    
    #get cell colors 
    uk_fishnet["color"] = uk_fishnet.apply(lambda row: get_cell_color(row["surf_expectation"]), axis = 1)
    uk_fishnet["label"] = uk_fishnet.apply(lambda row: get_cell_label(row["surf_expectation"]), axis = 1)
    
    #return uk_fishnet
    
    #now do plots     
    fig, ax = plt.subplots(1,figsize=(9,9))
    
    #this takes time, may be useful to create the overlay and store in db then use pandas join/merge to input expectation
    overlay = gpd.overlay(gb_regions, uk_fishnet, how='intersection')
    map_ax = overlay.plot(color=overlay['color'], ax=ax)
 
    title = "Movie Tweets Expectation Map"
 
    #get movie 
    if movieId > 0:
        movies_df = database_helper.select_query("movies", {"movieId" : movieId})
        title = movies_df.iloc[0]["title"] + " Tweet Expecation"  
 
 
    if critical_period:
        title = "{0} (Critical Period)".format(title)
    elif (start_date != None) and (end_date != None):
        title = "{0} ({1} - {2})".format(title, start_date.date(), end_date.date())
 
    ax.set_axis_off()
    #plt.axis('equal')
  
    legend_elements = [Line2D([0], [0], marker='s', color='red', label='Above Expected', markerfacecolor='red', markersize=15),
                     Line2D([0], [0], marker='s', color='white', label='At Expected', markerfacecolor='white', markersize=15),
                     Line2D([0], [0], marker='s', color='blue', label='Below Expected', markerfacecolor='blue', markersize=15)]
  
    ax.legend(handles=legend_elements, loc="upper left")
    plt.title(title)
    plt.show()
    plt.clf()
    plt.cla()
    plt.close()
 
    return overlay
        

