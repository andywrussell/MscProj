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
    movies_df = movie_helper.get_movies_df()
    movies_df["tweet_count"] = movies_df.apply(lambda row: movie_helper.count_tweets(row['movieId'])['count'], axis = 1)
    
    movies_df = movies_df.sort_values(by='tweet_count', ascending=False).head(20)

    plt.barh(movies_df["title"], movies_df["tweet_count"], color='green')
    plt.ylabel('Movie Title')
    plt.xlabel('Tweet Count')
    plt.title('Top 20 Movies')
  #  plt.yticks(x_pos, titles)
    plt.show()
    
def gen_bottom_20_tweet_count():
    movies_df = movie_helper.get_movies_df()
    movies_df["tweet_count"] = movies_df.apply(lambda row: movie_helper.count_tweets(row['movieId'])['count'], axis = 1)
    
    movies_df = movies_df.sort_values(by='tweet_count').head(20)

    plt.barh(movies_df["title"], movies_df["tweet_count"], color='green')
    plt.ylabel('Movie Title')
    plt.xlabel('Tweet Count')
    plt.title('Bottom 20 Movies')
 #   plt.yticks(x_pos, titles)
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
    
def plot_return_classes():
    sns.set(style="whitegrid")
    grouped_movies = movies_df.groupby(["return_class"]).size().reset_index(name = "counts")
    order_lst = ['< %0 (Flop)', '%0-100%', '%100-%400', '%400-%1000', '> %1000 (BlockBuster)']
    ax = sns.barplot(x="return_class", y="counts", data=grouped_movies, order=order_lst)
    ax.set(xlabel='Percentage Return', ylabel='Movie Count')
    plt.title("Movie Return Classes")
    plt.xticks(rotation=40)
    plt.show()    
    
def plot_uk_classes():
    sns.set(style="whitegrid")
    grouped_movies = movies_df.groupby(["uk_percentage_class"]).size().reset_index(name = "counts")
    order_lst = ['0% - 2%', '2% - 4%', '4% - 6%', '6% - 12%', '> 12%']
    ax = sns.barplot(x="uk_percentage_class", y="counts", data=grouped_movies, order=order_lst)
    ax.set(xlabel='Percentage of UK Profits', ylabel='Movie Count')
    plt.title("UK Takings Classes")
    plt.xticks(rotation=40)
    plt.show()        
    
def plot_financial_box(column, title, xlabel):
    temp_col_name = column + "_norm"
    movies_df[temp_col_name] = movies_df[column].replace('[\£,]', '', regex=True).astype(float) / 1000000
    ax = sns.boxplot(x=temp_col_name, data=movies_df)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    plt.show()
    
def plot_float_box(column, title, xlabel):
    ax = sns.boxplot(x=column, data=movies_df)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    plt.show()
    
def plot_financial_box_dist(column, title, xlabel):
    temp_col_name = column + "_norm"
    movies_df[temp_col_name] = movies_df[column].replace('[\£,]', '', regex=True).astype(float) / 1000000
    figure, axes = plt.subplots(1, 2)
    ax1 = sns.boxplot(x=temp_col_name, data=movies_df)
    ax1.set_title(title)
    ax1.set_xlabel(xlabel)
    
    ax2 = sns.distplot(movies_df[temp_col_name])
    ax2.set_title(title)
    ax2.set_xlabel(xlabel)
    plt.show()
    
    
def plot_top10_uk(percentage=False):
    column = "uk_percentage"
    
    sorted_movies = movies_df.sort_values(by=column, ascending=False).head(n=10)

    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    
    ax.bar(sorted_movies["title"], sorted_movies["uk_percentage"])
    ax.set_ylabel("Uk percentage")
    ax.set_xlabel("Movie TItle")
    ax.set_title("Percentage Of Takings in UK")
    plt.xticks(rotation=40)
    plt.show()
    
def plot_top10_profit():
    column = "gross_profit_usd"
    movies_df['profit_norm'] = movies_df["gross_profit_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    sorted_movies = movies_df.sort_values(by="profit_norm", ascending=False).head(n=10)

    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    
    ax.bar(sorted_movies["title"], sorted_movies["profit_norm"])
    ax.set_ylabel("Gross Profit $mil")
    ax.set_xlabel("Movie TItle")
    ax.set_title("Worldwide Gross Profit")
    plt.xticks(rotation=40)
    plt.show()
    
    
def plot_top10_roi(percentage=False):
    column = "return_percentage"
    
    sorted_movies = movies_df.sort_values(by=column, ascending=False).head(n=10)

    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    
    ax.bar(sorted_movies["title"], sorted_movies[column])
    ax.set_ylabel("Return percentage")
    ax.set_xlabel("Movie TItle")
    ax.set_title("Return On Investment")
    plt.xticks(rotation=40)
    plt.show()    
    
def plot_financial_distribution(column, title, xlabel):
    temp_col_name = column + "_norm"
    data = movies_df[column].replace('[\£,]', '', regex=True).astype(float) / 1000000
    ax = sns.distplot(data)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    plt.show()
    
def plot_float_distribution(column, title, xlabel):
    data = movies_df[column]
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
    
def plot_tweets_vs_finance(column, title, xlabel, ylabel, movie_run=False, logx=False, logy=False):
    movies_df["temp_col"] = movies_df[column].replace('[\£,]', '', regex=True).astype(float) / 1000000
    
    if movie_run:
        #do a loop?
        movies = movie_helper.gen_movies(movies_df)
        
        tweet_counts = []
        for movie in movies:
            tweet_counts.append(movie.get_geotweet_count_by_dates())

        movies_df["tweet_count"] = tweet_counts            
    else:
        movies_df["tweet_count"] = movies_df["movieId"].apply(lambda x: movie_helper.count_tweets(int(x))['count'])
    
    ax = sns.regplot(x="temp_col", y="tweet_count", data=movies_df)

    if logx:
        ax.set_xscale('log')
        
    if logy:
        ax.set_yscale('log')

    ax.set(xlabel=xlabel, ylabel=ylabel)
    plt.title(title)
    plt.show()
    
    
def plot_tweets_vs_ratio(column, title, xlabel, ylabel, movie_run=False, logx=False, logy=False):
    if movie_run:
        #do a loop?
        movies = movie_helper.gen_movies(movies_df)
        
        tweet_counts = []
        for movie in movies:
            tweet_counts.append(movie.get_geotweet_count_by_dates())
            
        movies_df["tweet_count"] = tweet_counts            
    else:
        movies_df["tweet_count"] = movies_df["movieId"].apply(lambda x: movie_helper.count_tweets(int(x))['count'])
    
    ax = sns.regplot(x=column, y="tweet_count", data=movies_df)

    if logx:
        ax.set_xscale('log')
        
    if logy:
        ax.set_yscale('log')

    ax.set(xlabel=xlabel, ylabel=ylabel)
    plt.title(title)
    plt.show()
  
def plot_top_5_by_tweet_count(movie_run = True):
    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    
    if movie_run:
        #do a loop?
        movies = movie_helper.gen_movies(movies_df)
        
        tweet_counts = []
        for movie in movies:
            tweet_counts.append(movie.get_geotweet_count_by_dates())

        movies_df["tweet_count"] = tweet_counts            
    else:
        movies_df["tweet_count"] = movies_df["movieId"].apply(lambda x: movie_helper.count_tweets(int(x))['count'])
        
    sorted_df = movies_df.sort_values(by="tweet_count", ascending=False).head()
    ax.bar(sorted_df["title"], sorted_df["tweet_count"])
    ax.set_ylabel("Tweet Count")
    ax.set_title("Top 5 by tweet counts")
    plt.xticks(rotation=40)
    plt.show()
    
def plot_genre_counts():
    genres_df = movie_helper.get_movie_genre_counts()
    genres_df = genres_df.sort_values(by="count", ascending=False)
    
    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    
    ax.bar(genres_df["genre"], genres_df["count"])
    ax.set_ylabel("Movie Count")
    ax.set_xlabel("Genre")
    ax.set_title("Genre Movie Counts")
    plt.xticks(rotation=40)
    plt.show()
    
def plot_top_10_genres():
    genres_df = movie_helper.get_movie_genre_counts()
    genres_df = genres_df.sort_values(by="count", ascending=False).head(n=10)
    
    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    
    ax.bar(genres_df["genre"], genres_df["count"])
    ax.set_ylabel("Movie Count")
    ax.set_xlabel("Genre")
    ax.set_title("Genres")
    plt.xticks(rotation=40)
    plt.show()
    
def plot_genre_tweet_counts():
    genres_df = movie_helper.get_genre_tweet_counts()
    genres_df = genres_df.sort_values(by="count", ascending=False)

    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    
    ax.bar(genres_df["genre"], genres_df["count"])
    ax.set_ylabel("Tweet Count")
    ax.set_xlabel("Genre")
    ax.set_title("Genre Tweet Counts")
    plt.xticks(rotation=40)
    plt.show()
    
def plot_genre_sentiment():
    genre_sentiment_class_counts = movie_helper.get_genre_tweet_sentiments()
    g = sns.catplot(x="genre", y="counts", hue="senti_class", data=genre_sentiment_class_counts, height=6, kind="bar", palette="muted", legend_out=False)
    fig = g.fig
    g.set_ylabels("Tweet Counts")
    g.set_xlabels("Genre")
    g.set_xticklabels(rotation=40, ha="right")
    fig.subplots_adjust(top=0.9)
    fig.suptitle("Genre Tweet Sentiment", fontsize=16)
    plt.show()
    
def plot_genre_sentiment_stacked(normalize = True):
    grouped_tweets = movie_helper.get_genre_tweet_sentiments()
    
    plot_col = "counts"
    stack_col = "senti_class"
    if normalize:
        grouped_sum = grouped_tweets.groupby(['genre']).sum().reset_index()
        grouped_sum.rename(columns={'counts' : 'total'}, inplace=True)
        grouped_tweets = grouped_tweets.join(grouped_sum.set_index("genre"), on="genre", how="inner", lsuffix="_left", rsuffix="_right_")
        grouped_tweets["percentage"] = grouped_tweets["counts"] / grouped_tweets["total"] 
        plot_col = "percentage"
        stack_col = "senti_class_left"
    
    data = grouped_tweets.pivot(index="genre", columns=stack_col, values=plot_col)
    data.plot.bar(stacked=True) 
    
def plot_genre_map(genre, normalize = False):
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
    
    title = "{0} tweets per region".format(genre)
    map_col = 'counts'
    
    genre_tweets = tweet_helper.get_genre_region_tweets(genre)
    tweet_freq = genre_tweets.groupby('NAME').size().reset_index(name='counts')
    
    if normalize:
        tweet_freq['population'] = tweet_freq['NAME'].map(regional_pop)
        tweet_freq["norm_count"] = tweet_freq['counts'] / tweet_freq['population']
        tweet_freq["norm_count"] = (tweet_freq['counts'] / tweet_freq['population']) * 1000000
        map_col = 'norm_count'
    
    gb = gpd.read_file("../../ProjectData/Data/GB/european_region_region.shp")
    map_freq = gb.merge(tweet_freq, left_on='NAME', right_on='NAME')
    
    fig, ax = plt.subplots(1, 1)
    ax.axis('off')
    ax.set_title(title)
    fig.set_dpi(100)
    map_freq.plot(column=map_col, ax=ax, legend=True, cmap='OrRd')
    
def plot_genre_profits():
    profits_df = movie_helper.get_genre_revenues()
    
    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    
    ax.bar(profits_df["genre"], profits_df["profit_mil"])
    ax.set_ylabel("Gross Profit $mil")
    ax.set_xlabel("Genre")
    ax.set_title("Genres Profits")
    plt.xticks(rotation=40)
    plt.show()
    
def plot_genre_movie_counts():
    genre_sentiment_movie_counts = movie_helper.get_genre_movie_class_counts()
    g = sns.catplot(x="genre", y="counts", hue="profit_class", data=genre_sentiment_movie_counts, height=6, kind="bar", palette="muted", legend_out=False)
    fig = g.fig
    g.set_ylabels("Movie Counts")
    g.set_xlabels("Genre")
    g.set_xticklabels(rotation=40, ha="right")
    fig.subplots_adjust(top=0.9)
    fig.suptitle("Movie Profit Class", fontsize=16)
    plt.show()
    
                    
def correlatte_movie_stats():
    #https://towardsdatascience.com/better-heatmaps-and-correlation-matrix-plots-in-python-41445d0f2bec
    movies_df = movie_helper.get_movies_df()
    
    movies_df["tweet_count"] = movies_df.apply(lambda row: movie_helper.count_tweets(row.movieId)['count'], axis = 1)
    movies_df["budget_usd"] = movies_df["budget_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["uk_gross_usd"] = movies_df["domestic_gross_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["domestic_gross_usd"] = movies_df["domestic_gross_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["worldwide_gross_usd"] = movies_df["worldwide_gross_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["international_gross_usd"] = movies_df["international_gross_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["gross_profit_usd"] = movies_df["gross_profit_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    
    columns = ['budget_usd', 'uk_gross_usd', 'domestic_gross_usd', 'worldwide_gross_usd', 'international_gross_usd', 'gross_profit_usd', 'return_percentage', 'uk_percentage', 'tweet_count']

    # Basic correlogram
    sns.pairplot(movies_df[columns])
    plt.show()
    
    correlation_mat = movies_df[columns].corr()
    sns.heatmap(correlation_mat, annot = True)
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



