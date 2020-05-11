#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 11 11:19:15 2020

@author: andy
"""

from tqdm import tqdm
import pandas as pd
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Utils')

import database_helper

movies_df = database_helper.select_query("movies")

##How many movies have the twitter account in their 