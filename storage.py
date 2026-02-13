# Persistence layer (seen IDs + current posts)
#Tracks which posts we've already sent to Amplitude and caches the current front page for the web UI.
import modal

store = modal.Dict.from_name("reddit-lotus-store", create_if_missing=True)

SEEN_IDS_KEY = "seen_ids"
CURRENT_POSTS_KEY = "current_posts"


def filter_new_and_mark_seen(posts: list[dict]) -> list[dict]:
    """Return only unseen posts and mark them as seen.

    Safe from races: Modal scheduled functions run single-concurrency.
    """
    seen_ids = store.get(SEEN_IDS_KEY, set())
    new_posts = [p for p in posts if p["id"] not in seen_ids]
    if new_posts:
        seen_ids.update(p["id"] for p in new_posts)
        store.put(SEEN_IDS_KEY, seen_ids)
    return new_posts


def save_current_posts(posts: list[dict]) -> None:
    """Overwrite the current front page posts for the web UI."""
    store.put(CURRENT_POSTS_KEY, posts)


def load_current_posts() -> list[dict]:
    """Read current front page posts for the web UI."""
    return store.get(CURRENT_POSTS_KEY, [])
