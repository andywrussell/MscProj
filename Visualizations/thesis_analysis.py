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
import spatial
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
    exploration.get_success_figure("budget_class", budget_lst, "budget_usd", movies_df, "Budget")
    
    #profit class
    profit_lst = ['< $0 (Flop)', '$0 < $90m', '$90m < $235m', '$235m < $700m', '> $700m (BlockBuster)' ]
    exploration.get_success_figure("profit_class", profit_lst, "gross_profit_usd", movies_df, "Gross Profit")    
    
    #uk gross class
    uk_lst =  ['< $1m (Small)', '$1m < $8m', '$8m < $20m', '$20m < $50m', '> $50m (Big)' ]
    exploration.get_success_figure("uk_gross_class", uk_lst, "uk_gross_usd", movies_df, "UK Takings")
    
    #return percentage
    return_lst = ['< %0 (Flop)', '0% - 290%', '100% - 540%', '540% - 1000%', '> 1000% (BlockBuster)']
    exploration.get_success_figure("return_class", return_lst, "return_percentage", movies_df, "Return Percentage", False)
    
    #uk percentage
    uk_percentage_lst = ['0% - 1%', '1% - 4%', '4% - 6%', '6% - 12%', '> 12%']
    exploration.get_success_figure("uk_percentage_class", uk_percentage_lst, "uk_percentage", movies_df, "UK Percentage", False)
    
def analyse_tweets(df):
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
    
    return summary_df_t

def get_correlation_for_tweets(full_week = False, week_inc_weekend = False, senti_class = None, percentage = False):
    correl_df = movie_helper.get_weekend_tweets_takings_correltation(full_week=full_week, week_inc_weekend=week_inc_weekend, senti_class = senti_class, percentage = False)
    
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
    weekend_tweet_cor_sig = weekend_tweet_cor[weekend_tweet_cor["stat_significance"] == True]
    weekend_tweet_cor_sig_desc = weekend_tweet_cor_sig.describe()
    weekend_tweet_cor_sig_desc_t = weekend_tweet_cor_sig_desc.drop(columns=["movieId"]).transpose()
        
    weekly_tweet_cor = get_correlation_for_tweets(full_week=True)   
    weekly_tweet_cor_sig = weekly_tweet_cor[weekly_tweet_cor["stat_significance"] == True]
    weekly_tweet_cor_sig_desc = weekly_tweet_cor_sig.describe()
    weekly_tweet_cor_sig_desc_t = weekly_tweet_cor_sig_desc.drop(columns=["movieId"]).transpose()
    
    results = {"weekend_tweet_cor" : weekend_tweet_cor,
               "weekend_tweet_cor_sig" : weekend_tweet_cor_sig,
               "weekend_tweet_cor_sig_desc" : weekend_tweet_cor_sig_desc,
               "weekend_tweet_cor_sig_desc_t" : weekend_tweet_cor_sig_desc_t,
               "weekly_tweet_cor" : weekly_tweet_cor,
               "weekly_tweet_cor_sig" : weekly_tweet_cor_sig,
               "weekly_tweet_cor_sig_desc" : weekly_tweet_cor_sig_desc,
               "weekly_tweet_cor_sig_desc_t" : weekly_tweet_cor_sig_desc_t}

    return results

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
    
    
    #create plots
    fig, ax = plt.subplots(figsize=(10,10))
    
    sns.distplot(films_with_release_peaks["uk_gross_usd"], hist=False, ax=ax)
    sns.distplot(films_without_release_peaks["uk_gross_usd"], hist=False, ax=ax)
    sns.distplot(films_with_trailer_peaks["uk_gross_usd"], hist=False, ax=ax)
    sns.distplot(films_without_trailer_peaks["uk_gross_usd"], hist=False, ax=ax)
    
    plt.show()
    
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
    
    
def get_class_order_df():
    class_order_list = [{"class_name" :"profit_class",
                   "order_list" : ['< $0 (Flop)', '$0 < $90m', '$90m < $235m', '$235m < $700m', '> $700m (BlockBuster)' ],
                   "class_title" : "Profit ($mil)"},
                  {"class_name" :"budget_class",
                   "order_list" : ['< $10m (Small)', '$10m < $40m', '$40m < $100m', '$100m < $185m', '> 185m (Big)' ],
                   "class_title" : "Budget ($mil)"},
                  {"class_name" :"uk_gross_class",
                   "order_list" :  ['< $1m (Small)', '$1m < $8m', '$8m < $20m', '$20m < $50m', '> $50m (Big)' ],
                   "class_title" : "UK Takings ($mil)"},
                  {"class_name" :"return_class",
                   "order_list" : ['< %0 (Flop)', '0% - 290%', '100% - 540%', '540% - 1000%', '> 1000% (BlockBuster)'],
                   "class_title" : "Return Percentage"},
                  {"class_name" :"uk_percentage_class",
                   "order_list" : ['0% - 1%', '1% - 4%', '4% - 6%', '6% - 12%', '> 12%'],
                   "class_title" : "Percentage Takings in UK"}]
    
    return pd.DataFrame(class_order_list)

def analyse_tweet_sentiment():
    movies_df = movie_helper.get_movies_df_with_opening_weekend()
    movies_df = movie_helper.convert_financial_to_mil(movies_df)           
    movies_df = movie_helper.get_movies_df_with_sentiment_summaryies(movies_df)

    #print general spread of tweetsnegative_tweets_percentage
    total_pos =  movies_df["positive_tweets"].sum()
    total_neu =  movies_df["neutral_tweets"].sum()
    total_neg =  movies_df["negative_tweets"].sum()
    
    total_tweets = movies_df["tweet_count"].sum()
    
    print("{0} total tweets".format(total_tweets))
    print("{0} positive tweets".format(total_pos))
    print("{0} neutral tweets".format(total_neu))
    print("{0} negative tweets".format(total_neg))
    
    senti_df = [{"count" : total_pos, "class" : "positive"},
              {"count" : total_neu, "class" : "neutral"},
              {"count" : total_neg, "class" : "negative"}]
    
    senti_df = pd.DataFrame(senti_df)
    ax = sns.barplot(x="class", y="count", data=senti_df, orient="v")
    ax.set(xlabel="Sentiment Class", ylabel='Tweet Count')
    ax.set_title("Movie Tweets Sentiment Class")
    plt.show()
    
    #get top pos and neg for total and critical period and trailers
    exploration.get_top_percentage_tweets(movies_df, "positive_tweets_percentage", "Top Percentage of Positive Tweets", "Positive Tweet Percentage")
    exploration.get_top_percentage_tweets(movies_df, "negative_tweets_percentage", "Top Percentage of Negative Tweets", "Negative Tweet Percentage")
    exploration.get_top_percentage_tweets(movies_df, "critical_period_pos_percentage", "Top Percentage of Positive Tweets (Critical Period)", "Positive Tweet Percentage")
    exploration.get_top_percentage_tweets(movies_df, "critical_period_neg_percentage", "Top Percentage of Negative Tweets (Critical Period)", "Negative Tweet Percentage")
    exploration.get_top_percentage_tweets(movies_df, "trailer_pos_percentage", "Top Percentage of Positive Tweets (Trailers)", "Positive Tweet Percentage")
    exploration.get_top_percentage_tweets(movies_df, "trailer_neg_percentage", "Top Percentage of Negative Tweets (Trailers)", "Negative Tweet Percentage")
    
   
    class_order_df = get_class_order_df()
    
    class_sent_df = movie_helper.get_tweet_senti_counts_by_class(movies_df, class_list=class_order_df["class_name"])
    
    for index, row in class_order_df.iterrows():
        class_name = row["class_name"]
        class_title = row["class_title"]
        
        class_df = class_sent_df[class_sent_df["class_name"] == class_name]
        
        class_order = class_order_df[class_order_df["class_name"] == class_name].iloc[0]["order_list"]
        
        #plot grouped bar
        hue_order = ["positive", "negative", "neutral"]
        hue_palette = {"positive" : "medium green", "negative" : "pale red", "neutral" : "amber"}
        
        grp_bar = sns.catplot(x="class_val", y="tweet_count", hue="senti_class", data=class_df, order=class_order, hue_order=hue_order, kind="bar")
        grp_bar.set_ylabels("Tweet Counts")
        grp_bar.set_xlabels(class_title)
        plt.title("Tweet Count by " + class_title)
        plt.xticks(rotation=40)
        plt.show()

        #plot percentage stacked bar 
        data = class_df.pivot(index="class_val", columns="senti_class", values="tweet_count")
        data = data.reindex(class_order)
        data = data[["positive", "negative", "neutral"]]
        
        stacked = data.plot.bar(stacked=True)
        patches, labels = stacked.get_legend_handles_labels()
        stacked.legend(patches, hue_order, bbox_to_anchor=(1, 0.5))
        stacked.set(xlabel=class_title, ylabel='Percentage of Tweets')
        plt.title("Tweet Sentiment by " + class_title)
        plt.xticks(rotation=40)
        plt.show()
    
    
    describe_df = movies_df[['movieId', 
                             'tweet_count',
                             'positive_tweets',
                             'positive_tweets_percentage',
                             'neutral_tweets',
                             'neutral_tweets_percentage',
                             'negative_tweets',
                             'negative_tweets_percentage',
                             'critical_period_tweet_count', 
                             'critical_period_tweet_pos',
                             'critical_period_pos_percentage',
                             'critical_period_tweet_neu',
                             'critical_period_neu_percentage',
                             'critical_period_tweet_neg',
                             'critical_period_neg_percentage',
                             'run_up_tweets',
                             'run_up_tweets_pos',
                             'run_up_pos_percentage',
                             'run_up_tweets_neu',
                             'run_up_neu_percentage',
                             'run_up_tweets_neg',
                             'run_up_neg_percentage',
                             'opening_tweets', 
                             'opening_tweets_pos',
                             'opening_pos_percentage',
                             'opening_tweets_neu',
                             'opening_neu_percentage',
                             'opening_tweets_neg',
                             'opening_pos_percentage',
                             'trailer_tweet_count', 
                             'trailer_tweet_pos',
                             'trailer_pos_percentage',
                             'trailer_tweet_neu',
                             'trailer_neu_percentage',
                             'trailer_tweet_neg',
                             'trailer_pos_percentage']]


    summary_df = pd.DataFrame(describe_df.describe().round(2).drop(['count']))
    summary_df_t = summary_df.drop(columns=['movieId']).transpose()
    
    exploration.plot_df_as_table(summary_df_t)
    
    correl_df = movies_df[['budget_usd',
                           'gross_profit_usd', 
                            'return_percentage', 
                            'uk_gross_usd', 
                            'uk_percentage', 
                             'tweet_count', 
                             'positive_tweets',
                             'negative_tweets',
                             'neutral_tweets',
                             'positive_tweets_percentage',
                             'negative_tweets_percentage',
                             'neutral_tweets_percentage']]

    exploration.generate_heatmap_from_df(correl_df, correl_df.columns, "TEST")    
    
    critical_correl_df = movies_df[['budget_usd',
                           'gross_profit_usd', 
                            'return_percentage', 
                            'uk_gross_usd', 
                            'uk_percentage', 
                             'critical_period_tweet_count', 
                             'critical_period_tweet_pos',
                             'critical_period_tweet_neg',
                             'critical_period_tweet_neu',
                             'critical_period_pos_percentage',
                             'critical_period_neg_percentage',
                             'critical_period_neu_percentage']]

    exploration.generate_heatmap_from_df(critical_correl_df, critical_correl_df.columns, "TEST")
    
    run_up_correl_df = movies_df[['budget_usd',
                           'gross_profit_usd', 
                            'return_percentage', 
                            'uk_gross_usd', 
                            'uk_percentage', 
                            'run_up_tweets', 
                             'run_up_tweets_pos',
                             'run_up_tweets_neg',
                             'run_up_tweets_neu',
                             'run_up_pos_percentage',
                             'run_up_neg_percentage',
                             'run_up_neu_percentage']]
    
    exploration.generate_heatmap_from_df(run_up_correl_df, run_up_correl_df.columns, "TEST")    
  
  
    opening_correl_df = movies_df[['budget_usd',
                           'gross_profit_usd', 
                            'return_percentage', 
                            'uk_gross_usd', 
                            'uk_percentage', 
                            'opening_tweets', 
                             'opening_tweets_pos',
                             'opening_tweets_neg',
                             'opening_tweets_neu',
                             'opening_pos_percentage',
                             'opening_neg_percentage',
                             'opening_neu_percentage']]
    
    exploration.generate_heatmap_from_df(opening_correl_df, opening_correl_df.columns, "TEST")
    
    trailer_correl_df = movies_df[['budget_usd',
                           'gross_profit_usd', 
                            'return_percentage', 
                            'uk_gross_usd', 
                            'uk_percentage', 
                             'trailer_tweet_count', 
                             'trailer_tweet_pos',
                             'trailer_pos_percentage',
                             'trailer_tweet_neu',
                             'trailer_neu_percentage',
                             'trailer_tweet_neg',
                             'trailer_pos_percentage']]
    
    exploration.generate_heatmap_from_df(trailer_correl_df, trailer_correl_df.columns, "TEST")
    
    #positive tweet analysis
    weekend_tweet_cor_pos = get_correlation_for_tweets(senti_class = "positive")
    weekend_tweet_cor_pos_sig = weekend_tweet_cor_pos[weekend_tweet_cor_pos["stat_significance"] == True]
    weekend_tweet_cor_pos_sig_desc = weekend_tweet_cor_pos_sig.describe().drop(["count"])
    weekend_tweet_cor_pos_sig_desc_t = weekend_tweet_cor_pos_sig_desc.transpose()
    
    weekly_tweet_cor_pos = get_correlation_for_tweets(full_week=True, senti_class = "positive")
    weekly_tweet_cor_pos_sig = weekly_tweet_cor_pos[weekly_tweet_cor_pos["stat_significance"] == True]
    weekly_tweet_cor_pos_sig_desc = weekly_tweet_cor_pos_sig.describe().drop(["count"])
    weekly_tweet_cor_pos_sig_desc_t = weekly_tweet_cor_pos_sig_desc.transpose()
    
    
    #negative tweet analysis
    weekend_tweet_cor_neg = get_correlation_for_tweets(senti_class = "negative")
    weekend_tweet_cor_neg_sig = weekend_tweet_cor_neg[weekend_tweet_cor_neg["stat_significance"] == True]
    weekend_tweet_cor_neg_sig_desc = weekend_tweet_cor_neg_sig.describe().drop(["count"])
    weekend_tweet_cor_neg_sig_desc_t = weekend_tweet_cor_neg_sig_desc.transpose() 
        
    weekly_tweet_cor_neg = get_correlation_for_tweets(full_week=True, senti_class = "negative")  
    weekly_tweet_cor_neg_sig = weekly_tweet_cor_neg[weekly_tweet_cor_neg["stat_significance"] == True]
    weekly_tweet_cor_neg_sig_desc = weekly_tweet_cor_neg_sig.describe().drop(["count"])
    weekly_tweet_cor_neg_sig_desc_t = weekly_tweet_cor_neg_sig_desc.transpose()
    
    
    #neutral tweet analysis
    weekend_tweet_cor_neu = get_correlation_for_tweets(senti_class = "neutral")
    weekend_tweet_cor_neu_sig = weekend_tweet_cor_neu[weekend_tweet_cor_neu["stat_significance"] == True]
    weekend_tweet_cor_neu_sig_desc = weekend_tweet_cor_neu_sig.describe().drop(["count"])
    weekend_tweet_cor_neu_sig_desc_t = weekend_tweet_cor_neu_sig_desc.transpose()  
    
    weekly_tweet_cor_neu = get_correlation_for_tweets(full_week=True, senti_class = "neutral") 
    weekly_tweet_cor_neu_sig = weekly_tweet_cor_neu[weekly_tweet_cor_neu["stat_significance"] == True]
    weekly_tweet_cor_neu_sig_desc = weekly_tweet_cor_neu_sig.describe().drop(["count"])
    weekly_tweet_cor_neu_sig_desc_t = weekly_tweet_cor_neu_sig_desc.transpose()
        
    
    results = {"movies_df" : movies_df, 
               "class_sent_df" : class_sent_df,
               "summary_df_t" : summary_df_t,
               "correl_df" : correl_df,
               "weekend_tweet_cor_pos" : weekend_tweet_cor_pos,
               "weekend_tweet_cor_pos_sig" : weekend_tweet_cor_pos_sig,
               "weekend_tweet_cor_pos_sig_desc_t" : weekend_tweet_cor_pos_sig_desc_t,
               "weekly_tweet_cor_pos" : weekly_tweet_cor_pos,
               "weekly_tweet_cor_pos_sig" : weekly_tweet_cor_pos_sig,
               "weekly_tweet_cor_pos_sig_desc_t" : weekly_tweet_cor_pos_sig_desc_t,
               "weekend_tweet_cor_neg" : weekend_tweet_cor_neg,
               "weekend_tweet_cor_neg_sig" : weekend_tweet_cor_neg_sig,
               "weekend_tweet_cor_neg_sig_desc_t" : weekend_tweet_cor_neg_sig_desc_t,
               "weekly_tweet_cor_neg" : weekly_tweet_cor_neg,
               "weekly_tweet_cor_neg_sig" : weekly_tweet_cor_neg_sig,
               "weekly_tweet_cor_neg_sig_desc_t" : weekly_tweet_cor_neg_sig_desc_t,
               "weekend_tweet_cor_neu" : weekend_tweet_cor_neu,
               "weekend_tweet_cor_neu_sig" : weekend_tweet_cor_neu_sig,
               "weekend_tweet_cor_neu_desc_t" : weekend_tweet_cor_neu_sig_desc_t,
               "weekly_tweet_cor_neu" : weekly_tweet_cor_neu,
               "weekly_tweet_cor_neu_sig" : weekly_tweet_cor_neu_sig,
               "weekly_tweet_cor_neu_sig_desc_t" : weekly_tweet_cor_neu_sig_desc_t}
    
    return results

def analyse_sentiment_special():
    plot_tweets = pd.DataFrame()
    trailer_tweets = pd.DataFrame()
    run_up_tweets = pd.DataFrame()
    week1_tweets = pd.DataFrame()
    week2_tweets = pd.DataFrame()
    
    avengers = movie_helper.get_movie_by_id(121)
    avengers_grped_tweets = avengers.get_grouped_tweets(critical_period=True, group_size=7)
    avengers_grped_tweets["title"] = avengers.title
    
    avengers_run_up = avengers_grped_tweets[avengers_grped_tweets["group"] == "Run Up Week"]
    avengers_run_up["day"] = avengers_run_up.apply(lambda row: "Day {0}".format((row["date"] - avengers_run_up["date"].min()).days + 1), axis=1)
 
    avengers_week_1 = avengers_grped_tweets[avengers_grped_tweets["group"] == "Release Week 1"]
    avengers_week_1["day"] = avengers_week_1.apply(lambda row: "Day {0}".format((row["date"] - avengers_week_1["date"].min()).days + 1), axis=1)
   
    avengers_week_2 = avengers_grped_tweets[avengers_grped_tweets["group"] == "Release Week 2"]
    avengers_week_2["day"] = avengers_week_2.apply(lambda row: "Day {0}".format((row["date"] - avengers_week_2["date"].min()).days + 1), axis=1)     

    #do trailer tweets
    avengers_trailer_tweets = movie_helper.get_trailer_tweets(121, most_tweeted=True)
    print("Avengers Trailer Tweets {0}".format(avengers_trailer_tweets.shape[0]))
    avengers_trailer_tweets["title"] = avengers.title
    avengers_trailer_tweets["date"] = pd.to_datetime(avengers_trailer_tweets["created_at"].dt.date, errors="coerce")
    avengers_trailer_tweets["day"] = avengers_trailer_tweets.apply(lambda row: "Day {0}".format((row["date"] - avengers_trailer_tweets["date"].min()).days + 1), axis=1)
    avengers_trailer_tweets["group"] = "Trailer Release"
    

    plot_tweets = plot_tweets.append(avengers_trailer_tweets[["title", "compound_scr", "group"]])
    plot_tweets = plot_tweets.append(avengers_grped_tweets[["title", "compound_scr", "group"]])
    trailer_tweets = trailer_tweets.append(avengers_trailer_tweets[["title", "compound_scr", "day"]])    
    run_up_tweets = run_up_tweets.append(avengers_run_up[["title", "compound_scr", "day"]])
    week1_tweets = week1_tweets.append(avengers_week_1[["title", "compound_scr", "day"]])
    week2_tweets = week2_tweets.append(avengers_week_2[["title", "compound_scr", "day"]])
    
    #CATS
    cats = movie_helper.get_movie_by_id(32)
    cats_grped_tweets = cats.get_grouped_tweets(critical_period=True, group_size=7)
    cats_grped_tweets["title"] = cats.title
    
    cats_run_up = cats_grped_tweets[cats_grped_tweets["group"] == "Run Up Week"]
    cats_run_up["day"] = cats_run_up.apply(lambda row: "Day {0}".format((row["date"] - cats_run_up["date"].min()).days + 1), axis=1)
 
    cats_week_1 = cats_grped_tweets[cats_grped_tweets["group"] == "Release Week 1"]
    cats_week_1["day"] = cats_week_1.apply(lambda row: "Day {0}".format((row["date"] - cats_week_1["date"].min()).days + 1), axis=1)
   
    cats_week_2 = cats_grped_tweets[cats_grped_tweets["group"] == "Release Week 2"]
    cats_week_2["day"] = cats_week_2.apply(lambda row: "Day {0}".format((row["date"] - cats_week_2["date"].min()).days + 1), axis=1)   
  
    #do trailer tweets
    cats_trailer_tweets = movie_helper.get_trailer_tweets(32, most_tweeted=True)
    print("Cats Trailer Tweets {0}".format(cats_trailer_tweets.shape[0]))
    cats_trailer_tweets["title"] = cats.title
    cats_trailer_tweets["date"] = pd.to_datetime(cats_trailer_tweets["created_at"].dt.date, errors="coerce")
    cats_trailer_tweets["day"] = cats_trailer_tweets.apply(lambda row: "Day {0}".format((row["date"] - cats_trailer_tweets["date"].min()).days + 1), axis=1)
    cats_trailer_tweets["group"] = "Trailer Release"   

    plot_tweets = plot_tweets.append(cats_trailer_tweets[["title", "compound_scr", "group"]])
    plot_tweets = plot_tweets.append(cats_grped_tweets[["title", "compound_scr", "group"]])
    trailer_tweets = trailer_tweets.append(cats_trailer_tweets[["title", "compound_scr", "day"]])    
    run_up_tweets = run_up_tweets.append(cats_run_up[["title", "compound_scr", "day"]])
    week1_tweets = week1_tweets.append(cats_week_1[["title", "compound_scr", "day"]])
    week2_tweets = week2_tweets.append(cats_week_2[["title", "compound_scr", "day"]])
    
    #GREEN BOOK
    green_book = movie_helper.get_movie_by_id(142)
    green_book_grped_tweets = green_book.get_grouped_tweets(critical_period=True, group_size=7)
    green_book_grped_tweets["title"] = green_book.title
    
    green_book_run_up = green_book_grped_tweets[green_book_grped_tweets["group"] == "Run Up Week"]
    green_book_run_up["day"] = green_book_run_up.apply(lambda row: "Day {0}".format((row["date"] - green_book_run_up["date"].min()).days + 1), axis=1)
 
    green_book_week_1 = green_book_grped_tweets[green_book_grped_tweets["group"] == "Release Week 1"]
    green_book_week_1["day"] = green_book_week_1.apply(lambda row: "Day {0}".format((row["date"] - green_book_week_1["date"].min()).days + 1), axis=1)
   
    green_book_week_2 = green_book_grped_tweets[green_book_grped_tweets["group"] == "Release Week 2"]
    green_book_week_2["day"] = green_book_week_2.apply(lambda row: "Day {0}".format((row["date"] - green_book_week_2["date"].min()).days + 1), axis=1)     
    
    #do trailer tweets
    # green_book_trailer_tweets = movie_helper.get_trailer_tweets(142, most_tweeted=True)
    # green_book_trailer_tweets["title"] = green_book.title
    # green_book_trailer_tweets["date"] = pd.to_datetime(green_book_trailer_tweets["created_at"].dt.date, errors="coerce")
    # green_book_trailer_tweets["day"] = green_book_trailer_tweets.apply(lambda row: "Day {0}".format((row["date"] - green_book_trailer_tweets["date"].min()).days + 1), axis=1)
    # green_book_trailer_tweets["group"] = "Best Trailer"       
    
    plot_tweets = plot_tweets.append(green_book_grped_tweets[["title", "compound_scr", "group"]])
    #plot_tweets = plot_tweets.append(green_book_trailer_tweets[["title", "compound_scr", "group"]])
   # trailer_tweets = trailer_tweets.append(green_book_trailer_tweets[["title", "compound_scr", "day"]])   
    run_up_tweets = run_up_tweets.append(green_book_run_up[["title", "compound_scr", "day"]])
    week1_tweets = week1_tweets.append(green_book_week_1[["title", "compound_scr", "day"]])
    week2_tweets = week2_tweets.append(green_book_week_2[["title", "compound_scr", "day"]])    
        
    #plt.figure(figsize=(20,5))
    g = sns.catplot(x="day", y="compound_scr", data=run_up_tweets, hue="title", kind="boxen", legend_out = False, height=5, aspect=1.5)  
    
    fig = g.fig
    g.set_ylabels("Compound Score")
    g.set_xlabels("Days")
    g.set_xticklabels(rotation=40, ha="right")
    fig.subplots_adjust(top=0.9)
    fig.suptitle("Run Up Week Sentiment", fontsize=16)
    plt.show()
    
    g = sns.catplot(x="day", y="compound_scr", data=week1_tweets, hue="title", kind="boxen", legend_out = False, height=5, aspect=1.5)  
    
    fig = g.fig
    g.set_ylabels("Compound Score")
    g.set_xlabels("Days")
    g.set_xticklabels(rotation=40, ha="right")
    fig.subplots_adjust(top=0.9)
    fig.suptitle("Release Week 1 Sentiment", fontsize=16)
    plt.show()
    
    g = sns.catplot(x="day", y="compound_scr", data=week2_tweets, hue="title", kind="boxen", legend_out = False, height=5, aspect=1.5)  
    
    fig = g.fig
    g.set_ylabels("Tweet Sentiment")
    g.set_xlabels("Days")
    g.set_xticklabels(rotation=40, ha="right")
    fig.subplots_adjust(top=0.9)
    fig.suptitle("Release Week 2 Sentiment", fontsize=16)
    plt.show()
    
    g = sns.catplot(x="group", y="compound_scr", data=plot_tweets, hue="title", kind="boxen", legend_out = False, height=5, aspect=1.5)  
    
    fig = g.fig
    g.set_ylabels("Tweet Sentiment")
    g.set_xlabels("Date")
    g.set_xticklabels(rotation=40, ha="right")
    fig.subplots_adjust(top=0.9)
    fig.suptitle("Critical Period Sentiment", fontsize=16)
    plt.show()
        
    g = sns.catplot(x="day", y="compound_scr", data=trailer_tweets, hue="title", kind="boxen", legend_out = False, height=5, aspect=1.5)  
    
    fig = g.fig
    g.set_ylabels("Tweet Sentiment")
    g.set_xlabels("Date")
    g.set_xticklabels(rotation=40, ha="right")
    fig.subplots_adjust(top=0.9)
    fig.suptitle("Trailer Sentiment", fontsize=16)
    plt.show()
    

def spatial_exploration():
    #plot normalized and unormalized cholopleth of movie tweets
    exploration.plot_movie_tweets_map()
    exploration.plot_movie_tweets_map(True)
    
    #get bar charts to back up this 
    spatial.plot_region_tweets_bar()
    spatial.plot_region_tweets_bar(True)
    
    #show unnormalized kde
    spatial.plot_movie_tweets_kde()
    
    #show expectation 
    spatial.plot_chi_sqrd_surface()
    
def spatial_regional_best(critical_period=True):
    #all moivies 
    movies_df = movie_helper.get_movies_df()
    
    #get most tweeted movie per region
    most_per_region = spatial.get_most_popular_movie_per_region(ignore_list=[], critical_period=critical_period)   
    #get most postivie tweets per region
    most_pos_per_region = spatial.get_most_popular_movie_per_region(senti_class="positive", ignore_list=[], critical_period=critical_period)      
    #get most negative per reigon
    most_neg_per_region = spatial.get_most_popular_movie_per_region(senti_class="negative", ignore_list=[], critical_period=critical_period)      
 
    exclude_values = [{"class_col" : None, "class_vals" : [], "reason" : "all movies"},
                      {"class_col" : "profit_class", "class_vals" : ["> $700m (BlockBuster)"], "reason" : "no blockbuster (profit)"},
                      {"class_col" : "profit_class", "class_vals" : ['< $0 (Flop)', '$0 < $90m', '$90m < $235m', '$235m < $700m'], "reason" : "only blockbuster (profit)"},
                      {"class_col" : "return_class", "class_vals" : ["> 1000% (BlockBuster)"], "reason" : "no blockbuster (return)"},
                      {"class_col" : "return_class", "class_vals" : ['< %0 (Flop)', '0% - 290%', '100% - 540%', '540% - 1000%'], "reason" : "only blockbuster (return)"},
                      {"class_col" : "budget_class", "class_vals" : ["> 185m (Big)"], "reason" : "no big budget"},
                      {"class_col" : "budget_class", "class_vals" : ['< $10m (Small)', '$10m < $40m', '$40m < $100m', '$100m < $185m'], "reason" : "only big budget"},
                      {"class_col" : "uk_gross_class", "class_vals" : ["> $50m (Big)"], "reason" : "no top uk takings"},
                      {"class_col" : "uk_gross_class", "class_vals" : ['< $1m (Small)', '$1m < $8m', '$8m < $20m', '$20m < $50m'], "reason" : "only top uk takings"},
                      {"class_col" : "uk_percentage_class", "class_vals" : ["> 12%"], "reason" : "no top uk (percentage)"},
                      {"class_col" : "uk_percentage_class", "class_vals" : ['0% - 1%', '1% - 4%', '4% - 6%', '6% - 12%'], "reason" : "only top uk (percentage)"}]
                      
 
    exclude_vals_df = pd.DataFrame(exclude_values)
    results_df = pd.DataFrame()
    
    for index, row in exclude_vals_df.iterrows(): 
        ignore_list = [28]
        
        if not row["class_col"] == None:
            ignore_df = movies_df[movies_df[row["class_col"]].isin(row["class_vals"])]
            ignore_list.extend(list(ignore_df["movieId"]))
        
        most_all = exploration.get_most_popular_movie_per_region(ignore_list=ignore_list, critical_period=critical_period)   
        most_all["senti_class"] = "All"
        most_all["reason"] = row["reason"]
        
        spatial.plot_favourites_map(most_all, annotate_col="tweet_count", title = "Most Tweeted ({0})".format(row["reason"]))
        results_df = results_df.append(most_all)
        
        #do positive tweets only
        most_pos = exploration.get_most_popular_movie_per_region(senti_class = "positive", ignore_list=ignore_list, critical_period=critical_period)   
        most_pos["senti_class"] = "positive"
        most_pos["reason"] = row["reason"]
        
        spatial.plot_favourites_map(most_pos, annotate_col="tweet_count", title = "Most Positive Tweets ({0})".format(row["reason"]))
        results_df = results_df.append(most_pos)
        
        #do positive tweets percentage
        most_pos_percentage = exploration.get_most_popular_movie_per_region(senti_class = "positive", ignore_list=ignore_list, senti_percentage=True, critical_period=critical_period)   
        most_pos_percentage["senti_class"] = "positive (Percentage)"
        most_pos_percentage["percentage_string"] = most_pos_percentage.apply(lambda row: "{0}%".format(round(row["senti_percentage"], 2)), axis=1)
        most_pos_percentage["reason"] = row["reason"]
        
        spatial.plot_favourites_map(most_pos_percentage, annotate_col="percentage_string", title = "Highest Rate of Positive Tweets ({0})".format(row["reason"]))
        results_df = results_df.append(most_pos_percentage)
                
        #do negative tweets only
        most_neg = exploration.get_most_popular_movie_per_region(senti_class = "negative", ignore_list=ignore_list, critical_period=critical_period)   
        most_neg["senti_class"] = "negative"
        most_neg["reason"] = row["reason"]
        
        exploration.plot_favourites_map(most_neg, annotate_col="tweet_count", title = "Most Negative Tweets ({0})".format(row["reason"]))
        results_df = results_df.append(most_neg)
        
        #do negative tweets percentage
        most_neg_percentage = exploration.get_most_popular_movie_per_region(senti_class = "negative", ignore_list=ignore_list, senti_percentage=True, critical_period=critical_period)   
        most_neg_percentage["percentage_string"] = most_neg_percentage.apply(lambda row: "{0}%".format(round(row["senti_percentage"], 2)), axis=1)
        most_neg_percentage["senti_class"] = "negative (Percentage)"
        most_neg_percentage["reason"] = row["reason"]
        
        spatial.plot_favourites_map(most_neg_percentage, annotate_col="percentage_string", title = "Highest Rate of Negative Tweets ({0})".format(row["reason"]))
        results_df = results_df.append(most_neg_percentage)
        

    return results_df[["region", "unit_id", "title", "movieid", "tweet_count", "reason", "senti_class", "senti_percentage"]]


def spatial_analyse_interesting_cases():
    special_cases_df = get_interesting_cases()
    unique_df = special_cases_df.drop_duplicates(subset="movieId", inplace=False, keep="first")
    
    unique_df = unique_df[(unique_df["movieId"] == 121) | (unique_df["movieId"] == 32) | (unique_df["movieId"] == 142)] 
    
    for index, row in unique_df.iterrows():
        #plot movie map and bar general and critical 
      #  exploration.plot_region_tweets_bar(movieId=row["movieId"], normalize=False)
      #  exploration.plot_region_tweets_bar(movieId=row["movieId"], normalize=True)
        spatial.plot_region_tweets_bar(movieId=row["movieId"], normalize=False, start_date=row["critical_start"], end_date=row["critical_end"], critical_period=True)
        spatial.plot_region_tweets_bar(movieId=row["movieId"], normalize=True, start_date=row["critical_start"], end_date=row["critical_end"], critical_period=True)
        
     #   spatial.plot_movie_tweets_map(movieId=row["movieId"], normalize=False)
     #   spatial.plot_movie_tweets_map(movieId=row["movieId"], normalize=True)
        spatial.plot_movie_tweets_map(movieId=row["movieId"], normalize=False, start_date=row["critical_start"], end_date=row["critical_end"], critical_period=True)
        spatial.plot_movie_tweets_map(movieId=row["movieId"], normalize=True, start_date=row["critical_start"], end_date=row["critical_end"], critical_period=True)
        
     #   spatial.plot_chi_sqrd_surface(movieId=row["movieId"])
        spatial.plot_chi_sqrd_surface(movieId=row["movieId"], start_date=row["critical_start"], end_date=row["critical_end"], critical_period=True)

    
    