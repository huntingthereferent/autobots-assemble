from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from threading import RLock
from time import monotonic
from typing import Any, Callable
from urllib.request import Request, urlopen
import json
import re
import xml.etree.ElementTree as ET


USER_AGENT = "Continuity/0.1 (live traversal frontage test)"
CACHE_SECONDS = 45
MAX_SNIPPET = 640

REDDIT_POPULAR_RSS = "https://www.reddit.com/r/popular/.rss"
HN_NEW = "https://hacker-news.firebaseio.com/v0/newstories.json"
HN_ITEM = "https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
REUTERS_YOUTUBE = "https://www.youtube.com/feeds/videos.xml?channel_id=UChqUTb7kYRX8-EiaN3XFrSQ"
BBC_NEWS_RSS = "https://feeds.bbci.co.uk/news/rss.xml"

# Topic admission follows the publisher's feed scope, never headline guesses.
REPORT_FEEDS = {
    "bbc_world": {"name": "BBC World", "publisher": "BBC News",
        "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "topics": ("world",),
        "documentation": "https://support.bbc.co.uk/platform/feeds/NewsFeeds.htm"},
    "bbc_sport": {"name": "BBC Sport", "publisher": "BBC Sport",
        "url": "https://feeds.bbci.co.uk/sport/rss.xml", "topics": ("sports",),
        "documentation": "https://www.bbc.co.uk/sport/articles/cqllxj2n4kyo"},
    "bbc_education": {"name": "BBC Education", "publisher": "BBC News",
        "url": "https://feeds.bbci.co.uk/news/education/rss.xml", "topics": ("learning",),
        "documentation": "https://support.bbc.co.uk/platform/feeds/UkNews.htm"},
    "bls_productivity": {"name": "BLS Productivity and Costs", "publisher": "Bureau of Labor Statistics",
        "url": "https://www.bls.gov/feed/prod2.rss", "topics": ("industry",),
        "documentation": "https://www.bls.gov/feed/"},
    "bls_jobs": {"name": "BLS Job Openings and Labor Turnover", "publisher": "Bureau of Labor Statistics",
        "url": "https://www.bls.gov/feed/jolts.rss", "topics": ("work",),
        "documentation": "https://www.bls.gov/feed/"},
    "sec_releases": {"name": "SEC Press Releases", "publisher": "Securities and Exchange Commission",
        "url": "https://www.sec.gov/news/pressreleases.rss", "topics": ("markets",),
        "documentation": "https://www.sec.gov/about/rss-feeds"},
    "nsf_news": {"name": "NSF Research News", "publisher": "National Science Foundation",
        "url": "https://www.nsf.gov/rss/rss_www_news.xml", "topics": ("research",),
        "documentation": "https://www.nsf.gov/rss"},
    "loc_music": {"name": "Library of Congress Performing Arts", "publisher": "Library of Congress",
        "url": "https://blogs.loc.gov/music/feed/", "topics": ("culture",),
        "documentation": "https://blogs.loc.gov/music/"},
    "cpsc_recalls": {"name": "CPSC Product Recalls", "publisher": "Consumer Product Safety Commission",
        "url": "https://www.cpsc.gov/Newsroom/CPSC-RSS-Feed/Recalls-RSS", "topics": ("household",),
        "documentation": "https://www.cpsc.gov/Newsroom/CPSC-RSS-Feed"},
}


# Country denotes the publishing institution's jurisdiction, not every claim's geography.
COUNTRY_REPORT_FEEDS = {
    "ca_manufacturing": {"name": "Statistics Canada Manufacturing", "publisher": "Statistics Canada", "url": "https://www150.statcan.gc.ca/n1/rss/dai-quo/16-eng.atom", "topics": ("industry",)},
    "ca_labour": {"name": "Statistics Canada Labour", "publisher": "Statistics Canada", "url": "https://www150.statcan.gc.ca/n1/rss/dai-quo/14-eng.atom", "topics": ("work",)},
    "ca_education": {"name": "Statistics Canada Education", "publisher": "Statistics Canada", "url": "https://www150.statcan.gc.ca/n1/rss/dai-quo/37-eng.atom", "topics": ("learning",)},
    "ca_households": {"name": "Statistics Canada Families and Households", "publisher": "Statistics Canada", "url": "https://www150.statcan.gc.ca/n1/rss/dai-quo/39-eng.atom", "topics": ("household",)},
    "ca_science": {"name": "Statistics Canada Science and Technology", "publisher": "Statistics Canada", "url": "https://www150.statcan.gc.ca/n1/rss/dai-quo/27-eng.atom", "topics": ("research",)},
    "au_releases": {"name": "RBA Media Releases", "publisher": "Reserve Bank of Australia", "url": "https://www.rba.gov.au/rss/rss-cb-media-releases.xml", "topics": ("markets",)},
    "au_research": {"name": "RBA Research Discussion Papers", "publisher": "Reserve Bank of Australia", "url": "https://www.rba.gov.au/rss/rss-cb-rdp.xml", "topics": ("research",)},
    "de_latest": {"name": "Bundesbank Latest", "publisher": "Deutsche Bundesbank", "url": "https://www.bundesbank.de/service/rss/en/633306/feed.rss", "topics": ("markets",)},
    "de_research": {"name": "Bundesbank Discussion Papers", "publisher": "Deutsche Bundesbank", "url": "https://www.bundesbank.de/service/rss/en/633292/feed.rss", "topics": ("research",)},
}
_COUNTRY_SCOPES = {
    "ca": ("CA", "Canada", "https://www.statcan.gc.ca/en/sc/rss"),
    "au": ("AU", "Australia", "https://www.rba.gov.au/updates/rss-feeds.html"),
    "de": ("DE", "Germany", "https://www.bundesbank.de/en/homepage/rss/deutsche-bundesbank-s-rss-feed-620440"),
}
for _key, _spec in COUNTRY_REPORT_FEEDS.items():
    _code, _country, _documentation = _COUNTRY_SCOPES[_key.split("_")[0]]
    _spec.update(country_code=_code, country=_country, language="en",
                 country_basis="publisher_jurisdiction", documentation=_documentation)
    _spec["topics"] += ("world:countries:" + _country.lower(),)
REPORT_FEEDS.update(COUNTRY_REPORT_FEEDS)

_TAG_RE = re.compile(r"<[^>]+>")
_SPACE_RE = re.compile(r"\s+")


def _clean_text(value: str, *, limit: int = MAX_SNIPPET) -> str:
    value = unescape(_TAG_RE.sub(" ", value or ""))
    value = _SPACE_RE.sub(" ", value).strip()
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def _many(values) -> list[str]:
    return list(dict.fromkeys(str(x).strip() for x in values or () if str(x).strip()))


def _clean_reddit_snippet(value: str) -> str:
    text = _clean_text(value)
    text = re.sub(
        r"\s*submitted by\s+/u/\S+(?:\s+to\s+r/\S+)?\s*",
        " ",
        text,
        flags=re.I,
    )
    text = re.sub(r"\s*\[(?:link|comments?)\]\s*", " ", text, flags=re.I)
    return _clean_text(text)


def _clean_reuters_description(value: str) -> str:
    text = _clean_text(value)
    promo_markers = (
        "Keep up with the latest news",
        "Subscribe:",
        "Follow Reuters",
        "Reuters on Facebook",
        "Reuters on X:",
        "Reuters on Instagram:",
        "Join host",
    )
    cut = len(text)
    lowered = text.casefold()
    for marker in promo_markers:
        pos = lowered.find(marker.casefold())
        if pos >= 0:
            cut = min(cut, pos)
    text = text[:cut].strip()
    text = re.sub(r"(?:\s+#[\w-]+){2,}\s*$", "", text).strip()
    return _clean_text(text)


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
    provider: str,
    provider_surface: str,
    medium: str,
    title: str,
    url: str,
    publisher: str = "",
    roles: tuple[str, ...] | list[str] = (),
    topics: tuple[str, ...] | list[str] = (),
    published_at: str = "",
    author: str = "",
    context: str = "",
    snippet: str = "",
    metrics: dict[str, Any] | None = None,
    native_type: str = "",
) -> dict[str, Any]:
    roles_clean = _many(roles)
    topics_clean = _many(topics)
    publisher = _clean_text(publisher, limit=120)
    provider = _clean_text(provider, limit=120)
    source_name = provider
    if publisher and publisher.casefold() != provider.casefold():
        source_name = f"{provider} · {publisher}"

    return {
        "id": item_id,
        # source_id is the adapter/provider stream key used for balancing.
        "source_id": source_id,
        "source_name": source_name,
        # These axes are deliberately independent.
        "provider": provider,
        "provider_surface": provider_surface,
        "publisher": publisher,
        "medium": medium,
        "roles": roles_clean,
        "topics": topics_clean,
        "native_type": native_type or medium,
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
                provider="Reddit",
                provider_surface="social_platform",
                medium="post",
                roles=("social", "community"),
                title=title,
                url=url,
                published_at=published,
                author=author.text if author is not None else "",
                context="r/popular",
                snippet=_clean_reddit_snippet(
                    content.text if content is not None else ""
                ),
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
                provider="Hacker News",
                provider_surface="community",
                medium="link" if external else "discussion",
                roles=("community",),
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
    media = "http://search.yahoo.com/mrss/"
    rows = []
    for entry in root.findall(f"{{{atom}}}entry")[:limit]:
        link = entry.find(f"{{{atom}}}link")
        video_id = entry.findtext(f"{{{yt}}}videoId", default="")
        description = entry.findtext(
            f"{{{media}}}group/{{{media}}}description",
            default="",
        )
        rows.append(
            _item(
                item_id=f"youtube:{video_id}",
                source_id="youtube_reuters",
                provider="YouTube",
                provider_surface="video_platform",
                publisher="Reuters",
                medium="video",
                roles=("news",),
                title=entry.findtext(f"{{{atom}}}title", default=""),
                url=link.attrib.get("href", "") if link is not None else "",
                published_at=entry.findtext(f"{{{atom}}}published", default=""),
                author=entry.findtext(
                    f"{{{atom}}}author/{{{atom}}}name", default="Reuters"
                ),
                context="Reuters",
                snippet=_clean_reuters_description(description),
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
                provider="BBC News",
                provider_surface="news_site",
                publisher="BBC News",
                medium="article",
                roles=("news",),
                title=node.findtext("title", default=""),
                url=url,
                published_at=_iso_from_rss(node.findtext("pubDate", default="")),
                author=node.findtext("author", default="BBC News"),
                context="BBC News",
                snippet=node.findtext("description", default=""),
            )
        )
    return rows


def fetch_report_feed(source_id: str, limit: int = 8) -> list[dict[str, Any]]:
    """Bounded RSS/Atom reports with explicit publisher-feed scope provenance."""
    spec = REPORT_FEEDS[source_id]
    root = ET.fromstring(_fetch(spec["url"], timeout=7))
    atom = "{http://www.w3.org/2005/Atom}"
    rdf = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
    rss1 = "{http://purl.org/rss/1.0/}"
    dc = "{http://purl.org/dc/elements/1.1/}"
    is_atom = root.tag == atom + "feed"
    is_rdf = root.tag == rdf + "RDF"
    if is_atom:
        nodes = root.findall(atom + "entry")
    elif root.tag == "rss":
        nodes = root.findall("./channel/item")
    elif is_rdf:
        nodes = root.findall(rss1 + "item")
    else:
        raise ValueError("response is not a supported RSS or Atom feed")
    rows = []
    for node in nodes[:max(0, limit)]:
        if is_atom:
            url = next((link.get("href", "") for link in node.findall(atom + "link")
                        if link.get("rel", "alternate") == "alternate"), "")
            title_node = node.find(atom + "title")
            title = "".join(title_node.itertext()) if title_node is not None else ""
            entry_id = node.findtext(atom + "id", default=url)
            published = node.findtext(atom + "published", default="") or node.findtext(atom + "updated", default="")
            snippet_node = node.find(atom + "summary")
            if snippet_node is None:
                snippet_node = node.find(atom + "content")
            snippet = "".join(snippet_node.itertext()) if snippet_node is not None else ""
            author = node.findtext(atom + "author/" + atom + "name", default="")
            categories = [x.get("term", "") for x in node.findall(atom + "category")]
        else:
            prefix = rss1 if is_rdf else ""
            url = node.findtext(prefix + "link", default="")
            title = node.findtext(prefix + "title", default="")
            entry_id = node.findtext(prefix + "guid", default="") or node.get(rdf + "about", "") or url
            published = _iso_from_rss(node.findtext(prefix + "pubDate", default="")) or node.findtext(dc + "date", default="")
            snippet = node.findtext(prefix + "description", default="")
            author = node.findtext(prefix + "author", default="") or node.findtext(dc + "creator", default="")
            categories = [x.text or "" for x in node.findall(prefix + "category") + node.findall(dc + "subject")]
        if not url.startswith(("https://", "http://")):
            continue
        row = _item(item_id=f"{source_id}:{entry_id}", source_id=source_id,
                    provider=spec["publisher"], publisher=spec["publisher"],
                    provider_surface="report_feed", medium="article", roles=("news",),
                    topics=spec["topics"], title=title, url=url, published_at=published,
                    author=author, context=spec["name"], snippet=snippet)
        row["native_categories"] = _many(categories)
        for field in ("country_code", "country", "country_basis", "language"):
            if field in spec:
                row[field] = spec[field]
        row["topic_basis"] = {"kind": "publisher_feed_scope", "feed_url": spec["url"],
                              "documentation": spec["documentation"], "topics": list(spec["topics"])}
        rows.append(row)
    return rows


FETCHERS: dict[str, Callable[[], list[dict[str, Any]]]] = {
    "reddit": fetch_reddit,
    "hacker_news": fetch_hacker_news,
    "youtube_reuters": fetch_reuters_youtube,
    "bbc_news": fetch_bbc_news,
}
FETCHERS.update({source_id: (lambda key=source_id: fetch_report_feed(key))
                 for source_id in REPORT_FEEDS})

SOURCE_META = {
    "reddit": {"name": "Reddit", "surface": "social_platform", "access": "public RSS"},
    "hacker_news": {"name": "Hacker News", "surface": "community", "access": "public API"},
    "youtube_reuters": {
        "name": "YouTube · Reuters",
        "surface": "video_platform",
        "access": "public Atom",
    },
    "bbc_news": {"name": "BBC News", "surface": "news_site", "access": "public RSS"},
    "bluesky": {
        "name": "Bluesky",
        "surface": "social_platform",
        "access": "public API",
        "enabled": False,
        "reason": "public endpoint returns 403 from this host; keep external rather than fabricate data",
    },
}
SOURCE_META.update({key: {"name": spec["name"], "surface": "report_feed",
                         "access": "public RSS / Atom", "feed_url": spec["url"],
                         "documentation": spec["documentation"],
                         "topics": list(spec["topics"]),
                         **{field: spec[field] for field in ("country_code", "country", "country_basis", "language") if field in spec}}
                    for key, spec in REPORT_FEEDS.items()})


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
        with ThreadPoolExecutor(max_workers=min(8, max(1, len(FETCHERS)))) as pool:
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

