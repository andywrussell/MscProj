#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 14:27:00 2020

@author: andy
"""

import pandas as pd # data analysis
import requests # get url
from bs4 import BeautifulSoup as bs # data scraping
import matplotlib.pyplot as plt # Data visualisation 
import datetime # Check week number
import re


def get_movie_page(imdbId):
    html = 'http://www.boxofficemojo.com/title/tt{}'.format(imdbId)
    r = requests.get(html)  
    return r.content


def get_uk_url(imdbId):
    html = get_movie_page(imdbId)
    soup = bs(html, 'html.parser')
    uk_a_elem_lst = soup.find_all('a', href=True, text='United Kingdom')
    if len(uk_a_elem_lst) > 0:
        uk_a_elem = uk_a_elem_lst[0]
        uk_url = "http://www.boxofficemojo.com{0}".format(uk_a_elem['href'])
        return uk_url
    
    return None

def get_uk_page(imdbId):
    url = get_uk_url(imdbId)
    if not url == None:
        r = requests.get(url)  
        return r.content
    else:
        return None

def get_mojo_stats(imdbId):
    #get stats from main page
    main_html = get_movie_page(imdbId)
    main_soup = bs(main_html, 'html.parser')
    
    summary = main_soup.select('.mojo-summary-table')[0]
    gross_siblings = summary.select("span.a-size-small")
    
    stats = {"Worldwide" : None, 
             "Domestic" : None,
             "International" : None
             }
    
    for gross in gross_siblings:
        gross_text = gross.get_text().strip()
        if gross_text == "Worldwide":
            money_str_lst =  gross.find_next_siblings("span")
            if len(money_str_lst) > 0:             
                money_lst = money_str_lst[0].select(".money")
                if len(money_lst) > 0:
                    money_str = money_lst[0].get_text()
                    money = int(re.sub(r'[^0-9.]', '', money_str))
                    stats["Worldwide"] = money
            
        elif "Domestic" in gross_text:
            money_str_lst =  gross.find_next_siblings("span")
            if len(money_str_lst) > 0:             
                money_lst = money_str_lst[0].select(".money")
                if len(money_lst) > 0:
                    money_str = money_lst[0].get_text()
                    money = int(re.sub(r'[^0-9.]', '', money_str))
                    stats["Domestic"] = money
                
        elif "International" in gross_text:
            money_str_lst =  gross.find_next_siblings("span")
            if len(money_str_lst) > 0:             
                money_lst = money_str_lst[0].select(".money")
                if len(money_lst) > 0:
                    money_str = money_lst[0].get_text()
                    money = int(re.sub(r'[^0-9.]', '', money_str))
                    stats["International"] = money
        
    #go to uk page for other info
    uk_html = get_uk_page(imdbId)
    if not uk_html == None:
        uk_soup = bs(uk_html, 'html.parser')
        uk_summary = uk_soup.select('.mojo-summary-table')[0]
           
        uk_gross_siblings = uk_summary.select("span.a-size-small")
        for gross in uk_gross_siblings:
            gross_text = gross.get_text().strip()
            if gross_text == "United Kingdom":
                money_str = gross.find_next_siblings("span")[0].select(".money")[0].get_text()
                money = int(re.sub(r'[^0-9.]', '', money_str))
                stats["UK"] = money
    else:
        stats["UK"] = None
      
    #some movies dont have budgetinfo
    budget_search = summary.find_all("span", text="Budget")
    if len(budget_search) > 0:
        budget_str = budget_search[0].find_next_siblings("span")[0].get_text()
        budget = int(re.sub(r'[^0-9.]', '', budget_str))
        stats["Budget"] = budget
    else:
        stats["Budget"] = None
          
    return stats
