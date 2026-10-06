from __future__ import annotations

from typing import Any

from systems.missouri_curriculum import path_for_grade


def build_comparison(*, state: dict[str, Any], learner: dict[str, Any]) -> dict[str, Any]:
    learner_id = str(learner.get("id") or "")
    grade = str(learner.get("grade_context") or "").strip()
    try:
        targets = list(path_for_grade(grade)) if grade else []
    except ValueError:
        targets = []

    progress = learner.get("progress_records") or {}
    tasks = [t for t in state.get("tasks", []) if learner_id in t.get("learner_ids", [])]
    works = [
        w for w in state.get("worksheets", [])
        if str(w.get("learner") or "") in {learner_id, str(learner.get("display_name") or "")}
    ]

    standards = []
    for target in targets:
        record = progress.get(target.code) or {}
        standards.append({
            "code": target.code,
            "unit": target.unit,
            "title": target.title,
            "description": target.description,
            "skill": target.skill,
            "status": str(record.get("status") or "not-observed"),
            "note": str(record.get("note") or ""),
            "updated_at": record.get("updated_at"),
            "task_evidence": [
                {
                    "id": t.get("id"),
                    "date": t.get("date"),
                    "title": t.get("title"),
                    "status": t.get("status"),
                }
                for t in tasks
                if str((t.get("meta") or {}).get("curriculum_standard") or "") == target.code
            ],
            "worksheet_evidence": [
                {"worksheet_id": w.get("worksheet_id"), "title": w.get("title")}
                for w in works
                if isinstance((w.get("source") or {}).get("provenance"), dict)
                and str((w.get("source") or {}).get("provenance", {}).get("standard") or "") == target.code
            ],
        })

    return {
        "learner_id": learner_id,
        "grade_context": grade,
        "source": "Missouri Learning Standards comparison fixture" if standards else "No Missouri comparison map loaded for this grade yet",
        "standards": standards,
        "boundary": "Comparison is read-only with respect to learning; it does not choose lessons or advance curriculum.",
    }
