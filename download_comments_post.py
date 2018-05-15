"""
Download comment from a post and export it in xlsx.
"""

#! /usr/bin/env python

import praw
import pandas as pd
import argparse
from tqdm import tqdm
import os
import time
import sys
import re
import json

def main(): 
    folder = "Comments"

    post = sys.argv[1]

    df = fetch_comments(post)
    
    if not os.path.exists(folder):
        os.makedirs(folder)

    os.chdir(folder)
    export_excel(df)

def fetch_comments(post):
    a = 0
    comments = []
    reddit = redditconnect('bot')
    #submission = reddit.submission(post)
    #submission = reddit.submission(id='3gljfi')
    submission = reddit.submission(url=str(post))
    print("Begin fetch")

    columns = ["id", "Author", "Comment", "Comment_length", \
               "Date", "Score", "Subreddit", "Gilded"]

    print(submission.fullname)
    
    submission.comments.replace_more(limit=None)
    for comment in submission.comments.list():
#    for comment in submission.comments:
        a = a+1
        print("\r" + "Fetching comment " + str(a) + "…")
        comments.append(comment)

    print("Fetching comments DONE.")

    print("Creating pandas dataframe...")

    d = []

    for x in tqdm(comments):
        if not x.author:
            author = '[deleted]'
        else:
            author = x.author.name
        d.append({"Comment_length":len(x.body),
                "Subreddit":x.subreddit.display_name,
                "Author":author,
                "Comment":x.body,
                "Score":x.score,
                "Date":x.created_utc,
                "Gilded":x.gilded,
                "id":x.id
                })

    df = pd.DataFrame(d)
    
    df = df[columns]
    
    print("Creating pandas dataframe DONE.")

    return df
    
def export_excel(df):
    
    actualtime = int(time.time())

    writer = pd.ExcelWriter('comments_' + str(actualtime) + '.xlsx', engine='xlsxwriter',options={'strings_to_urls': False})
        
    df.to_excel(writer, sheet_name='Sheet1')
    
    writer.save()
    
    print("Done.")
    
def redditconnect(bot):
    user_agent = "python:script:download_comments_post"

    reddit = praw.Reddit('bot', user_agent=user_agent)
    return reddit


if __name__ == '__main__':
    main()
    

