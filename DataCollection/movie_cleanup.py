#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 12 15:23:18 2020

@author: andy
"""

import imdb
from tqdm import tqdm
import pandas as pd
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Utils')

import database_helper


#initialize imdb 
ia = imdb.IMDb()

#greta
greta = database_helper.select_query("movies", { "movieId" : 234 })
greta = greta.iloc[0]

greta_res = ia.get_movie('2639336')
year = greta_res['year']
if (greta_res.get('genres')):     
    genres = ','.join(greta_res.get('genres'))  
rating = greta_res.get('rating')
votes = greta_res.get('votes')
certificates = None
if (greta_res.get('certificates')):     
    certificates = ','.join(greta_res.get('certificates'))
                
#update database
update_params = {
    "imdbId": '2639336',
    "url" : 'https://www.imdb.com/title/tt2639336/',
    "year" : year,
    "genres" : genres,
    "rating" : rating,
    "votes" : votes,
    "certificates" : certificates
    }
select_params = { "movieId" : int(greta["movieId"]) }
database_helper.update_data("movies", update_params = update_params, select_params = select_params)



#"Kobiety Mafii 2"
# kobiety_mafii = database_helper.select_query("movies", { "movieId" : 262 })
# kobiety_mafii = kobiety_mafii.iloc[0]

# kobiety_mafii_res = ia.get_movie('8858420')
# year = kobiety_mafii_res['year']
# if (kobiety_mafii_res.get('genres')):     
#     genres = ','.join(kobiety_mafii_res.get('genres'))  
# rating = kobiety_mafii_res.get('rating')
# votes = kobiety_mafii_res.get('votes')
# certificates = None
# if (kobiety_mafii_res.get('certificates')):     
#     certificates = ','.join(kobiety_mafii_res.get('certificates'))
                
# #update database
# update_params = {
#     "imdbId": '8858420',
#     "url" : 'https://www.imdb.com/title/tt8858420/',
#     "year" : year,
#     "genres" : genres,
#     "rating" : rating,
#     "votes" : votes,
#     "certificates" : certificates
#     }
# select_params = { "movieId" : int(kobiety_mafii["movieId"]) }
# database_helper.update_data("movies", update_params = update_params, select_params = select_params)


#fix out of the blue 
# out_of_the_blue = database_helper.select_query("movies", { "movieId" : 143 })
# out_of_the_blue = out_of_the_blue.iloc[0]

# out_of_the_blue_res = ia.get_movie('6874254')
# year = out_of_the_blue_res['year']
# if (out_of_the_blue_res.get('genres')):     
#     genres = ','.join(out_of_the_blue_res.get('genres'))  
# rating = out_of_the_blue_res.get('rating')
# votes = out_of_the_blue_res.get('votes')
# certificates = None
# if (out_of_the_blue_res.get('certificates')):     
#     certificates = ','.join(out_of_the_blue_res.get('certificates'))
                
# #update database
# update_params = {
#     "imdbId": '6874254',
#     "url" : 'https://www.imdb.com/title/tt6874254/',
#     "year" : year,
#     "genres" : genres,
#     "rating" : rating,
#     "votes" : votes,
#     "certificates" : certificates
#     }
# select_params = { "movieId" : int(out_of_the_blue["movieId"]) }
# database_helper.update_data("movies", update_params = update_params, select_params = select_params)


#fix the white crow
# the_white_crow = database_helper.select_query("movies", { "movieId" : 137 })
# the_white_crow = the_white_crow.iloc[0]

# the_white_crow_res = ia.get_movie('5460858')
# year = the_white_crow_res['year']
# if (the_white_crow_res.get('genres')):     
#     genres = ','.join(the_white_crow_res.get('genres'))  
# rating = the_white_crow_res.get('rating')
# votes = the_white_crow_res.get('votes')
# certificates = None
# if (the_white_crow_res.get('certificates')):     
#     certificates = ','.join(the_white_crow_res.get('certificates'))
                
# #update database
# update_params = {
#     "imdbId": '5460858',
#     "url" : 'https://www.imdb.com/title/tt5460858/',
#     "year" : year,
#     "genres" : genres,
#     "rating" : rating,
#     "votes" : votes,
#     "certificates" : certificates
#     }
# select_params = { "movieId" : int(the_white_crow["movieId"]) }
# database_helper.update_data("movies", update_params = update_params, select_params = select_params)


#fix the favourite
#63
# the_favourite = database_helper.select_query("movies", { "movieId" : 63 })
# the_favourite = the_favourite.iloc[0]

# the_favourite_res = ia.get_movie('5083738')
# year = the_favourite_res['year']
# if (the_favourite_res.get('genres')):     
#     genres = ','.join(the_favourite_res.get('genres'))  
# rating = the_favourite_res.get('rating')
# votes = the_favourite_res.get('votes')
# certificates = None
# if (the_favourite_res.get('certificates')):     
#     certificates = ','.join(the_favourite_res.get('certificates'))
                
# #update database
# update_params = {
#     "imdbId": '5083738',
#     "url" : 'https://www.imdb.com/title/tt5083738/',
#     "year" : year,
#     "genres" : genres,
#     "rating" : rating,
#     "votes" : votes,
#     "certificates" : certificates
#     }
# select_params = { "movieId" : int(the_favourite["movieId"]) }
# database_helper.update_data("movies", update_params = update_params, select_params = select_params)


#fix read joan
# read_joan = database_helper.select_query("movies", { "movieId" : 233 })
# read_joan = read_joan.iloc[0]

# read_joan_res = ia.get_movie('7615302')
# year = read_joan_res['year']
# if (read_joan_res.get('genres')):     
#     genres = ','.join(read_joan_res.get('genres'))  
# rating = read_joan_res.get('rating')
# votes = read_joan_res.get('votes')
# certificates = None
# if (read_joan_res.get('certificates')):     
#     certificates = ','.join(read_joan_res.get('certificates'))
                
# #update database
# update_params = {
#     "imdbId": '7615302',
#     "url" : 'https://www.imdb.com/title/tt7615302/',
#     "year" : year,
#     "genres" : genres,
#     "rating" : rating,
#     "votes" : votes,
#     "certificates" : certificates
#     }
# select_params = { "movieId" : int(read_joan["movieId"]) }
# database_helper.update_data("movies", update_params = update_params, select_params = select_params)


#fix beautiful boy
# beautiful_boy = database_helper.select_query("movies", { "movieId" : 85 })
# beautiful_boy = beautiful_boy.iloc[0]

# beautiful_boy_res = ia.get_movie('1226837')
# year = beautiful_boy_res['year']
# if (beautiful_boy_res.get('genres')):     
#     genres = ','.join(beautiful_boy_res.get('genres'))  
# rating = beautiful_boy_res.get('rating')
# votes = beautiful_boy_res.get('votes')
# certificates = None
# if (beautiful_boy_res.get('certificates')):     
#     certificates = ','.join(beautiful_boy_res.get('certificates'))
                
# #update database
# update_params = {
#     "imdbId": '1226837',
#     "url" : 'https://www.imdb.com/title/tt1226837/',
#     "year" : year,
#     "genres" : genres,
#     "rating" : rating,
#     "votes" : votes,
#     "certificates" : certificates
#     }
# select_params = { "movieId" : int(beautiful_boy["movieId"]) }
# database_helper.update_data("movies", update_params = update_params, select_params = select_params)


#fix amazing grace
# paw_patrol = database_helper.select_query("movies", { "movieId" : 122 })
# paw_patrol = paw_patrol.iloc[0]

# paw_patrol_res = ia.get_movie('6889128')
# year = paw_patrol_res['year']
# if (paw_patrol_res.get('genres')):     
#     genres = ','.join(paw_patrol_res.get('genres'))  
# rating = paw_patrol_res.get('rating')
# votes = paw_patrol_res.get('votes')
# certificates = None
# if (paw_patrol_res.get('certificates')):     
#     certificates = ','.join(paw_patrol_res.get('certificates'))
                
# #update database
# update_params = {
#     "imdbId": '6889128',
#     "url" : 'https://www.imdb.com/title/tt6889128/',
#     "year" : year,
#     "genres" : genres,
#     "rating" : rating,
#     "votes" : votes,
#     "certificates" : certificates
#     }
# select_params = { "movieId" : int(paw_patrol["movieId"]) }
# database_helper.update_data("movies", update_params = update_params, select_params = select_params)


# #fix amazing grace
# amazing_grace = database_helper.select_query("movies", { "movieId" : 128 })
# amazing_grace = amazing_grace.iloc[0]

# amazing_grace_res = ia.get_movie('4935462')
# year = amazing_grace_res['year']
# if (amazing_grace_res.get('genres')):     
#     genres = ','.join(amazing_grace_res.get('genres'))  
# rating = amazing_grace_res.get('rating')
# votes = amazing_grace_res.get('votes')
# certificates = None
# if (amazing_grace_res.get('certificates')):     
#     certificates = ','.join(amazing_grace_res.get('certificates'))
                
# #update database
# update_params = {
#     "imdbId": '4935462',
#     "url" : 'https://www.imdb.com/title/tt4935462/',
#     "year" : year,
#     "genres" : genres,
#     "rating" : rating,
#     "votes" : votes,
#     "certificates" : certificates
#     }
# select_params = { "movieId" : int(amazing_grace["movieId"]) }
# database_helper.update_data("movies", update_params = update_params, select_params = select_params)
            


#fix the grinch
# grinch = database_helper.select_query("movies", { "movieId" : 72 })
# grinch = grinch.iloc[0]

# grinch_res = ia.get_movie('2709692')
# year = grinch_res['year']
# if (grinch_res.get('genres')):     
#     genres = ','.join(grinch_res.get('genres'))  
# rating = grinch_res.get('rating')
# votes = grinch_res.get('votes')
# certificates = None
# if (grinch_res.get('certificates')):     
#     certificates = ','.join(grinch_res.get('certificates'))
                
# #update database
# update_params = {
#     "imdbId": '2709692',
#     "url" : 'https://www.imdb.com/title/tt2709692/',
#     "year" : year,
#     "genres" : genres,
#     "rating" : rating,
#     "votes" : votes,
#     "certificates" : certificates
#     }
# select_params = { "movieId" : int(grinch["movieId"]) }
# database_helper.update_data("movies", update_params = update_params, select_params = select_params)
            


