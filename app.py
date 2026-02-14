# Modal app definition, poller, FastAPI, scheduling

import modal

from reddit import fetch_healthcare_posts
from storage import filter_new_and_mark_seen, load_current_posts, save_current_posts
from amplitude import send_event

app = modal.App("reddit-lotus")

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("httpx", "requests", "fastapi", "jinja2")
    .add_local_python_source("reddit", "storage", "amplitude")
    .add_local_dir("templates", remote_path="/root/templates")
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


@app.function(image=image)
@modal.asgi_app()
def web():
    from fastapi import FastAPI, Request
    from fastapi.responses import HTMLResponse
    from fastapi.templating import Jinja2Templates

    web_app = FastAPI()
    templates = Jinja2Templates(directory="/root/templates")

    @web_app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        posts = load_current_posts()
        return templates.TemplateResponse("index.html", {"request": request, "posts": posts})

    return web_app
