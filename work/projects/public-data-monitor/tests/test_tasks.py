from app.celery_app import celery_app
from app.tasks import collect_hn


def test_celery_task_is_registered():
    assert "app.tasks.collect_hn" in celery_app.tasks


def test_celery_schedule_points_to_registered_task():
    schedule = celery_app.conf.beat_schedule["collect-hn-every-5-minutes"]
    assert schedule["task"] == "app.tasks.collect_hn"
    assert schedule["schedule"] == 300.0


def test_github_task_is_registered_and_scheduled():
    assert "app.tasks.collect_github" in celery_app.tasks
    schedule = celery_app.conf.beat_schedule["collect-github-every-10-minutes"]
    assert schedule["task"] == "app.tasks.collect_github"
    assert schedule["schedule"] == 600.0
