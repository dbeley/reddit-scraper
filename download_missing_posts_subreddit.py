"""
Download missing posts from a xlsx file containing subreddit posts.
"""

#! /usr/bin/env python

import time
import argparse
import os
import logging
import praw
import pandas as pd
from tqdm import tqdm

logger = logging.getLogger()
STARTTIME = time.time()


def main(args):
    subreddit = args.subreddit
    file = args.file
    folder = "Subreddit"
    type = "xls"

    # Définition du premier timestamp à télécharger
    beginningtime = 1212086987
    nom, type = os.path.splitext(file)
    endtime = int(nom.rsplit("_")[-1])
    subreddit = str(nom.rsplit("_")[-2])

    n = 0
    a = 0

    logger.debug("beginningtime = " + str(beginningtime))
    logger.debug("endtime = " + str(endtime))

    columns = ["id", "Name", "Date", "Score", "Ratio", "Nbr_comments",
               "Flair", "Domain", "Self text", "url", "permalink",
               "Author", "Author_flair_css", "Author_flair_text", "Gilded"]

    reddit = redditconnect('test')
    sub = reddit.subreddit(subreddit)

    df = pd.read_excel(file)
    length = len(df)
    # Récupération des posts entre beginningtime et endtime
    for x in sub.submissions(beginningtime, endtime):
        n = n + 1
        timestamp = x.created_utc
        if timestamp not in df.Date.values:
            print("Timestamp {} not found ! Fetching post {}".format(
                str(timestamp), str(n)))

            a = a + 1
            df.loc[length + a] = {"Score": x.score,
                                  "Author": str(x.author),
                                  "Author_flair_css": str(x.author_flair_css_class),
                                  "Author_flair_text": str(x.author_flair_text),
                                  "Ratio": x.upvote_ratio,
                                  "id": x.name,
                                  "permalink": str("https://reddit.com" + x.permalink),
                                  "Name": x.title,
                                  "url": x.url,
                                  "Nbr_comments": x.num_comments,
                                  "Date": timestamp,
                                  "Flair": str(x.link_flair_text),
                                  "Self text": str(x.selftext_html),
                                  "Domain": x.domain,
                                  "Gilded": int(x.gilded)
                                  }
        else:
            print("Timestamp {} already found ! post {}".format(
                str(timestamp), str(n)))

    print("Fetching posts DONE.")
    print("Creating pandas dataframe…")

    logger.debug("Opening export folder...")
    if not os.path.exists(folder):
        os.makedirs(folder)
    os.chdir(folder)
    logger.debug("Opening export folder DONE")

    df = df.sort_values("Date")

    # export du dataframe
    export(df, subreddit, endtime)

    # affichage du nombre de posts manquants trouvés
    print("Missing posts found : {}".format(str(a)))

    # affichage du temps de traitement
    runtime = time.time() - STARTTIME
    print("Runtime : %.2f seconds" % runtime)


def export(df, subreddit, endtime):
    """
    Fonction d'export générale.
    Excel uniquement supporté pour le moment
    """
    logger.debug("Début de l'export excel")
    export_excel(df, subreddit, endtime)


def export_excel(df, subreddit, endtime):
    """
    Fonction d'export vers excel.
    """
    filename = "posts_{}_{}.xlsx".format(str(subreddit), str(int(endtime)))
    writer = pd.ExcelWriter(filename, engine='xlsxwriter',
                            options={'strings_to_urls': False})
    logger.debug("df.to_excel")
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    logger.debug("writer.save")
    writer.save()


def redditconnect(bot):
    """
    Fonction de connexion à reddit
    """
    user_agent = "python:script:download_missing_posts_subreddit"

    reddit = praw.Reddit(bot, user_agent=user_agent)
    return reddit


def parse_args():
    """
    Fonction qui parse les argumnents.
    """

    parser = argparse.ArgumentParser(description='Download missing posts of a \
                                     specific subreddit')
    # arguments nécessaires
    requirednamed = parser.add_argument_group('required named arguments')
    requirednamed.add_argument('-f', '--file', type=str, help='The name of the \
                file containing the old data, must contains the timestamp \
                of the last record', required=True)
    # arguments optionnels
    parser.add_argument('-s', '--subreddit', type=str, help='The subreddit to \
                        download posts from. ', default='france')
    parser.add_argument('-ll', '--loglevel', type=str, choices=['DEBUG', 'INFO',
                                                                'WARNING', 'ERROR', 'CRITICAL'], help='Set the logging level')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main(parse_args())
