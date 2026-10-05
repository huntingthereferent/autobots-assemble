from .celery_app import celery_app
from .github_source import fetch_repository
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


@celery_app.task(name="app.tasks.collect_github")
def collect_github() -> dict[str, int]:
    rows = run_source("github_api", fetch_repository)
    return {"github_api": len(rows)}
