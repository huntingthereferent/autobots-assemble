"""Trial 11: discriminate *hypothetical* collision outcomes without choosing one.

Owns no original source geometry or native observation. Takes the verified
Trial 10 finite, mu=0 e=1 candidates; evaluates necessary (NOT sufficient)
mu=.4 Coulomb cone inequality and additional optional same-time equal-normal
restitution postulate; builds counterfactual quantized POSITION observations.
No invented sensors are counted as real readings, and a friction coefficient
alone is explicitly not a frictional collision solver.
"""
from __future__ import annotations
from collections import defaultdict
from systems.workspace.world_ab_active_set_trial import run as prior_run
from systems.workspace.world_ab_two_contact_stress import run as stress_run, LEAD
from systems.workspace.world_ab_junction_continuous import dot

SCHEMA="world-ab-contact-discrimination-hypotheses/v1"
SENSOR_TIMES=(.40,.60,1.10)
SENSOR_QUANTA=(.1,.01,.001)
MU_HYPOTHESIS=.4
EPS=5e-8

def signature(frame_position, quantum):
    return [int(round(float(z)/quantum)) for z in frame_position]

def candidate_position(answer,time):
    frames=answer["frames"]
    idx=round(time/.05)
    if not frames or idx>=len(frames) or abs(frames[idx]["time"]-time)>1e-8:
        raise ValueError("no retained source trajectory for proposed sample")
    return frames[idx]["position"]

def run():
    ancestor=prior_run()
    stress=stress_run()
    if ancestor["schema"]!="world-ab-two-contact-active-set-enumeration/v1":
        raise ValueError("Trial10 source identity changed")
    if len(ancestor["cases"])!=len(stress["cases"]) or len(ancestor["cases"])!=35:
        raise ValueError("source grid changed")
    cases=[]
    for entry,source in zip(ancestor["cases"],stress["cases"]):
        live=[x for x in entry["alternatives"] if x["status"]=="admissible-local-model"]
        if len(live)!=entry["admissible_count"]:
            raise ValueError("Trial10 alternatives no longer retain all original outcomes")
        incoming=tuple(source["incoming_velocity"])
        normals=[tuple(n) for n in source["normals"]]
        candidate_audits=[]
        for candidate in live:
            active=candidate["active_indices"]
            jn=candidate["normal_impulses"]
            if len(jn)!=2 or any(jn[k]<=0 for k in active):
                raise ValueError("invalid original unilateral impulse")
            # Normal-only trial: tangent impulse was assumed identically zero.
            # |J_t| <= mu J_n is merely a necessary static cone inequality,
            # not evidence the nonzero-mu sliding/friction law is satisfied.
            friction_bound=[MU_HYPOTHESIS*jn[k] for k in active]
            cone_pass=all(0.<=b+EPS for b in friction_bound)
            out=tuple(candidate["outgoing_velocity"])
            all_normal_rest=all(abs(dot(out,n)+dot(incoming,n))<=EPS for n in normals)
            candidate_audits.append({
                "active_indices":active,"source_ids":candidate["active_ids"],
                "outgoing_velocity":candidate["outgoing_velocity"],
                "necessary_mu_point_four_cone":cone_pass,
                "tangent_impulses_under_original_mu_zero_model":[0. for _ in active],
                "mu_point_four_normal_cone_bounds":[round(b,9) for b in friction_bound],
                "hypothesis_both_touching_normals_restitute":all_normal_rest,
                "has_actual_outgoing_motion_measurement":False})
        sensors=[]
        for time in SENSOR_TIMES:
            for quantum in SENSOR_QUANTA:
                grouped=defaultdict(list)
                for candidate in live:
                    x,y=signature(candidate_position(candidate,time),quantum)
                    grouped[(x,y)].append(candidate["active_indices"])
                readings=[{"bin_xy":[p[0],p[1]],"possible_active_sets":names}
                          for p,names in sorted(grouped.items())]
                sensors.append({
                    "virtual_time":time,"position_quantum":quantum,
                    "hypothetical_reading_partitions":readings,
                    "distinguishable_bins":len(readings),
                    "would_uniquely_discriminate_if_a_matching_reading_were_observed":
                        len(readings)==len(live),
                    "measured_reading":None})
        first=next(({"virtual_time":s["virtual_time"],
                      "position_quantum":s["position_quantum"]}
                    for s in sensors if s["would_uniquely_discriminate_if_a_matching_reading_were_observed"] and len(live)>1),None)
        pass_cone=sum(c["necessary_mu_point_four_cone"] for c in candidate_audits)
        pass_stronger=sum(c["hypothesis_both_touching_normals_restitute"] for c in candidate_audits)
        cases.append({
            "original_index":entry["original_index"],
            "incoming_angle_degrees":entry["incoming_angle_degrees"],
            "surface_B_rotation_degrees":entry["surface_B_rotation_degrees"],
            "geometry_kind":entry["geometry_kind"],
            "source_trial10_classification":entry["classification"],
            "original_admissible_count":len(live),
            "candidates":candidate_audits,"sensors":sensors,
            "necessary_friction_cone_retained_count":pass_cone,
            "additional_all_normals_restitution_retained_count":pass_stronger,
            "first_hypothetical_discriminating_sensor":first,
            "actual_source_sensor_reading_available":False,
            "physical_outcome_selected":False})
    counts={
        "ambiguous_cases":sum(c["original_admissible_count"]>1 for c in cases),
        "friction_cone_only_narrowed_cases":sum(c["necessary_friction_cone_retained_count"]<c["original_admissible_count"] for c in cases),
        "all_normals_rest_narrowed_cases":sum(c["additional_all_normals_restitution_retained_count"]<c["original_admissible_count"] for c in cases),
        "all_normals_rest_eliminated_cases":sum(c["additional_all_normals_restitution_retained_count"]==0 for c in cases),
        "ambiguous_cases_with_hypothetical_distinguishing_sensor":sum(
            c["original_admissible_count"]>1 and c["first_hypothetical_discriminating_sensor"] is not None for c in cases),
        "ambiguous_cases_not_distinguished_at_tested_sensor_settings":sum(
            c["original_admissible_count"]>1 and c["first_hypothetical_discriminating_sensor"] is None for c in cases)}
    if counts["ambiguous_cases"]!=ancestor["counts"]["multiple-admissible"]:
        raise ValueError("Trial10 ambiguous base drift")
    return {"schema":SCHEMA,"source_trial10_schema":ancestor["schema"],
       "source_trial09_schema":stress["schema"],
       "original_source_geometry":ancestor["original_source_geometry"],
       "source_trial10_counts":ancestor["counts"],
       "source_trial09_two_active_counts":ancestor["original_trial09_two_active_counts"],
       "sensor_times":list(SENSOR_TIMES),"sensor_position_quanta":list(SENSOR_QUANTA),
       "friction_coefficient_hypothesis":MU_HYPOTHESIS,
       "cases":cases,"counts":counts,
       "friction_cone_check_is_necessary_not_sufficient":True,
       "all_normals_restitution_is_extra_unobserved_postulate":True,
       "all_sensor_readings_are_counterfactual":True,
       "source_physical_outgoing_velocities_measured":False,
       "original_trial06_mu_point_four_solver_resolved":False,
       "actual_outcome_selected":False,
       "external_physical_blueprint_constructed":False}
