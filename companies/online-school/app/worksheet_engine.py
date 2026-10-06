from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Any
import re
import uuid


TEMPLATES = (
    "arithmetic",
    "spelling",
    "vocabulary",
    "reading",
    "handwriting",
    "custom",
)

LEVELS = ("support", "standard", "challenge")


@dataclass(frozen=True)
class WorksheetItem:
    prompt: str
    answer: str = ""
    kind: str = "short"
    lines: int = 1

    def as_dict(self) -> dict[str, Any]:
        return {
            "prompt": self.prompt,
            "answer": self.answer,
            "kind": self.kind,
            "lines": self.lines,
        }


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _lines(value: Any) -> list[str]:
    if isinstance(value, list):
        raw = [str(x) for x in value]
    else:
        raw = re.split(r"[\n,]+", str(value or ""))
    return [x.strip() for x in raw if x.strip()]


def _pairs(value: Any) -> list[tuple[str, str]]:
    rows = _lines(value)
    out: list[tuple[str, str]] = []
    for row in rows:
        if "::" in row:
            left, right = row.split("::", 1)
        elif ":" in row:
            left, right = row.split(":", 1)
        else:
            left, right = row, ""
        if left.strip():
            out.append((left.strip(), right.strip()))
    return out


def _seed(value: Any) -> int:
    text = _clean(value)
    if text:
        try:
            return int(text)
        except ValueError:
            return sum((i + 1) * ord(ch) for i, ch in enumerate(text))
    return 1


def _count(payload: dict[str, Any], default: int) -> int:
    try:
        return max(1, min(60, int(payload.get("count") or default)))
    except (TypeError, ValueError):
        return default


def _arithmetic(payload: dict[str, Any], rng: Random) -> list[WorksheetItem]:
    level = _clean(payload.get("level")) or "standard"
    op = _clean(payload.get("operation")) or "mixed"
    count = _count(payload, 20)
    ceilings = {
        "support": (10, 5),
        "standard": (50, 12),
        "challenge": (500, 20),
    }
    add_max, mult_max = ceilings.get(level, ceilings["standard"])
    operations = ["add", "subtract", "multiply", "divide"] if op == "mixed" else [op]
    items: list[WorksheetItem] = []
    for _ in range(count):
        current = rng.choice(operations)
        if current == "add":
            a, b = rng.randint(0, add_max), rng.randint(0, add_max)
            prompt, answer = f"{a} + {b} =", str(a + b)
        elif current == "subtract":
            a, b = rng.randint(0, add_max), rng.randint(0, add_max)
            a, b = max(a, b), min(a, b)
            prompt, answer = f"{a} − {b} =", str(a - b)
        elif current == "multiply":
            a, b = rng.randint(0, mult_max), rng.randint(0, mult_max)
            prompt, answer = f"{a} × {b} =", str(a * b)
        elif current == "divide":
            divisor = rng.randint(1, max(2, mult_max))
            quotient = rng.randint(1, max(2, mult_max))
            prompt, answer = f"{divisor * quotient} ÷ {divisor} =", str(quotient)
        else:
            raise ValueError(f"unsupported operation: {current}")
        items.append(WorksheetItem(prompt=prompt, answer=answer, kind="math"))
    return items


def _spelling(payload: dict[str, Any], rng: Random) -> list[WorksheetItem]:
    words = _lines(payload.get("words"))
    if not words:
        raise ValueError("spelling template requires words")
    level = _clean(payload.get("level")) or "standard"
    items: list[WorksheetItem] = []
    for word in words:
        if level == "support":
            items.append(WorksheetItem(
                prompt=f"Copy the word three times: {word}",
                answer=f"{word} / {word} / {word}",
                kind="handwriting",
                lines=3,
            ))
        elif level == "challenge":
            items.append(WorksheetItem(
                prompt=f"Use “{word}” in a sentence that shows its meaning.",
                answer="Accept a sentence that uses the word correctly in context.",
                kind="response",
                lines=2,
            ))
        else:
            chars = list(word)
            indexes = [i for i, ch in enumerate(chars) if ch.lower() in "aeiou"]
            if indexes:
                for i in rng.sample(indexes, k=max(1, min(2, len(indexes)))):
                    chars[i] = "_"
            items.append(WorksheetItem(
                prompt=f"Complete the spelling: {''.join(chars)}",
                answer=word,
                kind="short",
            ))
    return items


def _vocabulary(payload: dict[str, Any], rng: Random) -> list[WorksheetItem]:
    pairs = _pairs(payload.get("terms"))
    if not pairs:
        raise ValueError("vocabulary template requires term: definition pairs")
    level = _clean(payload.get("level")) or "standard"
    shuffled = list(pairs)
    rng.shuffle(shuffled)
    items: list[WorksheetItem] = []
    for term, definition in shuffled:
        if level == "support":
            items.append(WorksheetItem(
                prompt=f"{term}: {definition}\nWrite the word once, then explain it in your own words.",
                answer=f"Target word: {term}. Accept an accurate paraphrase of: {definition}",
                kind="response",
                lines=2,
            ))
        elif level == "challenge":
            items.append(WorksheetItem(
                prompt=f"Define “{term}” and use it to explain a relationship or example.",
                answer=f"Definition: {definition}. Example/relationship should be accurate.",
                kind="response",
                lines=3,
            ))
        else:
            items.append(WorksheetItem(
                prompt=f"Define: {term}",
                answer=definition or "Teacher-supplied definition.",
                kind="response",
                lines=2,
            ))
    return items


def _reading(payload: dict[str, Any], rng: Random) -> list[WorksheetItem]:
    passage = _clean(payload.get("passage"))
    if not passage:
        raise ValueError("reading template requires a source passage")
    level = _clean(payload.get("level")) or "standard"
    words = re.findall(r"[A-Za-z][A-Za-z'-]{4,}", passage)
    vocab = rng.choice(words) if words else "important word"
    if level == "support":
        prompts = [
            ("What is this passage mostly about?", "Accept the central topic stated in the passage.", 2),
            ("Write two facts you learned.", "Two facts must be supported directly by the passage.", 3),
            (f"What does “{vocab}” mean in this passage?", "Accept a context-supported meaning.", 2),
        ]
    elif level == "challenge":
        prompts = [
            ("State the central claim or main idea and cite two details that support it.", "Main idea plus two passage-supported details.", 4),
            ("What can you infer that the passage does not state directly? Explain your evidence.", "Inference must be supported by passage evidence.", 4),
            (f"Explain the meaning and effect of “{vocab}” as it is used here.", "Meaning and effect should be justified from context.", 3),
            ("Write one question that would extend this text into further investigation.", "Accept a relevant, researchable extension question.", 2),
        ]
    else:
        prompts = [
            ("What is the main idea of the passage?", "Accept the central idea supported by the passage.", 2),
            ("List three important details.", "Three details must be supported by the passage.", 3),
            (f"What does “{vocab}” mean in context?", "Accept a context-supported meaning.", 2),
            ("What is one reasonable inference you can make? What evidence supports it?", "Inference plus supporting passage evidence.", 3),
            ("Summarize the passage in 2–3 sentences.", "Summary should preserve the main idea and essential details.", 3),
        ]
    return [WorksheetItem(prompt=p, answer=a, kind="response", lines=l) for p, a, l in prompts]


def _handwriting(payload: dict[str, Any], rng: Random) -> list[WorksheetItem]:
    phrases = _lines(payload.get("copy_text") or payload.get("words"))
    if not phrases:
        raise ValueError("handwriting template requires copy text")
    count = _count(payload, len(phrases))
    out: list[WorksheetItem] = []
    while len(out) < count:
        phrase = phrases[len(out) % len(phrases)]
        out.append(WorksheetItem(
            prompt=phrase,
            answer=phrase,
            kind="handwriting",
            lines=3,
        ))
    return out


def _custom(payload: dict[str, Any], rng: Random) -> list[WorksheetItem]:
    rows = _pairs(payload.get("custom_items"))
    if not rows:
        raise ValueError("custom template requires question :: answer rows")
    return [
        WorksheetItem(
            prompt=question,
            answer=answer or "Teacher review.",
            kind="response",
            lines=max(1, min(8, int(payload.get("response_lines") or 2))),
        )
        for question, answer in rows
    ]


def generate_worksheet(payload: dict[str, Any]) -> dict[str, Any]:
    template = (_clean(payload.get("template")) or "custom").lower()
    if template not in TEMPLATES:
        raise ValueError(f"unsupported worksheet template: {template}")

    level = (_clean(payload.get("level")) or "standard").lower()
    if level not in LEVELS:
        raise ValueError(f"unsupported worksheet level: {level}")

    seed = _seed(payload.get("seed"))
    rng = Random(seed)
    builders = {
        "arithmetic": _arithmetic,
        "spelling": _spelling,
        "vocabulary": _vocabulary,
        "reading": _reading,
        "handwriting": _handwriting,
        "custom": _custom,
    }
    items = builders[template]({**payload, "level": level}, rng)

    title = _clean(payload.get("title")) or {
        "arithmetic": "Math Practice",
        "spelling": "Spelling Practice",
        "vocabulary": "Vocabulary",
        "reading": "Reading & Thinking",
        "handwriting": "Handwriting Practice",
        "custom": "Practice Worksheet",
    }[template]

    worksheet_id = _clean(payload.get("worksheet_id")) or f"ws_{uuid.uuid4().hex[:12]}"
    return {
        "schema_version": 1,
        "worksheet_id": worksheet_id,
        "title": title,
        "subtitle": _clean(payload.get("subtitle")),
        "learner": _clean(payload.get("learner")),
        "subject": _clean(payload.get("subject")),
        "knowledge_goal": _clean(payload.get("knowledge_goal")),
        "instructions": _clean(payload.get("instructions")),
        "template": template,
        "level": level,
        "seed": seed,
        "variant": _clean(payload.get("variant")) or "A",
        "page_size": (_clean(payload.get("page_size")) or "letter").lower(),
        "columns": max(1, min(3, int(payload.get("columns") or (2 if template == "arithmetic" else 1)))),
        "include_answer_key": bool(payload.get("include_answer_key", True)),
        "passage": _clean(payload.get("passage")) if template == "reading" else "",
        "items": [item.as_dict() for item in items],
        "source": {
            key: payload.get(key)
            for key in ("words", "terms", "copy_text", "custom_items", "operation", "count")
            if payload.get(key) not in (None, "")
        },
    }


def validate_saved_worksheet(payload: dict[str, Any]) -> dict[str, Any]:
    worksheet = dict(payload)
    worksheet_id = _clean(worksheet.get("worksheet_id"))
    if not worksheet_id:
        worksheet_id = f"ws_{uuid.uuid4().hex[:12]}"
    worksheet["worksheet_id"] = worksheet_id
    worksheet["title"] = _clean(worksheet.get("title")) or "Untitled Worksheet"
    worksheet["items"] = [
        {
            "prompt": _clean(item.get("prompt")),
            "answer": _clean(item.get("answer")),
            "kind": _clean(item.get("kind")) or "response",
            "lines": max(1, min(12, int(item.get("lines") or 1))),
        }
        for item in worksheet.get("items") or []
        if isinstance(item, dict) and _clean(item.get("prompt"))
    ]
    if not worksheet["items"]:
        raise ValueError("worksheet requires at least one item")
    return worksheet
