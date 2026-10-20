"""A/B bounded observed-source revision with intact historical ancestry.

Only an explicitly declared correction relationship can supersede a source
statement. Source known-time is not clinical validity time. A source revision
does not physically delete the statement, invent a clinical event, or prove
the correction is true. Equal-dated contradictions are AMBIGUOUS, never a
fabricated clean resolution.
"""
from __future__ import annotations

from .ab_time_respecting_source_chain import admit, token, day

SCHEMA = "ab-observed-source-supersession/v1"


def observe(rows, *, subject, claim_object, support_predicate,
            revision_predicate, known_at, target_at):
    subject = token(subject)
    claim_object = token(claim_object)
    support_predicate = token(support_predicate)
    revision_predicate = token(revision_predicate)
    if support_predicate == revision_predicate:
        raise ValueError("source support and revision relations must differ")
    # Reuse exact validated source observation/clock contract, with a
    # declared two-stage schema only for input validation, not a path claim.
    observations, _, known, target = admit(rows, [
        {"predicate":support_predicate,"object":claim_object},
        {"predicate":revision_predicate,"object":claim_object},
    ],known_at=known_at,target_at=target_at,subject=subject)
    relevant = [
        x for x in observations
        if x["subject"] == subject and x["object"] == claim_object
        and x["predicate"] in (support_predicate, revision_predicate)
        and x["valid_from"] <= target < x["valid_to"]
        and x["known_at"] <= known
    ]
    supports = sorted((x for x in relevant if x["predicate"] == support_predicate),
                      key=lambda x: (x["known_at"],x["id"]))
    revisions = sorted((x for x in relevant if x["predicate"] == revision_predicate),
                       key=lambda x: (x["known_at"],x["id"]))
    superseded = []
    ambiguities = []
    currently_supported = []
    for s in supports:
        later = [r for r in revisions if r["known_at"] > s["known_at"]]
        ties = [r for r in revisions if r["known_at"] == s["known_at"]]
        if later:
            superseded.append({
                "statement_id":s["id"],
                "later_revision_ids":[r["id"] for r in later],
                "source_ids":[s["id"]]+[r["id"] for r in later],
            })
        elif ties:
            ambiguities.append({
                "statement_id":s["id"],
                "unresolved_same_day_revision_ids":[r["id"] for r in ties],
            })
        else:
            currently_supported.append(s["id"])
    if ambiguities:
        outcome = "AMBIGUOUS"
        value = None
    elif not supports:
        outcome = "NOT_AVAILABLE"
        value = None
    elif currently_supported:
        outcome = "SUPPORTED"
        value = True
    else:
        outcome = "SUPERSEDED"
        value = False
    return {
        "schema":SCHEMA,
        "subject":subject,
        "claim_object":claim_object,
        "declared_support_predicate":support_predicate,
        "declared_revision_predicate":revision_predicate,
        "known_at":known,
        "target_at":target,
        "outcome":outcome,
        "currently_supported":value,
        "source_statement_ids_still_in_history":[x["id"] for x in supports],
        "source_revision_ids_still_in_history":[x["id"] for x in revisions],
        "effective_supersession_witnesses":superseded,
        "unresolved_ties":ambiguities,
        "not_silently_deleted":True,
        "source_observation_only":True,
        "clinical_truth_claimed":False,
        "original_W13_engine_modified":False,
    }
