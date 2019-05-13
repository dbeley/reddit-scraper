#!/usr/bin/env python
"""
Download comments from one or several users and export it in xlsx or csv.
"""

import praw
import argparse
import os
import time
import logging
import pandas as pd
from tqdm import tqdm

logger = logging.getLogger()
temps_debut = time.time()


def main(args):
    username = args.username
    export_format = args.export_format

    folder = "User"
    if not os.path.exists(folder):
        os.makedirs(folder)

    username = [x.strip() for x in username.split(',')]

    for i in username:
        logger.info(f"Fetching comments for user {i}")
        try:
            df = fetch_comments(i)
            df['Date'] = pd.to_datetime(df['Date'], unit='s')
            filename = f"{folder}/comments_{int(time.time())}_{i}"
            if export_format == 'xlsx':
                writer = pd.ExcelWriter(f'{filename}.xlsx', engine='xlsxwriter', options={'strings_to_urls': False})
                df.to_excel(writer, sheet_name='Sheet1')
                writer.save()
            else:
                df.to_csv(f'{filename}.csv', index=False, sep='\t')
        except Exception as e:
            logger.error(f"Does that user have made any comment ? Complete error : {e}")

    logger.info("Runtime : %.2f seconds" % (time.time() - temps_debut))


def fetch_comments(username):
    comments = []

    columns = ["User",
               "ID",
               "Comment",
               "Permalink",
               "Length",
               "Date",
               "Score",
               "Subreddit",
               "Gilded",
               "Post ID",
               "Post Title",
               "Post URL",
               "Post Permalink",
               "Post Author"]

    reddit = redditconnect('bot')
    user = reddit.redditor(username)

    for index, submission in enumerate(user.comments.new(limit=None), 1):
        logger.debug(f"\rFetching comment {index} for user {username}…")
        comments.append(submission)

    logger.debug("Fetching comments DONE.")

    logger.debug("Creating pandas dataframe...")

    d = []

    for x in tqdm(comments, dynamic_ncols=True):
        d.append({"Length": len(x.body),
                  "Subreddit": x.subreddit.display_name,
                  "Comment": x.body,
                  "Score": x.score,
                  "Date": x.created_utc,
                  "Gilded": x.gilded,
                  "ID": x.id,
                  "Post ID": x.link_id,
                  "Post Author": x.link_author,
                  "Post Title": x.link_title,
                  "Post URL": x.link_url,
                  "Post Permalink": f"https://reddit.com{submission.permalink}",
                  "User": str(username),
                  "Permalink": f"https://reddit.com{x.permalink}"
                  })

    df = pd.DataFrame(d)

    df = df[columns]

    logger.debug("Creating pandas dataframe DONE.")

    return df


def redditconnect(bot):
    user_agent = "python:script:download_comments_user"

    reddit = praw.Reddit(bot, user_agent=user_agent)
    return reddit


def parse_args():
    parser = argparse.ArgumentParser(description='Download all the comments of one or several users')
    parser.add_argument('--debug', help="Display debugging information", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('-u', '--username', type=str, help='The users to download comments from (separated by commas)', default='c154c7a68e0e29d9614e')
    parser.add_argument('--export_format', type=str, help='Export format (csv or xlsx). Default : csv', default='csv')
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main(parse_args())
