# reddit_sentiment_analysis
School Project

This is a school project about sentiment analysis on the Top 100 Subreddits of Reddit.com.

This repo contains a small sample CSV (as an export for excel sheets & visualization) and a sample database for demo purposes.
Downloading all data of one subreddit will probably take several days.

Some Infos about this script:
The Top 100 Subreddits are scraped from http://redditmetrics.com/top and are stored in a string list.
Visualization is live-updating through SQLite & also there is a spawned thread for the Downloader to make things easier.
The Download Thread downloads input from PushShift, preprocesses it, calculates the sentiment and inserts it into the Database.

There are small coding bugs, but will probably be fixed in the next days.

Screenshot: https://i.gyazo.com/7d441b5e68d8ab88047e9ea1b3822bd6.png
