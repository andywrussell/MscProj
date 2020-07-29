#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 12:20:34 2020

@author: andy
"""
import geopandas as gpd
import pandas.io.sql as sqlio
import psycopg2
from sqlalchemy import create_engine
import io
import csv

def run_query(sql, params):
    """
    Create a connection to the database and execute query
    
    :param sql: string contating sql query
    :param params: tuple containing query parameters
    """
    try: 
        connection = psycopg2.connect(user="postgres",
                                      password="4ndr3wP0ST!",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="geotweets")
        
        cursor = connection.cursor()      
        cursor.execute(sql, params)    
        connection.commit()
        cursor.close()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        #closing database connection.
            if(connection):
                # cursor.close()
                connection.close()
                #print("PostgreSQL connection is closed")
                
def get_data(sql, q_params = None):
    """
    Fetch data from the database and return as pandas dataframe
    
    :param sql: string contating sql query
    :param q_params: dictionary of query parameters
    :return pandas dataframe of query results
    """
    try: 
        connection = psycopg2.connect(user="postgres",
                                      password="4ndr3wP0ST!",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="geotweets")
        
        result = sqlio.read_sql_query(sql, connection, params = q_params)
        return result
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        #closing database connection.
            if(connection):
                # cursor.close()
                connection.close()
                #print("PostgreSQL connection is closed")
                
def get_geo_data(sql, geom ='geom'):
    try: 
        connection = psycopg2.connect(user="postgres",
                                      password="4ndr3wP0ST!",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="geotweets")
        
        result = gpd.GeoDataFrame.from_postgis(sql, connection, geom_col= geom )
        return result
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        #closing database connection.
            if(connection):
                # cursor.close()
                connection.close()
                #print("PostgreSQL connection is closed")
    
                
def select_query(table, params = None, where_operator = "AND"):
    """
    Method to select data from any table
    
    :param table: string name of table
    :param params: dictionary of select parameter
    :param where_operator: string to join parameters e.g "AND", "OR"
    :return pandas dataframe of query results
    """
    sql = "SELECT * FROM public." + table
    if (params):
        sql += " WHERE "
        for key in params:
            sql += '"{0}" = %({0})s'.format(key)
            if (key != list(params.keys())[-1]):
                sql += " {0} ".format(where_operator)
                
    return get_data(sql, params)

def search_tweets(search_terms = [], where_operator = "OR"):
    """
    Method to select data from any table
    
    :param table: string name of table
    :param params: dictionary of select parameter
    :param where_operator: string to join parameters e.g "AND", "OR"
    :return pandas dataframe of query results
    """
    sql = "SELECT * FROM public.tweets2019 WHERE"
    for idx, val in enumerate(search_terms):
        sql += """ "msg" ilike '{0}' """.format(val)
        if (idx != len(search_terms)-1):
            sql += " {0} ".format(where_operator)
      
    print(sql)
    return get_data(sql)
    


def insert_data(table, params):
    """
    Method to insert data into any table
    
    :param table: string name of table
    :param params: dictionary of insert values
    """
    sql = "INSERT INTO " + table + "("
    for key in params:
        sql += '"{0}"'.format(key)
        if (key != list(params.keys())[-1]):
          sql += ","
        
    sql += ") VALUES(" 
    for key in params:
      sql += "%s"
      if (key != list(params.keys())[-1]):
          sql += ","
    
    sql += ")"
    
    run_query(sql, tuple(params.values()))
            
def update_data(table, update_params, select_params, select_operator = "AND"):
    """
    Method to update data in any table
    
    :param table: string name of table
    :param update_params: dictionary containing the parameters to be updated
    :param select_params: dictionayry containing the paramers for selecting the updated row
    :param select_operator: string to join parameters e.g "AND", "OR"
    """
    
    sql = "UPDATE " + table + " SET "
    for key in update_params:
        sql += '"{0}" = %s'.format(key)
        if (key != list(update_params.keys())[-1]):
          sql += ","
          
    if (select_params):
        sql += " WHERE "
        for key in select_params:
            sql += '"{0}" = %s'.format(key)
            if (key != list(select_params.keys())[-1]):   
                sql += " {0} ".format(select_operator)
    run_query(sql, tuple(list(update_params.values()) + list(select_params.values())))
    
    
def bulk_insert_df(table, df, cols):
    address = 'postgresql://postgres:4ndr3wP0ST!@127.0.0.1:5432/geotweets'
    engine = create_engine(address)
    connection = engine.raw_connection()
    cursor = connection.cursor()
    
    escaped = {'\\': '\\\\', '\n': r'\n', '\r': r'\r', '\t': r'\t'}
    for col in df.columns:
        if df.dtypes[col] == 'object':
            for v, e in escaped.items():
                df[col] = df[col].str.replace(v, e)
    
    #stream the data using 'to_csv' and StringIO(); then use sql's 'copy_from' function
    output = io.StringIO()
    #ignore the index
    df.to_csv(output, sep='\t', header=False, index=False)
    #jump to start of stream
    output.seek(0)
    contents = output.getvalue()

    #null values become ''
    cursor.copy_from(output, table, columns=cols, null="")    
    connection.commit()
    cursor.close()
    connection.close()
    

def select_base_tweets():
    sql = """SELECT id, wgslat, wgslng, geombng FROM tweets2019 """
    df = get_geo_data(sql, "geombng")
    return df

def select_uk_fishnet():
    sql = """SELECT * FROM uk_fishnet"""
    df = get_geo_data(sql, 'geombng')
    return df
    
def select_fishnet_count(start_date = None, end_date = None):
    if (not start_date == None) and (not end_date == None):
        #need to count on the fly
        sql = """SELECT count(*) as tweet_count, cellid
                FROM tweets_fishnet
                WHERE created_at >= '{0}' AND created_at <= '{1}'
                GROUP BY cellid""".format(start_date, end_date)
                
        return get_data(sql)
        
    else:
        return select_query("tweets_fishnet_count")

def select_geo_tweets(movieId = 0, start_date = None, end_date = None, senti_class = None):
    sql = """
        SELECT geombng, movieid, msg, wgslat, wgslng, created_at, id, senti_class, compound_scr
        FROM movie_tweets2019
        WHERE 1 = 1
    """.format(movieId)
    
    if movieId > 0:
        sql += """ AND movieid = {0}""".format(movieId)    
    
    if not start_date == None:
        sql += """ AND "created_at" >= '{0}'""".format(start_date)
        
    if not end_date == None:
        sql += """ AND "created_at" <= '{0}'""".format(end_date)
    
    if not senti_class == None:
        sql += """ AND "senti_class" = '{0}'""".format(senti_class)
    
    df = get_geo_data(sql, 'geombng')
    return df

def select_movie_fishnet_tweets(movieId = 0, start_date = None, end_date = None, senti_class = None):
    sql = """select f.*, t.movieid from tweets_fishnet f 
            inner join movie_tweets2019 t 
            on t.id = f.id
            where 1 = 1"""
            
    if movieId > 0:
        sql += """ AND t.movieid = {0}""".format(movieId)
        
    if not start_date == None:
        sql += """ AND t.created_at >= '{0}'""".format(start_date)
        
    if not end_date == None:
        sql += """ AND t.created_at <= '{0}'""".format(end_date)
    
    if not senti_class == None:
        sql += """ AND t.senti_class = '{0}'""".format(senti_class)
        
    return get_data(sql)

def select_movie_region_tweets(movieId = 0, start_date = None, end_date = None, senti_class = None):
    sql = """select f.*, t.movieid from tweets_region f 
            inner join movie_tweets2019 t 
            on t.id = f.id
            where 1 = 1"""
            
    if movieId > 0:
        sql += """ AND t.movieid = {0}""".format(movieId)
        
    if not start_date == None:
        sql += """ AND t.created_at >= '{0}'""".format(start_date)
        
    if not end_date == None:
        sql += """ AND t.created_at <= '{0}'""".format(end_date)
    
    if not senti_class == None:
        sql += """ AND t.senti_class = '{0}'""".format(senti_class)
       
    return get_data(sql)

def select_movie_region_tweets_with_geo(movieId = 0, start_date = None, end_date = None, senti_class = None):
    sql = """select f.*, t.movieid, t.geombng from tweets_region f 
            inner join movie_tweets2019 t 
            on t.id = f.id
            where 1 = 1"""
            
    if movieId > 0:
        sql += """ AND t.movieid = {0}""".format(movieId)
        
    if not start_date == None:
        sql += """ AND t.created_at >= '{0}'""".format(start_date)
        
    if not end_date == None:
        sql += """ AND t.created_at <= '{0}'""".format(end_date)
    
    if not senti_class == None:
        sql += """ AND t.senti_class = '{0}'""".format(senti_class)
        
    df = get_geo_data(sql, 'geombng')
    return df

def select_region_tweets(start_date = None, end_date = None):
    sql = """ select count(*) as tweet_count, unit_id
              from tweets_region WHERE 1 = 1"""
              
    if not start_date == None:
        sql += """ AND "created_at" >= '{0}'""".format(start_date)
        
    if not end_date == None:
        sql += """ AND "created_at" <= '{0}'""".format(end_date)
              
    sql += "group by unit_id"
    
    return get_data(sql)

def select_movies_by_genre(genre, investigate_only=True):
    sql = """
        SELECT *
        FROM movies
        WHERE genres ilike '%{0}%'
    """.format(genre)
    
    if investigate_only:
        sql += " AND investigate = '1'"
        
    return get_data(sql)
      