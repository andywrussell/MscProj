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
import scipy.ndimage as ndi

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

seps = seps.astype(int)

sep_array=np.zeros((len(seps)-1,2)) # 1st column: x-coords, 2nd column: y-coords
sep_array[:,0]=seps[:-1]
sep_array[:,1]=seps[1:]

sep_array = sep_array.astype(int)

Ncolors=24*60 

Nside=4*256 # number of pixels along the x and y directions
width=4 # the number of pixels that specifies the width of the Gaussians for the Gaussian filter

# choose points within specified range. Example plot separations greater than 5 minutes:
#	indices = (sep_array[:,0]>5*60) & (sep_array[:,1]>5*60)
indices=range(sep_array.shape[0]) # all time separations

x_pts = np.log(sep_array[indices,0])
y_pts = np.log(sep_array[indices,1])



#x_pts = sep_array[indices,0]
#y_pts = sep_array[indices,1]

min_val = np.min([np.min(x_pts), np.min(y_pts)])
   	
x_pts = x_pts - min_val
y_pts = y_pts - min_val
   	
max_val = np.max([np.max(x_pts), np.max(y_pts)])
   	
x_pts = x_pts * (Nside-1)/max_val
y_pts = y_pts * (Nside-1)/max_val
   	
img=np.zeros((Nside,Nside))
   
for i in range(len(x_pts)):
    img[int(x_pts[i]),int(y_pts[i])] +=1
   
img = ndi.gaussian_filter(img,width) # apply Gaussian filter
img = np.sqrt(img) # taking the square root makes the lower values more visible
img=np.transpose(img) # needed so the orientation is the same as scatterplot
   
plt.imshow(img, origin='lower')
   	
## create custom tick marks. Calculate positions of tick marks on the transformed log scale of the image array
plt.minorticks_off()
   	
## change font, which can also now accept latex: http://matplotlib.org/users/usetex.html
plt.rc('text',usetex=False)
plt.rc('font',family='serif')
   
my_max = np.max([np.max(sep_array[indices,0]), np.max(sep_array[indices,1])])
my_min = np.max([np.min(sep_array[indices,0]), np.min(sep_array[indices,1])])

pure_ticks = np.array([1e-3,1,10,60*10,2*3600,1*24*3600, 7*24*3600]) 
# where the tick marks will be placed, in units of seconds. An additional value will be appended to the end for the max
labels = ['1 msec','1 sec','10 sec','10 min','2 hr','1 day','1 week']  # tick labels
   
index_lower=np.min(np.nonzero(pure_ticks >= my_min)) 
# index of minimum tick that is greater than or equal to the smallest time interval. This will be the first tick with a non-blank label
   
index_upper=np.max(np.nonzero(pure_ticks <= my_max))
# similar to index_lower, but for upperbound
   	
ticks = pure_ticks[index_lower: index_upper + 1]
ticks = np.log(np.hstack((my_min, ticks, my_max ))) # append values to beginning and end in order to specify the limits
ticks = ticks - min_val
ticks *= (Nside-1)/(max_val)
   	
labels= np.hstack(('',labels[index_lower:index_upper + 1],'')) # append blank labels to beginning and end
plt.xticks(ticks, labels,fontsize=16)
plt.yticks(ticks, labels,fontsize=16)
plt.xlabel('Time Before Tweet',fontsize=18)
plt.ylabel('Time After Tweet' ,fontsize=18)
plt.show()
 	
