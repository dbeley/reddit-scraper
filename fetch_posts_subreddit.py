#!/usr/bin/env python
"""
Download all the posts from a subreddit and export it in xlsx or csv.
"""

import argparse
import logging
import time
import json
import requests
import praw
import xlsxwriter
import pandas as pd
from tqdm import tqdm
from pathlib import Path

logger = logging.getLogger()
STARTTIME = time.time()


def getPushshiftData(before, after, sub):
    url = (
        "https://api.pushshift.io/reddit/search/submission?&size=1000&after="
        + str(after)
        + "&subreddit="
        + str(sub)
        + "&before="
        + str(before)
    )
    r = requests.get(url)
    data = json.loads(r.text)
    # with open('export_pushshift.json', 'w') as f:
    #     json.dump(data['data'], f)
    return data["data"]


def main(args):
    logger.debug("Démarrage du script")
    # export folder
    export_folder = "Subreddit"
    # list of post ID's
    post_ids = []

    df_orig = None

    logger.debug("Connexion à l'API reddit")
    reddit = redditconnect("bot")

    # lowest timestamp of extracted data
    if args.after is not None:
        after = int(args.after)
    else:
        after = 1100000000

    # highest timestamp of extracted data
    if args.before is not None:
        before = int(args.before)
    else:
        before = int(STARTTIME) - 600000

    if args.file is not None:
        logger.debug("Argument 'file' détecté")
        logger.debug("Chargement df_orig")
        if args.import_format == "xlsx":
            df_orig = pd.read_excel(args.file)
        else:
            df_orig = pd.read_csv(args.file, sep="\t", encoding="utf-8")
        logger.debug("#### LIST ####")
        logger.debug(list(df_orig))
        logger.debug("#### INFO ####")
        df_orig["Date"] = pd.to_datetime(df_orig["Date"])
        datemax = df_orig["Date"].max()
        logger.debug("datemax = " + str(datemax))
        datemax = pd.to_datetime(datemax, unit="s")
        # ~ 7 jours
        moins7j = pd.to_datetime(before - 600000, unit="s")
        if datemax >= moins7j:
            datemax = moins7j
        df_orig = df_orig[df_orig["Date"] <= datemax]
        # on enlève de df tout ce qui va être extrait
        after = int(datemax.timestamp())

    if args.source is None:
        logger.debug("Begin extracting Pushshift data")
        logger.debug(
            "before: %s, after: %s, subreddit: %s",
            str(before),
            str(after),
            str(args.subreddit),
        )
        data = getPushshiftData(before, after, args.subreddit)

        # Will run until all posts have been gathered
        # from the 'after' date up until todays date
        while len(data) > 0:
            for submission in data:
                post_ids.append(submission["id"])
            logger.debug("timestamp = " + str(data[-1]["created_utc"]))
            # Calls getPushshiftData() with the created date of the last submission
            data = getPushshiftData(
                before, data[-1]["created_utc"], args.subreddit
            )
        logger.debug("Extracting Pushshift data DONE.")

        data = post_ids

    else:
        logger.debug("ID file detected")
        with open(args.source, "r") as f:
            data = json.load(f)

    # Filename without extension
    filename_without_ext = "posts_{}_{}".format(
        str(args.subreddit), str(int(before))
    )

    # ID export
    export(data, export_folder, filename_without_ext, export_type="json")

    # Extract posts
    df = pd.DataFrame()
    df = fetch_posts(data, reddit)

    # Create the complete dataframe if df_orig exists
    if df_orig is not None:
        df_orig = df_orig[~df_orig["ID"].isin(df["ID"])]
        df = df_orig.append(df)

    # Posts export
    export(
        df, export_folder, filename_without_ext, export_type=args.export_format
    )

    runtime = time.time() - STARTTIME
    print("Runtime : %.2f seconds" % runtime)


def fetch_posts(data, reddit):
    """
    Extrait les commentaires du subreddit subreddit entre les timestamp \
    beginningtime et endtime. Renvoie un dataframe panda
    """
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
    df = []
    for x in tqdm(data, dynamic_ncols=True):
        try:
            submission = reddit.submission(id=str(x))
            df.append(
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
                    "Text": str(submission.selftext)
                    .replace("\r", "\n")
                    .replace("\t", " "),
                    "Domain": submission.domain,
                    "Gilded": submission.gilded,
                    "Hidden": submission.hidden,
                    "Archived": submission.archived,
                    "Can Gild": submission.can_gild,
                    "Can Crosspost": submission.is_crosspostable,
                }
            )
        except Exception as e:
            print("Error : " + str(e))
    logger.debug("Fetching posts DONE.")
    logger.debug("Creating pandas dataframe…")
    df = pd.DataFrame(df)
    df["Date"] = pd.to_datetime(df["Date"], unit="s")
    df = df[columns]
    return df


def export(data, folder, filename, export_type):
    """
    Fonction d'export
    """

    Path(folder).mkdir(parents=True, exist_ok=True)

    logger.debug("Opening subreddit folder DONE")

    if export_type == "json":
        # export json
        with open(f"{folder}/{filename}.json", "w") as f:
            json.dump(data, f)
    elif export_type == "xlsx":
        writer = pd.ExcelWriter(
            f"{filename}.xlsx",
            engine="xlsxwriter",
            options={"strings_to_urls": False},
        )
        logger.debug("df.to_excel")
        data.to_excel(writer, sheet_name="Sheet1", index=False)
        logger.debug("writer.save")
        writer.save()
    elif export_type == "csv":
        data.to_csv(f"{folder}/{filename}.csv", index=False, sep="\t")


def redditconnect(bot):
    """
    Fonction de connexion à reddit
    """
    user_agent = "python:script:download_posts_subreddit"

    reddit = praw.Reddit(bot, user_agent=user_agent)
    logger.debug(reddit.user.me())
    return reddit


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download all the posts of a specific subreddit"
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
        "-s",
        "--subreddit",
        type=str,
        help="The subreddit to download posts from. Default : /r/france",
        default="france",
    )
    parser.add_argument(
        "-a", "--after", type=str, help="The min unixstamp to download"
    )
    parser.add_argument(
        "-b", "--before", type=str, help="The max unixstamp to download"
    )
    parser.add_argument(
        "--source",
        type=str,
        help="The name of the json file containing posts ids",
    )
    parser.add_argument(
        "--file",
        type=str,
        help="The name of the file containing posts already extracted",
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
