"""Independent WORLD36 original six-plane and rotating-square clearance witness.

World-space CCW corner reconstruction, separately computed Taylor bounds, and
a fail-closed comparison of each original constraint. No sixth contact inferred.
"""
from __future__ import annotations

from copy import deepcopy
from math import cos,sin,hypot,isfinite
import unittest

from systems.workspace.world_ab_post_fifth_local_clearance import (
    attempt,run,SCHEMA,WINDOW,MARGIN,CONTACT_TOL,
)
from systems.workspace.world_ab_whole_contact_configuration import attempt as prior35
from network.tests.test_world_ab_whole_contact_configuration import reconstruct as verify35
from systems.workspace.world_ab_first_finite_response_qualification import attempt as prior29
from systems.workspace.world_ab_third_contact import attempt as prior21,ANGLES
from network.tests.test_world_ab_geometry_at_first_envelope_limit import original_planes
from systems.workspace.world_ab_oblique_impact import HALF

CCW=((-HALF,-HALF),(HALF,-HALF),(HALF,HALF),(-HALF,HALF))
MAP=(0,3,1,2)
ERROR=1e-6


def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]


def independent_corner(center,theta,index):
    x,y=CCW[MAP[index]]
    c,s=cos(theta),sin(theta)
    r=(c*x-s*y,s*x+c*y)
    return r,(center[0]+r[0],center[1]+r[1])


def check(row):
    angle=row.get("angle")
    prior=prior35(angle)
    parent=prior29(angle)
    ancestor=prior21(angle)
    if (row.get("schema")!=SCHEMA or angle not in ANGLES
        or not verify35(prior)):
        raise ValueError("original independent Trial35 ancestry invalid")
    immutable={
        "source_trial35_schema":prior["schema"],
        "source_trial35_status":prior["status"],
        "original_trial35_conditional_response":prior["conditional_fifth_response"],
        "original_source_candidate_time":prior["candidate_virtual_time"],
        "original_24_by_6_world":[24.,6.],
        "original_finite_faces":2,
        "original_world_boundaries":4,
        "declared_local_horizon":WINDOW,
        "positive_clearance_guard":MARGIN,
        "source_model_only":True,
        "physical_fifth_impact_selected":False,
        "sixth_impact_measured":False,
        "sixth_impulse_calculated":False,
        "post_window_continuation_admitted":False,
        "new_receiver_created":False,
        "outward_rounded_interval_certificate":False,
    }
    if any(row.get(k)!=v for k,v in immutable.items()):
        raise ValueError("WORLD35 source or physical-refusal state changed")
    if prior["conditional_fifth_response"] is None:
        if (row.get("status")!="NO_QUALIFIED_FIFTH_RESPONSE"
            or row.get("same_original_24_constraints")!=[]
            or row.get("nominal_clearance_covered") is not False
            or row.get("conditional_fifth_contact_center") is not None):
            raise ValueError("unqualified fifth response fabricated a next interval")
        return True
    fifth=prior["conditional_fifth_response"]
    parent_feature=parent["qualifying_source_feature"]
    outgoing_fourth=parent["conditional_fourth_response"]
    t=prior["candidate_virtual_time"]
    center=(parent_feature["contact_center"][0]+outgoing_fourth["outgoing_velocity"][0]*t,
            parent_feature["contact_center"][1]+outgoing_fourth["outgoing_velocity"][1]*t)
    theta=parent_feature["contact_angle"]+outgoing_fourth["outgoing_spin"]*t
    velocity=fifth["outgoing_velocity"]
    spin=fifth["outgoing_spin"]
    if (any(abs(a-b)>ERROR for a,b in zip(row.get("conditional_fifth_contact_center",[]),center))
        or abs(row.get("conditional_fifth_contact_orientation",99)-theta)>ERROR
        or row.get("source_selected_face")!=prior["source_face"]
        or row.get("source_selected_corner")!=prior["candidate_corner"]):
        raise ValueError("original source fifth contact pose changed")
    planes=original_planes(ancestor,angle)
    if len(planes)!=6:
        raise ValueError("source original planes incomplete")
    observed=row.get("same_original_24_constraints")
    if type(observed) is not list or len(observed)!=24:
        raise ValueError("24 original corner-plane records required")
    qualified=0
    selected_count=0
    for j,(name,n,anchor,span) in enumerate(planes):
        for i in range(4):
            rec=observed[4*j+i]
            r,p=independent_corner(center,theta,i)
            gap=dot((p[0]-anchor[0],p[1]-anchor[1]),n)
            rate=dot((velocity[0]-spin*r[1],velocity[1]+spin*r[0]),n)
            curvature=spin*spin*hypot(HALF,HALF)
            floor=gap+rate*WINDOW-.5*curvature*WINDOW*WINDOW
            rate_floor=rate-curvature*WINDOW
            selected=name==prior["source_face"] and i==prior["candidate_corner"]
            selected_count+=int(selected)
            sufficient=(abs(gap)<=CONTACT_TOL and rate_floor>MARGIN
                        if selected else min(gap,floor)>MARGIN)
            lower=rate_floor if selected else min(gap,floor)
            expected={
                "source_plane":name,
                "source_corner_index":i,
                "selected_source_contact":selected,
                "original_plane_is_finite":span is not None,
                "interval_supported":sufficient,
                "material_contact_observed":False,
                "classification":("QUALIFIED_OUTGOING_CONTACT_NORMAL_RATE" if sufficient
                                  else "CONTACT_DEPARTURE_UNRESOLVED") if selected
                                  else ("OTHER_ORIGINAL_CORNER_POSITIVE_CLEARANCE" if sufficient
                                  else "OTHER_ORIGINAL_CORNER_CLEARANCE_UNRESOLVED"),
            }
            if any(rec.get(k)!=v for k,v in expected.items()):
                raise ValueError("source original plane identity or classification changed")
            numeric={
                "gap_at_hypothetical_fifth":gap,
                "outgoing_normal_rate":rate,
                "curvature_upper_bound":curvature,
                "end_gap_taylor_lower_bound":floor,
                "outgoing_rate_lower_bound":rate_floor,
                "conservative_lower_bound":lower,
            }
            if any(not isinstance(rec.get(k),(float,int))
                   or not isfinite(rec[k]) or abs(rec[k]-v)>ERROR
                   for k,v in numeric.items()):
                raise ValueError("independent rotating-world coordinate witness mismatch")
            qualified+=int(sufficient)
    if selected_count!=1 or row.get("supported_original_constraints")!=qualified or (
        row.get("unresolved_original_constraints")!=24-qualified):
        raise ValueError("selected original corner or number of supported constraints changed")
    full=qualified==24
    expected_status=("CONDITIONAL_FIFTH_LOCAL_CLEARANCE_NOMINALLY_SUPPORTED" if full
                     else "POST_FIFTH_LOCAL_SEPARATION_INEQUALITIES_UNRESOLVED")
    if (row.get("nominal_clearance_covered") is not full
        or row.get("status")!=expected_status):
        raise ValueError("bound failure promoted into source motion or sixth event")
    return True


class World36Tests(unittest.TestCase):
    def test_all_original_cases_replayed_by_separate_world_corner_equations(self):
        data=run()
        self.assertEqual(data["schema"],SCHEMA)
        self.assertEqual(data["original_conditional_fifth_responses"],1)
        self.assertEqual(data["without_qualified_fifth_response"],7)
        self.assertEqual(data["nominal_short_clearance_cases"]+
                         data["locally_unresolved_cases"],1)
        self.assertEqual(data["physical_fifth_impacts"],0)
        self.assertEqual(data["sixth_impulses"],0)
        for rec in data["cases"]:
            with self.subTest(angle=rec["angle"]):
                self.assertTrue(check(rec))

    def test_absent_original_fifth_never_creates_later_clearance(self):
        for a in (0.,5.,12.25,20.):
            r=attempt(a)
            self.assertEqual(r["status"],"NO_QUALIFIED_FIFTH_RESPONSE")
            self.assertEqual(r["same_original_24_constraints"],[])

    def test_independent_witness_refuses_false_sixth_or_tampered_gap(self):
        original=attempt(10.)
        for k,v in (("sixth_impact_measured",True),
                    ("sixth_impulse_calculated",True),
                    ("physical_fifth_impact_selected",True),
                    ("post_window_continuation_admitted",True),
                    ("new_receiver_created",True),
                    ("outward_rounded_interval_certificate",True),
                    ("original_24_by_6_world",[24.,24.])):
            forged=deepcopy(original);forged[k]=v
            with self.subTest(key=k),self.assertRaises(ValueError):check(forged)
        fake=deepcopy(original)
        fake["same_original_24_constraints"][0]["outgoing_normal_rate"]+=.1
        with self.assertRaises(ValueError):check(fake)

    def test_clearance_lower_bounds_require_positive_margin(self):
        from systems.workspace.world_ab_post_fifth_local_clearance import bound
        # A departing selected corner with outward rate is supported locally.
        b=bound([0.,0.],0.,[2.,0.],0.,0,(1.,0.),
                (-HALF,-HALF),True)
        self.assertTrue(b["interval_supported"])
        # An incoming corner is not certified by a superficially positive gap.
        c=bound([0.,0.],0.,[-2.,0.],0.,0,(1.,0.),
                (-HALF,-HALF),True)
        self.assertFalse(c["interval_supported"])


if __name__=="__main__":
    unittest.main()
