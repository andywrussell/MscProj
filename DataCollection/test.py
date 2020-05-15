#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 15 10:40:34 2020

@author: andy
"""
from tqdm import tqdm
import sys
import re
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Entities')
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Utils')

from movie import Movie
import database_helper

movies_df = database_helper.select_query("movies", {"enabled" : '1'})
movies = []
with tqdm(total=len(movies_df)) as pbar:
    for index, row in movies_df.iterrows(): 
        movies.append(Movie(row))
        pbar.update(1)




