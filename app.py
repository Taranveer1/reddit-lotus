# Modal app definition, poller, FastAPI, scheduling

import modal

from reddit import fetch_healthcare_posts
from storage import filter_new_and_mark_seen, save_current_posts
from amplitude import send_event

app = modal.App("reddit-lotus")

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("httpx", "requests")
    .add_local_python_source("reddit", "storage", "amplitude")
)

@app.function(
    image=image,
    schedule=modal.Period(minutes=5),
    secrets=[modal.Secret.from_name("amplitude-secret")],
)
def poll_reddit():
    """Fetch r/healthcare posts, deduplicate, send new ones to Amplitude, update cache."""
    posts = fetch_healthcare_posts()
    if not posts:
        print("No posts fetched from Reddit, skipping cycle.")
        return

    save_current_posts(posts)

    new_posts = filter_new_and_mark_seen(posts)
    print(f"Fetched {len(posts)} posts, {len(new_posts)} are new.")

    sent = 0
    for post in new_posts:
        try:
            send_event(post)
            sent += 1
        except Exception as e:
            print(f"Failed to send event for post {post['id']}: {e}")

    print(f"Sent {sent}/{len(new_posts)} events to Amplitude.")
