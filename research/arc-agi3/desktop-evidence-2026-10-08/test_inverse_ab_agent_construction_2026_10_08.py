"""Focused local tests: proposed inverse A/B construct direction, not repo code."""
import sys,json,math,unittest
from pathlib import Path
from itertools import product
from collections import defaultdict
ROOT=Path(r"C:\Users\teepa\continuity-live")
EV=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
sys.path.insert(0,str(ROOT))
from runtime.ab_information import (
    ABOccurrence,information_closure,synthesize_continuation_relation,
    apply_synthesized,partition_is_sufficient)
from runtime.ab_loop import ABFrame,ABAgent,ABMove,ABLoop

def move(s,a):
    """Synthetic nested two-chamber world: chamber, gate0, gate1."""
    room,g0,g1=s
    if a=="step":
        gate=(g0,g1,0)[room]
        return (min(2,room+1) if gate else room,g0,g1)
    if a=="toggle":
        return (room,1-g0,g1) if room==0 else (
            (room,g0,1-g1) if room==1 else s)
    raise ValueError("unadmitted action")

STATES=[(0,g0,g1) for g0,g1 in product((0,1),repeat=2)]
def future(s,h):
    out=[]
    for _ in range(h):
        s=move(s,"step")
        out.append(s[0])
    return tuple(out)
def group(h):
    return [ABOccurrence.create(referent="nested-maze",
      relations={"gate0":s[1],"gate1":s[2],"unrelated":i},
      continuation=future(s,h)) for i,s in enumerate(STATES)]
def inverse_fibers(part):
    return {i:tuple(block) for i,block in enumerate(part)}

class ConstructionMathTests(unittest.TestCase):
    def test_forward_ab_one_step_categories(self):
        q=information_closure(group(1))
        self.assertEqual(sorted(map(len,q.continuation_partition)),[2,2])
        self.assertEqual(q.proofs[0].partition,q.continuation_partition)
        self.assertEqual(q.proofs[0].sources,(("gate0",),))
    def test_category_inverse_recovers_every_witness(self):
        q=information_closure(group(1));fibers=inverse_fibers(q.continuation_partition)
        self.assertEqual(sorted(sum((list(v) for v in fibers.values()),[])),list(range(4)))
        for i,ids in fibers.items():
            self.assertEqual(len({group(1)[j].continuation for j in ids}),1)
    def test_inverse_retains_all_source_histories(self):
        old=json.loads((EV/"sk48_l2_directional_phase_cross_source_ab.json").read_text())
        src=old["source_variants"]["1"]
        self.assertEqual(src,[[2],[1,7],[4,7]])
        self.assertEqual(len({tuple(s) for s in src}),3)
    def test_projections_are_candidates_not_native_observations(self):
        source=json.loads((EV/"SK48_AB_INVERTED_FRACTAL_PROJECTION_2026-10-08.json").read_text())
        self.assertFalse(source["native_game_spatial_fractal_evidence"])
        self.assertEqual(len(source["levels"]["5"]["nodes"]),243)
    def test_inverse_branch_witness_depth_three(self):
        e=json.loads((EV/"SK48_AB_REAL_CATEGORY_INVERSE_BRANCH_HOLDOUT_2026-10-08.json").read_text())
        self.assertEqual(len(e["counterexamples"]),0)
        self.assertEqual(len(e["branches"]),40)
        self.assertTrue(all(b["matched_categories"]==[b["depth"]] for b in e["branches"]))
    def test_deeper_native_witness_not_exaggerated(self):
        e=json.loads((EV/"SK48_AB_INVERSE_DEPTH5_FRONTIER_2026-10-08.json").read_text())
        self.assertEqual(e["all_paths_tested_for_visible_state"],243)
        self.assertEqual(e["six_action_holdout_sample_count"],24)
        self.assertLess(e["six_action_holdout_sample_count"],243)
    def test_coarse_parent_projection_fails(self):
        a,b=(0,0,0),(0,1,0)
        self.assertEqual(a[0],b[0])
        self.assertNotEqual(move(a,"step")[0],move(b,"step")[0])
    def test_first_horizon_does_not_erase_future_split(self):
        one=information_closure(group(1))
        two=information_closure(group(2))
        self.assertEqual(len(one.continuation_partition),2)
        self.assertEqual(len(two.continuation_partition),3)
        self.assertTrue(any(len(b)==2 for b in two.continuation_partition))
    def test_old_relation_names_cannot_encode_true_three_way_quotient(self):
        st=information_closure(group(2))
        self.assertTrue(all(len(p.partition)>len(st.continuation_partition) for p in st.proofs))
        syn=synthesize_continuation_relation(st)
        self.assertIsNotNone(syn)
        self.assertEqual(len(syn.proof_partition),4)
        self.assertEqual(len(syn.continuation_partition),3)
    def test_synthesis_repairs_lost_boundary_without_inventing_futures(self):
        st=information_closure(group(2)); syn=synthesize_continuation_relation(st)
        for block in st.continuation_partition:
            self.assertEqual(len({apply_synthesized(syn,i) for i in block}),1)
        self.assertEqual(len({apply_synthesized(syn,i) for i in range(4)}),3)
    def test_unobserved_relation_is_unknown(self):
        observations=[ABOccurrence.create(referent="missing",
           relations={"same":0},continuation=label) for label in ("X","Y")]
        with self.assertRaises(ValueError):
            information_closure(observations)
    def test_nested_chamber_coupling_changes_two_step_future(self):
        self.assertEqual(future((0,1,0),2),(1,1))
        self.assertEqual(future((0,1,1),2),(1,2))
        self.assertEqual(future((0,1,0),1),future((0,1,1),1))
    def test_complete_state_parent_rule_commutes_for_admitted_actions(self):
        # Identity projection is a valid control; do not claim a minimal quotient.
        for pos in range(3):
            for g0,g1 in product((0,1),repeat=2):
                s=(pos,g0,g1)
                for a in ("step","toggle"):
                    projected=tuple(move(s,a))
                    parent=move(tuple(s),a)
                    self.assertEqual(projected,parent)
    def test_projected_fractal_addresses_distinct(self):
        for n in range(1,6):
            intervals=sorted((
              sum(2*d/(5**(j+1)) for j,d in enumerate(seq)),
              sum(2*d/(5**(j+1)) for j,d in enumerate(seq))+5**(-n)
            ) for seq in product(range(3),repeat=n))
            self.assertEqual(len(intervals),3**n)
            self.assertTrue(all(intervals[i][1]<intervals[i+1][0]
                  for i in range(len(intervals)-1)))
        self.assertAlmostEqual(math.log(3)/math.log(5),0.6826061944859854)
    def test_existing_ab_loop_does_not_promote_unobserved_proposal(self):
        def worker(frame):
            return ABMove(state="UNKNOWN",
              reached={"proposal":frame.current["candidate"]},
              survived=frame.survives,changed=(),edge="unwitnessed construction",
              note="new world awaits comparison")
        frame=ABFrame(referent="nested-maze",direction="construct",
           current={"candidate":[0,1,1]},survives=("source provenance",),
           edge="projection admission")
        result=ABLoop((ABAgent("existing-ab",worker),),max_steps=2).run(frame)
        self.assertEqual(result.move_count,0)
        self.assertEqual(result.final_frame.current["stopped_state"],"UNKNOWN")
        self.assertIn("unresolved",result.stop_reason)

if __name__=="__main__":
    unittest.main(verbosity=2)
