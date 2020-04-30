#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 12:20:34 2020

@author: andy
"""
import pandas.io.sql as sqlio
import psycopg2

def run_query(sql, params):
    try: 
        connection = psycopg2.connect(user="postgres",
                                      password="4ndr3wP0ST",
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
    try: 
        connection = psycopg2.connect(user="postgres",
                                      password="4ndr3wP0ST",
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
                
def select_query(table, params = None, where_operator = "AND"):
    sql = "SELECT * FROM public." + table
    if (params):
        sql += " WHERE "
        for key in params:
            sql += '"{0}" = %({0})s'.format(key)
            if (key != list(params.keys())[-1]):
                sql += " {0} ".format(where_operator)
                
    return get_data(sql, params)

def insert_data(table, params):
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
            
