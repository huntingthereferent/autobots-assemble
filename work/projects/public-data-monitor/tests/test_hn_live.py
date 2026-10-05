from app.hn import fetch_api_stories, fetch_html_stories, pair_by_canonical_key
from app.platform import ReconciliationStatus, reconcile


def test_live_html_and_api_have_shared_story_identity():
    html_rows = fetch_html_stories()
    api_rows = fetch_api_stories(limit=40)

    assert len(html_rows) > 0
    assert len(api_rows) > 0

    pairs = pair_by_canonical_key(html_rows, api_rows)
    assert len(pairs) > 0

    result = reconcile([pairs[0][0], pairs[0][1]])
    assert result.status in {
        ReconciliationStatus.AGREEMENT,
        ReconciliationStatus.CONFLICT,
    }
