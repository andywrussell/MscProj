#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 14:30:50 2020

@author: andy
"""

from tqdm import tqdm
import pandas as pd
import sys
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Utils')

import database_helper
from youtube_helper import YouTubeHelper


yt = YouTubeHelper().yt
movies_df = database_helper.select_query("movies")

def get_youtube_trailers():
    with tqdm(total=len(movies_df)) as pbar:
        for index, row in movies_df.iterrows(): 
            if (row['distributor'] and not "/" in row["title"]):
               yt_search = yt.search(q = row["title"] + " trailer", max_results=10, parser=None) 
               distributor_trailers = list(filter(lambda x : row['distributor'].lower() in x['snippet']['channelTitle'].lower(), yt_search))
               if (len(distributor_trailers) > 0):
                   #add trailers to db
                   for trailer in distributor_trailers:
                       database_helper.insert_data("trailers", {"movieId" : row["movieId"], "youtubeId" : trailer['id']['videoId']})
               else:
                   print("Couldnt find trailer for " + row["title"])
            pbar.update(1)

get_youtube_trailers()

