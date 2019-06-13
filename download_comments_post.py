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
        for id in tqdm(data, dynamic_ncols=True):
            logger.info("Extracting comments for id %s", id)
            df = df.append(fetch_comments(reddit, id=id))
    elif args.id is not None:
        ids = [x.strip() for x in args.id.split(",")]
        for id in tqdm(ids, dynamic_ncols=True):
            logger.info("Extracting comments for id %s", id)
            df = df.append(fetch_comments(reddit, id=id))
    elif args.urls is not None:
        urls = [x.strip() for x in args.urls.split(",")]
        for url in tqdm(urls, dynamic_ncols=True):
            logger.info("Extracting comments for url %s", url)
            df = df.append(fetch_comments(reddit, url=url))
    else:
        logger.error("Error in arguments. Use --source,-i/--id or -u/--url")
        exit()

    columns = [
        "ID",
        "Comment",
        "Author",
        "Subreddit",
        "Permalink",
        "Length",
        "Score",
        "Date",
        "Gilded",
        "Parent",
        "Flair",
        "Post ID",
        "Post Permalink",
        "Post Title",
        "Post URL",
        "Post Author",
    ]

    df = df[columns]
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


def fetch_comments(reddit, url=None, id=None):
    comments = []
    if id:
        submission = reddit.submission(id=id)
    elif url:
        submission = reddit.submission(url=url)
    else:
        logger.error("Error in fetch_comments")
        exit()

    logger.debug("Begin fetch")
    logger.debug(submission.fullname)

    submission.comments.replace_more(limit=None)
    for index, comment in enumerate(submission.comments.list(), 1):
        logger.debug("\rFetching comment %s …", index)
        comments.append(comment)

    logger.debug("Fetching comments DONE.")

    logger.debug("Creating pandas dataframe...")

    d = []
    for x in comments:
        if not x.author:
            author = "[deleted]"
        else:
            author = x.author.name
        d.append(
            {
                "Length": len(x.body),
                "Subreddit": x.subreddit.display_name,
                "Author": author,
                "Comment": x.body,
                "ID": x.id,
                "Score": x.score,
                "Date": x.created_utc,
                "Gilded": x.gilded,
                "Parent": x.parent_id,
                "Flair": x.author_flair_text,
                "Post ID": submission.id,
                "Post Permalink": f"https://reddit.com{submission.permalink}",
                "Post Title": submission.title,
                "Post Author": submission.author,
                "Post URL": submission.url,
                "Permalink": f"https://reddit.com{x.permalink}",
            }
        )

    df = pd.DataFrame(d)

    logger.debug("Creating pandas dataframe DONE.")

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
        "--url",
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
