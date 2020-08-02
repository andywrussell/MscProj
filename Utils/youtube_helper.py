#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wrapper class and helper functions for the YouTube API

Created on Fri May  1 14:49:05 2020

@author: andy
"""
from youtube_api import YouTubeDataAPI
import dateutil.parser


class YouTubeHelper():
    api_key = 'AIzaSyB47ZBBrFZ-17oIXxLWdsQgPIsXRQ1bjNo'
    
    def __init__(self):
        self.yt = YouTubeDataAPI(self.api_key) 
        


def custom_parser(var):
    return var

        
def get_trailer_release(video_id, yt):
    """Custom function to retreive release dates from API (YouTubeDataAPI is broken)"""
    trailer_data = yt.get_video_metadata(video_id, parser=custom_parser)
    date_string = trailer_data['snippet']['publishedAt']
    publish_date = dateutil.parser.parse(trailer_data['snippet']['publishedAt'])
    
    return publish_date