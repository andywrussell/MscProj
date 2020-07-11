#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  8 09:12:03 2020

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
import exploration


def define_success():
    #get box plots 
    exploration.plot_financial_box("budget_usd", "Budget Box Plot",  "Budget ($mil)")
    exploration.plot_financial_distribution("budget_usd", "Budget Distribution", "Budget ($mil)")
    
    exploration.plot_financial_box("gross_profit_usd", "Profit Box Plot", "Profit ($mil)")
    exploration.plot_financial_distribution("gross_profit_usd", "Profit Distribution", "Profit ($mil)")
    
    exploration.plot_financial_box("uk_gross_usd", "UK Takings Box Plot", "UK Gross ($mil)")
    exploration.plot_financial_distribution("uk_gross_usd", "UK Takings Distribution", "Uk Gross ($mil)")
    
    exploration.plot_float_box("return_percentage", "Return On Investment Box Plot", "Return Percentage")
    exploration.plot_float_distribution("return_percentage", "Return On Investment Distribution", "Return Percentage")
    
    exploration.plot_float_box("uk_percentage", "Percentage Takings in UK", "Percentage of Takings in UK")
    exploration.plot_float_distribution("uk_percentage", "Percentage Takings in UK Distribution", "Percentage of Takings in UK")
    
    #plot classes 
    exploration.plot_profit_classes()
    exploration.plot_return_classes()
    exploration.plot_uk_classes()
    
    #get bar distributions
    
def twitter_exploration():
    
    exploration.gen_top_20_tweet_count()
    exploration.gen_bottom_20_tweet_count()
    
    #tweets vs budget 
    exploration.plot_tweets_vs_finance("budget_usd", "Tweets vs Budget", "Budget ($mil)", "Tweets", logx=True)
    #tweets vs profit
    exploration.plot_tweets_vs_finance("gross_profit_usd", "Tweets vs Profit", "Profit ($mil)", "Tweets", logx=True)
    #tweets vs uk
    exploration.plot_tweets_vs_ratio("uk_percentage", "Tweets vs UK Revenue", "UK Percentage", "Tweets")
    #tweets vs return
    exploration.plot_tweets_vs_ratio("return_percentage", "Tweets vs Return", "Return Percentage", "Tweets")
    
    