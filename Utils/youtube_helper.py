#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  1 14:49:05 2020

@author: andy
"""
from youtube_api import YouTubeDataAPI

class YouTubeHelper():
    api_key = 'AIzaSyB47ZBBrFZ-17oIXxLWdsQgPIsXRQ1bjNo'
    
    def __init__(self):
        self.yt = YouTubeDataAPI(self.api_key) 