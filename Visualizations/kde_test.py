#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 19:07:14 2020

@author: andy
"""

import matplotlib.pyplot as plt
import pysal as ps
import pandas as pd
import numpy as np
import geopandas as gpd
import geoplot as gplt

from geopandas.tools import sjoin
import sys
import math
import matplotlib.colors as colors
import seaborn as sns
from sklearn.neighbors import KernelDensity

sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Entities')
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Utils')

from movie import Movie
import database_helper
from mpl_toolkits.basemap import Basemap

# gb = gpd.read_file("../../ProjectData/Data/GB/european_region_region.shp")
    
# fig, ax = plt.subplots(1,figsize=(9,9))
# #remove any tweets without geometry info
# tweets = database_helper.select_geo_tweets(1)

# tweets.dropna(subset=["geombng"], inplace=True)
# gb_tweets = sjoin(tweets, gb, how='inner')
# gb_tweets["lat"] = gb_tweets["geombng"].y
# gb_tweets["lng"] = gb_tweets["geombng"].x

# gb.plot(ax=ax)

# test = sns.kdeplot(gb_tweets['lng'], gb_tweets['lat'], 
#             shade=True, shade_lowest=False, cmap='viridis',
#               ax=ax)


# ax.set_axis_off()
# plt.axis('equal')
# plt.title(self.title + " Tweet Density")
# plt.show()
# plt.clf()
# plt.cla()
# plt.close()

fig, ax = plt.subplots(1,figsize=(9,9))

gb = gpd.read_file("../../ProjectData/Data/GB/european_region_region.shp")
tweets = database_helper.select_geo_tweets(1)
tweets.dropna(subset=["geombng"], inplace=True) 

gb_tweets = sjoin(tweets, gb, how='inner')
gb_tweets["lat"] = gb_tweets["geombng"].y
gb_tweets["lng"] = gb_tweets["geombng"].x

grid = database_helper.select_uk_fishnet()
grid["minx"] = grid["geombng"].bounds.minx
grid["miny"] = grid["geombng"].bounds.miny
grid["maxx"] = grid["geombng"].bounds.maxx
grid["maxy"] = grid["geombng"].bounds.maxy

gb["minx"] = grid["geombng"].bounds.minx
gb["miny"] = grid["geombng"].bounds.miny
gb["maxx"] = grid["geombng"].bounds.maxx
gb["maxy"] = grid["geombng"].bounds.maxy

xmin = gb["minx"].min()
xmax = gb["maxx"].max()
ymin = gb["miny"].min()
ymax = gb["maxy"].max()

# xmin = gb_tweets["lng"].min()
# xmax = gb_tweets["lng"].max()
# ymin = gb_tweets["lat"].min()
# ymax = gb_tweets["lat"].max()

grid_size = 25000 #bng is in meteres

# x coordin#ates of the grid cells
xgrid = np.arange(xmin, xmax, 25000)
# y coordinates of the grid cells
ygrid = np.arange(ymin, ymax, 25000)

X, Y = np.meshgrid(xgrid[::5], ygrid[::5][::-1])

xy = np.vstack([Y.ravel(), X.ravel()]).T
xy *= np.pi / 180.

Xtrain = np.vstack([gb_tweets["lat"],
                    gb_tweets["lng"]]).T

Xtrain *= np.pi / 180.

kde = KernelDensity(bandwidth=0.04, metric='haversine',
                        kernel='gaussian', algorithm='ball_tree')
kde.fit(Xtrain)

Z = kde.score_samples(xy)
Z = Z.reshape(X.shape)

#Z = np.exp(np.exp(kde.score_samples(xy)))
#Z = Z.reshape(X.shape)

#Z = np.full(gb.shape[0], -9999, dtype='int')
Z = np.exp(kde.score_samples(xy))
Z = Z.reshape(X.shape)

levels = np.linspace(0, Z.max(), 25)
gb.plot(ax=ax)
ax.contourf(X, Y, Z, cmap='Reds')

