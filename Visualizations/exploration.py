#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Set of functions used to generate the figures and results for experiments

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

        
def gen_top_20_tweet_count():
    """
    Function to plot the top 20 movies by tweet count    
    """
    
    #get movies from db and count tweets
    movies_df = movie_helper.get_movies_df()
    movies_df["tweet_count"] = movies_df.apply(lambda row: movie_helper.count_tweets(row['movieId'])['count'], axis = 1)
    
    #sort by tweet count and take top 20
    movies_df = movies_df.sort_values(by='tweet_count', ascending=False).head(20)

    #do bar plot
    plt.barh(movies_df["title"], movies_df["tweet_count"], color='green')
    plt.ylabel('Movie Title')
    plt.xlabel('Tweet Count')
    plt.title('Top 20 Movies')
    plt.show()
    
def gen_bottom_20_tweet_count():
    """
    Function to plot the bottom 20 movies by tweet count 
    """
    
    #get movies from db and count tweets
    movies_df = movie_helper.get_movies_df()
    movies_df["tweet_count"] = movies_df.apply(lambda row: movie_helper.count_tweets(row['movieId'])['count'], axis = 1)
    
    #sort values and take bottom 20
    movies_df = movies_df.sort_values(by='tweet_count').head(20)

    #do bar plot
    plt.barh(movies_df["title"], movies_df["tweet_count"], color='green')
    plt.ylabel('Movie Title')
    plt.xlabel('Tweet Count')
    plt.title('Bottom 20 Movies')
    plt.show()
    

def plot_budget_vs_revenue():
    """
    Function to plot scatter of budget vs revenue
    """
    
    #normalize so money is measured in millions of usd
    movies_df["worldwide_gross_usd"] = movies_df['worldwide_gross_usd'].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["budget_usd"] = movies_df['budget_usd'].replace('[\£,]', '', regex=True).astype(float) / 1000000
    
    x_lower_lim = movies_df["budget_usd"].min()
    x_upper_lim = movies_df["budget_usd"].max()
    
    y_lower_lim = movies_df["worldwide_gross_usd"].min()
    y_upper_lim = movies_df["worldwide_gross_usd"].max()
    
    #plot scatter plot with regression line
    ax = sns.relplot(x="budget_usd", y="worldwide_gross_usd", data=movies_df)
    ax.set(ylim=(y_lower_lim, y_upper_lim))
    ax.set(xlim=(x_lower_lim, x_upper_lim))
    plt.show()
    
    
def plot_budget_vs_profit():
    """
    Function to plot scatter of budget vs profit
    """
    
    #normalize so money is measured in millions of usd
    movies_df["worldwide_gross_usd"] = movies_df['worldwide_gross_usd'].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["budget_usd"] = movies_df['budget_usd'].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["gross_usd"] = movies_df["worldwide_gross_usd"] - movies_df["budget_usd"]
    
    #plot scatter plot with regression line
    ax = sns.relplot(x="budget_usd", y="gross_usd", data=movies_df)
    plt.show()
    
def plot_profit_classes():
    """
    Function to create bar plot of movie counts by profit class
    """
    fig = plt.figure(figsize=(10, 10))
   
    #group movies by profit class
    grouped_movies = movies_df.groupby(["profit_class"]).size().reset_index(name = "counts")
    
    #plot classes in correct order
    order_lst = ['< $0 (Flop)', '$0 < $90m', '$90m < $235m', '$235m < $700m', '> $700m (BlockBuster)' ]
    
    #create barplot
    ax = sns.barplot(x="profit_class", y="counts", data=grouped_movies, order=order_lst)
    ax.set(xlabel='Gross Profit ($mil)', ylabel='Movie Count')
    plt.title("Movie Profit Classes")
    plt.xticks(rotation=40)
    plt.show()
    
def plot_return_classes():
    """
    Function to create bar plot of movie counts by return class
    """
    
    #group movies by return class
    grouped_movies = movies_df.groupby(["return_class"]).size().reset_index(name = "counts")
    
    #plot classes in correct order
    order_lst = ['< %0 (Flop)', '0% - 290%', '100% - 540%', '540% - 1000%', '> 1000% (BlockBuster)']
    
    #create barplot
    ax = sns.barplot(x="return_class", y="counts", data=grouped_movies, order=order_lst)
    ax.set(xlabel='Percentage Return', ylabel='Movie Count')
    plt.title("Movie Return Classes")
    plt.xticks(rotation=40)
    plt.show()    
    
def plot_uk_classes():
    """
    Function to create bar plot of movie counts by uk percentage class
    """
    
    #group movies by uk return class
    grouped_movies = movies_df.groupby(["uk_percentage_class"]).size().reset_index(name = "counts")
    
    #plot classes in correct order
    order_lst = ['0% - 1%', '1% - 4%', '4% - 6%', '6% - 12%', '> 12%']
    
    #create barplot
    ax = sns.barplot(x="uk_percentage_class", y="counts", data=grouped_movies, order=order_lst)
    ax.set(xlabel='Percentage of UK Profits', ylabel='Movie Count')
    plt.title("UK Percentage Takings Classes")
    plt.xticks(rotation=40)
    plt.show()    

def plot_budget_classes():
    """
    Function to create bar plot of movie counts by budget class
    """
    
    #group movies by budget class
    grouped_movies = movies_df.groupby(["budget_class"]).size().reset_index(name = "counts")
    
    #plot classes in correct order
    order_lst = ['< $10m (Small)', '$10m < $40m', '$40m < $100m', '$100m < $185m', '> 185m (Big)' ]
    
    #create barplot
    ax = sns.barplot(x="budget_class", y="counts", data=grouped_movies, order=order_lst)
    ax.set(xlabel='Movie Budget ($mil)', ylabel='Movie Count')
    plt.title("Movie Budget Classes")
    plt.xticks(rotation=40)
    plt.show()

def plot_uk_taking_classes():
    """
    Function to create bar plot of movie counts by uk gross class
    """
    
    #group movies by uk gross class
    grouped_movies = movies_df.groupby(["uk_gross_class"]).size().reset_index(name = "counts")
    
    #plot classes in correct order
    order_lst = ['< $1m (Small)', '$1m < $8m', '$8m < $20m', '$20m < $50m', '> $50m (Big)' ]
    
    #create barplot
    ax = sns.barplot(x="uk_gross_class", y="counts", data=grouped_movies, order=order_lst)
    ax.set(xlabel='Gross UK Takings ($mil)', ylabel='Movie Count')
    plt.title("UK Takings Classes")
    plt.xticks(rotation=40)
    plt.show()    
      
    
def plot_financial_box(column, title, xlabel):
    """
    Function to create box plot of money column from movies df
    
    :param column: string name of column to plot
    :param title: string title for plot
    :param xlabel: string x axis label for plot
    """
    
    #create normalized money column by millions of usd
    temp_col_name = column + "_norm"
    movies_df[temp_col_name] = movies_df[column].replace('[\£,]', '', regex=True).astype(float) / 1000000
    
    #create box plot
    ax = sns.boxplot(x=temp_col_name, data=movies_df)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    plt.show()
    
def plot_float_box(column, title, xlabel):
    """
    Function to create box plot of float column from movies df
    
    :param column: string name of column to plot
    :param title: string title for plot
    :param xlabel: string x axis label for plot
    """
    
    #create boxplot
    ax = sns.boxplot(x=column, data=movies_df)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    plt.show()
    
def plot_financial_box_dist(column, title, xlabel):
    """
    Function to create combined distribution and box plot on same figure
    
    :param column: string name of column to plot
    :param title: string title for plot
    :param xlabel: string x axis label for plot
    """
    
    #first normalize money into millions of usd
    temp_col_name = column + "_norm"
    movies_df[temp_col_name] = movies_df[column].replace('[\£,]', '', regex=True).astype(float) / 1000000
    
    #create plot with two axes
    figure, axes = plt.subplots(1, 2)
    
    #plot boxplot on first ax
    ax1 = sns.boxplot(x=temp_col_name, data=movies_df)
    ax1.set_title(title)
    ax1.set_xlabel(xlabel)
    
    #plot distplot on second ax
    ax2 = sns.distplot(movies_df[temp_col_name])
    ax2.set_title(title)
    ax2.set_xlabel(xlabel)
    plt.show()
    
    
def plot_top10_uk(percentage=False):
    """
    Function to plot the top 10 movies based on uk takings
    
    :param percentage: bool indicating wether or not to use percentage
    """
    
    
    column = "uk_percentage"
    
    sorted_movies = movies_df.sort_values(by=column, ascending=False).head(n=10)

    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    
    ax.bar(sorted_movies["title"], sorted_movies["uk_percentage"])
    ax.set_ylabel("Uk percentage")
    ax.set_xlabel("Movie TItle")
    ax.set_title("Percentage Of Takings in UK")
    plt.xticks(rotation=90)
    plt.show()
    
def plot_top10_profit():
    """
    Function to plot the top 10 movies based on profit
    """
    
    column = "gross_profit_usd"
    movies_df['profit_norm'] = movies_df["gross_profit_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    sorted_movies = movies_df.sort_values(by="profit_norm", ascending=False).head(n=10)

    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    
    ax.bar(sorted_movies["title"], sorted_movies["profit_norm"])
    ax.set_ylabel("Gross Profit $mil")
    ax.set_xlabel("Movie TItle")
    ax.set_title("Worldwide Gross Profit")
    plt.xticks(rotation=90)
    plt.show()
    
    
def plot_top10_roi(percentage=False):
    """
    Function to plot the top 10 movies return
    """
    
    column = "return_percentage"
    
    data = movies_df
    data[column] = data[column].replace('[\£,]', '', regex=True).astype(float) / 1000000
    
    sorted_movies = data.sort_values(by=column, ascending=False).head(n=10)

    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    
    ax.bar(sorted_movies["title"], sorted_movies[column])
    ax.set_ylabel("Return Percentage")
    ax.set_xlabel("Movie TItle")
    ax.set_title("Top 10 Return Percentage")
    plt.xticks(rotation=90)
    plt.show()    
    
def plot_financial_distribution(column, title, xlabel):
    """
    Function to plot distribution of the financial column from movies dataframe
    
    :param column: string name of column to plot
    :param title: string title for plot
    :param xlabel: string x axis label for plot
    """
    
    #normalize money into millions of usd
    temp_col_name = column + "_norm"
    data = movies_df[column].replace('[\£,]', '', regex=True).astype(float) / 1000000
    
    #plot distribution
    ax = sns.distplot(data)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    plt.show()
    
def plot_float_distribution(column, title, xlabel):
    """
    Function to plot distribution of the float column from movies dataframe
    
    :param column: string name of column to plot
    :param title: string title for plot
    :param xlabel: string x axis label for plot
    """
    
    data = movies_df[column]
    ax = sns.distplot(data)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    plt.show()
    
def plot_most_profitable_tweets():
    """
    Function to plot the tweets over time of the most profitable movie
    """
    
    #convert profit to millions of usd
    movies_df["profit_mil"] = movies_df["gross_profit_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    
    #get the movie with the most profit
    most_profit_row = movies_df[movies_df["profit_mil"] == movies_df["profit_mil"].max()]
    
    #plot tweets over time
    most_profit = movie_helper.get_movie_by_id(int(most_profit_row["movieId"]))
    most_profit.plot_tweets_over_time()
    
def plot_lest_profitable_tweets():
    """
    Function to plot the tweets over time of the least profitable movie
    """
    
    #convert profit to millions of usd
    movies_df["profit_mil"] = movies_df["gross_profit_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    
    #get the movie with the least profit
    least_profit_row = movies_df[movies_df["profit_mil"] == movies_df["profit_mil"].min()]
    
    #plot tweets over time
    least_profit = movie_helper.get_movie_by_id()
    least_profit.plot_tweets_over_time()
    
def plot_tweets_vs_finance(column, title, xlabel, ylabel, movie_run=False, logx=False, logy=False):
    """
    Function to plot the tweet counts vs finance column for movies df
    
    :param column: string column name of variable to plot
    :param title: string title for plot
    :param xlabel: string x label for plot
    :param ylabel: string y label for plot
    :param movie_run: bool indicating if tweets should only be counted over the cinema rub
    :param logx: bool indicating wether to use log scale on x axis
    :param logy: bool indicating wether to use log scale on y axis
    """
    
    #normalize column into millions of usd
    movies_df["temp_col"] = movies_df[column].replace('[\£,]', '', regex=True).astype(float) / 1000000
    
    #check if we need to only look at the movie run
    if movie_run:
        #do a loop?
        movies = movie_helper.gen_movies(movies_df)
        
        tweet_counts = []
        for movie in movies:
            tweet_counts.append(movie.get_geotweet_count_by_dates())

        movies_df["tweet_count"] = tweet_counts            
    else:
        #count all tweets
        movies_df["tweet_count"] = movies_df["movieId"].apply(lambda x: movie_helper.count_tweets(int(x))['count'])
    
    #create scatter plot with regression line
    ax = sns.regplot(x="temp_col", y="tweet_count", data=movies_df)

    #check axis log sclaes
    if logx:
        ax.set_xscale('log')
        
    if logy:
        ax.set_yscale('log')

    ax.set(xlabel=xlabel, ylabel=ylabel)
    plt.title(title)
    plt.show()
    
    
def plot_tweets_vs_ratio(column, title, xlabel, ylabel, movie_run=False, logx=False, logy=False):
    """
    Function to plot the tweet counts vs percnetage column for movies df
    
    :param column: string column name of variable to plot
    :param title: string title for plot
    :param xlabel: string x label for plot
    :param ylabel: string y label for plot
    :param movie_run: bool indicating if tweets should only be counted over the cinema rub
    :param logx: bool indicating wether to use log scale on x axis
    :param logy: bool indicating wether to use log scale on y axis
    """
    
    #check if we need to only look at the movie run
    if movie_run:
        #do a loop?
        movies = movie_helper.gen_movies(movies_df)
        
        tweet_counts = []
        for movie in movies:
            tweet_counts.append(movie.get_geotweet_count_by_dates())
            
        movies_df["tweet_count"] = tweet_counts            
    else:
        #count all tweets
        movies_df["tweet_count"] = movies_df["movieId"].apply(lambda x: movie_helper.count_tweets(int(x))['count'])
    
    #create scatter plot with regression line
    ax = sns.regplot(x=column, y="tweet_count", data=movies_df)

    #check axis log sclaes
    if logx:
        ax.set_xscale('log')
        
    if logy:
        ax.set_yscale('log')

    ax.set(xlabel=xlabel, ylabel=ylabel)
    plt.title(title)
    plt.show()
  
def plot_top_by_tweet_count(max_films = 10, crtiical_period = True):
    """
    Function to plot films with the top tweet counts
    
    :param max_films: integer for the maximum films to plot
    :param critical_period: bool indicating whether or not to only look at tweets in the critical period
    """
    
    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    
    #count tweets over defined time scale for each movie
    column = "tweet_count"
    if crtiical_period:
        movies_df["critical_period_tweet_count"] = movies_df.apply(lambda row: movie_helper.count_tweets(row["movieId"], row["critical_start"], row["critical_end"])['count'], axis = 1)           
        column = "critical_period_tweet_count"
    else:
        movies_df["tweet_count"] = movies_df["movieId"].apply(lambda x: movie_helper.count_tweets(int(x))['count'])
        
    #sort in descending order by tweet count and take the max films
    sorted_df = movies_df.sort_values(by=column, ascending=False).head(max_films)
    
    #create bar plot
    ax.bar(sorted_df["title"], sorted_df[column])
    ax.set_ylabel("Tweet Count")
    ax.set_title("Top {0} by tweet counts".format(max_films))
    plt.xticks(rotation=90)
    plt.show()
    
    
def plot_genre_counts():
    """
    Function to plot the number of films in each genre
    """

    #get counts of movies per genre and sort     
    genres_df = movie_helper.get_movie_genre_counts()
    genres_df = genres_df.sort_values(by="count", ascending=False)
    
    #create bar plot
    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    
    ax.bar(genres_df["genre"], genres_df["count"])
    ax.set_ylabel("Movie Count")
    ax.set_xlabel("Genre")
    ax.set_title("Genre Movie Counts")
    plt.xticks(rotation=40)
    plt.show()
    
def plot_top_10_genres():
    """
    Function to plot the top 10 genres with the most films
    """
    
    #get counts of movies per genre and sort and take the top 10
    genres_df = movie_helper.get_movie_genre_counts()
    genres_df = genres_df.sort_values(by="count", ascending=False).head(n=10)
    
    #create bar plot
    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    
    ax.bar(genres_df["genre"], genres_df["count"])
    ax.set_ylabel("Movie Count")
    ax.set_xlabel("Genre")
    ax.set_title("Genres")
    plt.xticks(rotation=40)
    plt.show()
    
def plot_genre_tweet_counts():
    """
    Function to plot the number of tweets per genre
    """
    
    #get genre counts and sort
    genres_df = movie_helper.get_genre_tweet_counts()
    genres_df = genres_df.sort_values(by="count", ascending=False)

    #create bar plot
    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    
    ax.bar(genres_df["genre"], genres_df["count"])
    ax.set_ylabel("Tweet Count")
    ax.set_xlabel("Genre")
    ax.set_title("Genre Tweet Counts")
    plt.xticks(rotation=40)
    plt.show()
    
def plot_genre_sentiment():
    """
    Function to plot the number of tweets per genre grouped by tweet sentiment
    """
    
    #get counts of genre tweets by sentiment class 
    genre_sentiment_class_counts = movie_helper.get_genre_tweet_sentiments()
    
    #creare grouped bar plot
    g = sns.catplot(x="genre", y="counts", hue="senti_class", data=genre_sentiment_class_counts, height=6, kind="bar", palette="muted", legend_out=False)
    fig = g.fig
    g.set_ylabels("Tweet Counts")
    g.set_xlabels("Genre")
    g.set_xticklabels(rotation=40, ha="right")
    fig.subplots_adjust(top=0.9)
    fig.suptitle("Genre Tweet Sentiment", fontsize=16)
    plt.show()
    
def plot_genre_sentiment_stacked(normalize = True):
    """
    Function to plot a stacked bar of the number of tweets per genre grouped by sentiment
    
    :param normalize: bool indicating wether or not snetient count should be normalized to show rate
    """
    
    #get counts of genre tweets grouped by sentiment
    grouped_tweets = movie_helper.get_genre_tweet_sentiments()
    
    #check if we need to normalize
    plot_col = "counts"
    stack_col = "senti_class"
    if normalize:
        grouped_sum = grouped_tweets.groupby(['genre']).sum().reset_index()
        grouped_sum.rename(columns={'counts' : 'total'}, inplace=True)
        grouped_tweets = grouped_tweets.join(grouped_sum.set_index("genre"), on="genre", how="inner", lsuffix="_left", rsuffix="_right_")
        grouped_tweets["percentage"] = grouped_tweets["counts"] / grouped_tweets["total"] 
        plot_col = "percentage"
        stack_col = "senti_class_left"
    
    #create bar plot
    data = grouped_tweets.pivot(index="genre", columns=stack_col, values=plot_col)
    data.plot.bar(stacked=True) 
    
##DEPRICATED -- NORMALIZING BY POPULATION STATS WAS NOT CONTINUED
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
    """ 
    Function to plot the total profit of movies in each genre
    """
    
    #get the total total profit for each genre
    profits_df = movie_helper.get_genre_revenues()
    
    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    
    #create bar plot
    ax.bar(profits_df["genre"], profits_df["profit_mil"])
    ax.set_ylabel("Gross Profit $mil")
    ax.set_xlabel("Genre")
    ax.set_title("Genres Profits")
    plt.xticks(rotation=40)
    plt.show()
      
def get_top_percentage_tweets(movies_df, percentage_col, title, ylabel, num_movies=10, tweet_threshold=100):
    """
    Function to plot the tweet counts of movies in the top 10 in terms of either return_percentage or uk_percentage
    
    
    :param movies_df: dataframe of movies
    :param percentage_col: string name of success column to use
    :param title: string title for plot
    :param ylabel: stirng y axis label for plot
    :param num_movies: number of movies from the top to plot
    :param tweet_threshold: minimum number of tweets to be considered for plotting
    """
    
    #filter by tweet count threshold
    filtered_movies = movies_df[movies_df["tweet_count"] >= tweet_threshold]
    
    #sorted movies by success col and take appropriate amount
    sorted_movies = filtered_movies.sort_values(by=percentage_col, ascending=False).head(n=10)

    #create bar plot
    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    
    ax.bar(sorted_movies["title"], sorted_movies[percentage_col])
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Movie TItle")
    ax.set_title(title)
    plt.xticks(rotation=90)
    plt.show() 
    
    
def generate_heatmap_from_df(df, columns, title):
    """
    Function to create correlation heatmap for dataframe
    
    
    :param df: dataframe of for plotting
    :param columns: list of column names to correlate
    :param title: string title for plot
    """
    
    #generate heatmap
    f, ax = plt.subplots(figsize=(11, 9))
    
    correlation_mat = df[columns].corr()
    cmap = sns.diverging_palette(220, 10, as_cmap=True)
    
    sns.heatmap(correlation_mat, cmap=cmap, center=0,
            square=True, annot = True, linewidths=.5)
    
   # plt.title(title)
    plt.rcParams.update({'font.size': 12})
    plt.show() 
                    
def get_success_figure(class_col, order_list, dist_col, movies_df, title, money=True):
    """
    Function to create summary figure for success class variable
    
    :param class_col: column name of success class to plot
    :param order_list: list of class values to determine the order for bar plot
    :param dist_col: coumn name of success col for distribution and boxplot
    :param movies_df: dataframe of movies
    :param title: string title for plot
    :param money: bool value indicsting if the dist_col is a monetary value
    """
    
    #create figure with three subplots
    f, (ax_box, ax_dist, ax_bar) = plt.subplots(3, sharex=False, gridspec_kw={"height_ratios": (.15, .35, .50)}, figsize=(10, 10))
    
    #set xlabel
    xlabel = title + " ($mil)" if money else title
    
    #boxplot and displot will share x axis
    ax_box.get_shared_x_axes().join(ax_box, ax_dist)
    ax_box.set_xticklabels([])
    
    #Create box and distplot 
    sns.boxplot(movies_df[dist_col], ax=ax_box)
    sns.distplot(movies_df[dist_col], ax=ax_dist)
     
    #get count of movies by success class
    grouped_movies = movies_df.groupby([class_col]).size().reset_index(name = "counts")
    
    #create bar plot of counts by class value
    sns.barplot(x=class_col, y="counts", data=grouped_movies, order=order_list, ax=ax_bar)
    ax_bar.set_xticklabels(order_list, rotation=40) 
    ax_bar.set(xlabel=class_col, ylabel='Movie Count')

    ax_box.set(xlabel='', title=title + " Summary")
    ax_dist.set(xlabel=xlabel)
    plt.rcParams.update({'font.size': 20})
    plt.show()
   
    
def get_dist_figure(col, df, title, money=True): 
    """
    Function to create distribution and boxplot on same figure
    
    :param col: column name of dist col to plot
    :param df: dataframe of movies
    :param title: string title for plot
    :param money: bool value indicsting if the dist_col is a monetary value
    """
    
    # https://python-graph-gallery.com/24-histogram-with-a-boxplot-on-top-seaborn/
    f, (ax_box, ax_hist) = plt.subplots(2, sharex=True, gridspec_kw={"height_ratios": (.15, .85)}, figsize=(10, 10))
    
    xlabel = title + " ($mil)" if money else title
    
    # Add a graph in each part
    sns.boxplot(df[col], ax=ax_box)
    sns.distplot(df[col], ax=ax_hist)

    ax_box.set(xlabel='', title=title)
    ax_hist.set(xlabel=xlabel)
    plt.rcParams.update({'font.size': 20})
    plt.show()

def correlatte_movie_stats():
    """
    Function to create correlation of base stats for movies
    """   
    
    #https://towardsdatascience.com/better-heatmaps-and-correlation-matrix-plots-in-python-41445d0f2bec
    
    #get all needed tweet columns
    movies_df = movie_helper.get_movies_df_with_opening_weekend()
    
    movies_df["tweet_count"] = movies_df.apply(lambda row: movie_helper.count_tweets(row.movieId)['count'], axis = 1)
    movies_df["budget_usd"] = movies_df["budget_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["uk_gross_usd"] = movies_df["uk_gross_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["domestic_gross_usd"] = movies_df["domestic_gross_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["worldwide_gross_usd"] = movies_df["worldwide_gross_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["international_gross_usd"] = movies_df["international_gross_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["gross_profit_usd"] = movies_df["gross_profit_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["opening_weekend_takings"] = movies_df["opening_weekend_takings"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    
    #list of columsn to use for correlation
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

    #generate heatmap
    generate_heatmap_from_df(df, columns)
    

def plot_df_as_table(df):
    """
    Function to plot dataframe as a table
    
    :param df: dataframe for plotting
    """   
    
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
    """
    Function to generate multiple boxplots for all cols in a dataframe
    
    :param df: dataframe for plotting
    """
    
    #https://towardsdatascience.com/dynamic-subplot-layout-in-seaborn-e777500c7386
    
    #work out number of rows and columns needed 
    num_plots = len(df.columns)
    total_cols = 5 if num_plots >= 5 else 4
    total_rows = num_plots//total_cols
    
    #create figure with enough axes
    fig, axs = plt.subplots(nrows=total_rows, ncols=total_cols, figsize=(7*total_cols, 7*total_rows), constrained_layout=True)
    ax_count = 0
    
    #plot boxplot for each column in df
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
    """
    Function to generate multiple distlpots for all cols in a dataframe
    
    :param df: dataframe for plotting
    """
    
    #https://towardsdatascience.com/dynamic-subplot-layout-in-seaborn-e777500c7386
    
    #work out number of rows and columns
    num_plots = len(df.columns)
    total_cols = 5 if num_plots >= 5 else 4
    total_rows = num_plots//total_cols

    #generate figure with enough axis
    fig, axs = plt.subplots(nrows=total_rows, ncols=total_cols, figsize=(7*total_cols, 7*total_rows), constrained_layout=True)
    ax_count = 0
    
    #create distplot for each column in dataframe
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
    
