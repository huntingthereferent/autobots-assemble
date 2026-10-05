from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup

from .platform import SourceObservation

HN_HTML = "https://news.ycombinator.com/"
HN_TOP = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM = "https://hacker-news.firebaseio.com/v0/item/{item_id}.json"


def _story_payload(*, title: str, url: str | None, score: int | None, comments: int | None, by: str | None) -> dict:
    return {
        "title": title,
        "url": url,
        "score": score,
        "comments": comments,
        "by": by,
    }


def parse_front_page(html: str, observed_at: datetime | None = None) -> list[SourceObservation]:
    observed_at = observed_at or datetime.now(timezone.utc)
    soup = BeautifulSoup(html, "html.parser")
    observations: list[SourceObservation] = []

    for row in soup.select("tr.athing[id]"):
        item_id = row.get("id")
        title_link = row.select_one("span.titleline > a")
        if not item_id or title_link is None:
            continue

        subtext_row = row.find_next_sibling("tr")
        subtext = subtext_row.select_one("td.subtext") if subtext_row else None

        score = None
        author = None
        comments = None
        if subtext is not None:
            score_el = subtext.select_one(f"#score_{item_id}")
            if score_el:
                raw_score = score_el.get_text(" ", strip=True).split()[0]
                if raw_score.isdigit():
                    score = int(raw_score)

            user_el = subtext.select_one("a.hnuser")
            if user_el:
                author = user_el.get_text(strip=True)

            comment_links = [a for a in subtext.select("a[href]") if f"item?id={item_id}" in a.get("href", "")]
            for link in reversed(comment_links):
                text = link.get_text(" ", strip=True)
                if "comment" in text:
                    first = text.split()[0]
                    comments = int(first) if first.isdigit() else 0
                    break

        href = title_link.get("href")
        if href and href.startswith("item?id="):
            href = f"https://news.ycombinator.com/{href}"

        observations.append(
            SourceObservation(
                source="hn_html",
                source_id=item_id,
                observed_at=observed_at,
                source_url=f"https://news.ycombinator.com/item?id={item_id}",
                entity_type="story",
                canonical_key=f"hn_story:{item_id}",
                payload=_story_payload(
                    title=title_link.get_text(" ", strip=True),
                    url=href,
                    score=score,
                    comments=comments,
                    by=author,
                ),
            )
        )

    return observations


def fetch_html_stories(client: httpx.Client | None = None) -> list[SourceObservation]:
    owns_client = client is None
    client = client or httpx.Client(timeout=15, follow_redirects=True)
    try:
        response = client.get(HN_HTML, headers={"User-Agent": "state-reconciliation-platform/0.1"})
        response.raise_for_status()
        return parse_front_page(response.text)
    finally:
        if owns_client:
            client.close()


def fetch_api_stories(limit: int = 30, client: httpx.Client | None = None) -> list[SourceObservation]:
    owns_client = client is None
    client = client or httpx.Client(timeout=15, follow_redirects=True)
    observed_at = datetime.now(timezone.utc)

    try:
        top = client.get(HN_TOP, headers={"User-Agent": "state-reconciliation-platform/0.1"})
        top.raise_for_status()
        ids = top.json()[:limit]

        observations: list[SourceObservation] = []
        for item_id in ids:
            response = client.get(
                HN_ITEM.format(item_id=item_id),
                headers={"User-Agent": "state-reconciliation-platform/0.1"},
            )
            response.raise_for_status()
            item = response.json()
            if not item or item.get("type") not in {"story", "job"}:
                continue

            observations.append(
                SourceObservation(
                    source="hn_api",
                    source_id=str(item["id"]),
                    observed_at=observed_at,
                    source_updated_at=None,
                    source_url=f"https://news.ycombinator.com/item?id={item['id']}",
                    entity_type="story",
                    canonical_key=f"hn_story:{item['id']}",
                    payload=_story_payload(
                        title=item.get("title") or "",
                        url=item.get("url"),
                        score=item.get("score"),
                        comments=item.get("descendants", 0),
                        by=item.get("by"),
                    ),
                )
            )

        return observations
    finally:
        if owns_client:
            client.close()


def pair_by_canonical_key(
    left: list[SourceObservation],
    right: list[SourceObservation],
) -> list[tuple[SourceObservation, SourceObservation]]:
    right_by_key = {obs.canonical_key: obs for obs in right}
    return [(obs, right_by_key[obs.canonical_key]) for obs in left if obs.canonical_key in right_by_key]
