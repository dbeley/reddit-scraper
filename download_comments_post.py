#!/usr/bin/env python
"""
Download comment from a post and export it in xlsx.
"""

import praw
import pandas as pd
import argparse
from tqdm import tqdm
import os
import time
import sys
import re
import json


def main(args):
    reddit = redditconnect('bot')

    folder = "Comments"

    post = sys.argv[1]
    file = args.file

    df = fetch_comments(post, reddit)

    if not os.path.exists(folder):
        os.makedirs(folder)

    os.chdir(folder)
    export_excel(df)


def fetch_comments(post, reddit):
    a = 0
    comments = []
    # submission = reddit.submission(post)
    # submission = reddit.submission(id='3gljfi')
    submission = reddit.submission(url=str(post))
    print("Begin fetch")

    print(submission.fullname)

    submission.comments.replace_more(limit=None)
    for comment in submission.comments.list():
    # for comment in submission.comments:
        a = a+1
        print("\r" + "Fetching comment " + str(a) + "…")
        comments.append(comment)

    print("Fetching comments DONE.")

    print("Creating pandas dataframe...")

    d = []
    columns = ["ID", "Auteur", "Commentaire", "Longueur",
               "Date", "Score", "Subreddit", "Doré", "Parent", "Flair"]

    for x in comments:
        if not x.author:
            author = '[deleted]'
        else:
            author = x.author.name
        d.append({"Longueur": len(x.body),
                  "Subreddit": x.subreddit.display_name,
                  "Auteur": author,
                  "Commentaire": x.body,
                  "Score": x.score,
                  "Date": x.created_utc,
                  "Doré": x.gilded,
                  "ID": x.id,
                  "Parent": x.parent_id,
                  "Flair": x.author_flair_text
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


def parse_args():

    parser = argparse.ArgumentParser(description="Download comments of a post or a set of post")
    parser.add_argument('-f', '--file', type=str, help='file containing set of ids or links (one per line')

    args = parser.parse_args()

    return args


if __name__ == '__main__':
    main(parse_args())
