#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Class definition for movie Trailers object

Created on Fri May 15 16:02:55 2020

@author: andy
"""

class Trailer():
    """
    Class definition for movie Trailers object
    """
    
    def __init__(self, db_row):
        """
        Trailer box office class constructor
        
        :param db_row: pandas series object corresponding to row from which object should be built
        """
        self.trailerId = db_row.id
        self.movieId = db_row.movieId
        self.youtubeId = db_row.youtubeId
        self.url = db_row.url
        self.title = db_row.title
        self.channel_title = db_row.channelTitle
        self.channelId = db_row.channelId
        self.categoryId = db_row.categoryId
        self.comment_count = db_row.commentCount
        self.description = db_row.description
        self.like_count = db_row.likeCount
        self.dislike_count = db_row.dislikeCount
        self.view_count = db_row.viewCount
        self.publish_date = db_row.publishDate
        self.tags = db_row.tags