#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
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
trailers_df = database_helper.select_query("trailers",)

def custom_parser(json):
    snippet = json['snippet']['topLevelComment']['snippet']
    # replies = []
    # if (json['snippet']['totalReplyCount'] > 0):
    #     print (json['id'] + " - " + str(json['snippet']['totalReplyCount']) + str(len(json['replies'])))
    #     replies = []
    #     for reply in json['replies']['comments']: 
    #         reply_obj = {
    #             'commentId' : reply['id'],
    #             'channelUrl' : reply['snippet']['authorChannelUrl'],
    #             'channelId' : reply['snippet']['authorChannelId']['value'],
    #             'authorName' : reply['snippet']['authorDisplayName'],
    #             'displayText' : reply['snippet']['textDisplay'],
    #             'originalText' : reply['snippet']['textOriginal'],
    #             'likeCount' : reply['snippet']['likeCount'],
    #             'publishDate' : reply['snippet']['publishedAt'],
    #             'updateDate' : reply['snippet']['updatedAt'],
    #             'parentId' : reply['snippet']['parentId']
    #             }
    #         replies.append(reply_obj)    
    
    # comment = {
    #     'commentId' : json['id'],
    #     'channelUrl' : snippet['authorChannelUrl'],
    #     'channelId' : snippet['authorChannelId']['value'],
    #     'channelName' : snippet['authorDisplayName'],
    #     'displayText' : snippet['textDisplay'],
    #     'originalText' : snippet['textOriginal'],
    #     'likeCount' : snippet['likeCount'],
    #     'publishDate' : snippet['publishedAt'],
    #     'updateDate' : snippet['updatedAt'],
    #     'replyCount' : json['snippet']['totalReplyCount'],
    #     'parentId' : 0
    # }
    
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
    with tqdm(total=len(trailers_df)) as pbar:
        for index, row in trailers_df.iterrows(): 
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

get_trailer_comments()

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

# test = yt.get_video_comments('TTOiVivEmwo', parser = custom_parser, part=['snippet','replies'])
# test_full = unpack_replies(test)

# driver = webdriver.Chrome(ChromeDriverManager().install())

# driver.get('https://www.youtube.com/watch?v=P6AaSMfXHbA')
# time.sleep(5)


# SCROLL_PAUSE_TIME = 4
# CYCLES = 100
# #window_pos = driver.get_window_position()['y']
# html = driver.find_element_by_tag_name('html')
# html.send_keys(Keys.PAGE_DOWN)  
# html.send_keys(Keys.PAGE_DOWN)  
# time.sleep(SCROLL_PAUSE_TIME * 3)
# window_pos = driver.execute_script('return window.pageYOffset;')


# stop_scrolling = False
# while(not stop_scrolling):
#     html.send_keys(Keys.END)
#     #html.send_keys(Keys.PAGE_DOWN)  
#     #html.send_keys(Keys.PAGE_DOWN)      
#     time.sleep(SCROLL_PAUSE_TIME)
#     new_pos = driver.execute_script('return window.pageYOffset;')
#     stop_scrolling =  window_pos == new_pos
#     print(window_pos)
#     print(new_pos)
#     window_pos = new_pos

# driver.execute_script('window.scrollTo(1, 500);')

# #now wait let load the comments
# time.sleep(5)

# driver.execute_script('window.scrollTo(1, 5000);')

# time.sleep(5)

# driver.execute_script('window.scrollTo(1, 5500);')

# time.sleep(5)



# comment_div=driver.find_element_by_xpath('//*[@id="contents"]')
# comments=comment_div.find_elements_by_xpath('//*[@id="comment"]')
# # for comment in comments:
# #     author_elm = comment.find_elements_by_xpath('//*[@id="author"]')
# #     author = author_elm.text
    
# #     print(comment.text)

# comment = comments[22]
# author_elm = comment.find_element_by_id('author-text')
# author = author_elm.text
# authorlink = author_elm.get_attribute('href')
# comment_text = comment.text
# like_count = comment.find_element_by_id('vote-count-middle').text
# date = comment.find_element_by_class_name('published-time-text').text


    
