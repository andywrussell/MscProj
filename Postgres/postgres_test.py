import psycopg2
import pandas as pd
import pandas.io.sql as sqlio
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import numpy as np


analyser = SentimentIntensityAnalyzer()

def sentiment_analyzer_scores(sentence):
    score = analyser.polarity_scores(sentence)
    print("{:-<40} {}".format(sentence, str(score)))
    
    
#def get_sentiment_by_search(searchTerm):
#    select_query = "SELECT * FROM public.tweets_part2 WHERE msg LIKE '%#SuicideSquad%' or msg LIKE '%#suicidesquad%'"
#    tweets_df = sqlio.read_sql_query(select_query, connection)

try:
    connection = psycopg2.connect(user="postgres",
                                  password="4ndr3wP0ST",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="twitter_test")
    
   # cursor = connection.cursor()
    # Print PostgreSQL Connection properties
    #print(connection.get_dsn_parameters(), "\n")
    
    select_query = "SELECT * FROM public.tweets_part2 WHERE msg LIKE '%#SuicideSquad%' or msg LIKE '%#suicidesquad%'"
    tweets_df = sqlio.read_sql_query(select_query, connection)
    
    sentiment_analyzer_scores(tweets_df.iloc[0].msg)
    
    graph_data = pd.DataFrame(columns =['tweet_id', 'msg', 'date', 'neg', 'neu', 'pos', 'compound'])
    for index, row in tweets_df.iterrows():
        score = analyser.polarity_scores(row['msg'])
        graph_row = {'tweet_id': row['id'], 'msg': row['msg'], 'date': row['created_at'], 'neg': score['neg'], 'neu': score['neu'], 'pos': score['pos'], 'compound': score['compound']} 
        graph_data = graph_data.append(graph_row, ignore_index=True)
       # sentiment_analyzer_scores()

    graph_data.plot(x='date', y='compound')
    #cursor.execute(select_query)
    #print("Selecting rows from mobile table using cursor.fetchall")
    #tweets = cursor.fetchall() 
        
    #tweets_df = pd.DataFrame(tweets)
    
    # Print PostgreSQL version
    #cursor.execute("SELECT version();")
    #record = cursor.fetchone()
    #print("You are connected to - ", record, "\n")

except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)
finally:
    #closing database connection.
        if(connection):
           # cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
            

