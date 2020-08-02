#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for trying out topic models (not used in thesis)

Created on Fri Jun 19 11:01:45 2020

@author: andy
"""

#https://towardsdatascience.com/building-a-topic-modeling-pipeline-with-spacy-and-gensim-c5dc03ffc619
import numpy as np
import pandas as pd

import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel
import sys
import spacy
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en.stop_words import STOP_WORDS
#import en_core_web_lg

#from tqdm import tqdm_notebook as tqdm
from pprint import pprint
from tqdm import tqdm
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Entities')
sys.path.insert(1, '/home/andy/Documents/MscProject/MscProj/Utils')

from movie import Movie
import database_helper
import movie_helper

movies = movie_helper.get_movies()
#movie = movies[0]

synopsis_list = []
keyword_list = []
#synopsis_list.append(movie.synopsis)
stop_list = ['Mr', 'Mrs', 'Miss', 'reference', 'relationship', 'title', 'character']
nlp= spacy.load("en_core_web_lg")

for movie in movies:
    synopsis_list.append(movie.synopsis)
    keyword_list.append(" ".join(movie.keywords))
    temp = [actor.role for actor in movie.actors if actor.credited]
    flat_list = [item for sublist in temp for item in sublist]
    stop_list.extend(flat_list)
    

# My list of stop words


# Updates spaCy's default stop words list with my additional words. 
nlp.Defaults.stop_words.update(stop_list)

# Iterates over the words in the stop words list and resets the "is_stop" flag.
for word in STOP_WORDS:
    lexeme = nlp.vocab[word]
    lexeme.is_stop = True

def lemmatizer(doc):
    # This takes in a doc of tokens from the NER and lemmatizes them. 
    # Pronouns (like "I" and "you" get lemmatized to '-PRON-', so I'm removing those.
    doc = [token.lemma_ for token in doc if token.lemma_ != '-PRON-']
    doc = u' '.join(doc)
    return nlp.make_doc(doc)
    
def remove_stopwords(doc):
    # This will remove stopwords and punctuation.
    # Use token.text to return strings, which we'll need for Gensim.
    doc = [token.text for token in doc if token.is_stop != True and token.is_punct != True]
    return doc


# The add_pipe function appends our functions to the default pipeline.
nlp.add_pipe(lemmatizer,name='lemmatizer',after='ner')
nlp.add_pipe(remove_stopwords, name="stopwords", last=True)

doc_list = []
# Iterates through each article in the corpus.
for doc in tqdm(keyword_list):
    # Passes that article through the pipeline and adds to a new list.
    pr = nlp(doc)
    doc_list.append(pr)
    

# Creates, which is a mapping of word IDs to words.
words = corpora.Dictionary(doc_list)
#words2 = corpora.Dictionary(keyword_list)

# Turns each document into a bag of words.
corpus = [words.doc2bow(doc) for doc in doc_list]

lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                           id2word=words,
                                           num_topics=10, 
                                           random_state=2,
                                           update_every=1,
                                           passes=10,
                                           alpha='auto',
                                           per_word_topics=True)