#!/usr/bin/env python
"""
Download comments from one or several users and export it in xlsx or csv.
"""

import praw
import argparse
import time
import logging
import pandas as pd
from tqdm import tqdm
from pathlib import Path

logger = logging.getLogger()
temps_debut = time.time()


def main(args):
    folder = "User"
    Path(folder).mkdir(parents=True, exist_ok=True)

    username = [x.strip() for x in args.username.split(",")]

    for i in tqdm(username):
        try:
            df = fetch_comments(i)
            df["Date"] = pd.to_datetime(df["Date"], unit="s")
            filename = f"{folder}/comments_{int(time.time())}_{i}"
            if args.export_format == "xlsx":
                writer = pd.ExcelWriter(
                    f"{filename}.xlsx",
                    engine="xlsxwriter",
                    options={"strings_to_urls": False},
                )
                df.to_excel(writer, sheet_name="Sheet1")
                writer.save()
            else:
                df.to_csv(f"{filename}.csv", index=False, sep="\t")
        except Exception as e:
            logger.error(
                "Does that user have made any comment ? Complete error : %s", e
            )

    logger.info("Runtime : %.2f seconds" % (time.time() - temps_debut))


def fetch_comments(username):
    reddit = redditconnect("bot")
    user = reddit.redditor(username)
    comments = []
    user = reddit.redditor(username)
    for index, comment in enumerate(user.comments.new(limit=None), 1):
        comments.append(
            {
                "User": str(username),
                "ID": comment.id,
                "Comment": comment.body,
                "Permalink": f"https://reddit.com{comment.permalink}",
                "Length": len(comment.body),
                "Date": comment.created_utc,
                "Score": comment.score,
                "Subreddit": comment.subreddit.display_name,
                "Gilded": comment.gilded,
                "Post ID": comment.link_id,
                "Post Title": comment.link_title,
                "Post URL": comment.link_url,
                "Post Author": comment.link_author,
            }
        )
    df = pd.DataFrame(comments)
    return df


def redditconnect(bot):
    user_agent = "python:script:download_comments_user"

    reddit = praw.Reddit(bot, user_agent=user_agent)
    return reddit


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download the last 1000 comments of one or several users"
    )
    parser.add_argument(
        "--debug",
        help="Display debugging information",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    parser.add_argument(
        "-u",
        "--username",
        type=str,
        help="The users to download comments from (separated by commas)",
        required=True,
    )
    parser.add_argument(
        "--export_format",
        type=str,
        help="Export format (csv or xlsx). Default : csv",
        default="csv",
    )
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == "__main__":
    main(parse_args())
