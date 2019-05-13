#!/usr/bin/env python
"""
Download posts from a user and export it in xlsx.
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
    folder = "User"
    if not os.path.exists(folder):
        os.makedirs(folder)

    username = [x.strip() for x in username.split(',')]

    for i in username:
        logger.info(f"Fetching posts for user {i}")
        try:
            df = fetch_posts(i)

            df['Date'] = pd.to_datetime(df['Date'], unit='s')
            export_excel(df, i, folder)
        except Exception as e:
            logger.error(e)
    logger.info("Runtime : %.2f seconds" % (time.time() - temps_debut))


def fetch_posts(username):
    posts = []

    columns = ["ID",
               "Title",
               "Date",
               "Score",
               "Ratio",
               "Comments",
               "Flair",
               "Domain",
               "Text",
               "URL",
               "Permalink",
               "Author",
               "Author CSS Flair",
               "Author Text Flair",
               "Gilded",
               "Can Gild",
               "Hidden",
               "Archived",
               "Can Crosspost"]

    reddit = redditconnect('bot')
    user = reddit.redditor(username)

    for index, submission in enumerate(user.submissions.new(limit=None), 1):
        logger.debug(f"\rFetching post {index} for user {username}…")
        posts.append(submission)

    logger.debug("Fetching posts DONE.")

    logger.debug("Creating pandas dataframe...")

    d = []

    for submission in tqdm(posts, dynamic_ncols=True):
        d.append({"Score": submission.score,
                  "Author": str(submission.author),
                  "Author CSS Flair":
                  str(submission.author_flair_css_class),
                  "Author Text Flair": str(submission.author_flair_text),
                  "Ratio": submission.upvote_ratio,
                  "ID": submission.name,
                  "Permalink": f"https://reddit.com{submission.permalink}",
                  "Title": submission.title,
                  "URL": submission.url,
                  "Comments": submission.num_comments,
                  "Date": submission.created_utc,
                  "Flair": str(submission.link_flair_text),
                  "Text": str(submission.selftext),
                  "Domain": submission.domain,
                  "Gilded": submission.gilded,
                  "Hidden": submission.hidden,
                  "Archived": submission.archived,
                  "Can Gild": submission.can_gild,
                  "Can Crosspost": submission.is_crosspostable
                  })

    df = pd.DataFrame(d)

    df = df[columns]

    logger.debug("Creating pandas dataframe DONE.")

    return df


def export_excel(df, username, folder):

    actualtime = int(time.time())

    writer = pd.ExcelWriter(f'{folder}/posts_{actualtime}_{username}.xlsx', engine='xlsxwriter',options={'strings_to_urls': False})

    df.to_excel(writer, sheet_name='Sheet1')

    writer.save()


def redditconnect(bot):
    user_agent = "python:script:download_posts_user"

    reddit = praw.Reddit(bot, user_agent=user_agent)
    return reddit


def parse_args():
    parser = argparse.ArgumentParser(description='Download all the posts of a specific user')
    parser.add_argument('--debug', help="Display debugging information", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('-u', '--username', type=str, help='The user to download posts from. ', default='c154c7a68e0e29d9614e')
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main(parse_args())
