#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Class definition for BoxOfficeMojo weekend box office object

Created on Sun Jul 12 10:09:52 2020

@author: andy
"""

class MojoWeekendBoxOffice():
    """
    Class definition for BoxOfficeMojo weekend box office object
    """
    
    def __init__(self, db_row):
        """
        MojoWeekendBoxOffice class constructor
        
        :param db_row: pandas series object corresponding to row from which object should be built
        """
        
        self.id = db_row.id
        self.movieid = db_row.movieid
        self.date = db_row.date
        self.rank = db_row.rank
        self.weekend_gross_usd = db_row.weekend_gross_usd
        self.percentage_change = db_row.percentage_change
        self.no_of_theatres = db_row.no_of_theatres
        self.average_per_theatre_usd = db_row.average_per_theatre_usd
        self.gross_to_date_usd = db_row.gross_to_date_usd
        self.weeks_on_release = db_row.weeks_on_release
        self.start_date = db_row.start_date
        self.end_date = db_row.end_date
        self.theatres_change = db_row.theatres_change