# Persistence layer (seen IDs + current posts)
#Tracks which posts we've already sent to Amplitude and caches the current front page for the web UI.
import modal

store = modal.Dict.from_name("reddit-lotus-store", create_if_missing=True)

SEEN_IDS_KEY = "seen_ids"
CURRENT_POSTS_KEY = "current_posts"


def filter_new(posts: list[dict]) -> list[dict]:
    """Return only unseen posts without marking them as seen."""
    seen_ids = store.get(SEEN_IDS_KEY, set())
    return [p for p in posts if p["id"] not in seen_ids]


def mark_seen(posts: list[dict]) -> None:
    """Add post IDs to the seen set.

    Call after successfully sending events so failed posts can be retried.
    Safe from races: Modal scheduled functions run single-concurrency.
    """
    if not posts:
        return
    seen_ids = store.get(SEEN_IDS_KEY, set())
    seen_ids.update(p["id"] for p in posts)
    store.put(SEEN_IDS_KEY, seen_ids)


def save_current_posts(posts: list[dict]) -> None:
    """Overwrite the current front page posts for the web UI."""
    store.put(CURRENT_POSTS_KEY, posts)


def load_current_posts() -> list[dict]:
    """Read current front page posts for the web UI."""
    return store.get(CURRENT_POSTS_KEY, [])
