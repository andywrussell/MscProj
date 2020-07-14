#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 09:33:06 2020

@author: andy
"""

from tqdm import tqdm
import pandas as pd
import sys
import re
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Entities')
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Utils')

from movie import Movie
import database_helper
import tweet_helper
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from datetime import timedelta
import scipy

def get_movies_df():
    movies_df = database_helper.select_query("movies", {"investigate" : "1"})
    movies_df = movies_df.sort_values(by=['movieId'])   
    return movies_df

def get_movies():
    #movies_df = database_helper.select_query("movies", { "enabled" : "1" })
    movies_df = database_helper.select_query("movies", {"investigate" : "1"})
    movies_df = movies_df.sort_values(by=['movieId'])  
    return gen_movies(movies_df)

def gen_movies(movies_df):
    movies = []
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            movie = Movie(row)
            movies.append(movie)
            pbar.update(1)
    return movies

def get_movie_by_id(movieId): 
    movies_df = database_helper.select_query("movies", { "movieId" : int(movieId) })
    if (not movies_df.empty):
        return Movie(movies_df.iloc[0])
    
    return None

def get_movie_by_title(title):
    movies_df = database_helper.select_query("movies", { "title" : title })
    if (not movies_df.empty):
        return Movie(movies_df.iloc[0])
    
    return None
    
def set_total_revenue_for_movies():
    movies = get_movies();
    with tqdm(total=len(movies)) as pbar:
        for movie in movies:
            total_rev = movie.box_office_df.iloc[movie.box_office_df['weeksOnRelease'].idxmax()]['grossToDate']
            update_params = { "totalRevenue" : total_rev }
            select_params = { "movieId" : movie.movieId }
            database_helper.update_data("movies", update_params = update_params, select_params = select_params)
            pbar.update(1)
            
def get_top_by_column(column, max_movies = 20):
    sql = """SELECT * FROM public.movies 
             WHERE "investigate" = '1'
             ORDER BY "{0}" DESC LIMIT {1}""".format(column, max_movies)

    return database_helper.get_data(sql)

def get_top_movies_by_column(column, max_movies = 20):
    top_df = get_top_by_column(column, max_movies)
    return gen_movies(top_df) 

def get_lowest_by_column(column, max_movies = 20):
    sql = """SELECT * FROM public.movies 
             WHERE "investigate" = '1'
             ORDER BY "{0}" ASC LIMIT {1}""".format(column, max_movies)
             
    return database_helper.get_data(sql)  

def get_lowest_movies_by_column(column, max_movies = 20):
    bottom_df = get_lowest_by_column(column, max_movies)
    return gen_movies(bottom_df)    

def count_tweets(movieId, start_date = None, end_date = None):
    sql = """
          SELECT "movieid", COUNT(*) 
          FROM movie_tweets2019 
          WHERE "movieid" = {0}""".format(movieId)   
          
    if not start_date == None:
        sql += """ AND "created_at" >= '{0}'""".format(start_date)
        
    if not end_date == None:
        sql += """ AND "created_at" <= '{0}'""".format(end_date)
          
    sql += """ GROUP BY "movieid" """

        
    tweet_count = database_helper.get_data(sql)
    return tweet_count

def categorize_by_gross_profit():
    movies_df = get_movies_df()
    
    #calculate gross profit based on budget and worldwide gross
    movies_df["worldwide_gross_usd_norm"] = movies_df['worldwide_gross_usd'].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["budget_usd_norm"] = movies_df['budget_usd'].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["gross_profit_usd_norm"] = movies_df["worldwide_gross_usd_norm"] - movies_df["budget_usd_norm"]
    movies_df["gross_profit_usd"] = movies_df["worldwide_gross_usd"].replace('[\£,]', '', regex=True).astype(float) - movies_df["budget_usd"].replace('[\£,]', '', regex=True).astype(float)
    
    custom_bucket_array =[-50, 0, 50, 150, 300, 2500]
    bucket_labels = ['< $0 (Flop)', '$0 < $50m', '$50m < $150m', '$150m < $300m', ' > $300m (BlockBuster)' ]
    
    movies_df['class'] = pd.cut(movies_df['gross_profit_usd_norm'], custom_bucket_array,labels= bucket_labels)
    
    for index, row in movies_df.iterrows(): 
            updates = { "gross_profit_usd" : row["gross_profit_usd"],
                    "profit_class" : row["class"]
                    }
            selects = {"movieId" : row["movieId"]}
            database_helper.update_data("movies", update_params = updates, select_params = selects)
    
    return movies_df

def calculate_percentage_profit():
    movies_df = get_movies_df()
    movies_df["gross_profit_norm"] = movies_df["gross_profit_usd"].replace('[\£,]', '', regex=True).astype(float)
    movies_df["budget_norm"] = movies_df["budget_usd"].replace('[\£,]', '', regex=True).astype(float)
    movies_df["return_percentage"] = (movies_df["gross_profit_norm"] / movies_df["budget_norm"]) * 100
    
    for index, row in movies_df.iterrows(): 
        updates = { "return_percentage" : row["return_percentage"] }
        selects = {"movieId" : row["movieId"]}
        database_helper.update_data("movies", update_params = updates, select_params = selects)
    
    return movies_df


def categorize_by_return_percentage():
    movies_df = get_movies_df()
    
    custom_bucket_array =[-100, 0, 100, 400, 1000, 2000]
    bucket_labels = ['< %0 (Flop)', '%0-100%', '%100-%400', '%400-%1000', '> %1000 (BlockBuster)']
    movies_df['class'] = pd.cut(movies_df['return_percentage'], custom_bucket_array,labels= bucket_labels)
    
    for index, row in movies_df.iterrows(): 
            updates = { "return_class" : row["class"] }
            selects = {"movieId" : row["movieId"]}
            database_helper.update_data("movies", update_params = updates, select_params = selects)
    
    return movies_df

def categorize_by_uk_percentage():
    movies_df = get_movies_df()
    
    custom_bucket_array =[0, 2, 4, 6, 12, 20]
    bucket_labels = ['0% - 2%', '2% - 4%', '4% - 6%', '6% - 12%', '> 12%']
    movies_df['class'] = pd.cut(movies_df['uk_percentage'], custom_bucket_array,labels= bucket_labels)
    
    for index, row in movies_df.iterrows(): 
            updates = { "uk_percentage_class" : row["class"] }
            selects = {"movieId" : row["movieId"]}
            database_helper.update_data("movies", update_params = updates, select_params = selects)
    
    return movies_df

  
def calculate_uk_percentage_gross():
    movies_df = get_movies_df()
    movies_df["worldwide_norm"] = movies_df["worldwide_gross_usd"].replace('[\£,]', '', regex=True).astype(float)
    movies_df["uk_takings_norm"] = movies_df["uk_gross_usd"].replace('[\£,]', '', regex=True).astype(float)
    movies_df["uk_percentage"] = (movies_df["uk_takings_norm"] / movies_df["worldwide_norm"]) * 100
    
    for index, row in movies_df.iterrows(): 
        updates = { "uk_percentage" : row["uk_percentage"] }
        selects = {"movieId" : row["movieId"]}
        database_helper.update_data("movies", update_params = updates, select_params = selects)
    
    return movies_df
    

def get_movie_genres():
    movies_df = get_movies_df()
    movies_df["genres_list"] = movies_df["genres"].apply(lambda x: x.split(',') if x != None else [])
    genre_list = movies_df["genres_list"].to_list()
    
    genre_list = list(set([item for sublist in genre_list for item in sublist]))
    
    return genre_list


def get_movie_genre_counts():
    movies_df = get_movies_df()
    genre_list = get_movie_genres()
    
    genre_df = pd.DataFrame(columns=["genre", "count"])
    
    counts = []
    for genre in genre_list:
        row_s = movies_df.apply(lambda x: True if genre in x["genres"] else False, axis=1)
        counts.append(len(row_s[row_s == True].index))
     
    genre_df["genre"] = genre_list
    genre_df["count"] = counts
    
    return genre_df

def get_genre_tweet_counts():
    genre_list = get_movie_genres()
    counts = []
    
    for genre in genre_list:
        #get all movies in this genre
        genre_movies = database_helper.select_movies_by_genre(genre)

        tweet_count = 0
        for index, row in genre_movies.iterrows():
            tweet_count += int(count_tweets(row["movieId"])['count'])

            
        counts.append(tweet_count)
        
    genre_df = pd.DataFrame(columns=["genre", "count"])
    genre_df["genre"] = genre_list
    genre_df["count"] = counts
    
    return genre_df

def get_genre_tweet_sentiments():
    genre_list = get_movie_genres()
    
    output_df = pd.DataFrame(columns=['senti_class', 'counts', 'genre'])
    for genre in genre_list:
        genre_movies = database_helper.select_movies_by_genre(genre)
        
        #do the first movie 
        first_tweets = database_helper.select_geo_tweets(genre_movies.iloc[0]['movieId'])
        class_freq = first_tweets.groupby('senti_class').size().reset_index(name='counts')
        
        for index, row in genre_movies.iterrows():
            if index > 0:
                tweets = database_helper.select_geo_tweets(row["movieId"])
                my_class_freq = tweets.groupby('senti_class').size().reset_index(name='counts')
                class_freq['counts'] += my_class_freq['counts']
    
        class_freq['genre'] = genre
        output_df = output_df.append(class_freq)
        
    return output_df

def get_genre_revenues():
    genre_list = get_movie_genres()
                
    genre_revenues = []
    for genre in genre_list:
        genre_movies = database_helper.select_movies_by_genre(genre)  
        genre_movies["profit_mil"] = genre_movies["gross_profit_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
        genre_total = genre_movies["profit_mil"].sum()
        
        genre_revenues.append(genre_total)
        
    output_df = pd.DataFrame(columns=["genre", "profit_mil"])
    output_df["genre"] = genre_list
    output_df["profit_mil"] = genre_revenues
    
    return output_df
        
        
def get_genre_movie_class_counts():
    genre_list = get_movie_genres()
      
    output_df = pd.DataFrame(columns=["profit_class", "genre", "counts"])
      
    for genre in genre_list: 
        genre_movies = database_helper.select_movies_by_genre(genre) 
        class_freq = genre_movies.groupby('profit_class').size().reset_index(name="counts")
        class_freq["genre"] = genre
        
        output_df = output_df.append(class_freq)
        
    return output_df


def get_correlation_matrix():
    #based on https://seaborn.pydata.org/examples/many_pairwise_correlations.html
    movies_df = get_movies_df()
    
    #get tweet counts for each movies 
    movies_df["tweet_count"] = movies_df.apply(lambda row: count_tweets(row.movieId)['count'], axis = 1)
    
    
    correlation_subset = movies_df[['budget_usd', 
                                    'uk_gross_usd', 
                                    'domestic_gross_usd', 
                                    'worldwide_gross_usd', 
                                    'international_gross_usd', 
                                    'gross_profit_usd', 
                                    'return_percentage', 
                                    'uk_percentage', 
                                    'tweet_count',
                                    'total_release_weeks',
                                    'first_run_weeks']]
    
    #covert money to float ($mil)
    correlation_subset["budget_usd"] = correlation_subset["budget_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    correlation_subset["uk_gross_usd"] = correlation_subset["domestic_gross_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    correlation_subset["domestic_gross_usd"] = correlation_subset["domestic_gross_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    correlation_subset["worldwide_gross_usd"] = correlation_subset["worldwide_gross_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    correlation_subset["international_gross_usd"] = correlation_subset["international_gross_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    correlation_subset["gross_profit_usd"] = correlation_subset["gross_profit_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    

    #computer the correlation 
    corr = correlation_subset.corr()
    
    # Generate a mask for the upper triangle
    mask = np.triu(np.ones_like(corr, dtype=np.bool))
    
    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 9))
    
    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(220, 10, as_cmap=True)
    
    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(corr, mask=mask, cmap=cmap, vmax=.3, center=0, 
                square=True, linewidths=.5, cbar_kws={"shrink": .5}) 
    
    
def get_movies_with_run_gaps():
    movies_df = get_movies_df()
    
    gap_movies_df = pd.DataFrame()
    for index, row in movies_df.iterrows():
        mojo_box_office_df = database_helper.select_query("weekend_box_office_mojo", {"movieid" : row['movieId']})
        
        if (check_mojo_for_gaps(mojo_box_office_df)):
            gap_movies_df = gap_movies_df.append(row)
            
    return gap_movies_df
        
def check_mojo_for_gaps(df):
    df = df.sort_values(by='weeks_on_release', ascending=True)
    
    prev_weeks = df.iloc[0]['weeks_on_release']
    for index, row in df.iterrows():
        if index > 0:
            cur_weeks = row['weeks_on_release']
            if (cur_weeks - prev_weeks) > 1:
                return True
            
            prev_weeks = cur_weeks
            
    return False

def get_end_weekend_for_first_run(df):
    df = df.sort_values(by='weeks_on_release', ascending=True)
    
    prev_weeks = df.iloc[0]['weeks_on_release']
    prev_end = df.iloc[0]['end_date']
    
    end_weekend = df.iloc[df['weeks_on_release'].idxmax()].end_date
    
    for index, row in df.iterrows():
        if index > 0:
            cur_weeks = row['weeks_on_release']
            cur_end = row['end_date']
            if (cur_weeks - prev_weeks) > 1:
                return prev_end
            
            prev_weeks = cur_weeks
            prev_end = cur_end
            
    return end_weekend

def get_movie_run_info():
    movies_df = get_movies_df()
    
    dict_lst = []
    for index, row in movies_df.iterrows():
        mojo_box_office_df = database_helper.select_query("weekend_box_office_mojo", {"movieid" : row['movieId']})
        
        end_weekend = mojo_box_office_df.iloc[mojo_box_office_df['weeks_on_release'].idxmax()].end_date
        end_weekend_datetime = datetime.combine((end_weekend + timedelta(days=14)), datetime.max.time())
        
        total_weekends = mojo_box_office_df.shape[0]
        total_release_weeks = mojo_box_office_df.iloc[mojo_box_office_df['weeks_on_release'].idxmax()].weeks_on_release
        
        
        #some films have gaps in their running
        first_run_end = get_end_weekend_for_first_run(mojo_box_office_df)
        first_run_datetime = datetime.combine((first_run_end + timedelta(days=14)), datetime.max.time())
        
        first_end_index = mojo_box_office_df.index[mojo_box_office_df['end_date'] == first_run_end].tolist()[0]
        first_run_weeks = mojo_box_office_df.iloc[first_end_index]['weeks_on_release']   
        
        my_dict = { "movieId" : int(row["movieId"]), 
                   "end_weekend" : end_weekend, 
                   "total_weekends" : total_weekends, 
                   "total_release_weeks" : total_release_weeks, 
                   "first_run_end" : first_run_end,
                   "first_run_weeks" : first_run_weeks}
        
        dict_lst.append(my_dict)
    
    return pd.DataFrame(dict_lst)

def check_run_dates_tweets():
    movies_df = get_movies_df()
    max_tweet_date = tweet_helper.get_max_date().date()
    
    
    problem_films = pd.DataFrame()
    for index, row in movies_df.iterrows():
        if row['first_run_end'] >= max_tweet_date:
            problem_films = problem_films.append(row)
            
    return problem_films

def get_run_positive_increase():
    movies_df = get_movies_df()
    
    positive_changes = pd.DataFrame()
    for index, row in movies_df.iterrows():
        mojo_box_office_df = database_helper.select_query("weekend_box_office_mojo", {"movieid" : row['movieId']})
        if (mojo_box_office_df['percentage_change'] > 0).any() :
            positive_changes = positive_changes.append(row)
            
    return positive_changes

def get_highest_mojo_rank():
    movies_df = get_movies_df()
    
    rank_list = []
    for index, row in movies_df.iterrows():
        mojo_box_office_df = database_helper.select_query("weekend_box_office_mojo", {"movieid" : row['movieId']})
        
        best_rank = mojo_box_office_df["rank"].min()
        
        best_rows = mojo_box_office_df[mojo_box_office_df['rank'] == best_rank]
        weekends_at_rank = best_rows.shape[0]
        
        top_3_rows = mojo_box_office_df[mojo_box_office_df['rank'] <= 3]
        top_3_weekends = top_3_rows.shape[0]
        
        top_5_rows = mojo_box_office_df[mojo_box_office_df['rank'] <= 5]
        top_5_weekends = top_5_rows.shape[0]
        
        top_10_rows = mojo_box_office_df[mojo_box_office_df['rank'] <= 10]
        top_10_weekends = top_10_rows.shape[0]
        
        top_15_rows = mojo_box_office_df[mojo_box_office_df['rank'] <= 15]
        top_15_weekends = top_15_rows.shape[0]
        
        rank_list.append({"movieId" : row["movieId"], 
                          "best_rank" : best_rank, 
                          'weekends_at_best_rank' : weekends_at_rank,
                          'weekends_in_top_3' : top_3_weekends,
                          'weekends_in_top_5' : top_5_weekends,
                          'weekends_in_top_10' : top_10_weekends,
                          'weekends_in_top_15' : top_15_weekends})
        
        
        
    return pd.DataFrame(rank_list)


def get_movies_df_with_opening_weekend():
    movies_df = get_movies_df()
    movies_df["opening_weekend_takings"] = movies_df.apply(lambda row: database_helper.select_query("weekend_box_office_mojo", {"movieid" : row['movieId']}).iloc[0]['weekend_gross_usd'], axis=1)
    
    
    
    tweets_prior_to_opening = [] 
    opening_weekend_tweets = []
    
    for index, row in movies_df.iterrows():
        mojo_df = database_helper.select_query("weekend_box_office_mojo", {"movieid" : row['movieId']})
        
        opening_start = mojo_df.iloc[0]['start_date']
        opening_end = mojo_df.iloc[0]['end_date']
        
        prev_week = datetime.combine((opening_start  - timedelta(days=7)), datetime.min.time())
        prev_end = datetime.combine((opening_start - timedelta(days=1)), datetime.max.time())


        run_up_count = count_tweets(row['movieId'], prev_week, prev_end)
        if run_up_count.empty:
            run_up_count = 0
        else: 
            run_up_count = run_up_count.iloc[0]['count']
        
        opening_start = datetime.combine(opening_start, datetime.min.time())
        opening_end = datetime.combine(opening_end, datetime.max.time())
        
        opening_count = count_tweets(row['movieId'], opening_start, opening_end)
        if opening_count.empty:
            opening_count = 0
        else: 
            opening_count = opening_count.iloc[0]['count'] 

        tweets_prior_to_opening.append(run_up_count)
        opening_weekend_tweets.append(opening_count)
        
    movies_df['run_up_tweets'] = tweets_prior_to_opening
    movies_df['opening_tweets'] = opening_weekend_tweets
    
    return movies_df


def get_df_and_col_list_for_correlation():
    movies_df = get_movies_df_with_opening_weekend()
    movies_df["tweet_count"] = movies_df.apply(lambda row: count_tweets(row.movieId)['count'], axis = 1)
    movies_df["critical_period_tweet_count"] = movies_df.apply(lambda row: count_tweets(row["movieId"], row["critical_start"], row["critical_end"])['count'], axis = 1)
    movies_df["budget_usd"] = movies_df["budget_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["uk_gross_usd"] = movies_df["domestic_gross_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["domestic_gross_usd"] = movies_df["domestic_gross_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["worldwide_gross_usd"] = movies_df["worldwide_gross_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["international_gross_usd"] = movies_df["international_gross_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["gross_profit_usd"] = movies_df["gross_profit_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["opening_weekend_takings"] = movies_df["opening_weekend_takings"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    
    col_list = ['budget_usd', 
                'uk_gross_usd', 
                'domestic_gross_usd', 
                'worldwide_gross_usd', 
                'international_gross_usd', 
                'gross_profit_usd', 
                'return_percentage', 
                'uk_percentage', 
                'tweet_count',
                'critical_period_tweet_count',
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

    return movies_df, col_list    

def get_correlation_measures_by_class(class_col):
    movies_df, col_list = get_df_and_col_list_for_correlation()

    class_list = movies_df[class_col].unique()
    
    results_df = pd.DataFrame()
    for class_val in class_list:
        class_df = movies_df[movies_df[class_col] == class_val]
        
        tweet_count_df = get_correlation_by_col(class_df, "tweet_count", col_list)
        critical_tweets_df = get_correlation_by_col(class_df, "critical_period_tweet_count", col_list)
        run_up_tweets_df = get_correlation_by_col(class_df, "run_up_tweets", col_list)
        opening_tweets_df = get_correlation_by_col(class_df, "opening_tweets", col_list)
        
        tweet_count_df["class_val"] = class_val
        critical_tweets_df["class_val"] = class_val        
        run_up_tweets_df["class_val"] = class_val
        opening_tweets_df["class_val"] = class_val
        
        results_df = results_df.append(tweet_count_df, ignore_index=True)
        results_df = results_df.append(critical_tweets_df, ignore_index=True)
        results_df = results_df.append(run_up_tweets_df, ignore_index=True)
        results_df = results_df.append(opening_tweets_df, ignore_index=True)
        
    return results_df
    

def get_correlation_measures():
    movies_df, col_list = get_df_and_col_list_for_correlation()
    
    #compare tweet_count for correlation  
    tweet_count_df = get_correlation_by_col(movies_df, "tweet_count", col_list)
    critical_tweets_df = get_correlation_by_col(movies_df, "critical_period_tweet_count", col_list)
    run_up_tweets_df = get_correlation_by_col(movies_df, "run_up_tweets", col_list)
    opening_tweets_df = get_correlation_by_col(movies_df, "opening_tweets", col_list)
                
    results_df = tweet_count_df.append(critical_tweets_df, ignore_index=True)
    results_df = results_df.append(run_up_tweets_df, ignore_index=True)
    results_df = results_df.append(opening_tweets_df, ignore_index=True)
    
    return results_df

def get_correlation_by_col(df, cor_col, col_list):
    results = []
    for col in col_list:
        if not col == cor_col:
                pearson = scipy.stats.pearsonr(df[cor_col], df[col])
                pearson_res = {"col_1" : cor_col, 
                              "col_2" : col, 
                              "method" : "pearson", 
                              "coef" : pearson[0], 
                              "p_val" : pearson[1]}
    
                spearman = scipy.stats.spearmanr(df[cor_col], df[col])
                spearman_res = {"col_1" : cor_col, 
                              "col_2" : col, 
                              "method" : "spearman", 
                              "coef" : spearman[0], 
                              "p_val" : spearman[1]}
                
                kendall = scipy.stats.kendalltau(df[cor_col], df[col])
                kendall_res = {"col_1" : cor_col, 
                              "col_2" : col, 
                              "method" : "kendalltau", 
                              "coef" : kendall[0], 
                              "p_val" : kendall[1]}

                results.append(pearson_res)                
                results.append(spearman_res)
                results.append(kendall_res)
                
    return pd.DataFrame(results)

def check_release_dates():
    movies_df = get_movies_df()
    movies_df["release_day"] = movies_df.apply(lambda row: row["ukReleaseDate"].weekday(), axis = 1)
    
    
    #get movies not released on a friday
    not_friday = movies_df.loc[lambda row: row["release_day"] != 4]
    
    return not_friday

def get_critical_period():
    movies_df = get_movies_df()
    
    movies_df["critical_start"] = movies_df.apply(lambda row: datetime.combine((row["ukReleaseDate"] - timedelta(days=7)), datetime.min.time()), axis = 1)
    movies_df["critical_end"] = movies_df.apply(lambda row: datetime.combine((row["ukReleaseDate"] + timedelta(days=14)), datetime.max.time()), axis = 1)
    
    
    return movies_df
    
