"""Independent WORLD21 third-contact witness and bound falsification.

Source20 construction is separately verified. The oracle recomputes incoming
rotated-vertex velocity and normal impulse without calling Trial21 helpers.
The post-contact geometry is checked by trigonometric stationary extrema,
not by relying on the generator's Taylor bound alone.
"""
from copy import deepcopy
from math import acos, atan2, cos, hypot, pi, sin
import unittest

from systems.workspace.world_ab_third_contact import attempt, run, SCHEMA, ANGLES, POST_WINDOW
from systems.workspace.world_ab_rotating_receiver import trial as source20, DURATION
from network.tests.test_world_ab_rotating_receiver import independent_check as verify20
from systems.workspace.world_ab_local_recontact_impulse import attempt as source18
from network.tests.test_world_ab_local_recontact_impulse import verify as verify18
from systems.workspace.world_ab_oblique_impact import HALF, INERTIA, WALL_CENTER

VERTICES=((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))
TOL=3e-7


def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]


def cross(a,b):
    return a[0]*b[1]-a[1]*b[0]


def near(a,b,tol=TOL):
    if isinstance(a,(list,tuple)):
        return isinstance(b,(list,tuple)) and len(a)==len(b) and all(near(x,y,tol) for x,y in zip(a,b))
    return abs(a-b)<tol


def rotated(v,theta):
    return (v[0]*cos(theta)-v[1]*sin(theta),
            v[0]*sin(theta)+v[1]*cos(theta))


def independent_extrema(center,theta,v,omega,normal,anchor,vertex):
    """Entire-time window stationary extrema of linear + harmonic gap."""
    r=rotated(vertex,theta)
    offset=(center[0]-anchor[0],center[1]-anchor[1])
    c=dot(offset,normal)
    linear=dot(v,normal)
    A=dot(r,normal)
    B=dot((-r[1],r[0]),normal)
    def value(t):
        return c+linear*t+A*cos(omega*t)+B*sin(omega*t)
    def derivative(t):
        return linear+omega*(-A*sin(omega*t)+B*cos(omega*t))
    times=[0.,POST_WINDOW]
    amplitude=hypot(A,B)
    if abs(omega)>1e-12 and amplitude>1e-12:
        q=-linear/(omega*amplitude)
        if abs(q)<=1:
            alpha=acos(max(-1.,min(1.,q)))
            phi=atan2(A,B)
            for k in range(-4,5):
                for s in (-1,1):
                    t=(s*alpha-phi+2*pi*k)/omega
                    if 1e-12<t<POST_WINDOW-1e-12:
                        times.append(t)
    times=sorted(set(times))
    return times,[value(t) for t in times],value(0.),derivative(0.)


def independent_check(record):
    if record["schema"]!=SCHEMA or record["angle"] not in ANGLES:
        raise ValueError("source type or angle")
    if record["relative_third_contact_time"]!=DURATION or record["local_window"]!=POST_WINDOW:
        raise ValueError("original bounded time scale changed")
    declarations={
        "third_impulse_model_hypothesis":True,
        "measured_material_response":False,
        "fourth_contact_selected":False,
        "another_receiver_constructed":False,
        "formal_interval_certificate":False,
        "first_second_contact_sources_unchanged":True,
    }
    if any(record[k] is not v for k,v in declarations.items()):
        raise ValueError("source/control or physical result misrepresented")
    old=source20(record["angle"])
    verify20(old)
    ancestor=source18(record["angle"])
    verify18(ancestor)
    if (record["source_trial20_schema"]!=old["schema"] or
        record["source_trial20_status"]!=old["status"] or
        record["source_receiver"]!=old["receiver"] or
        record["source_third_contact"]!=old["next_contact"]):
        raise ValueError("original derived receiver or geometry was modified")
    if old["status"]=="NO_SOURCE_SECOND_IMPULSE":
        if (record["status"]!="NO_QUALIFYING_THIRD_CONTACT" or
            record["third_impulse"] is not None or record["clearance_bounds"]):
            raise ValueError("impulse or object invented without source")
        return True
    if old["status"]!="CONDITIONAL_DERIVED_RECEIVER_REACHED":
        if record["third_impulse"] is not None:
            raise ValueError("third impact wrongly selected")
        return True
    original=ancestor["candidate_impulse"]
    receiver=old["receiver"]
    first=old["next_contact"]
    corner=first["vertex_index"]
    n=tuple(receiver["normal"])
    before=tuple(original["velocity_after"])
    spin=original["outgoing_spin"]
    center=(original["contact_center"][0]+DURATION*before[0],
            original["contact_center"][1]+DURATION*before[1])
    theta=original["contact_angle"]+DURATION*spin
    lever=rotated(VERTICES[corner],theta)
    point=(center[0]+lever[0],center[1]+lever[1])
    incoming_rate=dot((before[0]-spin*lever[1],
                       before[1]+spin*lever[0]),n)
    if not near(point,first["point"]) or not near(incoming_rate,first["incoming_normal_vertex_rate"]):
        raise ValueError("different original corner/time")
    if incoming_rate>=0:
        raise ValueError("not an incoming source corner")
    arm=cross(lever,n)
    # Independent linear/angular impulse with original unit mass.
    impulse=-2*incoming_rate/(1+arm*arm/INERTIA)
    after=(before[0]+impulse*n[0],
           before[1]+impulse*n[1])
    angular=spin+impulse*arm/INERTIA
    outgoing_rate=dot((after[0]-angular*lever[1],
                       after[1]+angular*lever[0]),n)
    energy0=.5*dot(before,before)+.5*INERTIA*spin*spin
    energy1=.5*dot(after,after)+.5*INERTIA*angular*angular
    if abs(energy0-energy1)>TOL or abs(outgoing_rate+incoming_rate)>TOL:
        raise ValueError("independent collision law inconsistent")

    h=record["third_impulse"]
    if h is None:
        raise ValueError("missing third impulse under incoming source")
    expected={
        "contact_vertex_index":corner,
        "receiver_id":receiver["id"],
        "contact_point":point,
        "contact_center":center,
        "contact_orientation":theta,
        "contact_absolute_virtual_time":first["absolute_virtual_time"],
        "source_receiver_normal":n,
        "incoming_velocity":before,
        "outgoing_velocity":after,
        "incoming_spin":spin,
        "outgoing_spin":angular,
        "incoming_contact_normal_rate":incoming_rate,
        "outgoing_contact_normal_rate":outgoing_rate,
        "normal_impulse":impulse,
        "lever_cross_normal":arm,
        "kinetic_energy_before":energy0,
        "kinetic_energy_after":energy1,
        "law":"original frictionless unit-mass rigid square, restitution 1",
        "materially_witnessed":False,
    }
    for field,val in expected.items():
        if isinstance(val,bool) or isinstance(val,str) or field in ("receiver_id","contact_vertex_index"):
            good=h[field]==val
        else:
            good=near(h[field],val)
        if not good:
            raise ValueError("third impulse falsified: "+field)

    boundaries=[
        ("receiver",n,tuple(receiver["anchor"]),corner),
        ("original_source",tuple(ancestor["source_first_contact"]["normal"]),WALL_CENTER,None),
        ("world_left",(1.,0.),(0.,0.),None),
        ("world_right",(-1.,0.),(24.,0.),None),
        ("world_bottom",(0.,1.),(0.,0.),None),
        ("world_top",(0.,-1.),(0.,6.),None),
    ]
    receipts=record["clearance_bounds"]
    if len(receipts)!=24:
        raise ValueError("incomplete four-corner/6-boundary verification")
    for line,(name,normal,anchor,touch) in enumerate(boundaries):
        for i,vertex in enumerate(VERTICES):
            z=receipts[4*line+i]
            if z["corner_index"]!=i or z["surface"]!=name or z["starts_touching"] is not (touch==i):
                raise ValueError("wrong original face/corner identity")
            times,values,f0,df0=independent_extrema(center,theta,after,angular,normal,anchor,vertex)
            curvature=angular*angular*hypot(*vertex)
            end_floor=f0+df0*POST_WINDOW-.5*curvature*POST_WINDOW**2
            der_floor=df0-curvature*POST_WINDOW
            margin=der_floor if touch==i else min(f0,end_floor)
            for field,value in (
                ("gap_at_third_contact",f0),
                ("outgoing_gap_rate",df0),
                ("curvature_upper_bound",curvature),
                ("end_gap_lower_bound",end_floor),
                ("rate_lower_bound",der_floor),
                ("conservative_margin",margin)):
                if not near(z[field],value):
                    raise ValueError("forged whole-interval bound: "+field)
            certified=(abs(f0)<=TOL and der_floor>1e-5 if touch==i
                       else margin>1e-5)
            if z["accepted"] is not certified:
                raise ValueError("incorrect local clearance admission")
            # Independent actual extrema check rather than the bound alone.
            if touch==i:
                if abs(values[0])>TOL or df0<=1e-5 or any(v<=1e-6 for v in values[1:]):
                    raise ValueError("touching corner re-enters source line")
            elif min(values)<=1e-6:
                raise ValueError("different corner crosses supporting line")

    if (record["status"]!="CONDITIONAL_LOCAL_SEPARATION" or
        record["local_separation_only"] is not True or
        record["source_finite_faces_unchanged"] is not True or
        record["hypothetical_outgoing_motion_only"] is not True):
        raise ValueError("unsupported physical or local continuation claim")
    return True


class WorldThirdContactTests(unittest.TestCase):
    def test_six_local_motions_and_two_unadmitted_controls(self):
        data=run()
        self.assertEqual(data["schema"],SCHEMA)
        self.assertEqual(len(data["cases"]),8)
        self.assertEqual(data["candidate_third_impulses"],6)
        self.assertEqual(data["local_conditional_separations"],6)
        self.assertEqual(data["cases_without_qualifying_third_contact"],2)
        self.assertFalse(data["real_material_behavior_verified"])
        self.assertFalse(data["another_receiver_created"])
        self.assertFalse(data["general_multicontact_solver_present"])
        for case in data["cases"]:
            with self.subTest(angle=case["angle"]):
                self.assertTrue(independent_check(case))

    def test_six_hypothetical_impulses_conserve_energy(self):
        for angle in ANGLES[1:-1]:
            c=attempt(angle)
            h=c["third_impulse"]
            self.assertEqual(c["status"],"CONDITIONAL_LOCAL_SEPARATION")
            self.assertGreater(h["normal_impulse"],0)
            self.assertAlmostEqual(h["kinetic_energy_before"],h["kinetic_energy_after"],delta=TOL)
            self.assertAlmostEqual(h["incoming_contact_normal_rate"],-h["outgoing_contact_normal_rate"],delta=TOL)
            self.assertTrue(independent_check(c))

    def test_two_no-contact_cases_do_not_invent_a_new_motion(self):
        for angle in (0.,20.):
            c=attempt(angle)
            self.assertEqual(c["status"],"NO_QUALIFYING_THIRD_CONTACT")
            self.assertIsNone(c["third_impulse"])
            self.assertEqual(c["clearance_bounds"],[])
            self.assertTrue(independent_check(c))

    def test_forged_impulse_and_frame_fail(self):
        c=attempt(10.)
        for field in ("normal_impulse","outgoing_spin","contact_orientation",
                      "kinetic_energy_after","contact_vertex_index",
                      "contact_absolute_virtual_time","contact_point"):
            bad=deepcopy(c)
            if field=="contact_point":bad["third_impulse"][field][0]+=.03
            else:bad["third_impulse"][field]+=.03
            with self.subTest(field=field),self.assertRaises(ValueError):
                independent_check(bad)

    def test_forged_bounds_or_claim_of_hardware_fail(self):
        c=attempt(12.25)
        for field in ("gap_at_third_contact","outgoing_gap_rate",
                      "curvature_upper_bound","end_gap_lower_bound",
                      "rate_lower_bound","conservative_margin"):
            bad=deepcopy(c)
            bad["clearance_bounds"][4][field]+=.04
            with self.subTest(field=field),self.assertRaises(ValueError):
                independent_check(bad)
        for field,value in (
            ("measured_material_response",True),
            ("another_receiver_constructed",True),
            ("formal_interval_certificate",True),
            ("local_window",.02),
            ("local_separation_only",False),
            ("third_impulse_model_hypothesis",False),
        ):
            bad=deepcopy(c);bad[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):
                independent_check(bad)

    def test_original_receiver_unchanged_or_refused(self):
        c=attempt(5.)
        for field in ("anchor","normal","endpoints"):
            bad=deepcopy(c)
            bad["source_receiver"][field][0][0]+=.1 if field=="endpoints" else 0
            if field!="endpoints":bad["source_receiver"][field][0]+=.1
            with self.subTest(field=field),self.assertRaises(ValueError):
                independent_check(bad)


if __name__=="__main__":
    unittest.main()
