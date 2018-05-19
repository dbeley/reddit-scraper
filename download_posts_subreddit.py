#!/usr/bin/env python
"""
Download all the posts from a subreddit and export it in xlsx.
"""

import argparse
import logging
import os
import time

import pandas as pd
import praw
from tqdm import tqdm

logger = logging.getLogger()
STARTTIME = time.time()
BUFFER = 1000


def main(args):

    subreddit = args.subreddit
    file = args.file
    temps = args.time
    folder = "Subreddit"
    type = "xls"
    timemois = int(time.time()) - 600000

    # Définition du dernier timestamp à télécharger
    if not temps is None:
        logger.debug("Timestamp défini")
        endtime = int(temps)
    else:
        logger.debug("Timestamp non défini")
        endtime = int(time.time())
    # Définition du premier timestamp à télécharger
    if not file is None:
        logger.debug("Fichier défini")
        nom, type = os.path.splitext(file)
        beginningtime = int(nom.rsplit("_")[-1])
        subreddit = str(nom.rsplit("_")[-2])
        file = file.find('posts_')
        if beginningtime >= timemois:
            beginningtime = timemois
    elif args.beginning is not None:
        beginningtime = args.beginning
    else:
        logger.debug("Fichier non défini")
        beginningtime = 1212086987

    a = 0
    number = BUFFER
    steptime = endtime
    df = pd.DataFrame()

    # Tant que le nombre de posts est égal au buffer
    while (number == BUFFER):
        logger.debug("beginningtime = " + str(beginningtime))
        logger.debug("endtime = " + str(endtime))
        # récupération du dataframe (inversé) des posts, du nombre de posts, et du dernier timestamp
        df, number, steptime = fetch_posts(
            df, subreddit, beginningtime, steptime, a)
        # Suppression de la dernière ligne du dataframe, puisque la prochaine recherche l'incluera
        if number == BUFFER:
            df = df.drop(df.index[len(df) - 1])
        a = a + 1
        logger.debug("While machin, boucle numéro " + str(a))
        logger.debug("endtime est " + str(endtime))

    df = df.sort_values("Date")
    # Si un fichier a déjà été défini, on concatène son contenu avec le dataframe
    if not file is None:
        logger.debug("Fichier défini")
        df = concatenate_excel(df, args.file, beginningtime)
    logger.debug("Opening subreddit folder...")
    if not os.path.exists(folder):
        os.makedirs(folder)
    os.chdir(folder)
    logger.debug("Opening subreddit folder DONE")

    # export du dataframe
    export(df, subreddit, endtime)

    # affichage du temps de traitement
    runtime = time.time() - STARTTIME
    print("Runtime : %.2f seconds" % runtime)


def fetch_posts(df, subreddit, beginningtime, endtime, a):
    """
    Extrait les commentaires du subreddit subreddit entre les timestamp \
    beginningtime et endtime. Renvoie un dataframe panda
    """
    n = 0
    columns = ["id", "Name", "Date", "Score", "Ratio", "Nbr_comments",
               "Flair", "Domain", "Self text", "url", "permalink",
               "Author", "Author_flair_css", "Author_flair_text", "Gilded"]
    reddit = redditconnect('test')
    sub = reddit.subreddit(subreddit)
    dd = []
    # Récupération des posts entre beginningtime et endtime
    for x in sub.submissions(beginningtime, endtime):
        n = n + 1
        timestamp = x.created_utc
        print("Fetching post {} for subreddit {} at timestamp {}…".format(
            str(n), str(subreddit), str(timestamp)))
        dd.append({"Score": x.score,
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
                  })

        # Sortie de la boucle si buffer atteint
        if n == BUFFER:
            print("N = " + str(BUFFER) + ", arrêt…")
            break
    print("Fetching posts DONE.")
    print("Creating pandas dataframe…")
    # Code à optimiser (d, dd, df)
    dd = pd.DataFrame(dd)
    dd = dd[columns]
    df = df.append(dd)
    logger.debug("Creating pandas dataframe DONE.")
    return df, n, timestamp


def concatenate_excel(df, file, beginningtime):
    """
    Concatène le dataframe et le fichier excel entré en param.
    Renvoie un dataframe.
    """
    logger.debug("Concatenate_excel")
    df_old = pd.read_excel(file)
    df_old = df_old.loc[df_old['Date'] < beginningtime]
    logger.debug("fichier lu")
    df = df_old.append(df)
    logger.debug("nouveau dataframe créé")
    return df


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
    user_agent = "python:script:download_posts_subreddit"

    reddit = praw.Reddit(bot, user_agent=user_agent)
    return reddit


def parse_args():

    parser = argparse.ArgumentParser(
        description='Download all the posts of a specific subreddit')
    parser.add_argument(
       '-f', '--file', type=str, help='The name of the file containing the old data, must contains the timestamp of the last record')
    parser.add_argument('-s', '--subreddit', type=str,
                        help='The subreddit to download posts from. Default : /r/france', default="france")
    parser.add_argument('-t', '--time', type=int,
                        help='The max unixstamp to download', default=None)
    parser.add_argument('--debug', help="Affiche les informations de déboguage",
                        action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.WARNING)
    parser.add_argument('-b', '--beginning', type=int,
                        help='the min unixstamp to download', default=None)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main(parse_args())
