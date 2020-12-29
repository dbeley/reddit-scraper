#!/usr/bin/env python
"""
Download comments from one or several users and export it in xlsx or csv.
"""

from psaw import PushshiftAPI

# import praw
import argparse
import time
import logging
import pandas as pd

# from tqdm import tqdm
from pathlib import Path

logger = logging.getLogger()
temps_debut = time.time()

COLUMNS = [
    "date",
    "date_utc",
    # "all_awardings",
    # "associated_award",
    "author",
    # "author_flair_background_color",
    # "author_flair_css_class",
    # "author_flair_richtext",
    # "author_flair_template_id",
    # "author_flair_text",
    # "author_flair_text_color",
    # "author_flair_type",
    # "author_fullname",
    # "author_patreon_flair",
    # "author_premium",
    # "awarders",
    "body",
    # "collapsed_because_crowd_control",
    "created_utc",
    # "gildings",
    "id",
    # "is_submitter",
    "link_id",
    # "locked",
    # "no_follow",
    "parent_id",
    "permalink",
    # "retrieved_on",
    "score",
    # "send_replies",
    # "stickied",
    "subreddit",
    # "subreddit_id",
    # "total_awards_received",
    # "treatment_tags",
    "created",
    "edited",
    # "steward_reports",
    "updated_utc",
    # "author_created_utc",
    # "can_gild",
    # "collapsed",
    # "collapsed_reason",
    # "controversiality",
    # "distinguished",
    # "gilded",
    # "nest_level",
    # "reply_delay",
    # "subreddit_name_prefixed",
    # "subreddit_type",
    # "rte_mode",
    # "score_hidden",
]


def main(args):
    api = PushshiftAPI()
    folder = "User"
    Path(folder).mkdir(parents=True, exist_ok=True)

    if args.username:
        username = [x.strip() for x in args.username.split(",")]
    else:
        logger.error("Use -u to set the username")
        exit()

    for i in username:
        try:
            df = fetch_comments(api, i)
            df["date_utc"] = pd.to_datetime(df["created_utc"], unit="s")
            df["date"] = pd.to_datetime(df["created"], unit="s")
            df["permalink"] = "https://old.reddit.com" + df["permalink"].astype(str)
            df = df[df.columns.intersection(COLUMNS)]
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


def fetch_comments(api, username):
    res = api.search_comments(author=username)
    df = pd.DataFrame([thing.d_ for thing in res])
    return df


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download the comments of one or several users"
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
