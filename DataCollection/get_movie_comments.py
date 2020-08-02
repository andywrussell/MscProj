#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Attempts to retrive comments from youtube, did not work due to API limits

Created on Tue May 19 11:03:38 2020

@author: andy
"""
from tqdm import tqdm
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time

import sys
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Utils')

import database_helper
from youtube_helper import YouTubeHelper


yt = YouTubeHelper().yt
trailers_df = database_helper.select_query("trailers")

#filter out this list of selected trailers
filter_ids = [95,103,81,93,89,36,239,71,30,41,14,80,70,350,59,65,64,110,124,368,372,123]
filtered_trailers = trailers_df[~trailers_df.id.isin(filter_ids)]

def custom_parser(json):
    snippet = json['snippet']['topLevelComment']['snippet']

    
    comment = {
        'commentId' : json['id'],
        'channelUrl' : '',
        'channelId' : '',
        'channelName' : '',
        'displayText' : '',
        'originalText' : '',
        'likeCount' : '',
        'publishDate' : '',
        'updateDate' : '',
        'replyCount' : '',
        'parentId' : 0
    }
    
    try:
        comment['channelUrl'] = snippet['authorChannelUrl']
    except:
        comment['channelUrl'] = ''
        
    try:
        comment['channelId'] = snippet['authorChannelId']['value']
    except:
        comment['channelId'] = ''
        
    try:
        comment['channelName'] = snippet['authorDisplayName']
    except:
        comment['channelName'] = ''
        
    try:
        comment['displayText'] = snippet['textDisplay']
    except:
        comment['displayText'] = ''
        
    try:
        comment['originalText'] = snippet['textOriginal']
    except:
        comment['originalText'] = ''
        
    try:
        comment['likeCount'] = snippet['likeCount']
    except:
        comment['likeCount'] = ''
        
    try:
        comment['publishDate'] = snippet['publishedAt']
    except:
        comment['publishDate'] = ''
        
    try:
        comment['updateDate'] = snippet['updatedAt']
    except:
        comment['updateDate'] = ''
        
    try:
        comment['replyCount'] = json['snippet']['totalReplyCount']
    except:
        comment['replyCount'] = ''


    return comment

def get_trailer_comments():
    with tqdm(total=len(filtered_trailers)) as pbar:
        for index, row in filtered_trailers.iterrows(): 
            tralier_comments = yt.get_video_comments(row['youtubeId'], parser = custom_parser, part=['snippet'])
            for comment in tralier_comments:
                insert_params = {
                        'trailerId' : row['id'],
                        'trailerYoutubeId' : row['youtubeId'],
                        'commentId' : comment['commentId'],
                        'channelUrl' : comment['channelUrl'],
                        'channelId' : comment['channelId'],
                        'channelName' : comment['channelName'],
                        'displayText' : comment['displayText'],
                        'originalText' : comment['originalText'],
                        'likeCount' : comment['likeCount'],
                        'publishDate' : comment['publishDate'],
                        'updateDate' : comment['updateDate'],
                        'replyCount' : comment['replyCount'],
                        'parentId' : comment['parentId']
                    }
                database_helper.insert_data("trailer_comments", insert_params)
                
            pbar.update(1)


def unpack_replies(comments):
    results = []
    for comment in comments:
        comment_obj = {
            'commentId' : comment['commentId'],
            'channelUrl' : comment['channelUrl'],
            'channelId' : comment['channelId'],
            'displayText' : comment['displayText'],
            'originalText' : comment['originalText'],
            'likeCount' : comment['likeCount'],
            'publishDate' : comment['publishDate'],
            'updateDate' : comment['updateDate'],
            'replyCount' : comment['replyCount'],
            'parentId' : comment['parentId']         
            }
        results.append(comment_obj)
        for reply in comment['replies']:
            results.append(reply)
            
    return results
    #get info from top level comment



    
