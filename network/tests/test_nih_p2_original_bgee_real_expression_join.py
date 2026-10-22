"""Independent Bgee original expression joins, negative controls and OWL RL."""
from __future__ import annotations
import importlib.util
import os
from pathlib import Path
import unittest
from rdflib import Graph,RDFS,OWL

from systems.workspace import nih_p2_original_bgee_real_expression_join as trial

HAS_OWLRL=importlib.util.find_spec("owlrl") is not None
RO=os.environ.get("NIH_ORIGINAL_RO_BASE_OWL")
CORE=os.environ.get("NIH_ORIGINAL_RO_CORE_OWL")
AUTHOR=os.environ.get("NIH_ORIGINAL_BGEE_SOURCE_DIR")
ZIP=os.environ.get("NIH_ORIGINAL_BGEE_POSTGRES_ZIP")


def sample_rows():
    return {
      "gene":[("bgee-1","GENE_12"),("bgee-2","GENE_14")],
      "globalcond":[("cond1","UBERON:0000955"),("cond2","UBERON:0000956")],
      "globalexpression":[
          ("x1","bgee-1","cond1","EXPRESSED"),
          ("x2","bgee-1","cond2","NOT_EXPRESSED"),
          ("x3","bgee-2","cond2","EXPRESSED"),
          ("x4","bgee-9","cond1","EXPRESSED")]
    }


class RealBgeeOriginalJoinTests(unittest.TestCase):
    def test_original_record_key_join_matches_independent_sql(self):
        rows=sample_rows()
        d,stats=trial.keyed_join(rows)
        static,n=trial.independent_sqlite_join(rows)
        self.assertEqual(d,static)
        self.assertEqual(stats["source_positive_expression_rows"],3)
        self.assertEqual(stats["unmatched_gene"],1)
        self.assertEqual(stats["joined_positive_rows"],2)
        self.assertEqual(n,2)
        self.assertEqual(len(d["anatomy"]),2)
        self.assertEqual(len(d["expression_condition"]),2)

    def test_not_expressed_and_missing_gene_do_not_enter_ground_inference(self):
        rows=sample_rows()
        d,_=trial.keyed_join(rows)
        self.assertFalse(any("0000956" in e[2] and "GENE_12" in e[0]
                             for e in d["anatomy"]))
        self.assertFalse(any("bgee-9" in e[0] for e in d["anatomy"]))

    def test_duplicate_key_with_conflicting_anatomy_refused(self):
        rows=sample_rows()
        rows["globalcond"].append(("cond1","UBERON:3333333"))
        with self.assertRaises(ValueError):
            trial.keyed_join(rows)

    def test_unsafe_gene_uri_from_original_data_refused(self):
        rows=sample_rows()
        rows["gene"][0]=("bgee-1","Gene id with whitespace")
        with self.assertRaises(ValueError):
            trial.keyed_join(rows)

    def test_independent_sqlite_negative_missing_join(self):
        rows=sample_rows()
        rows["globalcond"].clear()
        d,counts=trial.keyed_join(rows)
        sql,n=trial.independent_sqlite_join(rows)
        self.assertEqual(d,sql)
        self.assertEqual(n,0)
        self.assertEqual(counts["unmatched_condition"],2)

    @unittest.skipUnless(HAS_OWLRL,"optional OWL RL reasoner required")
    def test_fixture_source_bridge_withheld_inverse_has_no_false_positive(self):
        graph=Graph()
        graph.add((trial.bridge.GENEX.isExpressedIn,RDFS.subPropertyOf,trial.bridge.RO_EXPRESSED))
        empty=Graph()
        edges,counts=trial.keyed_join(sample_rows())
        with self.assertRaises(ValueError):
            trial.bounded_source_owlrl(edges,graph,empty)

    @unittest.skipUnless(HAS_OWLRL,"optional OWL RL reasoner required")
    def test_bounded_source_rule_checker_positive_fixture_with_24_realistic_tuples(self):
        graph=Graph()
        graph.add((trial.bridge.GENEX.isExpressedIn,RDFS.subPropertyOf,trial.bridge.RO_EXPRESSED))
        ro=Graph()
        ro.add((trial.bridge.RO_EXPRESSED,OWL.inverseOf,trial.bridge.RO_EXPRESSES))
        data={"anatomy":set(),"expression_condition":set()}
        for n in range(24):
            for kind,edge in trial.construct_edges("GENE"+str(n),"COND"+str(n),"UBERON:0000955"):
                data[kind].add(edge)
        proofs,materialized=trial.bounded_source_owlrl(data,graph,ro)
        self.assertEqual(len(proofs),48)
        self.assertGreater(materialized,48)

    @unittest.skipUnless(HAS_OWLRL and ZIP and RO and CORE and AUTHOR,
                         "whole original author Bgee archive and ontology owner files required")
    def test_genuine_original_author_data_full_join_and_source_rule_sample(self):
        author={name:Path(AUTHOR)/name for name in trial.bridge.FILES}
        result=trial.execute(Path(ZIP),author,{"ro-base.owl":Path(RO),"core.owl":Path(CORE)})
        self.assertEqual(result["schema"],trial.SCHEMA)
        self.assertEqual(result["original_positive_expression_call_rows"],19804)
        self.assertGreaterEqual(result["source_unmatched_gene_rows"],0)
        self.assertGreaterEqual(result["source_unmatched_condition_rows"],0)
        self.assertEqual(result["real_source_ground_OWL_RL_edges_tested"],48)
        self.assertTrue(result["original_complete_source_key_join_matches_independent_SQL"])
        self.assertTrue(result["actual_source_relationships_not_trial_synthetic"])
        self.assertFalse(result["official_NIH_benchmark"])
        self.assertFalse(result["original_W13_modified"])


if __name__=="__main__":
    unittest.main()
