# Reddit API fetch + response parsing (with PullPush fallback)

import requests

REDDIT_URL = "https://www.reddit.com/r/healthcare.json"
PULLPUSH_URL = "https://api.pullpush.io/reddit/search/submission/?subreddit=healthcare&sort=desc&size=25"
HEADERS = {
    "User-Agent": "linux:reddit-lotus-bot:v0.1 (by /u/tsflora)"
}


def _parse_reddit(response_json: dict) -> list[dict]:
    """Parse Reddit JSON API response into standardized post dicts."""
    posts = []
    for child in response_json["data"]["children"]:
        post = child["data"]
        posts.append({
            "id": post["id"],
            "title": post["title"],
            "author": post["author"],
            "link": f"https://www.reddit.com{post['permalink']}",
        })
    return posts


def _parse_pullpush(response_json: dict) -> list[dict]:
    """Parse PullPush API response into standardized post dicts."""
    posts = []
    for post in response_json["data"]:
        posts.append({
            "id": post["id"],
            "title": post["title"],
            "author": post["author"],
            "link": f"https://www.reddit.com/r/healthcare/comments/{post['id']}/",
        })
    return posts


def fetch_healthcare_posts() -> list[dict]:
    """Fetch current front page posts from r/healthcare, falling back to PullPush on failure."""
    # Try Reddit first
    try:
        response = requests.get(REDDIT_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        posts = _parse_reddit(response.json())
        print(f"Source: reddit ({len(posts)} posts)")
        return posts
    except requests.exceptions.RequestException as e:
        print(f"Reddit API failed ({e}), falling back to PullPush.")

    # Fallback to PullPush
    try:
        response = requests.get(PULLPUSH_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        posts = _parse_pullpush(response.json())
        print(f"Source: pullpush ({len(posts)} posts)")
        return posts
    except requests.exceptions.RequestException as e:
        print(f"PullPush API also failed: {e}")
        return []


if __name__ == "__main__":
    for post in fetch_healthcare_posts():
        print(post)
