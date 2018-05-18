# reddit-scripts

Various reddit scripts.

Launch the script with the `-h` flag to view how to use.

- **download_comments_post.py** : Download the comments of a post.
- **download_comments_user.py** : Download the 1000 most recents comments of a
    user.
- **download_missing_posts_subreddit.py** : Deprecated, doesn't work since an API update.
- **download_posts_subreddit.py** : Deprecated, doesn't work since an API update.
- **fetch_posts_subreddit.py** : Download the posts of a subreddit.

Needs a praw.ini under the form :

```
[bot]
client_id=id
client_secret=secret
password=password
username=username
```

