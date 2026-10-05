from datetime import datetime, timezone

from app.hn import pair_by_canonical_key, parse_front_page
from app.platform import ReconciliationStatus, reconcile


FIXTURE = """<html><body><table class="itemlist">
<tr class="athing submission" id="123">
  <td class="title"><span class="titleline"><a href="https://example.com/a">Example A</a></span></td>
</tr>
<tr>
  <td class="subtext"><span class="score" id="score_123">42 points</span> by <a class="hnuser">alice</a>
  <a href="item?id=123">17 comments</a></td>
</tr>
<tr class="athing submission" id="456">
  <td class="title"><span class="titleline"><a href="item?id=456">Ask HN: Example B</a></span></td>
</tr>
<tr>
  <td class="subtext"><span class="score" id="score_456">1 point</span> by <a class="hnuser">bob</a>
  <a href="item?id=456">discuss</a></td>
</tr>
</table></body></html>"""
NOW = datetime(2026, 10, 5, 9, 0, tzinfo=timezone.utc)


def test_html_parser_emits_canonical_observations():
    rows = parse_front_page(FIXTURE, observed_at=NOW)

    assert len(rows) == 2
    first = rows[0]
    assert first.source == "hn_html"
    assert first.source_id == "123"
    assert first.canonical_key == "hn_story:123"
    assert first.payload == {
        "title": "Example A",
        "url": "https://example.com/a",
        "score": 42,
        "comments": 17,
        "by": "alice",
    }


def test_relative_item_link_is_normalized():
    rows = parse_front_page(FIXTURE, observed_at=NOW)
    assert rows[1].payload["url"] == "https://news.ycombinator.com/item?id=456"
    assert rows[1].payload["comments"] is None


def test_pairing_uses_canonical_identity_not_title():
    html_rows = parse_front_page(FIXTURE, observed_at=NOW)
    api_like = html_rows[0].model_copy(update={
        "source": "hn_api",
        "payload": {**html_rows[0].payload, "score": 43},
    })

    pairs = pair_by_canonical_key(html_rows, [api_like])
    assert len(pairs) == 1
    assert pairs[0][0].canonical_key == "hn_story:123"

    result = reconcile([pairs[0][0], pairs[0][1]])
    assert result.status == ReconciliationStatus.CONFLICT
    assert result.conflicting_fields == ["score"]
