"""Independent WORLD26 interval-margin / between-grid counterexample witness.

The original generator uses fixed-world-axis SAT sample margins plus a rigid
corner speed envelope. This verifier independently reconstructs the rotating
polygon and finite segment projections, challenges every interval's source
classification, and tests an intentionally sub-grid finite intersection.

Not a formally outward-rounded or measured physical clearance certificate.
"""
from __future__ import annotations

from copy import deepcopy
from math import cos, sin, hypot, sqrt
import unittest

from systems.workspace.world_ab_between_sample_clearance import (
    attempt, run, face_windows, SCHEMA, GUARD, START, DURATION, SAMPLE_COUNT,
)
from systems.workspace.world_ab_finite_segment_square_overlap import (
    attempt as source25, finite_clip
)
from systems.workspace.world_ab_third_contact import attempt as source21
from systems.workspace.world_ab_oblique_impact import HALF
from systems.workspace.world_ab_first_post_third_candidate import ANGLES

EPS = 4e-7
CORNERS = ((-HALF,-HALF),(HALF,-HALF),(HALF,HALF),(-HALF,HALF))


def dot(x,y):
    return x[0]*y[0]+x[1]*y[1]


def separately_reconstructed_sat_margin(h,segment,t):
    theta=h["contact_orientation"]+h["outgoing_spin"]*t
    c,s=cos(theta),sin(theta)
    cx=h["contact_center"][0]+h["outgoing_velocity"][0]*t
    cy=h["contact_center"][1]+h["outgoing_velocity"][1]*t
    world_corners=[
        (cx+c*x-s*y,cy+s*x+c*y) for x,y in CORNERS
    ]
    direction=(segment[1][0]-segment[0][0],
               segment[1][1]-segment[0][1])
    size=hypot(*direction)
    if size<=1e-12:
        raise ValueError("invalid finite source segment")
    candidate_normals=[
        (world_corners[1][0]-world_corners[0][0],
         world_corners[1][1]-world_corners[0][1]),
        (world_corners[2][0]-world_corners[1][0],
         world_corners[2][1]-world_corners[1][1]),
        direction,
    ]
    # From each edge direction, build a world normal; source instead
    # computes the square's angle axes and the source segment normal.
    best=float("-inf")
    for dx,dy in candidate_normals:
        scale=hypot(dx,dy)
        axis=(-dy/scale,dx/scale)
        moving=[dot(p,axis) for p in world_corners]
        fixed=[dot(p,axis) for p in segment]
        separation=max(min(moving)-max(fixed),min(fixed)-max(moving))
        best=max(best,separation)
    return best


def verify(case):
    angle=case.get("angle")
    if case.get("schema")!=SCHEMA or angle not in ANGLES:
        raise ValueError("source trial identity changed")
    original=source21(angle)
    before=source25(angle)
    expected={
        "source_trial25_schema":before["schema"],
        "source_trial25_status":before["status"],
        "source_trial25_intersecting_grid_samples":sum(
            r["intersecting_grid_samples"] for r in before["face_results"]),
        "source_third_impulse":original["third_impulse"],
        "source_receiver":original["source_receiver"],
        "observation_start":START,
        "observation_end":DURATION,
        "sample_intervals":SAMPLE_COUNT,
        "nominal_velocity_margin_guard":GUARD,
        "unchanged_existing_two_finite_faces":True,
        "model_free_flight_hypothesis_only":True,
        "physical_motion_witnessed":False,
        "selected_fourth_impulse":False,
        "new_receiver_constructed":False,
        "certified_floating_point_interval_arithmetic":False,
        "counterfactual_after_any_earlier_contact":True,
    }
    if any(case.get(k)!=v for k,v in expected.items()):
        raise ValueError("original finite source ancestry/claim changed")
    if original["third_impulse"] is None:
        if (case.get("status")!="NO_ADMITTED_THIRD_IMPULSE"
            or case.get("face_clearance_bounds")!=[]
            or case.get("fully_nominally_covered_faces")!=0
            or case.get("uncovered_total_intervals")!=0):
            raise ValueError("absent third impulse invented later motion")
        return True
    if original["status"]!="CONDITIONAL_LOCAL_SEPARATION":
        raise ValueError("third impulse not conditionally admitted")
    h=original["third_impulse"]
    velocity=h["outgoing_velocity"]
    speed=hypot(*velocity)+abs(h["outgoing_spin"])*hypot(HALF,HALF)
    faces=case.get("face_clearance_bounds")
    if type(faces) is not list or len(faces)!=2:
        raise ValueError("both original finite faces required")
    dt=(DURATION-START)/SAMPLE_COUNT
    total=0
    whole=0
    for observed,prior in zip(faces,before["face_results"]):
        segment=prior["segment"]
        if observed.get("face")!=prior["face"] or observed.get("segment")!=segment:
            raise ValueError("original finite face changed")
        if abs(observed.get("velocity_norm_upper_bound",0)-speed)>EPS:
            raise ValueError("corner velocity upper bound was weakened")
        if (observed.get("sampled_margins_count")!=SAMPLE_COUNT+1
            or observed.get("grid_intervals_checked")!=SAMPLE_COUNT
            or observed.get("formal_outward_rounded_certificate") is not False):
            raise ValueError("claimed formal proof or changed source sample count")
        # Evaluate every native grid point using independently reconstructed
        # world-space polygon axes rather than the generator's axis formula.
        margins=[
            separately_reconstructed_sat_margin(h,segment,START+i*dt)
            for i in range(SAMPLE_COUNT+1)
        ]
        uncovered=[]
        proven=[]
        for i in range(SAMPLE_COUNT):
            left,right=margins[i],margins[i+1]
            remaining=left+right-speed*dt
            admitted=(left>GUARD and right>GUARD and remaining>2*GUARD)
            if admitted:
                proven.append(remaining)
                # Extra independent midpoint falsification check: if either
                # sample axis supports full coverage, midpoint must separate.
                midpoint=START+(i+.5)*dt
                m=separately_reconstructed_sat_margin(h,segment,midpoint)
                if m < -EPS:
                    raise ValueError("supposed interval covering refuted by SAT midpoint")
                if finite_clip(h,segment,midpoint)["overlap"]:
                    raise ValueError("nominally clear interval physically overlaps in model")
            else:
                uncovered.append(i)
        observed_unknown=observed.get("uncovered_intervals")
        if type(observed_unknown) is not list or len(observed_unknown)!=len(uncovered):
            raise ValueError("source omitted unknown between-frame intervals")
        for i,item in zip(uncovered,observed_unknown):
            if (item.get("interval_index")!=i
                or abs(item.get("start",-10)-(START+i*dt))>EPS
                or abs(item.get("end",-10)-(START+(i+1)*dt))>EPS
                or abs(item.get("sample_start_separating_margin",-99)-margins[i])>EPS
                or abs(item.get("sample_end_separating_margin",-99)-margins[i+1])>EPS
                or abs(item.get("velocity_envelope_surplus",-99)-
                       (margins[i]+margins[i+1]-speed*dt))>EPS
                or item.get("classification")!="NOT_CERTIFIED_BY_ENDPOINT_MARGIN"):
                raise ValueError("unknown interval classification changed")
        if (observed.get("uncovered_interval_count")!=len(uncovered)
            or observed.get("endpoint_margin_covered_intervals")!=len(proven)
            or observed.get("all_intervals_nominally_covered") is not (not uncovered)):
            raise ValueError("source endpoint interval cover count changed")
        claimed_min=observed.get("minimum_covered_margin_surplus")
        if (claimed_min is None) != (not proven):
            raise ValueError("minimum certified surplus missing or invented")
        if proven and abs(claimed_min-min(proven))>EPS:
            raise ValueError("source minimum guaranteed margin altered")
        whole+=int(not uncovered)
        total+=len(uncovered)
    if case.get("fully_nominally_covered_faces")!=whole:
        raise ValueError("whole finite-face counts changed")
    if case.get("uncovered_total_intervals")!=total:
        raise ValueError("source unknown interval count changed")
    label=("ALL_FINITE_FACE_INTERVALS_NOMINALLY_SEPARATED" if whole==2
           else "SAMPLED_FINITE_INTERSECTION_WITH_UNRESOLVED_BETWEEN_FRAMES"
           if before["faces_with_sampled_intersection"]>0
           else "SOME_BETWEEN_FRAME_INTERVALS_REMAIN_UNRESOLVED")
    if case.get("status")!=label:
        raise ValueError("unsupported whole-interval status promoted")
    return True


class World26NumericalIntervalTests(unittest.TestCase):
    def test_fast_unobserved_between_grid_intersection_is_not_proved_clear(self):
        # At t=START, the square is left of a vertical segment. Within the
        # first sampling interval it sweeps across the segment and escapes,
        # so both endpoint samples are separated despite intervening overlap.
        h={
            "contact_center":[-8000.3,0.],
            "contact_orientation":0.,
            "outgoing_velocity":[1_000_000.,0.],
            "outgoing_spin":0.,
        }
        face=[[.4,-.1],[.4,.1]]
        dt=(DURATION-START)/SAMPLE_COUNT
        self.assertFalse(finite_clip(h,face,START)["overlap"])
        self.assertFalse(finite_clip(h,face,START+dt)["overlap"])
        self.assertTrue(finite_clip(h,face,START+0.00000045)["overlap"])
        bound=face_windows(h,"synthetic-fast-face",face)
        self.assertGreater(bound["uncovered_interval_count"],0)
        self.assertEqual(bound["uncovered_intervals"][0]["interval_index"],0)
        self.assertFalse(bound["all_intervals_nominally_covered"])

    def test_original_eight_conditional_cases_check_all_grid_intervals(self):
        report=run()
        self.assertEqual(report["schema"],SCHEMA)
        self.assertEqual(report["conditional_third_impulse_cases"],6)
        self.assertEqual(report["no_source_third_impulse_controls"],2)
        self.assertEqual(report["actual_hardware_measurements"],0)
        self.assertEqual(report["fourth_impulses_selected"],0)
        self.assertEqual(report["new_physical_receivers_constructed"],0)
        for case in report["cases"]:
            with self.subTest(angle=case["angle"]):
                self.assertTrue(verify(case))

    def test_absent_impulse_never_earns_between_frame_certificate(self):
        for angle in (0.,20.):
            result=attempt(angle)
            self.assertEqual(result["status"],"NO_ADMITTED_THIRD_IMPULSE")
            self.assertEqual(result["face_clearance_bounds"],[])

    def test_forged_continuity_hardware_and_omitted_unknown_interval_rejected(self):
        result=attempt(7.5)
        for key,value in (
            ("certified_floating_point_interval_arithmetic",True),
            ("physical_motion_witnessed",True),
            ("selected_fourth_impulse",True),
            ("observation_end",2.),
            ("counterfactual_after_any_earlier_contact",False),
        ):
            altered=deepcopy(result)
            altered[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                verify(altered)
        altered=deepcopy(result)
        if altered["face_clearance_bounds"]:
            x=altered["face_clearance_bounds"][0]
            x["endpoint_margin_covered_intervals"]+=1
            with self.assertRaises(ValueError):
                verify(altered)


if __name__=="__main__":
    unittest.main()
