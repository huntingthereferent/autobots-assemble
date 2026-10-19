"""Independent oracle: no manufactured witness, no unmeasured contact selection."""
import unittest
from copy import deepcopy
from math import hypot,cos,sin,radians
from systems.workspace.world_ab_contact_discrimination import run,SCHEMA,SENSOR_TIMES,SENSOR_QUANTA,MU_HYPOTHESIS
from systems.workspace.world_ab_active_set_trial import run as original
from systems.workspace.world_ab_two_contact_stress import run as stress
from network.tests.test_world_ab_junction_continuous import source_equivalent

def check(out):
    ancestor=original();src=stress()
    if out["schema"]!=SCHEMA or out["source_trial10_schema"]!=ancestor["schema"] or out["source_trial09_schema"]!=src["schema"]:
        raise ValueError("source lineage altered")
    if not source_equivalent(out["original_source_geometry"],ancestor["original_source_geometry"]):
        raise ValueError("parent source geometry mutated")
    if out["sensor_times"]!=list(SENSOR_TIMES) or out["sensor_position_quanta"]!=list(SENSOR_QUANTA):
        raise ValueError("hypothetical sensor grid modified")
    if out["source_trial10_counts"]!=ancestor["counts"] or out["source_trial09_two_active_counts"]!=ancestor["original_trial09_two_active_counts"]:
        raise ValueError("prior verified response set hidden")
    if out["friction_coefficient_hypothesis"]!=MU_HYPOTHESIS:
        raise ValueError("Coulomb cone parameter disguised")
    for key,expected in (
        ("friction_cone_check_is_necessary_not_sufficient",True),
        ("all_normals_restitution_is_extra_unobserved_postulate",True),
        ("all_sensor_readings_are_counterfactual",True),
        ("source_physical_outgoing_velocities_measured",False),
        ("original_trial06_mu_point_four_solver_resolved",False),
        ("actual_outcome_selected",False),
        ("external_physical_blueprint_constructed",False)):
        if out[key] is not expected:raise ValueError("unobserved physical event claimed")
    if len(out["cases"])!=35:raise ValueError("not all source cases recorded")
    measures={"ambiguous_cases":0,"friction_cone_only_narrowed_cases":0,
        "all_normals_rest_narrowed_cases":0,"all_normals_rest_eliminated_cases":0,
        "ambiguous_cases_with_hypothetical_distinguishing_sensor":0,
        "ambiguous_cases_not_distinguished_at_tested_sensor_settings":0}
    for case,orig,source in zip(out["cases"],ancestor["cases"],src["cases"]):
        if case["original_index"]!=orig["original_index"] or case["geometry_kind"]!=orig["geometry_kind"]:
            raise ValueError("original case identity swapped")
        if case["incoming_angle_degrees"]!=orig["incoming_angle_degrees"] or case["surface_B_rotation_degrees"]!=orig["surface_B_rotation_degrees"]:
            raise ValueError("source angle or controlled rotation overwritten")
        if case["source_trial10_classification"]!=orig["classification"]:
            raise ValueError("Trial10 source status hidden")
        if case["actual_source_sensor_reading_available"] is not False or case["physical_outcome_selected"] is not False:
            raise ValueError("invented actual physical sensor measurement")
        live=[q for q in orig["alternatives"] if q["status"]=="admissible-local-model"]
        if case["original_admissible_count"]!=len(live) or len(case["candidates"])!=len(live):
            raise ValueError("discarded verified Trial10 candidates")
        vin=(-2*cos(radians(source["incoming_angle_degrees"])),-2*sin(radians(source["incoming_angle_degrees"])))
        normals=[]
        center=source["contact_center"]
        for seg in source["surfaces"]:
            a,b=seg["endpoints"];dx=b[0]-a[0];dy=b[1]-a[1]
            length=hypot(dx,dy);n=(-dy/length,dx/length)
            if (center[0]-a[0])*n[0]+(center[1]-a[1])*n[1]<0:n=(-n[0],-n[1])
            normals.append(n)
        cone=0;rest=0
        for recorded,owner in zip(case["candidates"],live):
            if recorded["active_indices"]!=owner["active_indices"] or recorded["source_ids"]!=owner["active_ids"]:
                raise ValueError("contact identity switched")
            if recorded["outgoing_velocity"]!=owner["outgoing_velocity"]:
                raise ValueError("owner's resulting velocity mutated")
            if recorded["has_actual_outgoing_motion_measurement"] is not False:
                raise ValueError("pretended hypothetical velocity was measured")
            active=owner["active_indices"];jn=owner["normal_impulses"]
            if recorded["tangent_impulses_under_original_mu_zero_model"]!=[0. for _ in active]:
                raise ValueError("invented frictional tangential impulse")
            expected_bound=[round(MU_HYPOTHESIS*jn[k],9) for k in active]
            if recorded["mu_point_four_normal_cone_bounds"]!=expected_bound:
                raise ValueError("friction cone bound unrelated to normal impulse")
            if recorded["necessary_mu_point_four_cone"] is not True:
                raise ValueError("zero-tangent impulse fails necessary cone inequality")
            cone+=1
            vout=owner["outgoing_velocity"]
            # Independent all-touching-normals reflection hypothesis oracle.
            expected=all(abs(sum((vout[k]+vin[k])*n[k] for k in (0,1)))<=6e-8 for n in normals)
            if recorded["hypothesis_both_touching_normals_restitute"]!=expected:
                raise ValueError("unobserved extra restitution postulate misapplied")
            rest+=expected
        if case["necessary_friction_cone_retained_count"]!=cone or case["additional_all_normals_restitution_retained_count"]!=rest:
            raise ValueError("postulate/cone counts do not equal independently read candidate set")
        if cone<len(live):measures["friction_cone_only_narrowed_cases"]+=1
        if rest<len(live):measures["all_normals_rest_narrowed_cases"]+=1
        if rest==0:measures["all_normals_rest_eliminated_cases"]+=1
        if len(live)>1:measures["ambiguous_cases"]+=1
        if len(case["sensors"])!=len(SENSOR_TIMES)*len(SENSOR_QUANTA):
            raise ValueError("not all hypothetical sensor settings evaluated")
        first=None
        for i,(time,quantum) in enumerate((t,q) for t in SENSOR_TIMES for q in SENSOR_QUANTA):
            sensor=case["sensors"][i]
            if sensor["virtual_time"]!=time or sensor["position_quantum"]!=quantum:
                raise ValueError("sensor time/precision substituted")
            if sensor["measured_reading"] is not None:
                raise ValueError("synthetic reading promoted as actual data")
            # Independently reconstruct from true owner motion at original
            # sampled time; do not consult generator's rounded bins.
            bins={}
            frame=round(time/.05)
            for choice in live:
                p=choice["frames"][frame]["position"]
                if abs(choice["frames"][frame]["time"]-time)>1e-8:
                    raise ValueError("missing time in actual finite source")
                binxy=(round(p[0]/quantum),round(p[1]/quantum))
                bins.setdefault(binxy,[]).append(choice["active_indices"])
            expected=[{"bin_xy":list(k),"possible_active_sets":v} for k,v in sorted(bins.items())]
            if not source_equivalent(sensor["hypothetical_reading_partitions"],expected):
                raise ValueError("counterfactual reading partition fabricated")
            if sensor["distinguishable_bins"]!=len(expected) or sensor["would_uniquely_discriminate_if_a_matching_reading_were_observed"]!=(len(expected)==len(live)):
                raise ValueError("hypothetical experiment claim not justified")
            if first is None and len(live)>1 and len(expected)==len(live):
                first={"virtual_time":time,"position_quantum":quantum}
        if case["first_hypothetical_discriminating_sensor"]!=first:
            raise ValueError("first potential sensor setting misreported")
        if len(live)>1:
            key=("ambiguous_cases_with_hypothetical_distinguishing_sensor" if first else
                 "ambiguous_cases_not_distinguished_at_tested_sensor_settings")
            measures[key]+=1
    if out["counts"]!=measures:
        raise ValueError("classification or possible evidence counts forged")
    if measures["ambiguous_cases"]!=26 or measures["friction_cone_only_narrowed_cases"]!=0:
        raise ValueError("Trial10 source changed or cone necessary condition misrepresented")
    return True

class Trial11Tests(unittest.TestCase):
    def test_entire_source_with_independent_candidate_oracle(self):
        self.assertTrue(check(run()))
    def test_no_unobserved_measurement_can_choose_an_active_set(self):
        obj=run()
        self.assertFalse(obj["actual_outcome_selected"])
        self.assertTrue(all(c["physical_outcome_selected"] is False for c in obj["cases"]))
        self.assertTrue(all(s["measured_reading"] is None for c in obj["cases"] for s in c["sensors"]))
    def test_necessary_cone_does_not_act_as_friction_solver(self):
        obj=run()
        self.assertEqual(obj["counts"]["friction_cone_only_narrowed_cases"],0)
        self.assertFalse(obj["original_trial06_mu_point_four_solver_resolved"])
    def test_additional_postulate_kept_separate_from_evidence(self):
        obj=run()
        self.assertTrue(obj["all_normals_restitution_is_extra_unobserved_postulate"])
        self.assertGreater(obj["counts"]["all_normals_rest_narrowed_cases"],0)
    def test_fake_evidence_and_changed_candidate_rejected(self):
        obj=run()
        cases=[lambda x:x["cases"][0]["sensors"][0].update(measured_reading=[1,2]),
          lambda x:x["cases"][10]["candidates"][0].update(has_actual_outgoing_motion_measurement=True),
          lambda x:x["cases"][10]["candidates"][0]["outgoing_velocity"].__setitem__(0,100.),
          lambda x:x["cases"][10]["sensors"][1].update(distinguishable_bins=99),
          lambda x:x.update(actual_outcome_selected=True),
          lambda x:x.update(original_trial06_mu_point_four_solver_resolved=True),
          lambda x:x["counts"].update(ambiguous_cases=0)]
        for i,mutate in enumerate(cases):
            invalid=deepcopy(obj);mutate(invalid)
            with self.subTest(i=i),self.assertRaises(ValueError):check(invalid)

if __name__=="__main__":unittest.main()
