"""WORLD18 independent virtual second-impulse comparison and negative evidence.

The source computes a *candidate* normal impact, not material truth. This
oracle independently rotates the square, reconstructs the original contact
feature, computes the impulse, and replays short local face-clearance samples.
No generator impact or vertex helpers are called.
"""
from __future__ import annotations

from copy import deepcopy
from math import cos, sin, radians, hypot
import unittest

from network.tests.test_world_ab_square_first_recontact import independent_check as verify_trial17
from network.tests.test_world_ab_oblique_impact import verify_impact
from systems.workspace.world_ab_square_first_recontact import trial as original_return
from systems.workspace.world_ab_local_recontact_impulse import (
    attempt,run,SCHEMA,ANGLES,POST_HORIZON,STEP,
)
from systems.workspace.world_ab_oblique_impact import INERTIA, HALF, WALL_CENTER, SPAN

POINTS=((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))
TOL=3e-7


def dot(a,b):
    return sum(x*y for x,y in zip(a,b))


def det(a,b):
    return a[0]*b[1]-a[1]*b[0]


def near(a,b,epsilon=TOL):
    if isinstance(a,(tuple,list)):
        return isinstance(b,(tuple,list)) and len(a)==len(b) and all(
            near(x,y,epsilon) for x,y in zip(a,b))
    return abs(a-b)<epsilon


def coordinate(center,rot,point):
    x,y=point
    return (center[0]+x*cos(rot)-y*sin(rot),
            center[1]+x*sin(rot)+y*cos(rot))


def independent_sample(center,theta,normal):
    tangent=(-normal[1],normal[0])
    measured=[]
    for k,point in enumerate(POINTS):
        vertex=coordinate(center,theta,point)
        relative=(vertex[0]-WALL_CENTER[0],vertex[1]-WALL_CENTER[1])
        along=dot(relative,tangent)
        if abs(along)<=SPAN/2+1e-8:
            measured.append((dot(relative,normal),k,along))
    return min(measured) if measured else None


def verify(candidate):
    if candidate["schema"]!=SCHEMA or candidate["angle"] not in ANGLES:
        raise ValueError("source or angle changed")
    if candidate["local_time_horizon"]!=POST_HORIZON or candidate["observation_step"]!=STEP:
        raise ValueError("local observation window changed")
    if candidate["physical_second_impact_observed"] is not False:
        raise ValueError("invented measured physical result")
    if candidate["second_impulse_is_a_model_hypothesis"] is not True:
        raise ValueError("unwitnessed material law promoted")
    if candidate["receiver_constructed"] is not False or candidate["continuous_clearance_certified"] is not False or candidate["further_impacts_solved"] is not False:
        raise ValueError("invented completed later construction")
    prior=original_return(candidate["angle"])
    verify_trial17(prior)
    source=candidate["source_first_contact"]
    verify_impact(source)
    if source!=prior["source_original_first_contact"]:
        raise ValueError("original first source impact changed")
    if candidate["source_trial17"]!=prior["schema"] or candidate["source_trial17_first_return"]!=prior["first_return"]:
        raise ValueError("original first renewed recontact changed")
    event=prior["first_return"]
    if event is None:
        if (candidate["status"]!="NO_ADMITTED_RENEWED_CONTACT" or
                candidate["candidate_impulse"] is not None or
                candidate["post_contact_samples"]):
            raise ValueError("response invented without a source recontact")
        return True
    if candidate["status"] not in (
        "LOCAL_OVERLAP_UNRESOLVED","NO_OVERLAP_DETECTED_IN_LOCAL_SAMPLES"):
        raise ValueError("an admitted source was silently rejected or promoted")
    impact=candidate["candidate_impulse"]
    if impact is None or impact["selected_as_actual_material_response"] is not False:
        raise ValueError("unobserved physical impulse selected")
    if impact["constitutive_hypothesis"]!="single frictionless normal, e=1, rotating rigid square":
        raise ValueError("contact law changed without new admission")

    time=event["dt_after_initial_contact"]
    idx=event["corner_index"]
    normal=(-cos(radians(candidate["angle"])),-sin(radians(candidate["angle"])))
    vin=source["velocity_after"]
    incoming_spin=source["angular_velocity_after"]
    center=(
        source["first_contact_center"][0]+vin[0]*time,
        source["first_contact_center"][1]+vin[1]*time,
    )
    theta=time*incoming_spin
    point=coordinate(center,theta,POINTS[idx])
    lever=(point[0]-center[0],point[1]-center[1])
    tangent=(-normal[1],normal[0])
    along=dot((point[0]-WALL_CENTER[0],point[1]-WALL_CENTER[1]),tangent)
    gap=dot((point[0]-WALL_CENTER[0],point[1]-WALL_CENTER[1]),normal)
    if not -SPAN/2<along<SPAN/2 or abs(gap)>TOL:
        raise ValueError("first finite recontact is not on the source face")

    relative_velocity=(vin[0]-incoming_spin*lever[1],
                       vin[1]+incoming_spin*lever[0])
    rate=dot(relative_velocity,normal)
    if rate>=0:
        raise ValueError("candidate corner is not incoming")
    arm=det(lever,normal)
    # Separately derive momentum + angular-momentum response for e=1.
    j=-2*rate/(1+arm*arm/INERTIA)
    vout=(vin[0]+j*normal[0],vin[1]+j*normal[1])
    outspin=incoming_spin+j*arm/INERTIA
    out_corner=(vout[0]-outspin*lever[1],vout[1]+outspin*lever[0])
    eb=.5*dot(vin,vin)+.5*INERTIA*incoming_spin**2
    ea=.5*dot(vout,vout)+.5*INERTIA*outspin**2
    if abs(eb-ea)>TOL or abs(dot(out_corner,normal)+rate)>TOL:
        raise ValueError("frictionless candidate impulse violates independent conservation")

    pairs=(
        ("normal_impulse",j),
        ("incoming_vertex_normal_rate",rate),
        ("outgoing_vertex_normal_rate",dot(out_corner,normal)),
        ("lever_cross_normal",arm),
        ("angular_velocity_before",incoming_spin),
        ("angular_velocity_after",outspin),
        ("kinetic_energy_before",eb),
        ("kinetic_energy_after",ea),
        ("contact_time_relative",time),
        ("contact_angle",theta),
    )
    for name,actual in pairs:
        if not near(impact[name],actual):
            raise ValueError("changed contact impulse measurement: "+name)
    for name,actual in (
        ("velocity_before",vin),("velocity_after",vout),
        ("contact_point",point),("contact_center",center),
        ("source_face_normal",normal)):
        if not near(impact[name],actual):
            raise ValueError("changed contact vector: "+name)
    if impact["contact_vertex_index"]!=idx:
        raise ValueError("different contact feature chosen")

    samples=candidate["post_contact_samples"]
    if len(samples)!=round(POST_HORIZON/STEP)+1:
        raise ValueError("source local observation frames missing")
    first_overlap=None
    for index,record in enumerate(samples):
        dt=index*STEP
        p=(center[0]+dt*vout[0],center[1]+dt*vout[1])
        angle=theta+dt*outspin
        measured=independent_sample(p,angle,normal)
        if not near(record["dt_after_candidate"],dt) or not near(record["center"],p) or not near(record["orientation"],angle):
            raise ValueError("fabricated local motion sample")
        if measured is None:
            if (record["minimum_sampled_signed_face_gap"] is not None
                    or record["worst_finite_face_corner"] is not None
                    or record["worst_finite_face_tangent"] is not None):
                raise ValueError("unsampled finite wall value invented")
        else:
            clearance,k,along=measured
            if (record["worst_finite_face_corner"]!=k or
                    not near(record["worst_finite_face_tangent"],along) or
                    not near(record["minimum_sampled_signed_face_gap"],clearance)):
                raise ValueError("local rotating square clearance differs")
            if clearance < -1e-8 and first_overlap is None:
                first_overlap=round(dt,10)
    expected="LOCAL_OVERLAP_UNRESOLVED" if first_overlap is not None else "NO_OVERLAP_DETECTED_IN_LOCAL_SAMPLES"
    if candidate["status"]!=expected or candidate["first_sampled_post_contact_overlap"]!=first_overlap:
        raise ValueError("local continuation status was selected without source evidence")
    if candidate["next_movement_admitted_as_verified"] is not False:
        raise ValueError("sampled clearance substituted for continuous physics")
    return True


class World18Tests(unittest.TestCase):
    def test_all_eight_source_cases_independently_verified(self):
        data=run()
        self.assertEqual(data["schema"],SCHEMA)
        self.assertEqual(len(data["cases"]),8)
        self.assertEqual(data["cases_with_candidate_impulse"],6)
        self.assertEqual(data["cases_without_recontact"],2)
        self.assertFalse(data["material_contact_response_proven"])
        self.assertFalse(data["created_any_new_receiver"])
        self.assertFalse(data["general_rotating_contact_solver"])
        for r in data["cases"]:
            with self.subTest(angle=r["angle"]):
                self.assertTrue(verify(r))

    def test_six_second_impulse_hypotheses_preserve_energy(self):
        for a in ANGLES[1:-1]:
            with self.subTest(angle=a):
                r=attempt(a)
                p=r["candidate_impulse"]
                self.assertIsNotNone(p)
                self.assertGreater(p["normal_impulse"],0)
                self.assertLess(abs(p["kinetic_energy_before"]-p["kinetic_energy_after"]),TOL)
                self.assertAlmostEqual(p["incoming_vertex_normal_rate"],
                                       -p["outgoing_vertex_normal_rate"],delta=TOL)
                self.assertTrue(verify(r))

    def test_no_recontact_means_no_second_impulse(self):
        for a in (0.,20.):
            r=attempt(a)
            self.assertEqual(r["status"],"NO_ADMITTED_RENEWED_CONTACT")
            self.assertIsNone(r["candidate_impulse"])
            self.assertEqual(r["post_contact_samples"],[])
            self.assertTrue(verify(r))

    def test_all_forged_second_impulses_rejected(self):
        original=attempt(10.)
        keys=["normal_impulse","angular_velocity_after","incoming_vertex_normal_rate",
              "kinetic_energy_after","contact_time_relative","contact_vertex_index"]
        for field in keys:
            candidate=deepcopy(original)
            candidate["candidate_impulse"][field]+=.1 if field!="contact_vertex_index" else 1
            with self.subTest(field=field),self.assertRaises(ValueError):
                verify(candidate)
        for field in ("center","orientation","minimum_sampled_signed_face_gap","worst_finite_face_corner"):
            candidate=deepcopy(original)
            if field=="center":candidate["post_contact_samples"][5][field][0]+=.1
            elif field=="worst_finite_face_corner":candidate["post_contact_samples"][5][field]=99
            else:candidate["post_contact_samples"][5][field]+=.1
            with self.subTest(field=field),self.assertRaises(ValueError):
                verify(candidate)

    def test_cannot_claim_hardware_continuation_or_receiver(self):
        original=attempt(10.)
        for name,value in (
            ("physical_second_impact_observed",True),
            ("receiver_constructed",True),
            ("continuous_clearance_certified",True),
            ("further_impacts_solved",True),
            ("next_movement_admitted_as_verified",True),
        ):
            candidate=deepcopy(original);candidate[name]=value
            with self.subTest(name=name),self.assertRaises(ValueError):
                verify(candidate)

    def test_unsupported_original_angles_rejected(self):
        for a in (-1,21,True,"10",float("nan")):
            with self.subTest(angle=a),self.assertRaises(ValueError):
                attempt(a)


if __name__=="__main__":
    unittest.main()
