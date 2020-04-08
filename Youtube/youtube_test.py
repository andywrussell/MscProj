#GOOGLE API Key AIzaSyAq4OIWZ19jvTC_2GFC3TdL0A9oCcFNc2Q

import pandas as pd
from youtube_api import YouTubeDataAPI
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyser = SentimentIntensityAnalyzer()

api_key = 'AIzaSyBR2kc8R5EzD1rnOjyXZfEL1FOGLKojsg4'
yt = YouTubeDataAPI(api_key)

sonic_search = yt.search(q = "Sonic The Headgehog", max_results=5, parser=None)
spy
df_sonic = pd.DataFrame(sonic_search)
df_sonic.head(5)


trailer = df_sonic.iloc[0]
trailer.video_id

comments = yt.get_video_comments(trailer.video_id, max_results=10)
df_comments = pd.DataFrame(comments)

df_graph_data = pd.DataFrame(columns = ['comment_id', 'commenter_channel_id', 'channel_country', 'text', 'date', 'neg', 'neu', 'pos', 'compound'])

channel_id = df_comments.iloc[0].commenter_channel_id
channel_data = yt.get_channel_metadata(channel_id)

# for index, row in df_comments.iterrows():
#     channel_id = df_comments.iloc[0].commenter_channel_id
#     channel_data = yt.get_channel_metadata(channel_id)
    
#     print
    
#     score = analyser.polarity_scores(row['text'])
#     graph_row = {'comment_id': row['comment_id'], 'commenter_channel_id': row['commenter_channel_id'], 'channel_country' : channel_data['country'], 'text' : row['text'], 'date': row['collection_date'], 'neg': score['neg'], 'neu': score['neu'], 'pos': score['pos'], 'compound': score['compound']} 
#     df_graph_data = df_graph_data.append(graph_row, ignore_index=True)
