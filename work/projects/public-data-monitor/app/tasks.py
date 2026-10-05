from .celery_app import celery_app
from .github_source import fetch_repository
from .hn import fetch_api_stories, fetch_html_stories
from .orchestrator import run_source_persisted


@celery_app.task(bind=True, name="app.tasks.collect_hn")
def collect_hn(self) -> dict[str, int]:
    task_id = self.request.id
    html = run_source_persisted("hn_html", fetch_html_stories, task_id=task_id)
    api = run_source_persisted("hn_api", fetch_api_stories, task_id=task_id)
    return {
        "hn_html": len(html),
        "hn_api": len(api),
    }


@celery_app.task(bind=True, name="app.tasks.collect_github")
def collect_github(self) -> dict[str, int]:
    rows = run_source_persisted("github_api", fetch_repository, task_id=self.request.id)
    return {"github_api": len(rows)}
