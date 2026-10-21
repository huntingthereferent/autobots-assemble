"""Independent WORLD32 finite geometry at source WORLD31 first bound limits.

The original source uses local-frame finite-segment clipping for square/face
overlap. This verifier independently reconstructs all source planes, model
corner poses and world-coordinate separating-axis geometry from prior source.
It does not turn a source sufficient-bound limit into a fifth actual contact.
"""
from __future__ import annotations

from copy import deepcopy
from math import cos,sin
import unittest

from systems.workspace.world_ab_geometry_at_first_envelope_limit import (
    attempt,run,SCHEMA,EPS
)
from systems.workspace.world_ab_first_envelope_limit import attempt as source31,constraint_limit
from network.tests.test_world_ab_first_envelope_limit import check as verify31
from systems.workspace.world_ab_first_finite_response_qualification import attempt as source29
from systems.workspace.world_ab_third_contact import attempt as source21,ANGLES
from systems.workspace.world_ab_local_recontact_impulse import attempt as source18
from systems.workspace.world_ab_oblique_impact import HALF,WALL_CENTER
from systems.workspace.world_ab_finite_segment_square_overlap import finite_clip
from network.tests.test_world_ab_finite_segment_square_overlap import sat_segment_square
from network.tests.test_world_ab_between_sample_clearance import separately_reconstructed_sat_margin

CORNERS=((-HALF,-HALF),(HALF,-HALF),(HALF,HALF),(-HALF,HALF))
# Mapping between local source indices and the independent CCW corner order.
SOURCE_INDEX_IN_CCW=(0,3,1,2)
ERROR=3e-6


def dot(x,y):
    return x[0]*y[0]+x[1]*y[1]


def original_planes(original,angle):
    first=source18(angle)["source_first_contact"]
    receiver=original["source_receiver"]
    return [
        ("original_finite_face",tuple(first["normal"]),tuple(WALL_CENTER),1.),
        ("motion_derived_receiver",tuple(receiver["normal"]),
         tuple(receiver["anchor"]),1.),
        ("world_left",(1.,0.),(0.,0.),None),
        ("world_right",(-1.,0.),(24.,0.),None),
        ("world_bottom",(0.,1.),(0.,0.),None),
        ("world_top",(0.,-1.),(0.,6.),None),
    ]


def independent_pose(original,dt,i):
    theta=original["contact_orientation"]+dt*original["outgoing_spin"]
    cx=original["contact_center"][0]+original["outgoing_velocity"][0]*dt
    cy=original["contact_center"][1]+original["outgoing_velocity"][1]*dt
    x,y=CORNERS[SOURCE_INDEX_IN_CCW[i]]
    co,si=cos(theta),sin(theta)
    return (cx+co*x-si*y,cy+si*x+co*y)


def model(original_response,feature):
    return {
        "contact_center":feature["contact_center"],
        "contact_orientation":feature["contact_angle"],
        "outgoing_velocity":original_response["outgoing_velocity"],
        "outgoing_spin":original_response["outgoing_spin"],
    }


def verify(row):
    angle=row.get("angle")
    if row.get("schema")!=SCHEMA or angle not in ANGLES:
        raise ValueError("invalid source trial identity")
    original31=source31(angle)
    if not verify31(original31):
        raise ValueError("original independent WORLD31 witness missing")
    earlier=source29(angle)
    ancestor=source21(angle)
    required={
        "source_trial31_schema":original31["schema"],
        "source_trial31_status":original31["status"],
        "source_first_nominal_limit":original31["max_common_nominal_clearance_prefix"],
        "source_limiting_constraints":original31["first_limiting_constraints"],
        "source_conditional_fourth_response":earlier["conditional_fourth_response"],
        "original_24_by_6_world":[24.,6.],
        "original_source_faces":2,
        "source_declared_max_horizon":.25,
        "conditional_mathematical_pose_only":True,
        "actual_material_fifth_contact_measured":False,
        "fifth_impulse_calculated":False,
        "new_receiver_constructed":False,
        "post_limit_ballistic_movement_admitted":False,
        "certified_exact_first_contact":False,
    }
    if any(row.get(k)!=v for k,v in required.items()):
        raise ValueError("source source-limit ancestry or physical refusal changed")
    if earlier["conditional_fourth_response"] is None:
        if (row.get("status")!="NO_QUALIFIED_FOURTH_RESPONSE"
            or row.get("finite_face_model_states")!=[]
            or row.get("limiting_corner_model_states")!=[]
            or row.get("original_boundary_min_gaps")!=[]
            or row.get("model_finite_overlap_at_limit") is not False):
            raise ValueError("no original fourth response fabricated further movement")
        return True
    if original31["status"]!="FIRST_SUFFICIENT_ENVELOPE_LIMIT_NOT_A_CONTACT":
        if (row.get("status")!="NO_FIRST_LIMIT_WITHIN_DECLARED_HORIZON"
            or row.get("finite_face_model_states")!=[]
            or row.get("limiting_corner_model_states")!=[]
            or row.get("original_boundary_min_gaps")!=[]):
            raise ValueError("model horizon with no first limit promoted")
        return True
    t=original31["max_common_nominal_clearance_prefix"]
    h=model(earlier["conditional_fourth_response"],earlier["qualifying_source_feature"])
    planes=original_planes(ancestor,angle)
    states=row.get("finite_face_model_states")
    if type(states) is not list or len(states)!=2:
        raise ValueError("two original finite face positions required")
    overlaps=[]
    near=False
    for record,(name,n,anchor,span) in zip(states,planes[:2]):
        tangent=(-n[1],n[0])
        segment=[
            [anchor[0]-span*tangent[0]/2,anchor[1]-span*tangent[1]/2],
            [anchor[0]+span*tangent[0]/2,anchor[1]+span*tangent[1]/2],
        ]
        source_reported=record.get("source_finite_clip_overlap_at_limit")
        independently=sat_segment_square(h,segment,t)
        signed=separately_reconstructed_sat_margin(h,segment,t)
        if (record.get("source_face")!=name
            or record.get("source_original_segment")!=segment
            or source_reported is not independently
            or record.get("model_only_not_material_measurement") is not True
            or abs(record.get("signed_sat_separation_at_limit",99)-signed)>ERROR):
            raise ValueError("original finite square/segment source differs from independent SAT")
        along=record.get("source_clip_entry_fraction")
        exit=record.get("source_clip_exit_fraction")
        if independently:
            if (not isinstance(along,(float,int)) or
                not isinstance(exit,(float,int)) or
                not 0<=along<=exit<=1):
                raise ValueError("finite clip fraction did not lie in original segment")
        elif along is not None or exit is not None:
            raise ValueError("invented finite intersection clipping fractions")
        overlaps.append(independently)
        near|=abs(signed)<=EPS
    world=[]
    for (name,n,anchor,span),rec in zip(planes[2:],row.get("original_boundary_min_gaps",[])):
        if span is not None:
            raise ValueError("original perimeter unexpectedly finite")
        gaps=[
            dot((p[0]-anchor[0],p[1]-anchor[1]),n)
            for p in [independent_pose(h,t,i) for i in range(4)]
        ]
        if (rec.get("plane")!=name or
            len(rec.get("four_vertex_gaps",[]))!=4 or
            any(abs(a-b)>ERROR for a,b in zip(rec["four_vertex_gaps"],gaps)) or
            abs(rec.get("minimum_model_gap",99)-min(gaps))>ERROR or
            rec.get("world_boundary_measured") is not False):
            raise ValueError("original world perimeter evidence changed")
        world.append(min(gaps))
    if len(world)!=4:
        raise ValueError("missing original world perimeter constraints")
    expected=[]
    for prior in original31["first_limiting_constraints"]:
        plane=next((x for x in planes if x[0]==prior["source_plane"]),None)
        if plane is None:
            raise ValueError("original limiting source plane not in world")
        name,n,anchor,span=plane
        idx=prior["source_corner_index"]
        p=independent_pose(h,t,idx)
        diff=(p[0]-anchor[0],p[1]-anchor[1])
        tangent=(-n[1],n[0])
        u=dot(diff,tangent) if span is not None else None
        expected.append((name,idx,p,dot(diff,n),u,
                         abs(u)<span/2 if u is not None else None))
    actual=row.get("limiting_corner_model_states")
    if type(actual) is not list or len(actual)!=len(expected):
        raise ValueError("original first limiting source identities missing")
    for record,(name,idx,p,gap,u,inside) in zip(actual,expected):
        if (record.get("source_plane")!=name
            or record.get("source_corner_index")!=idx
            or any(abs(a-b)>ERROR for a,b in zip(record.get("model_corner_position",[]),p))
            or abs(record.get("actual_signed_gap_in_conditional_model",99)-gap)>ERROR
            or record.get("within_finite_source_face_tangent_span") is not inside
            or record.get("no_material_sensor") is not True):
            raise ValueError("original restricting feature/source signed gap altered")
        observed_u=record.get("finite_face_tangent_coordinate")
        if (u is None and observed_u is not None or
            u is not None and
            (not isinstance(observed_u,(float,int)) or abs(observed_u-u)>ERROR)):
            raise ValueError("original finite face limiting corner tangential coordinate changed")
    overlap=any(overlaps)
    expected_status=("SAMPLED_CONDITIONAL_FINITE_INTERSECTION_AT_EVIDENCE_LIMIT"
                     if overlap else
                     "CONDITIONAL_WORLD_BOUNDARY_OR_GRAZING_GEOMETRY_UNRESOLVED"
                     if near or any(v<=EPS for v in world) else
                     "CONDITIONAL_FINITE_SHAPES_SEPARATED_AT_EVIDENCE_LIMIT")
    if row.get("status")!=expected_status or row.get("model_finite_overlap_at_limit") is not overlap:
        raise ValueError("evidence-bound failure fabricated a contact or masked finite geometry")
    return True


class Trial32Tests(unittest.TestCase):
    def test_a_sufficient_margin_can_expire_while_finite_shapes_still_separate(self):
        h={"contact_center":[0.,0.],
           "contact_orientation":0.,
           "outgoing_velocity":[.5,0.],
           "outgoing_spin":0.}
        segment=[[.28,-.15],[.28,.15]]
        datum={"gap_at_candidate":.03,
               "outgoing_normal_rate":-.5,
               "curvature_upper_bound":0.,
               "starts_at_qualified_contact":False}
        bound=constraint_limit(datum)
        t=bound["max_supported_prefix"]
        self.assertAlmostEqual(t,(.03-1e-5)/.5,places=7)
        self.assertFalse(finite_clip(h,segment,t)["overlap"])
        self.assertFalse(sat_segment_square(h,segment,t))

    def test_all_three_source_first_limit_poses_have_independent_sat_witness(self):
        report=run()
        self.assertEqual(report["schema"],SCHEMA)
        self.assertEqual(report["source_limit_model_cases"],3)
        self.assertEqual(report["without_qualified_fourth_response"],5)
        self.assertEqual(report["actual_material_impacts_measured"],0)
        self.assertEqual(report["fifth_impulses_solved"],0)
        self.assertEqual(report["finite_intersection_at_evidence_limit_cases"]+
                         report["finite_shapes_separated_at_limit_cases"]+
                         report["ambiguous_or_grazing_limit_cases"],3)
        for row in report["cases"]:
            with self.subTest(angle=row["angle"]):
                self.assertTrue(verify(row))

    def test_absent_hypothetical_response_never_creates_geometry(self):
        for angle in (0.,20.):
            row=attempt(angle)
            self.assertEqual(row["status"],"NO_QUALIFIED_FOURTH_RESPONSE")
            self.assertEqual(row["finite_face_model_states"],[])

    def test_false_real_fifth_impact_and_altered_geometric_state_refused(self):
        row=attempt(5.)
        for key,value in (
            ("actual_material_fifth_contact_measured",True),
            ("fifth_impulse_calculated",True),
            ("source_declared_max_horizon",1.),
            ("post_limit_ballistic_movement_admitted",True),
            ("certified_exact_first_contact",True),
        ):
            fake=deepcopy(row);fake[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                verify(fake)
        fake=deepcopy(row)
        fake["source_first_nominal_limit"]=.99
        with self.assertRaises(ValueError):verify(fake)
        if row["limiting_corner_model_states"]:
            fake=deepcopy(row)
            fake["limiting_corner_model_states"][0]["actual_signed_gap_in_conditional_model"]+=.03
            with self.assertRaises(ValueError):verify(fake)


if __name__=="__main__":
    unittest.main()
