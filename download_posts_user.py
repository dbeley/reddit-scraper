#!/usr/bin/env python
"""
Download posts from a user and export it in xlsx.
"""

import praw
import pandas as pd
import argparse
from tqdm import tqdm
import os
import time

def main(args): 
    username = args.username
    folder = "User"

    username = [x.strip() for x in username.split(',')]

    df = pd.DataFrame()
    for i in username:
        df = fetch_posts(df, i)
    if not os.path.exists(folder):
        os.makedirs(folder)

    df['Date'] = pd.to_datetime(df['Date'], unit='s')

    os.chdir(folder)
    export_excel(df, username)

def fetch_posts(df, username):
    a = 0
    posts = []

    columns = ["ID", "Nom", "Date", "Score", "Ratio", "Commentaires", "Flair",
               "Domaine", "Texte", "URL", "Permalien", "Auteur",
               "CSS Flair Auteur", "Texte Flair Auteur", "Doré", "Peut dorer",
               "Caché", "Archivé", "Peut crossposter"]

    reddit = redditconnect('bot')
    user = reddit.redditor(username)

    for a, submission in enumerate(user.submissions.new(limit=None), 1):
        print("\r" + "Fetching post " + str(a) + " for user " + str(username) + "…")
        posts.append(submission)

    print("Fetching posts DONE.")

    print("Creating pandas dataframe...")

    d = []

    for submission in tqdm(posts, dynamic_ncols=True):
        d.append({"Score": submission.score,
                  "Auteur": str(submission.author),
                  "CSS Flair Auteur":
                  str(submission.author_flair_css_class),
                  "Texte Flair Auteur": str(submission.author_flair_text),
                  "Ratio": submission.upvote_ratio,
                  "ID": submission.name,
                  "Permalien": str("https://reddit.com" +
                                   submission.permalink),
                  "Nom": submission.title,
                  "URL": submission.url,
                  "Commentaires": submission.num_comments,
                  "Date": submission.created_utc,
                  "Flair": str(submission.link_flair_text),
                  "Texte": str(submission.selftext),
                  "Domaine": submission.domain,
                  "Doré": submission.gilded,
                  "Caché": submission.hidden,
                  "Archivé": submission.archived,
                  "Peut dorer": submission.can_gild,
                  "Peut crossposter": submission.is_crosspostable
                  })

    d = pd.DataFrame(d)

    d = d[columns]

    df = df.append(d)

    print("Creating pandas dataframe DONE.")

    return df

def export_excel(df, username):

    actualtime = int(time.time())

    writer = pd.ExcelWriter('posts_' + str(actualtime) + '_' + str(username[0]) + '.xlsx', engine='xlsxwriter',options={'strings_to_urls': False})

    df.to_excel(writer, sheet_name='Sheet1')

    writer.save()

    print("Done.")

def redditconnect(bot):
    user_agent = "python:script:download_posts_user"

    reddit = praw.Reddit(bot, user_agent=user_agent)
    return reddit


def parse_args():
    parser = argparse.ArgumentParser(description='Download all the posts of a specific user')
    parser.add_argument('-u', '--username', type=str, help='The user to download posts from. ', default='c154c7a68e0e29d9614e')

    args = parser.parse_args()

    return args

if __name__ == '__main__':
    main(parse_args())
    

