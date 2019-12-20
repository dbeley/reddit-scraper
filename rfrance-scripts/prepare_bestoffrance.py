#!/usr/bin/env python
"""
Parser for an bestoffrance export
"""
import sys
import pandas as pd
import time

STARTTIME = time.time()


def index_containing_substring(the_list, substring):
    for i, s in enumerate(the_list):
        if substring in s:
            return i
    return -1


def main():
    # df = pd.read_excel(sys.argv[1])
    df = pd.read_csv(sys.argv[1], sep="\t", encoding="utf-8")

    Texte = df["Text"].str.split("\n")

    for i, val in enumerate(Texte):
        print(i, val)
        print(str(val[index_containing_substring(Texte[i], "total")]))

    Texte = Texte.apply(pd.Series)
    Texte = Texte.rename(columns=lambda x: "str_" + str(x))

    df = pd.concat([df[:], Texte[:]], axis=1)
    df.to_csv("BestOfFrance_traité.csv", index=False, sep="\t")

    # writer = pd.ExcelWriter(
    #     "BestOfFrance_traité.xlsx",
    #     engine="xlsxwriter",
    #     options={"strings_to_urls": False},
    # )
    # df.to_excel(writer, sheet_name="Sheet1")
    # writer.save()

    # affichage du temps de traitement
    runtime = time.time() - STARTTIME
    print("Runtime : %.2f seconds" % runtime)


if __name__ == "__main__":
    main()
