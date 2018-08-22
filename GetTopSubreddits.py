import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
import praw
import math
import time
import GetRedditPosts
import DataPreProcessing
from textblob import TextBlob
import nltk
from bs4 import BeautifulSoup

reddit = praw.Reddit(client_id='...',client_secret='...', user_agent='...')
# https://www.analyticsvidhya.com/blog/2015/10/beginner-guide-web-scraping-beautiful-soup-python/
# https://stackoverflow.com/questions/2792650/import-error-no-module-name-urllib2

reddit_top = "http://redditmetrics.com/top"

page = urllib.request.urlopen(urllib.request.Request(reddit_top)).read().decode('utf-8')

soup = BeautifulSoup(page, "html.parser")

all_tables = soup.find('table', {"class" : 'table table-bordered'})

# generate lists
#A = []
B = []
#C = []

for row in all_tables.findAll("tr")[1:]:
    cells = row.findAll('td')
    #A.append(cells[0].find(text=True))
    B.append(cells[1].find(text=True)[3:])
   # C.append(cells[2].find(text=True))

print(B) # printing top 100 subreddits

# check paper from methodic

# apis #
# textblob (https://media.readthedocs.org/pdf/textblob/dev/textblob.pdf) (https://stevenloria.com/simple-text-classification/)
# nltk/vader (https://programminghistorian.org/lessons/sentiment-analysis) (https://www.learndatasci.com/tutorials/sentiment-analysis-reddit-headlines-pythons-nltk/)

# if more time: lstm netowrk

#print posts 1 day back
# https://stackoverflow.com/questions/12463818/using-praw-how-do-you-get-comment-linked-by-a-url
# https://www.reddit.com/r/redditdev/comments/2ix3aj/how_do_i_read_the_fields_of_praw_submission/

# filter options
# urls = GetRedditPosts.GrabData_DaysBack("bitcoin", 1)
# for link in urls:
#      submission = reddit.submission(url=link)
#     # print(str(submission.selftext))
#      for comment in submission.comments:
#         print(comment.body)

sb_reddit = "funny"
post_urls = GetRedditPosts.GrabData_DaysBack(sb_reddit, 5, 0) # subreddit, days back, modi (0=threads, 1=comments)
#comment_urls = GetRedditPosts.GrabData_DaysBack(sb_reddit, 0, 1)
#mods = reddit.subreddit(sb_reddit).moderator()

############################################## Grabs Posts incl. Headline ##############################################
posts = []
for obj in post_urls:
    content = []
   # for url in obj: # 0 = time, 1 = data
    print(obj[0])
        #print("https://reddit.com" + url['permalink'])
        # submission = reddit.submission(url=url)
        #
        # # print(str(submission.title) + ' // ' + str(submission.selftext) + ' // ' + str(submission.url) + ' // ' + str(submission.permalink) + '\n')
        # # submission.title = reddit post title
        # # submission.selftext = content written by user
        # # submission.url = external url
        # # submission.permalink = /r/... link
        #
        # headline_word_array = DataPreProcessing.preprocess_Data(submission.title)
        # if headline_word_array:
        #     string = " ".join(headline_word_array)
        #     #print(string)
        #     content.append(string)
        #
        # selftext_word_array = DataPreProcessing.preprocess_Data(submission.selftext)
        # if selftext_word_array:
        #     string = " ".join(selftext_word_array)
        #    # print(string)
        #     content.append(string)

        # scrapes comments, although there can be comments older/newer than the specific post day..
        # submission.comments.replace_more(limit=0)
        #
        # for comment in submission.comments: # 'MoreComments' object has no attribute 'body' - https://praw.readthedocs.io/en/latest/tutorials/comments.html#extracting-comments-with-praw
        #     badNames = ['bot']
        #     if(comment.author is not None):
        #         if(not DataPreProcessing.does_contain_words(comment.author.name, badNames)) and comment.author not in mods: # filter mods and bots
        #             comment_word_array = DataPreProcessing.preprocess_Data(comment.body)
        #             if comment_word_array:
        #                 string = " ".join(comment_word_array)
        #                 print(string)
        #                 content.append(string)

    #posts.append([obj[0], content])
########################################################################################################################


# analyze persons who interacted in timeframe and characterize them
#################################################### Grabs Comments ####################################################
# comments = []
# for obj in comment_urls:
#     content = []
#     for url in obj[1]:
        #print(url)
    #     bla = DataPreProcessing.preprocess_Data(url['body'])
    #     if bla:
    #         sentiment_value = TextBlob(" ".join(bla)).sentiment.polarity
    #         if(sentiment_value > 0.5):
    #             print('-----------------------------------')
    #             print("https://reddit.com" + url['permalink'])
    #             print(bla)
    #             print(sentiment_value)
    #             print('-----------------------------------')
    #     # url = "https://reddit.com" + url['permalink']
    #     # comment = reddit.submission(url=url)
    #     #
    #     # selftext_word_array = DataPreProcessing.preprocess_Data(comment.body)
    #     # if selftext_word_array:
    #     #     string = " ".join(selftext_word_array)
    #     #     content.append(string)
    #
    # comments.append([obj[0], content])

########################################################################################################################
# https://chrisalbon.com/python/data_wrangling/pandas_create_column_with_loop/
# later grab news content from posts => more data
#print("------posts---------")
#print(posts)
#print("------comments--------")
#print(comments)
#print("-------------------")
#df = pd.DataFrame(posts, columns=['date', 'content'])
#print(df)
# sentiment = []
# for row in df['content']:
#     sentiment_value = 0
#     for content in row:
#         sentiment_value += TextBlob(content).sentiment.polarity # textblob
#         print(content)
#         print(sentiment_value)
#
#     sentiment_value /= len(row) # get average
#     sentiment.append(sentiment_value)
#
# df['sentiment'] = sentiment
#
# print(df)





# searchstr = "timestamp:{}..{}".format(day_start,day_end)
# subreddit = reddit.subreddit(B[0])
# sub_submissions = subreddit.search(searchstr, sort='relevance', syntax='plain', limit=None) #subreddit.submissions(day_start, day_end) # no longer works.....
#
# submission = reddit.submission(url='https://www.reddit.com/r/funny/comments/3g1jfi/buttons/')
# for top_level_comment in submission.comments:
#     print(top_level_comment.body)

#for submission in sub_submissions:
#    if not submission.stickied:
#        print(str(submission.title) + ' // ' + str(submission.selftext) + ' // ' + str(
#        submission.url) + ' // ' + str(submission.permalink) + '\n')
#        print('---------------------------------------------')
