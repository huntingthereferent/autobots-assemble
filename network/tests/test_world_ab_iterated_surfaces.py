"""Independent chronology and contact geometry oracle for iterative A/B growth.

It does not run the generator or read desired blueprint shape labels. Checks
each source-grown face was activated at its causal contact and did not exist
earlier. Each next contact is recomputed with elementary line intersection.
"""
from copy import deepcopy
from math import isclose
import unittest
from systems.workspace.world_ab_iterated_surfaces import run,DURATION,SCHEMA
from systems.workspace.world_ab_contact_trial import HALF,initial
from network.tests.test_world_ab_relation_growth import check_original_blueprint_after

def independent_trace(out):
    if out.get("schema")!=SCHEMA or out.get("source_original_wall_preserved") is not True:
        raise ValueError("original source geometry not proved")
    source=out["surfaces"][0]
    if (source["id"]!="source-wall" or source["face_x"]!=12 or
        source["normal"]!=[-1.,0.] or source["active_at"]!=0):
        raise ValueError("original wall moved")
    x,y,vx,vy=[out["input"][key] for key in ("x","y","vx","vy")]
    t=0.
    before_ids={source["id"]}
    events=out["events"]
    surfaces=out["surfaces"]
    proposals=out["construction_attempts"]
    if len(proposals)!=len(events):raise ValueError("unrecorded construction decision")
    for i,event in enumerate(events):
        if event["index"]!=i:raise ValueError("event chronology index drifted")
        sec=event["time"]-t
        if sec< -1e-8:raise ValueError("time moved backwards")
        predicted_x=x+vx*sec
        predicted_y=y+vy*sec
        if (abs(event["point"][0]-predicted_x)>4e-8 or
            abs(event["point"][1]-predicted_y)>4e-8 or
            event["incoming_velocity"]!=[round(vx,9),round(vy,9)]):
            raise ValueError("event position not derived from free flight")
        hit=next((z for z in surfaces if z["id"]==event["source_surface_id"]),None)
        if hit is None or hit["id"] not in before_ids:
            raise ValueError("future-generated surface was used in earlier contact")
        if hit["active_at"]>event["time"]+1e-8:
            raise ValueError("surface collided before creation")
        n=hit["normal"][0]
        if (vx*n>=0 or
            abs(predicted_x-(hit["face_x"]+n*HALF))>3e-8 or
            not hit["y_min"]-HALF-1e-8<=predicted_y<=hit["y_max"]+HALF+1e-8):
            raise ValueError("event did not contact its active physical face")
        e=out["input"]["restitution"]
        vx_after=-e*vx
        if (event["outgoing_velocity"]!=[round(vx_after,9),round(vy,9)] or
            not isclose(event["impulse"],(1+e)*abs(vx),abs_tol=4e-8) or
            event["energy_after"]>event["energy_before"]+4e-8):
            raise ValueError("elastic impulse/energy contradicted")
        proposal=proposals[i]
        if proposal["contact_index"]!=i:raise ValueError("proposal not bound to observed event")
        candidates=[z for z in surfaces if z["source_contact_index"]==i]
        if proposal["accepted"]:
            if len(candidates)!=1 or candidates[0]!=proposal["candidate"]:
                raise ValueError("accepted physical surface not actually installed")
            new=candidates[0]
            if new["id"] in before_ids or abs(new["active_at"]-event["time"])>1e-8:
                raise ValueError("created wall lacks unique causal source")
            if abs(new["normal"][0])!=1 or new["normal"][1]!=0:
                raise ValueError("novel rotated/curved geometry claimed")
            for old in surfaces:
                if old["id"] not in before_ids:continue
                overlap_y=new["y_min"]<=old["y_max"]+.5 and new["y_max"]>=old["y_min"]-.5
                if overlap_y and abs(new["face_x"]-old["face_x"])<=.5+1e-8:
                    raise ValueError("insufficient space between constructed surfaces")
            before_ids.add(new["id"])
        elif candidates:
            raise ValueError("rejected receiver inserted anyway")
        t=event["time"];x=event["point"][0];y=event["point"][1];vx=vx_after
    last=out["final"]
    if (abs(last["time"]-DURATION)>1e-9 or
        abs(last["x"]-(x+vx*(DURATION-t)))>5e-8 or
        abs(last["y"]-(y+vy*(DURATION-t)))>5e-8):
        raise ValueError("final continued motion disagrees with collision events")
    if len(surfaces)!=len(before_ids) or len(surfaces)-1!=out["generated_surface_count"]:
        raise ValueError("source-derived physical growth count wrong")
    if out["straight_vertical_faces_only"] is not True or out["full_original_visual_blueprint_generated"] is not False:
        raise ValueError("unsupported structural outcome promoted")
    return True

class IteratedWORLDConstructionTests(unittest.TestCase):
    def test_01_generated_faces_have_nonretroactive_causal_chronology(self):
        out=run()
        self.assertTrue(independent_trace(out))
        self.assertEqual(out["generated_surface_count"],3)
        self.assertEqual([x["face_x"] for x in out["surfaces"]],
                         [12.0,9.5,10.875,10.0625])
        self.assertEqual([e["source_surface_id"] for e in out["events"][:4]],
                         ["source-wall","generated-face-1","generated-face-2","generated-face-3"])
        self.assertTrue(any(not p["accepted"] for p in out["construction_attempts"]))
        self.assertTrue(any(p["reason"]=="FACES_TOO_CLOSE_FOR_BLOCK" for p in out["construction_attempts"]))
    def test_02_original_reference_still_does_not_emerge(self):
        out=run()
        # Independent comparison uses the source sketch only AFTER generation.
        first=check_original_blueprint_after({
            "assembly":{"constructed":True,"surface":{"id":out["surfaces"][1]["id"]}},
            "second_motion":{"contacts":out["events"]}})
        self.assertEqual(first["missing_original_shapes"],
             ["guide","funnel","diverter","spiral"])
        self.assertFalse(first["full_original_blueprint_generated"])
        self.assertFalse(out["spontaneous_material_self_assembly"])
    def test_03_no_wall_contact_stops_construction(self):
        out=run(initial(y=3.5,vy=0))
        self.assertEqual(out["generated_surface_count"],0)
        self.assertEqual(out["events"],[])
        self.assertTrue(independent_trace(out))
    def test_04_stopped_block_stops_construction(self):
        out=run(initial(restitution=0))
        self.assertEqual(out["generated_surface_count"],0)
        self.assertEqual(len(out["events"]),1)
        self.assertEqual(out["construction_attempts"][0]["reason"],"NO_REBOUND")
        self.assertTrue(independent_trace(out))
    def test_05_restitution_changes_grown_geometry(self):
        full=run(initial(restitution=1))
        lower=run(initial(restitution=.5))
        self.assertTrue(independent_trace(lower))
        self.assertNotEqual(full["surfaces"][1]["face_x"],lower["surfaces"][1]["face_x"])
    def test_06_deliberate_false_sources_fail_independent_replay(self):
        out=run()
        edits=[
          lambda t:t["events"][1].update(time=3.7),
          lambda t:t["surfaces"][1].update(active_at=4.0),
          lambda t:t["surfaces"][2].update(face_x=10.0),
          lambda t:t["events"][2].update(impulse=0.0),
          lambda t:t["surfaces"][3].update(normal=[0.0,1.0]),
          lambda t:t["construction_attempts"][0].update(accepted=False),
          lambda t:t["final"].update(x=11.7),
        ]
        for i,change in enumerate(edits):
            modified=deepcopy(out);change(modified)
            with self.subTest(i=i),self.assertRaises(ValueError):
                independent_trace(modified)
if __name__=="__main__":
    unittest.main()
