#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Set of functions specifically for producing visualizations of the spatial data

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
import seaborn as sns

sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Entities')
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Utils')

from movie import Movie
import database_helper
from matplotlib.lines import Line2D

def calc_surface_expectation(total_pop, total_samp, square_pop, square_samp):
    """
    Helper function for calculating expectation score for expectation map
    
    :param total_pop: total population tweet count for normalizing
    :param total_samp: total sample tweet count
    :param square_pop: total population tweets in cell
    :param square_samp: total sample tweets in call
    :return float representing expectation score
    """
    obs = (total_pop/total_samp) * square_samp
    exp = square_pop
    
    surface = (obs - exp) / math.sqrt(exp)
    
    return surface

def get_cell_color(surface_val):
    """
    Helper function for getting cell colour based on expectation score
    
    :param surface_val: expectation score of cell
    :return string representing color of cell
    """
    
    if surface_val >= 5:
        return "red"
    
    if surface_val <= -5:
        return "blue"
            
    return "white"

def get_cell_label(surface_val):
    """
    Helper function for getting cell label based on expectation score
    
    :param surface_val: expectation score of cell
    :return string representing cell label
    """
    
    if surface_val >= 5:
        return "Above Expected"
    
    if surface_val <= -5:
        return "Below Expected"
    
    return "Expected"

def plot_chi_sqrd_surface(movieId = 0, normalize_by="All", start_date = None, end_date = None, critical_period=False):
    """
    Function for generating expectation maps
    
    :param movieId: integer movieId for creating expecation score for movie tweets
    :param normalize_by: string val indicating if scores should be normalized by all tweets, or movie tweets
    :param start_date: datetime of start date for filtering tweets
    :param end_date: datetime of end_date for filtering tweets
    :param critical_period: bool indicating if movie tweets should only be counted over critical period
    """   
    
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

def plot_movie_tweets_kde(movieId = 0, start_date=None, end_date=None, senti_class = None):
    """
    Function for generating kde plots of tweets (FILTERS NOT WIRED UP)
    
    :param movieId: integer movieId for creating expecation score for movie tweets
    :param start_date: datetime of start date for filtering tweets
    :param end_date: datetime of end_date for filtering tweets
    :param senti_class: string for filtering tweets by sentiment
    """  
    
    #http://darribas.org/gds_scipy16/ipynb_md/06_points.html
    
    #load uk regions shape file
    gb = gpd.read_file("../../ProjectData/Data/GB/european_region_region.shp")
        
    fig, ax = plt.subplots(1,figsize=(11,9))
    
    #no need to do slow spatial join
    gb_tweets = database_helper.select_movie_region_tweets_with_geo()
    gb_tweets["lat"] = gb_tweets["geombng"].y
    gb_tweets["lng"] = gb_tweets["geombng"].x
    
    gb.plot(ax=ax)
    
    title = "Movie Tweet Hotspots"
    
    sns.kdeplot(gb_tweets['lng'], gb_tweets['lat'], 
                shade=True, shade_lowest=False, cmap='viridis',
                 ax=ax, bw=25000, legend=True)


    
    ax.set_axis_off()
    plt.title(title)
    plt.show()
    plt.clf()
    plt.cla()
    plt.close()
    
def plot_movie_tweets_map(movieId = 0, normalize=False, start_date=None, end_date=None, critical_period = False):
    """
    Function for generating heatmap of movie tweets
    
    :param movieId: integer movieId for creating expecation score for movie tweets
    :param start_date: datetime of start date for filtering tweets
    :param end_date: datetime of end_date for filtering tweets
    :param critical_period: bool indicating if tweets should be filtered to crticial period
    """  
    
    #select movie tweets with region cell id and unit id attached
    region_movie_tweets = database_helper.select_movie_region_tweets(movieId, start_date=start_date, end_date=end_date) 
    
    #group by region unit_id to per region tweet count
    tweet_freq = region_movie_tweets.drop(columns=['movieid'])
    tweet_freq = region_movie_tweets.groupby(by="unit_id").size().reset_index(name="movie_tweet_count")
    
    map_col = "movie_tweet_count"
    
    title = "Regional Movie Tweets"
    movie_title = ""
    if movieId > 0:
        movies_df = database_helper.select_query("movies", {"movieId" : movieId})
        movie_title = movies_df.iloc[0]["title"]
        title = movie_title + " Tweets"
    
    #if normalize generate column (movie tweets per million tweets)
    if normalize:
        tweet_region_counts = database_helper.select_query("tweets_region_count")
        tweet_freq = tweet_region_counts.merge(tweet_freq, on="unit_id", how="left")
        
        #fill na with 0
        tweet_freq = tweet_freq.fillna(0)
        tweet_freq["norm_count"] = (tweet_freq['movie_tweet_count'] / tweet_freq['tweet_count']) * 1000000
        map_col = "norm_count"
        
        #title = "Regional Movie Tweets (per million tweets)"
        #if movieId > 0:
            #title = movie_title + " Tweets (per million tweets)"
     
    #check if we need to filter by critical period
    if critical_period:
        title = "{0} (Critical Period)".format(title)
    elif (start_date != None) and (end_date != None):
        title = "{0} ({1} - {2})".format(title, start_date.date(), end_date.date())
    
    #merge with shape file
    gb = gpd.read_file("../../ProjectData/Data/GB/european_region_region.shp")
    map_freq = gb.merge(tweet_freq, left_on='UNIT_ID', right_on='unit_id')
    
    #plot
    fig, ax = plt.subplots(1, 1, figsize=(11, 9))
    ax.axis('off')
    ax.set_title(title)
    fig.set_dpi(100)
    map_freq.plot(column=map_col, ax=ax, legend=True, cmap='OrRd')
    plt.show()
    
    return map_freq

def plot_region_tweets_bar(movieId = 0, normalize=False, start_date=None, end_date=None, critical_period=True):
    """
    Function for generating bar plot of regional movie tweets
    
    :param movieId: integer movieId for creating expecation score for movie tweets
    :param normalize: bool indicating if tweet counts should be normalized
    :param start_date: datetime of start date for filtering tweets
    :param end_date: datetime of end_date for filtering tweets
    :param critical_period: bool indicating if tweets should be filtered to crticial period
    """  
    
    #select movie tweets with region cell id and unit id attached
    region_movie_tweets = database_helper.select_movie_region_tweets(movieId, start_date=start_date, end_date=end_date)
    
    #group by region unit_id to per region tweet count
    tweet_freq = region_movie_tweets.drop(columns=['movieid'])
    tweet_freq = region_movie_tweets.groupby(by="unit_id").size().reset_index(name="movie_tweet_count")
    
    plot_col = "movie_tweet_count"
    
    title = "Regional Movie Tweets"
    ylabel = "Movie Tweet"
    movie_title = ""
    if movieId > 0:
        movies_df = database_helper.select_query("movies", {"movieId" : movieId})
        movie_title = movies_df.iloc[0]["title"]
        title = movie_title + " Tweets"
    
    #if normalize generate column (movie tweets per million tweets)
    tweet_region_counts = database_helper.select_query("tweets_region_count")
    
    if normalize:
        tweet_freq = tweet_region_counts.merge(tweet_freq, on="unit_id", how="left")
        
        #fill na with 0
        tweet_freq = tweet_freq.fillna(0)
        tweet_freq["norm_count"] = (tweet_freq['movie_tweet_count'] / tweet_freq['tweet_count']) * 1000000
        plot_col = "norm_count"
        
        title = "Regional Movie Tweets (per million tweets)"
        if movieId > 0:
            title = movie_title + " Tweets (per million tweets)"
        ylabel = "Movie Tweets (per million tweets)"
    else: 
        regions = tweet_region_counts[["unit_id", "region"]]
        tweet_freq = tweet_freq.merge(regions, on="unit_id", how="left")
     

    #check if we need to filter by the critical period
    if critical_period:
        title = "{0} (Critical Period)".format(title)
    elif (start_date != None) and (end_date != None):
        title = "{0} ({1} - {2})".format(title, start_date.date(), end_date.date())
        
    
    #create bar plot
    ax = sns.barplot(x="region", y=plot_col, data=tweet_freq)
    ax.set(xlabel='Region', ylabel=ylabel)
    plt.title(title)
    plt.xticks(rotation=90)
    plt.show()
        
    return tweet_freq

def get_most_popular_movie_per_region(start_date=None, end_date=None, senti_class=None, ignore_list = [28,121], senti_percentage = False, critical_period=False):
    """
    Function to get the most popular move per region by tweet count
    
    :param start_date: datetime of start date for filtering tweets
    :param end_date: datetime of end_date for filtering tweets
    :param senti_class: string to filter tweets by sentiment
    :param ignore_list: integer list of movie ids to ignore
    :param senti_percentage: bool indicating favourites should be based on sentiment percentage
    :param critical_period: bool indicating if tweets should be filtered to crticial period
    
    :return dataframe of regions and their favourite movies
    """  
    
    #get all regional tweets according to date and sentiment filters
    region_movie_tweets = database_helper.select_movie_region_tweets(start_date=start_date, end_date=end_date, senti_class=senti_class)
    
    #check if we need to filter by the crticial period
    if critical_period:
        movies_df = movie_helper.get_movies_df()
        small_movies_df = movies_df[["movieId", "critical_start", "critical_end"]]
        small_movies_df = small_movies_df.rename(columns={"movieId" : "movieid"})
        region_movie_tweets = region_movie_tweets.merge(small_movies_df, how="left", on="movieid")
        region_movie_tweets = region_movie_tweets[(region_movie_tweets["created_at"] >= region_movie_tweets["critical_start"]) 
                                                     & (region_movie_tweets["created_at"] <= region_movie_tweets["critical_end"])]
    
    #group tweets by region and movie
    region_movie_grouped = region_movie_tweets.groupby(by=["unit_id", "movieid"]).size().reset_index(name="tweet_count")
    
    #check if we should use sentiment percentage (i.e film with highest percentage of positive tweets)
    group_col = "tweet_count"
    if (senti_percentage) and (not senti_class == None):
        #calculate sentiment tweets as percentage
        region_movie_all = database_helper.select_movie_region_tweets(start_date=start_date, end_date=end_date)
        
        if critical_period:
            movies_df = movie_helper.get_movies_df()
            small_movies_df = movies_df[["movieId", "critical_start", "critical_end"]]
            small_movies_df = small_movies_df.rename(columns={"movieId" : "movieid"})
            region_movie_all = region_movie_all.merge(small_movies_df, how="left", on="movieid")
            region_movie_all = region_movie_all[(region_movie_all["created_at"] >= region_movie_all["critical_start"]) 
                                                         & (region_movie_all["created_at"] <= region_movie_all["critical_end"])]
        
        region_movie_all_grouped = region_movie_all.groupby(by=["unit_id", "movieid"]).size().reset_index(name="tweet_count_all")  
        
        #use threshold of 20 tweets per region?
        region_movie_all_grouped = region_movie_all_grouped[region_movie_all_grouped["tweet_count_all"] >= 20]
        
        region_movie_grouped = region_movie_grouped.merge(region_movie_all_grouped, how="left", on=["unit_id", "movieid"])
        
        region_movie_grouped["senti_percentage"] = (region_movie_grouped["tweet_count"] / region_movie_grouped["tweet_count_all"]) * 100
        group_col = "senti_percentage"
    
    #remove ignored movies from list
    if len(ignore_list) > 0:
        region_movie_grouped = region_movie_grouped[~region_movie_grouped["movieid"].isin(ignore_list)]
      
    #get the movies with the highest count per region
    most_popular_per_region = region_movie_grouped.loc[region_movie_grouped.groupby(['unit_id'])[group_col].idxmax()]   
    
    #this is slow but really helps with generating the figures
    #attach movie ttitles to results
    movies_df = movie_helper.get_movies_df()
    movie_titles = movies_df[["movieId", "title"]]
 
    #attach region names
    gb_regions = database_helper.select_query("tweets_region_count")
    gb_regions = gb_regions[["unit_id", "region"]]
 
    most_popular_per_region = most_popular_per_region.merge(gb_regions, how="left", on="unit_id")  
    most_popular_per_region = most_popular_per_region.merge(movie_titles, how="left", left_on="movieid", right_on="movieId").drop(columns="movieId")
 
    return most_popular_per_region


def plot_favourites_map(favs_df, annotate_col, title):
    """
    Function to get  plot the regional favourites
    
    :param favs_df: dataframe of regional favourites
    :param annotate_col: column name to use for annotations
    :param title: string title for plot
    """  

    #load Ordnance Survey shapefiles    
    gb = gpd.read_file("../../ProjectData/Data/GB/european_region_region.shp")
    
    #merge favs df with shapefile
    favs_map = gb.merge(favs_df, how="left", left_on="UNIT_ID", right_on="unit_id")
    
    #plot map
    fig, ax = plt.subplots(1, 1, figsize=(11, 9))
    ax.axis('off')
    ax.set_title(title)
    fig.set_dpi(100)
    favs_map.plot(column="title", legend=True, ax=ax)
    
    scotland = favs_map[favs_map["unit_id"] == 41429]
    max_area = scotland.loc[scotland["AREA"].idxmax()].NUMBER
    
    #add annotations
    for index, row in favs_map.iterrows(): 
        #scotland has tonnes of polygons
        if row["UNIT_ID"] == 41429:
            if row["NUMBER"] == max_area:
                plt.annotate(s=row[annotate_col], xy=row.geometry.centroid.coords[0], horizontalalignment='center') 
        else:
            plt.annotate(s=row[annotate_col], xy=row.geometry.centroid.coords[0], horizontalalignment='center') 
    
    plt.show()
        

