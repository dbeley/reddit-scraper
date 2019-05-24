#!/usr/bin/env python
"""
Download posts from one or several users and export it in xlsx or csv.
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

    if args.username:
        username = [x.strip() for x in args.username.split(",")]
    else:
        logger.error("Use -u to set the username")
        exit()

    for i in username:
        logger.info("Fetching posts for user %s", i)
        try:
            df = fetch_posts(i)
            df["Date"] = pd.to_datetime(df["Date"], unit="s")
            filename = f"{folder}/posts_{int(time.time())}_{i}"
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
                "Does that user have made any post ? Complete error : %s", e
            )

    logger.info("Runtime : %.2f seconds" % (time.time() - temps_debut))


def fetch_posts(username):
    posts = []

    columns = [
        "ID",
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
        "Can Crosspost",
    ]

    reddit = redditconnect("bot")
    user = reddit.redditor(username)

    for index, submission in enumerate(user.submissions.new(limit=None), 1):
        logger.debug("\rFetching post %s for user {username}…", index)
        posts.append(submission)

    logger.debug("Fetching posts DONE.")

    logger.debug("Creating pandas dataframe...")

    d = []

    for submission in tqdm(posts, dynamic_ncols=True):
        d.append(
            {
                "Score": submission.score,
                "Author": str(submission.author),
                "Author CSS Flair": str(submission.author_flair_css_class),
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
                "Can Crosspost": submission.is_crosspostable,
            }
        )

    df = pd.DataFrame(d)

    df = df[columns]

    logger.debug("Creating pandas dataframe DONE.")

    return df


def redditconnect(bot):
    user_agent = "python:script:download_posts_user"

    reddit = praw.Reddit(bot, user_agent=user_agent)
    return reddit


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download all the posts of one or several users"
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
        help="The users to download posts from (separated by commas)",
        default="c154c7a68e0e29d9614e",
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