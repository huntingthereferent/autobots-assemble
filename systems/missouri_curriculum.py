from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CurriculumTarget:
    grade: str
    unit: int
    code: str
    title: str
    skill: str
    description: str
    math_prompt: str


# Canonical subset of the previously-built Missouri Math Studio path.
# Order is curriculum movement, not a claim that completing one worksheet
# automatically establishes mastery.
MISSOURI_MATH_PATHS: dict[str, tuple[CurriculumTarget, ...]] = {
    "1": (
        CurriculumTarget(
            "1", 1, "1.NBT.A.3", "Compare two-digit numbers", "compare2",
            "Compare two two-digit numbers using >, = or < based on tens and ones.",
            "Compare two-digit numbers for 1st grade",
        ),
        CurriculumTarget(
            "1", 2, "1.RA.A.1", "Solve addition and subtraction stories", "addSubStory1",
            "Use addition and subtraction within 20 to solve varied story-problem types.",
            "Addition and subtraction word problems within 20 for 1st grade",
        ),
        CurriculumTarget(
            "1", 2, "1.RA.C.7", "Add and subtract within 20", "addSub20",
            "Use strategies and relationships to add and subtract with numbers and results within 20.",
            "Addition and subtraction within 20 for 1st grade",
        ),
        CurriculumTarget(
            "1", 2, "1.RA.C.8", "Fluency within 10", "fluency10",
            "Demonstrate accurate and efficient addition and subtraction within 10 without treating speed as the goal.",
            "Addition and subtraction within 10 for 1st grade",
        ),
        CurriculumTarget(
            "1", 3, "1.RA.A.4", "Find an unknown whole number", "missing20",
            "Determine the unknown whole number in an addition or subtraction equation relating three whole numbers.",
            "Missing-number addition and subtraction equations within 20 for 1st grade",
        ),
        CurriculumTarget(
            "1", 4, "1.GM.A.4", "Halves and fourths", "simpleFractions",
            "Partition circles and rectangles into two or four equal shares and describe the shares and whole verbally.",
            "Halves and fourths as equal shares for 1st grade",
        ),
        CurriculumTarget(
            "1", 6, "1.GM.C.8", "Time to the hour and half-hour", "timeHalf",
            "Tell and write time in hours and half-hours using analog and digital clocks.",
            "Tell time to the hour and half-hour for 1st grade",
        ),
        CurriculumTarget(
            "1", 6, "1.GM.C.9", "Know coin values", "coinValue",
            "Know the values of a penny, nickel, dime and quarter.",
            "Coin values and simple money practice for 1st grade",
        ),
    ),
    "3": (
        CurriculumTarget(
            "3", 2, "3.NBT.A.2", "Add and subtract within 1,000", "addSub1000",
            "Use place-value strategies and algorithms to add and subtract within 1,000.",
            "Addition and subtraction within 1000 for 3rd grade",
        ),
        CurriculumTarget(
            "3", 3, "3.OA.A.1", "Understand multiplication", "multiply",
            "Interpret products as equal groups.",
            "Multiplication as equal groups for 3rd grade",
        ),
        CurriculumTarget(
            "3", 3, "3.OA.A.2", "Understand division", "divide",
            "Interpret quotients as sharing or grouping.",
            "Division as sharing and grouping for 3rd grade",
        ),
        CurriculumTarget(
            "3", 3, "3.OA.D.8", "Two-step word problems", "wordTwoStep",
            "Represent and solve two-step problems.",
            "Two-step word problems using all four operations for 3rd grade",
        ),
        CurriculumTarget(
            "3", 4, "3.NF.A.1", "Fractions as equal parts", "fractionMeaning",
            "Understand a fraction as equal parts of one whole.",
            "Fractions as equal parts of a whole for 3rd grade",
        ),
    ),
}


def path_for_grade(grade: str) -> tuple[CurriculumTarget, ...]:
    try:
        return MISSOURI_MATH_PATHS[str(grade)]
    except KeyError as exc:
        raise ValueError(f"no canonical Missouri math path loaded for grade {grade}") from exc


def target_by_code(code: str) -> CurriculumTarget:
    for path in MISSOURI_MATH_PATHS.values():
        for target in path:
            if target.code == code:
                return target
    raise KeyError(code)


def next_target(current_code: str) -> CurriculumTarget | None:
    """Return the next item in the current curriculum sequencing fixture.

    This proves curriculum motion through the pipes. It is not the education
    kernel's learner-path decision rule and must not be treated as one.
    """
    current = target_by_code(current_code)
    path = path_for_grade(current.grade)
    for index, target in enumerate(path):
        if target.code == current_code:
            return path[index + 1] if index + 1 < len(path) else None
    return None


def worksheet_request(
    target: CurriculumTarget,
    *,
    level: str = "standard",
    count: int = 10,
    seed: int = 1,
    learner: str = "",
) -> dict[str, Any]:
    return {
        "template": "arithmetic",
        "title": target.title,
        "subject": "Mathematics",
        "learner": learner,
        "knowledge_goal": target.description,
        "math_prompt": target.math_prompt,
        "grade": target.grade,
        "math_topic": "auto",
        "level": level,
        "question_type": "mixed",
        "count": count,
        "seed": seed,
        "include_answer_key": True,
        "provenance": {
            "curriculum": "Missouri Math Studio",
            "standard": target.code,
            "unit": target.unit,
            "skill": target.skill,
        },
    }


def homework_task(
    *,
    worksheet: dict[str, Any],
    target: CurriculumTarget,
    learner_id: str,
    date: str,
) -> dict[str, Any]:
    return {
        "id": f"homework-{learner_id}-{target.code}-{worksheet['worksheet_id']}",
        "date": date,
        "title": f"Homework — {target.title}",
        "category": "curriculum-homework",
        "kind": "instruction",
        "scope": "individual",
        "learner_ids": [learner_id],
        "planned_minutes": 30,
        "status": "todo",
        "source": "missouri-math-studio",
        "notes": target.description,
        "meta": {
            "curriculum_standard": target.code,
            "curriculum_unit": target.unit,
            "curriculum_skill": target.skill,
            "worksheet_id": worksheet["worksheet_id"],
            "knowledge_goal": target.description,
            "required_evidence": "worksheet result + learner work",
        },
    }


def reconcile_homework(
    *,
    target: CurriculumTarget,
    correct: int,
    total: int,
    completed: bool = True,
) -> dict[str, Any]:
    """Pipe-test reconciliation policy, not a mastery model.

    Percentage thresholds make movement observable in the current embryo.
    The education kernel should later reconcile relation-level observations
    rather than promote this score policy into learner intelligence.
    """
    if total <= 0 or correct < 0 or correct > total:
        raise ValueError("invalid homework score")
    accuracy = correct / total
    if not completed:
        movement = "resume"
        next_code = target.code
        level = "support"
    elif accuracy < 0.70:
        movement = "revisit"
        next_code = target.code
        level = "support"
    elif accuracy < 0.85:
        movement = "continue"
        next_code = target.code
        level = "standard"
    else:
        nxt = next_target(target.code)
        movement = "advance" if nxt else "hold"
        next_code = nxt.code if nxt else target.code
        level = "standard"

    return {
        "standard": target.code,
        "correct": correct,
        "total": total,
        "accuracy": accuracy,
        "movement": movement,
        "next_standard": next_code,
        "next_level": level,
        "boundary": "worksheet completion/score is evidence for next movement, not automatic mastery",
    }


def next_worksheet_request(
    result: dict[str, Any],
    *,
    learner: str = "",
    count: int = 10,
    seed: int = 2,
) -> dict[str, Any]:
    target = target_by_code(result["next_standard"])
    return worksheet_request(
        target,
        level=result["next_level"],
        count=count,
        seed=seed,
        learner=learner,
    )
