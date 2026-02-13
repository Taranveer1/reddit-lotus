# Reddit API fetch + response parsing
import requests

#url for the reddit community we are parsing the posts from
REDDIT_URL = "https://www.reddit.com/r/healthcare.json" 

HEADERS = {
    "User-Agent": "reddit-lotus-bot/0.1 by tsflora"
}

#fetches the top posts from the subreddit 
def fetch_healthcare_posts(limit=10):
    response = requests.get(REDDIT_URL, headers=HEADERS, params={"limit": limit})

    if response.status_code != 200:
        raise Exception(f"Reddit API error: {response.status_code}")

    data = response.json()

    posts = []
    for child in data["data"]["children"]:
        post_data = child["data"]

          # organizes all the reddit responses into a clean schema
        posts.append({
            "id": post_data["id"],
            "title": post_data["title"],
            "author": post_data["author"],
            "link": f"https://www.reddit.com{post_data['permalink']}"
        })

    return posts

#personal local testing 
if __name__ == "__main__":
    posts = fetch_healthcare_posts()

    for post in posts:
        print(post)