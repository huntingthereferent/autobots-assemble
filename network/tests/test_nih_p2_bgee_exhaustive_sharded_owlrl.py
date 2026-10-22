"""Original Bgee full-coverage entailment, independent oracle and negative controls."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import unittest
from rdflib import Graph,RDFS,OWL,URIRef

from systems.workspace import nih_p2_bgee_exhaustive_sharded_owlrl as trial
from systems.workspace import nih_p2_original_bgee_real_expression_join as join

HAS_OWLRL=importlib.util.find_spec("owlrl") is not None
RO=os.environ.get("NIH_ORIGINAL_RO_BASE_OWL")
CORE=os.environ.get("NIH_ORIGINAL_RO_CORE_OWL")
AUTHOR=os.environ.get("NIH_ORIGINAL_BGEE_SOURCE_DIR")
ZIP=os.environ.get("NIH_ORIGINAL_BGEE_POSTGRES_ZIP")


def sources():
    genex=Graph()
    ro=Graph()
    genex.add((join.bridge.GENEX.isExpressedIn,RDFS.subPropertyOf,join.bridge.RO_EXPRESSED))
    ro.add((join.bridge.RO_EXPRESSED,OWL.inverseOf,join.bridge.RO_EXPRESSES))
    return genex,ro


def fixture_rows(n=5):
    rows={"gene":[],"globalcond":[],"globalexpression":[]}
    for i in range(n):
        rows["gene"].append(("gene"+str(i),"ENSG0000"+str(i)))
        rows["globalcond"].append(("condition"+str(i),"UBERON:0000"+str(i)))
        rows["globalexpression"].append(("expression"+str(i),
                                          "gene"+str(i),"condition"+str(i),"EXPRESSED"))
    return rows


class CompleteSourceBgeeEntailmentTests(unittest.TestCase):
    def test_aggregate_original_map_edges_are_disjoint_source_categories(self):
        a,_=join.keyed_join(fixture_rows(5))
        raw=trial.original_join_graph(a)
        self.assertEqual(len(raw),10)
        forward_reverse=trial.direct_entailed(raw)
        self.assertEqual(len(forward_reverse),20)
        self.assertEqual(len(forward_reverse),
                         len(trial.static_sparql_oracle(raw,*trial.source_axioms(*sources()))))

    def test_independent_static_sparql_needs_both_owner_axioms(self):
        g,ro=sources()
        raw=trial.original_join_graph(join.keyed_join(fixture_rows(2))[0])
        sub,inverse=trial.source_axioms(g,ro)
        self.assertEqual(len(trial.static_sparql_oracle(raw,sub,inverse)),8)
        missing_sub=(URIRef("urn:fake-missing"),RDFS.subPropertyOf,join.bridge.RO_EXPRESSED)
        self.assertEqual(trial.static_sparql_oracle(raw,missing_sub,inverse),set())
        reverse_only=(join.bridge.RO_EXPRESSES,OWL.inverseOf,join.bridge.RO_EXPRESSED)
        self.assertEqual(trial.static_sparql_oracle(raw,sub,reverse_only),set())

    def test_conflicting_unpinned_mapping_roles_refused(self):
        a,_=join.keyed_join(fixture_rows(2))
        a["anatomy"].add(("urn:fake-gene",str(join.bridge.GENEX.isExpressedIn),"urn:fake-target"))
        with self.assertRaises(ValueError):
            trial.original_join_graph(a)
        g,ro=sources()
        ro.remove((join.bridge.RO_EXPRESSED,OWL.inverseOf,join.bridge.RO_EXPRESSES))
        with self.assertRaises(ValueError):
            trial.source_axioms(g,ro)

    def test_full_sql_independent_source_join_matches_hypothetical_controls(self):
        a,events=join.keyed_join(fixture_rows(4))
        b,count=join.independent_sqlite_join(fixture_rows(4))
        self.assertEqual(a,b)
        self.assertEqual(count,4)
        self.assertEqual(events["source_positive_expression_rows"],4)

    @unittest.skipUnless(HAS_OWLRL,"dedicated source inference CI installs independent OWL RL")
    def test_every_shard_including_tail_is_complete_and_nonoverlapping(self):
        g,ro=sources()
        report=trial.evaluate(fixture_rows(5),g,ro,chunk_size=3)
        self.assertEqual(report["all_source_original_author_mapped_triples"],10)
        self.assertEqual(report["independent_static_SPARQL_consequences"],20)
        self.assertEqual(report["exhaustive_sharded_OWL_RL_consequences_verified"],20)
        self.assertEqual(report["actual_shard_count"],4)
        self.assertEqual(sum(s["source_edge_count"] for s in report["shards"]),10)
        self.assertEqual(sum(s["forward_and_inverse_entailed"] for s in report["shards"]),20)
        self.assertEqual(report["missing_OWL_RL_consequences"],0)
        self.assertFalse(report["full_unpartitioned_RO_OWL_RL_closure_measured"])
        self.assertFalse(report["official_NIH_benchmark"])

    @unittest.skipUnless(HAS_OWLRL,"dedicated source inference CI installs independent OWL RL")
    def test_predeclared_source_chunk_upper_bound_enforced(self):
        g,ro=sources()
        sub,inv=trial.source_axioms(g,ro)
        raw=trial.original_join_graph(join.keyed_join(fixture_rows(2))[0])
        expected=trial.static_sparql_oracle(raw,sub,inv)
        with self.assertRaises(ValueError):
            trial.sharded_owlrl_all(raw,expected,sub,inv,chunk_size=trial.CHUNK_SIZE+1)

    @unittest.skipUnless(HAS_OWLRL and ZIP and RO and CORE and AUTHOR,
                         "original author pinned archive and 5 original ontology/mapping files required")
    def test_all_authentic_source_relationships_are_verified_partitionwise(self):
        author={name:Path(AUTHOR)/name for name in join.bridge.FILES}
        result=trial.execute(Path(ZIP),author,{"ro-base.owl":Path(RO),"core.owl":Path(CORE)})
        self.assertEqual(result["schema"],trial.SCHEMA)
        self.assertEqual(result["original_source_positive_expression_rows"],19804)
        self.assertEqual(result["original_joined_positive_expression_rows"],19804)
        self.assertEqual(result["source_missing_genes"],0)
        self.assertEqual(result["source_missing_conditions"],0)
        self.assertEqual(result["original_source_anatomy_relationships"],5223)
        self.assertEqual(result["original_source_expression_condition_relationships"],19804)
        self.assertEqual(result["all_source_original_author_mapped_triples"],25027)
        self.assertEqual(result["independent_static_SPARQL_consequences"],50054)
        self.assertEqual(result["exhaustive_sharded_OWL_RL_consequences_verified"],50054)
        self.assertTrue(result["independent_full_SQL_source_mapping_agrees"])
        self.assertTrue(result["independent_static_full_RDFLib_SPARQL_agrees"])
        self.assertEqual(result["missing_OWL_RL_consequences"],0)
        self.assertFalse(result["full_unpartitioned_Bgee_plus_RO_OWL_RL_closure_measured"])
        self.assertTrue(result["equal_capacity_SQL_static_reasoning_is_comparator_not_lift"])
        self.assertFalse(result["official_NIH_benchmark"])
        self.assertFalse(result["original_W13_modified"])


if __name__=="__main__":
    unittest.main()
