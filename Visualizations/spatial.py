#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 17:03:01 2020

@author: andy
"""

#http://darribas.org/gds_scipy16/ipynb_md/04_esda.html
#testing some spatial analysis techniques

import matplotlib.pyplot as plt
import pysal as ps
import pandas as pd
import numpy as np
import geopandas as gpd
from geopandas.tools import sjoin
import sys
import math
import matplotlib.colors as colors

sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Entities')
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Utils')

from movie import Movie
import database_helper

def calc_surface_expectation(total_pop, total_samp, square_pop, square_samp):
    obs = (total_pop/total_samp) * square_samp
    exp = square_pop
    
    surface = (obs - exp) / math.sqrt(exp)
    
    return surface


uk_fishnet = database_helper.get_geo_data("select * from uk_fishnet", "geombng")
uk_regions = database_helper.get_geo_data("select * from uk_regions", "geombng")

gb_fishnet = sjoin(uk_fishnet, uk_regions, how = 'inner')

tweets_fishnet_count = database_helper.select_query("tweets_fishnet_count")
total_tweets = tweets_fishnet_count['tweet_count'].sum()

avengers_tweets = database_helper.select_geo_tweets(121)
total_avengers = avengers_tweets.shape[0]

avengers_fishnet_tweets = sjoin(avengers_tweets, uk_fishnet, how='inner')

tweet_freq = avengers_fishnet_tweets.groupby('id_right').size().reset_index(name='counts')

expectation_nums = tweets_fishnet_count.merge(tweet_freq, how='left', left_on='cellid', right_on='id_right')
expectation_nums = expectation_nums.rename(columns={'counts' : 'movie_count'})
expectation_nums = expectation_nums.fillna(0)

expectation_nums['chi_sqrd'] = expectation_nums.apply(lambda row: calc_surface_expectation(total_tweets, total_avengers, row['tweet_count'], row['movie_count']) if row['id_right'] > 0 else 0, axis = 1)

uk_fishnet_merge = uk_fishnet.merge(expectation_nums, how='left', left_on='id', right_on='cellid')

uk_fishnet_merge = uk_fishnet_merge.drop(columns=['id_right', 'cellid'])
uk_fishnet_merge = uk_fishnet_merge.fillna(0)

gb_fishnet = sjoin(uk_fishnet_merge, uk_regions, how = 'inner')


#TODO LOOK AT SCALING FOR COLOR BAR
#pivot around value that is 
max_val = uk_fishnet_merge['chi_sqrd'].max()
min_val = uk_fishnet_merge['chi_sqrd'].min()


divnorm = colors.TwoSlopeNorm(vmin=-max_val, vcenter=0, vmax=abs(max_val))
cbar = plt.cm.ScalarMappable(norm=divnorm, cmap='RdBu_r')

fig, ax = plt.subplots(1,figsize=(9,9))

uk_fishnet_merge.plot(column='chi_sqrd', legend=False, cmap='RdBu_r', norm=divnorm, ax=ax, alpha=1)
uk_regions.plot(ax=ax, alpha=0.25, color='green')

fig.colorbar(cbar, ax=ax)
ax.set_axis_off()
plt.axis('equal')
plt.show()
plt.clf()
plt.cla()
plt.close()
