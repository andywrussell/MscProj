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
    
   # exploration.plot_boxplot_for_df(describe_df)
#    exploration.plot_dist_for_df(describe_df)
    
    small_describe = describe_df = describe_df[["budget_usd", "uk_gross_usd", "gross_profit_usd", "return_percentage", "uk_percentage"]]
    small_summary = pd.DataFrame(describe_df.describe().round(2).drop(['count']))
    
    small_summary_t = small_summary.transpose()
    
    sns.pairplot(small_describe)
    plt.show()
    
    exploration.plot_df_as_table(small_summary)
    exploration.plot_df_as_table(small_summary_t)
    exploration.plot_dist_for_df(small_describe)
    
    return summary_df_t, small_summary_t
    
   
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
    budget_lst = ['< $10m (Small)', '$10m < $40m', '$40m < $100m', '$100m < $185m', '> 185m (Big)' ]
   # exploration.get_success_figure("budget_class", budget_lst, "budget_usd", movies_df, "Budget")
    exploration.plot_budget_classes()
    exploration.get_dist_figure("budget_usd", movies_df, "Budget ")
    
    #profit class
    profit_lst = ['< $0 (Flop)', '$0 < $90m', '$90m < $235m', '$235m < $700m', '> $700m (BlockBuster)' ]
   # exploration.get_success_figure("profit_class", profit_lst, "gross_profit_usd", movies_df, "Gross Profit")    
    exploration.plot_profit_classes()
    exploration.get_dist_figure("gross_profit_usd", movies_df, "Gross Profit")
   
    
    #uk gross class
    uk_lst =  ['< $1m (Small)', '$1m < $8m', '$8m < $20m', '$20m < $50m', '> $50m (Big)' ]
    #exploration.get_success_figure("uk_gross_class", uk_lst, "uk_gross_usd", movies_df, "UK Takings")
    exploration.plot_uk_taking_classes()
    exploration.get_dist_figure("uk_gross_usd", movies_df, "UK Takings") 
    
    
    #return percentage
    return_lst = ['< %0 (Flop)', '0% - 290%', '100% - 540%', '540% - 1000%', '> 1000% (BlockBuster)']
    #exploration.get_success_figure("return_class", return_lst, "return_percentage", movies_df, "Return Percentage", False)
    exploration.plot_return_classes()
    exploration.get_dist_figure("return_percentage", movies_df, "Return Percentage ")
    
    
    #uk percentage
    uk_percentage_lst = ['0% - 1%', '1% - 4%', '4% - 6%', '6% - 12%', '> 12%']
    #exploration.get_success_figure("uk_percentage_class", uk_percentage_lst, "uk_percentage", movies_df, "UK Percentage", False)
    exploration.plot_uk_classes()
    exploration.get_dist_figure("uk_percentage", movies_df, "UK Percentage")


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
    
    exploration.get_dist_figure("tweet_count", describe_df, "Tweet Count", money=False)
    exploration.get_dist_figure("critical_period_tweet_count", describe_df, "Critical Period Tweets", money=False)
    exploration.get_dist_figure("run_up_tweets", describe_df, "Run Up Tweets", money=False)
    exploration.get_dist_figure("opening_tweets", describe_df, "Opening Weekend Tweets", money=False)
    
   # g = sns.lmplot(x="uk_gross_usd", y="tweet_count", hue="profit_class", data=df)
    #profit class
    # g = sns.lmplot(x="uk_gross_usd", y="tweet_count", hue="profit_class", data=df, fit_reg=False)
    # sns.regplot(x="uk_gross_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    # g = sns.lmplot(x="budget_usd", y="tweet_count", hue="profit_class", data=df, fit_reg=False)
    # sns.regplot(x="budget_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    # g = sns.lmplot(x="gross_profit_usd", y="tweet_count", hue="profit_class", data=df, fit_reg=False)
    # sns.regplot(x="gross_profit_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    # g = sns.lmplot(x="return_percentage", y="tweet_count", hue="profit_class", data=df, fit_reg=False)
    # sns.regplot(x="return_percentage", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
       
    # g = sns.lmplot(x="uk_percentage", y="tweet_count", hue="profit_class", data=df, fit_reg=False)
    # sns.regplot(x="uk_percentage", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    # #return class
    # g = sns.lmplot(x="uk_gross_usd", y="tweet_count", hue="return_class", data=df, fit_reg=False)
    # sns.regplot(x="uk_gross_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    # g = sns.lmplot(x="budget_usd", y="tweet_count", hue="return_class", data=df, fit_reg=False)
    # sns.regplot(x="budget_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    # g = sns.lmplot(x="gross_profit_usd", y="tweet_count", hue="return_class", data=df, fit_reg=False)
    # sns.regplot(x="gross_profit_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    # g = sns.lmplot(x="return_percentage", y="tweet_count", hue="return_class", data=df, fit_reg=False)
    # sns.regplot(x="return_percentage", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
       
    # g = sns.lmplot(x="uk_percentage", y="tweet_count", hue="return_class", data=df, fit_reg=False)
    # sns.regplot(x="uk_percentage", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    # #uk percentage class
    # g = sns.lmplot(x="uk_gross_usd", y="tweet_count", hue="uk_percentage_class", data=df, fit_reg=False)
    # sns.regplot(x="uk_gross_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    # g = sns.lmplot(x="budget_usd", y="tweet_count", hue="uk_percentage_class", data=df, fit_reg=False)
    # sns.regplot(x="budget_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    # g = sns.lmplot(x="gross_profit_usd", y="tweet_count", hue="uk_percentage_class", data=df, fit_reg=False)
    # sns.regplot(x="gross_profit_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    # g = sns.lmplot(x="return_percentage", y="tweet_count", hue="uk_percentage_class", data=df, fit_reg=False)
    # sns.regplot(x="return_percentage", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
       
    # g = sns.lmplot(x="uk_percentage", y="tweet_count", hue="uk_percentage_class", data=df, fit_reg=False)
    # sns.regplot(x="uk_percentage", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    # #budget_class
    # g = sns.lmplot(x="uk_gross_usd", y="tweet_count", hue="budget_class", data=df, fit_reg=False)
    # sns.regplot(x="uk_gross_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    # g = sns.lmplot(x="budget_usd", y="tweet_count", hue="budget_class", data=df, fit_reg=False)
    # sns.regplot(x="budget_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    # g = sns.lmplot(x="gross_profit_usd", y="tweet_count", hue="budget_class", data=df, fit_reg=False)
    # sns.regplot(x="gross_profit_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    # g = sns.lmplot(x="return_percentage", y="tweet_count", hue="budget_class", data=df, fit_reg=False)
    # sns.regplot(x="return_percentage", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
       
    # g = sns.lmplot(x="uk_percentage", y="tweet_count", hue="budget_class", data=df, fit_reg=False)
    # sns.regplot(x="uk_percentage", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    # #uk gross class
    # g = sns.lmplot(x="uk_gross_usd", y="tweet_count", hue="uk_gross_class", data=df, fit_reg=False)
    # sns.regplot(x="uk_gross_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    # g = sns.lmplot(x="budget_usd", y="tweet_count", hue="uk_gross_class", data=df, fit_reg=False)
    # sns.regplot(x="budget_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    # g = sns.lmplot(x="gross_profit_usd", y="tweet_count", hue="uk_gross_class", data=df, fit_reg=False)
    # sns.regplot(x="gross_profit_usd", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
    
    # g = sns.lmplot(x="return_percentage", y="tweet_count", hue="uk_gross_class", data=df, fit_reg=False)
    # sns.regplot(x="return_percentage", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])
       
    # g = sns.lmplot(x="uk_percentage", y="tweet_count", hue="uk_gross_class", data=df, fit_reg=False)
    # sns.regplot(x="uk_percentage", y="tweet_count", data=df, scatter=False, ax=g.axes[0, 0])   
    # return df
    return summary_df_t

def get_correlation_for_tweets(full_week = False, week_inc_weekend = False, senti_class = None):
    correl_df = movie_helper.get_weekend_tweets_takings_correltation(full_week=full_week, week_inc_weekend=week_inc_weekend, senti_class = senti_class)
    
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
    where = "profit_class = '> $700m (BlockBuster)'"
    lowest_budget_successful_df = movie_helper.get_lowest_by_column('budget_usd', 2, where)
    lowest_budget_successful_df['reason'] = 'lowest budget successful'
    return_df = return_df.append(lowest_budget_successful_df)
    
    #lowest budget high return 
    where = "profit_class = '> 1000% (BlockBuster)'"
    lowest_budget_return_df = movie_helper.get_lowest_by_column('budget_usd', 2, where)
    lowest_budget_return_df['reason'] = 'lowest budget return'
    return_df = return_df.append(lowest_budget_successful_df)   
    
    #poorly performing movies who did well in the uk
    where = "(profit_class = '< $0 (Flop)' or return_class = '< %0 (Flop)' or return_class = '0% - 290%')"
    bad_uk_success_df = movie_helper.get_top_by_column('uk_percentage', 2, where)
    bad_uk_success_df['reason'] = 'bad film who did well in uk'
    return_df = return_df.append(bad_uk_success_df)
    
    #good movies that under performed in the uk
    where = "(profit_class = ' > $700m (BlockBuster)' or profit_class = '$235m < $700m' or return_class = '> 1000% (BlockBuster)' or return_class = '540% - %1000')"
    good_bad_uk_df = movie_helper.get_lowest_by_column('uk_percentage', 2, where)
    good_bad_uk_df['reason'] = 'good movies that underperformed in the uk'
    return_df = return_df.append(good_bad_uk_df)
    
    #Green book
    #low budget, blockbuster, 
    green_book_df = database_helper.select_query("movies", {"movieId" : 142})
    green_book_df["reason"] = "low budget, high return, and low two week takings"    
    return_df = return_df.append(green_book_df)
    
    #toy story
    toy_story_df = database_helper.select_query("movies", {"movieId" : 11})
    toy_story_df["reason"] = "Slow burner, animation, big budget" 
    return_df = return_df.append(toy_story_df)    
    
    #it
    it_df = database_helper.select_query("movies", {"movieId" : 5})
    it_df["reason"] = "Fast burner, good uk return"
    return_df = return_df.append(it_df)    
    
    return_df["tweet_count"] = return_df.apply(lambda row: movie_helper.count_tweets(row.movieId)['count'], axis = 1)
    return_df["critical_period_tweet_count"] = return_df.apply(lambda row: movie_helper.count_tweets(row["movieId"], row["critical_start"], row["critical_end"])['count'], axis = 1)
    
    #it - high two week takings but still took alot in uk
    
    
    return return_df.reset_index(drop=True)

def analyse_special_cases():
    special_cases_df = get_interesting_cases()
    
    unique_df = special_cases_df.drop_duplicates(subset="movieId", inplace=False, keep="first")
    
    
    special_cases = movie_helper.gen_movies(unique_df)
    
    #explore heatmaps and tweet correlations for special cases
    for movie in special_cases:
        movie.plot_weekend_revenue_mojo_vs_tweets(full_week=True)
     #   movie.plot_time_map()
     #   movie.plot_heated_time_map()
        movie.plot_tweets_over_time()
        
        # opening_start = movie.mojo_box_office_df.iloc[0]['start_date']
        # opening_end = movie.mojo_box_office_df.iloc[0]['end_date']
        # movie.plot_time_map(start_date = opening_start, end_date = opening_end)
        # movie.plot_heated_time_map(start_date = opening_start, end_date = opening_end)
        
        # run_up_start = datetime.combine((opening_start  - timedelta(days=7)), datetime.min.time())
        # run_up_end = datetime.combine((opening_start - timedelta(days=1)), datetime.max.time())
        # movie.plot_time_map(start_date = run_up_start, end_date = run_up_end)
        # movie.plot_heated_time_map(start_date = run_up_start, end_date = run_up_end)
        
        # critical_start = movie.critical_start
        # critical_end = movie.critical_end
        # movie.plot_time_map(start_date = critical_start, end_date = critical_end)
        # movie.plot_heated_time_map(start_date = critical_start, end_date = critical_end)
        
def twitter_weekly():
    weekend_tweet_cor = get_correlation_for_tweets()
    weekly_tweet_cor = get_correlation_for_tweets(full_week=True)
        
    

def event_peak_analysis():
    event_results = movie_helper.get_movie_tweet_events()

    all_events_df = event_results["all_events"]
    peak_events_df = event_results["peak_events"]
    trailer_peaks_df = event_results["trailer_peaks"]
    
    no_peaks_df = all_events_df[(all_events_df["movie_release"] == False)
                                & (all_events_df["movie_opening_weekend"] == False) 
                                & (all_events_df["youtubeId"] == "NO")
                                & (all_events_df["count"] == 0)]
    
    no_peaks_movies = no_peaks_df["movieId"].unique()

    opening_release_peaks = peak_events_df[(peak_events_df["movie_release"] == 1) | (peak_events_df["movie_opening_weekend"] == 1)]
    opening_release_peaks_movies = opening_release_peaks["movieId"].unique()

    trailers_top_3_peaks = trailer_peaks_df[trailer_peaks_df["rank"] <= 3]
    top_trailer_movies = trailers_top_3_peaks["movieId"].unique()

    #return opening_release_peaks
    movies_df = movie_helper.get_movies_df_with_opening_weekend()
    movies_df = movie_helper.convert_financial_to_mil(movies_df)  
    
    movies_df["opening_release_peaks"] = movies_df.apply(lambda row: row["movieId"] in opening_release_peaks_movies, axis=1)
    movies_df["trailer_peaks_top_3"] = movies_df.apply(lambda row: row["movieId"] in top_trailer_movies, axis=1)
    
    describe_cols = ['budget_usd','gross_profit_usd', 'return_percentage', 'uk_gross_usd', 'uk_percentage']
    
    films_with_release_peaks = movies_df[movies_df["opening_release_peaks"]]
    films_without_release_peaks = movies_df[movies_df["opening_release_peaks"] == False]
    
    #get success factor summary for films with release peaks
    with_release_summary_df = pd.DataFrame(films_with_release_peaks[describe_cols].describe().round(2).drop(['count']))
    with_release_summary_df_t = with_release_summary_df.transpose()
    
    #get success factor summary for films without release peaks
    without_release_summary_df = pd.DataFrame(films_without_release_peaks[describe_cols].describe().round(2).drop(['count']))
    without_release_summary_df_t = without_release_summary_df.transpose()    
    
    print("{0} films have release peaks".format(films_with_release_peaks.shape[0]))
    
    films_with_trailer_peaks = movies_df[movies_df["trailer_peaks_top_3"]]
    films_without_trailer_peaks = movies_df[movies_df["trailer_peaks_top_3"] == False]
    
    #get success factor summary for films with trailer peaks
    with_trailer_summary_df = pd.DataFrame(films_with_trailer_peaks[describe_cols].describe().round(2).drop(['count']))
    with_trailer_summary_df_t = with_trailer_summary_df.transpose()
    
    #get success factor summary for films without trailer peaks
    without_trailer_summary_df = pd.DataFrame(films_without_trailer_peaks[describe_cols].describe().round(2).drop(['count']))
    without_trailer_summary_df_t = without_trailer_summary_df.transpose()   
    
    print("{0} films with trailers in top 3 peaks".format(films_with_trailer_peaks.shape[0]))
    
    no_peaks_movies_df = movies_df[movies_df["movieId"].isin(no_peaks_movies)]
    
    print("{0} films with no peaks".format(no_peaks_movies_df.shape[0]))
    
    
    #analyse trailer tweets 
    trailer_tweets = movie_helper.get_trailer_tweet_counts()
    
    movies_df = pd.merge(movies_df, trailer_tweets, on='movieId', how='left')
    
    return_vals = {"movies_df" : movies_df,
                   "films_with_release_peaks" : films_with_release_peaks,
                   "with_release_summary_df_t" : with_release_summary_df_t,
                   "films_without_release_peaks" : films_without_release_peaks,
                   "without_release_summary_df_t" : without_release_summary_df_t,
                   "films_with_trailer_peaks" : films_with_trailer_peaks,
                   "with_trailer_summary_df_t" : with_trailer_summary_df_t,
                   "films_without_trailer_peaks" : films_without_trailer_peaks,
                   "without_trailer_summary_df_t" : without_trailer_summary_df_t}
    
    return return_vals
    
    

def analyse_tweet_sentiment():
    movies_df = movie_helper.get_movies_df_with_opening_weekend()
    movies_df = movie_helper.convert_financial_to_mil(movies_df)           
    

    
    movies_df["tweet_count"] = movies_df.apply(lambda row: movie_helper.count_tweets(row.movieId)['count'], axis = 1)
    movies_df["positive_tweets"] = movies_df.apply(lambda row: movie_helper.count_tweets(row.movieId, senti_class = 'positive')['count'], axis = 1)
    movies_df["positive_percentage"] = movies_df["positive_tweets"] / movies_df["tweet_count"]
    
    movies_df["neutral_tweets"] = movies_df.apply(lambda row: movie_helper.count_tweets(row.movieId, senti_class = 'neutral')['count'], axis = 1)
    movies_df["neutral_percentage"] = movies_df["neutral_tweets"] / movies_df["tweet_count"]
    
    movies_df["negative_tweets"] = movies_df.apply(lambda row: movie_helper.count_tweets(row.movieId, senti_class = 'negative')['count'], axis = 1)  
    movies_df["negative_percentage"] = movies_df["negative_tweets"] / movies_df["tweet_count"]
    
    describe_df = movies_df[['movieId', 
                             'tweet_count', 
                             'positive_tweets', 
                             'positive_percentage', 
                             'neutral_tweets', 
                             'neutral_percentage', 
                             'negative_tweets', 
                             'negative_percentage']]
    
    
    #describe_df = df.drop(columns=drop_cols)
    summary_df = pd.DataFrame(describe_df.describe().round(2).drop(['count']))
    summary_df_t = summary_df.drop(columns=['movieId']).transpose()
    describe_df = describe_df.drop(columns=['movieId'])
    
    exploration.plot_df_as_table(summary_df)
    exploration.plot_df_as_table(summary_df_t)
    exploration.plot_boxplot_for_df(describe_df)
    exploration.plot_dist_for_df(describe_df)
    
    correl_df = movies_df.drop(columns=get_cols_to_drop())
    correl_df = correl_df[['budget_usd',
                           'gross_profit_usd', 
                           'return_percentage', 
                           'uk_gross_usd', 
                           'uk_percentage', 
                           'tweet_count', 
                           'positive_tweets',
                           'positive_percentage',
                           'neutral_tweets', 
                           'neutral_percentage',
                           'negative_tweets',
                           'negative_percentage']]

    exploration.generate_heatmap_from_df(correl_df, correl_df.columns, "TEST")
    
    
    weekend_tweet_cor_pos = get_correlation_for_tweets(senti_class = "positive")
    weekly_tweet_cor_pos = get_correlation_for_tweets(full_week=True, senti_class = "positive")
    
    weekend_tweet_cor_neg = get_correlation_for_tweets(senti_class = "negative")
    weekly_tweet_cor_neg = get_correlation_for_tweets(full_week=True, senti_class = "negative")
    
    return weekend_tweet_cor_neg, weekly_tweet_cor_neg
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
    
    