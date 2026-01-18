import os
import time
from typing import Callable, Optional


def mastodon_stream_instance(instance: str, callback: Callable[[dict], None], since_id: Optional[str] = None):
    """Simple polling connector for Mastodon timelines using `mastodon.py` if available.

    Falls back to raising an informative error if `mastodon` is not installed.
    """
    try:
        from mastodon import Mastodon
    except Exception as e:
        raise RuntimeError('mastodon.py not installed') from e
    m = Mastodon(api_base_url=instance, access_token=os.environ.get('MASTODON_TOKEN'))
    timeline = m.timeline_home(since_id=since_id)
    for toot in timeline:
        callback(toot)


def reddit_poll(subreddit: str, callback: Callable[[dict], None], interval: int = 30):
    """Simple polling connector for Reddit using PRAW if available; otherwise polls RSS.
    """
    try:
        import praw
        reddit = praw.Reddit(client_id=os.environ.get('REDDIT_CLIENT_ID'),
                             client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
                             user_agent='verity-stream')
        sub = reddit.subreddit(subreddit)
        for post in sub.new(limit=50):
            callback({'id': post.id, 'title': post.title, 'selftext': post.selftext})
        while True:
            time.sleep(interval)
            for post in sub.new(limit=10):
                callback({'id': post.id, 'title': post.title, 'selftext': post.selftext})
    except Exception:
        # fallback: poll subreddit RSS feed
        import requests
        feed = f'https://www.reddit.com/r/{subreddit}/new/.rss'
        while True:
            try:
                r = requests.get(feed, headers={'User-Agent': 'verity-stream'}, timeout=10)
                if r.status_code == 200:
                    callback({'rss': r.text})
            except Exception:
                pass
            time.sleep(interval)
