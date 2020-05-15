#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 14:58:04 2020

@author: andy
"""

import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Utils')

import bfi_helper
import database_helper
from tqdm import tqdm




#get full film set 
film_df = bfi_helper.get_raw_data()
film_df_sub = film_df[['Film', 'Country of Origin', 'Distributor']].drop_duplicates()
film_df_unq = film_df.drop_duplicates()

def add_movies_to_db():
    with tqdm(total=len(film_df_unq)) as pbar:
        for index, row in film_df_unq.iterrows(): 
            #check that the movie has not been added yet
            existing = database_helper.select_query("movies", {"title" : row["Film"]})
            if (existing.empty):
                database_helper.insert_data("movies", {"title" : row['Film'], "distributor" : row['Distributor'], "country" : row['Country of Origin']})
            pbar.update(1)

def add_box_office():
    with tqdm(total=len(film_df)) as pbar:
        for index, row in film_df.iterrows(): 
            movie_df = database_helper.select_query("movies", {"title" : row['Film']})
            movie_id = int(movie_df.iloc[0]['movieId'])
      
            percentage_change = None
            try:
                percentage_change = float(row['% change on last week'])
            except ValueError:
                percentage_change = None
                
            insert_params = {
                "movieId" : movie_id, 
                "weeksOnRelease" : row['Weeks on release'], 
                "noOfcinemas" : row['Number of cinemas'], 
                "weekendGross" : row['Weekend Gross'], 
                "percentageChange" : percentage_change, 
                "siteAverage" : row['Site average'], 
                "grossToDate" : row['Total Gross to date'], 
                "weekendStart" : row['weekendStart'], 
                "weekendEnd" : row['weekendEnd'], 
                "rank" : row['Rank']
                }
            database_helper.insert_data("weekend_box_office", insert_params)

            pbar.update(1)

#add_movies_to_db()
add_box_office()

# for index, row in film_df.iterrows():  
#     get_movie_sql = " SELECT * FROM public.movies WHERE title = %(film)s"
#     get_movie_params = {'film' : row['Film']}
    
#     movie_df = database_helper.select_query("movies", {"title" : row['Film']})
#    # movie_df = database_helper.get_data(get_movie_sql, get_movie_params)
#     movie_id = int(movie_df.iloc[0]['movieId'])
      
#     percentage_change = None
#     try:
#         percentage_change = float(row['% change on last week'])
#     except ValueError:
#             percentage_change = None
        
#     insert_sql = """
#     INSERT INTO 
#     weekend_box_office("movieId", "weeksOnRelease", "noOfcinemas", "weekendGross", "percentageChange", "siteAverage", "grossToDate", "weekendStart", "weekendEnd", "rank") 
#     VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
#     """ 
#     insert_params = (movie_id, row['Weeks on release'], row['Number of cinemas'], row['Weekend Gross'], percentage_change, row['Site average'], row['Total Gross to date'], row['weekendStart'], row['weekendEnd'], row['Rank'])
#     database_helper.run_query(insert_sql, insert_params)

# =============================================================================
# try: 
#     connection = psycopg2.connect(user="postgres",
#                                   password="4ndr3wP0ST",
#                                   host="127.0.0.1",
#                                   port="5432",
#                                   database="geotweets")
#     
#     for index, row in film_df.iterrows():  
#         get_movie = " SELECT * FROM public.movies WHERE title = %(film)s"
#         movie_df = sqlio.read_sql_query(get_movie, connection, params = {'film' : row['Film']})
#         movie_id = int(movie_df.head(1)['movieId'])
#         
#         percentage_change = None
#         try:
#             percentage_change = float(row['% change on last week'])
#         except ValueError:
#             percentage_change = None
#         
#         sql = """
#         INSERT INTO 
#         weekend_box_office("movieId", "weeksOnRelease", "noOfcinemas", "weekendGross", "percentageChange", "siteAverage", "grossToDate", "weekendStart", "weekendEnd", "rank") 
#         VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
#         """ 
#         cursor = connection.cursor()      
#         cursor.execute(sql, (movie_id, row['Weeks on release'], row['Number of cinemas'], row['Weekend Gross'], percentage_change, row['Site average'], row['Total Gross to date'], row['weekendStart'], row['weekendEnd'], row['Rank']))    
#         connection.commit()
#         cursor.close()
#     
#     
# except (Exception, psycopg2.Error) as error :
#     print ("Error while connecting to PostgreSQL", error)
# finally:
#     #closing database connection.
#         if(connection):
#             # cursor.close()
#             connection.close()
#             print("PostgreSQL connection is closed")
# =============================================================================

#create postgres connection 
# =============================================================================
# try: 
#     connection = psycopg2.connect(user="postgres",
#                                   password="4ndr3wP0ST",
#                                   host="127.0.0.1",
#                                   port="5432",
#                                   database="geotweets")
#     
#     for index, row in film_df_sub.iterrows():      
#         sql = """
#         INSERT INTO movies(title, distributor, country) VALUES(%s, %s, %s);
#         """
#     
#         cursor = connection.cursor()      
#         cursor.execute(sql, (row['Film'], row['Distributor'], row['Country of Origin']))    
#         connection.commit()
#         cursor.close()
#     
#     
# except (Exception, psycopg2.Error) as error :
#     print ("Error while connecting to PostgreSQL", error)
# finally:
#     #closing database connection.
#         if(connection):
#            # cursor.close()
#             connection.close()
#             print("PostgreSQL connection is closed")
# =============================================================================
