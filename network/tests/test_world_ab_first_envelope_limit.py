"""Independent WORLD31 first-limit witness using closed-form quadratic bounds.

WORLD31 native source bisects each source-owned original Taylor inequality.
This verifier derives its separate *analytic* first threshold, rechecks the
original independent WORLD30 witness, and demands the entire bounded record,
first restrictive plane/corner set and nonmaterial epistemic boundary match.

A sufficiency-envelope limit is NOT a fifth collision or actual contact.
"""
from __future__ import annotations

from copy import deepcopy
from math import sqrt,isfinite
import unittest

from systems.workspace.world_ab_first_envelope_limit import (
    attempt,run,constraint_limit,SCHEMA,HORIZON,WINDOW,LIMIT_MARGIN,TIME_TOLERANCE
)
from systems.workspace.world_ab_post_fourth_local_clearance import attempt as source30
from network.tests.test_world_ab_post_fourth_local_clearance import verify as independently_verify30
from systems.workspace.world_ab_first_finite_response_qualification import attempt as source29
from systems.workspace.world_ab_third_contact import ANGLES

ROOT_TOL=3e-7


def analytic_limit(original):
    """First threshold from the original fixed-world normal quadratic."""
    g=original["gap_at_candidate"]
    v=original["outgoing_normal_rate"]
    a=original["curvature_upper_bound"]
    if original["starts_at_qualified_contact"]:
        if abs(g)>3e-6 or v<=LIMIT_MARGIN:
            raise ValueError("source touching vertex never qualified")
        t=float("inf") if a==0 else (v-LIMIT_MARGIN)/a
    else:
        if g<=LIMIT_MARGIN:
            raise ValueError("source noncontact corner initial gap not positive")
        if a<0:
            raise ValueError("source second-derivative bound negative")
        if a==0:
            t=float("inf") if v>=0 else (g-LIMIT_MARGIN)/(-v)
        else:
            t=(v+sqrt(v*v+2*a*(g-LIMIT_MARGIN)))/a
    if not t>WINDOW-ROOT_TOL:
        raise ValueError("original WORLD30 shorter interval not covered")
    return max(WINDOW,min(HORIZON,t))


def check(row):
    angle=row.get("angle")
    if row.get("schema")!=SCHEMA or angle not in ANGLES:
        raise ValueError("original source identity changed")
    original=source30(angle)
    previous=source29(angle)
    if not independently_verify30(original):
        raise ValueError("original source30 independent witness failed")
    immutable={
        "source_trial30_schema":original["schema"],
        "source_trial30_status":original["status"],
        "original_source30_case":original,
        "source_trial29_schema":previous["schema"],
        "source_trial29_status":previous["status"],
        "source_qualified_fourth_response":previous["conditional_fourth_response"],
        "original_24_by_6_world":[24.,6.],
        "source_original_minimum_horizon":WINDOW,
        "declared_followup_horizon":HORIZON,
        "positive_separation_margin":LIMIT_MARGIN,
        "original_24_halfplane_constraints":24,
        "same_original_two_finite_source_faces":True,
        "original_model_response_only":True,
        "physical_fourth_impulse_selected":False,
        "fifth_impulse_solved":False,
        "fifth_contact_feature_observed":False,
        "physical_trajectory_recorded":False,
        "exact_interval_arithmetic_certificate":False,
        "post_limit_continuation_admitted":False,
    }
    if any(row.get(k)!=v for k,v in immutable.items()):
        raise ValueError("source geometry ancestry or physical scope changed")
    if previous["conditional_fourth_response"] is None:
        if (row.get("status")!="NO_QUALIFIED_FOURTH_RESPONSE"
            or row.get("per_original_constraint_limits")!=[]
            or row.get("max_common_nominal_clearance_prefix") is not None
            or row.get("first_limiting_constraints")!=[]
            or row.get("original_constraints_checked")!=0):
            raise ValueError("unqualified source had invented response")
        return True
    if original["status"]!="CONDITIONAL_LOCAL_OUTGOING_SEPARATION":
        if (row.get("status")!="ORIGINAL_SHORT_LOCAL_GEOMETRY_UNRESOLVED"
            or row.get("per_original_constraint_limits")!=[]
            or row.get("max_common_nominal_clearance_prefix") is not None):
            raise ValueError("unverified short clearance promoted")
        return True
    bounds=original["clearance_bounds"]
    reported=row.get("per_original_constraint_limits")
    if len(bounds)!=24 or len(reported)!=24:
        raise ValueError("original constraint list not preserved")
    analytical=[]
    for a,b in zip(bounds,reported):
        t=analytic_limit(a)
        if not isfinite(t):
            raise ValueError("nonfinite analytically clipped support time")
        required={
            "source_plane":a["surface"],
            "source_corner_index":a["corner_index"],
            "source_starts_at_qualified_contact":a["starts_at_qualified_contact"],
            "original_gap_at_contact":a["gap_at_candidate"],
            "original_outgoing_normal_rate":a["outgoing_normal_rate"],
            "original_curvature_bound":a["curvature_upper_bound"],
            "at_short_window":True,
            "at_declared_horizon":t>=HORIZON-1e-10,
            "constraint_restricts_declared_horizon":t<HORIZON-1e-10,
        }
        if any(b.get(k)!=v for k,v in required.items()):
            raise ValueError("original corner/plane certificate changed")
        if abs(b.get("max_supported_prefix",-1)-t)>ROOT_TOL:
            raise ValueError("numeric bisection disagreed with independent analytic threshold")
        analytical.append(t)
    end=min(analytical)
    expected_limited=[z for z,t in zip(reported,analytical) if
                      t<=end+TIME_TOLERANCE and t<HORIZON-1e-10]
    if (row.get("original_constraints_checked")!=24
        or abs(row.get("max_common_nominal_clearance_prefix",-1)-end)>ROOT_TOL
        or row.get("first_limiting_constraints")!=expected_limited):
        raise ValueError("source lost limiting plane or support time")
    status=("NOMINAL_CLEARANCE_THROUGH_DECLARED_HORIZON" if end>=HORIZON-1e-10
            else "FIRST_SUFFICIENT_ENVELOPE_LIMIT_NOT_A_CONTACT")
    if row.get("status")!=status:
        raise ValueError("inconclusive envelope promoted to later contact")
    return True


class World31FirstSourceLimitTests(unittest.TestCase):
    def test_synthetic_quadratic_and_linear_thresholds(self):
        for g,v,c,t in ((.030,-.5,0.,(.03-LIMIT_MARGIN)/.5),
                        (.02,0.,2.,sqrt(.02-LIMIT_MARGIN)),
                        (.0,.4,4.,(.4-LIMIT_MARGIN)/4.)):
            datum={"gap_at_candidate":g,
                   "outgoing_normal_rate":v,
                   "curvature_upper_bound":c,
                   "starts_at_qualified_contact":g==0}
            out=constraint_limit(datum)
            self.assertAlmostEqual(out["max_supported_prefix"],t,places=6)
            self.assertAlmostEqual(analytic_limit(datum),t,places=6)
            self.assertTrue(out["constraint_restricts_declared_horizon"])

    def test_all_eight_source_candidates_and_controls_independent(self):
        summary=run()
        self.assertEqual(summary["schema"],SCHEMA)
        self.assertEqual(summary["qualified_original_responses"],3)
        self.assertEqual(summary["without_qualified_response"],5)
        self.assertEqual(summary["cases_clear_through_horizon"]+
                         summary["cases_with_prior_envelope_limit"],3)
        self.assertEqual(summary["contact_features_solved"],0)
        self.assertEqual(summary["fifth_impulses_computed"],0)
        self.assertEqual(summary["real_material_measurements"],0)
        for case in summary["cases"]:
            with self.subTest(angle=case["angle"]):
                self.assertTrue(check(case))

    def test_no_original_response_never_gets_future_prefix(self):
        for a in (0.,20.):
            c=attempt(a)
            self.assertEqual(c["status"],"NO_QUALIFIED_FOURTH_RESPONSE")
            self.assertIsNone(c["max_common_nominal_clearance_prefix"])

    def test_false_fifth_contact_and_changed_limit_refused(self):
        base=attempt(7.5)
        for key,value in (
            ("physical_fourth_impulse_selected",True),
            ("fifth_impulse_solved",True),
            ("declared_followup_horizon",2.),
            ("exact_interval_arithmetic_certificate",True),
            ("post_limit_continuation_admitted",True),
        ):
            forged=deepcopy(base);forged[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                check(forged)
        if base["per_original_constraint_limits"]:
            forged=deepcopy(base)
            forged["per_original_constraint_limits"][0]["max_supported_prefix"]=0.
            with self.assertRaises(ValueError):check(forged)


if __name__=="__main__":
    unittest.main()
