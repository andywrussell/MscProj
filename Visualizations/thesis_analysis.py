#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  8 09:12:03 2020

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
import exploration
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime


def get_cols_to_drop():
      return [
        'movieId', 
        'imdbId',
        'certificates',
        'ukReleaseDate',
        'title', 
        'distributor', 
        'country', 
        'url', 
        'year', 
        'genres', 
        'keywords', 
        'enabled', 
        'hashtags',
        'twitterHandle',
        'totalRevenue',
        'investigate',
        'profit_class',
        'return_class',
        'uk_percentage_class',
        'run_up_tweets',
        'opening_tweets',
        'end_weekend',
        'first_run_end',
        'critical_start',
        'critical_end',
        'budget_class',
        'uk_gross_class']

def explore_movies():
    movies_df = movie_helper.get_movies_df_with_opening_weekend()
    movies_df = movie_helper.convert_financial_to_mil(movies_df)
    
    get_exploration_plots(movies_df, "YESY")
    
def get_exploration_plots(df, title):
    #drop certain columns
    drop_cols = get_cols_to_drop()
    
    describe_df = df.drop(columns=drop_cols)
    summary_df = pd.DataFrame(describe_df.describe().round(2).drop(['count']))
    
    #get summary stats
    exploration.plot_df_as_table(summary_df)
    
    #get correlations of key feilds
    exploration.generate_heatmap_from_df(describe_df, describe_df.columns)
    
  #  sns.pairplot(describe_df)
  #  plt.show()
    
    exploration.plot_boxplot_for_df(describe_df)
    exploration.plot_dist_for_df(describe_df)
    
   
def explore_movies_by_class(class_col):
    movies_df = movie_helper.get_movies_df_with_opening_weekend()
    movies_df = movie_helper.convert_financial_to_mil(movies_df)
    
    class_val_list = movies_df[class_col].unique()
    
    for class_val in class_val_list:
        class_df = movies_df[movies_df[class_col] == class_val]
        get_exploration_plots(class_df)
    
def define_success():
    #get box plots 
    exploration.plot_financial_box("budget_usd", "Budget Box Plot",  "Budget ($mil)")
    exploration.plot_financial_distribution("budget_usd", "Budget Distribution", "Budget ($mil)")
    
    exploration.plot_financial_box("gross_profit_usd", "Profit Box Plot", "Profit ($mil)")
    exploration.plot_financial_distribution("gross_profit_usd", "Profit Distribution", "Profit ($mil)")
    
    exploration.plot_financial_box("uk_gross_usd", "UK Takings Box Plot", "UK Gross ($mil)")
    exploration.plot_financial_distribution("uk_gross_usd", "UK Takings Distribution", "Uk Gross ($mil)")
    
    exploration.plot_float_box("return_percentage", "Return On Investment Box Plot", "Return Percentage")
    exploration.plot_float_distribution("return_percentage", "Return On Investment Distribution", "Return Percentage")
    
    exploration.plot_float_box("uk_percentage", "Percentage Takings in UK", "Percentage of Takings in UK")
    exploration.plot_float_distribution("uk_percentage", "Percentage Takings in UK Distribution", "Percentage of Takings in UK")
    
    #plot classes 
    exploration.plot_profit_classes()
    exploration.plot_return_classes()
    exploration.plot_uk_classes()
    
    #get bar distributions
    
def twitter_exploration(df):
    df["tweet_count"] = df.apply(lambda row: movie_helper.count_tweets(row.movieId)['count'], axis = 1)
    df["critical_period_tweet_count"] = df.apply(lambda row: movie_helper.count_tweets(row["movieId"], row["critical_start"], row["critical_end"])['count'], axis = 1)

    describe_df = df[['movieId', 'tweet_count', 'critical_period_tweet_count', 'run_up_tweets', 'opening_tweets']]   
    
    #describe_df = df.drop(columns=drop_cols)
    summary_df = pd.DataFrame(describe_df.describe().round(2).drop(['count']))
    
    describe_df = describe_df.drop(columns=['movieId'])
    
    exploration.plot_df_as_table(summary_df)
    exploration.plot_boxplot_for_df(describe_df)
    exploration.plot_dist_for_df(describe_df)
    
    # return df
    return describe_df
    
    
    
# def twitter_exploration():
    
#     exploration.gen_top_20_tweet_count()
#     exploration.gen_bottom_20_tweet_count()
    
#     #tweets vs budget 
#     exploration.plot_tweets_vs_finance("budget_usd", "Tweets vs Budget", "Budget ($mil)", "Tweets", logx=True)
#     #tweets vs profit
#     exploration.plot_tweets_vs_finance("gross_profit_usd", "Tweets vs Profit", "Profit ($mil)", "Tweets", logx=True)
#     #tweets vs uk
#     exploration.plot_tweets_vs_ratio("uk_percentage", "Tweets vs UK Revenue", "UK Percentage", "Tweets")
#     #tweets vs return
#     exploration.plot_tweets_vs_ratio("return_percentage", "Tweets vs Return", "Return Percentage", "Tweets")
    
    