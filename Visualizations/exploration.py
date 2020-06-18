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
movie = movies[1]
releaseDate = movie.ukReleaseDate
endWeekend = movie.box_office_df.iloc[movie.box_office_df['weeksOnRelease'].idxmax()].weekendEnd
fig, ax = plt.subplots()
ax.axvspan(*mdates.datestr2num([str(releaseDate), str(endWeekend)]), color='skyblue', alpha=0.5)
tweets =  database_helper.select_geo_tweets(movie.movieId)
tweets['date'] = tweets['created_at'].dt.date
date_freq = tweets.groupby('date').size().reset_index(name='count') 
date_freq.sort_values('date')
date_freq['date'] = pd.to_datetime(date_freq['date'], errors='coerce')
date_freq.set_index('date')['count'].plot()
#plt.plot(date_freq['date'], date_freq['count'])

#plt.xticks(date_freq['date'])
plt.xlabel("Date")
plt.ylabel("Tweet Count")
plt.title(movie.title + " Tweets over time")
plt.show()


