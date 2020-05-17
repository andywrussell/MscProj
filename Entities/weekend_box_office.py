#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 17 13:52:27 2020

@author: andy
"""

class WeekendBoxOffice():
    def __init__(self, db_row):
        self.id = db_row.id
        self.movieId = db_row.movieId
        self.weeks_on_release = db_row.weeksOnRelease
        self.no_of_cinemas = db_row.noOfcinemas
        self.weekend_gross = db_row.weekendGross
        self.percentage_change = db_row.percentageChange
        self.site_average = db_row.siteAverage
        self.gross_to_date = db_row.grossToDate
        self.weekend_start = db_row.weekendStart
        self.weekend_end = db_row.weekendEnd
        self.rank = db_row.rank