#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main set of utility functions used to explore and interrogate the data, this got very long but is well documented

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
    """
    Function to retreive dataframe of movies from the db (filtered to the 85 investigate)
    
    :return pandas dataframe of movies
    """
    
    movies_df = database_helper.select_query("movies", {"investigate" : "1"})
    movies_df = movies_df.sort_values(by=['movieId'])   
    return movies_df

def get_movies():
    """
    Function to build list of movie objects, filtered to 85 investigate movies  
    
    :return list of movie object
    """

    movies_df = database_helper.select_query("movies", {"investigate" : "1"}) 
     
    movies_df = movies_df.sort_values(by=['movieId'])  
    return gen_movies(movies_df)

def gen_movies(movies_df):
    """
    Function to generate a lis
    
    :param movies_df: dataframe from which movies list should be generated
    :return pandas dataframe of tweet counts and region ids
    """
    
    movies = []
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            movie = Movie(row)
            movies.append(movie)
            pbar.update(1)
    return movies

def get_movie_by_id(movieId): 
    """
    Function to get a singular movie object using its movie id
    
    :param movieId: integer movie id
    :return movie object   
    """
    
    #get movie from db and build object
    movies_df = database_helper.select_query("movies", { "movieId" : int(movieId) })
    if (not movies_df.empty):
        return Movie(movies_df.iloc[0])
    
    #if no matching movie return none
    return None


def get_movie_by_title(title):
    """
    Function to get a singular movie object using its title
    
    :param title: string movie title
    :return movie object   
    """
    
    #get movie from db and build object
    movies_df = database_helper.select_query("movies", { "title" : title })
    if (not movies_df.empty):
        return Movie(movies_df.iloc[0])
    
    #if no matching movie return none
    return None
    

def get_top_by_column(column, max_movies = 20, where_clause = ""):
    """
    Function to get the top movies in a certain column from the db
    
    :param column: string column name to use for ranking
    :param max_movies: limit on the number of movies to return
    :param where_clause: string peice of sql to use for additonal filtering
    :return dataframe of movies   
    """
    
    
    sql = """SELECT * FROM public.movies 
             WHERE "investigate" = '1'"""
             
    if where_clause:
        sql+= """ AND ({0})""".format(where_clause)
        
    sql+=""" ORDER BY "{0}" DESC LIMIT {1}""".format(column, max_movies)

    return database_helper.get_data(sql)

def get_top_movies_by_column(column, max_movies = 20):
    top_df = get_top_by_column(column, max_movies)
    return gen_movies(top_df) 

def get_lowest_by_column(column, max_movies = 20, where_clause = ""):
    """
    Function to get the bottom movies in a certain column from the db
    
    :param column: string column name to use for ranking
    :param max_movies: limit on the number of movies to return
    :param where_clause: string peice of sql to use for additonal filtering
    :return dataframe of movies   
    """
    
    sql = """SELECT * FROM public.movies 
             WHERE "investigate" = '1'"""
             
    if where_clause:
        sql+= """ AND ({0})""".format(where_clause)
        
    sql+=""" ORDER BY "{0}" ASC LIMIT {1}""".format(column, max_movies)
             
    return database_helper.get_data(sql)  

def get_lowest_movies_by_column(column, max_movies = 20):
    bottom_df = get_lowest_by_column(column, max_movies)
    return gen_movies(bottom_df)    


def count_tweets(movieId, start_date = None, end_date = None, senti_class = None):
    """
    Function to count movie related tweets
    
    :param movieId: integer movieId used to filter tweets to specific movie
    :param start_date: datetime of the start date to filter tweets
    :param end_date: datetime of the end date to filter tweets
    :param senti_class: string used to filter tweets to specific sentiment class
    :return pandas dataframe of movieId and tweet count
    """  
    
    sql = """
          SELECT "movieid", COUNT(*) 
          FROM movie_tweets2019 
          WHERE "movieid" = {0}""".format(movieId)   
        
    #apply filters if specified
    if not start_date == None:
        sql += """ AND "created_at" >= '{0}'""".format(start_date)
        
    if not end_date == None:
        sql += """ AND "created_at" <= '{0}'""".format(end_date)
          
    if not senti_class == None:
        sql += """ AND senti_class = '{0}'""".format(senti_class)
        
    sql += """ GROUP BY "movieid" """

        
    tweet_count = database_helper.get_data(sql)
    return tweet_count

def categorize_by_gross_profit():
    """
    Function to assign movies to ordinal classes based on their gross profit
    
    :return pandas dataframe of movies
    """      
    
    #get movies from db
    movies_df = get_movies_df()
    
    #calculate gross profit based on budget and worldwide gross
    movies_df["worldwide_gross_usd_norm"] = movies_df['worldwide_gross_usd'].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["budget_usd_norm"] = movies_df['budget_usd'].replace('[\£,]', '', regex=True).astype(float) / 1000000
    movies_df["gross_profit_usd_norm"] = movies_df["worldwide_gross_usd_norm"] - movies_df["budget_usd_norm"]
    movies_df["gross_profit_usd"] = movies_df["worldwide_gross_usd"].replace('[\£,]', '', regex=True).astype(float) - movies_df["budget_usd"].replace('[\£,]', '', regex=True).astype(float)
    
    #create buckets to group movies
    custom_bucket_array =[-100, 0, 90, 235, 700, 99999]
    bucket_labels = ['< $0 (Flop)', '$0 < $90m', '$90m < $235m', '$235m < $700m', '> $700m (BlockBuster)' ]
    
    #assign movies to buckets
    movies_df['class'] = pd.cut(movies_df['gross_profit_usd_norm'], custom_bucket_array,labels= bucket_labels)
    
    #update the profit class in the database
    for index, row in movies_df.iterrows(): 
            updates = { "gross_profit_usd" : row["gross_profit_usd"],
                    "profit_class" : row["class"]
                    }
            selects = {"movieId" : row["movieId"]}
            database_helper.update_data("movies", update_params = updates, select_params = selects)
    
    #return dataframe of movies
    return movies_df

def categorize_by_budget():
    """
    Function to assign movies to ordinal classes based on their budget
    
    :return pandas dataframe of movies
    """          
    
    #get movies from db
    movies_df = get_movies_df()
    
    #normalize budget to millions of usd
    movies_df["budget_norm"] = movies_df["budget_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    
    #create buckets to group movies
    custom_bucket_array =[0, 10, 40, 100, 185, 1000]
    bucket_labels = ['< $10m (Small)', '$10m < $40m', '$40m < $100m', '$100m < $185m', '> 185m (Big)' ]
    
    #assign movies to buckets
    movies_df['class'] = pd.cut(movies_df['budget_norm'], custom_bucket_array,labels= bucket_labels)
    
    #update the profit class in the database
    for index, row in movies_df.iterrows(): 
            updates = { "budget_class" : row["class"] }
            selects = {"movieId" : row["movieId"]}
            database_helper.update_data("movies", update_params = updates, select_params = selects)
    
    #return dataframe of movies
    return movies_df    

def categorize_by_uk_gross():
    """
    Function to assign movies to ordinal classes based on their uk gross
    
    :return pandas dataframe of movies
    """  
    
    #get movies from db
    movies_df = get_movies_df()
    
    #normalise uk gross to millions of usd
    movies_df["uk_gross_usd"] = movies_df["uk_gross_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    
    #create buckets to group movies
    custom_bucket_array =[0, 1, 8, 20, 50, 1000]
    bucket_labels = ['< $1m (Small)', '$1m < $8m', '$8m < $20m', '$20m < $50m', '> $50m (Big)' ]
    
    #assign movies to buckets
    movies_df['class'] = pd.cut(movies_df['uk_gross_usd'], custom_bucket_array,labels= bucket_labels)
    
    #update the budget class in the df
    for index, row in movies_df.iterrows(): 
            updates = { "uk_gross_class" : row["class"] }
            selects = {"movieId" : row["movieId"]}
            database_helper.update_data("movies", update_params = updates, select_params = selects)
    
    #return dataframe of movies
    return movies_df       

def calculate_percentage_profit():
    """
    Function to calculate the return percentage for each film
    
    :return pandas dataframe of movies
    """  
    
    #get movies from db
    movies_df = get_movies_df()
    
    #calculate the return based on worldwide gross and budget
    movies_df["gross_profit_norm"] = movies_df["gross_profit_usd"].replace('[\£,]', '', regex=True).astype(float)
    movies_df["budget_norm"] = movies_df["budget_usd"].replace('[\£,]', '', regex=True).astype(float)
    movies_df["return_percentage"] = (movies_df["gross_profit_norm"] / movies_df["budget_norm"]) * 100
    
    #update the return percentage in the db
    for index, row in movies_df.iterrows(): 
        updates = { "return_percentage" : row["return_percentage"] }
        selects = {"movieId" : row["movieId"]}
        database_helper.update_data("movies", update_params = updates, select_params = selects)
    
    #return dataframe of movies
    return movies_df


def categorize_by_return_percentage():
    """
    Function to assign movies to ordinal classes based on their return percentage
    
    :return pandas dataframe of movies
    """  
    
    #get movies from db
    movies_df = get_movies_df()
    
    #create buckets to group movies 
    custom_bucket_array = [-100, 0, 290, 540, 1000, 2000]
    bucket_labels = ['< %0 (Flop)', '0% - 290%', '100% - 540%', '540% - 1000%', '> 1000% (BlockBuster)']
    
    #assign movies to classes
    movies_df['class'] = pd.cut(movies_df['return_percentage'], custom_bucket_array,labels= bucket_labels)
  
    #update the return class in the db
    for index, row in movies_df.iterrows(): 
            updates = { "return_class" : row["class"] }
            selects = {"movieId" : row["movieId"]}
            database_helper.update_data("movies", update_params = updates, select_params = selects)
    
    #return dataframe of movies
    return movies_df

def categorize_by_uk_percentage():
    """
    Function to assign movies to ordinal classes based on their percentage of takings in the UK
    
    :return pandas dataframe of movies
    """  
    
    #get movies from the db
    movies_df = get_movies_df()
    
    #create buckets to group movies 
    custom_bucket_array =[0, 1, 4, 6, 12, 20]
    bucket_labels = ['0% - 1%', '1% - 4%', '4% - 6%', '6% - 12%', '> 12%']
    
    #assign movies to classes
    movies_df['class'] = pd.cut(movies_df['uk_percentage'], custom_bucket_array,labels= bucket_labels)
    
    #update the return class in the db
    for index, row in movies_df.iterrows(): 
            updates = { "uk_percentage_class" : row["class"] }
            selects = {"movieId" : row["movieId"]}
            database_helper.update_data("movies", update_params = updates, select_params = selects)
    
    #return dataframe of movies
    return movies_df

  
def calculate_uk_percentage_gross():
    """
    Function to calculate the uk percentage takings for each film
    
    :return pandas dataframe of movies
    """  
    
    #get movies from db
    movies_df = get_movies_df()
    
    #calculate return percentage based on worldwide gross and uk gross
    movies_df["worldwide_norm"] = movies_df["worldwide_gross_usd"].replace('[\£,]', '', regex=True).astype(float)
    movies_df["uk_takings_norm"] = movies_df["uk_gross_usd"].replace('[\£,]', '', regex=True).astype(float)
    movies_df["uk_percentage"] = (movies_df["uk_takings_norm"] / movies_df["worldwide_norm"]) * 100
    
    #update the db
    for index, row in movies_df.iterrows(): 
        updates = { "uk_percentage" : row["uk_percentage"] }
        selects = {"movieId" : row["movieId"]}
        database_helper.update_data("movies", update_params = updates, select_params = selects)
    
    #return list of movies
    return movies_df
    

def get_movie_genres():
    """
    Function to return a list of unqiue movie genres
    
    :return string list of movie genres
    """
    
    #get movies from df
    movies_df = get_movies_df()
    
    #get list of genres
    movies_df["genres_list"] = movies_df["genres"].apply(lambda x: x.split(',') if x != None else [])
    genre_list = movies_df["genres_list"].to_list()
    
    #extract unqiue list of genres
    genre_list = list(set([item for sublist in genre_list for item in sublist]))
    
    return genre_list


def get_movie_genre_counts():
    """
    Function to count the number of movies per genre
    
    :return pandas dataframe of genres and movie counts
    """
    
    #get movies from df
    movies_df = get_movies_df()
    
    #get unique list of genres
    genre_list = get_movie_genres()
    
    genre_df = pd.DataFrame(columns=["genre", "count"])
    
    #count the number of movies per genre
    counts = []
    for genre in genre_list:
        row_s = movies_df.apply(lambda x: True if genre in x["genres"] else False, axis=1)
        counts.append(len(row_s[row_s == True].index))
     
    genre_df["genre"] = genre_list
    genre_df["count"] = counts
    
    #return results
    return genre_df

def get_genre_tweet_counts():
    """
    Function to count the number of tweets per genre
    
    :return pandas dataframe of genres and tweet counts
    """
    
    #get unique list of movies and genres
    genre_list = get_movie_genres()
    counts = []
    
    #count the tweets for each movie in every genre
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
    
    #return results
    return genre_df

def get_genre_tweet_sentiments():
    """
    Function to get senti the number of tweets per sentiment and genre
    
    :return pandas dataframe of genre, sentiment classes and tweet counts
    """    
    
    #gt unique list of genres
    genre_list = get_movie_genres()
    
    output_df = pd.DataFrame(columns=['senti_class', 'counts', 'genre'])
    
    #for each genre get all the movies in that genre
    for genre in genre_list:
        genre_movies = database_helper.select_movies_by_genre(genre)
        
        #do the first movie 
        first_tweets = database_helper.select_geo_tweets(genre_movies.iloc[0]['movieId'])
        class_freq = first_tweets.groupby('senti_class').size().reset_index(name='counts')
        
        #get sentiment grouped tweet counts
        for index, row in genre_movies.iterrows():
            if index > 0:
                tweets = database_helper.select_geo_tweets(row["movieId"])
                my_class_freq = tweets.groupby('senti_class').size().reset_index(name='counts')
                class_freq['counts'] += my_class_freq['counts']
    
        class_freq['genre'] = genre
        output_df = output_df.append(class_freq)
      
    #return results
    return output_df

def get_genre_revenues():
    """
    Function to get the total profit per genre
    
    :return pandas dataframe of genre and profits
    """    
    
    #get unique list of genres
    genre_list = get_movie_genres()
                
    #get the profit for each movie in each genre
    genre_revenues = []
    for genre in genre_list:
        genre_movies = database_helper.select_movies_by_genre(genre)  
        genre_movies["profit_mil"] = genre_movies["gross_profit_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
        genre_total = genre_movies["profit_mil"].sum()
        
        genre_revenues.append(genre_total)
        
    output_df = pd.DataFrame(columns=["genre", "profit_mil"])
    output_df["genre"] = genre_list
    output_df["profit_mil"] = genre_revenues
    
    #return results
    return output_df


def get_correlation_matrix():
    """
    Function to generate correlation matrix for movie variables
    """    
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
    """
    Function to get movies where there is a gap in the cinema run
    
    :return pandas dataframe of movies 
    """    
    
    #get movies from db
    movies_df = get_movies_df()
    
    #check each movie to see if there is a gap in the box office data
    gap_movies_df = pd.DataFrame()
    for index, row in movies_df.iterrows():
        mojo_box_office_df = database_helper.select_query("weekend_box_office_mojo", {"movieid" : row['movieId']})
        
        if (check_mojo_for_gaps(mojo_box_office_df)):
            gap_movies_df = gap_movies_df.append(row)
        
    #return results
    return gap_movies_df
        
def check_mojo_for_gaps(df):
    """
    Function to check df of box office data for gaps in consecutive weekends
    
    :param df dataframe of weekend box office info
    :return True if gap exists otherwise False
    """   
    
    #order by the weeks on release incrementor
    df = df.sort_values(by='weeks_on_release', ascending=True)
    
    #if gap between previous week and next week is one then a gap exists
    prev_weeks = df.iloc[0]['weeks_on_release']
    for index, row in df.iterrows():
        if index > 0:
            cur_weeks = row['weeks_on_release']
            if (cur_weeks - prev_weeks) > 1:
                return True
            
            prev_weeks = cur_weeks
            
    return False

def get_end_weekend_for_first_run(df):
    """
    Function to get the last weekend from the first run of consecutive box office data
    
    :param df: dataframe of weekend box office info
    :return date of the end weekend
    """       
    
    #order by the weeks on release incrementor
    df = df.sort_values(by='weeks_on_release', ascending=True)
    
    prev_weeks = df.iloc[0]['weeks_on_release']
    prev_end = df.iloc[0]['end_date']
    
    end_weekend = df.iloc[df['weeks_on_release'].idxmax()].end_date
    
    #for each week, check if gap is greater than one week
    for index, row in df.iterrows():
        if index > 0:
            cur_weeks = row['weeks_on_release']
            cur_end = row['end_date']
            if (cur_weeks - prev_weeks) > 1:
                return prev_end
            
            prev_weeks = cur_weeks
            prev_end = cur_end
            
    return end_weekend

def get_trailer_tweets(movieId, most_tweeted = False, senti_class=None, time_period=1):
    """
    Function to return tweets around the release of movie trailers
    
    :param movieId: integer id of the movie whose trailer tweets we are looking for
    :param most_tweeted: boolean flag to indicate if only the most tweeted trailer should be used
    :param time_period: integer indicating the number of days after trailer release date to take into account
    :return geopandas dataframe of trailer tweets
    """ 
    
    #get movie trailers from the db
    trailers_df = database_helper.select_query("trailers", { "movieId" : int(movieId) })
    
    #set the start and end dates to widen the search field
    trailers_df["start_date"] = trailers_df.apply(lambda row: datetime.combine(row["publishDate"], datetime.min.time()), axis=1)
    trailers_df["end_date"] = trailers_df.apply(lambda row: datetime.combine((row["publishDate"] + timedelta(days=time_period)), datetime.max.time()), axis=1)
    
    tweets = pd.DataFrame()
    
    #using the date range get the tweets for each trailer
    for index, row in trailers_df.iterrows():
        trailer_tweets = database_helper.select_geo_tweets(movieId, start_date = row["start_date"], end_date = row["end_date"], senti_class = senti_class)
        trailer_tweets["trailerId"] = row["id"]
        trailer_tweets["youtubeId"] = row["youtubeId"]
        
        tweets = tweets.append(trailer_tweets)
        
        
    #if most tweeted only return the tweets for the most tweeted trailer
    if most_tweeted:
        trailer_counts = tweets.groupby(by="trailerId").size().reset_index(name="tweet_count")
        most_tweeted_id = trailer_counts.loc[trailer_counts["tweet_count"].idxmax()]["trailerId"]
        
        tweets = tweets[tweets["trailerId"] == most_tweeted_id]

    #return dataframe of trailer tweets
    return tweets.reset_index()

def get_trailer_tweet_count(movieId, most_tweeted = False, senti_class=None):
    """
    Function to return count tweets around the release of movie trailers
    
    :param movieId: integer id of the movie whose trailer tweets we are looking for
    :param most_tweeted: boolean flag to indicate if only the most tweeted trailer should be used
    :param time_period: integer indicating the number of days after trailer release date to take into account
    :return integer count of movie trailer tweets
    """ 
    
    #get tweets and count
    trailer_tweets = get_trailer_tweets(movieId, most_tweeted, senti_class)

    return trailer_tweets.shape[0]

def get_movies_df_with_sentiment_summaryies(movies_df, most_tweeted_trailer=False):
    """
    Function to get summaries of the count and sentiment of tweets for each movie at different time periods
    
    :param movies_df: dataframe of movies collected from the db
    :param most_tweeted_trailer: boolean flag to indicate if only the most tweeted trailer should be used
    :return pandas dataframe with counts and percentages of movie tweets and sentiment
    """ 
    
    #get the total tweets, negative, positive and neutral rates
    movies_df["tweet_count"] = movies_df.apply(lambda row: count_tweets(row.movieId)['count'], axis = 1)
    movies_df["positive_tweets"] = movies_df.apply(lambda row: count_tweets(row.movieId, senti_class = 'positive')['count'], axis = 1)
    movies_df["positive_tweets_percentage"] = (movies_df["positive_tweets"] / movies_df["tweet_count"]) * 100   
    movies_df["neutral_tweets"] = movies_df.apply(lambda row: count_tweets(row.movieId, senti_class = 'neutral')['count'], axis= 1)  
    movies_df["neutral_tweets_percentage"] = (movies_df["neutral_tweets"] / movies_df["tweet_count"]) * 100
    movies_df["negative_tweets"] = movies_df.apply(lambda row: count_tweets(row.movieId, senti_class = 'negative')['count'], axis = 1)  
    movies_df["negative_tweets_percentage"] = (movies_df["negative_tweets"] / movies_df["tweet_count"]) * 100

    #get the critical period tweets, negative, positive and neutral rates
    movies_df["critical_period_tweet_count"] = movies_df.apply(lambda row: count_tweets(row["movieId"], row["critical_start"], row["critical_end"])['count'], axis = 1)
    movies_df["critical_period_tweet_pos"] = movies_df.apply(lambda row: count_tweets(row["movieId"], row["critical_start"], row["critical_end"], senti_class = 'positive')['count'], axis = 1)
    movies_df["critical_period_pos_percentage"] = (movies_df["critical_period_tweet_pos"] / movies_df["critical_period_tweet_count"]) * 100
    movies_df["critical_period_tweet_neu"] = movies_df.apply(lambda row: count_tweets(row["movieId"], row["critical_start"], row["critical_end"], senti_class = 'neutral')['count'], axis = 1)
    movies_df["critical_period_neu_percentage"] = (movies_df["critical_period_tweet_neu"] / movies_df["critical_period_tweet_count"]) * 100
    movies_df["critical_period_tweet_neg"] = movies_df.apply(lambda row: count_tweets(row["movieId"], row["critical_start"], row["critical_end"], senti_class = 'negative')['count'], axis = 1)
    movies_df["critical_period_neg_percentage"] = (movies_df["critical_period_tweet_neg"] / movies_df["critical_period_tweet_count"]) * 100
    
    #get the trailer tweets, negative, positive and neutral rates
    movies_df["trailer_tweet_count"] = movies_df.apply(lambda row: get_trailer_tweet_count(row["movieId"], most_tweeted=most_tweeted_trailer), axis = 1)
    movies_df["trailer_tweet_pos"] = movies_df.apply(lambda row: get_trailer_tweet_count(row["movieId"], most_tweeted=most_tweeted_trailer, senti_class = 'positive'), axis = 1)
    movies_df["trailer_pos_percentage"] = (movies_df["trailer_tweet_pos"] / movies_df["trailer_tweet_count"]) * 100
    movies_df["trailer_tweet_neu"] = movies_df.apply(lambda row: get_trailer_tweet_count(row["movieId"], most_tweeted=most_tweeted_trailer, senti_class = 'neutral'), axis = 1)
    movies_df["trailer_neu_percentage"] = (movies_df["trailer_tweet_neu"] / movies_df["trailer_tweet_count"]) * 100
    movies_df["trailer_tweet_neg"] = movies_df.apply(lambda row: get_trailer_tweet_count(row["movieId"], most_tweeted=most_tweeted_trailer, senti_class = 'negative'), axis = 1)
    movies_df["trailer_neg_percentage"] = (movies_df["trailer_tweet_neg"] / movies_df["trailer_tweet_count"]) * 100
    
    #return the extended movies dataframe
    return movies_df

def get_movie_run_info():
    """
    Function to get extended dataframe of movies with informaion about their first uninterrupted cinema run

    :return pandas dataframe of movies with first run info
    """    
    
    #get movies from db
    movies_df = get_movies_df()
    
    #use box office mojo data to get first run stats for each movie
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
    
    #return results
    return pd.DataFrame(dict_lst)

def check_run_dates_tweets():
    """
    Function to check for films where the cinema run extends beyond the coverage of the twitter data
    
    :return pandas dataframe of movies
    """ 
    
    #get movies from db
    movies_df = get_movies_df()
    
    #get max tweet date
    max_tweet_date = tweet_helper.get_max_date().date()
    
    #check max film weekend against max tweet date for each film
    problem_films = pd.DataFrame()
    for index, row in movies_df.iterrows():
        if row['first_run_end'] >= max_tweet_date:
            problem_films = problem_films.append(row)
       
    #return results
    return problem_films

##DEPRICATED##
def get_trailer_tweet_counts():
    movies = get_movies()
    
    results = []
    for movie in movies:
        results.append({"movieId" : movie.movieId, "trailer_tweets" : movie.get_trailer_tweet_counts()})
        
        
    return pd.DataFrame(results)
###


def get_run_positive_increase():
    """
    Function to check for movies where the percentage of revenue increases instead of decrease across a weekend
    
    :return pandas dataframe of movies
    """ 
    
    #get movies from db
    movies_df = get_movies_df()
    
    #check the weekly box office data from each movie for a positive percentage change
    positive_changes = pd.DataFrame()
    for index, row in movies_df.iterrows():
        #if ppstive change exists add movie to return list
        mojo_box_office_df = database_helper.select_query("weekend_box_office_mojo", {"movieid" : row['movieId']})
        if (mojo_box_office_df['percentage_change'] > 0).any() :
            positive_changes = positive_changes.append(row)
     
    #return results
    return positive_changes

def get_highest_mojo_rank():
    """
    Function to get rank information based on box office data
    
    :return pandas dataframe of movies
    """ 
    
    #get movies from db
    movies_df = get_movies_df()
    
    rank_list = []
    for index, row in movies_df.iterrows():
        mojo_box_office_df = database_helper.select_query("weekend_box_office_mojo", {"movieid" : row['movieId']})
        
        #get top rank
        best_rank = mojo_box_office_df["rank"].min()
        
        #get weekends at best
        best_rows = mojo_box_office_df[mojo_box_office_df['rank'] == best_rank]
        weekends_at_rank = best_rows.shape[0]
        
        #get weekends in top 3
        top_3_rows = mojo_box_office_df[mojo_box_office_df['rank'] <= 3]
        top_3_weekends = top_3_rows.shape[0]
        
        #get weekends in top 5
        top_5_rows = mojo_box_office_df[mojo_box_office_df['rank'] <= 5]
        top_5_weekends = top_5_rows.shape[0]
        
        #get weekends in top 10
        top_10_rows = mojo_box_office_df[mojo_box_office_df['rank'] <= 10]
        top_10_weekends = top_10_rows.shape[0]
        
        #get weekends in top 15
        top_15_rows = mojo_box_office_df[mojo_box_office_df['rank'] <= 15]
        top_15_weekends = top_15_rows.shape[0]
        
        rank_list.append({"movieId" : row["movieId"], 
                          "best_rank" : best_rank, 
                          'weekends_at_best_rank' : weekends_at_rank,
                          'weekends_in_top_3' : top_3_weekends,
                          'weekends_in_top_5' : top_5_weekends,
                          'weekends_in_top_10' : top_10_weekends,
                          'weekends_in_top_15' : top_15_weekends})
        
        
    #return extended dataframe of movies  
    return pd.DataFrame(rank_list)

def get_movie_tweet_events():
    """
    Function to get daily peak events for each movie
    
    :return dictionary of pandas dataframes of events
    """ 
    
    #get movies from db
    movies = get_movies()
    
    events_df = pd.DataFrame()
    all_peaks = pd.DataFrame()
    trailer_peaks = pd.DataFrame()
    
    #for each film get top event and any trailer events
    for movie in movies:
        tweet_peaks = movie.get_tweet_peak_events()
        
        events_df = events_df.append(tweet_peaks)
        all_peaks = all_peaks.append(tweet_peaks.iloc[0])
       
        trailer_peaks = trailer_peaks.append(tweet_peaks.loc[tweet_peaks["youtubeId"] != "NO"])

    results = {"all_events" : events_df.reset_index(drop=True),
               "peak_events" : all_peaks.reset_index(drop=True),
               "trailer_peaks" : trailer_peaks.reset_index(drop=True)}  
      
    return results



def get_movies_df_with_opening_weekend():
    """
    Function to get extended list of movies with opening weekend data
    
    :return pandas dataframe of movies
    """ 
    
    #get all movies and calculate opening weekend takigns
    movies_df = get_movies_df()
    movies_df["opening_weekend_takings"] = movies_df.apply(lambda row: database_helper.select_query("weekend_box_office_mojo", {"movieid" : row['movieId']}).iloc[0]['weekend_gross_usd'], axis=1)
    
    
    
    tweets_prior_to_opening = [] 
    
    pos_tweets_prior_to_opening = []
    neu_tweets_prior_to_opening = []
    neg_tweets_prior_to_opening = []
    
    opening_weekend_tweets = []
    
    pos_opening_weekend_tweets = []
    neu_opening_weekend_tweets = []
    neg_opening_weekend_tweets = []
    
    #get opening weekend and run up week tweets and percentages
    for index, row in movies_df.iterrows():
        mojo_df = database_helper.select_query("weekend_box_office_mojo", {"movieid" : row['movieId']})
        
        opening_start = mojo_df.iloc[0]['start_date']
        opening_end = mojo_df.iloc[0]['end_date']
        
        prev_week = datetime.combine((opening_start  - timedelta(days=7)), datetime.min.time())
        prev_end = datetime.combine((opening_start - timedelta(days=1)), datetime.max.time())

        #check run up tweets
        run_up_count = count_tweets(row['movieId'], prev_week, prev_end)
        pos_run_up_count = count_tweets(row['movieId'], prev_week, prev_end, senti_class="positive")
        neu_run_up_count = count_tweets(row['movieId'], prev_week, prev_end, senti_class="neutral")
        neg_run_up_count = count_tweets(row['movieId'], prev_week, prev_end, senti_class="negative")

        #check for empty results
        run_up_count = run_up_count.iloc[0]['count'] if not run_up_count.empty else 0
        pos_run_up_count = pos_run_up_count.iloc[0]['count'] if not pos_run_up_count.empty else 0
        neu_run_up_count = neu_run_up_count.iloc[0]['count'] if not neu_run_up_count.empty else 0
        neg_run_up_count = neg_run_up_count.iloc[0]['count'] if not neg_run_up_count.empty else 0
        
        #search opening weekend tweets
        opening_start = datetime.combine(opening_start, datetime.min.time())
        opening_end = datetime.combine(opening_end, datetime.max.time())
        
        opening_count = count_tweets(row['movieId'], opening_start, opening_end)
        pos_opening_count = count_tweets(row['movieId'], opening_start, opening_end, senti_class="positive")
        neu_opening_count = count_tweets(row['movieId'], opening_start, opening_end, senti_class="neutral")
        neg_opening_count = count_tweets(row['movieId'], opening_start, opening_end, senti_class="negative")
        
        #check for empty results
        opening_count = opening_count.iloc[0]['count'] if not opening_count.empty else 0
        pos_opening_count = pos_opening_count.iloc[0]['count'] if not pos_opening_count.empty else 0
        neu_opening_count = neu_opening_count.iloc[0]['count'] if not neu_opening_count.empty else 0
        neg_opening_count = neg_opening_count.iloc[0]['count'] if not neg_opening_count.empty else 0

        tweets_prior_to_opening.append(run_up_count)
        pos_tweets_prior_to_opening.append(pos_run_up_count)
        neu_tweets_prior_to_opening.append(neu_run_up_count)
        neg_tweets_prior_to_opening.append(neg_run_up_count)        
        
        opening_weekend_tweets.append(opening_count)
        pos_opening_weekend_tweets.append(pos_opening_count)
        neu_opening_weekend_tweets.append(neu_opening_count)
        neg_opening_weekend_tweets.append(neg_opening_count)
      
    #extend movies df to contain info about run up tweets
    movies_df['run_up_tweets'] = tweets_prior_to_opening
    movies_df['run_up_tweets_pos'] = pos_tweets_prior_to_opening
    movies_df['run_up_pos_percentage'] = (movies_df["run_up_tweets_pos"] / movies_df["run_up_tweets"]) * 100
    movies_df['run_up_tweets_neu'] = neu_tweets_prior_to_opening
    movies_df['run_up_neu_percentage'] = (movies_df["run_up_tweets_neu"] / movies_df["run_up_tweets"]) * 100
    movies_df['run_up_tweets_neg'] = neg_tweets_prior_to_opening
    movies_df['run_up_neg_percentage'] = (movies_df["run_up_tweets_neg"] / movies_df["run_up_tweets"]) * 100
    
    #extend movies df to contain info about opening weekend tweets
    movies_df['opening_tweets'] = opening_weekend_tweets
    movies_df['opening_tweets_pos'] = pos_opening_weekend_tweets
    movies_df['opening_pos_percentage'] = (movies_df["opening_tweets_pos"] / movies_df["opening_tweets"]) * 100
    movies_df['opening_tweets_neu'] = neu_opening_weekend_tweets
    movies_df['opening_neu_percentage'] = (movies_df["opening_tweets_neu"] / movies_df["opening_tweets"]) * 100
    movies_df['opening_tweets_neg'] = neg_opening_weekend_tweets
    movies_df['opening_neg_percentage'] = (movies_df["opening_tweets_neg"] / movies_df["opening_tweets"]) * 100
    
    #return extended movies dataframe
    return movies_df


def get_df_and_col_list_for_correlation():
    """
    Function to get extended dataframe of movies with variables needed for correlaiton
    
    :return movies dataframe and list of columns to use in correlations
    """ 
    
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

def get_weekend_tweets_takings_correltation(full_week=False, week_inc_weekend=False, senti_class = None, percentage = False):
    movies = get_movies()
    
    results_df = pd.DataFrame()
    
    for movie in movies:
        correl_df = movie.corellate_weekend_takings_against_tweets(full_week=full_week, week_inc_weekend=week_inc_weekend, senti_class = senti_class, percentage = percentage)
        results_df = results_df.append(correl_df)
        
    return results_df
        

def get_tweet_senti_counts_by_class(movies_df, class_list, pos_col = "positive_tweets", neu_col = "neutral_tweets", neg_col = "negative_tweets"):
    
    results_df = pd.DataFrame()

    for class_name in class_list:
        pos_budget_df = movies_df.groupby([class_name])[pos_col].sum().reset_index(name="tweet_count")
        pos_budget_df = pos_budget_df.rename(columns={class_name : 'class_val'})
        pos_budget_df["senti_class"] = "positive"
        pos_budget_df["class_name"] = class_name
        
        neg_budget_df = movies_df.groupby([class_name])[neu_col].sum().reset_index(name="tweet_count")
        neg_budget_df = neg_budget_df.rename(columns={class_name : 'class_val'})
        neg_budget_df["senti_class"] = "negative"
        neg_budget_df["class_name"] = class_name
        
        neu_budget_df = movies_df.groupby([class_name])[neg_col].sum().reset_index(name="tweet_count")
        neu_budget_df = neu_budget_df.rename(columns={class_name : 'class_val'})
        neu_budget_df["senti_class"] = "neutral"
        neu_budget_df["class_name"] = class_name
        
        
        
        results_df = results_df.append(pos_budget_df)
        results_df = results_df.append(neg_budget_df)
        results_df = results_df.append(neu_budget_df)

    #get totals and percentage
    grouped_sum = results_df.groupby(['class_val'])["tweet_count"].sum().reset_index(name="total")
    results_df = results_df.merge(grouped_sum, on="class_val", how="left")
    results_df["percentage"] = (results_df["tweet_count"] / results_df["total"]) * 100

    return results_df

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

def convert_financial_to_mil(df):
    df["budget_usd"] = df["budget_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    df["uk_gross_usd"] = df["uk_gross_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    df["domestic_gross_usd"] = df["domestic_gross_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    df["worldwide_gross_usd"] = df["worldwide_gross_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    df["international_gross_usd"] = df["international_gross_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    df["gross_profit_usd"] = df["gross_profit_usd"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    df["opening_weekend_takings"] = df["opening_weekend_takings"].replace('[\£,]', '', regex=True).astype(float) / 1000000
    
    return df

def get_percentage_of_takings_in_first_weeks():
    movies = get_movies()

    for movie in movies:
        percentage = movie.get_percentage_of_takings_in_first_two_weeks()
        updates = { "two_week_takings" : percentage }
        selects = {"movieId" : movie.movieId }
        database_helper.update_data("movies", update_params = updates, select_params = selects)


        
