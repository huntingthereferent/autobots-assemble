"""Source-independent arrival geometry and conservative motion audit, Trial 07."""
from copy import deepcopy
from math import hypot
import unittest
from systems.workspace.world_ab_connected_routing import assemble
from systems.workspace.world_ab_junction_continuous import R,trace,nearest
from systems.workspace.world_ab_junction_threshold import (
    SCHEMA,BRACKET,OFFSETS,run,locate,arrival_pair)
from network.tests.test_world_ab_junction_continuous import source_equivalent

def verify(result):
    if result["schema"] != SCHEMA or not source_equivalent(result["source_geometry"],assemble()):
        raise ValueError("original source geometry substituted")
    if result["bracket"] != list(BRACKET) or result["simultaneous_contact_solver"] is not False:
        raise ValueError("trial claim scope changed")
    if result["full_original_blueprint_generated"] is not False or result["earth_material_equivalence"] is not False:
        raise ValueError("unsupported claim")
    geo=result["source_geometry"]
    center=result["junction_contact"]["contact_center"]
    y=result["junction_contact"]["entry_y"]
    if not BRACKET[0]<y<BRACKET[1]:raise ValueError("tie escaped source bracket")
    arrivals=arrival_pair(y,geo["surfaces"])
    if abs(arrivals[0]["time"]-arrivals[1]["time"])>2e-9:
        raise ValueError("not simultaneous")
    if abs(result["junction_contact"]["candidate_gap"])>2e-9:
        raise ValueError("bad reported tie")
    if abs(result["junction_contact"]["contact_time"]-arrivals[0]["time"])>2e-9:
        raise ValueError("reported collision time substituted")
    if result["junction_contact"]["source_ids"]!=[x["id"] for x in geo["surfaces"]]:
        raise ValueError("wrong original surface identities")
    if result["junction_contact"]["features"]!=["interior","interior"]:
        raise ValueError("endpoint contact incorrectly called interior")
    # Independent closest-point geometry: both source finite segments are
    # physically tangent to the same disc center at the detected instant.
    for face in geo["surfaces"]:
        a,b=face["endpoints"];ab=[b[j]-a[j] for j in (0,1)]
        ap=[center[j]-a[j] for j in (0,1)]
        frac=sum(ap[j]*ab[j] for j in (0,1))/sum(z*z for z in ab)
        if not 0<frac<1:raise ValueError("contact outside finite interior")
        point=[a[j]+frac*ab[j] for j in (0,1)]
        if abs(hypot(center[0]-point[0],center[1]-point[1])-R)>5e-8:
            raise ValueError("disc not tangent to original finite face")
    if len(result["probes"])!=len(OFFSETS):raise ValueError("missing nearby controls")
    for index,offset in enumerate(OFFSETS):
        rec=result["probes"][index]
        y=result["junction_contact"]["entry_y"]+offset
        if rec["offset"]!=offset or abs(rec["entry_y"]-y)>1e-10:
            raise ValueError("nearby probe substituted")
        native=trace(y,geo["surfaces"])
        if (rec["status"]!=native["status"] or
            rec["unresolved"]!=native["unresolved"] or
            rec["first_contact"]!=native["first_contact"] or
            rec["observed_contacts"]!=len(native["contacts"]) or
            rec["end_time"]!=native["exit"]["time"]):
            raise ValueError("reported nearby trajectory was not replayed")
        if rec["surface_order_independent"] is not True or native!=trace(y,geo["surfaces"][::-1]):
            raise ValueError("physics depended on face declaration order")
    middle=result["probes"][len(OFFSETS)//2]
    if middle["status"]!="unresolved-multiple-contacts" or middle["observed_contacts"]!=0:
        raise ValueError("arrival tie was falsely promoted to a solved impulse")
    if set(middle["unresolved"]["surfaces"])!=set(result["junction_contact"]["source_ids"]):
        raise ValueError("source pair was not present at unresolved contact")
    return True

class Trial07Tests(unittest.TestCase):
    def test_original_faces_actually_have_an_interior_arrival_tie(self):
        outcome=run();self.assertTrue(verify(outcome))
        self.assertAlmostEqual(outcome["junction_contact"]["entry_y"],1.3910443961,places=8)
    def test_opposite_sides_of_switch_have_different_first_hits(self):
        o=run();pairs=arrival_pair(o["junction_contact"]["entry_y"]-.01,o["source_geometry"]["surfaces"])
        self.assertLess(pairs[1]["time"],pairs[0]["time"])
        pairs=arrival_pair(o["junction_contact"]["entry_y"]+.01,o["source_geometry"]["surfaces"])
        self.assertLess(pairs[0]["time"],pairs[1]["time"])
    def test_tie_fails_closed_even_with_reversed_surface_order(self):
        out=run();mid=out["probes"][4]
        self.assertEqual(mid["status"],"unresolved-multiple-contacts")
        self.assertTrue(all(x["surface_order_independent"] for x in out["probes"]))
        self.assertEqual(mid["observed_contacts"],0)
    def test_falsified_contact_or_scope_rejected(self):
        out=run()
        edits=[
            lambda x:x["junction_contact"].update(contact_time=0.0),
            lambda x:x["junction_contact"].update(candidate_gap=0.02),
            lambda x:x["junction_contact"]["contact_center"].__setitem__(0,7.0),
            lambda x:x["probes"][4].update(status="completed"),
            lambda x:x.update(simultaneous_contact_solver=True),
            lambda x:x["source_geometry"]["surfaces"][0]["endpoints"][0].__setitem__(0,5.0),
        ]
        for i,edit in enumerate(edits):
            damaged=deepcopy(out);edit(damaged)
            with self.subTest(i=i),self.assertRaises(ValueError):verify(damaged)
    def test_nearby_controls_do_not_create_new_geometry(self):
        out=run()
        self.assertEqual(out["bracket"],[1.35,1.4])
        self.assertFalse(out["source_04B_branches_simultaneously_generated"])
        self.assertFalse(out["full_original_blueprint_generated"])

if __name__=="__main__":unittest.main()
