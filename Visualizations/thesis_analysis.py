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
from datetime import timedelta

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
    
    return get_exploration_plots(movies_df, "Test")
    
    #create table of variables t0 use 
    #plot success measures 
    
def get_exploration_plots(df, title):
    #drop certain columns
    drop_cols = get_cols_to_drop()
    
    describe_df = df.drop(columns=drop_cols)
    summary_df = pd.DataFrame(describe_df.describe().round(2).drop(['count']))
    
    summary_df_t = summary_df.transpose()
    
    #get summary stats
    exploration.plot_df_as_table(summary_df)
    exploration.plot_df_as_table(summary_df_t)
    
    #get correlations of key feilds
    exploration.generate_heatmap_from_df(describe_df, describe_df.columns, title)
    
  #  sns.pairplot(describe_df)
  #  plt.show()
    
    exploration.plot_boxplot_for_df(describe_df)
    exploration.plot_dist_for_df(describe_df)
    
    return summary_df_t
    
   
def explore_movies_by_class(class_col):
    movies_df = movie_helper.get_movies_df_with_opening_weekend()
    movies_df = movie_helper.convert_financial_to_mil(movies_df)
    
    class_val_list = movies_df[class_col].unique()
    
    for class_val in class_val_list:
        class_df = movies_df[movies_df[class_col] == class_val]
        get_exploration_plots(class_df)
    
def define_success():
    movies_df = movie_helper.get_movies_df_with_opening_weekend()
    movies_df = movie_helper.convert_financial_to_mil(movies_df)
    
    #budget class
    budget_lst = ['< $10m (Small)', '$10m < $25m', '$25m < $50m', '$50m < $150m', ' > $150m (Big)' ]
    exploration.get_success_figure("budget_class", budget_lst, "budget_usd", movies_df, "Budget")
    
    #profit class
    profit_lst = ['< $0 (Flop)', '$0 < $50m', '$50m < $150m', '$150m < $300m', ' > $300m (BlockBuster)' ]
    exploration.get_success_figure("profit_class", profit_lst, "gross_profit_usd", movies_df, "Gross Profit")
    
    #uk gross class
    uk_lst = ['< $1m (Small)', '$1m < $5m', '$5m < $15m', '$15m < $50m', ' > $50m (Big)' ]
    exploration.get_success_figure("uk_gross_class", uk_lst, "uk_gross_usd", movies_df, "UK Takings")
     
    #return percentage
    return_lst = ['< %0 (Flop)', '%0-100%', '%100-%400', '%400-%1000', '> %1000 (BlockBuster)']
    exploration.get_success_figure("return_class", return_lst, "return_percentage", movies_df, "Return Percentage", False)
    
    #uk percentage
    uk_percentage_lst = ['0% - 2%', '2% - 4%', '4% - 6%', '6% - 12%', '> 12%']   
    exploration.get_success_figure("uk_percentage_class", uk_percentage_lst, "uk_percentage", movies_df, "UK Percentage", False)

    #get bar distributions
    
def twitter_exploration(df):
    df["tweet_count"] = df.apply(lambda row: movie_helper.count_tweets(row.movieId)['count'], axis = 1)
    df["critical_period_tweet_count"] = df.apply(lambda row: movie_helper.count_tweets(row["movieId"], row["critical_start"], row["critical_end"])['count'], axis = 1)

    describe_df = df[['movieId', 'tweet_count', 'critical_period_tweet_count', 'run_up_tweets', 'opening_tweets']]   
    
    #describe_df = df.drop(columns=drop_cols)
    summary_df = pd.DataFrame(describe_df.describe().round(2).drop(['count']))
    summary_df_t = summary_df.drop(columns=['movieId']).transpose()
    describe_df = describe_df.drop(columns=['movieId'])
    
    exploration.plot_df_as_table(summary_df)
    exploration.plot_df_as_table(summary_df_t)
    exploration.plot_boxplot_for_df(describe_df)
    exploration.plot_dist_for_df(describe_df)
    
    correl_df = df.drop(columns=get_cols_to_drop())
    correl_df = df[['budget_usd','gross_profit_usd', 'return_percentage', 'uk_gross_usd', 'uk_percentage', 'tweet_count', 'critical_period_tweet_count', 'run_up_tweets', 'opening_tweets']]

    #get correlations of key feilds
    exploration.generate_heatmap_from_df(correl_df, correl_df.columns, "TEST")
    
   # g = sns.lmplot(x="uk_gross_usd", y="tweet_count", hue="profit_class", data=df)
    #profit class
    g = sns.lmplot(x="uk_gross_usd", y="tweet_count", hue="profit_class", data=df, fit_reg=False)
    sns.regplot(x="uk_gross_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    g = sns.lmplot(x="budget_usd", y="tweet_count", hue="profit_class", data=df, fit_reg=False)
    sns.regplot(x="budget_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    g = sns.lmplot(x="gross_profit_usd", y="tweet_count", hue="profit_class", data=df, fit_reg=False)
    sns.regplot(x="gross_profit_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    g = sns.lmplot(x="return_percentage", y="tweet_count", hue="profit_class", data=df, fit_reg=False)
    sns.regplot(x="return_percentage", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
       
    g = sns.lmplot(x="uk_percentage", y="tweet_count", hue="profit_class", data=df, fit_reg=False)
    sns.regplot(x="uk_percentage", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    #return class
    g = sns.lmplot(x="uk_gross_usd", y="tweet_count", hue="return_class", data=df, fit_reg=False)
    sns.regplot(x="uk_gross_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    g = sns.lmplot(x="budget_usd", y="tweet_count", hue="return_class", data=df, fit_reg=False)
    sns.regplot(x="budget_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    g = sns.lmplot(x="gross_profit_usd", y="tweet_count", hue="return_class", data=df, fit_reg=False)
    sns.regplot(x="gross_profit_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    g = sns.lmplot(x="return_percentage", y="tweet_count", hue="return_class", data=df, fit_reg=False)
    sns.regplot(x="return_percentage", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
       
    g = sns.lmplot(x="uk_percentage", y="tweet_count", hue="return_class", data=df, fit_reg=False)
    sns.regplot(x="uk_percentage", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    #uk percentage class
    g = sns.lmplot(x="uk_gross_usd", y="tweet_count", hue="uk_percentage_class", data=df, fit_reg=False)
    sns.regplot(x="uk_gross_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    g = sns.lmplot(x="budget_usd", y="tweet_count", hue="uk_percentage_class", data=df, fit_reg=False)
    sns.regplot(x="budget_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    g = sns.lmplot(x="gross_profit_usd", y="tweet_count", hue="uk_percentage_class", data=df, fit_reg=False)
    sns.regplot(x="gross_profit_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    g = sns.lmplot(x="return_percentage", y="tweet_count", hue="uk_percentage_class", data=df, fit_reg=False)
    sns.regplot(x="return_percentage", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
       
    g = sns.lmplot(x="uk_percentage", y="tweet_count", hue="uk_percentage_class", data=df, fit_reg=False)
    sns.regplot(x="uk_percentage", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    #budget_class
    g = sns.lmplot(x="uk_gross_usd", y="tweet_count", hue="budget_class", data=df, fit_reg=False)
    sns.regplot(x="uk_gross_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    g = sns.lmplot(x="budget_usd", y="tweet_count", hue="budget_class", data=df, fit_reg=False)
    sns.regplot(x="budget_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    g = sns.lmplot(x="gross_profit_usd", y="tweet_count", hue="budget_class", data=df, fit_reg=False)
    sns.regplot(x="gross_profit_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    g = sns.lmplot(x="return_percentage", y="tweet_count", hue="budget_class", data=df, fit_reg=False)
    sns.regplot(x="return_percentage", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
       
    g = sns.lmplot(x="uk_percentage", y="tweet_count", hue="budget_class", data=df, fit_reg=False)
    sns.regplot(x="uk_percentage", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    #uk gross class
    g = sns.lmplot(x="uk_gross_usd", y="tweet_count", hue="uk_gross_class", data=df, fit_reg=False)
    sns.regplot(x="uk_gross_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    g = sns.lmplot(x="budget_usd", y="tweet_count", hue="uk_gross_class", data=df, fit_reg=False)
    sns.regplot(x="budget_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    g = sns.lmplot(x="gross_profit_usd", y="tweet_count", hue="uk_gross_class", data=df, fit_reg=False)
    sns.regplot(x="gross_profit_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    g = sns.lmplot(x="return_percentage", y="tweet_count", hue="uk_gross_class", data=df, fit_reg=False)
    sns.regplot(x="return_percentage", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
       
    g = sns.lmplot(x="uk_percentage", y="tweet_count", hue="uk_gross_class", data=df, fit_reg=False)
    sns.regplot(x="uk_percentage", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])   
    # return df
    return summary_df_t

def get_correlation_for_tweets(full_week = False, week_inc_weekend = False):
    correl_df = movie_helper.get_weekend_tweets_takings_correltation(full_week=full_week, week_inc_weekend=week_inc_weekend)
    
    #only take perasons
    correl_df = correl_df[(correl_df["method"] == 'pearson') | (correl_df["method"] == 'NA')]
    
    #test for significance
    correl_df['stat_significance'] = correl_df.apply(lambda row: (row['p_val'] < 0.05) & (row["method"] == "pearson"), axis=1)
    
    correl_df = correl_df.drop(columns="method")
    correl_df = correl_df.sort_values(by="tweet_count", ascending=False)
    correl_df = correl_df.round({"coef" : 5})
    
    return correl_df
    
def get_interesting_cases():
    return_df = pd.DataFrame()
    
    #get most profitable
    most_profitable_df = movie_helper.get_top_by_column('gross_profit_usd', 1)
    most_profitable_df['reason'] = 'most_profitable'
    return_df = return_df.append(most_profitable_df)
    
    least_profitable_df = movie_helper.get_lowest_by_column('gross_profit_usd', 1)
    least_profitable_df['reason'] = 'least profitable'    
    return_df = return_df.append(least_profitable_df)    

    #get biggest uk takings
    most_uk_df = movie_helper.get_top_by_column('uk_gross_usd', 1)
    most_uk_df['reason'] = 'most gross uk'
    return_df = return_df.append(most_uk_df)    
    
    least_gross_uk_df = movie_helper.get_lowest_by_column('uk_gross_usd', 1)
    least_gross_uk_df['reason'] = 'least gross uk' 
    return_df = return_df.append(least_gross_uk_df)    
    
    #get best return
    most_return_df = movie_helper.get_top_by_column('return_percentage', 1)
    most_return_df['reason'] = 'most return'
    return_df = return_df.append(most_return_df)    
    
    least_return_df = movie_helper.get_lowest_by_column('return_percentage', 1)
    least_return_df['reason'] = 'least return'  
    return_df = return_df.append(least_return_df)    
    
    #bes uk percentage
    most_uk_percentage_df = movie_helper.get_top_by_column('uk_percentage', 1)
    most_uk_percentage_df['reason'] = 'most uk percentage'
    return_df = return_df.append(most_uk_percentage_df)    
    
    least_uk_percentage_df = movie_helper.get_lowest_by_column('uk_percentage', 1)
    least_uk_percentage_df['reason'] = 'least uk percentage' 
    return_df = return_df.append(least_uk_percentage_df)    
    
    #biggest budget
    biggest_budget_df = movie_helper.get_top_by_column('budget_usd', 1)
    biggest_budget_df['reason'] = 'biggest budget'
    return_df = return_df.append(biggest_budget_df)
    
    smallest_budget_df = movie_helper.get_lowest_by_column('budget_usd', 2)
    smallest_budget_df['reason'] = 'smallest budget'  
    return_df = return_df.append(smallest_budget_df)
    
    #lowest budget successful
    where = "profit_class = ' > $300m (BlockBuster)'"
    lowest_budget_successful_df = movie_helper.get_lowest_by_column('budget_usd', 1, where)
    lowest_budget_successful_df['reason'] = 'lowest budget successful'
    return_df = return_df.append(lowest_budget_successful_df)
    
    #poorly performing movies who did well in the uk
    where = "(profit_class = '< $0 (Flop)' or return_class = '< %0 (Flop)' or return_class = '%0-100%')"
    bad_uk_success_df = movie_helper.get_top_by_column('uk_percentage', 2, where)
    bad_uk_success_df['reason'] = 'bad film who did well in uk'
    return_df = return_df.append(bad_uk_success_df)
    
    #good movies that under performed in the uk
    where = "(profit_class = ' > $300m (BlockBuster)' or profit_class = '$150m < $300m' or return_class = '> %1000 (BlockBuster)' or return_class = '%400-%1000')"
    good_bad_uk_df = movie_helper.get_lowest_by_column('uk_percentage', 2, where)
    good_bad_uk_df['reason'] = 'good movies that underperformed in the uk'
    return_df = return_df.append(good_bad_uk_df)
    
    return return_df.reset_index(drop=True)

def analyse_special_cases():
    special_cases_df = get_interesting_cases()
    special_cases = movie_helper.gen_movies(special_cases_df)
    
    #explore heatmaps and tweet correlations for special cases
    for movie in special_cases:
        movie.plot_weekend_revenue_mojo_vs_tweets()
        movie.plot_weekend_revenue_mojo_vs_tweets(full_week=True)
        movie.plot_time_map()
        movie.plot_heated_time_map()
        
        opening_start = movie.mojo_box_office_df.iloc[0]['start_date']
        opening_end = movie.mojo_box_office_df.iloc[0]['end_date']
        movie.plot_time_map(start_date = opening_start, end_date = opening_end)
        movie.plot_heated_time_map(start_date = opening_start, end_date = opening_end)
        
        run_up_start = datetime.combine((opening_start  - timedelta(days=7)), datetime.min.time())
        run_up_end = datetime.combine((opening_start - timedelta(days=1)), datetime.max.time())
        movie.plot_time_map(start_date = run_up_start, end_date = run_up_end)
        movie.plot_heated_time_map(start_date = run_up_start, end_date = run_up_end)
        
        critical_start = movie.critical_start
        critical_end = movie.critical_end
        movie.plot_time_map(start_date = critical_start, end_date = critical_end)
        movie.plot_heated_time_map(start_date = critical_start, end_date = critical_end)
        
def twitter_weekly():
    weekend_tweet_cor = get_correlation_for_tweets()
    weekly_tweet_cor = get_correlation_for_tweets(full_week=True)
        
def analyse_tweet_sentiment():
    movies_df = movie_helper.get_movies_df_with_opening_weekend()
    movies_df = movie_helper.convert_financial_to_mil(movies_df)     
        
    
    movies_df["tweet_count"] = movies_df.apply(lambda row: movie_helper.count_tweets(row.movieId)['count'], axis = 1)
    movies_df["positive_tweets"] = movies_df.apply(lambda row: movie_helper.count_tweets(row.movieId, senti_class = 'positive')['count'], axis = 1)
    movies_df["neutral_tweets"] = movies_df.apply(lambda row: movie_helper.count_tweets(row.movieId, senti_class = 'positive')['count'], axis = 1)
    
    
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
    
    