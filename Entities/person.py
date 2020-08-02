#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Class definitions for person, actor, director and writer

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
    """
    Class definition for person object
    """
    def __init__(self, db_row):
        """
        Person box office class constructor
        
        :param db_row: pandas series object corresponding to row from which object should be built
        """
        
        self.personId = db_row.id
        self.imdbId = db_row.imdbId
        self.name = db_row.fullName
        
        
class Actor(Person):
    """
    Class definition for Actor object, inherits person
    """
    def __init__(self, db_row):
        """
        Actor box office class constructor
        
        :param db_row: pandas series object corresponding to row from which object should be built
        """
        
        self.actorId = db_row.id
        self.movie_imdbId = db_row.m_imdbId
        self.role = db_row.role
        self.credited = not db_row.notes == '(uncredited)'
        #get person entry 
        person_df = database_helper.select_query("people", { "imdbId" : db_row.p_imdbId })
        Person.__init__(self, person_df.iloc[0])
    
        
class Director(Person):
    """
    Class definition for Director object, inherits person
    """
    def __init__(self, db_row):
        """
        Director box office class constructor
        
        :param db_row: pandas series object corresponding to row from which object should be built
        """
        
        self.movie_imdbId = db_row.m_imdbId
        person_df = database_helper.select_query("people", { "imdbId" : db_row.p_imdbId })
        Person.__init__(self, person_df.iloc[0])
        

class Writer(Person):
    """
    Class definition for Writer object, inherits person
    """
    
    def __init__(self, db_row):
        """
        Director box office class constructor
        
        :param db_row: pandas series object corresponding to row from which object should be built
        """
        self.movie_imdbId = db_row.m_imdbId
        person_df = database_helper.select_query("people", { "imdbId" : db_row.p_imdbId })
        Person.__init__(self, person_df.iloc[0])
        
    