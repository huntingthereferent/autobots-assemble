"""Independent finite-law controls for budgeted extension of a path union."""
import unittest
from dataclasses import replace

from ab_chatbot_discovered_correspondence import DOMAIN
from ab_chatbot_path_union import PathUnionAgent
from ab_chatbot_union_extension import UnionEdgeExtender
from ab_chatbot_relation_probe import FiniteSystem
from ab_chatbot_stability_witness import TransportedLaw
import test_ab_chatbot_path_union as fixture

class UnionExtensionTests(unittest.TestCase):
    def make(self, old_phi=(0,0,1), new_phi=(0,0,0), *, depth=0,
             goals=((0,0,0),), budget=54, remote=False):
        f=fixture.PathUnionTests()
        self.addCleanup(f.doCleanups)
        discovered, old, new, old_owner, new_owner = f.make(
            old_phi, new_phi, depth=depth, budget=budget, remote_new=remote)
        src=PathUnionAgent(discovered,goals)
        return UnionEdgeExtender(src), old, new, old_owner, new_owner

    @staticmethod
    def finish(e, *, allowance=4):
        for _ in range(250):
            r=e.advance(max_new_edges=allowance)
            if r.status!='CONTINUING':return r
        raise AssertionError('extension did not finish')

    @staticmethod
    def oracle(base, old_phi, new_phi):
        """Reference greedy paired-graph closure, independent of bridge/caches."""
        old, new = FiniteSystem(old_phi), FiniteSystem(new_phi)
        mapping=dict(base.state_pairs)
        reverse={v:k for k,v in mapping.items()}
        edges={(s,a):(s,a,t,ns,nt) for s,a,t,ns,nt in base.admitted_edges}
        queue=[(s,a) for s in sorted(mapping) for a in 'AB' if (s,a) not in edges]
        excluded=[]
        for s,a in queue:
            if (s,a) in edges:continue
            ns=mapping[s]
            t,nt=old.step(s,a),new.step(ns,a)
            if t in mapping and mapping[t]!=nt:
                excluded.append((s,a,t,nt,'SOURCE_COLLISION'))
            elif nt in reverse and reverse[nt]!=t:
                excluded.append((s,a,t,nt,'TARGET_COLLISION'))
            else:
                if t not in mapping:
                    mapping[t]=nt;reverse[nt]=t
                    queue.extend((t,l) for l in 'AB' if (t,l) not in edges)
                edges[(s,a)]=(s,a,t,ns,nt)
        return tuple(sorted(mapping.items())),tuple(sorted(edges.values())),tuple(excluded)

    def test_root_only_union_extends_and_preserves_conflicts(self):
        e,old,new,*_=self.make()
        original=e.base
        r=self.finish(e)
        self.assertEqual(r.status,'PARTIAL_EXTENSION_WITNESSED')
        self.assertEqual((len(r.state_pairs),len(r.admitted_edges),len(r.rejected)),(9,15,3))
        self.assertEqual((r.old_observed_edges,r.new_observed_edges),(18,18))
        self.assertEqual(r.initial_states,1)
        self.assertEqual(r.initial_edges,0)
        self.assertEqual(r.pending,0)
        self.assertEqual((len(original.state_pairs),len(original.admitted_edges)),(1,0))
        self.assertTrue(all(x.witness.old_equal != x.witness.new_equal for x in r.rejected))
        for s,a,t,ns,nt in r.admitted_edges:
            self.assertEqual(dict(r.state_pairs)[s],ns)
            self.assertEqual(dict(r.state_pairs)[t],nt)
            self.assertEqual(old.snapshot.edges[(s,a)],t)
            self.assertEqual(new.snapshot.edges[(ns,a)],nt)

    def test_existing_joined_paths_not_discarded(self):
        e,*_=self.make(depth=7,goals=((0,1,1),(2,2,0)))
        base_pairs=set(e.base.state_pairs)
        base_edges=set(e.base.admitted_edges)
        r=self.finish(e)
        self.assertEqual(r.status,'PARTIAL_EXTENSION_WITNESSED')
        self.assertTrue(base_pairs.issubset(r.state_pairs))
        self.assertTrue(base_edges.issubset(r.admitted_edges))
        self.assertEqual((len(r.state_pairs),len(r.admitted_edges),len(r.rejected)),(9,12,6))

    def test_independent_reference_for_three_rule_pairs(self):
        for a,b in [((0,0,1),(0,0,0)),((0,0,0),(0,0,1)),((0,1,0),(2,1,0))]:
            with self.subTest(old=a,new=b):
                e,*_=self.make(a,b)
                ref=self.oracle(e.base,a,b)
                r=self.finish(e)
                self.assertEqual(r.state_pairs,ref[0])
                self.assertEqual(r.admitted_edges,ref[1])
                self.assertEqual(tuple((x.source,x.action,x.old_target,x.new_target,x.cause)
                                       for x in r.rejected),ref[2])

    def test_zero_budget_no_new_reads_then_single_reads(self):
        e,old,new,*_=self.make()
        r=e.advance(max_new_edges=0)
        self.assertEqual(r.status,'CONTINUING')
        self.assertEqual((len(old.snapshot.edges),len(new.snapshot.edges)),(0,0))
        for _ in range(100):
            before=len(old.snapshot.edges)+len(new.snapshot.edges)
            r=e.advance(max_new_edges=1)
            after=len(old.snapshot.edges)+len(new.snapshot.edges)
            self.assertLessEqual(after-before,1)
            if r.status!='CONTINUING':break
        self.assertEqual(r.status,'PARTIAL_EXTENSION_WITNESSED')
        self.assertEqual((len(old.snapshot.edges),len(new.snapshot.edges)),(18,18))

    def test_underlying_budget_is_recoverable_explicitly(self):
        e,old,new,*_=self.make(budget=2)
        r=self.finish(e,allowance=10)
        self.assertEqual(r.status,'UNKNOWN_BUDGET')
        self.assertLessEqual(r.old_observed_edges,2)
        self.assertLessEqual(r.new_observed_edges,2)
        old.snapshot.max_edges=54
        new.snapshot.max_edges=54
        self.assertEqual(self.finish(e).status,'PARTIAL_EXTENSION_WITNESSED')

    def test_same_law_reaches_rooted_closure(self):
        e,*_=self.make(new_phi=(0,0,1))
        r=self.finish(e)
        self.assertEqual(r.status,'ROOTED_CLOSED_WITNESSED')
        self.assertEqual(len(r.rejected),0)
        self.assertEqual(len(r.admitted_edges),2*len(r.state_pairs))
        self.assertTrue(all(a==b for a,b in r.state_pairs))

    def test_remote_is_not_locally_certified(self):
        e,*_=self.make(remote=True)
        r=self.finish(e)
        self.assertEqual(r.status,'PARTIAL_EXTENSION_REMOTE_REPORTED')

    def test_repin_blocks_reuse(self):
        e,old,new,_,owner=self.make()
        self.finish(e)
        owner.replace(TransportedLaw((1,1,1),tuple(DOMAIN)))
        new.ask('pin current version')
        self.assertEqual(e.advance().status,'UNKNOWN_VERSION')

    def test_corrupt_newly_added_edge_fails_replay(self):
        e,old,new,*_=self.make()
        r=self.finish(e)
        s,a,t,ns,nt=r.new_edges[0]
        old.snapshot.edges[(s,a)]=(2,2,2) if t!=(2,2,2) else (1,1,1)
        self.assertEqual(e.advance(max_new_edges=0).status,'WALL_OBSERVATION')

    def test_corrupt_excluded_edge_fails_replay(self):
        e,old,new,*_=self.make()
        r=self.finish(e)
        x=r.rejected[0]
        old.snapshot.edges[(x.source,x.action)]=(2,2,2) if x.old_target!=(2,2,2) else (1,1,1)
        self.assertEqual(e.advance(max_new_edges=0).status,'WALL_OBSERVATION')

    def test_corrupt_prior_history_fails_replay(self):
        e,old,new,*_=self.make(depth=7,goals=((0,1,1),(2,2,0)))
        self.finish(e)
        old.snapshot.edges[((0,0,0),'A')]=(2,2,2)
        self.assertEqual(e.advance(max_new_edges=0).status,'WALL_OBSERVATION')

    def test_terminal_is_idempotent_and_read_free(self):
        e,old,new,*_=self.make()
        r=self.finish(e)
        cached=(dict(old.snapshot.edges),dict(new.snapshot.edges))
        repeated=e.advance(max_new_edges=0)
        self.assertEqual(r,repeated)
        self.assertEqual(cached,(old.snapshot.edges,new.snapshot.edges))

    def test_rejected_witnesses_replay_in_both_finite_laws(self):
        e,*_=self.make()
        r=self.finish(e)
        old,new=FiniteSystem((0,0,1)),FiniteSystem((0,0,0))
        for x in r.rejected:
            w=x.witness
            self.assertEqual(w.old_equal,old.follow(w.left_word)==old.follow(w.right_word))
            self.assertEqual(w.new_equal,new.follow(w.left_word)==new.follow(w.right_word))
            self.assertNotEqual(w.old_equal,w.new_equal)

    def test_initial_without_completed_discovery_rejected(self):
        f=fixture.PathUnionTests()
        self.addCleanup(f.doCleanups)
        discovered,*_=f.make(finish=False)
        with self.assertRaises(ValueError):
            UnionEdgeExtender(PathUnionAgent(discovered,((0,1,1),)))

    def test_budget_argument_validation(self):
        e,*_=self.make()
        for bad in (-1,109,True,1.1):
            with self.assertRaises(ValueError):e.advance(max_new_edges=bad)

if __name__=='__main__':unittest.main()
