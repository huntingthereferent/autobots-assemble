"""Independent WORLD20 witness: independently reconstruct proposed receiver and path.

Compute trigonometric corner-distance extrema by scanning derivative signs
and bisecting them, NOT using the generator's analytic stationary-time method.
The source is a declared virtual law: no physical material observation.
"""
from copy import deepcopy
from math import cos,sin,hypot
import unittest

from systems.workspace.world_ab_rotating_receiver import trial,run,SCHEMA,ANGLES,DURATION
from systems.workspace.world_ab_local_recontact_impulse import attempt as old_attempt
from network.tests.test_world_ab_local_recontact_impulse import verify as verify_prior
from systems.workspace.world_ab_oblique_impact import HALF,WALL_CENTER,SPAN

VERTICES=((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))
TOL=3e-7

def d(a,b):
    return a[0]*b[0]+a[1]*b[1]

def near(a,b,epsilon=TOL):
    if isinstance(a,(tuple,list)):
        return isinstance(b,(tuple,list)) and len(a)==len(b) and all(
            near(x,y,epsilon) for x,y in zip(a,b))
    return abs(a-b)<epsilon

def transformed(impulse,local,t):
    center=impulse["contact_center"];v=impulse["velocity_after"]
    angle=impulse["contact_angle"]+impulse["angular_velocity_after"]*t
    cc,ss=cos(angle),sin(angle)
    return (center[0]+v[0]*t+cc*local[0]-ss*local[1],
            center[1]+v[1]*t+ss*local[0]+cc*local[1])

def derivative(impulse,vertex,normal,t):
    w=impulse["angular_velocity_after"]
    theta=impulse["contact_angle"]+w*t
    rx=cos(theta)*vertex[0]-sin(theta)*vertex[1]
    ry=sin(theta)*vertex[0]+cos(theta)*vertex[1]
    v=impulse["velocity_after"]
    return d((v[0]-w*ry,v[1]+w*rx),normal)

def extrema(impulse,vertex,normal,origin):
    """Numerical derivative-root search; different method than source."""
    def gap(t):
        p=transformed(impulse,vertex,t)
        return d((p[0]-origin[0],p[1]-origin[1]),normal)
    times=[0.,DURATION]
    divisions=256
    left=0.;vleft=derivative(impulse,vertex,normal,0.)
    for i in range(1,divisions+1):
        right=DURATION*i/divisions
        vright=derivative(impulse,vertex,normal,right)
        if vleft*vright<0:
            a,b=left,right
            oldsign=vleft
            for _ in range(52):
                mid=(a+b)/2
                vmid=derivative(impulse,vertex,normal,mid)
                if oldsign*vmid>0:
                    a=mid;oldsign=vmid
                else:b=mid
            times.append((a+b)/2)
        left=right;vleft=vright
    return sorted(set(times)),[gap(t) for t in sorted(set(times))]

def independent_check(record):
    if record["schema"]!=SCHEMA or record["source_angle"] not in ANGLES:
        raise ValueError("source trial/angle altered")
    if (record["projection_duration"]!=DURATION or
        record["original_source_wall_center"]!=list(WALL_CENTER) or
        record["model_movement_not_hardware_measurement"] is not True or
        record["receiver_real_material_built"] is not False or
        record["third_impulse_calculated"] is not False or
        record["nominal_floating_point_not_formal_interval"] is not True or
        record["earlier_world_sources_unchanged"] is not True):
        raise ValueError("research origin/temporal scope promoted")
    previous=old_attempt(record["source_angle"])
    verify_prior(previous)
    if record["source_trial18_schema"]!=previous["schema"] or record["source_first_return"]!=previous["source_trial17_first_return"]:
        raise ValueError("prior source movement changed")
    h=previous["candidate_impulse"]
    if h is None:
        if record["status"]!="NO_SOURCE_SECOND_IMPULSE" or record["receiver"] is not None or record["next_contact"] is not None or record["frames"]:
            raise ValueError("receiver fabricated without second source impulse")
        return True
    if record["status"]!="CONDITIONAL_DERIVED_RECEIVER_REACHED":
        raise ValueError("declared source geometry not admitted")
    if any(record[key] is not True for key in (
        "source_clearance_entire_interval_checked",
        "receiver_clearance_entire_interval_checked",
        "world_boundary_clearance_entire_interval_checked",
        "third_collision_outcome_unresolved")):
        raise ValueError("whole interval or unresolved next impulse hidden")
    v=tuple(h["velocity_after"])
    speed=hypot(*v)
    n=(-v[0]/speed,-v[1]/speed)
    tangent=(-n[1],n[0])
    p0=tuple(h["contact_center"])
    future_center=(p0[0]+DURATION*v[0],p0[1]+DURATION*v[1])
    offset=[transformed(h,p,DURATION) for p in VERTICES]
    projections=[d((pt[0]-future_center[0],pt[1]-future_center[1]),n) for pt in offset]
    target=min(range(4),key=lambda i:(projections[i],i))
    anchor=(future_center[0]+projections[target]*n[0],
            future_center[1]+projections[target]*n[1])
    r=record["receiver"]
    if (r["id"]!="motion-derived-finite-receiver" or
        not near(r["anchor"],anchor) or not near(r["normal"],n) or
        r["source_corner"]!=h["contact_vertex_index"] or
        r["activated_at_relative_time"]!=0 or
        r["proposed_target_time"]!=DURATION or
        r["constructed_from"]!="Trial18 conditional outgoing velocity and square rotation"):
        raise ValueError("receiver not constructed from source movement")
    expected=[(anchor[0]+s*SPAN/2*tangent[0],
               anchor[1]+s*SPAN/2*tangent[1]) for s in (-1,1)]
    if not near(r["endpoints"],expected):
        raise ValueError("finite receiver endpoints fabricated")
    for end in expected:
        if not (0<end[0]<24 and 0<end[1]<6):
            raise ValueError("receiver outside world")
    original=tuple(previous["source_first_contact"]["normal"])
    for end in expected:
        if d((end[0]-WALL_CENTER[0],end[1]-WALL_CENTER[1]),original)<=0:
            raise ValueError("derived segment crosses original supporting line")

    contact=record["next_contact"]
    vertex=offset[target]
    along=d((vertex[0]-anchor[0],vertex[1]-anchor[1]),tangent)
    if (contact["vertex_index"]!=target or
        contact["at_relative_time"]!=DURATION or
        not near(contact["point"],vertex) or
        not near(contact["tangent_coordinate"],along) or
        abs(along)>=SPAN/2 or
        contact["geometric_touch_only"] is not True or
        contact["third_impulse_assumed"] is not False or
        not near(contact["incoming_normal_vertex_rate"],derivative(h,VERTICES[target],n,DURATION)) or
        contact["incoming_normal_vertex_rate"]>=0):
        raise ValueError("receiver contact claim unsupported")
    absolute=h["contact_time_relative"]+previous["source_first_contact"]["first_contact_time"]+DURATION
    if not near(contact["absolute_virtual_time"],absolute):
        raise ValueError("source time lineage broken")

    limits=[
        (original,WALL_CENTER,"source",h["contact_vertex_index"]),
        (n,anchor,"receiver",target),
        ((1.,0.),(0.,0.),"boundary",None),
        ((-1.,0.),(24.,0.),"boundary",None),
        ((0.,1.),(0.,0.),"boundary",None),
        ((0.,-1.),(0.,6.),"boundary",None),
    ]
    for normal,origin,kind,contact_index in limits:
        for i,p in enumerate(VERTICES):
            times,gaps=extrema(h,p,normal,origin)
            if kind=="source" and i==contact_index:
                if abs(gaps[0])>TOL or derivative(h,p,normal,0.)<=1e-5:
                    raise ValueError("source does not separate after original contact")
                tested=gaps[1:]
            elif kind=="receiver" and i==contact_index:
                if abs(gaps[-1])>TOL or derivative(h,p,normal,DURATION)>=-1e-5:
                    raise ValueError("not incoming finite receiver at projected time")
                tested=gaps[:-1]
            else:tested=gaps
            if any(g<=1e-6 for g in tested):
                raise ValueError("whole interval source/receiver/boundary clearance failed")

    frames=record["frames"]
    if len(frames)!=11:raise ValueError("partial movement history")
    for i,frame in enumerate(frames):
        t=DURATION*i/10
        theta=h["contact_angle"]+h["angular_velocity_after"]*t
        center=(p0[0]+v[0]*t,p0[1]+v[1]*t)
        if not near(frame["time"],t) or not near(frame["center"],center) or not near(frame["orientation"],theta):
            raise ValueError("fabricated frame")
    return True


class World20Tests(unittest.TestCase):
    def test_all_eight_controls_independently_replayed(self):
        data=run()
        self.assertEqual(data["schema"],SCHEMA)
        self.assertEqual(data["conditional_receiver_arrivals"],6)
        self.assertEqual(data["no_source_second_impulse"],2)
        self.assertFalse(data["real_material_receiver_fabricated"])
        self.assertFalse(data["new_engine_or_world_created"])
        for case in data["cases"]:
            with self.subTest(angle=case["source_angle"]):
                self.assertTrue(independent_check(case))

    def test_six_rotating_square_movements_reach_new_derived_finite_face(self):
        for angle in ANGLES[1:-1]:
            with self.subTest(angle=angle):
                case=trial(angle)
                self.assertEqual(case["status"],"CONDITIONAL_DERIVED_RECEIVER_REACHED")
                self.assertLess(case["next_contact"]["incoming_normal_vertex_rate"],0)
                self.assertTrue(independent_check(case))

    def test_no_second_impulse_means_no_receiver(self):
        for angle in (0.,20.):
            case=trial(angle)
            self.assertEqual(case["status"],"NO_SOURCE_SECOND_IMPULSE")
            self.assertIsNone(case["receiver"])
            self.assertIsNone(case["next_contact"])
            self.assertTrue(independent_check(case))

    def test_forged_anchor_orientation_endpoints_or_contact_rejected(self):
        good=trial(12.25)
        for field in ("anchor","normal","endpoints"):
            fake=deepcopy(good)
            if field=="endpoints":fake["receiver"][field][0][0]+=.08
            else:fake["receiver"][field][0]+=.08
            with self.subTest(field=field),self.assertRaises(ValueError):
                independent_check(fake)
        for field in ("vertex_index","at_relative_time","tangent_coordinate",
                      "absolute_virtual_time","incoming_normal_vertex_rate","point"):
            fake=deepcopy(good)
            if field=="point":fake["next_contact"][field][0]+=.08
            else:fake["next_contact"][field]+=.08
            with self.subTest(field=field),self.assertRaises(ValueError):
                independent_check(fake)

    def test_false_time_material_or_third_impulse_claim_rejected(self):
        for field,value in (
            ("projection_duration",.5),
            ("receiver_real_material_built",True),
            ("third_impulse_calculated",True),
            ("nominal_floating_point_not_formal_interval",False),
            ("source_clearance_entire_interval_checked",False),
            ("third_collision_outcome_unresolved",False),
        ):
            fake=deepcopy(trial(10.))
            fake[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):
                independent_check(fake)

    def test_wrong_interval_frames_refused(self):
        base=trial(7.5)
        for field in ("time","center","orientation"):
            fake=deepcopy(base)
            if field=="center":fake["frames"][6][field][0]+=.05
            else:fake["frames"][6][field]+=.05
            with self.subTest(field=field),self.assertRaises(ValueError):
                independent_check(fake)


if __name__=="__main__":
    unittest.main()
