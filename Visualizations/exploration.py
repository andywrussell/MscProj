#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 09:15:02 2020

@author: andy
"""

from tqdm import tqdm
import pandas as pd
import sys
import re
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Entities')
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Utils')

from movie import Movie
import database_helper
import movie_helper

#movie_helper.set_total_revenue_for_movies()

#movies = movie_helper.get_movies()

movies = movie_helper.get_top_earning()

#test = movies[90].plot_weekend_revenues()
#test = movies[0].box_office_df
#def get_revenue_for_top_20():
    