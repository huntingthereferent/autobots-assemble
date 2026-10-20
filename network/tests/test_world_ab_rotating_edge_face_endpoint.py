"""Independent WORLD24 rotating-edge / finite-endpoint numerical witness.

The native verifier reconstructs WORLD21 and WORLD22, then independently
transforms each of four square edges and both endpoints of the two existing
finite source faces. It uses 8,192-step signed-edge root sweeps rather than
the generator's 4,096-step sweep. A root is a *model candidate*, never a
fourth impulse, physical material contact or complete polygon collision proof.
"""
from __future__ import annotations

from copy import deepcopy
from math import sin,cos,hypot
import unittest

from systems.workspace.world_ab_rotating_edge_face_endpoint import (
    attempt,run,inward_endpoint_edge_roots,SCHEMA,DURATION,START,ANGLES,KINDS
)
from systems.workspace.world_ab_third_contact import attempt as source21
from systems.workspace.world_ab_first_post_third_candidate import attempt as source22
from network.tests.test_world_ab_first_post_third_candidate import independent_check as check22
from systems.workspace.world_ab_local_recontact_impulse import attempt as source18
from systems.workspace.world_ab_oblique_impact import HALF,WALL_CENTER

POLY=(( -HALF,-HALF),(HALF,-HALF),(HALF,HALF),(-HALF,HALF))
WORLD=(24.,6.)
EPS=3e-5


def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]


def cross(a,b):
    return a[0]*b[1]-a[1]*b[0]


def position(h,vertex,t):
    theta=h["contact_orientation"]+h["outgoing_spin"]*t
    c,s=cos(theta),sin(theta)
    x,y=vertex
    return (h["contact_center"][0]+h["outgoing_velocity"][0]*t+c*x-s*y,
            h["contact_center"][1]+h["outgoing_velocity"][1]*t+s*x+c*y)


def independent_gap_and_fraction(h,endpoint,edge,t):
    a=position(h,POLY[edge],t)
    b=position(h,POLY[(edge+1)%4],t)
    v=(b[0]-a[0],b[1]-a[1])
    w=(endpoint[0]-a[0],endpoint[1]-a[1])
    d=hypot(*v)
    return cross(v,w)/d,dot(v,w)/(d*d)


def independent_roots(h,p,edge):
    left=START
    former=independent_gap_and_fraction(h,p,edge,left)[0]
    roots=[]
    for j in range(1,8193):
        right=START+(DURATION-START)*j/8192
        current=independent_gap_and_fraction(h,p,edge,right)[0]
        if former<-1e-9 and current>1e-9:
            a,b=left,right
            for _ in range(53):
                m=(a+b)/2
                if independent_gap_and_fraction(h,p,edge,m)[0]<0:
                    a=m
                else:
                    b=m
            t=(a+b)/2
            if not roots or abs(t-roots[-1])>1e-8:
                roots.append(t)
        left,former=right,current
    return roots


def definitions(prior,angle):
    first=source18(angle)["source_first_contact"]
    receiver=prior["source_receiver"]
    result=[]
    for label,normal,anchor in (
        ("original_finite_face",first["normal"],WALL_CENTER),
        ("motion_derived_receiver",receiver["normal"],receiver["anchor"])
    ):
        tangent=(-normal[1],normal[0])
        for end,sgn in enumerate((-1.,1.)):
            result.append((label,end,(
                anchor[0]+sgn*.5*tangent[0],
                anchor[1]+sgn*.5*tangent[1])))
    return result


def verify(case):
    angle=case.get("angle")
    if case.get("schema")!=SCHEMA or angle not in ANGLES:
        raise ValueError("original trial identity changed")
    ancestor=source21(angle)
    preceding=source22(angle)
    check22(preceding)
    required={
        "source_trial22_schema":preceding["schema"],
        "source_trial22_status":preceding["status"],
        "source_trial22_first_crossing":preceding["first_crossing"],
        "source_third_impulse":ancestor["third_impulse"],
        "source_receiver":ancestor["source_receiver"],
        "observation_start":START,
        "observation_end":DURATION,
        "square_edges_examined":4,
        "source_finite_faces_examined":2,
        "source_face_endpoints_per_face":2,
        "original_source_and_world_unchanged":True,
        "conditional_ballistic_model_only":True,
        "physical_contact_witnessed":False,
        "fourth_impulse_calculated":False,
        "new_receiver_constructed":False,
        "formal_root_completeness_certificate":False,
    }
    if any(case.get(k)!=v for k,v in required.items()):
        raise ValueError("original source or physical-claim scope changed")
    if ancestor["third_impulse"] is None:
        if (case["status"]!="NO_ADMITTED_THIRD_IMPULSE"
            or case["endpoint_edge_roots"]!=[]
            or case["eligible_edge_candidates"]!=[]
            or case["first_eligible_edge"] is not None
            or case["conditional_model_pairs_checked"]!=0):
            raise ValueError("no-source-impulse control fabricated endpoint response")
        return True
    h=ancestor["third_impulse"]
    numerical=[]
    for name,point_index,p in definitions(ancestor,angle):
        for e in range(4):
            roots=independent_roots(h,p,e)
            for t in roots:
                _,u=independent_gap_and_fraction(h,p,e,t)
                kind=(KINDS[2] if u<-3e-7 or u>1+3e-7 else
                      KINDS[1] if u<=3e-7 or u>=1-3e-7 else KINDS[0])
                numerical.append((t,name,point_index,e,u,kind))
    numerical.sort(key=lambda v:(v[0],v[1],v[2],v[3]))
    source=case["endpoint_edge_roots"]
    if len(source)!=len(numerical):
        raise ValueError("source omitted or added endpoint-edge crossing")
    for item,e in zip(source,numerical):
        t,name,point_index,edge,frac,kind=e
        if (item["face"]!=name
            or item["face_endpoint_index"]!=point_index
            or item["square_edge_index"]!=edge
            or abs(item["dt_after_third_impulse"]-t)>EPS
            or abs(item["absolute_virtual_time"]-(t+h["contact_absolute_virtual_time"]))>EPS
            or abs(item["edge_fraction"]-frac)>EPS
            or abs(item["edge_signed_gap_residual"])>EPS
            or item["feature_classification"]!=kind
            or item["material_contact_witnessed"] is not False
            or item["conditionally_modeled"] is not True):
            raise ValueError("independent moving edge and fixed endpoint disagree")
    eligible=[x for x in source if x["feature_classification"]==KINDS[0]]
    extension=[x for x in source if x["feature_classification"]==KINDS[2]]
    endpoints=[x for x in source if x["feature_classification"]==KINDS[1]]
    if (case.get("eligible_edge_candidates")!=eligible
        or case.get("edge_extension_roots")!=extension
        or case.get("vertex_endpoint_uncertainties")!=endpoints):
        raise ValueError("finite-edge membership altered")
    first=eligible[0] if eligible else None
    tied=[x for x in eligible if
          abs(x["dt_after_third_impulse"]-first["dt_after_third_impulse"])<=1e-7
          ] if first else []
    if case.get("first_eligible_edge")!=first or case.get("coearliest_edge_candidates")!=tied:
        raise ValueError("first modeled endpoint-edge candidate substituted")
    earlier=[x for x in preceding["all_source_line_crossings"]
             if x["feature_classification"] in (
                 "FINITE_FACE_INTERIOR_CANDIDATE","WORLD_PERIMETER_CANDIDATE")]
    original_first=earlier[0] if earlier else None
    if case.get("first_geometric_source_candidate")!=original_first:
        raise ValueError("Trial22 vertex event hidden")
    expected=("NO_ELIGIBLE_ENDPOINT_EDGE_ROOT_IN_BOUNDED_SAMPLES" if first is None else
              "COEARLIEST_ENDPOINT_EDGE_FEATURES_UNRESOLVED" if len(tied)>1 else
              "ENDPOINT_EDGE_CANDIDATE_BEFORE_VERTEX_LINE_CANDIDATE" if
              original_first is None or first["dt_after_third_impulse"]+1e-7 <
              original_first["dt_after_third_impulse"] else
              "ENDPOINT_EDGE_CANDIDATE_NOT_EARLIER_THAN_VERTEX_LINE")
    if case.get("status")!=expected or case.get("conditional_model_pairs_checked")!=16:
        raise ValueError("source comparison or all-pair coverage changed")
    for item in case.get("near_zero_sample_watches",[]):
        if item["face"] not in ("original_finite_face","motion_derived_receiver"):
            raise ValueError("unsupported near-zero face")
        if item["face_endpoint_index"] not in (0,1) or item["square_edge_index"] not in range(4):
            raise ValueError("bad watched corner or edge")
        t=item["sample_time"]
        if not START <= t <= DURATION:
            raise ValueError("near-zero event outside original source window")
        p=next(pt for name,i,pt in definitions(ancestor,angle)
               if name==item["face"] and i==item["face_endpoint_index"])
        if abs(independent_gap_and_fraction(h,p,item["square_edge_index"],t)[0])>5e-6:
            raise ValueError("fabricated near-zero numerical watch")
    return True


class World24Tests(unittest.TestCase):
    def test_direct_translation_reaches_face_endpoint_mid_square_edge(self):
        h={"contact_center":[0.,0.],"contact_orientation":0.,
           "outgoing_velocity":[1.,0.],"outgoing_spin":0.}
        point=(.4,0.)
        r,watch=inward_endpoint_edge_roots(h,point,1)
        self.assertEqual(len(r),1)
        self.assertAlmostEqual(r[0],.15,places=6)
        a,b=independent_gap_and_fraction(h,point,1,r[0])
        self.assertAlmostEqual(a,0.,places=7)
        self.assertAlmostEqual(b,.5,places=7)

    def test_all_source_cases_reconstructed_by_distinct_numerical_grid(self):
        result=run()
        self.assertEqual(result["schema"],SCHEMA)
        self.assertEqual(result["conditional_source_inputs"],6)
        self.assertEqual(result["without_source_impulse"],2)
        self.assertEqual(result["source_edge_pairs_checked"],96)
        self.assertEqual(result["cases_with_eligible_endpoint_edge"]+
                         result["cases_without_eligible_endpoint_edge"],6)
        self.assertEqual(result["physical_measurements"],0)
        self.assertEqual(result["fourth_impulses_selected"],0)
        self.assertEqual(result["new_receivers_built"],0)
        for case in result["cases"]:
            with self.subTest(angle=case["angle"]):
                self.assertTrue(verify(case))

    def test_absent_impulse_never_gains_endpoint_interaction(self):
        for angle in (0.,20.):
            c=attempt(angle)
            self.assertEqual(c["status"],"NO_ADMITTED_THIRD_IMPULSE")
            self.assertEqual(c["endpoint_edge_roots"],[])

    def test_false_material_and_early_contact_promotions_refused(self):
        case=attempt(7.5)
        for key,value in (
            ("fourth_impulse_calculated",True),
            ("physical_contact_witnessed",True),
            ("observation_end",3.),
            ("new_receiver_constructed",True),
            ("conditional_ballistic_model_only",False),
        ):
            altered=deepcopy(case)
            altered[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                verify(altered)
        if case["endpoint_edge_roots"]:
            altered=deepcopy(case)
            altered["endpoint_edge_roots"][0]["edge_fraction"]=99.
            with self.assertRaises(ValueError):verify(altered)
        altered=deepcopy(case)
        altered["source_trial22_status"]="FOURTH_IMPULSE_SOLVED"
        with self.assertRaises(ValueError):verify(altered)


if __name__=="__main__":
    unittest.main()
