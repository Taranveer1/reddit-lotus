"""Amplitude HTTP event sending."""

import os

import httpx

AMPLITUDE_URL = "https://api2.amplitude.com/2/httpapi"


def send_event(post: dict) -> None:
    """Send a reddit_post_ingested event to Amplitude for a single post."""
    api_key = os.environ["AMPLITUDE_API_KEY"]
    payload = {
        "api_key": api_key,
        "events": [
            {
                "event_type": "reddit_post_ingested",
                "user_id": post["author"],
                "event_properties": {
                    "title": post["title"],
                    "link": post["link"],
                    "author": post["author"],
                },
            }
        ],
    }
    response = httpx.post(AMPLITUDE_URL, json=payload, timeout=10)
    response.raise_for_status()


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    dummy_post = {
        "id": "test_001",
        "title": "Test Post from reddit-lotus",
        "author": "test_user",
        "link": "https://www.reddit.com/r/healthcare/comments/test",
    }
    send_event(dummy_post)
    print("Event sent. Check Amplitude dashboard.")
