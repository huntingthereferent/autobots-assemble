from fastapi.testclient import TestClient

from app.main import app
from app.orchestrator import run_source


def test_prometheus_metrics_surface_records_source_runs():
    run_source("metrics_fixture", lambda: [])

    client = TestClient(app)
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "platform_source_runs_total" in response.text
    assert 'source="metrics_fixture"' in response.text
    assert 'status="success"' in response.text
