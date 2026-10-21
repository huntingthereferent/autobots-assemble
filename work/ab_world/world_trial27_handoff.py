"""WORLD27 three-way interval classification, preserving original WORLD25/26.

The pinned original model and its independently reconstructed SAT/velocity
oracle own all geometric claims. Neutral A/B records source interval classes:
sampled-intersection adjacent, genuinely unproved clear-endpoint, and
nominal sufficient separation. No fourth impact or real material proof.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from work.ab_world.construction import PLAN, digest, load_json, run_plan
from work.ab_world.verify_construction import verify_receipt

SCHEMA = "ab-world-trial27-partitioned-finite-interval-evidence/v1"
SOURCE = "world-ab-sampled-contact-versus-unknown-gap/v1"
SOURCE25 = "world-ab-finite-segment-rotating-square-intersection/v1"
SOURCE26 = "world-ab-between-sample-conditional-finite-clearance/v1"
PIN = "d1268d30c58825500354137ebdd3b140a131a84e"
ANGLES = (0., 2.5, 5., 7.5, 10., 12.25, 15., 20.)
FACES = ("original_finite_face", "motion_derived_receiver")
START, END, N = .008, .25, 2048
HIT = "AT_LEAST_ONE_ENDPOINT_HAS_SAMPLED_FINITE_OVERLAP"
UNKNOWN = "BOTH_ENDPOINT_SAMPLES_SEPARATED_BUT_ENVELOPE_INSUFFICIENT"
COVERED = "NOMINAL_SEPARATION_SUFFICIENT_ON_FULL_INTERVAL"
CLASSES = (HIT,UNKNOWN,COVERED)


def require(ok: bool, explanation: str) -> None:
    if not ok:
        raise ValueError("A/B WORLD27: "+explanation)


def reconstruct_partition(record25: dict, record26: dict, reported: dict) -> dict:
    require(type(record25) is dict and type(record26) is dict and
            type(reported) is dict and
            record25.get("face") == record26.get("face") == reported.get("face") and
            record25.get("segment") == record26.get("segment") and
            record25.get("samples_checked") == N+1 and
            record26.get("grid_intervals_checked") == N and
            record26.get("formal_outward_rounded_certificate") is False,
            "original finite source face or source sample grid substituted")
    flags=[False]*(N+1)
    windows=record25.get("sampled_intersection_windows")
    require(type(windows) is list,"source sampled finite intersections missing")
    for block in windows:
        require(type(block) is dict and
                type(block.get("first_sample_index")) is int and
                type(block.get("last_sample_index")) is int,
                "native overlap grid indices missing")
        lo,hi=block["first_sample_index"],block["last_sample_index"]
        require(0<=lo<=hi<=N,"native overlap index out of bounds")
        for j in range(lo,hi+1):
            require(not flags[j],"source sampled overlap windows multiply counted")
            flags[j]=True
    require(sum(flags)==record25.get("intersecting_grid_samples") and
            flags[0] is record25.get("start_intersected"),
            "source sampled intersection flags disagree with native count")
    rows=record26.get("uncovered_intervals")
    require(type(rows) is list and len(rows)==record26.get("uncovered_interval_count"),
            "source original uncovered intervals missing")
    uncertain=set()
    previous=-1
    for row in rows:
        require(type(row) is dict and type(row.get("interval_index")) is int and
                previous < row["interval_index"] < N and
                row.get("classification")=="NOT_CERTIFIED_BY_ENDPOINT_MARGIN",
                "source uncertain intervals reordered or promoted")
        previous=row["interval_index"]
        uncertain.add(previous)
    labels=[]
    for j in range(N):
        hit=flags[j] or flags[j+1]
        require(not hit or j in uncertain,
                "sampled finite overlap falsely declared nominally separated")
        labels.append(HIT if hit else UNKNOWN if j in uncertain else COVERED)
    counts={k:labels.count(k) for k in CLASSES}
    spans=[]
    for j,label in enumerate(labels):
        if not spans or spans[-1]["classification"]!=label:
            spans.append({"first_interval_index":j,
                          "last_interval_index":j,
                          "classification":label})
        else:
            spans[-1]["last_interval_index"]=j
    clear_unknown=[j for j,label in enumerate(labels) if label==UNKNOWN]
    expected={
        "face":record25["face"],
        "source_sampled_overlap_count":record25["intersecting_grid_samples"],
        "source_uncovered_interval_count":record26["uncovered_interval_count"],
        "classified_interval_counts":counts,
        "ordered_classification_spans":spans,
        "uncovered_both_samples_separated_intervals":clear_unknown,
        "physical_contact_measurements":0,
        "formal_intervals_certified":0,
    }
    require(reported==expected,"source27 independent three-way interval partition altered")
    require(sum(counts.values())==N and
            counts[HIT]+counts[UNKNOWN]==len(uncertain),
            "source finite interval partition not exhaustive")
    return expected


def carry(native27: dict[str,Any],native25: dict[str,Any],
          native26: dict[str,Any],source_commit: str = PIN) -> dict[str,Any]:
    require(source_commit==PIN,"source original immutable commit changed")
    require(type(native27) is dict and native27.get("schema")==SOURCE and
            native27.get("angles")==list(ANGLES) and
            native27.get("physical_measurements")==0 and
            native27.get("selected_fourth_impulses")==0 and
            native27.get("new_engine_or_world") is False and
            type(native25) is dict and native25.get("schema")==SOURCE25 and
            native25.get("angles")==list(ANGLES) and
            native25.get("fourth_impulses_solved")==0 and
            type(native26) is dict and native26.get("schema")==SOURCE26 and
            native26.get("angles")==list(ANGLES) and
            native26.get("fourth_impulses_selected")==0,
            "pinned source three-way classification/physical boundaries changed")
    cases27,cases25,cases26=(q.get("cases") for q in
                             (native27,native25,native26))
    require(all(type(q) is list and len(q)==8 for q in
                (cases27,cases25,cases26)),"original eight angles absent")
    source_basis={"kind":"source-execution",
                  "source":"original WORLD25/26/27 @" + PIN}
    declared={"kind":"declared",
              "source":"sampled finite overlap vs nominal margin sufficiency"}
    pages=[]
    total={k:0 for k in CLASSES}
    admitted=refused=unknown_cases=hit_cases=0
    for i,angle in enumerate(ANGLES):
        row,x25,x26=(q[i] for q in (cases27,cases25,cases26))
        require(all(type(q) is dict for q in (row,x25,x26)) and
                row.get("schema")==SOURCE and row.get("angle")==angle and
                x25.get("schema")==SOURCE25 and x25.get("angle")==angle and
                x26.get("schema")==SOURCE26 and x26.get("angle")==angle and
                row.get("source_trial25_schema")==SOURCE25 and
                row.get("source_trial26_schema")==SOURCE26 and
                row.get("source_trial25_status")==x25.get("status") and
                row.get("source_trial26_status")==x26.get("status") and
                row.get("original_source_third_impulse")==
                x25.get("source_third_impulse")==x26.get("source_third_impulse"),
                "original three source stages or third-impulse ancestry altered")
        for key,value in (
            ("source_original_window",[START,END]),
            ("source_intervals_per_face",N),
            ("unchanged_original_24_by_6_world",True),
            ("conditional_ballistic_model_only",True),
            ("physical_event_witnessed",False),
            ("fourth_impulse_selected",False),
            ("new_receiver_constructed",False),
            ("formal_root_or_interval_certificate",False),
        ):
            require(row.get(key)==value,
                    "source geometric time bound or material claim changed: "+key)
        impulse=row["original_source_third_impulse"]
        joined=row.get("face_partitions")
        local=row.get("totals")
        require(type(joined) is list and type(local) is dict and
                all(type(local.get(k)) is int and local[k]>=0 for k in CLASSES),
                "source finite classification or totals missing")
        known=impulse is not None
        if not known:
            require(row.get("status")=="NO_ADMITTED_THIRD_IMPULSE" and
                    joined==[] and
                    local=={k:0 for k in CLASSES} and
                    x25.get("face_results")==[] and
                    x26.get("face_clearance_bounds")==[],
                    "absent source third impulse acquired imagined finite movement")
            refused+=1
        else:
            admitted+=1
            require(type(impulse) is dict and impulse.get("materially_witnessed") is False and
                    len(joined)==2 and
                    type(x25.get("face_results")) is list and
                    type(x26.get("face_clearance_bounds")) is list and
                    len(x25["face_results"])==len(x26["face_clearance_bounds"])==2,
                    "original two finite faces or conditional third impulse missing")
            rebuilt=[
                reconstruct_partition(prev,margin,now)
                for prev,margin,now in zip(x25["face_results"],
                                           x26["face_clearance_bounds"],joined)]
            require([x["face"] for x in rebuilt]==list(FACES),
                    "finite face identity/order changed")
            computed={k:sum(face["classified_interval_counts"][k]
                            for face in rebuilt) for k in CLASSES}
            require(local==computed and sum(local.values())==2*N,
                    "native case totals inconsistent with original complete grid")
            label=("SAMPLED_FINITE_OVERLAP_WITH_SEPARATE_UNKNOWN_TAILS"
                   if computed[HIT] else
                   "CLEAR_GRID_ENDPOINTS_WITH_UNRESOLVED_GAPS"
                   if computed[UNKNOWN] else
                   "ALL_FACE_INTERVALS_NOMINALLY_SEPARATED")
            require(row.get("status")==label,
                    "original interval classification promoted to contact or full certificate")
            hit_cases+=int(computed[HIT]>0)
            unknown_cases+=int(computed[UNKNOWN]>0)
        for key in CLASSES:
            total[key]+=local[key]
        steps=[
            {"op":"introduce","id":"original-conditional-square",
             "state":{"source_angle":angle,"third_impulse_model":deepcopy(impulse),
                      "real_material_contact":False,"fourth_impulse":None},
             "basis":source_basis},
            {"op":"introduce","id":"bounded-finite-interval-partition",
             "state":{"world":[24.,6.],"window":[START,END],
                      "intervals_per_original_face":N,
                      "source_status":row["status"],
                      "physical_intervals_certified":0},"basis":declared},
            {"op":"connect","id":"original-square-finite-evidence",
             "from":"original-conditional-square",
             "to":"bounded-finite-interval-partition",
             "label":"source-owned-nominal-face-interval-tests",
             "state":{"unselected_model_third_impulse":known,
                      "new_receiver_constructed":False}, "basis":declared},
            {"op":"observe","id":"source25-26-ancestry",
             "entity":"object","subject":"bounded-finite-interval-partition",
             "reading":{"native_source25_digest":digest(x25),
                        "native_source26_digest":digest(x26),
                        "source25_sampled_overlap_count":
                            x26.get("source_trial25_intersecting_grid_samples"),
                        "source26_unknown_interval_count":
                            x26.get("uncovered_total_intervals"),
                        "material_measurements":0}, "basis":source_basis},
        ]
        for j,part in enumerate(joined):
            rec=x25["face_results"][j]
            steps.extend([
                {"op":"introduce","id":f"original-finite-face-{j}",
                 "state":{"face":part["face"],
                          "endpoints":deepcopy(rec["segment"]),
                          "from_original_source":True,
                          "new_physical_geometry":False},
                 "basis":source_basis},
                {"op":"connect","id":f"tested-source-face-{j}",
                 "from":f"original-finite-face-{j}",
                 "to":"bounded-finite-interval-partition",
                 "label":"finite-segment-rotating-square-grid-partition",
                 "state":{"original_face_unchanged":True},
                 "basis":declared},
                {"op":"observe","id":f"native-source-face-partition-{j}",
                 "entity":"object","subject":f"original-finite-face-{j}",
                 "reading":{"native_three_way_partition":deepcopy(part),
                            "native_source_face_digest":digest(rec),
                            "nominallly_classified_not_hardware":True},
                 "basis":source_basis},
            ])
        steps.extend([
            {"op":"observe","id":"source27-whole-case-verdict",
             "entity":"object","subject":"bounded-finite-interval-partition",
             "reading":{"source_case_digest":digest(row),
                        "status":row["status"],
                        "native_counts":deepcopy(local),
                        "source_candidate_not_material_hit":True,
                        "fourth_impulse_selected":False},
             "basis":source_basis},
            {"op":"observe","id":"source27-contrast",
             "entity":"object","subject":"original-conditional-square",
             "reading":{"conditional_source_admitted":known,
                        "sampled_overlap_endpoint_intervals":local[HIT]>0,
                        "clear_endpoint_unknown_intervals":local[UNKNOWN]>0,
                        "material_collision_measured":False},
             "basis":source_basis},
            {"op":"compare","id":"no-sampled-finite-overlap-hypothesis",
             "observation":"source27-contrast",
             "expected":{"conditional_source_admitted":known,
                        "sampled_overlap_endpoint_intervals":False,
                        "clear_endpoint_unknown_intervals":local[UNKNOWN]>0,
                        "material_collision_measured":False},
             "basis":declared},
            {"op":"compare","id":"no-clear-endpoint-unknown-hypothesis",
             "observation":"source27-contrast",
             "expected":{"conditional_source_admitted":known,
                        "sampled_overlap_endpoint_intervals":local[HIT]>0,
                        "clear_endpoint_unknown_intervals":False,
                        "material_collision_measured":False},
             "basis":declared},
        ])
        plan={"schema":PLAN,
              "referent":f"WORLD27 / original finite interval types {angle}deg",
              "limits":{"objects":4,"relations":3,"steps":len(steps)},
              "steps":steps}
        receipt=run_plan(plan)
        w=verify_receipt(receipt)
        result=receipt["final"]["comparisons"]
        require(w["valid"] and
                result["no-sampled-finite-overlap-hypothesis"]["result"]==
                ("DIFFERENT" if local[HIT] else "MATCH") and
                result["no-clear-endpoint-unknown-hypothesis"]["result"]==
                ("DIFFERENT" if local[UNKNOWN] else "MATCH"),
                "independent A/B source contrast failed")
        pages.append({"case":i,"angle":angle,"source_status":row["status"],
                      "hit":local[HIT],"uncertain":local[UNKNOWN],
                      "nominal":local[COVERED],
                      "receipt":receipt,"witness":w})
    require(native27.get("source_conditional_impulse_cases")==admitted==6 and
            native27.get("no_impulse_controls")==refused==2 and
            native27.get("cases_with_unobserved_only_uncertainty")==unknown_cases and
            native27.get("classified_face_intervals")==total and
            total[HIT]+total[UNKNOWN]+total[COVERED]==6*2*N,
            "pinned aggregate three-way interval classifications changed")
    manifest={"pinned_source_commit":PIN,
              "source27_digest":digest(native27),
              "source25_digest":digest(native25),
              "source26_digest":digest(native26),
              "ordered_receipt_heads":[
                  {"case":p["case"],"angle":p["angle"],
                   "head_hash":p["receipt"]["head_hash"]}
                  for p in pages]}
    return {"schema":SCHEMA,"source_commit":PIN,
            "original_angle_controls":8,"conditional_third_impulse_cases":admitted,
            "no_original_impulse_controls":refused,
            "sampled_overlap_adjacent_intervals":total[HIT],
            "clear_endpoint_unknown_intervals":total[UNKNOWN],
            "nominal_covered_intervals":total[COVERED],
            "sampled_overlap_cases":hit_cases,
            "clear_endpoint_unknown_cases":unknown_cases,
            "fourth_impulses_selected":0,"material_impacts_measured":0,
            "actual_continuous_contact_response_solved":False,
            "formally_rounded_certificate":False,
            "ledger_pages":pages,
            "ledger_witness":{
                "valid":all(p["witness"]["valid"] for p in pages),
                "pages_verified":len(pages),
                "steps_verified":sum(p["witness"]["steps_verified"] for p in pages),
                "observations_recorded":sum(p["witness"]["observations_recorded"] for p in pages)},
            "manifest":manifest,"manifest_sha256":digest(manifest)}


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--native",type=Path,required=True)
    parser.add_argument("--source25",type=Path,required=True)
    parser.add_argument("--source26",type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(carry(load_json(args.native),load_json(args.source25),
                           load_json(args.source26)),sort_keys=True,indent=2))


if __name__ == "__main__":
    main()
