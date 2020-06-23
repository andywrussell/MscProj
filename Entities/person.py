#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 11 15:59:44 2020

@author: andy
"""
import json
import sys
import re
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Utils')

import database_helper
import jsonpickle
from json import JSONEncoder

class Person():
    def __init__(self, db_row):
        self.personId = db_row.id
        self.imdbId = db_row.imdbId
        self.name = db_row.fullName
        
    def toJSON(self):
        return jsonpickle.encode(self, unpicklable=False)
        #return json.dumps(empJSON, indent=4)
        #return json.dumps(self, default=lambda o: o.__dict__)
        
class Actor(Person):
    def __init__(self, db_row):
        self.actorId = db_row.id
        self.movie_imdbId = db_row.m_imdbId
        self.role = db_row.role
        self.credited = not db_row.notes == '(uncredited)'
        #get person entry 
        person_df = database_helper.select_query("people", { "imdbId" : db_row.p_imdbId })
        Person.__init__(self, person_df.iloc[0])
    
        
class Director(Person):
    def __init__(self, db_row):
        self.movie_imdbId = db_row.m_imdbId
        person_df = database_helper.select_query("people", { "imdbId" : db_row.p_imdbId })
        Person.__init__(self, person_df.iloc[0])
        

class Writer(Person):
    def __init__(self, db_row):
        self.movie_imdbId = db_row.m_imdbId
        person_df = database_helper.select_query("people", { "imdbId" : db_row.p_imdbId })
        Person.__init__(self, person_df.iloc[0])
        
    