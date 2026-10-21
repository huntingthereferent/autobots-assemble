"""WORLD27 — distinguish sampled finite overlap from unproved clear-endpoint gaps.

Existing original WORLD25 supplies sampled intersection windows. WORLD26
supplies sufficient nominal separating-envelope coverage and leaves 2,290
face-time intervals uncovered. Classify these *without changing either source*:
(1) at least one endpoint sample intersects, (2) both sample poses separate
but the envelope is insufficient, (3) nominal envelope supports separation.

Not a new contact solver: a sampled intersection is conditional geometry,
an uncovered separated-endpoint interval is UNKNOWN (not a collision), and
nominal coverage is not a formally outward-rounded numerical certificate.
"""
from __future__ import annotations

from systems.workspace.world_ab_between_sample_clearance import (
    attempt as source26, SAMPLE_COUNT, START, DURATION
)
from systems.workspace.world_ab_finite_segment_square_overlap import attempt as source25
from systems.workspace.world_ab_third_contact import attempt as source21, ANGLES

SCHEMA="world-ab-sampled-contact-versus-unknown-gap/v1"
HIT="AT_LEAST_ONE_ENDPOINT_HAS_SAMPLED_FINITE_OVERLAP"
UNKNOWN="BOTH_ENDPOINT_SAMPLES_SEPARATED_BUT_ENVELOPE_INSUFFICIENT"
COVERED="NOMINAL_SEPARATION_SUFFICIENT_ON_FULL_INTERVAL"


def classified_intervals(face25,face26):
    """Run-length encoded interval partition with strict source ancestry."""
    if (face25["face"]!=face26["face"] or
        face25["segment"]!=face26["segment"] or
        face25["samples_checked"]!=SAMPLE_COUNT+1 or
        face26["grid_intervals_checked"]!=SAMPLE_COUNT):
        raise ValueError("changed original finite face or sample grid")
    flags=[False]*(SAMPLE_COUNT+1)
    for cluster in face25["sampled_intersection_windows"]:
        lo,hi=cluster["first_sample_index"],cluster["last_sample_index"]
        if not (type(lo) is type(hi) is int and 0<=lo<=hi<=SAMPLE_COUNT):
            raise ValueError("invalid sample-overlap cluster")
        for j in range(lo,hi+1):
            if flags[j]:
                raise ValueError("overlapping source sample clusters")
            flags[j]=True
    if (sum(flags)!=face25["intersecting_grid_samples"] or
        flags[0] is not face25["start_intersected"]):
        raise ValueError("source finite grid sample evidence inconsistent")
    indices=[]
    for item in face26["uncovered_intervals"]:
        j=item["interval_index"]
        if type(j) is not int or not 0<=j<SAMPLE_COUNT or (indices and j<=indices[-1]):
            raise ValueError("source unknown interval roster reordered")
        if item["classification"]!="NOT_CERTIFIED_BY_ENDPOINT_MARGIN":
            raise ValueError("source uncertainty promoted")
        indices.append(j)
    if len(indices)!=face26["uncovered_interval_count"]:
        raise ValueError("source unknown count mismatch")
    unknown_set=set(indices)
    labels=[]
    for i in range(SAMPLE_COUNT):
        sampled=flags[i] or flags[i+1]
        uncovered=i in unknown_set
        if sampled and not uncovered:
            raise ValueError("sampled overlap falsely certified clear")
        labels.append(HIT if sampled else UNKNOWN if uncovered else COVERED)
    spans=[]
    for i,label in enumerate(labels):
        if not spans or spans[-1]["classification"]!=label:
            spans.append({"first_interval_index":i,
                          "last_interval_index":i,
                          "classification":label})
        else:
            spans[-1]["last_interval_index"]=i
    counts={k:labels.count(k) for k in (HIT,UNKNOWN,COVERED)}
    if sum(counts.values())!=SAMPLE_COUNT or counts[HIT]+counts[UNKNOWN]!=len(indices):
        raise ValueError("incomplete separation / unknown source partition")
    return {"face":face25["face"],
            "source_sampled_overlap_count":face25["intersecting_grid_samples"],
            "source_uncovered_interval_count":face26["uncovered_interval_count"],
            "classified_interval_counts":counts,
            "ordered_classification_spans":spans,
            "uncovered_both_samples_separated_intervals":[
                i for i,x in enumerate(labels) if x==UNKNOWN],
            "physical_contact_measurements":0,
            "formal_intervals_certified":0}


def attempt(angle):
    old25=source25(angle)
    old26=source26(angle)
    old21=source21(angle)
    base={
        "schema":SCHEMA,"angle":float(angle),
        "source_trial25_schema":old25["schema"],
        "source_trial25_status":old25["status"],
        "source_trial26_schema":old26["schema"],
        "source_trial26_status":old26["status"],
        "original_source_third_impulse":old21["third_impulse"],
        "source_original_window":[START,DURATION],
        "source_intervals_per_face":SAMPLE_COUNT,
        "unchanged_original_24_by_6_world":True,
        "conditional_ballistic_model_only":True,
        "physical_event_witnessed":False,
        "fourth_impulse_selected":False,
        "new_receiver_constructed":False,
        "formal_root_or_interval_certificate":False,
    }
    if old21["third_impulse"] is None:
        if old25["face_results"] or old26["face_clearance_bounds"]:
            raise ValueError("missing source impulse acquired finite contact data")
        return {**base,"status":"NO_ADMITTED_THIRD_IMPULSE",
                "face_partitions":[], "totals":{HIT:0,UNKNOWN:0,COVERED:0}}
    if not (len(old25["face_results"])==len(old26["face_clearance_bounds"])==2):
        raise ValueError("two original source finite faces required")
    faces=[classified_intervals(a,b) for a,b in zip(
        old25["face_results"],old26["face_clearance_bounds"])]
    total={key:sum(p["classified_interval_counts"][key] for p in faces)
           for key in (HIT,UNKNOWN,COVERED)}
    if total[HIT]:
        status="SAMPLED_FINITE_OVERLAP_WITH_SEPARATE_UNKNOWN_TAILS"
    elif total[UNKNOWN]:
        status="CLEAR_GRID_ENDPOINTS_WITH_UNRESOLVED_GAPS"
    else:
        status="ALL_FACE_INTERVALS_NOMINALLY_SEPARATED"
    return {**base,"status":status,"face_partitions":faces,"totals":total}


def run():
    records=[attempt(a) for a in ANGLES]
    totals={k:sum(c["totals"][k] for c in records)
            for k in (HIT,UNKNOWN,COVERED)}
    return {"schema":SCHEMA,"angles":list(ANGLES),"cases":records,
            "source_conditional_impulse_cases":sum(
                c["original_source_third_impulse"] is not None for c in records),
            "no_impulse_controls":sum(c["status"]=="NO_ADMITTED_THIRD_IMPULSE"
                                     for c in records),
            "classified_face_intervals":totals,
            "cases_with_unobserved_only_uncertainty":sum(
                c["totals"][UNKNOWN]>0 for c in records),
            "physical_measurements":0,"selected_fourth_impulses":0,
            "new_engine_or_world":False}
