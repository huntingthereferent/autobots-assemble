"""Independent finite RDFS property ancestry evidence on author-owned Bgee semantics."""
from __future__ import annotations

from rdflib import Graph, URIRef, RDFS
import os
from pathlib import Path
import unittest
from systems.workspace import nih_p2_bgee_original_property_ancestry as trial
from systems.workspace import nih_p2_author_genex_bgee_ro_mapping_gate as bridge
from systems.workspace import nih_p2_original_bgee_real_expression_join as bgee

RO=os.environ.get("NIH_ORIGINAL_RO_BASE_OWL")
CORE=os.environ.get("NIH_ORIGINAL_RO_CORE_OWL")
AUTHOR=os.environ.get("NIH_ORIGINAL_BGEE_SOURCE_DIR")
ARCHIVE=os.environ.get("NIH_ORIGINAL_BGEE_POSTGRES_ZIP")
ROOT=bridge.GENEX.isExpressedIn
SUPER=URIRef("urn:nih:source-original-finite-rdfs-fixture:super")


def fixture():
    author=Graph()
    ro=Graph()
    author.add((ROOT,RDFS.subPropertyOf,bridge.RO_EXPRESSED))
    ro.add((bridge.RO_EXPRESSED,RDFS.subPropertyOf,SUPER))
    mapped={"anatomy":set(),"expression_condition":set()}
    for kind,triple in bgee.construct_edges("GENE123","CONDITION123","UBERON:0000955"):
        mapped[kind].add(triple)
    return mapped,author,ro


class OriginalBgeePropertyAncestryTests(unittest.TestCase):
    def test_two_ancestor_chain_independent_graph_traversal_and_sparql(self):
        m,a,r=fixture()
        result=trial.evaluate(m,a,r)
        self.assertEqual(result["original_mapped_Bgee_expression_assertions"],2)
        self.assertEqual(result["source_owned_named_superproperty_ancestors"],2)
        self.assertEqual(result["independent_SPARQL_named_superproperty_ancestors"],2)
        self.assertEqual(result["additional_hierarchy_entailed_statements_beyond_RO_expressed_in"],2)
        self.assertEqual(result["inherited_Bgee_properties_directly_or_indirectly"],4)
        self.assertEqual(len(result["full_named_property_hierarchy_source_declarations"][str(SUPER)]["original_source_minimal_property_chain"]),2)
        self.assertFalse(result["full_original_OWL_RL_reasoner_ran"])

    def test_no_additional_parent_keeps_source_only_known_property(self):
        m,a,r=fixture()
        r.remove((bridge.RO_EXPRESSED,RDFS.subPropertyOf,SUPER))
        result=trial.evaluate(m,a,r)
        self.assertEqual(result["source_owned_named_superproperty_ancestors"],1)
        self.assertEqual(result["source_owned_named_additional_properties_beyond_expressed_in"],0)
        self.assertEqual(result["additional_hierarchy_entailed_statements_beyond_RO_expressed_in"],0)

    def test_missing_original_genex_semantic_link_fails(self):
        m,a,r=fixture()
        a.remove((ROOT,RDFS.subPropertyOf,bridge.RO_EXPRESSED))
        with self.assertRaises(ValueError):
            trial.evaluate(m,a,r)

    def test_property_cycle_does_not_manufacture_a_self_ancestor(self):
        m,a,r=fixture()
        r.add((SUPER,RDFS.subPropertyOf,ROOT))
        result=trial.evaluate(m,a,r)
        self.assertEqual(result["source_owned_named_superproperty_ancestors"],2)
        self.assertNotIn(str(ROOT),result["full_named_property_hierarchy_source_declarations"])

    def test_wrong_gene_expression_mapping_predicate_fails(self):
        m,a,r=fixture()
        m["anatomy"].add(("urn:unverified",str(ROOT),"urn:unsupported-anatomy"))
        with self.assertRaises(ValueError):
            trial.evaluate(m,a,r)

    def test_wrong_schema_argument_type_cannot_be_silently_accepted(self):
        with self.assertRaises(AttributeError):
            trial.traverse_source_property_ancestors(None)

    @unittest.skipUnless(ARCHIVE and AUTHOR and RO and CORE,
                         "requires full immutable original Bgee and RO ontology source files")
    def test_authenticated_original_named_RDFS_hierarchy_all_edges(self):
        authors={name:Path(AUTHOR)/name for name in bridge.FILES}
        result=trial.execute(Path(ARCHIVE),authors,{"ro-base.owl":Path(RO),"core.owl":Path(CORE)})
        self.assertEqual(result["schema"],trial.SCHEMA)
        self.assertEqual(result["original_mapped_Bgee_expression_assertions"],25027)
        self.assertEqual(result["original_Bgee_positive_expression_rows"],19804)
        self.assertEqual(result["original_Bgee_unmatched_genes"],0)
        self.assertEqual(result["original_Bgee_unmatched_conditions"],0)
        self.assertEqual(result["source_owned_named_superproperty_ancestors"],
                         result["independent_SPARQL_named_superproperty_ancestors"])
        self.assertTrue(result["entire_original_named_RDFS_property_ancestry_independently_verified"])
        self.assertTrue(result["all_reported_source_provenance_verified"])
        self.assertFalse(result["official_NIH_benchmark"])


if __name__=="__main__":
    unittest.main()
