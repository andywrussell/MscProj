#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 09:15:02 2020

@author: andy
"""

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
import osmnx as ox
import geopandas as gpd
from geopandas.tools import sjoin
import seaborn as sns
import matplotlib.dates as mdates
import numpy as np
from colour import Color
import scipy.signal
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer



movies = movie_helper.get_movies()

#movies = movie_helper.get_top_earning()

def gen_top_20_hist():
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
    plt.title('Top 20 Movies')
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
    
# movie = movies[0]
# regional_pop = { 'Scotland Euro Region' :  5463300,  
#         'East Midlands Euro Region' : 4835928, 
#         'London Euro Region' : 8961989, 
#         'North West Euro Region' : 7341196, 
#         'West Midlands Euro Region' : 5934037,
#         'Yorkshire and the Humber Euro Region' : 5502967,
#         'South East Euro Region' : 9180135, 
#         'North East Euro Region' : 2669941,
#         'Wales Euro Region' : 3152879, 
#         'Eastern Euro Region' : 6236072,
#         'South West Euro Region' : 5624696} 
  
# title = "{0} tweets per region".format(movie.title)
# map_col = 'counts'
# gb = gpd.read_file("../../ProjectData/Data/GB/european_region_region.shp")
# tweets =  database_helper.select_geo_tweets(movie.movieId)
# gb_tweets = sjoin(tweets, gb, how='inner')
# gb = gb.to_crs("EPSG:4326")
# f, ax = plt.subplots(1, figsize=(9, 9))

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
# ax.set_xscale('log')

# plt.minorticks_off()
# pure_ticks = np.array([1e-3,1,10,60*10,2*3600,1*24*3600, 7*24*3600]) # where the tick marks will be placed, in units of seconds.
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

analyser = SentimentIntensityAnalyzer()
movie = movies[0]
tweets =  database_helper.select_geo_tweets(movie.movieId)
tweet_sentiment = []
for index, row in tweets.iterrows(): 
    sentiment = analyser.polarity_scores(row['msg'])
    tweet_sentiment.append(sentiment['compound'])
    
tweets['compound_sentiment'] = tweet_sentiment
tweets['date'] = tweets['created_at'].dt.date
date_sentiment = tweets.groupby(['date'], as_index = False).sum()
date_sentiment['count'] = tweets.groupby('date').size().reset_index(name='count')['count']
date_sentiment.sort_values('date')
date_sentiment['date'] = pd.to_datetime(date_sentiment['date'], errors='coerce')
indexes, _ = scipy.signal.find_peaks(date_sentiment['compound_sentiment'], height=7, distance=2.1)
date_sentiment["compound_norm"] = date_sentiment['compound_sentiment'] / date_sentiment['count']
#date_freq.set_index('date')['count'].plot(markevery=indexes.tolist())
plt.plot(date_sentiment['date'], date_sentiment['compound_norm'], marker='D',markerfacecolor='r', markevery=indexes.tolist())

print('Peaks are: %s' % (indexes))
#plt.xticks(date_freq['date'])
plt.xlabel("Date")
plt.ylabel("Tweet Sentiment")
plt.title(movie.title + " Tweet sentiment over time")
plt.show()

