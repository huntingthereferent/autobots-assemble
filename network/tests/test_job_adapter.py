from pathlib import Path

from work.job_adapter import evaluate_job, load_all_jobs


def test_all_job_records_are_admissible_without_rewriting_them():
    jobs_root = Path(__file__).resolve().parents[2] / "jobs"
    jobs = load_all_jobs(jobs_root)
    assert len(jobs) >= 21
    states = [evaluate_job(job) for job in jobs]
    assert {state.result.state for state in states} <= {"MOVE", "WALL", "UNKNOWN", "PARTIAL"}
    assert any(state.result.state == "WALL" for state in states)
    assert any(state.result.state in {"MOVE", "PARTIAL"} for state in states)


def test_blocked_job_does_not_emit_completion_relations():
    job = {
        "id": "JOB-X",
        "title": "blocked",
        "preferred_referent": "spec",
        "boundary": "do thing",
        "acceptance": "thing passes",
        "status": "blocked",
        "blockers": ["client file missing"],
        "result": "prototype exists",
    }
    state = evaluate_job(job)
    assert state.result.state == "WALL"
    assert state.result.outputs == ()
