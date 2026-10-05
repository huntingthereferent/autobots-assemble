from .celery_app import celery_app
from .hn import fetch_api_stories, fetch_html_stories
from .orchestrator import run_source


@celery_app.task(name="app.tasks.collect_hn")
def collect_hn() -> dict[str, int]:
    html = run_source("hn_html", fetch_html_stories)
    api = run_source("hn_api", fetch_api_stories)
    return {
        "hn_html": len(html),
        "hn_api": len(api),
    }
