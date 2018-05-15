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
BUFFER = 1000


def getPushshiftData(before, after, sub):
    url = 'https://api.pushshift.io/reddit/search/submission?&size=1000&after='+str(after)+'&subreddit='+str(sub)+'&before='+str(before)
    r = requests.get(url)
    data = json.loads(r.text)
    with open("youpi.json", "w") as f:
        json.dump(r.text, f)
    return data['data']


def main(args):
    # list of post ID's
    post_ids = []
    # Subreddit to query
    sub = args.subreddit
    folder = "Subreddit"
    # Unix timestamp of date to crawl from.
    # 2018/04/01
    # after = "1522618956"
    after = args.after
    before = args.before
    file = args.file
    source = args.source

    if before is None:
        before = int(STARTTIME)

    if file is None:
        print("Begin extracting Pushshift data")
        data = getPushshiftData(before, after, sub)

        # Will run until all posts have been gathered
        # from the 'after' date up until todays date
        while len(data) > 0:
            for submission in data:
                post_ids.append(submission["id"])
            print("timestamp = " + str(data[-1]['created_utc']))
            # Calls getPushshiftData() with the created date of the last submission
            data = getPushshiftData(before, data[-1]['created_utc'], sub)
        print("Extracting Pushshift data DONE.")

        data = {}
        data['sub'] = sub
        data['id'] = post_ids
    else:
        logger.debug("ID file detected")
        with open(file, "r") as f:
            data = json.loads(f)

    if source is not None:
       print("ne marche pas encore")
       exit
       # on charge df
       # on enlève de data tout ceux qui sont présent dans df, sauf ceux qui ont moins
       # d'un mois
       # on enlève de df
    else:
        df = pd.DataFrame()
        df = fetch_posts(data)

    # export du dataframe
    if not os.path.exists(folder):
        os.makedirs(folder)
    os.chdir(folder)
    logger.debug("Opening subreddit folder DONE")

    filename = "posts_{}_{}.json".format(str(sub), str(int(STARTTIME)))
    with open(filename, "w") as f:
        json.dump(data, f)
    export_excel(df, data['sub'], STARTTIME)

    # affichage du temps de traitement
    runtime = time.time() - STARTTIME
    print("Runtime : %.2f seconds" % runtime)


def fetch_posts(data):
    """
    Extrait les commentaires du subreddit subreddit entre les timestamp \
    beginningtime et endtime. Renvoie un dataframe panda
    """
    columns = ["id", "Name", "Date", "Score", "Ratio", "Nbr_comments",
               "Flair", "Domain", "Self text", "url", "permalink",
               "Author", "Author_flair_css", "Author_flair_text", "Gilded"]

    reddit = redditconnect('bot')
    df = []
    for x in tqdm(data["id"]):
        submission = reddit.submission(id=str(x))
        df.append({"Score": submission.score,
                   "Author": str(submission.author),
                   "Author_flair_css": str(submission.author_flair_css_class),
                   "Author_flair_text": str(submission.author_flair_text),
                   "Ratio": submission.upvote_ratio,
                   "id": submission.name,
                   "permalink": str("https://reddit.com" +
                                    submission.permalink),
                   "Name": submission.title,
                   "url": submission.url,
                   "Nbr_comments": submission.num_comments,
                   "Date": submission.created_utc,
                   "Flair": str(submission.link_flair_text),
                   "Self text": str(submission.selftext),
                   "Domain": submission.domain,
                   "Gilded": submission.gilded
                   })
    logger.debug("Fetching posts DONE.")
    logger.debug("Creating pandas dataframe…")
    df = pd.DataFrame(df)
    df = df[columns]
    return df


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

    reddit = praw.Reddit('bot', user_agent=user_agent)
    logger.debug(reddit.user.me())
    return reddit


def parse_args():

    parser = argparse.ArgumentParser(description='Download all the posts of a \
            specific subreddit')
    parser.add_argument('-a', '--after', type=str, help='The min unixstamp to \
            download', default="1115419038")
    parser.add_argument('-b', '--before', type=str, help='The max unixstamp to\
             download')
    parser.add_argument('--source', type=str, help='The name of the file \
            containing posts')
    parser.add_argument('-f', '--file', type=str, help='The name of the file \
            containing posts id')
    parser.add_argument('-s', '--subreddit', type=str, help='The subreddit to \
            download posts from. Default : /r/france', default="france")
    parser.add_argument('--debug', help="Affiche les informations de \
            déboguage", action="store_const", dest="loglevel",
                        const=logging.DEBUG, default=logging.WARNING)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main(parse_args())
