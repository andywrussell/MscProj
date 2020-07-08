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
    exploration.plot_financial_box("budget_usd", "Budget Distribution", "Budget ($mil)")
    exploration.plot_financial_distribution("budget_usd", "Budget Distribution", "Budget ($mil)")
    
    exploration.plot_financial_box("gross_profit_usd", "Profit Distribution", "Profit ($mil)")
    exploration.plot_financial_distribution("gross_profit_usd", "Profit Distribution", "Profit ($mil)")
    
    exploration.plot_financial_box("uk_gross_usd", "UK Takings Distribution", "Profit ($mil)")
    exploration.plot_financial_distribution("uk_gross_usd", "UK Takings Distribution", "Profit ($mil)")
    
    exploration.plot_float_box("return_percentage", "Return On Investment Distribution", "Return Percentage")
    exploration.plot_float_distribution("return_percentage", "Return On Investment Distribution", "Return Percentage")
    
    exploration.plot_float_box("uk_percentage", "Percentage Takings in UK", "Percentage of Takings in UK")
    exploration.plot_float_distribution("uk_percentage", "Percentage Takings in UK", "Percentage of Takings in UK")
    
    #plot classes 
    exploration.plot_profit_classes()
    exploration.plot_return_classes()
    exploration.plot_uk_classes()
    
    #get bar distributions
    
def twitter_exploration():
    
    exploration.gen_top_20_tweet_count()
    exploration.gen_bottom_20_tweet_count()