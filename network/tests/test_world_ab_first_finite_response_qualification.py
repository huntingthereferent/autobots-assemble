"""Independent WORLD29 source geometry and conditional elastic-response witness.

The original generator applies its inherited Trial18/21 impulse formula after
checking WORLD28 first-onset and WORLD23 source corner identity. This verifier
rederives world-space corner kinematics and the impulse from an independent
effective-mass / restitution relation, and refuses any selected physical event.
"""
from __future__ import annotations

from copy import deepcopy
from math import cos,sin,hypot
import unittest

from systems.workspace.world_ab_first_finite_response_qualification import (
    attempt,run,ideal_response,SCHEMA,MASS,INERTIA,EPS
)
from systems.workspace.world_ab_local_finite_onset import attempt as prior28
from systems.workspace.world_ab_all_inward_finite_features import attempt as prior23
from systems.workspace.world_ab_third_contact import attempt as prior21
from systems.workspace.world_ab_first_post_third_candidate import ANGLES,surfaces
from systems.workspace.world_ab_oblique_impact import HALF

LOCAL=((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))
LIMIT=5e-7


def project(a,b):
    return a[0]*b[0]+a[1]*b[1]


def reconstructed_corner(h,t,index):
    theta=h["contact_orientation"]+t*h["outgoing_spin"]
    co,si=cos(theta),sin(theta)
    x,y=LOCAL[index]
    r=(x*co-y*si,x*si+y*co)
    c=(h["contact_center"][0]+t*h["outgoing_velocity"][0],
       h["contact_center"][1]+t*h["outgoing_velocity"][1])
    return c,r,(c[0]+r[0],c[1]+r[1]),theta


def verify(case):
    a=case.get("angle")
    if case.get("schema")!=SCHEMA or a not in ANGLES:
        raise ValueError("source identity or angle changed")
    p28=prior28(a);p23=prior23(a);p21=prior21(a)
    expected={
        "source_trial28_schema":p28["schema"],
        "source_trial28_status":p28["status"],
        "source_trial23_schema":p23["schema"],
        "source_trial23_first_eligible":p23["first_eligible_geometry"],
        "source_original_third_response":p21["third_impulse"],
        "original_world_dimensions":[24.,6.],
        "original_mass":MASS,"original_inertia":INERTIA,
        "source_conditional_free_flight_only":True,
        "assumed_law":"single frictionless normal, restitution 1, unit-mass rotating square",
        "physical_fourth_impact_witnessed":False,
        "physical_response_selected":False,
        "post_response_trajectory_solved":False,
        "another_receiver_constructed":False,
        "exact_root_or_material_certification":False,
    }
    if any(case.get(k)!=v for k,v in expected.items()):
        raise ValueError("original source ancestry or physical claim changed")
    src=p28["first_eligible_finite_onset"]
    if p21["third_impulse"] is None:
        if (case["status"]!="NO_ADMITTED_THIRD_IMPULSE" or
            case["qualifying_source_feature"] is not None or
            case["conditional_fourth_response"] is not None):
            raise ValueError("nonexistent source third impulse created fourth model feature")
        return True
    if src is None:
        if (case["status"]!="NO_ORIGINAL_FIRST_FINITE_ONSET" or
            case["qualifying_source_feature"] is not None or
            case["conditional_fourth_response"] is not None):
            raise ValueError("no source finite overlap became an impulse")
        return True
    if case["status"]!="CONDITIONAL_SINGLE_VERTEX_NORMAL_RESPONSE_CANDIDATE":
        if (case["status"] not in (
              "UNRESOLVED_OR_COMPETING_FINITE_CONTACT",
              "UNRESOLVED_FIRST_ONSET_ANCESTRY")
            or case["qualifying_source_feature"] is not None
            or case["conditional_fourth_response"] is not None
            or not case["source_contact_rejection"]):
            raise ValueError("unresolved contact promoted")
        return True
    f=case["qualifying_source_feature"]
    response=case["conditional_fourth_response"]
    if not isinstance(f,dict) or not isinstance(response,dict):
        raise ValueError("qualified response lacks original source movement")
    t=f["dt_after_original_third_impulse"]
    idx=f["source_vertex_index"]
    name=f["source_face"]
    native=p21["third_impulse"]
    if not (isinstance(idx,int) and 0<=idx<4):
        raise ValueError("invalid original contact vertex")
    face=[(tuple(n),anchor,span) for label,n,anchor,span in surfaces(p21,a)
          if label==name and span is not None]
    if len(face)!=1:
        raise ValueError("source finite contact face missing")
    n,anchor,span=face[0]
    center,r,point,theta=reconstructed_corner(native,t,idx)
    tangent=(-n[1],n[0])
    d=(point[0]-anchor[0],point[1]-anchor[1])
    v=tuple(native["outgoing_velocity"])
    spin=native["outgoing_spin"]
    contact_velocity=(v[0]-spin*r[1],v[1]+spin*r[0])
    incoming=project(contact_velocity,n)
    along=project(d,tangent)
    root=[c for c in p23["eligible_geometry_roots"] if
          c["surface"]==name and c["vertex_index"]==idx and
          abs(c["dt_after_third_impulse"]-t)<LIMIT]
    if (len(root)!=1 or f["source_vertex_witness"]!=root[0]
        or abs(t-src["refined_sat_bracket"]["first_nominally_intersecting_time"])>LIMIT
        or abs(project(d,n))>LIMIT
        or not -span/2+LIMIT<along<span/2-LIMIT
        or incoming>=-LIMIT
        or abs(project(d,n))>LIMIT):
        raise ValueError("source contact geometry inconsistent")
    for k,vec in [
        ("contact_point",point),("contact_center",center),
        ("contact_normal",n),("contact_lever",r)
    ]:
        if any(abs(x-y)>LIMIT for x,y in zip(f[k],vec)):
            raise ValueError("original contact location or lever changed: "+k)
    if (abs(f["contact_angle"]-theta)>LIMIT or
        abs(f["absolute_virtual_time"]-
            (native["contact_absolute_virtual_time"]+t))>LIMIT
        or abs(f["finite_face_tangent_coordinate"]-along)>LIMIT
        or f["independent_finite_geometry_not_material_contact"] is not True):
        raise ValueError("source chronology/contact feature altered")
    if (response.get("source_face")!=name or
        response.get("source_vertex_index")!=idx or
        response.get("materially_witnessed") is not False or
        response.get("response_selected_as_actual") is not False or
        response.get("further_contacts_resolved") is not False):
        raise ValueError("modeled mathematical impulse became a physical result")
    # Distinct algebra: solve the point-contact normal velocity inversion
    # using the inverse effective normal mass, then reconstruct momentum.
    lever=r[0]*n[1]-r[1]*n[0]
    delta=-2*incoming
    effective_inverse=1/MASS+lever*lever/INERTIA
    j=delta/effective_inverse
    outgoing=(v[0]+n[0]*j/MASS,v[1]+n[1]*j/MASS)
    new_w=spin+j*lever/INERTIA
    rate=project((outgoing[0]-new_w*r[1],
                  outgoing[1]+new_w*r[0]),n)
    eb=(MASS*project(v,v)+INERTIA*spin*spin)/2
    ea=(MASS*project(outgoing,outgoing)+INERTIA*new_w*new_w)/2
    controls={
        "normal_impulse":j,"incoming_contact_normal_rate":incoming,
        "outgoing_contact_normal_rate":rate,"incoming_spin":spin,
        "outgoing_spin":new_w,"lever_cross_normal":lever,
        "kinetic_energy_before":eb,"kinetic_energy_after":ea,
    }
    for key,want in controls.items():
        if abs(response[key]-want)>LIMIT:
            raise ValueError("independent elastic response fails: "+key)
    for key,want in [("incoming_velocity",v),("outgoing_velocity",outgoing)]:
        if any(abs(x-y)>LIMIT for x,y in zip(response[key],want)):
            raise ValueError("independent velocity differs: "+key)
    if (abs(rate+incoming)>LIMIT or abs(ea-eb)>LIMIT or j<=0):
        raise ValueError("conditional restitution or kinetic energy invalid")
    return True


class World29Tests(unittest.TestCase):
    def test_original_single_normal_impulse_known_analytic_case(self):
        v=(1.,0.);w=0.;r=(.25,.0);n=(-1.,0.)
        sample=ideal_response(v,w,r,n)
        self.assertAlmostEqual(sample["normal_impulse"],2.,places=7)
        self.assertAlmostEqual(sample["outgoing_velocity"][0],-1.,places=7)
        self.assertAlmostEqual(sample["outgoing_spin"],0.,places=7)
        self.assertAlmostEqual(sample["kinetic_energy_before"],
                               sample["kinetic_energy_after"],places=7)

    def test_eight_original_cases_qualification_before_response(self):
        r=run()
        self.assertEqual(r["schema"],SCHEMA)
        self.assertEqual(r["original_finite_first_onset_cases"],3)
        self.assertEqual(r["absent_source_impulse_controls"],2)
        self.assertEqual(r["material_impacts_witnessed"],0)
        self.assertEqual(r["actual_fourth_impulses_selected"],0)
        self.assertEqual(r["receivers_constructed"],0)
        self.assertEqual(r["post_response_trajectories_solved"],0)
        self.assertLessEqual(r["conditionally_qualifying_responses"],3)
        for case in r["cases"]:
            with self.subTest(angle=case["angle"]):
                self.assertTrue(verify(case))

    def test_absent_original_third_impulse_does_not_create_response(self):
        for angle in (0.,20.):
            case=attempt(angle)
            self.assertEqual(case["status"],"NO_ADMITTED_THIRD_IMPULSE")
            self.assertIsNone(case["conditional_fourth_response"])

    def test_material_promotion_and_forged_energy_are_refused(self):
        row=attempt(10.)
        for key,value in (
            ("physical_fourth_impact_witnessed",True),
            ("physical_response_selected",True),
            ("post_response_trajectory_solved",True),
            ("exact_root_or_material_certification",True),
            ("original_world_dimensions",[50.,50.]),
        ):
            wrong=deepcopy(row)
            wrong[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                verify(wrong)
        r=run()
        accepted=next((case for case in r["cases"]
                       if case["conditional_fourth_response"] is not None),None)
        if accepted:
            tampered=deepcopy(accepted)
            tampered["conditional_fourth_response"]["kinetic_energy_after"]+=.1
            with self.assertRaises(ValueError):verify(tampered)
            tampered=deepcopy(accepted)
            tampered["conditional_fourth_response"]["response_selected_as_actual"]=True
            with self.assertRaises(ValueError):verify(tampered)


if __name__=="__main__":
    unittest.main()
