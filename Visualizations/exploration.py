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
   # sns.set(style="whitegrid")
    fig = plt.figure(figsize=(10, 10))
   
    grouped_movies = movies_df.groupby(["profit_class"]).size().reset_index(name = "counts")
    order_lst = ['< $0 (Flop)', '$0 < $90m', '$90m < $235m', '$235m < $700m', '> $700m (BlockBuster)' ]
    ax = sns.barplot(x="profit_class", y="counts", data=grouped_movies, order=order_lst)
    ax.set(xlabel='Gross Profit ($mil)', ylabel='Movie Count')
    plt.title("Movie Profit Classes")
    plt.xticks(rotation=40)
    plt.show()
    
def plot_return_classes():
  #  sns.set(style="whitegrid")
    grouped_movies = movies_df.groupby(["return_class"]).size().reset_index(name = "counts")
    order_lst = ['< %0 (Flop)', '0% - 290%', '100% - 540%', '540% - 1000%', '> 1000% (BlockBuster)']
    ax = sns.barplot(x="return_class", y="counts", data=grouped_movies, order=order_lst)
    ax.set(xlabel='Percentage Return', ylabel='Movie Count')
    plt.title("Movie Return Classes")
    plt.xticks(rotation=40)
    plt.show()    
    
def plot_uk_classes():
 #   sns.set(style="whitegrid")
    grouped_movies = movies_df.groupby(["uk_percentage_class"]).size().reset_index(name = "counts")
    order_lst = ['0% - 1%', '1% - 4%', '4% - 6%', '6% - 12%', '> 12%']
    ax = sns.barplot(x="uk_percentage_class", y="counts", data=grouped_movies, order=order_lst)
    ax.set(xlabel='Percentage of UK Profits', ylabel='Movie Count')
    plt.title("UK Percentage Takings Classes")
    plt.xticks(rotation=40)
    plt.show()    

def plot_budget_classes():
  #  sns.set(style="whitegrid")
    grouped_movies = movies_df.groupby(["budget_class"]).size().reset_index(name = "counts")
    order_lst = ['< $10m (Small)', '$10m < $40m', '$40m < $100m', '$100m < $185m', '> 185m (Big)' ]
    ax = sns.barplot(x="budget_class", y="counts", data=grouped_movies, order=order_lst)
    ax.set(xlabel='Movie Budget ($mil)', ylabel='Movie Count')
    plt.title("Movie Budget Classes")
    plt.xticks(rotation=40)
    plt.show()

def plot_uk_taking_classes():
   # sns.set(style="whitegrid")
    grouped_movies = movies_df.groupby(["uk_gross_class"]).size().reset_index(name = "counts")
    order_lst = ['< $1m (Small)', '$1m < $8m', '$8m < $20m', '$20m < $50m', '> $50m (Big)' ]
    ax = sns.barplot(x="uk_gross_class", y="counts", data=grouped_movies, order=order_lst)
    ax.set(xlabel='Gross UK Takings ($mil)', ylabel='Movie Count')
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
  
    
def generate_heatmap_from_df(df, columns, title):
    f, ax = plt.subplots(figsize=(11, 9))
    
    correlation_mat = df[columns].corr()
  #  sns.heatmap(correlation_mat, annot = True)
    cmap = sns.diverging_palette(220, 10, as_cmap=True)
    
    sns.heatmap(correlation_mat, cmap=cmap, center=0,
            square=True, annot = True, linewidths=.5)
    
   # plt.title(title)
    plt.show() 
                    
def get_success_figure(class_col, order_list, dist_col, movies_df, title, money=True):
   #  fig, axs = plt.subplots(figsize=(20, 10), ncols=3)
    
   #  xlabel = title + " ($mil)" if money else title
    
   #  #get box
   #  box = sns.boxplot(x=movies_df[dist_col], data=movies_df, ax=axs[0])
   #  box.set_title(title + " Box Plot")
   #  box.set_xlabel(xlabel)
    
   #  #get dist
   #  dist = sns.distplot(movies_df[dist_col], ax=axs[1])
   #  dist.set_title(title + " Distribution")
   #  dist.set_xlabel(xlabel)
    
   #  #show class plot
   #  grouped_movies = movies_df.groupby([class_col]).size().reset_index(name = "counts")
   #  bar = sns.barplot(x=class_col, y="counts", data=grouped_movies, order=order_list, ax=axs[2])
   #  bar.set(xlabel=class_col, ylabel='Movie Count')
   #  bar.set_title(title + " Class Counts")
   #  bar.set_xticklabels(order_list, rotation=40)
   # # plt.xticks(rotation=40)
   #  plt.show()   
    f, (ax_box, ax_dist, ax_bar) = plt.subplots(3, sharex=False, gridspec_kw={"height_ratios": (.15, .35, .50)}, figsize=(10, 10))
    
    xlabel = title + " ($mil)" if money else title
    
    ax_box.get_shared_x_axes().join(ax_box, ax_dist)
    ax_box.set_xticklabels([])
    
    # Add a graph in each part
    sns.boxplot(movies_df[dist_col], ax=ax_box)
    sns.distplot(movies_df[dist_col], ax=ax_dist)
    

    
    grouped_movies = movies_df.groupby([class_col]).size().reset_index(name = "counts")
    sns.barplot(x=class_col, y="counts", data=grouped_movies, order=order_list, ax=ax_bar)
    ax_bar.set_xticklabels(order_list, rotation=40) 
    ax_bar.set(xlabel=class_col, ylabel='Movie Count')

    ax_box.set(xlabel='', title=title + " Summary")
    ax_dist.set(xlabel=xlabel)
    plt.show()
   
    
def get_dist_figure(col, df, title, money=True): 
    # https://python-graph-gallery.com/24-histogram-with-a-boxplot-on-top-seaborn/
    f, (ax_box, ax_hist) = plt.subplots(2, sharex=True, gridspec_kw={"height_ratios": (.15, .85)}, figsize=(10, 10))
    
    xlabel = title + " ($mil)" if money else title
    
    # Add a graph in each part
    sns.boxplot(df[col], ax=ax_box)
    sns.distplot(df[col], ax=ax_hist)

    ax_box.set(xlabel='', title=title)
    ax_hist.set(xlabel=xlabel)
    plt.show()

def correlatte_movie_stats():
    #https://towardsdatascience.com/better-heatmaps-and-correlation-matrix-plots-in-python-41445d0f2bec
    #movies_df = movie_helper.get_movies_df()
    movies_df = movie_helper.get_movies_df_with_opening_weekend()
    
    movies_df["tweet_count"] = movies_df.apply(lambda row: movie_helper.count_tweets(row.movieId)['count'], axis = 1)
    movies_df["budget_usd"] = movies_df["budget_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["uk_gross_usd"] = movies_df["uk_gross_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["domestic_gross_usd"] = movies_df["domestic_gross_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["worldwide_gross_usd"] = movies_df["worldwide_gross_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["international_gross_usd"] = movies_df["international_gross_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["gross_profit_usd"] = movies_df["gross_profit_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["opening_weekend_takings"] = movies_df["opening_weekend_takings"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    
    columns = ['budget_usd', 
                'uk_gross_usd', 
                'domestic_gross_usd', 
                'worldwide_gross_usd', 
                'international_gross_usd', 
                'gross_profit_usd', 
                'return_percentage', 
                'uk_percentage', 
                'tweet_count',
                'total_release_weeks',
                'first_run_weeks',
                'best_rank',
                'weekends_at_best_rank',
                'weekends_in_top_3',
                'weekends_in_top_5',
                'weekends_in_top_10',
                'weekends_in_top_15',
                'opening_weekend_takings',
                'run_up_tweets',
                'opening_tweets']

    # Basic correlogram
   # sns.pairplot(movies_df[columns])
   # plt.show()
    
    generate_heatmap_from_df(df, columns)
    

def plot_df_as_table(df):
    #https://pythonmatplotlibtips.blogspot.com/2018/11/matplotlib-only-table.html
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    # Draw table
    the_table = plt.table(cellText=df.values,
                          rowLabels=df.index,
                          colLabels=df.columns,
                          loc='center')
    the_table.auto_set_font_size(False)
    the_table.auto_set_column_width(col=list(range(len(df.columns))))
   # the_table.set_fontsize(24)
   # the_table.scale(4, 4)
    
    # Removing ticks and spines enables you to get the figure only with table
    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    plt.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)
    for pos in ['right','top','bottom','left']:
        plt.gca().spines[pos].set_visible(False)
        
    plt.show()
    
def plot_boxplot_for_df(df):
    #https://towardsdatascience.com/dynamic-subplot-layout-in-seaborn-e777500c7386
    
    num_plots = len(df.columns)
    total_cols = 5 if num_plots >= 5 else 4
    total_rows = num_plots//total_cols
    
    print("{2} plots, {0} cols, {1} rows".format(total_cols, total_rows, num_plots))
    
    fig, axs = plt.subplots(nrows=total_rows, ncols=total_cols, figsize=(7*total_cols, 7*total_rows), constrained_layout=True)
    ax_count = 0
    
    for i, var in enumerate(df.columns):
        row = i//total_cols
        pos = i % total_cols
        
        if total_rows > 1:        
            sns.boxplot(x=df[var], orient='v', ax=axs[row][pos])
            axs[row][pos].xaxis.label.set_size(100)
        else:
            sns.boxplot(x=df[var], orient='v', ax=axs[pos])
            axs[pos].xaxis.label.set_size(100)
    

    plt.show()
    
def plot_dist_for_df(df):
    #https://towardsdatascience.com/dynamic-subplot-layout-in-seaborn-e777500c7386
    
    num_plots = len(df.columns)
    total_cols = 5 if num_plots >= 5 else 4
    total_rows = num_plots//total_cols
    
    print(total_cols)
    print(total_rows)
    
    fig, axs = plt.subplots(nrows=total_rows, ncols=total_cols, figsize=(7*total_cols, 7*total_rows), constrained_layout=True)
    ax_count = 0
    
    for i, var in enumerate(df.columns):
        row = i//total_cols
        pos = i % total_cols
        
        if total_rows > 1:        
            sns.distplot(df[var], ax=axs[row][pos])
            axs[row][pos].xaxis.label.set_size(12)
        else:
            sns.distplot(df[var], ax=axs[pos])
            axs[pos].xaxis.label.set_size(12)           

    plt.show()
    
def plot_movie_tweets_kde(movieId = 0, start_date=None, end_date=None, senti_class = None):
    #http://darribas.org/gds_scipy16/ipynb_md/06_points.html
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
  #  plt.axis('equal')
    plt.title(title)
    plt.show()
    plt.clf()
    plt.cla()
    plt.close()
    
def plot_movie_tweets_map(movieId = 0, normalize=False, start_date=None, end_date=None):
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
        
        title = "Regional Movie Tweets (per million tweets)"
        if movieId > 0:
            title = movie_title + " Tweets (per million tweets)"
            
    if (start_date != None) and (end_date != None):
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

def plot_region_tweets_bar(movieId = 0, normalize=False, start_date=None, end_date=None):
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
     

    if (start_date != None) and (end_date != None):
        title = "{0} ({1} - {2})".format(title, start_date.date(), end_date.date())

    ax = sns.barplot(x="region", y=plot_col, data=tweet_freq)
    ax.set(xlabel='Region', ylabel=ylabel)
    plt.title(title)
    plt.xticks(rotation=90)
    plt.show()
        
    return tweet_freq

def get_most_popular_movie_per_region(start_date=None, end_date=None, senti_class=None, ignore_list = [28,121]):
    region_movie_tweets = database_helper.select_movie_region_tweets(start_date=start_date, end_date=end_date, senti_class=senti_class)
    region_movie_grouped = region_movie_tweets.groupby(by=["unit_id", "movieid"]).size().reset_index(name="tweet_count")
        
    if len(ignore_list) > 0:
        region_movie_grouped = region_movie_grouped[~region_movie_grouped["movieid"].isin(ignore_list)]
        
    most_popular_per_region = region_movie_grouped.loc[region_movie_grouped.groupby(['unit_id'])['tweet_count'].idxmax()]   
    
    return most_popular_per_region

def get_most_popular_per_region_by_success_class(class_col, class_vals, start_date=None, end_date=None, senti_class=None, ignore_list = [28,121], find_min=False):
    region_movie_tweets = database_helper.select_movie_region_tweets(start_date=start_date, end_date=end_date, senti_class=senti_class)
    region_movie_grouped = region_movie_tweets.groupby(by=["unit_id", "movieid"]).size().reset_index(name="tweet_count")
    
    #get list of movies which match the passed in class vals
    movies_df = movie_helper.get_movies_df()
    
    filtered_df = movies_df[movies_df[class_col].isin(class_vals)]
    
    region_movie_grouped_filter = region_movie_grouped[region_movie_grouped["movieid"].isin(filtered_df["movieId"])]
    
    if len(ignore_list) > 0:
        region_movie_grouped_filter = region_movie_grouped_filter[~region_movie_grouped_filter["movieid"].isin(ignore_list)]
        
    most_popular_per_region = region_movie_grouped_filter.loc[region_movie_grouped_filter.groupby(['unit_id'])['tweet_count'].idxmax()]   
    if find_min:
        most_popular_per_region = region_movie_grouped_filter.loc[region_movie_grouped_filter.groupby(['unit_id'])['tweet_count'].idxmin()]  
    
    return most_popular_per_region
    #return most_popular_per_region
    


