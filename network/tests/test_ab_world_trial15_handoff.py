"""Trial15 carrier: two supports, causal receiver, unsupported square endpoint."""
from copy import deepcopy
import unittest

from work.ab_world.world_trial15_handoff import carry, ANGLES, BODIES, SOURCE
from work.ab_world.verify_construction import verify_receipt

PIN = "65339494abaccac3c4dd20aa89439af057ec3035"


def fixture(body="disc", angle=0., status="TWO_MODELED_CONTACTS"):
    face = {
        "id": "original-test-source", "anchor": [12., 1.5],
        "normal": [-1., 0.], "endpoints": [[12., 1.], [12., 2.]],
    }
    state = {
        "schema": SOURCE, "body": body,
        "body_support": ("disc radius" if body == "disc" else
                         "axis-aligned square support, orientation fixed by constraint"),
        "half_extent": .25, "source_angle": angle,
        "source_anchor": [12.,1.5], "initial_center": [3.,1.35],
        "initial_velocity": [3., .12], "source": face,
        "selected_physical_outcome": False,
        "measured_earth_material": False,
        "target_receiver_shape_provided": False,
    }
    if status != "TWO_MODELED_CONTACTS":
        return {**state, "status": status, "receiver": None,
                "contacts": [], "frames": []}
    rec = {
        "id": "movement-derived-receiver", "normal": [1.,0.],
        "anchor": [11.,1.5], "endpoints": [[11.,1.], [11.,2.]],
        "activated_at": .2, "caused_by_contact_index": 0,
        "constructed_from": "recorded-model-outgoing-velocity",
    }
    events = [
        {"time": .2, "source_id": face["id"], "center": [11.75,1.5],
         "before": [3.,.12], "after": [-3.,.12]},
        {"time": .4, "source_id": rec["id"], "center": [11.,1.6],
         "before": [-3.,.12], "after": [3.,.12]},
    ]
    frames = [
        {"time": round(i*.05,9), "center": [3.+i*.1,1.35],
         "velocity": [3., .12] if i < 4 or i >= 8 else [-3., .12]}
        for i in range(12)
    ]
    return {**state, "status": status, "receiver": rec, "contacts": events,
            "frames": frames,
            "square_rotation_prevented_by_constraint": body=="fixed-square",
            "finite_face_endpoints_matter": True,
            "actual_hardware_contact_witnessed": False,
            "new_physical_law_inferred": False,
    }


def sample():
    return {"schema": SOURCE,
            "source_trial14": "world-ab-relation-derived-free-orientation/v1",
            "source_trial04b_reused": True, "body_types": list(BODIES),
            "angles": list(ANGLES),
            "shape_independent_contact_law": "frictionless translational normal reflection",
            "no_new_world_or_renderer": True,
            "real_material_behavior_observed": False,
            "cases": [fixture(body,angle) for body in BODIES for angle in ANGLES]}


def excluded():
    q=fixture("fixed-square",30.,"NO_ADMITTED_INTERIOR_CONTACT")
    return q


class Trial15SupportCarrierTests(unittest.TestCase):
    def test_01_both_body_supports_preserved_in_nine_bounded_receipts(self):
        original=sample()
        snap=deepcopy(original)
        out=carry(original,PIN,excluded())
        self.assertEqual(original,snap)
        self.assertEqual(out["completed_source_cases"],8)
        self.assertEqual(out["unsupported_endpoint_cases"],1)
        self.assertEqual(out["preserved_motion_frames"],96)
        self.assertEqual(out["ledger_witness"]["pages_verified"],9)
        self.assertEqual(out["ledger_witness"]["steps_verified"],163)
        self.assertEqual(out["ledger_witness"]["observations_recorded"],25)
        self.assertTrue(out["ledger_witness"]["valid"])
        self.assertFalse(out["free_square_rotation_solved"])
        self.assertFalse(out["physical_endpoint_miss_established"])
        for page in out["ledger_pages"]:
            self.assertTrue(verify_receipt(page["receipt"])["valid"])
        square=out["ledger_pages"][4]["receipt"]["final"]["objects"]["controlled-moving-body"]
        self.assertTrue(square["square_rotation_fixed"])
        self.assertNotIn("derived-receiver",out["ledger_pages"][-1]["receipt"]["final"]["objects"])

    def test_02_receiver_introduced_after_original_source_contact(self):
        receipt=carry(sample(),PIN,excluded())["ledger_pages"][0]["receipt"]
        steps=[e["operation"] for e in receipt["events"]]
        witness=next(i for i,op in enumerate(steps)
                     if op["op"]=="observe" and op["id"]=="first-source-model-contact")
        derived=next(i for i,op in enumerate(steps)
                     if op["op"]=="introduce" and op["id"]=="derived-receiver")
        self.assertEqual(derived,witness+1)
        self.assertNotIn("derived-receiver",
                         [x["id"] for x in steps[:derived] if "id" in x])

    def test_03_square_constraint_and_original_support_cannot_be_forged(self):
        a=sample()
        a["cases"][4]["square_rotation_prevented_by_constraint"]=False
        with self.assertRaisesRegex(ValueError,"rotation boundary"):
            carry(a,PIN,excluded())
        a=sample()
        a["cases"][4]["body_support"]="free spinning square"
        with self.assertRaisesRegex(ValueError,"square constraint"):
            carry(a,PIN,excluded())
        a=sample()
        a["cases"][0]["body"]="fixed-square"
        with self.assertRaisesRegex(ValueError,"support"):
            carry(a,PIN,excluded())

    def test_04_endpoint_refusal_never_acquires_created_geometry(self):
        r=excluded()
        r["receiver"]={"id":"fabricated"}
        with self.assertRaisesRegex(ValueError,"unsupported endpoint"):
            carry(sample(),PIN,r)
        r=excluded()
        r["status"]="PHYSICAL_MISS"
        with self.assertRaisesRegex(ValueError,"unsupported endpoint"):
            carry(sample(),PIN,r)
        r=excluded()
        r["frames"]=[{"time":0.,"center":[2.,2.]}]
        with self.assertRaisesRegex(ValueError,"unsupported endpoint"):
            carry(sample(),PIN,r)

    def test_05_model_history_and_real_material_claims_rejected(self):
        a=sample()
        a["cases"][0]["receiver"]["activated_at"]=0.
        with self.assertRaisesRegex(ValueError,"backdated"):
            carry(a,PIN,excluded())
        a=sample()
        a["cases"][0]["frames"][3]["time"]=.01
        with self.assertRaisesRegex(ValueError,"out of order"):
            carry(a,PIN,excluded())
        a=sample()
        a["cases"][0]["actual_hardware_contact_witnessed"]=True
        with self.assertRaisesRegex(ValueError,"rotation boundary"):
            carry(a,PIN,excluded())
        with self.assertRaisesRegex(ValueError,"exact pinned"):
            carry(sample(),"moving-branch",excluded())

    def test_06_independent_ledger_rejects_unreported_rotation_or_early_receiver(self):
        receipt=carry(sample(),PIN,excluded())["ledger_pages"][4]["receipt"]
        altered=deepcopy(receipt)
        altered["final"]["objects"]["controlled-moving-body"]["square_rotation_fixed"]=False
        with self.assertRaises(ValueError):
            verify_receipt(altered)
        altered=deepcopy(receipt)
        altered["events"][-1]["effect"]={"status":"real-matter-constructed"}
        with self.assertRaises(ValueError):
            verify_receipt(altered)


if __name__=="__main__":
    unittest.main()
