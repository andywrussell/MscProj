#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 28 10:29:54 2020

@author: andy
"""

def get_comments_by_handle(handle):                
    sql = "SELECT * FROM public.tweets2019 WHERE "
    sql += 'lower("msg") LIKE '
    sql += "'%{0}%'".format(handle)
    
    return get_data(sql, params)
    