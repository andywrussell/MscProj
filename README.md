# MscProj
Welcome to the git repo for my MSc thesis "Analysis of Success Factors and Preferences in the UK Film Market"

## Layout 

```bash
├── DataCollection (Contains files with methods used to collect data from discussed sources)
│   ├── create_movie_db.py (Generate DB from BFI data)
│   ├── get_movie_comments.py (Attempts to get comments form YouTube - Unused)
│   ├── get_movie_metadata.py (Collect movie meta data from IMDb and Box Office Mojo)
│   ├── get_movie_trailers.py (Collect trailer meta data from YouTube)
│   ├── get_movie_tweets.py (Methods to seach tweets db for movie hashtags and apply sentiment)
│   ├── movie_cleanup.py (Cleanup of some broken movie data)
│   └── test.py (Script used for testing for missing data)
├── Entities (Contains Class Definitions for Movie and Related Objects)
│   ├── mojo_box_office.py
│   ├── movie.py
│   ├── person.py
│   ├── trailers.py
│   └── weekend_box_office.py
├── Postgres (Tester functions used to figure out postgres data transfer)
│   ├── bfi_movie_create.py
│   ├── geotweets.py
│   └── postgres_test.py
├── QGIS (Open Street Map Data used to play with QGIS - Not relevant)
│   ├── uk.osm
│   └── uk.osm.db
├── Utils (Set of utilty modules)
│   ├── bfi_helper.py (Functions for loading raw data from BFI)
│   ├── comment_helper.py (Unused)
│   ├── database_helper.py (Custom Data Layer functions for data select, insert and update from postgres)
│   ├── mojo_helper.py (Functions for scraping data from BoxOfficeMojo)
│   ├── movie_helper.py (Many utlity functiosn for analysing movies -- LOTS IN HERE)
│   ├── omdb_helper.py (Unused)
│   ├── tweet_helper.py (Set of helper functions for processing tweet data)
│   └── youtube_helper.py (Wrapper class and helper functions for YouTube API)
├── Visualizations (Set of modules for visualizing and exploring data)
│   ├── exploration.py (Set of functions used to generate the figures and results for experiments)
│   ├── kde_test.py (Test for KDE not important)
│   ├── spatial.py (Set of functions to perform spatial analysis, expectation map, heatmap etc)
│   ├── thesis_analysis.py (Set functions to perform experiments used in thesis)
│   ├── timemap_test.py (Testing Time maps (Not Used))
│   └── topic_modelling.py (Testing Topic Modelling (Not Used))
└── Youtube (Test functions for YouTube (not important))
    ├── youtube_sonic.py
    └── youtube_test.py
```
