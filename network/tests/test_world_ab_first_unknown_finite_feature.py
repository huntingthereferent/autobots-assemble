"""Independent WORLD34 finite SAT / source corner feature witness.

Original source clips finite segments against a local-frame rotating square.
Here the native original finite segments are checked with separately derived
world-coordinate SAT and rigid-vertex velocities, never with a fifth impulse.
"""
from __future__ import annotations

from copy import deepcopy
from math import cos,sin
import unittest

from systems.workspace.world_ab_first_unknown_finite_feature import (
    attempt,run,SCHEMA,EDGE_EPS,RATE_EPS
)
from systems.workspace.world_ab_local_plane_prefix import attempt as source33
from network.tests.test_world_ab_local_plane_prefix import verify as verify33
from systems.workspace.world_ab_first_finite_response_qualification import attempt as source29
from systems.workspace.world_ab_third_contact import attempt as source21,ANGLES
from network.tests.test_world_ab_finite_segment_square_overlap import sat_segment_square
from network.tests.test_world_ab_geometry_at_first_envelope_limit import original_planes
from systems.workspace.world_ab_oblique_impact import HALF

CCW=((-HALF,-HALF),(HALF,-HALF),(HALF,HALF),(-HALF,HALF))
SOURCE_MAP=(0,3,1,2)
EPS=4e-6


def world_corner(h,i,t):
    x,y=CCW[SOURCE_MAP[i]]
    theta=h["contact_orientation"]+h["outgoing_spin"]*t
    co,si=cos(theta),sin(theta)
    r=(co*x-si*y,si*x+co*y)
    p=(h["contact_center"][0]+h["outgoing_velocity"][0]*t+r[0],
       h["contact_center"][1]+h["outgoing_velocity"][1]*t+r[1])
    return p,r


def verify(row):
    angle=row.get("angle")
    prior=source33(angle)
    parent=source29(angle)
    ancestor=source21(angle)
    if angle not in ANGLES or row.get("schema")!=SCHEMA or not verify33(prior):
        raise ValueError("original first-unknown source identity invalid")
    expected={
        "source_trial33_schema":prior["schema"],
        "source_trial33_status":prior["status"],
        "source_first_unknown_subinterval":prior["first_unknown_subinterval"],
        "source_supported_prefix_end":prior["supported_prefix_end_time"],
        "source_conditional_fourth_response":parent["conditional_fourth_response"],
        "original_world":[24.,6.],
        "original_static_finite_faces":2,
        "conditional_unselected_response_only":True,
        "material_fifth_impact_witnessed":False,
        "fifth_impulse_selected":False,
        "real_material_trajectory_authenticated":False,
        "new_receiver_constructed":False,
        "continuation_after_first_unknown_solved":False,
    }
    if any(row.get(k)!=v for k,v in expected.items()):
        raise ValueError("original first-unknown state or physical boundary changed")
    if prior["status"]!="FIRST_LOCAL_HALFPLANE_BOUND_UNRESOLVED":
        if (row.get("status")!="NO_UNRESOLVED_SOURCE_LOCAL_INTERVAL"
            or row.get("source_finite_face_probes")!=[]
            or row.get("earliest_local_model_candidate") is not None
            or row.get("unique_incoming_source_feature") is not None):
            raise ValueError("already covered case acquired a fifth candidate")
        return True
    a=prior["first_unknown_subinterval"]["start"]
    b=prior["first_unknown_subinterval"]["end"]
    feature=parent["qualifying_source_feature"]
    fourth=parent["conditional_fourth_response"]
    h={"contact_center":feature["contact_center"],
       "contact_orientation":feature["contact_angle"],
       "outgoing_velocity":fourth["outgoing_velocity"],
       "outgoing_spin":fourth["outgoing_spin"]}
    planes=original_planes(ancestor,angle)[:2]
    probes=row.get("source_finite_face_probes")
    if type(probes) is not list or len(probes)!=2:
        raise ValueError("two unchanged source finite faces missing")
    with_transition=[]
    for report,(name,n,anchor,span) in zip(probes,planes):
        direction=(-n[1],n[0])
        segment=[
            [anchor[0]-direction[0]*span/2,anchor[1]-direction[1]*span/2],
            [anchor[0]+direction[0]*span/2,anchor[1]+direction[1]*span/2],
        ]
        start=sat_segment_square(h,segment,a)
        midpoint=sat_segment_square(h,segment,(a+b)/2)
        end=sat_segment_square(h,segment,b)
        if (report.get("source_face")!=name
            or report.get("original_finite_segment")!=segment
            or report.get("first_unknown_interval")!=[a,b]
            or report.get("sampled_overlap_left") is not start
            or report.get("sampled_overlap_midpoint") is not midpoint
            or report.get("sampled_overlap_right") is not end
            or report.get("numerical_root_not_formally_certified") is not True
            or report.get("material_contact_measured") is not False):
            raise ValueError("independent finite world SAT disagrees with original clipping")
        if start or not end:
            if (report.get("status")!="NO_SEPARATED_TO_INTERSECTING_ENDPOINT_BRACKET"
                or report.get("refined_model_transition_time") is not None
                or report.get("candidate_source_corners")!=[]
                or report.get("qualified_unique_incoming_corner") is not None):
                raise ValueError("unbracketed original feature became candidate")
            continue
        lo,hi=a,b
        for _ in range(49):
            mid=(lo+hi)/2
            if sat_segment_square(h,segment,mid):
                hi=mid
            else:
                lo=mid
        reported=report.get("refined_model_transition_time")
        if (not isinstance(reported,(float,int)) or
            not a<=reported<=b or abs(reported-hi)>EPS):
            raise ValueError("original refined finite-onset bracket differs from SAT")
        tangent=(-n[1],n[0])
        matches=[]
        for i in range(4):
            p,r=world_corner(h,i,reported)
            d=(p[0]-anchor[0],p[1]-anchor[1])
            gap=d[0]*n[0]+d[1]*n[1]
            along=d[0]*tangent[0]+d[1]*tangent[1]
            velocity=(h["outgoing_velocity"][0]-h["outgoing_spin"]*r[1],
                      h["outgoing_velocity"][1]+h["outgoing_spin"]*r[0])
            rate=velocity[0]*n[0]+velocity[1]*n[1]
            if abs(gap)<=EDGE_EPS and abs(along)<span/2-EDGE_EPS:
                matches.append((i,gap,along,rate,p))
        observations=report.get("candidate_source_corners")
        if type(observations) is not list or len(observations)!=len(matches):
            raise ValueError("rotating source vertex feature candidates altered")
        for observed,(idx,gap,along,rate,p) in zip(observations,matches):
            if (observed.get("source_corner_index")!=idx
                or observed.get("source_face")!=name
                or abs(observed.get("normal_gap",99)-gap)>EPS
                or abs(observed.get("finite_face_tangent_coordinate",99)-along)>EPS
                or abs(observed.get("incoming_normal_rate",99)-rate)>EPS
                or any(abs(x-y)>EPS for x,y in zip(
                    observed.get("contact_model_position",[]),p))):
                raise ValueError("original incoming finite corner identity changed")
        incoming=[x for x in matches if x[3]<-RATE_EPS]
        unique=len(matches)==len(incoming)==1
        if (report.get("qualified_unique_incoming_corner") !=
            (observations[0] if unique else None)):
            raise ValueError("simultaneous or nonincoming original contact promoted")
        kind=("UNIQUE_INCOMING_FINITE_CORNER_MODEL_CANDIDATE" if unique
              else "FINITE_MODEL_TRANSITION_BUT_CONTACT_FEATURE_UNRESOLVED")
        if report.get("status")!=kind:
            raise ValueError("unqualified numerical feature promoted")
        with_transition.append(report)
    with_transition.sort(key=lambda x:(x["refined_model_transition_time"],x["source_face"]))
    first=with_transition[0] if with_transition else None
    if row.get("earliest_local_model_candidate")!=first:
        raise ValueError("earliest numerical finite transition changed")
    if first is None:
        status="FIRST_LOCAL_UNKNOWN_WITH_NO_FINITE_TRANSITION_BRACKET"
    elif (len(with_transition)>1 and
          abs(with_transition[1]["refined_model_transition_time"]-
              first["refined_model_transition_time"])<3e-7):
        status="SIMULTANEOUS_FINITE_MODEL_FEATURE_UNRESOLVED"
    elif first["qualified_unique_incoming_corner"] is None:
        status="FINITE_OVERLAP_TRANSITION_FEATURE_UNRESOLVED"
    else:
        status="FIRST_FINITE_MODEL_CORNER_TRANSITION_QUALIFIED"
    qualified=(first["qualified_unique_incoming_corner"]
               if status=="FIRST_FINITE_MODEL_CORNER_TRANSITION_QUALIFIED" else None)
    if row.get("status")!=status or row.get("unique_incoming_source_feature")!=qualified:
        raise ValueError("original finite candidate/source contact qualification changed")
    return True


class World34Tests(unittest.TestCase):
    def test_only_unverified_first_local_interval_can_supply_candidate(self):
        report=run()
        self.assertEqual(report["schema"],SCHEMA)
        self.assertEqual(report["source_first_unknown_cases"],1)
        self.assertEqual(report["inactive_source_controls"],7)
        self.assertEqual(report["material_contacts_measured"],0)
        self.assertEqual(report["fifth_impulses_selected"],0)
        self.assertLessEqual(report["uniquely_incoming_finite_corner_cases"],1)
        for row in report["cases"]:
            with self.subTest(angle=row["angle"]):
                self.assertTrue(verify(row))

    def test_covered_other_angles_never_acquire_a_fifth_candidate(self):
        for a in (0.,5.,12.25,20.):
            row=attempt(a)
            self.assertEqual(row["status"],"NO_UNRESOLVED_SOURCE_LOCAL_INTERVAL")
            self.assertIsNone(row["unique_incoming_source_feature"])

    def test_real_impulse_and_fabricated_time_refused(self):
        source=attempt(10.)
        for key,val in (
            ("material_fifth_impact_witnessed",True),
            ("fifth_impulse_selected",True),
            ("real_material_trajectory_authenticated",True),
            ("continuation_after_first_unknown_solved",True),
            ("original_world",[24.,24.]),
        ):
            forged=deepcopy(source);forged[key]=val
            with self.subTest(key=key),self.assertRaises(ValueError):verify(forged)
        altered=deepcopy(source)
        altered["source_supported_prefix_end"]+=.001
        with self.assertRaises(ValueError):verify(altered)


if __name__=="__main__":
    unittest.main()
