"""WORLD19 independent whole-interval rotating-square clearance witness.

Does NOT use the generator's Taylor certificate, rotated-coordinate routines
or accepted flag for the result. Independently find all stationary times of
each corner's signed line-distance function; evaluate every extremum. A
positive gap of all vertices separates the convex square from the WHOLE
supporting line, hence from the original FINITE line segment.

This is a bounded nominal-real-number mathematical result, not formal
outward-rounded interval arithmetic or actual material evidence.
"""
from __future__ import annotations

from copy import deepcopy
from math import acos, atan2, cos, hypot, isfinite, pi, sin
import unittest

from systems.workspace.world_ab_continuous_separation import (
    evaluate,run,SCHEMA,EPS,MIN_CERTIFIED_MARGIN,RADIUS
)
from systems.workspace.world_ab_local_recontact_impulse import (
    attempt as old_attempt,POST_HORIZON,ANGLES
)
from network.tests.test_world_ab_local_recontact_impulse import verify as verify_trial18
from systems.workspace.world_ab_oblique_impact import HALF,WALL_CENTER

CORNERS=((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))
TOL=4e-7


def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]


def independent_extrema(normal,velocity,omega,center,theta,point,window):
    # Different expression from generator: signed gap as linear translation
    # plus A*cos(omega*t) + B*sin(omega*t).
    x,y=point
    r=(x*cos(theta)-y*sin(theta),x*sin(theta)+y*cos(theta))
    origin=(center[0]-WALL_CENTER[0],center[1]-WALL_CENTER[1])
    c=dot(origin,normal)
    vn=dot(velocity,normal)
    A=dot(r,normal)
    B=dot((-r[1],r[0]),normal)

    def f(t):
        return c+vn*t+A*cos(omega*t)+B*sin(omega*t)

    def fprime(t):
        return vn+omega*(-A*sin(omega*t)+B*cos(omega*t))

    stationary=[0.,window]
    amplitude=hypot(A,B)
    if abs(omega)>1e-12 and amplitude>1e-12:
        ratio=-vn/(omega*amplitude)
        if abs(ratio)<=1.:
            phi=atan2(A,B)
            root=acos(max(-1.,min(1.,ratio)))
            for k in range(-4,5):
                for sign in (-1,1):
                    t=(sign*root-phi+2*pi*k)/omega
                    if 1e-12<t<window-1e-12:
                        stationary.append(t)
    return {
        "gap0":f(0.),
        "derivative0":fprime(0.),
        "stationary_times":sorted(set(stationary)),
        "stationary_gaps":[f(t) for t in sorted(set(stationary))],
        "rotated_corner":r,
    }


def independent_check(result):
    if result["schema"]!=SCHEMA or result["original_source_angle"] not in ANGLES:
        raise ValueError("wrong WORLD18 source or angle")
    if result["window"]!=POST_HORIZON or result["half_extent"]!=HALF or result["finite_face_origin"]!=list(WALL_CENTER):
        raise ValueError("changed source geometry or proof interval")
    for flag in ("conditional_second_impulse_only","actual_hardware_behavior_witnessed",
                 "further_contact_response_solved","derived_receiver_constructed",
                 "formal_floating_point_interval_certificate"):
        expected=flag=="conditional_second_impulse_only"
        if result[flag] is not expected:
            raise ValueError("a mathematical model was misrepresented: "+flag)
    source=old_attempt(result["original_source_angle"])
    verify_trial18(source)
    if result["source_trial18_schema"]!=source["schema"] or result["source_trial18_status"]!=source["status"]:
        raise ValueError("original WORLD18 lineage changed")
    if result["source_candidate_impulse"]!=source["candidate_impulse"]:
        raise ValueError("original candidate source was rewritten")
    impulse=source["candidate_impulse"]
    if impulse is None:
        if result["status"]!="NO_ADMITTED_SECOND_IMPULSE" or result["per_vertex_bounds"] or result["worst_positive_margin"] is not None:
            raise ValueError("invented continuous proof without renewed contact")
        if result["all_corner_halfspace_clearance_supported"] is not False:
            raise ValueError("unsupported continuous claim")
        return True
    if result["bounding_method"]!="four rotated-corner Taylor lower bounds; whole interval":
        raise ValueError("certificate method substituted")
    if (result["nominal_real_arithmetic_only"] is not True
        or result["postcontact_motion_assumed_ballistic"] is not True
        or result["no_additional_contacts_or_forces_in_assumed_window"] is not True):
        raise ValueError("nominal kinematic conditions omitted")
    normal=tuple(impulse["source_face_normal"])
    speed=tuple(impulse["velocity_after"])
    omega=impulse["angular_velocity_after"]
    theta=impulse["contact_angle"]
    center=tuple(impulse["contact_center"])
    contact=source["source_trial17_first_return"]["corner_index"]
    if len(result["per_vertex_bounds"])!=4:
        raise ValueError("not all original square corners checked")

    minimum_reported=[]
    for i,(point,record) in enumerate(zip(CORNERS,result["per_vertex_bounds"])):
        if record["corner_index"]!=i:
            raise ValueError("corner identity changed")
        values=independent_extrema(normal,speed,omega,center,theta,point,POST_HORIZON)
        f0=values["gap0"]
        df0=values["derivative0"]
        # Separately compute the universal curvature bound and Taylor end
        # value to authenticate the generator's claimed certificate.
        k=omega*omega*hypot(*point)
        end=f0+df0*POST_HORIZON-.5*k*POST_HORIZON**2
        velocity_lower=df0-k*POST_HORIZON
        margin=(velocity_lower if i==contact else min(f0,end))
        expected_kind=("touching-corner-derivative-positive-entire-window"
                       if i==contact else "noncontact-corner-quadratic-lower-bound-positive")
        expected=(abs(f0)<=EPS and velocity_lower>MIN_CERTIFIED_MARGIN
                  if i==contact else margin>MIN_CERTIFIED_MARGIN)

        for key,witness in (
            ("source_signed_gap_at_contact",f0),
            ("outgoing_signed_gap_derivative",df0),
            ("absolute_second_derivative_bound",k),
            ("quadratic_lower_bound_at_window_end",end),
            ("derivative_lower_bound_at_window_end",velocity_lower),
            ("conservative_margin",margin),
        ):
            if abs(record[key]-witness)>TOL:
                raise ValueError("forged or inaccurately rounded bound: "+key)
        if record["admission_condition"]!=expected_kind or record["accepted"]!=expected:
            raise ValueError("wrong source corner admission condition")
        if not expected:
            raise ValueError("trial does not pass declared bound")
        # Crucial INDEPENDENT proof: evaluate ALL extrema rather than rely on
        # the generator's Taylor polynomial.
        extrema=values["stationary_gaps"]
        if i==contact:
            if abs(extrema[0])>EPS or values["derivative0"]<=0:
                raise ValueError("touching source corner is not separating")
            if any(z<=1e-5 for z in extrema[1:]):
                raise ValueError("touching corner returned to original line")
        elif min(extrema)<=1e-5:
            raise ValueError("another corner enters source supporting line")
        minimum_reported.append(margin)

    if result["status"]!="CONDITIONAL_CONTINUOUS_HALFSPACE_SEPARATION":
        raise ValueError("mathematical continuous clearance status omitted")
    if (result["all_corner_halfspace_clearance_supported"] is not True
        or result["line_clearance_implies_finite_face_clearance"] is not True
        or abs(result["worst_positive_margin"]-min(minimum_reported))>TOL):
        raise ValueError("clearance was not justified for every corner")
    return True


class World19Tests(unittest.TestCase):
    def test_all_8_original_source_controls_independently_verified(self):
        out=run()
        self.assertEqual(out["schema"],SCHEMA)
        self.assertEqual(out["angles"],list(ANGLES))
        self.assertEqual(len(out["cases"]),8)
        self.assertEqual(out["conditional_continuous_clearance_count"],6)
        self.assertEqual(out["no_second_impulse_count"],2)
        self.assertEqual(out["inconclusive_count"],0)
        self.assertFalse(out["physics_engine_created"])
        self.assertFalse(out["all_earth_physics_verified"])
        self.assertFalse(out["new_receiver_created"])
        for case in out["cases"]:
            with self.subTest(angle=case["original_source_angle"]):
                self.assertTrue(independent_check(case))

    def test_six_candidates_have_whole_interval_separation_not_just_samples(self):
        for a in ANGLES[1:-1]:
            with self.subTest(angle=a):
                case=evaluate(a)
                self.assertEqual(case["status"],"CONDITIONAL_CONTINUOUS_HALFSPACE_SEPARATION")
                self.assertGreater(case["worst_positive_margin"],MIN_CERTIFIED_MARGIN)
                self.assertTrue(case["line_clearance_implies_finite_face_clearance"])
                self.assertTrue(independent_check(case))

    def test_two_no_return_controls_do_not_gain_proof_or_ghost_impulses(self):
        for a in (0.,20.):
            out=evaluate(a)
            self.assertEqual(out["status"],"NO_ADMITTED_SECOND_IMPULSE")
            self.assertIsNone(out["source_candidate_impulse"])
            self.assertFalse(out["all_corner_halfspace_clearance_supported"])
            self.assertTrue(independent_check(out))

    def test_forged_corner_or_margin_rejected(self):
        for field in ("source_signed_gap_at_contact",
                      "outgoing_signed_gap_derivative",
                      "absolute_second_derivative_bound",
                      "quadratic_lower_bound_at_window_end",
                      "derivative_lower_bound_at_window_end",
                      "conservative_margin"):
            wrong=deepcopy(evaluate(15.))
            wrong["per_vertex_bounds"][2][field]+=.2
            with self.subTest(field=field),self.assertRaises(ValueError):
                independent_check(wrong)
        for field in ("corner_index","accepted","admission_condition"):
            wrong=deepcopy(evaluate(10.))
            wrong["per_vertex_bounds"][2][field]=(
                3 if field=="corner_index" else
                False if field=="accepted" else
                "noncontact-corner-quadratic-lower-bound-positive")
            with self.subTest(field=field),self.assertRaises(ValueError):
                independent_check(wrong)

    def test_false_math_certification_hardware_or_longer_window_refused(self):
        for field,value in (
            ("actual_hardware_behavior_witnessed",True),
            ("formal_floating_point_interval_certificate",True),
            ("derived_receiver_constructed",True),
            ("further_contact_response_solved",True),
            ("window",.03),
            ("all_corner_halfspace_clearance_supported",False),
            ("line_clearance_implies_finite_face_clearance",False),
        ):
            wrong=deepcopy(evaluate(10.))
            wrong[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):
                independent_check(wrong)

    def test_original_impulse_or_orientation_cannot_be_replaced(self):
        for field in ("angular_velocity_after","normal_impulse","contact_center"):
            wrong=deepcopy(evaluate(10.))
            if field=="contact_center":
                wrong["source_candidate_impulse"][field][0]+=.5
            else:
                wrong["source_candidate_impulse"][field]+=.5
            with self.subTest(field=field),self.assertRaises(ValueError):
                independent_check(wrong)


if __name__=="__main__":
    unittest.main()
