#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 09:15:02 2020

@author: andy
"""

import imdb
from tqdm import tqdm
import pandas as pd
import sys
import re
import matplotlib.pyplot as plt
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Entities')
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Utils')

from movie import Movie
import database_helper
import movie_helper
import tweet_helper
import osmnx as ox
import geopandas as gpd
from geopandas.tools import sjoin
import seaborn as sns
import matplotlib.dates as mdates
import numpy as np
from colour import Color
import scipy.signal
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nameparser import HumanName


movies_df = movie_helper.get_movies_df()
#top_20 = movie_helper.get_top_earning()
#bottom_20 = movie_helper.get_lowest_earning()

#movies = movie_helper.get_movies()

#movies = movie_helper.get_top_earning()

def get_revenue_bar_plot(movies, title = 'Top 20 Movies'):
    titles = []
    revenue = []
    for movie in movies:
        titles.append(movie.title)
        rev = float(re.sub(r'[^\d.]', '', movie.totalRevenue)) / 1000000
        revenue.append(rev)

    titles = titles[::-1]
    revenue = revenue[::-1]
    x_pos = [i for i, _ in enumerate(titles)]
    plt.barh(titles, revenue, color='green')
    plt.ylabel('Movie Title')
    plt.xlabel('Total Revenue (£mil)')
    plt.title(title)
    plt.yticks(x_pos, titles)
    plt.show()
        
def gen_top_20_tweet_count():
    titles = []
    tweets = []
    for movie in movies:
        titles.append(movie.title)
        count_df = movie_helper.count_tweets(movie.movieId)
        count = count_df.iloc[0]['count']
        tweets.append(count)
    
    titles = titles[::-1]
    tweets = tweets[::-1]
    x_pos = [i for i, _ in enumerate(titles)]
    plt.barh(titles, tweets, color='green')
    plt.ylabel('Movie Title')
    plt.xlabel('Tweet Count')
    plt.title('Top 20 Movies')
    plt.yticks(x_pos, titles)
    plt.show()
    
def map_test():
    place = "United Kingdom"
    graph = ox.graph_from_place(place)
    

def plot_budget_vs_revenue():
    movies_df["worldwide_gross_usd"] = movies_df['worldwide_gross_usd'].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["budget_usd"] = movies_df['budget_usd'].replace('[\£,]', '', regex=True).astype(float) / 1000000
    
    x_lower_lim = movies_df["budget_usd"].min()
    x_upper_lim = movies_df["budget_usd"].max()
    
    y_lower_lim = movies_df["worldwide_gross_usd"].min()
    y_upper_lim = movies_df["worldwide_gross_usd"].max()
    
    ax = sns.relplot(x="budget_usd", y="worldwide_gross_usd", data=movies_df)
    ax.set(ylim=(y_lower_lim, y_upper_lim))
    ax.set(xlim=(x_lower_lim, x_upper_lim))
    plt.show()
    
    
def plot_budget_vs_profit():
    movies_df["worldwide_gross_usd"] = movies_df['worldwide_gross_usd'].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["budget_usd"] = movies_df['budget_usd'].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["gross_usd"] = movies_df["worldwide_gross_usd"] - movies_df["budget_usd"]
    
    ax = sns.relplot(x="budget_usd", y="gross_usd", data=movies_df)
    plt.show()
    
def plot_profit_classes():
    sns.set(style="whitegrid")
    grouped_movies = movies_df.groupby(["profit_class"]).size().reset_index(name = "counts")
    order_lst = ['< $0 (Flop)', '$0 < $50m', '$50m < $150m', '$150m < $300m', ' > $300m (BlockBuster)' ]
    ax = sns.barplot(x="profit_class", y="counts", data=grouped_movies, order=order_lst)
    ax.set(xlabel='Gross Profit (USD)', ylabel='Movie Count')
    plt.title("Movie Profit Classes")
    plt.xticks(rotation=40)
    plt.show()
    
def plot_financial_box(column, title, xlabel):
    temp_col_name = column + "_norm"
    movies_df[temp_col_name] = movies_df[column].replace('[\£,]', '', regex=True).astype(float) / 1000000
    ax = sns.boxplot(x=temp_col_name, data=movies_df)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    plt.show()
    
def plot_financial_distribution(column, title, xlabel):
    temp_col_name = column + "_norm"
    data = movies_df[column].replace('[\£,]', '', regex=True).astype(float) / 1000000
    ax = sns.distplot(data)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    plt.show()
    
def plot_most_profitable_tweets():
    movies_df["profit_mil"] = movies_df["gross_profit_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    most_profit_row = movies_df[movies_df["profit_mil"] == movies_df["profit_mil"].max()]
    most_profit = movie_helper.get_movie_by_id(int(most_profit_row["movieId"]))
    most_profit.plot_tweets_over_time()
    
def plot_lest_profitable_tweets():
    movies_df["profit_mil"] = movies_df["gross_profit_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    least_profit_row = movies_df[movies_df["profit_mil"] == movies_df["profit_mil"].min()]
    #least_profit = movie_helper.get_movie_by_id(int(least_profit_row["movieId"]))
    least_profit = movie_helper.get_movie_by_id()
    least_profit.plot_tweets_over_time()
    
def plot_tweets_vs_finance(column, title, xlabel, ylabel):
    movies_df["temp_col"] = movies_df[column].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["tweet_count"] = movies_df["movieId"].apply(lambda x: movie_helper.count_tweets(int(x))['count'])
    
    ax = sns.relplot(x="temp_col", y="tweet_count", data=movies_df)

    ax.set(xlabel=xlabel, ylabel=ylabel)
    plt.title(title)
    plt.show()
    
  
def plot_top_5_by_tweet_count():
    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    movies_df["tweet_count"] = movies_df["movieId"].apply(lambda x: movie_helper.count_tweets(int(x))['count'])
    sorted_df = movies_df.sort_values(by="tweet_count", ascending=False).head()
    ax.bar(sorted_df["title"], sorted_df["tweet_count"])
    ax.set_ylabel("Tweet Count")
    ax.set_title("Top 5 by tweet counts")
    plt.xticks(rotation=40)
    plt.show()
    
    
#plot_budget_vs_revenue()
#plot_budget_vs_profit()
#plot_profit_classes()


# gb.plot(ax=ax)
# sns.kdeplot(gb_tweets['wgslng'], gb_tweets['wgslat'], 
#             shade=False, cmap='Purples',
#             ax=ax);

# ax.set_axis_off()
# plt.axis('equal')
# plt.grid()
# plt.show()
#
# tweet_freq = gb_tweets.groupby('NAME').size().reset_index(name='counts')
# if normalize:
#     tweet_freq['population'] = tweet_freq['NAME'].map(regional_pop)
#     tweet_freq["norm_count"] = tweet_freq['counts'] / tweet_freq['population']
#     tweet_freq["norm_count"] = (tweet_freq['counts'] / tweet_freq['population']) * 1000000
#     map_col = 'norm_count'
# map_freq = gb.merge(tweet_freq, left_on='NAME', right_on='NAME')
# fig, ax = plt.subplots(1, 1)
# ax.axis('off')
# ax.set_title(title)
# fig.set_dpi(100)
# map_freq.plot(column=map_col, ax=ax, legend=True, cmap='OrRd')       


#test = movies[90].plot_weekend_revenues()
#test = movies[0].box_office_df
#def get_revenue_for_top_20():
    
#uk = ps.pdio.read_files("../../ProjectData/Data/GB/european_region_region.shp")
# movie = movies[0]
# tweets = database_helper.select_geo_tweets(movie.movieId)
# zero =  mdates.date2num(tweets['created_at'].min())
# times = [t - zero for t in mdates.date2num(tweets['created_at'])]
# diffs = np.array([times[i]-times[i-1] for i in range(1,len(times))])
# xcoords = diffs[:-1]
# ycoords = diffs[1:]
# plt.plot(xcoords, ycoords, 'b.')
# plt.show()


#get tweets TESTING TIME MAP
# movie = movies[0]
# tweets = database_helper.select_geo_tweets(movie.movieId)
# tweets = tweets.sort_values(by=['created_at'])
# times = tweets['created_at']
# times_tot_mins = 24*60 - (60*np.array([t.hour for t in times]) + np.array([t.minute for t in times]))
# seps=np.array([(times[i]-times[i-1]).total_seconds() for i in range(1,len(times))])
# seps[seps==0]=1 # convert zero second separations to 1-second separations

# sep_array=np.zeros((len(seps)-1,2)) # 1st column: x-coords, 2nd column: y-coords
# sep_array[:,0]=seps[:-1]
# sep_array[:,1]=seps[1:]

# Ncolors=24*60 

# ## set up color list
# red=Color("red")
# blue=Color("blue")
# color_list = list(red.range_to(blue, Ncolors)) # range of colors evenly speced on the spectrum between red and blue. Each element is a colour object
# color_list = [c.hex for c in color_list] # give hex version

# fig=plt.figure()
# ax =fig.add_subplot(111)

# plt.rc('text',usetex=False)
# plt.rc('font',family='serif')
# 	
# colormap = plt.cm.get_cmap('rainbow')  # see color maps at http://matplotlib.org/users/colormaps.html

# order=np.argsort(times_tot_mins[1:-1]) # so that the red dots are on top
# #	order=np.arange(1,len(times_tot_mins)-2) # dots are unsorted

# sc= ax.scatter(sep_array[:,0][order],sep_array[:,1][order],c=times_tot_mins[1:-1][order],vmin=0,vmax=24*60,s=25,cmap=colormap,marker='o',edgecolors='none')
# # taken from http://stackoverflow.com/questions/6063876/matplotlib-colorbar-for-scatter
# 	
# color_bar=fig.colorbar(sc,ticks=[0,24*15,24*30,24*45,24*60],orientation='horizontal',shrink=0.5)
# color_bar.ax.set_xticklabels(['Midnight','18:00','Noon','6:00','Midnight'])
# color_bar.ax.invert_xaxis()
# color_bar.ax.tick_params(labelsize=16)
# 	
# ax.set_yscale('log') # logarithmic axes
# pure_ticks = np.array([1e-3,1,10,60*10,2*3600,1*24*3600, 7*24*3600])
# ax.set_xscale('log')

# plt.minorticks_off() # where the tick marks will be placed, in units of seconds.
# labels = ['1 msec','1 sec','10 sec','10 min','2 hr','1 day','1 week']  # tick labels
# 	
# max_val = np.max([np.max(sep_array[:,0]), np.max(sep_array[:,1])])
# 	
# ticks = np.hstack((pure_ticks, max_val))

# min_val = np.min([np.min(sep_array[:,0]), np.min(sep_array[:,1])])
# 	
# plt.xticks(ticks,labels,fontsize=16)
# plt.yticks(ticks,labels,fontsize=16)
# 	
# plt.xlabel('Time Before Tweet',fontsize=18)
# plt.ylabel('Time After Tweet',fontsize=18)

# plt.xlim((min_val, max_val))
# plt.ylim((min_val, max_val))
# 	
# ax.set_aspect('equal')
# plt.tight_layout()

# plt.show()



