import dash
from dash.dependencies import Output, Event, Input
import dash_core_components as dcc
import dash_html_components as html
import random
import plotly.graph_objs as go
from collections import deque
import sqlite3
import pandas as pd
import urllib.request
from bs4 import BeautifulSoup
from multiprocessing import Pool
import praw
import time
import GetRedditPosts
import DataPreProcessing
from textblob import TextBlob
import plotly
import plotly.graph_objs as go
import threading
import datetime
#import nltk
#nltk.download_shell() # DOWNLOAD on first run required.
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA # http://t-redactyl.io/blog/2017/04/using-vader-to-handle-sentiment-analysis-with-social-media-text.html

reddit = praw.Reddit(client_id='...',client_secret='...', user_agent='...')

# https://plot.ly/products/dash/
# https://dash.plot.ly/getting-started
# https://www.youtube.com/watch?v=K6ixFSxZAX0 (tutorial series)


top100sr = []
reddit_top = "http://redditmetrics.com/top"
page = urllib.request.urlopen(urllib.request.Request(reddit_top)).read().decode('utf-8')
soup = BeautifulSoup(page, "html.parser")
all_tables = soup.find('table', {"class" : 'table table-bordered'})

for row in all_tables.findAll("tr")[1:]:
    cells = row.findAll('td')
    top100sr.append(cells[1].find(text=True)[3:])

# delete private subreddits
# make another list but with (Last Update: ....) for description

top100sr_desc = []

conn = sqlite3.connect("reddit.db")
c = conn.cursor()


for subreddit in top100sr:
    print('Checking subreddit: ' + subreddit)
    if (reddit.subreddit(subreddit).subreddit_type == 'private'):
        top100sr.remove(subreddit)
        print('Subreddit private')
        continue

    try:
        sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS {} (
                                                            timestamp integer,
                                                            type text,
                                                            content text,
                                                            sentiment_textblob real,
                                                            sentiment_vader real
                                                        ); """
        c.execute(sql_create_projects_table.format(subreddit + "_sr"))
        # c.execute("PRAGMA journal_mode=wal")
        # c.execute("PRAGMA wal_checkpoint=TRUNCATE")

        conn.commit()

        sqlquery = "SELECT timestamp FROM {} ORDER BY timestamp DESC".format(subreddit + "_sr")
        for timestamp in c.execute(sqlquery):
            print('Subreddit found: ' + subreddit)
            top100sr_desc.append([subreddit, subreddit + " (Last Updated: " + datetime.datetime.fromtimestamp(int(timestamp[0])).strftime('%Y-%m-%d %H:%M:%S') + ")"])
            break
        else:
            top100sr_desc.append([subreddit, subreddit + " (Last Updated: Never)"])
    except: # when contains number, sql query bugs also ? doesnt work...
        top100sr.remove(subreddit)
        print('Subreddit BUG')
        continue


conn.close()

print(top100sr_desc)




print("Download of Top 100 Subreddits completed.")

senti_algorithms = ["TextBlob", "Natural Language Toolkit"]

app = dash.Dash("")

app.layout = html.Div([

    html.Img(
        src="https://d3atagt0rnqk7k.cloudfront.net/wp-content/uploads/2017/11/16094905/five-reddit-communities-1280x800.jpg",
        style={
            'height': '110px',
            'margin-right': '7px',
            'margin-top': '7px',
            'margin-bottom': '20px',
            'float': 'left'
        }),

html.H2('Reddit Sentiment Analysis',
                style={'display': 'inline',
                       'float': 'left',
                       'font-size': '2.65em',
                       'margin-left': '7px',
                       'font-weight': 'bolder',
                       'font-family': 'Arial',
                       'color': "rgba(117, 117, 117, 0.95)",
                       'margin-top': '20px',
                       'margin-bottom': '0'
                       }),

    html.Div(className='container', children=[
        html.H2('Top 100 Subreddits',  style={'display': 'inline',
                       'float': 'left',
                       'margin-left': '7px',
                       'margin-top': '5px',
                       'margin-bottom': '0'
                       }),

     ], style={'width': '98%', 'max-width':660}),

html.Div(className='container', children=[
    html.H5('Subreddit', style={'clear': 'both', 'margin-bottom': '5px'}),
    dcc.Dropdown(id='subreddit-dropdown', options=[{'label': sr[1], 'value': sr[0]} for sr in top100sr_desc]),



    html.H5('Sentiment Detection', style={'clear': 'both', 'margin-bottom': '5px', 'margin-top': '10px'}),
    dcc.Dropdown(id='algo-dropdown', options=[{'label': algo, 'value': algo} for algo in senti_algorithms],
                  multi=True, value=senti_algorithms),
    # time begin: now, subreddit begin
    # timestamp format: Last 15 Minutes, daily
    # Checkboxes Positive, Neutral, Negative
    # status

    html.H5('Timespan Mode', style={'clear': 'both', 'margin-bottom': '5px', 'margin-top': '10px'}),
    dcc.RadioItems(
    id='timespan-mode',
    options=[
        {'label': 'History (Last 15 Minutes)', 'value': '15min'},
        {'label': 'History (Daily)', 'value': 'Daily'},
    ],
    labelStyle={'display': 'inline-block'},
    value='Daily'
    ),

    html.H5('Sentiment Neutral Component', style={'clear': 'both', 'margin-bottom': '5px', 'margin-top': '10px'}),

    dcc.Checklist(id='sentiment-components',
    options=[
        {'label': 'Include Neutral Sentiment', 'value': 'Neutral'},
    ],
    labelStyle={'display': 'inline-block'},
    values=['Positive', 'Negative']
    ),

    html.Div(id='status'), # add status :)

    html.Div(className='row', children=[
        html.Div(dcc.Graph(id='daily-graph', animate=False)),
        html.Div(dcc.Graph(id='pie-chart', animate=False))]),

    html.H5('Save Options', style={'clear': 'both', 'margin-bottom': '5px', 'margin-top': '10px'}),
    html.Button('Export to CSV', id='savebutton'),  # 15 mins = min based, daily = per 24hrs



    # Save Options:
    # export to csv button :)
     ], style={'width': '98%', 'margin-left': 10, 'margin-right': 10}),

    # status missing

    html.Div(id='output'),

    dcc.Interval(
            id='status-update',
            interval=3000
        ),

    # dcc.Interval(
    #     id='pie-chart-update',
    #     interval=3000
    # )

    # plot 1: sentiment (durchschnitt)
    # plot 2: sentiment verteilung

], style={'font-family':'Arial'})


current_status = "Nothing"
current_sr = None
piedata = None


clicks = 0
@app.callback(Output('output', 'children'), [Input('savebutton', 'n_clicks')]) # dash requires an output
def on_click(n_clicks):
    global piedata
    global current_sr
    global clicks
    if n_clicks is not None:
        if n_clicks > clicks:
            clicks = n_clicks
            if subreddit is not None:
                if not piedata is None:
                    piedata.to_csv(current_sr + ".csv", sep=',')
                    print(current_sr + " saved as CSV!")


@app.callback(
    dash.dependencies.Output('status','children'),
    [Input('subreddit-dropdown', 'value')],
    events=[Event('status-update', 'interval')])
def update_status(subreddit):
    global current_status
    global current_sr
    if subreddit is not None:
        if current_status == "Updating":
            conn = sqlite3.connect("reddit.db")
            c = conn.cursor()
            # create table if it doesnt exist (http://www.sqlitetutorial.net/sqlite-python/create-tables/)
            # (https://stackoverflow.com/questions/34392011/create-table-using-a-variable-in-python)
            sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS {} (
                                                                  timestamp integer,
                                                                  type text,
                                                                  content text,
                                                                  sentiment_textblob real,
                                                                  sentiment_vader real
                                                              ); """
            c.execute(sql_create_projects_table.format(current_sr + "_sr"))

            # read out days...

            c.execute("SELECT count(*) FROM {}".format(current_sr + "_sr"))
            data = c.fetchone()[0]
            if data != 0:
                sql = ''' SELECT * FROM {} ORDER BY timestamp DESC LIMIT 1'''
                c.execute(sql.format(current_sr + "_sr"))
                last_timestamp_available = c.fetchone()[0]

                count_days = (time.time() - last_timestamp_available) / 86400

                return html.H3(
                        'Status: Updating ({} days left)'.format(str(count_days)),
                        style={'marginTop': 20, 'marginBottom': 20}
                    )
            else:
                return html.H3(
                    'Status: Updating',
                    style={'marginTop': 20, 'marginBottom': 20}
                )


    else:
        return html.H3(
            'Status: Select a Subreddit',
            style={'marginTop': 20, 'marginBottom': 20}
        )






# start downloading thread, once current_sr set -> start download (DOWNLOADER)

# https://github.com/Sentdex/socialsentiment/blob/master/dash_mess.py
# https://github.com/plotly/dash-stock-tickers-demo-app/blob/master/app.py

@app.callback(Output('pie-chart', 'figure'),
              [Input('subreddit-dropdown', 'value'),
              Input('sentiment-components', 'values')],
              events=[Event('status-update', 'interval')])
def update_pie_chart(subreddit, components):
    global piedata
    if subreddit is not None:
        if not piedata is None:
            #print(piedata)
            pos_count = len(piedata[(piedata['sentiment_textblob'] > 0) & (piedata['sentiment_vader'] > 0)])

            neutral_count = len(piedata[(piedata['sentiment_textblob'] == 0.0) & (piedata['sentiment_vader'] == 0.0)])

            neg_count = len(piedata[(piedata['sentiment_textblob'] < 0) & (piedata['sentiment_vader'] < 0)])


            #print(str(pos_count_textblob))
            #print(components)
            values = []
            labels = []
            colors = []


            values.append(pos_count)
            labels.append('Positive Timesteps')
            colors.append('#008000')

            if "Neutral" in components:
                values.append(neutral_count)
                labels.append('Neutral Timesteps')
                colors.append('#D3D3D3')


            values.append(neg_count)
            labels.append('Negative Timesteps')
            colors.append('#FF0000')

            # if selected, add to ...

            trace = go.Pie(labels=labels, values=values,
                           hoverinfo='label+percent', textinfo='value',
                           textfont=dict(size=20),
                           marker=dict(colors=colors,
                                       line=dict(width=2)))

            return {"data": [trace], 'layout': go.Layout(
                title='Summarized Pie Chart for Subreddit "{}"'.format(subreddit),
                showlegend=True)}



last_time_checked = 0
@app.callback(
    Output('daily-graph', 'figure'),
    [Input('subreddit-dropdown', 'value'),
     Input('sentiment-components', 'values'),
     Input('timespan-mode', 'value')],
    events=[Event('status-update', 'interval')])
def update_status(subreddit, components, timemode):
    global current_status
    global current_sr
    global piedata
    global last_time_checked
    if subreddit is not None:
        if True: #reddit.subreddit(subreddit).subreddit_type == 'public':

            if(subreddit != current_sr):
                last_time_checked = 0

            current_status = "Updating"

            current_sr = subreddit

            #c = conn.cursor()
            conn = sqlite3.connect("reddit.db")
            c = conn.cursor()
            sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS {} (
                                                                  timestamp integer,
                                                                  type text,
                                                                  content text,
                                                                  sentiment_textblob real,
                                                                  sentiment_vader real
                                                              ); """
            c.execute(sql_create_projects_table.format(current_sr + "_sr"))
            c.execute("PRAGMA journal_mode=wal")
            c.execute("PRAGMA wal_checkpoint=TRUNCATE")

            c.execute("SELECT count(*) FROM {}".format(current_sr + "_sr"))
            data = c.fetchone()[0]

            #print(data)

            if data != 0:
                # check if entry exists, if not let download
                df = pd.read_sql('SELECT * FROM {} ORDER BY timestamp DESC'.format(current_sr + '_sr'), conn)
                #df.sort_values('timestamp', inplace=True)
                df['date'] = pd.to_datetime(df['timestamp'], unit='s')
                df.set_index('date', inplace=True)
                df = df.drop(['timestamp', 'type', 'content'], axis=1)
                # delete neutral ones

                if not 'Neutral' in components:
                    df = df[df['sentiment_textblob'] != 0.0]
                    df = df[df['sentiment_vader'] != 0.0]
                # df.append(neutral_part)


                #if 'Positive'

                # pos_part = df[(df['sentiment_textblob'] > 0.2) & (df['sentiment_vader'] > 0.2)]
                # neutral_part =  df[(df['sentiment_textblob'] < 0.2) & (df['sentiment_textblob'] > -0.2) & (df['sentiment_vader'] < 0.2) & (df['sentiment_vader'] > -0.2)]
                # neg_part = df[(df['sentiment_textblob'] < -0.2) & (df['sentiment_vader'] < -0.2)]
                #
                # if components:
                #     df = df[0:0]
                #     if 'Positive' in components:
                #         df.append(pos_part)
                #     if 'Neutral' in components:
                #         df.append(neutral_part)
                #     if 'Negative' in components:
                #         df.append(neg_part)

                if df.empty:
                    return
                
                
                df['volume'] = 1


                # daily or 15 min HERE -------------------------------------------------------------------------
                #print(timemode)
                if timemode == '15min':
                    df = df.resample('1Min').agg({'sentiment_textblob': 'mean', 'sentiment_vader': 'mean', 'volume': 'count'}).tail(15)
                elif timemode == 'Daily':
                    df = df.resample('24h').agg({'sentiment_textblob': 'mean', 'sentiment_vader': 'mean', 'volume':'count'})
                df.dropna(inplace=True)



                piedata = df

                conn.close()

                # daily chart

                data = plotly.graph_objs.Scatter(
                    x=df.index,
                    y=df.sentiment_textblob.values,
                    name='Sentiment TextBlob',
                    mode='lines',
                    yaxis='y2',
                    line=dict(color='#00FFFF', width=4, ) # HEX CODE: blue
                )

                data1 = plotly.graph_objs.Scatter(
                    x=df.index,
                    y=df.sentiment_vader.values,
                    name='Sentiment NLTK',
                    mode='lines',
                    yaxis='y2',
                    line=dict(color='#FFA500', # HEX CODE: orange
                              width=4, )
                )

                data2 = plotly.graph_objs.Bar(
                    x=df.index,
                    y=df.volume.values,
                    name='Volume',
                    marker=dict(color='#008000') # HEX CODE: green
                )
                # read out graphs

                #print(df)

                #add status text (count days, x/34)
                # elements.append(html.H3(
                #     'Status: Updating',
                #     style={'marginTop': 20, 'marginBottom': 20}
                # ))
                # add element
                figure = {'data': [data, data1, data2], 'layout': go.Layout(xaxis=dict(range=[min(df.index), max(df.index)]),
                                                                            yaxis=dict(range=[min(df.volume.values), max(df.volume.values * 4)], title='Post Count', side='right'),
                                                                            yaxis2=dict(range=[-1, +1], side='left', overlaying='y', title='Sentiment'),
                                                                            yaxis3=dict(range=[min(df.sentiment_vader.values), max(df.sentiment_vader.values)], side='left', overlaying='y',title='Sentiment NLTK'),
                                                                            title='Daily Sentiment for Subreddit "{}"'.format(subreddit),
                                                                            showlegend=True
                                                                            )}

                return figure
    else:
        current_status = "Nothing"
        current_sr = None
        last_time_checked = 0
        piedata = None
        # elements.append(html.H3(
        # 'Status: Idle. Please select a subreddit.',
        # style={'marginTop': 20, 'marginBottom': 20}
        # ))


    # if download available

# last 15 min chart
#
#             data = plotly.graph_objs.Scatter(
#                 x=dfmin.index,
#                 y=dfmin.sentiment_textblob.values,
#                 name='Sentiment TextBlob',
#                 mode='lines',
#                 yaxis='y2',
#                 line=dict(color='#00FFFF', width=4, )  # HEX CODE: blue
#             )
#
#             data1 = plotly.graph_objs.Scatter(
#                 x=dfmin.index,
#                 y=dfmin.sentiment_vader.values,
#                 name='Sentiment NLTK',
#                 mode='lines',
#                 yaxis='y2',
#                 line=dict(color='#FFA500',  # HEX CODE: orange
#                           width=4, )
#             )
#
#             data2 = plotly.graph_objs.Bar(
#                 x=dfmin.index,
#                 y=dfmin.volume.values,
#                 name='Volume',
#                 marker=dict(color='#008000')  # HEX CODE: green
#             )
#
#             figure = {'data': [data, data1, data2],
#                       'layout': go.Layout(xaxis=dict(range=[min(dfmin.index), max(dfmin.index)]),
#                                           yaxis=dict(range=[min(dfmin.volume.values), max(dfmin.volume.values * 4)],
#                                                      title='Volume', side='right'),
#                                           yaxis2=dict(range=[-1, +1], side='left', overlaying='y', title='Sentiment'),
#                                           yaxis3=dict(
#                                               range=[min(dfmin.sentiment_vader.values), max(dfmin.sentiment_vader.values)],
#                                               side='left', overlaying='y', title='Sentiment NLTK'),
#                                           title='Last 15 Minute Sentiment for Subreddit "{}"'.format(subreddit),
#                                           showlegend=True
#                                           )}
#             elements.append(dcc.Graph(id='sentiment-graph-15min', figure=figure))
#
#             return elements


def AddPosts(c, posts, subreddit):
        for post in posts:
            if post:
                # check if selftext exists, create variables here
                if 'selftext' in post:
                    selftext = post['selftext']
                else:
                    selftext = ""

                #print(post)
                #print(post['title'])

                headline_word_array = DataPreProcessing.preprocess_Data(post['title'])
                if 'selftext' in post:
                    selftext_word_array = DataPreProcessing.preprocess_Data(selftext)

                if 'selftext' in post:
                    if headline_word_array and selftext_word_array:
                        preprocessed_text = " ".join(headline_word_array) + " " + " ".join(selftext_word_array)
                    else:
                        preprocessed_text = ""
                else:
                    if headline_word_array:
                        preprocessed_text = " ".join(headline_word_array)
                    else:
                        preprocessed_text = ""

                if preprocessed_text: # if filtering gives out no significant words -> don't post

                    sql = ''' INSERT INTO {}(timestamp,type,content,sentiment_textblob,sentiment_vader)
                                             VALUES(?,?,?,?,?) '''
                    # add post (including headline)
                    sid = SIA()
                    c.execute(sql.format(subreddit + "_sr"),
                                (int(post['created_utc']),
                                "post",
                                str(post['title'] + " " + selftext),
                                float(TextBlob(preprocessed_text).sentiment.polarity),
                                float(sid.polarity_scores(preprocessed_text)["compound"]))) # https://stackoverflow.com/questions/39462021/nltk-sentiment-vader-polarity-scorestext-not-working))

def AddComments(c, comments, subreddit):
        for comment in comments:
            if comment:
                # full_link does not exists! create one with link_id and parent id......
                body_word_array = DataPreProcessing.preprocess_Data(comment['body'])
                if body_word_array:
                    preprocessed_text = " ".join(body_word_array)
                    sql = ''' INSERT INTO {}(timestamp,type,content,sentiment_textblob,sentiment_vader)
                                                                VALUES(?,?,?,?,?) '''
                    # add post (including headline)
                    sid = SIA()
                    c.execute(sql.format(subreddit + "_sr"),
                              (int(comment['created_utc']),
                               "comment",
                               str(comment['body']),
                               float(TextBlob(preprocessed_text).sentiment.polarity),
                               float(sid.polarity_scores(preprocessed_text)["compound"])
                               ))

def Downloader():
    global last_time_checked
    global current_sr
    while True:
        if not current_sr is None:
            if current_status == "Nothing":
                continue
            elif current_status == "Updating":
                # connect to db (creates file, if that doesn't exist)
                conn = sqlite3.connect("reddit.db")
                c = conn.cursor()
                # create table if it doesnt exist (http://www.sqlitetutorial.net/sqlite-python/create-tables/)
                # (https://stackoverflow.com/questions/34392011/create-table-using-a-variable-in-python)
                sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS {} (
                                                       timestamp integer,
                                                       type text,
                                                       content text,
                                                       sentiment_textblob real,
                                                       sentiment_vader real
                                                   ); """
                c.execute(sql_create_projects_table.format(current_sr + "_sr"))
                # c.execute("PRAGMA journal_mode=wal")
                # c.execute("PRAGMA wal_checkpoint=TRUNCATE")

                conn.commit()
                # get last data point from sentiment table (if possible, if not possible -> get date when subreddit was created and download from there) (https://stackoverflow.com/questions/2440147/how-to-check-the-existence-of-a-row-in-sqlite-with-python)
                c.execute("SELECT count(*) FROM {}".format(current_sr + "_sr"))
                data = c.fetchone()[0]
                if data == 0:
                    # grab subreddit creation date (http://praw.readthedocs.io/en/latest/code_overview/models/subreddit.html)
                    subreddit_created_utc = int(reddit.subreddit(current_sr).created_utc)


                    # somehow stays on 0

                    if last_time_checked == 0:
                        last_time_checked = subreddit_created_utc


                    if time.time() - last_time_checked > 86400:
                        posts = GetRedditPosts.GrabPostsPartial(current_sr, last_time_checked, last_time_checked + 86400)
                        comments = GetRedditPosts.GrabCommentsPartial(current_sr, last_time_checked, last_time_checked + 86400)
                    else:
                        posts = GetRedditPosts.GrabPostsPartial(current_sr, last_time_checked, time.time())
                        comments = GetRedditPosts.GrabCommentsPartial(current_sr, last_time_checked, time.time())

                    AddPosts(c, posts, current_sr)
                    AddComments(c, comments, current_sr)

                    last_time_checked += 86400
                    #

                    # add every post/comment to db
                    # download ONE DAY, or rest of day....
                    # make requests in 24h steps (if step is possible for bigger then >24hrs) until now, everytime request takes place -> write to db
                else:
                    # get last unix timestamp
                    if last_time_checked == 0: # prevents loop, when no data comes in
                        sql = ''' SELECT * FROM {} ORDER BY timestamp DESC LIMIT 1'''
                        c.execute(sql.format(current_sr + "_sr"))
                        last_timestamp_available = c.fetchone()[0]
                        last_time_checked = last_timestamp_available
                    else:
                        last_time_checked += 86400


                    if time.time() - last_time_checked > 86400:
                        posts = GetRedditPosts.GrabPostsPartial(current_sr, last_time_checked,
                                                                last_time_checked + 86400)
                        comments = GetRedditPosts.GrabCommentsPartial(current_sr, last_time_checked,
                                                                      last_time_checked + 86400)
                    else:
                        posts = GetRedditPosts.GrabPostsPartial(current_sr, last_time_checked, time.time())
                        comments = GetRedditPosts.GrabCommentsPartial(current_sr, last_time_checked, time.time())

                    AddPosts(c, posts, current_sr)
                    AddComments(c, comments, current_sr)
                    # take last unix available, + 24 hrs if step > 24hrs else do under 24 hrs step..
                    # download since last
                # download data, ONCE day finished -> create sentiment entry in another table
                conn.commit()
                conn.close()
        else:
            continue

#Downloader()

if __name__ == '__main__': # multiprocessing = https://stackoverflow.com/questions/1239035/asynchronous-method-call-in-python

    t1 = threading.Thread(target=Downloader)
    t1.start()
    app.run_server()

