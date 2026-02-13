# Reddit API fetch + response parsing
import requests

REDDIT_URL = "https://www.reddit.com/r/healthcare.json"
HEADERS = {
    "User-Agent": "linux:reddit-lotus-bot:v0.1 (by /u/tsflora)"
}


def fetch_healthcare_posts() -> list[dict]:
    """Fetch current front page posts from r/healthcare."""
    response = requests.get(REDDIT_URL, headers=HEADERS, timeout=10)
    response.raise_for_status()

    # Parse each post into a clean schema
    posts = []
    for child in response.json()["data"]["children"]:
        post = child["data"]
        posts.append({
            "id": post["id"],
            "title": post["title"],
            "author": post["author"],
            "link": f"https://www.reddit.com{post['permalink']}",
        })

    return posts


if __name__ == "__main__":
    for post in fetch_healthcare_posts():
        print(post)