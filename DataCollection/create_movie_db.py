#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 14:58:04 2020

@author: andy
"""

import psycopg2
import pandas as pd
import pandas.io.sql as sqlio
import glob
from os import listdir
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Utils')

import bfi_helper


#get full film set 
film_df = bfi_helper.get_raw_data()
film_df_sub = film_df[['Film', 'Country of Origin', 'Distributor']].drop_duplicates()

#create postgres connection 
try: 
    connection = psycopg2.connect(user="postgres",
                                  password="4ndr3wP0ST",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="geotweets")
    
    for index, row in film_df_sub.iterrows():      
        sql = """
        INSERT INTO movies(title, distributor, country) VALUES(%s, %s, %s);
        """
    
        cursor = connection.cursor()      
        cursor.execute(sql, (row['Film'], row['Distributor'], row['Country of Origin']))    
        connection.commit()
        cursor.close()
    
    
except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)
finally:
    #closing database connection.
        if(connection):
           # cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")