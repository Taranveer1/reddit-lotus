# reddit-lotus

A web application that continuously mirrors posts from r/healthcare into Amplitude and displays the current front page. Built on [Modal](https://modal.com) as a serverless ASGI backend.

## Live App

- **Web UI:** https://taranveersinghflora--reddit-lotus-web.modal.run
- **Poller:** Runs every 5 minutes on Modal's scheduler

## Architecture

```
┌─────────────┐         ┌──────────────────────────────────────────┐
│   Browser   │────────▶│              Modal Cloud                 │
└─────────────┘         │                                          │
                        │  ┌────────────┐     ┌────────────────┐   │
                        │  │  FastAPI    │────▶│  Modal Dict    │   │
                        │  │  (ASGI)    │     │  (storage)     │   │
                        │  └────────────┘     └───────┬────────┘   │
                        │                             │            │
                        │  ┌────────────┐             │            │
┌─────────────┐         │  │  Poller    │─────────────┘            │
│   Reddit    │◀────────│  │  (5 min)   │                          │
│   API       │────────▶│  │            │──────┐                   │
└─────────────┘         │  └────────────┘      │                   │
                        └──────────────────────┼───────────────────┘
                                               │
                        ┌──────────────────────▼───────────────────┐
                        │            Amplitude                      │
                        │     (reddit_post_ingested events)         │
                        └──────────────────────────────────────────┘
```

**Two independent paths:**

1. **Ingestion (scheduled):** Poller fetches r/healthcare posts → filters unseen posts → sends `reddit_post_ingested` events to Amplitude → marks successfully sent posts as seen → caches all posts for the web UI.

2. **Display (on-demand):** Browser requests the web UI → FastAPI reads cached posts from Modal Dict → renders server-side HTML.

## Deduplication Strategy

Posts are deduplicated by `id` using a persistent set stored in Modal Dict.

The key correctness property: **posts are marked as seen only after their Amplitude event is successfully sent.** If `send_event` fails for a post, that post remains unseen and will be retried on the next poll cycle. This ensures at-least-once delivery to Amplitude rather than at-most-once.

```
new_posts = filter_new(posts)       # check only, no side effects
for post in new_posts:
    try:
        send_event(post)            # send to Amplitude
        sent_posts.append(post)     # track successes
    except Exception:
        log failure, continue       # don't block remaining posts
mark_seen(sent_posts)               # persist only after success
```

## Race Condition Handling

Modal scheduled functions run with **single concurrency by default** — only one instance of `poll_reddit` executes at a time. This means the read-modify-write cycle on `seen_ids` is safe without explicit locking:

- No concurrent writers: the poller is the only function that writes to `seen_ids`.
- The web UI only reads `current_posts`, never writes to `seen_ids`.
- No overlapping poll cycles: if a cycle runs long, the next one waits.

No additional locks, mutexes, or atomic operations are needed.

## Reddit Cloud IP Blocking

Reddit's public JSON endpoint (`https://www.reddit.com/r/healthcare.json`) returns 403 errors from cloud provider IP ranges, including Modal's infrastructure. This is a known Reddit restriction affecting all cloud-hosted applications, not specific to this project.

**Workaround:** The app tries the spec-required Reddit endpoint first. If blocked, it falls back to [Arctic Shift](https://arctic-shift.photon-reddit.com/), a third-party API that indexes Reddit posts in near-real-time. Both sources are parsed into the same schema. The fallback is logged on each cycle.

Arctic Shift returns posts sorted by creation time (newest first) rather than Reddit's "hot" ranking algorithm. The pipeline logic is identical regardless of source.

## File Structure

```
reddit-lotus/
├── app.py              # Modal app: scheduled poller + FastAPI web UI
├── reddit.py           # Reddit API fetch with Arctic Shift fallback
├── storage.py          # Modal Dict persistence (dedup + post cache)
├── amplitude.py        # Amplitude HTTP API event sending
├── templates/
│   └── index.html      # Server-rendered HTML template
├── requirements.txt    # Python dependencies
└── README.md
```

## Setup & Deployment

**Prerequisites:** Python 3.12+, Modal CLI authenticated

```bash
# Install dependencies
pip install -r requirements.txt

# Create Modal secret
modal secret create amplitude-secret AMPLITUDE_API_KEY=<your-key>

# Test locally (reddit.py fetches directly, works outside cloud IPs)
python reddit.py

# Test a single poll cycle on Modal
modal run app.py::poll_reddit

# Deploy (starts 5-min scheduler + web UI)
modal deploy app.py
```

## Tech Stack

- **Runtime:** Modal (serverless Python)
- **Web framework:** FastAPI (ASGI)
- **HTTP clients:** `requests` (Reddit), `httpx` (Amplitude)
- **Storage:** Modal Dict (key-value, persistent)
- **Scheduling:** `modal.Period(minutes=5)`
- **Frontend:** Server-rendered HTML with Jinja2

## Production Improvements

Given more time, I would add:

- **Retry with backoff** for failed Amplitude events instead of relying on next-cycle retry.
- **Bounded seen_ids set** — currently grows unbounded. In production, prune IDs older than a configurable window.
- **Health check endpoint** (`/health`) reporting last successful poll time and post count.
- **Structured logging** with timestamps and log levels instead of print statements.
- **Monitoring/alerting** on consecutive poll failures or Amplitude send errors.
- **Handle removed posts** — detect when posts disappear from the subreddit and optionally track removal events.