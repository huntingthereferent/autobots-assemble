"""Neutral WORLD20 transport tests; synthetic records do not validate physics.

Pinned source-native workflow separately runs the untouched original WORLD18/
WORLD20 numerical generation and independent rotating-corner/extrema verifier.
"""
from copy import deepcopy
import unittest

from work.ab_world.world_trial20_handoff import (
    carry, PIN, SOURCE, SOURCE18, ANGLES, DURATION, ARRIVED, ABSENT
)
from work.ab_world.verify_construction import verify_receipt


def fixture():
    older=[]
    newer=[]
    for i,angle in enumerate(ANGLES):
        active=i not in (0,7)
        first_return={"corner_index":2,"dt_after_initial_contact":.02} if active else None
        impulse={"contact_vertex_index":2,
                 "selected_as_actual_material_response":False} if active else None
        old={"schema":SOURCE18,"angle":angle,
             "source_trial17_first_return":first_return,
             "candidate_impulse":impulse,
             "status":"NO_OVERLAP_DETECTED_IN_LOCAL_SAMPLES" if active else
                      "NO_ADMITTED_RENEWED_CONTACT",
             "physical_second_impact_observed":False,
             "receiver_constructed":False,
             "further_impacts_solved":False}
        old_record={
            "schema":SOURCE,"source_trial18_schema":SOURCE18,
            "source_angle":angle,"source_first_return":deepcopy(first_return),
            "original_source_wall_center":[12.,1.5],
            "projection_duration":DURATION,
            "construction_policy":
                "normal opposite recorded outgoing centre velocity; pose-supported future face",
            "model_movement_not_hardware_measurement":True,
            "third_impulse_calculated":False,
            "receiver_real_material_built":False,
            "nominal_floating_point_not_formal_interval":True,
            "earlier_world_sources_unchanged":True,
        }
        if active:
            old_record.update({
                "status":ARRIVED,
                "receiver":{
                    "id":"motion-derived-finite-receiver",
                    "constructed_from":
                        "Trial18 conditional outgoing velocity and square rotation",
                    "source_corner":2,"activated_at_relative_time":0.,
                    "proposed_target_time":DURATION,
                    "normal":[-1.,0.],
                    "anchor":[10.,2.],
                    "endpoints":[[10.,1.5],[10.,2.5]],
                },
                "next_contact":{
                    "at_relative_time":DURATION,
                    "geometric_touch_only":True,
                    "third_impulse_assumed":False,
                    "vertex_index":2,
                    "point":[10.,2.],
                    "absolute_virtual_time":1.25,
                    "incoming_normal_vertex_rate":-1.,
                },
                "frames":[{"time":round(DURATION*j/10,10),
                           "center":[12.-j*.1,2.],
                           "orientation":j*.01} for j in range(11)],
                "source_clearance_entire_interval_checked":True,
                "receiver_clearance_entire_interval_checked":True,
                "world_boundary_clearance_entire_interval_checked":True,
                "third_collision_outcome_unresolved":True,
            })
        else:
            old_record.update({"status":ABSENT,
                               "receiver":None,"next_contact":None,
                               "frames":[]})
        older.append(old)
        newer.append(old_record)
    return {
        "schema":SOURCE,"angles":list(ANGLES),"cases":newer,
        "conditional_receiver_arrivals":6,"no_source_second_impulse":2,
        "real_material_receiver_fabricated":False,
        "new_engine_or_world_created":False,
    },{
        "schema":SOURCE18,"angles":list(ANGLES),"cases":older,
        "material_contact_response_proven":False,
        "created_any_new_receiver":False,
    }


class Trial20NeutralCarrierTests(unittest.TestCase):
    def test_source_movement_construction_and_no_impulse_cases_separated(self):
        native,previous=fixture()
        frozen=(deepcopy(native),deepcopy(previous))
        report=carry(native,previous)
        self.assertEqual((native,previous),frozen)
        self.assertTrue(report["ledger_witness"]["valid"])
        self.assertEqual(report["ledger_witness"]["pages_verified"],8)
        self.assertEqual(report["ledger_witness"]["steps_verified"],140)
        self.assertEqual(report["ledger_witness"]["observations_recorded"],96)
        self.assertEqual(report["source_conditional_receiver_arrivals"],6)
        self.assertEqual(report["no_second_impulse_controls"],2)
        self.assertEqual(report["source_candidate_model_frames"],66)
        self.assertEqual(report["real_material_receiver_constructions"],0)
        self.assertEqual(report["third_impulses_calculated_by_adapter"],0)
        for i,page in enumerate(report["ledger_pages"]):
            r=page["receipt"]
            self.assertTrue(verify_receipt(r)["valid"])
            objects=r["final"]["objects"]
            expected=i not in (0,7)
            self.assertEqual("conditional-finite-receiver" in objects,expected)
            self.assertEqual(
                r["final"]["comparisons"]
                ["receiver-versus-no-receiver-hypothesis"]["result"],
                "DIFFERENT" if expected else "MATCH")

    def test_derived_receiver_introduced_after_source_frames_and_clearance(self):
        native,previous=fixture()
        receipt=carry(native,previous)["ledger_pages"][1]["receipt"]
        operations=[e["operation"] for e in receipt["events"]]
        end_frames=max(i for i,o in enumerate(operations)
                       if o["op"]=="observe"
                       and o["id"].startswith("proposed-model-pose"))
        clearance=next(i for i,o in enumerate(operations)
                       if o["op"]=="observe"
                       and o["id"]=="conditional-source-clearance")
        receiver=next(i for i,o in enumerate(operations)
                      if o["op"]=="introduce"
                      and o["id"]=="conditional-finite-receiver")
        third=next(i for i,o in enumerate(operations)
                   if o["op"]=="observe"
                   and o["id"]=="conditional-third-contact-feature")
        self.assertLess(end_frames,clearance)
        self.assertEqual(receiver,clearance+1)
        self.assertGreater(third,receiver)
        self.assertFalse(
            receipt["final"]["objects"]["conditional-finite-receiver"]
            ["physical_material_constructed"])

    def test_no_second_impulse_cannot_create_receiver(self):
        native,previous=fixture()
        native["cases"][0]["receiver"]=deepcopy(native["cases"][1]["receiver"])
        with self.assertRaises(ValueError):carry(native,previous)
        native,previous=fixture()
        native["cases"][0]["frames"]=deepcopy(native["cases"][1]["frames"])
        with self.assertRaises(ValueError):carry(native,previous)

    def test_source_control_and_hardware_promotions_rejected(self):
        for key,value in (
            ("receiver_real_material_built",True),
            ("third_impulse_calculated",True),
            ("nominal_floating_point_not_formal_interval",False),
            ("source_clearance_entire_interval_checked",False),
            ("third_collision_outcome_unresolved",False),
        ):
            native,previous=fixture()
            native["cases"][1][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                carry(native,previous)
        native,previous=fixture()
        previous["cases"][1]["candidate_impulse"][
            "selected_as_actual_material_response"]=True
        with self.assertRaises(ValueError):carry(native,previous)

    def test_source_pair_and_geometry_lineage_rejected(self):
        native,previous=fixture()
        native["cases"][1]["source_first_return"]={"corner_index":3}
        with self.assertRaises(ValueError):carry(native,previous)
        native,previous=fixture()
        native["cases"][1]["receiver"]["source_corner"]=3
        with self.assertRaises(ValueError):carry(native,previous)
        native,previous=fixture()
        native["cases"][1]["next_contact"]["third_impulse_assumed"]=True
        with self.assertRaises(ValueError):carry(native,previous)
        native,previous=fixture()
        native["cases"][1]["frames"][4]["time"]=.5
        with self.assertRaises(ValueError):carry(native,previous)
        native,previous=fixture()
        native["cases"][1],native["cases"][2]=native["cases"][2],native["cases"][1]
        with self.assertRaises(ValueError):carry(native,previous)

    def test_source_pin_and_independent_receipt_replay(self):
        native,previous=fixture()
        with self.assertRaises(ValueError):
            carry(native,previous,source_commit="0"*40)
        receipt=carry(native,previous,source_commit=PIN)["ledger_pages"][1]["receipt"]
        bad=deepcopy(receipt)
        bad["events"][-1]["effect"]={"fake":"hardware"}
        with self.assertRaises(ValueError):verify_receipt(bad)
        bad=deepcopy(receipt)
        bad["final"]["objects"]["conditional-finite-receiver"][
            "physical_material_constructed"]=True
        with self.assertRaises(ValueError):verify_receipt(bad)


if __name__ == "__main__":
    unittest.main()
