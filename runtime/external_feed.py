from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path
from threading import RLock
from time import monotonic
from typing import Any, Callable
from urllib.parse import quote
from urllib.request import Request, urlopen
import json
import re
import xml.etree.ElementTree as ET


USER_AGENT = "Continuity/0.1 (live traversal frontage test)"
CACHE_SECONDS = 45
MAX_SNIPPET = 320

REDDIT_POPULAR_RSS = "https://www.reddit.com/r/popular/.rss"
LEMMY_NEW = "https://lemmy.world/api/v3/post/list?sort=New&limit=14"
HN_NEW = "https://hacker-news.firebaseio.com/v0/newstories.json"
HN_ITEM = "https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
REUTERS_YOUTUBE = "https://www.youtube.com/feeds/videos.xml?channel_id=UChqUTb7kYRX8-EiaN3XFrSQ"
BBC_NEWS_RSS = "https://feeds.bbci.co.uk/news/rss.xml"

_TAG_RE = re.compile(r"<[^>]+>")
_SPACE_RE = re.compile(r"\s+")


def _clean_text(value: str, *, limit: int = MAX_SNIPPET) -> str:
    value = unescape(_TAG_RE.sub(" ", value or ""))
    value = _SPACE_RE.sub(" ", value).strip()
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def _iso_from_rss(value: str) -> str:
    if not value:
        return ""
    try:
        return parsedate_to_datetime(value).astimezone(timezone.utc).isoformat()
    except (TypeError, ValueError, OverflowError):
        return value


def _fetch(url: str, *, timeout: float = 10) -> bytes:
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json, application/atom+xml, application/rss+xml, application/xml, text/xml;q=0.9, */*;q=0.8",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def _item(
    *,
    item_id: str,
    source_id: str,
    source_name: str,
    source_kind: str,
    title: str,
    url: str,
    published_at: str = "",
    author: str = "",
    context: str = "",
    snippet: str = "",
    metrics: dict[str, Any] | None = None,
    native_type: str = "",
) -> dict[str, Any]:
    return {
        "id": item_id,
        "source_id": source_id,
        "source_name": source_name,
        "source_kind": source_kind,
        "native_type": native_type or source_kind,
        "title": _clean_text(title, limit=240),
        "url": url,
        "published_at": published_at,
        "author": _clean_text(author, limit=120),
        "context": _clean_text(context, limit=140),
        "snippet": _clean_text(snippet),
        "metrics": metrics or {},
    }


def fetch_reddit(limit: int = 12) -> list[dict[str, Any]]:
    root = ET.fromstring(_fetch(REDDIT_POPULAR_RSS))
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    rows = []
    for entry in root.findall("atom:entry", ns)[:limit]:
        link = entry.find("atom:link", ns)
        author = entry.find("atom:author/atom:name", ns)
        content = entry.find("atom:content", ns)
        title = entry.findtext("atom:title", default="", namespaces=ns)
        published = (
            entry.findtext("atom:updated", default="", namespaces=ns)
            or entry.findtext("atom:published", default="", namespaces=ns)
        )
        url = link.attrib.get("href", "") if link is not None else ""
        entry_id = entry.findtext("atom:id", default=url, namespaces=ns)
        rows.append(
            _item(
                item_id=f"reddit:{entry_id}",
                source_id="reddit",
                source_name="Reddit",
                source_kind="social",
                native_type="post",
                title=title,
                url=url,
                published_at=published,
                author=author.text if author is not None else "",
                context="r/popular",
                snippet=content.text if content is not None else "",
            )
        )
    return rows


def fetch_lemmy(limit: int = 12) -> list[dict[str, Any]]:
    data = json.loads(_fetch(LEMMY_NEW).decode("utf-8"))
    rows = []
    for wrapper in (data.get("posts") or [])[:limit]:
        post = wrapper.get("post") or {}
        creator = wrapper.get("creator") or {}
        community = wrapper.get("community") or {}
        counts = wrapper.get("counts") or {}
        local_url = post.get("ap_id") or post.get("url") or ""
        rows.append(
            _item(
                item_id=f"lemmy:{post.get('id', local_url)}",
                source_id="lemmy",
                source_name="Lemmy",
                source_kind="social",
                native_type="post",
                title=post.get("name") or "",
                url=local_url,
                published_at=post.get("published") or "",
                author=creator.get("name") or "",
                context=community.get("name") or "lemmy.world",
                snippet=post.get("body") or "",
                metrics={
                    "score": counts.get("score"),
                    "comments": counts.get("comments"),
                },
            )
        )
    return rows


def _fetch_hn_item(item_id: int) -> dict[str, Any] | None:
    try:
        return json.loads(_fetch(HN_ITEM.format(item_id=item_id), timeout=7).decode("utf-8"))
    except Exception:
        return None


def fetch_hacker_news(limit: int = 12) -> list[dict[str, Any]]:
    ids = json.loads(_fetch(HN_NEW).decode("utf-8"))[:limit]
    stories = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(_fetch_hn_item, item_id) for item_id in ids]
        for future in as_completed(futures):
            story = future.result()
            if story:
                stories.append(story)
    stories.sort(key=lambda x: x.get("time") or 0, reverse=True)
    rows = []
    for story in stories[:limit]:
        story_id = story.get("id")
        external = story.get("url")
        discussion = f"https://news.ycombinator.com/item?id={story_id}"
        published = ""
        if story.get("time"):
            published = datetime.fromtimestamp(
                int(story["time"]), tz=timezone.utc
            ).isoformat()
        rows.append(
            _item(
                item_id=f"hn:{story_id}",
                source_id="hacker_news",
                source_name="Hacker News",
                source_kind="community",
                native_type="story",
                title=story.get("title") or "",
                url=external or discussion,
                published_at=published,
                author=story.get("by") or "",
                context="Hacker News",
                snippet=story.get("text") or "",
                metrics={
                    "score": story.get("score"),
                    "comments": story.get("descendants"),
                    "discussion_url": discussion,
                },
            )
        )
    return rows


def fetch_reuters_youtube(limit: int = 10) -> list[dict[str, Any]]:
    root = ET.fromstring(_fetch(REUTERS_YOUTUBE))
    atom = "http://www.w3.org/2005/Atom"
    yt = "http://www.youtube.com/xml/schemas/2015"
    rows = []
    for entry in root.findall(f"{{{atom}}}entry")[:limit]:
        link = entry.find(f"{{{atom}}}link")
        video_id = entry.findtext(f"{{{yt}}}videoId", default="")
        rows.append(
            _item(
                item_id=f"youtube:{video_id}",
                source_id="youtube_reuters",
                source_name="YouTube · Reuters",
                source_kind="video",
                native_type="video",
                title=entry.findtext(f"{{{atom}}}title", default=""),
                url=link.attrib.get("href", "") if link is not None else "",
                published_at=entry.findtext(f"{{{atom}}}published", default=""),
                author=entry.findtext(f"{{{atom}}}author/{{{atom}}}name", default="Reuters"),
                context="Reuters",
            )
        )
    return rows


def fetch_bbc_news(limit: int = 12) -> list[dict[str, Any]]:
    root = ET.fromstring(_fetch(BBC_NEWS_RSS))
    rows = []
    for node in root.findall("./channel/item")[:limit]:
        url = node.findtext("link", default="")
        guid = node.findtext("guid", default=url)
        rows.append(
            _item(
                item_id=f"bbc:{guid}",
                source_id="bbc_news",
                source_name="BBC News",
                source_kind="news",
                native_type="article",
                title=node.findtext("title", default=""),
                url=url,
                published_at=_iso_from_rss(node.findtext("pubDate", default="")),
                author=node.findtext("author", default="BBC News"),
                context="BBC News",
                snippet=node.findtext("description", default=""),
            )
        )
    return rows


FETCHERS: dict[str, Callable[[], list[dict[str, Any]]]] = {
    "reddit": fetch_reddit,
    "lemmy": fetch_lemmy,
    "hacker_news": fetch_hacker_news,
    "youtube_reuters": fetch_reuters_youtube,
    "bbc_news": fetch_bbc_news,
}

SOURCE_META = {
    "reddit": {"name": "Reddit", "kind": "social", "access": "public RSS"},
    "lemmy": {"name": "Lemmy", "kind": "social", "access": "public API"},
    "hacker_news": {"name": "Hacker News", "kind": "community", "access": "public API"},
    "youtube_reuters": {"name": "YouTube · Reuters", "kind": "video", "access": "public Atom"},
    "bbc_news": {"name": "BBC News", "kind": "news", "access": "public RSS"},
    "bluesky": {"name": "Bluesky", "kind": "social", "access": "public API", "enabled": False, "reason": "public endpoint returns 403 from this host; keep external rather than fabricate data"},
}


class LiveFeed:
    """Read-through live external feed projection.

    Items are fetched and normalized in memory. This class does not persist
    external feed contents. Durable state is created only when a traversal
    touch or another explicit Continuity output is recorded.
    """

    def __init__(self, *, cache_seconds: int = CACHE_SECONDS) -> None:
        self.cache_seconds = cache_seconds
        self._lock = RLock()
        self._cached_at = 0.0
        self._cache: dict[str, Any] | None = None

    def snapshot(self, *, force: bool = False) -> dict[str, Any]:
        now = monotonic()
        with self._lock:
            if (
                not force
                and self._cache is not None
                and now - self._cached_at < self.cache_seconds
            ):
                return self._cache

        items: list[dict[str, Any]] = []
        statuses = []
        with ThreadPoolExecutor(max_workers=len(FETCHERS)) as pool:
            future_map = {
                pool.submit(fetcher): source_id
                for source_id, fetcher in FETCHERS.items()
            }
            for future in as_completed(future_map):
                source_id = future_map[future]
                meta = SOURCE_META[source_id]
                try:
                    source_items = future.result()
                    items.extend(source_items)
                    statuses.append(
                        {
                            "id": source_id,
                            **meta,
                            "enabled": True,
                            "ok": True,
                            "count": len(source_items),
                        }
                    )
                except Exception as exc:
                    statuses.append(
                        {
                            "id": source_id,
                            **meta,
                            "enabled": True,
                            "ok": False,
                            "count": 0,
                            "error": f"{exc.__class__.__name__}: {exc}",
                        }
                    )

        for source_id, meta in SOURCE_META.items():
            if source_id in FETCHERS:
                continue
            statuses.append(
                {
                    "id": source_id,
                    **meta,
                    "ok": False,
                    "count": 0,
                }
            )

        items.sort(key=lambda x: x.get("published_at") or "", reverse=True)
        snapshot = {
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "cache_seconds": self.cache_seconds,
            "items": items,
            "sources": sorted(statuses, key=lambda x: x["name"]),
        }
        with self._lock:
            self._cache = snapshot
            self._cached_at = monotonic()
        return snapshot
