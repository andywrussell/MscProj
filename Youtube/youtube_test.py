#GOOGLE API Key AIzaSyAq4OIWZ19jvTC_2GFC3TdL0A9oCcFNc2Q

import pandas as pd
from youtube_api import YouTubeDataAPI

api_key = 'AIzaSyAq4OIWZ19jvTC_2GFC3TdL0A9oCcFNc2Q'
yt = YouTubeDataAPI(api_key)

sonic_search = yt.search(q = "Sonic The Headgehog")

df_sonic = pd.DataFrame(sonic_search)
df_sonic.head(5)


trailer = df_sonic.iloc[0]
trailer.video_id

comments = yt.get_video_comments(trailer.video_id, max_results=100)
df_comments = pd.DataFrame(comments)
df_comments.head(5)
