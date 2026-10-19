"""Independent first-impact mechanics for source-wall angle versus fixed-normal A/B.

Independent source-face first-contact solution and impulse-energy oracle; reads
no output targets from the visual blueprint. Does not authenticate full
rotational free flight after collision or a functioning second surface.
"""
import unittest
from copy import deepcopy
from math import radians,cos,sin,isclose,hypot
from systems.workspace.world_ab_oblique_impact import experiment,strike,INERTIA,HALF
from systems.workspace.world_ab_contact_trial import initial

def verify_impact(result):
    start=result["incoming"]
    angle=result["angle_degrees"]
    n=(-cos(radians(angle)),-sin(radians(angle)))
    tangent=(-n[1],n[0])
    # Independently derive square's support by comparing 4 projected corners.
    projections=[(dx,dy,dx*n[0]+dy*n[1]) for dx in (-HALF,HALF) for dy in (-HALF,HALF)]
    min_projection=min(x[2] for x in projections)
    support=[(x,y) for x,y,q in projections if abs(q-min_projection)<1e-10]
    lever=(sum(x for x,y in support)/len(support),
           sum(y for x,y in support)/len(support))
    separation=(start["x"]-12)*n[0]+(start["y"]-1.5)*n[1]+min_projection
    velocity_normal=start["vx"]*n[0]+start["vy"]*n[1]
    t=-separation/velocity_normal
    at=(start["x"]+start["vx"]*t+lever[0],
        start["y"]+start["vy"]*t+lever[1])
    finite_param=(at[0]-12)*tangent[0]+(at[1]-1.5)*tangent[1]
    contact_ok=0<t<4 and abs(finite_param)<=.5+1e-9
    if not contact_ok:
        if result["hit"]:raise ValueError("invented contact outside finite boundary")
        return True
    if not result["hit"]:raise ValueError("real incoming square contact omitted")
    rxn=lever[0]*n[1]-lever[1]*n[0]
    e=start["restitution"]
    impulse=-(1+e)*velocity_normal/(1+rxn*rxn/INERTIA)
    outgoing=(start["vx"]+impulse*n[0],start["vy"]+impulse*n[1])
    spin=impulse*rxn/INERTIA
    def equal(a,b,name):
        if not isclose(a,b,rel_tol=0,abs_tol=5e-8):raise ValueError(name)
    equal(result["first_contact_time"],t,"time")
    equal(result["finite_wall_parameter"],finite_param,"span")
    equal(result["normal_impulse"],impulse,"impulse")
    equal(result["angular_velocity_after"],spin,"angular velocity")
    equal(result["moment_of_inertia"],INERTIA,"inertia")
    for z,v in zip(result["contact_point"],at):equal(z,v,"contact point")
    for z,v in zip(result["support_lever"],lever):equal(z,v,"lever arm")
    for z,v in zip(result["velocity_after"],outgoing):equal(z,v,"rebound")
    E0=.5*(start["vx"]**2+start["vy"]**2)
    E1=.5*(outgoing[0]**2+outgoing[1]**2)+.5*INERTIA*spin*spin
    equal(result["kinetic_energy_before"],E0,"incoming energy")
    equal(result["kinetic_energy_after"],E1,"outgoing energy")
    if E1>E0+1e-8:raise ValueError("passive contact increased kinetic energy")
    receiver=result["candidate_receiver"]
    if hypot(*outgoing)>1e-9:
        if receiver is None:raise ValueError("derived receiver missing")
        speed=hypot(*outgoing)
        normal=(-outgoing[0]/speed,-outgoing[1]/speed)
        expected_center=(at[0]+outgoing[0]*.6,at[1]+outgoing[1]*.6)
        for v,w in zip(receiver["normal"],normal):equal(v,w,"derived normal")
        for v,w in zip(receiver["center"],expected_center):equal(v,w,"derived center")
        if receiver["surface_built"] is not False or receiver["second_contact_witnessed"] is not False:
            raise ValueError("candidate silently promoted to witnessed second surface")
    return True

class ObliqueFirstImpactTests(unittest.TestCase):
    def test_01_original_vertical_face_remains_no_spin(self):
        result=experiment()
        a=result["A_original_vertical"]
        self.assertTrue(verify_impact(a))
        self.assertEqual(a["support_count"],2)
        self.assertEqual(a["angular_velocity_after"],0.)
        self.assertEqual(a["velocity_after"],[-2.1,.12])
        self.assertFalse(result["exact_original_blueprint_generated"])
    def test_02_oblique_contact_generates_spin_and_new_direction(self):
        r=experiment(angle=20)
        a,b=r["A_original_vertical"],r["B_oblique"]
        self.assertTrue(verify_impact(b))
        self.assertNotEqual(b["angular_velocity_after"],0.)
        self.assertEqual(b["support_count"],1)
        self.assertNotEqual(a["velocity_after"],b["velocity_after"])
        self.assertNotEqual(a["candidate_receiver"]["normal"],
                            b["candidate_receiver"]["normal"])
        self.assertTrue(b["after_look"]["unconstrained_ballistic_projection_only"])
        self.assertFalse(b["after_look"]["continuous_contact_retested"])
    def test_03_multiple_angles_separate_source_normal_and_contact(self):
        for angle in (0,5,10,15,20):
            with self.subTest(angle=angle):
                r=experiment(angle=angle)
                self.assertTrue(verify_impact(r["A_original_vertical"]))
                self.assertTrue(verify_impact(r["B_oblique"]))
    def test_04_missed_face_does_not_claim_contact(self):
        missed=strike(initial(y=3.5,vy=0),20)
        self.assertFalse(missed["hit"])
        self.assertEqual(missed["reason"],"CONTACT_OUTSIDE_FINITE_SOURCE_FACE")
        self.assertTrue(verify_impact(missed))
    def test_05_zero_restitution_keeps_energy_nonincreasing(self):
        for e in (0,.2,.7,1):
            with self.subTest(e=e):
                obj=experiment(initial(restitution=e),angle=20)
                for key in ("A_original_vertical","B_oblique"):
                    r=obj[key]
                    self.assertTrue(verify_impact(r))
                    self.assertLessEqual(r["kinetic_energy_after"],
                                         r["kinetic_energy_before"]+1e-8)
    def test_06_forged_angular_evidence_and_target_labels_rejected(self):
        r=experiment()["B_oblique"]
        for key,value in (("angular_velocity_after",0),("normal_impulse",0),
                          ("first_contact_time",5),("kinetic_energy_after",99)):
            fake=deepcopy(r);fake[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):verify_impact(fake)
        fake=deepcopy(r);fake["candidate_receiver"]["surface_built"]=True
        with self.assertRaises(ValueError):verify_impact(fake)
        for angle in (-1,21,"20",float("nan")):
            with self.subTest(angle=angle),self.assertRaises(ValueError):
                experiment(angle=angle)
if __name__=="__main__":unittest.main()
