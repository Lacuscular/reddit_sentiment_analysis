# Links
# https://github.com/pushshift/api
# https://www.reddit.com/r/pushshift/comments/89pxra/pushshift_api_with_large_amounts_of_data/
# https://www.reddit.com/r/pushshift/comments/5gawot/pushshift_reddit_api_v20_documentation_use_this/

import requests
import ujson as json
import calendar
import datetime
import time

# before: everything after this date
# after: everything before this date

def getPushshiftData(sub=None, before=None, after=None, ids=None, getSubmissions=True, getComments=False): # respect 1 request per second
    try:
        suffix=''
        searchType = 'submission'
        if getComments or not getSubmissions:
            searchType='comment'
        if (before is not None):
            suffix += '&before='+str(before)
        if (after is not None):
            suffix += '&after='+str(after)
        if (sub is not None):
            suffix += '&subreddit='+sub
        if (ids is not None):
            suffix += '&ids='+','.join(ids)

        url = 'https://apiv2.pushshift.io/reddit/search/'+searchType+'?sort=asc&size=1000&sort_type=created_utc'+suffix # 1000 is the max size, oldest -> newest
        #print('loading '+url)
        # downloading from to print
        print(sub +': Downloading ' + searchType + 's from ' + datetime.datetime.fromtimestamp(after).strftime('%Y-%m-%d %H:%M:%S') + ' to ' + datetime.datetime.fromtimestamp(before).strftime('%Y-%m-%d %H:%M:%S') + ' ' + url)
        r = requests.get(url) # fix error for gateway problems? try catch, wait and try again...
        #print(r.text)
        data = json.loads(r.text)
        if len(data['data']) > 0:
            grabbed_data = data
        else:
            grabbed_data = None

        return grabbed_data
    except Exception as e:
         return None# on gateway errors -> try again in 5 sec
         # print(str(e))
         # print("Error Grabbing: Trying again in 5 sec")
         # time.sleep(15)
    #     return getPushshiftData(sub, before, after, ids, getSubmissions, getComments)


def GrabPostsPartial(sub, starttime, endtime): # recursive function
        submissions = []
        grabbed_data = getPushshiftData(sub=sub, before=endtime, after=starttime)
        if grabbed_data is None:
            #print(len(submissions))
            return submissions
        for item in grabbed_data['data']:
             if item not in submissions:
                 submissions.append(item)
             # if item['full_link'] not in submissions:
             #     submissions.append(item['full_link'])  # adds content

        #print(len(grabbed_data['data']))
        if (len(grabbed_data['data']) == 1000): # over 1000
            return submissions + GrabPostsPartial(sub, grabbed_data['data'][999]['created_utc'], endtime)
        else: # loop as long as data length == 1000, if not anymore, just use this
            return submissions

def GrabCommentsPartial(sub, starttime, endtime): # grabs comments directly (timestamp based)
        comments = []
        grabbed_Data = getPushshiftData(sub=sub, before=endtime, after=starttime, getSubmissions=False, getComments=True)
        if grabbed_Data is None:
            #print(len(comments))
            return comments
        for item in grabbed_Data['data']:
            if item not in comments:
                comments.append(item)
             # if ("https://www.reddit.com" + item['permalink']) not in comments:
             #     comments.append("https://www.reddit.com" + item['permalink'])

        #print(len(grabbed_Data['data']))
        if (len(grabbed_Data['data']) == 1000):  # over 1000
            return comments + GrabCommentsPartial(sub, grabbed_Data['data'][999]['created_utc'], endtime)
        else:  # loop as long as data length == 1000, if not anymore, just use this
            return comments

def GrabData_DaysBack(sub, length, type): # used to get data for x days, 0 = only 12am today to now
    data = []
    current_time = calendar.timegm(datetime.date.today().timetuple()) # https://stackoverflow.com/questions/22189341/find-the-epoch-of-the-most-recent-midnight (get time at 00:00 aka 12am)
    counter = length
    # length 0 = today 12 am -> now
    done = False
    while(not done):
        if(counter != 0):
            begin = current_time - counter * 86400  # (travel x days back, 86400 = 1day in seconds)
            end = current_time - (counter - 1) * 86400 # one day forward
        else: # when is 0
            begin = current_time  # 12am
            end = int(time.time())  # now

        if(type == 0):
            data.append([datetime.datetime.fromtimestamp(int(begin)).strftime('%d-%m-%Y'), GrabPostsPartial(sub, begin, end)])
        else:
            data.append([datetime.datetime.fromtimestamp(int(begin)).strftime('%d-%m-%Y'), GrabCommentsPartial(sub, begin, end)])

        counter -= 1
        if(counter < 0):
            done = True

    return data

def GrabData_DaysBack_Database(sub, length, type): # used to get data for x days, 0 = only 12am today to now
    data = []
    current_time = calendar.timegm(datetime.date.today().timetuple()) # https://stackoverflow.com/questions/22189341/find-the-epoch-of-the-most-recent-midnight (get time at 00:00 aka 12am)
    counter = length
    # length 0 = today 12 am -> now
    done = False
    while(not done):
        if(counter != 0):
            begin = current_time - counter * 86400  # (travel x days back, 86400 = 1day in seconds)
            end = current_time - (counter - 1) * 86400 # one day forward
        else: # when is 0
            begin = current_time  # 12am
            end = int(time.time())  # now

        if(type == 0):
            data.append([datetime.datetime.fromtimestamp(int(begin)).strftime('%d-%m-%Y'), GrabPostsPartial(sub, begin, end)])
        else:
            data.append([datetime.datetime.fromtimestamp(int(begin)).strftime('%d-%m-%Y'), GrabCommentsPartial(sub, begin, end)])

        counter -= 1
        if(counter < 0):
            done = True

    return data






# def travelBack(sub, time): # travel back time and grab all submission urls
#     submissions = []
#     current_time = int(time.time())
#     day_count = time
#     done = False
#     while (not done):
#         m_vAfter = current_time - day_count * 86400  # after: 1. (start)
#         m_vBefore = current_time - (day_count - 1) * 86400  # before: 2. (end)
#         grabbed_data = getPushshiftData(sub=sub, before=m_vAfter, after=m_vBefore)
#
#         for item in grabbed_data['data']:
#             submissions.append(item['full_link']) # adds links
#
#         if(len(grabbed_data['data']) == 1000): # if exceeded limit, split into smaller parts
#             another_grab = GrabDataPartial(sub, grabbed_data['data'][999]['created_utc'], m_vBefore)
#
#
#         if(day_count-1 == 0):
#             done = True
#         else:
#             day_count -= 1


        # if limit reached, half the time? (use timestamp!!!)
        # submissions.append(getPushshiftData(sub=sub, before=m_vAfter+'d', after=m_vBefore+'d')['full_link'])

#Prozedur:
#after --> 10d back
#before --> 9d back
#-----------------
#after --> 9d back
#before --> 8d b

# sub='bitcoin'
# (submissions_tmp, prev_end_date) = getPushshiftData(sub=sub, after='10d')
# submissions = submissions_tmp['data']
# while prev_end_date is not None:
#     (submissions_tmp, prev_end_date) = getPushshiftData(sub=sub, before=prev_end_date-1, after='10d')
#     if prev_end_date is not None:
#         submissions.extend(submissions_tmp['data'])


# for item in submissions:
#     print(item['full_link'])