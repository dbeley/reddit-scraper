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
import json
import logging

logger = logging.getLogger()
STARTTIME = time.time()


def main(args):
    reddit = redditconnect('bot')

    folder = "Comments"

    post = sys.argv[1]
    file = args.file
    source = args.source

    if file is not None:
        df_orig = pd.read_excel(file)
        logger.debug(list(df_orig))

    df = pd.DataFrame()
    if source is not None:
        with open(source, "r") as f:
            data = json.load(f)
        for i in tqdm(data):
            df = df.append(fetch_comments(i, reddit))
    else:
        df = fetch_comments(post, reddit)

    columns = ["ID", "Auteur", "Commentaire", "Longueur",
               "Date", "Score", "Subreddit", "Doré", "Parent", "Flair"]
    df = df[columns]

    df['Date'] = pd.to_datetime(df['Date'], unit='s')

    if file is not None:
        df_orig = df_orig[~df_orig['ID'].isin(df['ID'])]
        df = df_orig.append(df)

    if not os.path.exists(folder):
        os.makedirs(folder)

    os.chdir(folder)
    export_excel(df)

    # affichage du temps de traitement
    runtime = time.time() - STARTTIME
    print("Runtime : %.2f seconds" % runtime)


def fetch_comments(post, reddit):
    a = 0
    comments = []
    # submission = reddit.submission(post)
    # submission = reddit.submission(id='3gljfi')
    submission = reddit.submission(str(post))
    logger.debug("Begin fetch")

    logger.debug(submission.fullname)

    submission.comments.replace_more(limit=None)
    for comment in submission.comments.list():
    # for comment in submission.comments:
        a = a+1
        logger.debug("\r" + "Fetching comment " + str(a) + "…")
        comments.append(comment)

    logger.debug("Fetching comments DONE.")

    logger.debug("Creating pandas dataframe...")

    d = []
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

    logger.debug("Creating pandas dataframe DONE.")

    return df


def export_excel(df):
    """
    Fonction d'export
    """

    actualtime = int(time.time())

    writer = pd.ExcelWriter('comments_' + str(actualtime) + '.xlsx', engine='xlsxwriter',options={'strings_to_urls': False})

    df.to_excel(writer, sheet_name='Sheet1')

    writer.save()

    logger.debug("Done.")


def redditconnect(bot):
    """
    Fonction de connexion à reddit
    """
    user_agent = "python:script:download_comments_post"

    reddit = praw.Reddit('bot', user_agent=user_agent)
    return reddit


def parse_args():

    parser = argparse.ArgumentParser(description="Download comments of a post  or a set of posts")
    parser.add_argument('--source', type=str, help='The name of the json file containing posts ids')
    parser.add_argument('--file', type=str, help='The name of the xlsx file containing comments already extracted')
    parser.add_argument('--debug', help="Affiche les informations de déboguage", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.WARNING)

    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main(parse_args())
