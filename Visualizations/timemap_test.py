#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 12 17:01:01 2020

@author: andy
"""

import imdb
from tqdm import tqdm
import pandas as pd
import sys
import re
import matplotlib.pyplot as plt
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Entities')
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Utils')

from movie import Movie
import database_helper
import movie_helper
import tweet_helper
import osmnx as ox
import geopandas as gpd
from geopandas.tools import sjoin
import seaborn as sns
import matplotlib.dates as mdates
import numpy as np
from colour import Color
import scipy.signal
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nameparser import HumanName
from datetime import datetime
from datetime import timedelta

movie = movie_helper.get_movie_by_id(28)

#start_date = datetime.combine((movie.ukReleaseDate - timedelta(days=14)), datetime.min.time())
#end_date = datetime.combine((movie.first_run_end - timedelta(days=14)), datetime.min.time())
start_date = None
end_date = None
   
tweets = database_helper.select_geo_tweets(movie.movieId, start_date, end_date)
tweets = tweets.sort_values(by=['created_at']).reset_index()
times = tweets['created_at']
times_tot_mins = 24*60 - (60*np.array([t.hour for t in times]) + np.array([t.minute for t in times]))

seps=np.array([(times[i]-times[i-1]).total_seconds() for i in range(1,len(times))])
seps[seps==0]=1 # convert zero second separations to 1-second separations

sep_array=np.zeros((len(seps)-1,2)) # 1st column: x-coords, 2nd column: y-coords
sep_array[:,0]=seps[:-1]
sep_array[:,1]=seps[1:]

Ncolors=24*60 

## set up color list
red=Color("red")
blue=Color("blue")
color_list = list(red.range_to(blue, Ncolors)) # range of colors evenly speced on the spectrum between red and blue. Each element is a colour object
color_list = [c.hex for c in color_list] # give hex version

fig=plt.figure()
ax =fig.add_subplot(111)

plt.rc('text',usetex=False)
plt.rc('font',family='serif')
 	
colormap = plt.cm.get_cmap('rainbow')  # see color maps at http://matplotlib.org/users/colormaps.html

order=np.argsort(times_tot_mins[1:-1]) # so that the red dots are on top
#	order=np.arange(1,len(times_tot_mins)-2) # dots are unsorted

sc= ax.scatter(sep_array[:,0][order],sep_array[:,1][order],c=times_tot_mins[1:-1][order],vmin=0,vmax=24*60,s=25,cmap=colormap,marker='o',edgecolors='none')
# taken from http://stackoverflow.com/questions/6063876/matplotlib-colorbar-for-scatter
 	
color_bar=fig.colorbar(sc,ticks=[0,24*15,24*30,24*45,24*60],orientation='horizontal',shrink=0.5)
color_bar.ax.set_xticklabels(['Midnight','18:00','Noon','6:00','Midnight'])
color_bar.ax.invert_xaxis()
color_bar.ax.tick_params(labelsize=16)
 	
ax.set_yscale('log') # logarithmic axes
ax.set_xscale('log')

plt.minorticks_off()
pure_ticks = np.array([1e-3,1,10,60*10,2*3600,1*24*3600, 7*24*3600]) # where the tick marks will be placed, in units of seconds.
labels = ['1 msec','1 sec','10 sec','10 min','2 hr','1 day','1 week']  # tick labels

max_val = np.max([np.max(sep_array[:,0]), np.max(sep_array[:,1])])
 	
ticks = np.hstack((pure_ticks, max_val))

min_val = np.min([np.min(sep_array[:,0]), np.min(sep_array[:,1])])
 	
plt.xticks(ticks,labels,fontsize=16)
plt.yticks(ticks,labels,fontsize=16)
 	
plt.xlabel('Time Before Tweet',fontsize=18)
plt.ylabel('Time After Tweet',fontsize=18)

plt.xlim((min_val, max_val))
plt.ylim((min_val, max_val))
 	
ax.set_aspect('equal')
plt.tight_layout()

plt.show()