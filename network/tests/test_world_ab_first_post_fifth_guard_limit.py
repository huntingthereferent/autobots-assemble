"""Independent WORLD38 rotating-world-coordinate first guard limit witness.

Unlike the generator's cosine stationary-angle construction, this witness
uses a sine-phase equation for the extrema of each original gap. It rebuilds
all 24 signed normal gaps from the CCW source square, requires the earliest
guard exhaustion in chronological order, and refuses a material sixth event.
"""
from __future__ import annotations

from copy import deepcopy
from math import asin,atan2,ceil,cos,sin,pi,hypot,isfinite
import unittest

from systems.workspace.world_ab_first_post_fifth_guard_limit import (
    attempt,run,SCHEMA,START,END,GUARD,TIME_TIE,
    first_guard_limit
)
from systems.workspace.world_ab_post_fifth_contiguous_prefix import (
    attempt as original37
)
from network.tests.test_world_ab_post_fifth_contiguous_prefix import verify as verify37
from systems.workspace.world_ab_whole_contact_configuration import attempt as original35
from systems.workspace.world_ab_first_finite_response_qualification import attempt as original29
from systems.workspace.world_ab_third_contact import attempt as original21,ANGLES
from network.tests.test_world_ab_geometry_at_first_envelope_limit import original_planes
from systems.workspace.world_ab_oblique_impact import HALF

CCW=((-HALF,-HALF),(HALF,-HALF),(HALF,HALF),(-HALF,HALF))
INDEX_MAP=(0,3,1,2)
TOL=2e-6


def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]


def source_corner(model,index,t):
    x,y=CCW[INDEX_MAP[index]]
    theta=model["theta"]+model["spin"]*t
    c,s=cos(theta),sin(theta)
    return (model["center"][0]+model["velocity"][0]*t+x*c-y*s,
            model["center"][1]+model["velocity"][1]*t+x*s+y*c)


def signed_gap(model,index,normal,anchor,t):
    p=source_corner(model,index,t)
    return dot((p[0]-anchor[0],p[1]-anchor[1]),normal)


def phase_minima(model,index,n,anchor):
    x,y=CCW[INDEX_MAP[index]]
    c,s=cos(model["theta"]),sin(model["theta"])
    rx,ry=x*c-y*s,x*s+y*c
    harmonic_cos=rx*n[0]+ry*n[1]
    harmonic_sin=-ry*n[0]+rx*n[1]
    velocity=dot(model["velocity"],n)
    w=model["spin"]
    r=hypot(harmonic_cos,harmonic_sin)
    times=[START,END]
    if abs(w)>1e-12 and r>1e-12:
        q=velocity/(w*r)
        if abs(q)<=1:
            phase=atan2(harmonic_sin,harmonic_cos)
            a=asin(max(-1.,min(1.,q)))
            kbound=ceil(abs(w)*END/(2*pi))+8
            for k in range(-kbound,kbound+1):
                for z in (a,pi-a):
                    t=(phase+z+2*pi*k)/w
                    if START+1e-13<t<END-1e-13:
                        times.append(t)
    return sorted(set(times))


def earliest(limit_model,index,normal,anchor):
    marks=phase_minima(limit_model,index,normal,anchor)
    g=lambda t:signed_gap(limit_model,index,normal,anchor,t)
    if g(START)<=GUARD:
        raise ValueError("independent first prefix missing starting positive gap")
    crossing=None
    for a,b in zip(marks,marks[1:]):
        ga,gb=g(a),g(b)
        if ga<=GUARD:
            crossing=a
            break
        if gb>GUARD:continue
        low,high=a,b
        for _ in range(65):
            mid=(low+high)/2
            if g(mid)>GUARD:low=mid
            else:high=mid
        crossing=(low+high)/2
        break
    if crossing is None and g(marks[-1])<=GUARD:
        crossing=marks[-1]
    return crossing,len(marks)-2,min(g(t) for t in marks)


def verify(row):
    angle=row.get("angle")
    if row.get("schema")!=SCHEMA or angle not in ANGLES:
        raise ValueError("original WORLD38 source identity invalid")
    prior=original37(angle)
    if not verify37(prior):
        raise ValueError("WORLD37 independent original prefix failed")
    before=original35(angle)
    fixed={
        "source_trial37_schema":prior["schema"],
        "source_trial37_status":prior["status"],
        "source_original_trial37_supported_prefix_end":prior["supported_prefix_end"],
        "original_world":[24.,6.],
        "source_finite_face_count":2,
        "source_perimeter_plane_count":4,
        "previous_nominally_supported_time":START,
        "declared_max_horizon_after_unselected_fifth":END,
        "positive_source_guard":GUARD,
        "corner_plane_count":24,
        "source_model_is_counterfactual":True,
        "material_fifth_impact_observed":False,
        "sixth_material_contact_observed":False,
        "sixth_impulse_computed":False,
        "new_receiver_constructed":False,
        "post_first_guard_limit_motion_certified":False,
        "formal_outward_rounded_certificate":False,
    }
    if any(row.get(k)!=v for k,v in fixed.items()):
        raise ValueError("first source guard evidence or physical refusal altered")
    if before["conditional_fifth_response"] is None or (
        prior["status"]!="EXTENDED_CONDITIONAL_FIFTH_MODEL_CLEARANCE_SUPPORTED"
        or prior["supported_prefix_end"]!=START):
        expected=("NO_SOURCE_FIFTH_RESPONSE"
                  if before["conditional_fifth_response"] is None else
                  "SOURCE_PREFIX_NOT_FULLY_SUPPORTED")
        if (row.get("status")!=expected
            or row.get("original_24_analytic_gap_records")!=[]
            or row.get("first_source_guard_limit") is not None
            or row.get("coearliest_source_guard_features")!=[]
            or row.get("nominally_supported_until") is not None
            or row.get("all_original_supporting_lines_clear_through_horizon") is not False):
            raise ValueError("inactive case invented a sixth trajectory")
        return True
    fourth=original29(angle)
    t=before["candidate_virtual_time"]
    feature=fourth["qualifying_source_feature"]
    outgoing_fourth=fourth["conditional_fourth_response"]
    fifth=before["conditional_fifth_response"]
    model={
        "center":[feature["contact_center"][i]+outgoing_fourth["outgoing_velocity"][i]*t
                  for i in (0,1)],
        "theta":feature["contact_angle"]+outgoing_fourth["outgoing_spin"]*t,
        "velocity":fifth["outgoing_velocity"],
        "spin":fifth["outgoing_spin"]
    }
    planes=original_planes(original21(angle),angle)
    if len(planes)!=6:
        raise ValueError("six original planes not retained")
    records=row.get("original_24_analytic_gap_records")
    if not isinstance(records,list) or len(records)!=24:
        raise ValueError("missing original 24 independent guard boundaries")
    recovered=[]
    for p,(name,n,anchor,span) in enumerate(planes):
        tangent=(-n[1],n[0])
        for i in range(4):
            rec=records[p*4+i]
            root,nintervals,least=earliest(model,i,n,anchor)
            if (rec.get("source_plane")!=name
                or rec.get("source_corner_index")!=i
                or rec.get("source_plane_is_finite") is not (span is not None)
                or rec.get("never_assume_sixth_collision") is not True
                or rec.get("stationary_partition_count")!=nintervals):
                raise ValueError("original plane identity/complete extrema missing")
            for key,value in (("at_start_signed_gap",signed_gap(model,i,n,anchor,START)),
                              ("at_horizon_signed_gap",signed_gap(model,i,n,anchor,END)),
                              ("minimum_analytic_stationary_gap",least)):
                if not isinstance(rec.get(key),(int,float)) or (
                    abs(rec[key]-value)>TOL):
                    raise ValueError("independent world-coordinate source gap mismatch")
            f=rec.get("first_guard_limit")
            if root is None:
                if f is not None:raise ValueError("invented original guard crossing")
                continue
            world=source_corner(model,i,root)
            along=dot((world[0]-anchor[0],world[1]-anchor[1]),tangent)
            if not isinstance(f,dict):
                raise ValueError("first original guard boundary omitted")
            expected={
                "source_plane":name,
                "source_corner_index":i,
                "source_plane_is_finite":span is not None,
                "finite_face_intersecting_span_at_limit":(
                    abs(along)<=span/2+1e-8 if span is not None else None),
                "physical_contact":False,
            }
            if any(f.get(k)!=v for k,v in expected.items()):
                raise ValueError("finite face classification or physical refusal changed")
            values={
                "guard_limit_time":root,
                "gap_at_guard_limit":signed_gap(model,i,n,anchor,root),
                "finite_face_tangent_coordinate":along if span is not None else None,
            }
            for key,value in values.items():
                if value is None:
                    if f.get(key) is not None:
                        raise ValueError("perimeter plane gained finite face")
                elif not isinstance(f.get(key),(int,float)) or abs(f[key]-value)>TOL:
                    raise ValueError("first guard time or finite source tangent changed")
            theta=model["theta"]+model["spin"]*root
            ox,oy=CCW[INDEX_MAP[i]]
            rotated=(ox*cos(theta)-oy*sin(theta),ox*sin(theta)+oy*cos(theta))
            incoming=dot((model["velocity"][0]-model["spin"]*rotated[1],
                          model["velocity"][1]+model["spin"]*rotated[0]),n)
            if not isinstance(f.get("normal_rate_at_limit"),(float,int)) or abs(
                    f["normal_rate_at_limit"]-incoming)>TOL:
                raise ValueError("independent source contact rate mismatch")
            if any(abs(a-b)>TOL for a,b in zip(f.get("world_corner_at_limit",[]),world)):
                raise ValueError("original world corner does not agree")
            recovered.append((root,f))
    recovered.sort(key=lambda x:(x[0],x[1]["source_plane"],x[1]["source_corner_index"]))
    first=recovered[0][1] if recovered else None
    co=[f for t,f in recovered if abs(t-recovered[0][0])<=TIME_TIE] if recovered else []
    observed=row.get("first_source_guard_limit")
    if (observed!=first or row.get("coearliest_source_guard_features")!=co
        or row.get("all_original_supporting_lines_clear_through_horizon") is not (first is None)
        or row.get("status")!=("FIRST_ORIGINAL_CLEARANCE_GUARD_BOUNDARY" if first else
                              "NO_ORIGINAL_PLANE_GUARD_LIMIT_THROUGH_DECLARED_HORIZON")):
        raise ValueError("earliest original guard relationship not independently supported")
    target=first["guard_limit_time"] if first else END
    if not isinstance(row.get("nominally_supported_until"),(int,float)) or abs(
            row["nominally_supported_until"]-target)>TOL:
        raise ValueError("source moved beyond its first original guard boundary")
    return True


class World38Tests(unittest.TestCase):
    def test_eight_original_cases_have_independent_sine_phase_witness(self):
        data=run()
        self.assertEqual(data["schema"],SCHEMA)
        self.assertEqual(data["source_qualified_cases"],1)
        self.assertEqual(data["inactive_original_cases"],7)
        self.assertEqual(data["complete_horizon_cases"]+data["first_guard_limit_cases"],1)
        self.assertEqual(data["sixth_impulses"],0)
        for row in data["cases"]:
            with self.subTest(angle=row["angle"]):
                self.assertTrue(verify(row))

    def test_synthetic_between_endpoint_rotation_cannot_hide_guard_loss(self):
        from math import pi
        w=2*pi/(END-START)
        r=.002
        q=(GUARD+.001,0.,r*cos(w*START),r*sin(w*START),w)
        self.assertGreater(q[0]+q[2]*cos(w*START)+q[3]*sin(w*START),GUARD)
        self.assertGreater(q[0]+q[2]*cos(w*END)+q[3]*sin(w*END),GUARD)
        result=first_guard_limit(q)
        self.assertIsNotNone(result[0])
        self.assertLess(result[0],(START+END)/2)

    def test_unqualified_source_and_false_physical_impacts_refused(self):
        source=attempt(10.)
        for key,value in (("material_fifth_impact_observed",True),
                          ("sixth_material_contact_observed",True),
                          ("sixth_impulse_computed",True),
                          ("new_receiver_constructed",True),
                          ("post_first_guard_limit_motion_certified",True),
                          ("formal_outward_rounded_certificate",True),
                          ("original_world",[6.,24.])):
            forged=deepcopy(source);forged[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                verify(forged)
        changed=deepcopy(source)
        changed["original_24_analytic_gap_records"][0]["at_start_signed_gap"]+=.1
        with self.assertRaises(ValueError):
            verify(changed)


if __name__=="__main__":
    unittest.main()
