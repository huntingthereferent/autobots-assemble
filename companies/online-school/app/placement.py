from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Any

from math_space import FAMILIES, DOMAINS, BUILDERS


@dataclass(frozen=True)
class PlacementBand:
    band_id: str
    label: str
    domains: tuple[str, ...]


ADULT_MATH_BANDS = (
    PlacementBand(
        "foundations",
        "Foundations",
        ("number","number-theory","algebra","geometry"),
    ),
    PlacementBand(
        "secondary",
        "Secondary",
        ("functions","sequences","exponents-logarithms","analytic-geometry","trigonometry"),
    ),
    PlacementBand(
        "advanced",
        "Advanced",
        ("vectors","complex-numbers","linear-algebra","combinatorics","probability","statistics"),
    ),
    PlacementBand(
        "higher",
        "Higher mathematics",
        ("calculus","differential-equations","financial-math","sets-logic"),
    ),
)


def math_placement(age: int | None, grade: str, seed: int = 1) -> dict[str, Any]:
    rng = Random(seed)
    adult = age is not None and age >= 18

    if adult:
        bands = ADULT_MATH_BANDS
    else:
        try:
            g = int(grade)
        except (TypeError, ValueError):
            g = max(1, min(12, (age or 7) - 5))
        if g <= 2:
            domains = ("number","algebra","geometry")
        elif g <= 5:
            domains = ("number","number-theory","algebra","geometry","functions")
        elif g <= 8:
            domains = ("number","algebra","functions","geometry","statistics","probability")
        else:
            domains = ("algebra","functions","exponents-logarithms","geometry","trigonometry","statistics")
        bands = (PlacementBand("bounded", f"Grade-context {g}", domains),)

    items = []
    order = 0
    for band in bands:
        for domain in band.domains:
            family = "solve"
            if domain in {"geometry","analytic-geometry","vectors","linear-algebra"}:
                family = "measure"
            elif domain in {"probability","statistics","sets-logic"}:
                family = "infer"
            elif domain in {"functions","exponents-logarithms"}:
                family = "represent"
            row = BUILDERS[domain](rng, family)
            order += 1
            items.append(
                {
                    "id": f"math-{order:02d}",
                    "band": band.band_id,
                    "band_label": band.label,
                    "domain": domain,
                    "family": family,
                    "prompt": row["prompt"],
                    "answer": row["answer"].split("\n", 1)[0],
                }
            )

    return {
        "subject": "mathematics",
        "kind": "placement",
        "adult": adult,
        "age_bounded": not adult,
        "grade_bounded": not adult,
        "bands": [
            {"id": band.band_id, "label": band.label, "domains": band.domains}
            for band in bands
        ],
        "items": items,
    }


def placement_plan(learner: dict[str, Any]) -> list[dict[str, Any]]:
    learner_id = str(learner.get("id") or "")
    name = str(learner.get("display_name") or learner_id)
    age_raw = learner.get("age")
    try:
        age = int(age_raw) if age_raw not in (None, "") else None
    except (TypeError, ValueError):
        age = None
    grade = str(learner.get("grade_context") or "")
    adult = age is not None and age >= 18

    return [
        {
            "subject": "mathematics",
            "title": "Placement test — Mathematics",
            "minutes": 45 if adult else 25,
            "description": (
                "Start broad. Stop guessing where the learner belongs; use the returned answers to locate the current mathematical line."
            ),
            "diagnostic": math_placement(age, grade, seed=17),
        },
        {
            "subject": "reading",
            "title": "Placement test — Reading",
            "minutes": 30 if adult else 20,
            "description": (
                "Read a passage, identify its main claim, distinguish evidence from inference, and explain one unfamiliar relation in your own words."
            ),
            "prompts": (
                "State the main idea or claim.",
                "Give two details that directly support it.",
                "Give one reasonable inference and identify the evidence that supports it.",
                "Explain one important word, phrase, or relation from context.",
            ),
        },
        {
            "subject": "writing",
            "title": "Placement test — Writing",
            "minutes": 30 if adult else 20,
            "description": (
                "Write from a supplied claim so the school can observe organization, language, evidence, and revision without assuming a level first."
            ),
            "prompts": (
                "Explain a position or idea clearly.",
                "Support it with at least two reasons or examples.",
                "Revise one sentence to make the relation more precise.",
            ),
        },
        {
            "subject": "science-research",
            "title": "Placement test — Science & Research",
            "minutes": 35 if adult else 20,
            "description": (
                "Move from question to claim to evidence: identify what would count as evidence, what would change the claim, and what should be investigated next."
            ),
            "prompts": (
                "Choose or accept a question.",
                "State a testable claim.",
                "Name evidence that would support or contradict it.",
                "Say what you would investigate next and why.",
            ),
        },
    ]
