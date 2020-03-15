#!/usr/bin/env python
"""
Download comment from posts by IDs or URLs and export it to xlsx or csv
"""

import praw
import argparse
import time
import json
import logging
import pandas as pd
from pathlib import Path
from tqdm import tqdm

logger = logging.getLogger()
STARTTIME = time.time()


def main(args):
    reddit = redditconnect("bot")

    folder = "Comments"

    if args.file is not None:
        if args.import_format == "xlsx":
            df_orig = pd.read_excel(args.file)
            logger.debug(list(df_orig))
        else:
            df_orig = pd.read_csv(args.file, sep="\t", encoding="utf-8")

    df = pd.DataFrame()
    if args.source is not None:
        with open(args.source, "r") as f:
            data = json.load(f)
        for post_id in tqdm(data, dynamic_ncols=True):
            logger.info("Extracting comments for id %s", post_id)
            df = df.append(fetch_comments(reddit, post_id=post_id))
    elif args.id is not None:
        ids = [x.strip() for x in args.id.split(",")]
        for post_id in tqdm(ids, dynamic_ncols=True):
            logger.info("Extracting comments for id %s", post_id)
            df = df.append(fetch_comments(reddit, post_id=post_id))
    elif args.urls is not None:
        urls = [x.strip() for x in args.urls.split(",")]
        for url in tqdm(urls, dynamic_ncols=True):
            logger.info("Extracting comments for url %s", url)
            df = df.append(fetch_comments(reddit, url=url))
    else:
        logger.error("Error in arguments. Use --source,-i/--id or -u/--url")
        exit()

    df["Date"] = pd.to_datetime(df["Date"], unit="s")

    if args.file is not None:
        df_orig = df_orig[~df_orig["ID"].isin(df["ID"])]
        df = df_orig.append(df)

    Path(folder).mkdir(parents=True, exist_ok=True)

    filename = f"{folder}/comments_{int(time.time())}"
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

    runtime = time.time() - STARTTIME
    logger.info("Runtime : %.2f seconds" % runtime)


def fetch_comments(reddit, url=None, post_id=None):
    comments = []
    if post_id:
        submission = reddit.submission(id=post_id)
    elif url:
        submission = reddit.submission(url=url)
    else:
        logger.error("Error in fetch_comments")
        exit()

    submission = reddit.submission(url=url)
    submission.comments.replace_more(limit=None)
    for index, comment in enumerate(submission.comments.list(), 1):
        if not comment.author:
            author = "[deleted]"
        else:
            author = comment.author.name
        comments.append(
            {
                "ID": comment.id,
                "Subreddit": comment.subreddit.display_name,
                "Date": comment.created_utc,
                "Author": author,
                "Comment": comment.body,
                "Score": comment.score,
                "Length": len(comment.body),
                "Gilded": comment.gilded,
                "Parent": comment.parent_id,
                "Flair": comment.author_flair_text,
                "Post ID": submission.id,
                "Post Permalink": f"https://reddit.com{submission.permalink}",
                "Post Title": submission.title,
                "Post Author": submission.author,
                "Post URL": submission.url,
                "Permalink": f"https://reddit.com{comment.permalink}",
            }
        )

    df = pd.DataFrame(comments)

    return df


def redditconnect(bot):
    """
    Fonction de connexion à reddit
    """
    user_agent = "python:script:download_comments_post"

    reddit = praw.Reddit("bot", user_agent=user_agent)
    return reddit


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download comments of a post or a set of posts (by id or by url)"
    )
    parser.add_argument(
        "--debug",
        help="Display debugging information",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument(
        "-i",
        "--id",
        type=str,
        help="IDs of the posts to extract (separated by commas)",
    )
    parser.add_argument(
        "-u",
        "--urls",
        type=str,
        help="URLs of the posts to extract (separated by commas)",
    )
    parser.add_argument(
        "--source",
        type=str,
        help="The name of the json file containing posts ids",
    )
    parser.add_argument(
        "--file",
        type=str,
        help="The name of the file containing comments already extracted",
    )
    parser.add_argument(
        "--export_format",
        type=str,
        help="Export format (csv or xlsx). Default : csv",
        default="csv",
    )
    parser.add_argument(
        "--import_format",
        type=str,
        help="Import format, if used with --file (csv or xlsx). Default : csv",
        default="csv",
    )

    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == "__main__":
    main(parse_args())
