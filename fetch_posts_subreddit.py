#!/usr/bin/env python
"""
Download all the posts from a subreddit and export it in xlsx.
"""

import argparse
import logging
import os
import time
import json
import requests
import pandas as pd
import praw
from tqdm import tqdm

logger = logging.getLogger()
STARTTIME = time.time()


def getPushshiftData(before, after, sub):
    url = 'https://api.pushshift.io/reddit/search/submission?&size=1000&after='+str(after)+'&subreddit='+str(sub)+'&before='+str(before)
    r = requests.get(url)
    data = json.loads(r.text)
    # with open("data.json", "w") as f:
    #     json.dump(r.text, f)
    return data['data']


def main(args):
    # current folder
    original_folder = os.getcwd()
    # folder where to put extracted data
    folder = "Subreddit"
    # list of post ID's
    post_ids = []
    # Subreddit to query
    subreddit = args.subreddit
    # xlsx file containing already extracted data
    file = args.file
    # json file containing post ids
    source = args.source
    df_orig = None

    reddit = redditconnect('bot')

    # lowest timestamp of extracted data
    if args.after is not None:
        after = int(args.after)
    else:
        after = 1100000000

    # highest timestamp of extracted data
    if args.before is not None:
        before = int(args.before)
    else:
        before = int(STARTTIME)

    if file is not None:
        df_orig = pd.read_excel(file)
        logger.debug(list(df_orig))
        datemax = df_orig['Date'].max()
        # ~ 24 jours
        if datemax >= before - 2000000:
            datemax = before - 2000000
        df_orig = df_orig[df_orig['Date'] <= datemax]
        # on enlève de data tout ceux qui sont présent dans df, sauf ceux qui ont moins
        # d'un mois
        # on enlève de df tout ce qui va être extrait
        after = datemax

    if source is None:
        logger.debug("Begin extracting Pushshift data")
        data = getPushshiftData(before, after, subreddit)

        # Will run until all posts have been gathered
        # from the 'after' date up until todays date
        while len(data) > 0:
            for submission in data:
                post_ids.append(submission["id"])
            logger.debug("timestamp = " + str(data[-1]['created_utc']))
            # Calls getPushshiftData() with the created date of the last submission
            data = getPushshiftData(before, data[-1]['created_utc'], subreddit)
        logger.debug("Extracting Pushshift data DONE.")

        data = post_ids

    else:
        logger.debug("ID file detected")
        with open(source, "r") as f:
            data = json.load(f)

    # export du fichier json data
    filename = "posts_{}_{}.json".format(str(subreddit), str(int(before)))
    export(data, folder, original_folder, filename, "json")

    df = pd.DataFrame()
    df = fetch_posts(data, reddit)

    if df_orig is not None:
        df_orig = df_orig[~df_orig['ID'].isin(df['ID'])]
        df = df_orig.append(df)

    # export du dataframe en xlsx
    filename = "posts_{}_{}.xlsx".format(str(subreddit), str(int(before)))
    export(df, folder, original_folder, filename, "xlsx")

    # affichage du temps de traitement
    runtime = time.time() - STARTTIME
    print("Runtime : %.2f seconds" % runtime)


def fetch_posts(data, reddit):
    """
    Extrait les commentaires du subreddit subreddit entre les timestamp \
    beginningtime et endtime. Renvoie un dataframe panda
    """
    columns = ["ID", "Nom", "Date", "Score", "Ratio", "Commentaires", "Flair",
               "Domaine", "Texte", "URL", "Permalien", "Auteur",
               "CSS Flair Auteur", "Texte Flair Auteur", "Doré", "Peut dorer",
               "Caché", "Archivé", "Peut crossposter"]
    df = []
    for x in tqdm(data):
        try:
            submission = reddit.submission(id=str(x))
            df.append({"Score": submission.score,
                       "Auteur": str(submission.author),
                       "CSS Flair Auteur":
                       str(submission.author_flair_css_class),
                       "Texte Flair Auteur": str(submission.author_flair_text),
                       "Ratio": submission.upvote_ratio,
                       "ID": submission.name,
                       "Permalien": str("https://reddit.com" +
                                        submission.permalink),
                       "Nom": submission.title,
                       "URL": submission.url,
                       "Commentaires": submission.num_comments,
                       "Date": submission.created_utc,
                       "Flair": str(submission.link_flair_text),
                       "Texte": str(submission.selftext),
                       "Domaine": submission.domain,
                       "Doré": submission.gilded,
                       "Caché": submission.hidden,
                       "Archivé": submission.archived,
                       "Peut dorer": submission.can_gild,
                       "Peut crossposter": submission.is_crosspostable
                       })
        except Exception as e:
            print("Error : " + str(e))
    logger.debug("Fetching posts DONE.")
    logger.debug("Creating pandas dataframe…")
    df = pd.DataFrame(df)
    df['Date'] = pd.to_datetime(df['Date'], unit='s')
    df = df[columns]
    return df


def export(data, folder, original_folder, filename, type):
    """
    Fonction d'export
    """

    # ouverture du dossier d'export
    if not os.path.exists(folder):
        os.makedirs(folder)
    os.chdir(folder)
    logger.debug("Opening subreddit folder DONE")

    if type == "json":
        # export json
        with open(filename, "w") as f:
            json.dump(data, f)
    elif type == "xlsx":
        writer = pd.ExcelWriter(filename, engine='xlsxwriter',
                                options={'strings_to_urls': False})
        logger.debug("df.to_excel")
        data.to_excel(writer, sheet_name='Sheet1', index=False)
        logger.debug("writer.save")
        writer.save()

    os.chdir(original_folder)


def redditconnect(bot):
    """
    Fonction de connexion à reddit
    """
    user_agent = "python:script:download_posts_subreddit"

    reddit = praw.Reddit(bot, user_agent=user_agent)
    logger.debug(reddit.user.me())
    return reddit


def parse_args():

    parser = argparse.ArgumentParser(description='Download all the posts of a specific subreddit')
    parser.add_argument('-a', '--after', type=str, help='The min unixstamp to download')
    parser.add_argument('-b', '--before', type=str, help='The max unixstamp to download')
    parser.add_argument('--source', type=str, help='The name of the json file containing posts ids')
    parser.add_argument('--file', type=str, help='The name of the xlsx file containing posts already extracted')
    parser.add_argument('-s', '--subreddit', type=str, help='The subreddit to download posts from. Default : /r/france', default="france")
    parser.add_argument('--debug', help="Affiche les informations de déboguage", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.WARNING)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main(parse_args())
