from __future__ import annotations

from pathlib import Path
import argparse
import json

from work.job_adapter import evaluate_job, load_all_jobs

ROOT = Path(__file__).resolve().parents[1]
JOBS = ROOT / 'jobs'


def job_folder(job: dict, jobs_root: Path) -> str:
    job_id = str(job.get('id', ''))
    for p in jobs_root.glob(f'{job_id}_*/job.json'):
        return 'jobs/' + p.parent.name
    return 'jobs'


def render_tasks(jobs: tuple[dict, ...], jobs_root: Path = JOBS) -> str:
    lines = [
        '# TASKS — Current Work', '',
        '> Generated from canonical `jobs/*/job.json` records through the job evidence adapter.', '',
        '| Job | Protocol result | Work status | Next movement |',
        '|---|---|---|---|',
    ]
    for job in jobs:
        status = str(job.get('status', '')).lower()
        if status in {'paid', 'closed'}:
            continue
        state = evaluate_job(job)
        folder = job_folder(job, jobs_root)
        title = str(job.get('title', job.get('id', 'Untitled')))
        nxt = str(job.get('next_movement') or '').replace('|', '\\|')
        lines.append(
            f"| [{job.get('id')} — {title}]({folder}/JOB.md) | "
            f"{state.result.state} | {job.get('status','')} | {nxt} |"
        )
    lines += ['', 'A `WALL` here is intentional: the missing condition must be named rather than guessed.', '']
    return '\n'.join(lines)


def render_protocol_state(jobs: tuple[dict, ...]) -> str:
    counts = {k: 0 for k in ('MOVE','WALL','UNKNOWN','PARTIAL')}
    for job in jobs:
        counts[evaluate_job(job).result.state] += 1
    return json.dumps({'jobs': len(jobs), 'protocol_results': counts}, indent=2) + '\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--jobs', default=str(JOBS))
    parser.add_argument('--tasks', default=str(ROOT / 'TASKS.md'))
    parser.add_argument('--state', default=str(ROOT / 'views' / 'work_state.json'))
    args = parser.parse_args()

    jobs = load_all_jobs(args.jobs)
    jobs_root = Path(args.jobs)
    Path(args.tasks).write_text(render_tasks(jobs, jobs_root), encoding='utf-8')
    Path(args.state).parent.mkdir(parents=True, exist_ok=True)
    Path(args.state).write_text(render_protocol_state(jobs), encoding='utf-8')
    print(f'Generated work views from {len(jobs)} jobs.')


if __name__ == '__main__':
    main()
