# Reddit post fetching via PullPush API

import requests

PULLPUSH_URL = "https://api.pullpush.io/reddit/search/submission/?subreddit=healthcare&sort=desc&size=25"
HEADERS = {
    "User-Agent": "linux:reddit-lotus-bot:v0.1 (by /u/tsflora)"
}


def fetch_healthcare_posts() -> list[dict]:
    """Fetch recent r/healthcare posts from PullPush API."""
    try:
        response = requests.get(PULLPUSH_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"PullPush API failed: {e}")
        return []

    posts = []
    for post in response.json()["data"]:
        posts.append({
            "id": post["id"],
            "title": post["title"],
            "author": post["author"],
            "link": f"https://www.reddit.com/r/healthcare/comments/{post['id']}/",
        })

    print(f"Source: pullpush ({len(posts)} posts)")
    return posts


if __name__ == "__main__":
    for post in fetch_healthcare_posts():
        print(post)
