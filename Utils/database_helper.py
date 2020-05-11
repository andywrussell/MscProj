#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 12:20:34 2020

@author: andy
"""
import pandas.io.sql as sqlio
import psycopg2

def run_query(sql, params):
    """
    Create a connection to the database and execute query
    
    :param sql: string contating sql query
    :param params: tuple containing query parameters
    """
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
    """
    Fetch data from the database and return as pandas dataframe
    
    :param sql: string contating sql query
    :param q_params: dictionary of query parameters
    :return pandas dataframe of query results
    """
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
