#!/usr/bin/env python
"""
Download posts from a subreddit and export it in xlsx or csv.
"""

from psaw import PushshiftAPI
import argparse
import time
import logging
import pandas as pd
from pathlib import Path

logger = logging.getLogger()
temps_debut = time.time()

COLUMNS = [
    "date",
    "date_utc",
    "author",
    # "author_flair_css_class",
    # "author_flair_richtext",
    # "author_flair_text",
    # "author_flair_type",
    # "brand_safe",
    # "can_mod_post",
    # "contest_mode",
    "created_utc",
    "domain",
    "full_link",
    # "gilded",
    "id",
    # "is_crosspostable",
    # "is_original_content",
    # "is_reddit_media_domain",
    # "is_self",
    # "is_video",
    # "link_flair_background_color",
    # "link_flair_css_class",
    # "link_flair_richtext",
    # "link_flair_template_id",
    "link_flair_text",
    # "link_flair_text_color",
    # "link_flair_type",
    # "locked",
    # "no_follow",
    "num_comments",
    # "num_crossposts",
    # "over_18",
    # "parent_whitelist_status",
    "permalink",
    # "pinned",
    # "post_hint",
    # "preview",
    # "retrieved_on",
    # "rte_mode",
    "score",
    "selftext",
    # "send_replies",
    # "spoiler",
    # "stickied",
    "subreddit",
    # "subreddit_id",
    "subreddit_subscribers",
    # "subreddit_type",
    "thumbnail",
    # "thumbnail_height",
    # "thumbnail_width",
    "title",
    "url",
    # "whitelist_status",
    "created",
    # "media",
    # "media_embed",
    # "secure_media",
    # "secure_media_embed",
    # "approved_at_utc",
    # "banned_at_utc",
    # "suggested_sort",
    # "view_count",
    # "author_created_utc",
    # "author_fullname",
    # "distinguished",
    # "author_flair_background_color",
    # "author_flair_template_id",
    # "author_flair_text_color",
    # "author_patreon_flair",
    # "gildings",
    # "is_meta",
    # "is_robot_indexable",
    # "media_only",
    # "pwls",
    # "wls",
    # "author_id",
    # "all_awardings",
    # "allow_live_comments",
    # "author_premium",
    # "awarders",
    # "total_awards_received",
]


def main(args):
    api = PushshiftAPI()
    folder = "Subreddit"
    Path(folder).mkdir(parents=True, exist_ok=True)

    if args.subreddit:
        subreddit = [x.strip() for x in args.subreddit.split(",")]
    else:
        logger.error("Use -s to set the subreddit")
        exit()

    for i in subreddit:
        try:
            df = fetch_posts(api, i)
            df["date_utc"] = pd.to_datetime(df["created_utc"], unit="s")
            df["date"] = pd.to_datetime(df["created"], unit="s")
            df["permalink"] = "https://old.reddit.com" + df["permalink"].astype(str)
            df = df[df.columns.intersection(COLUMNS)]
            filename = f"{folder}/posts_{i}_{int(time.time())}"
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
            logger.error("Complete error : %s", e)

    logger.info("Runtime : %.2f seconds" % (time.time() - temps_debut))


def fetch_posts(api, subreddit):
    res = api.search_submissions(subreddit=subreddit)
    df = pd.DataFrame([thing.d_ for thing in res])
    return df


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
        "-s", "--subreddit", type=str, help="Subreddit", required=True,
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
