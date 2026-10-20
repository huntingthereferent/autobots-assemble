"""A/B finite, time-respecting *source relationship* witness.

An ordered relationship is admitted only when distinct source observations
match an explicitly declared sequence, keep the same subject, and have
strictly increasing event-start dates no later than the requested target day.
Every hop must have been source-known by the independent knowledge cutoff.

This witnesses an observed sequence, NOT causality, treatment efficacy,
OWL entailment, real clinical valid-at provenance or a clinical decision.
Use an exhaustive bounded search: no path is FALSE only inside that scope;
over-capacity must fail closed rather than masquerade as a negative.
"""
from __future__ import annotations
from datetime import date
import re

SCHEMA="ab-finite-time-respecting-source-chain/v1"
FIELDS=frozenset({
    "id","subject","predicate","object","valid_from","valid_to","known_at","source_ref"
})
DATE=re.compile(r"\d{4}-\d{2}-\d{2}\Z")
TOKEN=re.compile(r"[a-z][a-z0-9_-]{0,69}\Z")
MAX_ROWS=64
MAX_STAGES=5
MAX_PATHS=128


def day(raw):
    if type(raw) is not str or DATE.fullmatch(raw) is None:
        raise ValueError("source clock requires YYYY-MM-DD")
    try:
        if date.fromisoformat(raw).isoformat()!=raw:
            raise ValueError("noncanonical source day")
    except ValueError as error:
        raise ValueError("not a valid calendar day") from error
    return raw


def token(raw):
    if type(raw) is not str or TOKEN.fullmatch(raw) is None:
        raise ValueError("noncanonical bounded source token")
    return raw


def admit(observations, stages, *, known_at, target_at, subject=None):
    """Exact source/stage schema, no implicit domain semantics or fabricated time."""
    known,target=day(known_at),day(target_at)
    if (type(observations) is not list or not 1<=len(observations)<=MAX_ROWS
            or type(stages) is not list or not 2<=len(stages)<=MAX_STAGES):
        raise ValueError("finite source rows and 2..5 relationship stages required")
    if subject is not None:
        token(subject)
    normalized=[]
    seen=set()
    for row in observations:
        if type(row) is not dict or set(row)!=FIELDS:
            raise ValueError("exact evidence source schema required")
        r={k:token(row[k]) for k in (
            "id","subject","predicate","object","source_ref")}
        r.update({k:day(row[k]) for k in ("valid_from","valid_to","known_at")})
        if r["valid_from"]>=r["valid_to"] or r["id"] in seen:
            raise ValueError("reversed interval or duplicate evidence ID")
        seen.add(r["id"])
        normalized.append(r)
    pattern=[]
    for stage in stages:
        if (type(stage) is not dict or set(stage)!={"predicate","object"}):
            raise ValueError("each requested stage must be an exact predicate/object")
        pattern.append({k:token(stage[k]) for k in ("predicate","object")})
    return normalized,pattern,known,target


def observe(observations, stages, *, known_at, target_at, subject=None):
    rows,pattern,known,target=admit(
        observations,stages,known_at=known_at,target_at=target_at,subject=subject
    )
    candidates=[]
    for stage in pattern:
        matches=[
            r for r in rows if r["predicate"]==stage["predicate"]
            and r["object"]==stage["object"]
            and r["known_at"]<=known and r["valid_from"]<=target
            and (subject is None or r["subject"]==subject)
        ]
        candidates.append(sorted(matches,key=lambda r:(r["valid_from"],r["id"])))

    paths=[]
    def walk(i, chosen):
        if i==len(pattern):
            if len(paths)>=MAX_PATHS:
                raise ValueError("path witness limit exceeded: not a negative result")
            paths.append(tuple(chosen))
            return
        for r in candidates[i]:
            if chosen:
                prior=chosen[-1]
                if (r["subject"]!=prior["subject"]
                        or r["valid_from"]<=prior["valid_from"]
                        or r["id"] in {x["id"] for x in chosen}):
                    continue
            chosen.append(r)
            walk(i+1,chosen)
            chosen.pop()
    walk(0,[])
    paths.sort(key=lambda trail:tuple(r["id"] for r in trail))
    return {
        "schema":SCHEMA,
        "known_at":known,
        "target_at":target,
        "subject_constraint":subject,
        "stages":pattern,
        "path_exists":bool(paths),
        "exhaustive_within_declared_scope":True,
        "witnesses":[{
            "subject":trail[0]["subject"],
            "evidence_ids":[r["id"] for r in trail],
            "event_starts":[r["valid_from"] for r in trail],
            "source_known_dates":[r["known_at"] for r in trail],
            "source_references":[r["source_ref"] for r in trail],
        } for trail in paths],
        "observed_relation":"declared-time-ordered-source-pattern-only",
        "causal_conclusion":False,
        "clinical_validity_independently_authenticated":False,
        "original_W13_engine_modified":False,
    }
