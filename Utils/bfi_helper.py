#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 14:40:21 2020

@author: andy
"""

import pandas as pd
import glob
from os import listdir


def get_raw_data():  
    """Helper function to return top 15 film data for each weekend from BFI data"""
    
    #Get list of folders for each month
    folder_names = listdir("../../ProjectData/BFI/2019/") 
    
    
    film_df = pd.DataFrame()
    
    #read all raw data files in each folder 
    for folder in folder_names:
        folder_path = "../../ProjectData/BFI/2019/" + folder + "/Raw/*.xls"
        month_files = glob.glob(folder_path)
        
        for file in month_files:
            data = pd.read_excel(file)
            film_df = pd.concat([film_df, data])    
            
    return film_df