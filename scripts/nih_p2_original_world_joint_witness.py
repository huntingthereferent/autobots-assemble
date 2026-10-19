"""Joint falsification boundary for two independently played original W13 world panels.

Pure host verification only: one panel varies explicitly synthetic source
versions; the other varies an explicitly hypothetical publication-date interval.
Both are tied to the SAME previously restored twelve-job W13 native journal.
No worker admission, journal mutation, or historical study claim.
"""
from __future__ import annotations
from hashlib import sha256
import json

SCHEMA="nih-p2-original-world-joint-source-publication-witness/v1"
PROFILES=("original","later-knowledge","additional-conflict")
CUTOFFS=("2026-01-03","2026-01-04","2026-01-06","2026-01-07")
SHA="0"*64

def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()

def indexed(records,keys,expected):
    if type(records) is not list or len(records)!=len(expected):
        raise ValueError("missing or excess live game-world source observations")
    result={}
    for row in records:
        if type(row) is not dict: raise ValueError("source frame is not a record")
        key=tuple(row.get(k) for k in keys)
        if key in result: raise ValueError("duplicate original-world source observation")
        result[key]=row
    if set(result)!=set(expected): raise ValueError("missing original-world frame identity")
    return result

def relate(motion,unknown):
    if (type(motion) is not dict or type(unknown) is not dict
        or motion.get("schema")!="nih-phase1-original-world-source-motion/v1"
        or unknown.get("schema")!="nih-phase1-original-world-publication-uncertainty/v1"
        or motion.get("native_jobs")!=12 or unknown.get("original_native_jobs")!=12
        or motion.get("actual_world_solved") is not True
        or unknown.get("played_original_game_solved") is not True
        or motion.get("original_journals_preserved") is not True
        or unknown.get("original_native_journals_preserved") is not True
        or motion.get("source_partition_verified") is not True
        or unknown.get("independent_three_state_policy_verified") is not True
        or motion.get("new_native_job") is not False
        or unknown.get("new_native_job") is not False
        or motion.get("new_NIH_checkpoint") is not False
        or unknown.get("new_NIH_checkpoint") is not False
        or motion.get("real_historical_registry_version_authenticated") is not False
        or unknown.get("real_historical_publication_authenticated") is not False
        or motion.get("synthetic_only") is not True
        or unknown.get("synthetic_only") is not True
        or motion.get("clinical_verdict")!="NOT_EVALUATED"
        or unknown.get("clinical_verdict")!="NOT_EVALUATED"
        or motion.get("official_NIH_submission") is not False
        or unknown.get("official_NIH_submission") is not False):
        raise ValueError("different lineage, missing oracle, or unsupported scientific promotion")
    n=motion.get("actual_world_actions")
    if type(n) is not int or n<2 or unknown.get("world_actions")!=n:
        raise ValueError("game action sequence differs across original played observations")
    if (motion.get("selected_counterfactual_profiles")!=list(PROFILES)
        or unknown.get("cutoff_choices")!=list(CUTOFFS)
        or motion.get("original_emitted_python_sha256")!=unknown.get("original_emitted_python_sha256")):
        raise ValueError("original executable or source observation axis changed")
    profiles=motion.get("source_profile_sha256")
    if (type(profiles) is not dict or set(profiles)!=set(PROFILES)
        or len(set(profiles.values()))!=len(PROFILES)
        or any(type(v) is not str or len(v)!=64 for v in profiles.values())):
        raise ValueError("source versions lack independent dataset identities")
    fm=indexed(motion.get("actual_browser_source_frames"),
        ("turn","profile"),[(t,p) for t in range(n+1) for p in PROFILES])
    fu=indexed(unknown.get("observed_browser_frames"),
        ("turn","known_at"),[(t,k) for t in range(n+1) for k in CUTOFFS])
    program=motion["original_emitted_python_sha256"]
    prior_clock=None
    transitions=[]
    for turn in range(n+1):
        rows=[fm[turn,p] for p in PROFILES]
        baseline=rows[0]
        known=baseline.get("known_at")
        if known not in ("2026-01-04","2026-01-06"):
            raise ValueError("source exact-known assumption changed")
        if prior_clock is not None and known!=prior_clock:
            if prior_clock!="2026-01-04" or known!="2026-01-06":
                raise ValueError("original knowledge axis reversed")
            transitions.append(turn)
        prior_clock=known
        if any(r.get("known_at")!=known or r.get("target_at")!="2026-01-04"
               or r.get("source_program_sha256")!=program
               or r.get("source_dataset_sha256")!=profiles[r["profile"]]
               or r.get("independent_source_oracle_agreed") is not True
               for r in rows):
            raise ValueError("source-panel oracle, native clock or dataset moved")
        for cutoff in CUTOFFS:
            u=fu[turn,cutoff]
            if (u.get("native_game_known_at")!=known or u.get("target_at")!="2026-01-04"
                or u.get("source_program_sha256")!=program
                or u.get("independent_source_policy_agreement") is not True):
                raise ValueError("source-policy clock or original Python identity differs")
            # Enforce every independently observed cutoff, not merely the
            # two selected counterexample turns. Partial mutations must fail.
            expected={
                "2026-01-03":"definitely_withheld_ids",
                "2026-01-04":"indeterminate_ids",
                "2026-01-06":"indeterminate_ids",
                "2026-01-07":"admitted_ids"}[cutoff]
            groups=("admitted_ids","definitely_withheld_ids","indeterminate_ids")
            if (u.get("static_valid_ids")!=["delayed-result","prior-note"]
                or any(type(u.get(k)) is not list for k in groups)
                or sum("delayed-result" in u[k] for k in groups)!=1
                or "delayed-result" not in u[expected]):
                raise ValueError("original bounded publication interval falsely resolved")
    if len(transitions)!=1:
        raise ValueError("original browser cutover missing or repeated")
    cut=transitions[0]
    early=fm[cut-1,"original"]
    later=fm[cut,"original"]
    if ("delayed-result" not in early["future_leakage_ids"]
        or "delayed-result" in early["temporal_ids"]
        or "delayed-result" not in later["temporal_ids"]
        or "delayed-result" in later["future_leakage_ids"]
        or "delayed-result" not in fm[cut,"later-knowledge"]["future_leakage_ids"]
        or "delayed-result" in fm[cut,"later-knowledge"]["temporal_ids"]
        or not fm[0,"additional-conflict"]["declared_conflicts"]):
        raise ValueError("the originally witnessed source-motion counterexamples disappeared")
    # Same original game time; different explicit evidence assumption:
    # exact fictional known_at is allowed to answer deterministically, but a
    # bounded/unverified publication date is NOT licensed to copy that answer.
    counterexamples=[]
    for turn in (cut-1,cut):
        known=fm[turn,"original"]["known_at"]
        original=fm[turn,"original"]
        bounded=fu[turn,known]
        if "delayed-result" not in bounded["indeterminate_ids"]:
            raise ValueError("unsupported certainty promoted from uncertain publication")
        exact="ADMITTED" if "delayed-result" in original["temporal_ids"] else "WITHHELD"
        if exact!=("WITHHELD" if turn<cut else "ADMITTED"):
            raise ValueError("original exact-source cutover was not reproduced")
        counterexamples.append({"turn":turn,"original_game_known_at":known,
            "observation_id":"delayed-result",
            "exact_synthetic_known_at_projection":exact,
            "bounded_hypothetical_publication_projection":"INDETERMINATE"})
    calls=motion.get("independently_verified_original_python_calls")
    uncertainty_calls=unknown.get("actual_original_python_calls")
    if (type(calls) is not list or len(calls)<len(fm)
        or type(uncertainty_calls) is not list or len(uncertainty_calls)<len(fu)):
        raise ValueError("actual independent original Python evidence is missing")
    return {"schema":SCHEMA,"original_native_jobs":12,
        "original_game_actions":n,"native_cutover_turn":cut,
        "source_browser_frames":len(fm),
        "publication_browser_frames":len(fu),
        "new_original_python_calls":len(calls)+len(uncertainty_calls),
        "original_emitted_python_sha256":program,
        "source_motion_receipt_sha256":digest(motion),
        "publication_uncertainty_receipt_sha256":digest(unknown),
        "two_independent_browser_panels_cross_checked":True,
        "exact_vs_unknown_publication_counterexamples":counterexamples,
        "same_native_journal_verified_by_invoker":True,
        "real_historical_publication_authenticated":False,
        "synthetic_only":True,"clinical_verdict":"NOT_EVALUATED",
        "new_native_jobs":0,"new_NIH_checkpoint":False,
        "official_NIH_submission":False}
