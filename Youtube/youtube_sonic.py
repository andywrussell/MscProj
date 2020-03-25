import pandas as pd
from youtube_api import YouTubeDataAPI
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyser = SentimentIntensityAnalyzer()

api_key = 'AIzaSyBR2kc8R5EzD1rnOjyXZfEL1FOGLKojsg4'
yt = YouTubeDataAPI(api_key)

#video parts
video_parts = ['statistics', 'snippet', 'contentDetails', 'topicDetails']

#check api key is valid
if yt.verify_key() :
    sonic = yt.get_video_metadata('szby7ZHLnkA', 
                                  parser = None,
                                  part=video_parts)
    
    sonic_comments = yt.get_video_comments('szby7ZHLnkA', max_results=100)
    df_comments = pd.DataFrame(sonic_comments)
    
    df_graph_data = pd.DataFrame(columns = ['comment_id', 'commenter_channel_id', 'channel_country', 'text', 'date', 'neg', 'neu', 'pos', 'compound'])
    
    for index, row in df_comments.iterrows():
        channel_id = df_comments.iloc[0].commenter_channel_id
        channel_data = yt.get_channel_metadata(channel_id)
    
        score = analyser.polarity_scores(row['text'])
        graph_row = {'comment_id': row['comment_id'], 'commenter_channel_id': row['commenter_channel_id'], 'channel_country' : channel_data['country'], 'text' : row['text'], 'date': row['collection_date'], 'neg': score['neg'], 'neu': score['neu'], 'pos': score['pos'], 'compound': score['compound']} 
        df_graph_data = df_graph_data.append(graph_row, ignore_index=True)
        
        
    df_graph_data.plot(x='comment_id', y='compound')
#Get soinc trailer -- this is hardcoded for now
