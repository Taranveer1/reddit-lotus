# Reddit post fetching with fallback to Arctic Shift API

import requests

REDDIT_URL = "https://www.reddit.com/r/healthcare.json"
ARCTIC_SHIFT_URL = "https://arctic-shift.photon-reddit.com/api/posts/search"
HEADERS = {
    "User-Agent": "linux:reddit-lotus-bot:v0.1 (by /u/tsflora)"
}


def _parse_reddit_response(data: dict) -> list[dict]:
    """Parse Reddit JSON API response into normalized post dicts."""
    return [
        {
            "id": child["data"]["id"],
            "title": child["data"]["title"],
            "author": child["data"]["author"],
            "link": f"https://www.reddit.com{child['data']['permalink']}",
        }
        for child in data["data"]["children"]
    ]


def _parse_arctic_shift_response(data: dict) -> list[dict]:
    """Parse Arctic Shift API response into normalized post dicts."""
    return [
        {
            "id": post["id"],
            "title": post["title"],
            "author": post["author"],
            "link": f"https://www.reddit.com{post['permalink']}",
        }
        for post in data["data"]
    ]


def fetch_healthcare_posts() -> list[dict]:
    """Fetch recent r/healthcare posts. Tries Reddit first, falls back to Arctic Shift."""
    # Try Reddit JSON API first
    try:
        response = requests.get(REDDIT_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        posts = _parse_reddit_response(response.json())
        print(f"Source: reddit ({len(posts)} posts)")
        return posts
    except (requests.exceptions.RequestException, KeyError) as e:
        print(f"Reddit API failed: {e}")

    # Fall back to Arctic Shift API
    try:
        params = {"subreddit": "healthcare", "limit": 25}
        response = requests.get(ARCTIC_SHIFT_URL, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        posts = _parse_arctic_shift_response(response.json())
        print(f"Source: arctic-shift ({len(posts)} posts)")
        return posts
    except (requests.exceptions.RequestException, KeyError) as e:
        print(f"Arctic Shift API failed: {e}")
        return []


if __name__ == "__main__":
    for post in fetch_healthcare_posts():
        print(post)
