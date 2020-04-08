#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 11:00:35 2020

@author: andy
"""

import psycopg2
import pandas as pd
import pandas.io.sql as sqlio
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import numpy as np


analyser = SentimentIntensityAnalyzer()

def sentiment_analyzer_scores(sentence):
    score = analyser.polarity_scores(sentence)
    print("{:-<40} {}".format(sentence, str(score)))
    
    
try:
    connection = psycopg2.connect(user="postgres",
                                  password="4ndr3wP0ST",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="geotweets")

    
    endgame = "SELECT * FROM public.tweets2019 WHERE msg LIKE '%#AvengersEndgame%' or msg LIKE '%Avengers: Endgame%'"
    endgame_df = sqlio.read_sql_query(endgame, connection)
    
    lionKing = "SELECT * FROM public.tweets2019 WHERE msg LIKE '%#thelionking%' or msg LIKE '%#TheLionKing%' or msg LIKE '%Lion King%'"
    lionKing_df = sqlio.read_sql_query(lionKing, connection)
    
    toyStory4 = "SELECT * FROM public.tweets2019 WHERE msg LIKE '%#toystory4%' or msg LIKE '%#ToyStory4%' or msg LIKE '%Toy Story 4%'"
    toyStory4_df = sqlio.read_sql_query(toyStory4, connection)
    
    joker = "SELECT * FROM public.tweets2019 WHERE msg LIKE '%#joker%' or msg LIKE '%#Joker%' or msg LIKE '%Joker%' or msg LIKE '%#jokermovie%' or msg LIKE '%#JokerMovie%' or msg LIKE '%Joker Movie%'or msg LIKE '%#thejoker%' or msg LIKE '%#TheJoker%' or msg LIKE '%The Joker%'"
    joker_df = sqlio.read_sql_query(joker, connection)
    
    starwars = "SELECT * FROM public.tweets2019 WHERE msg LIKE '%#TheRiseOfSkywalker%' or msg LIKE '%#theriseofskywalker%' or msg LIKE '%The Rise of Skywalker%' or msg LIKE '%#StarWars%' or msg LIKE '%#starwars%' or msg LIKE '%Star Wars: The Rise of Skywalker%'"
    starwars_df = sqlio.read_sql_query(starwars, connection)
    
    frozen2 = "SELECT * FROM public.tweets2019 WHERE msg LIKE '%#Frozen2%' or msg LIKE '%#frozen2%' or msg LIKE '%Frozen 2%' or msg LIKE '%frozen 2%'"
    frozen2_df = sqlio.read_sql_query(frozen2, connection)
    
    captainMarvel = "SELECT * FROM public.tweets2019 WHERE msg LIKE '%#CaptainMarvel%' or msg LIKE '%#captainmarvel%' or msg LIKE '%Captain Marvel%' or msg LIKE '%captain marvel%'"
    captainMarvel_df = sqlio.read_sql_query(captainMarvel, connection)
    
    aladdin = "SELECT * FROM public.tweets2019 WHERE msg LIKE '%#Aladdin%' or msg LIKE '%#aladdin%' or msg LIKE '%Aladdin%'"
    aladdin_df = sqlio.read_sql_query(aladdin, connection)   

    spidermanfarfromhome = "SELECT * FROM public.tweets2019 WHERE msg LIKE '%#SpiderManFarFromHome%' or msg LIKE '%#spidermanfarfromhome%' or msg LIKE '%SpiderMan Far From Home%' or msg LIKE '%spiderman far from home%'"
    spidermanfarfromhome_df = sqlio.read_sql_query(spidermanfarfromhome, connection) 
    
    jumanji = "SELECT * FROM public.tweets2019 WHERE msg LIKE '%#jumaji%' or msg LIKE '#Jumanji' or msg LIKE '#jumanjithenextlevel'or msg LIKE '#JumanjiTheNextLevel' or msg LIKE '%Jumanji the Next Level%'or msg LIKE '%jumanji the next level%' or msg LIKE '%Jumanji%'"
    jumanji_df = sqlio.read_sql_query(jumanji, connection)     

except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)
finally:
    #closing database connection.
        if(connection):
           # cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")