#!/usr/bin/env python
"""
Get the forumlibre ids in a xlsx file extracted by the fetch_posts_subreddit.py
script
"""
import sys
import pandas as pd
import json
import time

STARTTIME = time.time()


def main():
    df = pd.read_excel(sys.argv[1])
    df_fl = df[df['Flair'] == "Forum Libre"]
    df_fl = df_fl[df_fl['Nom'].str.contains("Forum Libre")]
    df_fl = df_fl[df_fl['Auteur'] == "AutoModerator"]

    id_fl = df_fl['ID'].tolist()
    id_fl = [s[3:] for s in id_fl]
    with open("export_fl.json", "w") as f:
        json.dump(id_fl, f)

    # affichage du temps de traitement
    runtime = time.time() - STARTTIME
    print("Runtime : %.2f seconds" % runtime)


if __name__ == '__main__':
    main()
