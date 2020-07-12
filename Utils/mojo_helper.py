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
from datetime import datetime


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

def get_uk_box_office_df(imdbId):
    uk_html = get_uk_page(imdbId)
    uk_soup = bs(uk_html, 'html.parser')
    div = uk_soup.select('.imdb-scroll-table-inner')[0]
    tables = div.find_all('table')
    
    box_office_df = pd.read_html(str(tables[0]))[0]
    box_office_df["start_date"] = box_office_df.apply(lambda row: get_start_date(row['Date']), axis = 1)
    box_office_df["end_date"] = box_office_df.apply(lambda row: get_end_date(row['Date']), axis = 1)

    
    prev_start = box_office_df.iloc[0]["start_date"]
    prev_end = box_office_df.iloc[0]["end_date"]
    fix_remaining = False
    
    for index, row in box_office_df.iterrows(): 
        if index > 0:
            curr_start = row["start_date"]
            curr_end = row["end_date"]
        
            if (prev_start.month > curr_start.month) or fix_remaining:
                new_start = row["start_date"].replace(year=2020)
                box_office_df.loc[index, "start_date"] = new_start
                fix_remaining = True
                
            if (prev_end.month > curr_end.month) or fix_remaining:
                new_end = row["end_date"].replace(year=2020)
                box_office_df.loc[index, "end_date"] = new_end
                fix_remaining = True
                
            prev_start = row["start_date"]
            prev_end = row["end_date"]
                
    box_office_df = box_office_df.rename(columns = {"Date" : "date",
                                    "Rank" : "rank",
                                    "Weekend" : "weekend_gross_usd",
                                    "%± LW" : "percentage_change",
                                    "Theaters" : "no_of_theatres",
                                    "Change" : "theatres_change",
                                    "Avg" : "average_per_theatre_usd",
                                    "To Date" : "gross_to_date_usd", 
                                    "Weekend.1" : "weeks_on_release" })
    
    box_office_df["weekend_gross_usd"] = box_office_df.apply(lambda row: try_convert_money(row["weekend_gross_usd"]), axis = 1)
    box_office_df["average_per_theatre_usd"] = box_office_df.apply(lambda row: try_convert_money(row["average_per_theatre_usd"]), axis = 1)
    box_office_df["gross_to_date_usd"] = box_office_df.apply(lambda row: try_convert_money(row["gross_to_date_usd"]), axis = 1)
    box_office_df["no_of_theatres"] = box_office_df.apply(lambda row: try_convert_int(row["no_of_theatres"]), axis = 1)
    box_office_df['percentage_change'] = box_office_df.apply(lambda row: try_convert_float(row['percentage_change']), axis=1)
    
    box_office_df = box_office_df.astype({'no_of_theatres': 'int32'})
    box_office_df = box_office_df.drop(columns='Estimated')
    
    return box_office_df
    
def get_start_date(date_str):
    dates = date_str.split('-')
    dates[0] = "{0} 2019".format(dates[0])
    return datetime.strptime(dates[0], '%b %d %Y').date()

def get_end_date(date_str):
    dates = date_str.split('-')
    month = dates[0].split(' ')[0]
    
    if try_convert_int(dates[1]) == -1:
        dates[1] = "{0} 2019".format(dates[1])
    else:
        dates[1] = "{0} {1} 2019".format(month, dates[1])
        
    return datetime.strptime(dates[1], '%b %d %Y').date() 

def try_convert_float(val):
    return_val = None
    try:
        return_val = float(val.strip('%'))/100
    except ValueError:
        return_val = None
        
    return return_val

def try_convert_money(val):
    return_val = None
    try:
        return_val = int(re.sub(r'[^0-9.]', '', str(val)))
    except ValueError:
        return_val = None
        
    return return_val

def try_convert_int(val):
    return_val = None

    try:
        return_val = int(float(val))
    except ValueError:
        return_val = -1

    
    return return_val