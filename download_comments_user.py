"""
Download comments from a user and export it in xlsx.
"""

#! /usr/bin/env python

import praw
import pandas as pd
import argparse
from tqdm import tqdm
import os
import time

def main(args): 
    username = args.username
    folder = "User"
    
    df = fetch_comments(username)
    
    if not os.path.exists(folder):
        os.makedirs(folder)

    os.chdir(folder)
    export_excel(df, username)

def fetch_comments(username):
    a = 0
    comments = []

    columns = ["id", "Comment", "Comment_length", \
               "Date", "Score", "Subreddit", "Gilded", \
               "Link_id", "Link_title", "Link_author", "Link_url"]

    reddit = redditconnect('bot')
    user = reddit.redditor(username)
 
    for submission in user.comments.new(limit=None):
        a = a+1
        print("\r" + "Fetching comment " + str(a) + " for user " + str(username) + "…")
        comments.append(submission)

    print("Fetching comments DONE.")

    print("Creating pandas dataframe...")

    d = []

    for x in tqdm(comments):
        d.append({"Comment_length":len(x.body),
                "Subreddit":x.subreddit.display_name,
                "Comment":x.body_html,
                "Score":x.score,
                "Date":x.created_utc,
                "Gilded":x.gilded,
                "id":x.id,
                "Link_id":x.link_id,
                "Link_author":x.link_author,
                "Link_title":x.link_title,
                "Link_url":x.link_url
                })

    df = pd.DataFrame(d)
    
    df = df[columns]
    
    print("Creating pandas dataframe DONE.")

    return df
    
def export_excel(df, username):
    
    actualtime = int(time.time())

    writer = pd.ExcelWriter('comments_' + str(username) + '_' + str(actualtime) + '.xlsx', engine='xlsxwriter',options={'strings_to_urls': False})
        
    df.to_excel(writer, sheet_name='Sheet1')
    
    writer.save()
    
    print("Done.")
    
def redditconnect(bot):
    user_agent = "python:script:download_comments_user"

    reddit = praw.Reddit(bot, user_agent=user_agent)
    return reddit


def parse_args():
    parser = argparse.ArgumentParser(description='Download all the comments of a specific user')
    parser.add_argument('-u', '--username', type=str, help='The user to download comments from. ', default='c154c7a68e0e29d9614e')

    args = parser.parse_args()

    return args

if __name__ == '__main__':
    main(parse_args())
    

