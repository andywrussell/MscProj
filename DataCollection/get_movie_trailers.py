#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 14:30:50 2020

@author: andy
"""

from tqdm import tqdm
import pandas as pd
import sys
import re
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Utils')

import database_helper
from youtube_helper import YouTubeHelper


#yt = YouTubeHelper().yt
movies_df = database_helper.select_query("movies")

def get_youtube_trailers():
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            title = re.sub(r"\s*\(.*\)\s*","", row["title"])
            title = re.sub(r'[^\w\s]','',title)
            print(title)
            # if (row['distributor']):
            #     try:
            #         yt_search = yt.search(q = title + " trailer", max_results=10, parser=None) 
            #         distributor_trailers = list(filter(lambda x : row['distributor'].lower() in x['snippet']['channelTitle'].lower(), yt_search))
                        
            #         if (len(distributor_trailers) > 0):
            #             #add trailers to db
            #             for trailer in distributor_trailers:
            #                 database_helper.insert_data("trailers", {"movieId" : row["movieId"], "youtubeId" : trailer['id']['videoId']})
            #         else:
            #             print("Couldnt find trailer for " + row["title"])
                        
            #     except Exception as error:
            #         print(error)
            pbar.update(1)

def load_trailers_from_csv():
    file_path = "../../ProjectData/trailers.csv"
    trailers_df = pd.read_csv(file_path)
    with tqdm(total=len(trailers_df)) as pbar:
        for index, row in trailers_df.iterrows():
            insert_pararms = {
                    "movieId" : row["movieId"],
                    "youtubeId" : row["youtubeId"],
                    "url" : row["url"],
                    "title" : row["title"],
                    "channelTitle" : row["channelTitle"]
                }
            database_helper.insert_data("trailers", insert_pararms)    
            pbar.update(1)


#get_youtube_trailers()
#load_trailers_from_csv()
