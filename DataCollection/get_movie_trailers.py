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
#from youtube_helper import YouTubeHelper
import youtube_helper


yt = youtube_helper.YouTubeHelper().yt
movies_df = database_helper.select_query("movies")

def get_youtube_trailers():
    """
    Use this to collect movie trailers from yotube (INCOMPLETE)
    """
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
    """
    Load manually collected movie trailers into datbase
    """
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

def get_trailer_metadata():
    """
    Use youtubeId to collect trailer metadata
    """
    trailers_df = database_helper.select_query("trailers")
    with tqdm(total=len(trailers_df)) as pbar:
        for index, row in trailers_df.iterrows():
            trailer_data = yt.get_video_metadata(row['youtubeId'])
            update_params = {
                'title' : trailer_data['video_title'],
                'channelTitle' : trailer_data['channel_title'],
                'channelId' : trailer_data['channel_id'],
                'categoryId' : trailer_data['video_category'],
                'commentCount' : trailer_data['video_comment_count'],
                'description' : trailer_data['video_description'],
                'likeCount' : trailer_data['video_like_count'],
                'dislikeCount' : trailer_data['video_dislike_count'],
                'viewCount' : trailer_data['video_view_count'],
                'publishDate' : trailer_data['video_publish_date'],
                'tags' : trailer_data['video_tags']
            }
            select_params = {"youtubeId" : row["youtubeId"]}
            database_helper.update_data("trailers", update_params = update_params, select_params = select_params)
            pbar.update(1)
    
def get_trailer_release_dates():
    trailers_df = database_helper.select_query("trailers")
    with tqdm(total=len(trailers_df)) as pbar:
        for index, row in trailers_df.iterrows():  
            trailer_date = youtube_helper.get_trailer_release(row['youtubeId'], yt)
            
            update_params = { 'publishDate' : trailer_date }
            select_params = {"youtubeId" : row["youtubeId"]}
            
            database_helper.update_data("trailers", update_params = update_params, select_params = select_params)
            pbar.update(1)

def get_hashtags_from_trailers():
   trailers_df = database_helper.select_query("trailers")
   with tqdm(total=len(trailers_df)) as pbar:
       for index, row in trailers_df.iterrows():
           if ('#' in row.description):
               hashtags = re.findall(r"#(\w+)", row.description)
               print(row.title)
               print(hashtags)
           pbar.update(1)
#test = yt.get_video_metadata('XvHSlHhh1gk')
#get_trailer_metadata()
#get_youtube_trailers()
#load_trailers_from_csv()
#get_hashtags_from_trailers()
#get_trailer_metadata()

            
