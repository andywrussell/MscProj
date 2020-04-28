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


#Get list of folders for each month
folder_names = listdir("../../ProjectData/BFI/2019/") 


film_df = pd.DataFrame()

#read all raw data files in each folder 
for folder in folder_names:
    folder_path = "../../ProjectData/BFI/2019/" + folder + "/Raw/*.xls"
    month_files = glob.glob(folder_path)
    
    for file in month_files:
        data = pd.read_excel(file)
        film_df = pd.concat([film_df, data])
        

#extract unique films      
film_df_sub = film_df[['Film', 'Country of Origin', 'Distributor']].drop_duplicates()

#create postgres connection 
try: 
    connection = psycopg2.connect(user="postgres",
                                  password="4ndr3wP0ST",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="geotweets")
    
    
    
except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)
finally:
    #closing database connection.
        if(connection):
           # cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")