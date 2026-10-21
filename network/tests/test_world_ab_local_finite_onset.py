"""WORLD28 first finite onset independently reconstructed in world coordinates.

The source refines local onset with its signed SAT implementation. This witness
rebuilds rotating square geometry through independent SAT axes, bisects the
same ORIGINAL first grid interval, and verifies original WORLD23 vertex feature.
It never chooses a fourth impulse or treats a numeric root as physical contact.
"""
from __future__ import annotations

from copy import deepcopy
import unittest

from systems.workspace.world_ab_local_finite_onset import (
    attempt,run,refine,SCHEMA,TOL
)
from systems.workspace.world_ab_finite_segment_square_overlap import (
    attempt as source25, finite_clip, START,DURATION,SAMPLE_COUNT
)
from systems.workspace.world_ab_between_sample_clearance import attempt as source26
from systems.workspace.world_ab_all_inward_finite_features import attempt as source23
from systems.workspace.world_ab_third_contact import attempt as source21
from systems.workspace.world_ab_first_post_third_candidate import ANGLES
from network.tests.test_world_ab_between_sample_clearance import (
    separately_reconstructed_sat_margin, verify as verify26
)


def separate_refinement(h,segment,original_bracket):
    lo=original_bracket["last_grid_separated_at"]
    hi=original_bracket["first_grid_intersection_at"]
    signed=lambda t: separately_reconstructed_sat_margin(h,segment,t)
    if not (START<=lo<hi<=DURATION and signed(lo)>-1e-7 and signed(hi)<1e-7):
        raise ValueError("original finite first-onset bracket missing or corrupted")
    for _ in range(53):
        mid=(lo+hi)/2
        if signed(mid)>0:
            lo=mid
        else:
            hi=mid
    return lo,hi


def verify(row):
    a=row.get("angle")
    if row.get("schema")!=SCHEMA or a not in ANGLES:
        raise ValueError("trial/angle mismatch")
    prior25=source25(a)
    prior26=source26(a)
    prior23=source23(a)
    original=source21(a)
    if not verify26(prior26):
        raise ValueError("original WORLD26 independent witness missing")
    expected={
        "source_trial25_schema":prior25["schema"],
        "source_trial25_status":prior25["status"],
        "source_trial26_schema":prior26["schema"],
        "source_trial26_status":prior26["status"],
        "source_trial23_schema":prior23["schema"],
        "source_original_third_impulse":original["third_impulse"],
        "original_window":[START,DURATION],
        "original_sample_intervals":SAMPLE_COUNT,
        "finite_source_faces_unchanged":True,
        "nominal_conditional_motion_only":True,
        "certified_exact_root":False,
        "material_measurements":False,
        "fourth_impulse_selected":False,
        "new_receiver_constructed":False,
        "post_candidate_motion_solved":False,
    }
    if any(row.get(k)!=v for k,v in expected.items()):
        raise ValueError("original source or material scope altered")
    if original["third_impulse"] is None:
        if (row.get("status")!="NO_ADMITTED_THIRD_IMPULSE" or
            row.get("face_first_onsets")!=[] or
            row.get("first_eligible_finite_onset") is not None or
            row.get("cases_with_earlier_unknown_clear_sample_gaps")!=0):
            raise ValueError("source no-impulse control invented first contact")
        return True
    results=row.get("face_first_onsets")
    if type(results) is not list:
        raise ValueError("source finite candidate list omitted")
    evidence=[]
    uncovered=0
    for p,q in zip(prior25["face_results"],prior26["face_clearance_bounds"]):
        source_bracket=p["first_transition_bracket"]
        if source_bracket is None:
            continue
        match=[r for r in results if r["face"]==p["face"]]
        if len(match)!=1:
            raise ValueError("missing or repeated original finite face candidate")
        candidate=match[0]
        if candidate.get("original_grid_bracket")!=source_bracket:
            raise ValueError("original WORLD25 onset source replaced")
        index=p["sampled_intersection_windows"][0]["first_sample_index"]
        if index<=0:
            if candidate.get("status")!="FIRST_FRAME_ALREADY_INTERSECTING":
                raise ValueError("original already-intersecting control promoted")
            continue
        gap_indices=sorted(
            item["interval_index"] for item in q["uncovered_intervals"]
            if item["interval_index"] < index-1
        )
        if candidate.get("uncleared_intervals_before_onset")!=gap_indices:
            raise ValueError("unknown preceding source intervals omitted")
        uncovered+=int(bool(gap_indices))
        left,right=separate_refinement(original["third_impulse"],p["segment"],source_bracket)
        reported=candidate.get("refined_sat_bracket")
        if not isinstance(reported,dict):
            raise ValueError("missing finite SAT onset refinement")
        if (reported.get("numeric_bracket_only") is not True or
            reported.get("physically_witnessed") is not False or
            abs(reported["first_nominally_intersecting_time"]-right)>2e-7 or
            abs(reported["last_nominally_separated_time"]-left)>2e-7 or
            abs(reported["signed_sat_margin_at_left"])>1e-6 or
            abs(reported["signed_sat_margin_at_right"])>1e-6):
            raise ValueError("independent finite SAT root rejected")
        if finite_clip(original["third_impulse"],p["segment"],
                       reported["first_nominally_intersecting_time"]+2e-8)["overlap"] is not True:
            raise ValueError("refined candidate does not enter original finite segment")
        roots=[x["dt_after_third_impulse"] for x in prior23["eligible_geometry_roots"]
               if x["surface"]==p["face"]
               and x["feature_classification"]=="FINITE_FACE_INTERIOR_CANDIDATE"]
        first=min(roots) if roots else None
        confirmed=(first is not None and
                   abs(first-right)<=TOL)
        if (candidate.get("same_face_first_vertex_candidate_time")!=first or
            candidate.get("local_vertex_time_consistent") is not confirmed or
            candidate.get("source_after_first_contact_counterfactual") is not True):
            raise ValueError("source vertex relation not independently witnessed")
        status=("EARLIER_CLEAR_ENDPOINT_GAP_NOT_CERTIFIED" if gap_indices else
                "NUMERIC_FINITE_ONSET_ALIGNS_WITH_VERTEX_SOURCE" if confirmed else
                "NUMERIC_FINITE_ONSET_FEATURE_UNRESOLVED")
        if candidate.get("status")!=status:
            raise ValueError("unsupported onset feature promoted")
        evidence.append(candidate)
    evidence.sort(key=lambda c:(
        c["refined_sat_bracket"]["first_nominally_intersecting_time"],c["face"]))
    first=evidence[0] if evidence else None
    if row.get("first_eligible_finite_onset")!=first:
        raise ValueError("changed earliest numeric finite model onset")
    if row.get("cases_with_earlier_unknown_clear_sample_gaps")!=uncovered:
        raise ValueError("unknown source periods before onset discarded")
    expected_status=("NO_SAMPLED_FINITE_ONSET_IN_ORIGINAL_WINDOW" if not results else
                     "SOURCE_EARLIER_INTERVALS_REMAIN_UNRESOLVED" if uncovered else
                     "FIRST_NUMERICAL_FINITE_ONSET_CORROBORATED_BY_VERTEX" if
                     first is not None and first["local_vertex_time_consistent"] else
                     "FIRST_NUMERICAL_FINITE_ONSET_FEATURE_UNRESOLVED")
    if row.get("status")!=expected_status:
        raise ValueError("first candidate status invalid")
    return True


class World28Tests(unittest.TestCase):
    def test_known_translating_square_first_finite_contact(self):
        h={"contact_center":[0.,0.],"contact_orientation":0.,
           "outgoing_velocity":[1.,0.],"outgoing_spin":0.}
        face=[[.4,-.1],[.4,.1]]
        b={"last_grid_separated_at":.149,
           "first_grid_intersection_at":.151}
        r=refine(h,face,b)
        self.assertAlmostEqual(r["first_nominally_intersecting_time"],.15,places=7)
        lo,hi=separate_refinement(h,face,b)
        self.assertAlmostEqual(hi,.15,places=7)

    def test_original_eight_controls_reverified_and_retained(self):
        report=run()
        self.assertEqual(report["schema"],SCHEMA)
        self.assertEqual(report["admitted_third_impulse_cases"],6)
        self.assertEqual(report["no_source_impulse_controls"],2)
        self.assertEqual(report["actual_material_contacts_measured"],0)
        self.assertEqual(report["fourth_impulses_solved"],0)
        self.assertEqual(report["earlier_clear_endpoint_uncertainty_cases"],0)
        for row in report["cases"]:
            with self.subTest(angle=row["angle"]):
                self.assertTrue(verify(row))

    def test_unsupported_material_claim_and_source_tampering_refused(self):
        row=attempt(7.5)
        for key,value in (
            ("fourth_impulse_selected",True),
            ("material_measurements",True),
            ("certified_exact_root",True),
            ("original_window",[0.,1.]),
        ):
            bad=deepcopy(row)
            bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                verify(bad)
        bad=deepcopy(row)
        if bad["first_eligible_finite_onset"] is not None:
            bad["first_eligible_finite_onset"]["status"]="MATERIAL_IMPACT"
            with self.assertRaises(ValueError):verify(bad)


if __name__=="__main__":
    unittest.main()
