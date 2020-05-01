#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  1 14:49:05 2020

@author: andy
"""
from youtube_api import YouTubeDataAPI

class YouTubeHelper():
    api_key = 'AIzaSyBR2kc8R5EzD1rnOjyXZfEL1FOGLKojsg4'
    
    def __init__(self):
        self.yt = YouTubeDataAPI(self.api_key) 