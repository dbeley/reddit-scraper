# reddit-scraper

Various scripts to scrape reddit.

- **download_comments_post.py** : Download the comments of one or several posts.
- **download_comments_user.py** : Download the last 1000 comments of one or several users.
- **download_posts_user.py** : Download the posts of one or several users.
- **fetch_posts_subreddit.py** : Download the posts of a subreddit with the help of the Pushshift api.

## Requirements

- tqdm
- praw
- requests
- pandas
- numpy
- xlsxwriter
- xlrd

Needs a praw.ini under the form :

```
[bot]
client_id=id
client_secret=secret
password=password
username=username
```

## Installation of the virtualenv (recommended)

```
pipenv install
```

## Usage

```
python fetch_posts_subreddit.py -s france
```

## Help

### download_comments_post

```
python download_comments_post -h
```

```
usage: download_comments_post.py [-h] [--debug] [-i ID] [-u URL]
                                 [--source SOURCE] [--file FILE]
                                 [--export_format EXPORT_FORMAT]
                                 [--import_format IMPORT_FORMAT]

Download comments of a post or a set of posts (by id or by url)

optional arguments:
  -h, --help            show this help message and exit
  --debug               Display debugging information
  -i ID, --id ID        IDs of the posts to extract (separated by commas)
  -u URL, --url URL     URLs of the posts to extract (separated by commas)
  --source SOURCE       The name of the json file containing posts ids
  --file FILE           The name of the file containing comments already
                        extracted
  --export_format EXPORT_FORMAT
                        Export format (csv or xlsx). Default : csv
  --import_format IMPORT_FORMAT
                        Import format, if used with --file (csv or xlsx).
                        Default : csv
```

### download_comments_user

```
python download_comments_user -h
```

```
usage: download_comments_user.py [-h] [--debug] [-u USERNAME]
                                 [--export_format EXPORT_FORMAT]

Download the last 1000 comments of one or several users

optional arguments:
  -h, --help            show this help message and exit
  --debug               Display debugging information
  -u USERNAME, --username USERNAME
                        The users to download comments from (separated by
                        commas)
  --export_format EXPORT_FORMAT
                        Export format (csv or xlsx). Default : csv
```

### download_posts_user

```
python download_posts_user -h
```

```
usage: download_posts_user.py [-h] [--debug] [-u USERNAME]
                              [--export_format EXPORT_FORMAT]

Download all the posts of one or several users

optional arguments:
  -h, --help            show this help message and exit
  --debug               Display debugging information
  -u USERNAME, --username USERNAME
                        The users to download posts from (separated by commas)
  --export_format EXPORT_FORMAT
                        Export format (csv or xlsx). Default : csv
```

### fetch_posts_subreddit

```
python fetch_posts_subreddit -h
```

```
usage: fetch_posts_subreddit.py [-h] [--debug] [-s SUBREDDIT] [-a AFTER]
                                [-b BEFORE] [--source SOURCE] [--file FILE]
                                [--export_format EXPORT_FORMAT]
                                [--import_format IMPORT_FORMAT]

Download all the posts of a specific subreddit

optional arguments:
  -h, --help            show this help message and exit
  --debug               Display debugging information
  -s SUBREDDIT, --subreddit SUBREDDIT
                        The subreddit to download posts from. Default :
                        /r/france
  -a AFTER, --after AFTER
                        The min unixstamp to download
  -b BEFORE, --before BEFORE
                        The max unixstamp to download
  --source SOURCE       The name of the json file containing posts ids
  --file FILE           The name of the file containing posts already
                        extracted
  --export_format EXPORT_FORMAT
                        Export format (csv or xlsx). Default : csv
  --import_format IMPORT_FORMAT
                        Import format, if used with --file (csv or xlsx).
                        Default : csv
```

