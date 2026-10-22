"""E20 source RDFS type derivation: independent fixtures and refusal controls."""
from __future__ import annotations

import unittest
from rdflib import Graph,URIRef,RDF,RDFS
from systems.workspace import nih_p2_bgee_rdfs_type_witness_e20 as e20

GENE=URIRef("urn:e20:original-gene")
TARGET=URIRef("urn:e20:original-target")
OTHER=URIRef("urn:e20:outside-native-node")
P=URIRef("urn:e20:source-subproperty")
Q=URIRef("urn:e20:parent-property")
X=URIRef("urn:e20:domain-class")
X_PARENT=URIRef("urn:e20:domain-parent-class")
Y=URIRef("urn:e20:range-class")
V=URIRef("urn:e20:asserted-type")
V_PARENT=URIRef("urn:e20:asserted-type-parent")


def fixture():
    g=Graph()
    for t in [
        (P,RDFS.subPropertyOf,Q),
        (Q,RDFS.domain,X),
        (Q,RDFS.range,Y),
        (X,RDFS.subClassOf,X_PARENT),
        (V,RDFS.subClassOf,V_PARENT),
        (GENE,P,TARGET),
        (GENE,RDF.type,V),
        (OTHER,P,OTHER),
    ]:
        g.add(t)
    return g


class OriginalSourceRDFSTypeWitnessTests(unittest.TestCase):
    def test_genuine_direct_domain_range_property_and_class_ancestry(self):
        graph=fixture()
        sch=e20.direct_owner_schema(graph)
        expected,counts,sources=e20.explicit_rdfs_type_oracle(
            graph,set(),{GENE,TARGET},sch)
        self.assertEqual(expected,{
            (GENE,RDF.type,V),(GENE,RDF.type,V_PARENT),
            (GENE,RDF.type,X),(GENE,RDF.type,X_PARENT),
            (TARGET,RDF.type,Y)})
        self.assertEqual(sum(counts.values()),len(expected))
        self.assertIn("source_facts_considered",sources)
        self.assertNotIn((OTHER,RDF.type,X),expected)

    def test_four_rule_edge_could_supply_new_owner_domain_witness(self):
        graph=fixture()
        graph.remove((GENE,P,TARGET))
        sch=e20.direct_owner_schema(graph)
        extra={(GENE,Q,TARGET)}
        witnessed,_,_=e20.explicit_rdfs_type_oracle(graph,extra,{GENE,TARGET},sch)
        self.assertIn((GENE,RDF.type,X),witnessed)
        self.assertIn((TARGET,RDF.type,Y),witnessed)

    def test_no_original_property_hierarchy_disables_inherited_witness(self):
        graph=fixture()
        graph.remove((P,RDFS.subPropertyOf,Q))
        witnessed,_,_=e20.explicit_rdfs_type_oracle(
            graph,set(),{GENE,TARGET},e20.direct_owner_schema(graph))
        self.assertNotIn((GENE,RDF.type,X),witnessed)
        self.assertNotIn((TARGET,RDF.type,Y),witnessed)
        self.assertIn((GENE,RDF.type,V_PARENT),witnessed)

    def test_residual_type_is_visible_not_falsely_claimed_explained(self):
        graph=fixture()
        witnessed,support,provenance=e20.explicit_rdfs_type_oracle(
            graph,set(),{GENE,TARGET},e20.direct_owner_schema(graph))
        original={(GENE,RDF.type,V)}
        unexplained=(GENE,RDF.type,URIRef("urn:e20:OWL-RL-only-class"))
        full=witnessed|{unexplained}
        output=e20.compare_types(original,full,witnessed,support,provenance)
        self.assertEqual(output["full_profile_type_residual_not_justified_by_this_limited_oracle"],1)
        self.assertEqual(output["independently_RDFS_supported_inferred_type_statements"],4)
        self.assertTrue(output["source_domain_range_oracle_not_full_OWL_RL"])
        self.assertFalse(output["official_NIH_scored"])

    def test_missing_independent_rdfs_candidate_must_fail(self):
        graph=fixture()
        witnessed,support,provenance=e20.explicit_rdfs_type_oracle(
            graph,set(),{GENE,TARGET},e20.direct_owner_schema(graph))
        original={(GENE,RDF.type,V)}
        with self.assertRaisesRegex(ValueError,"candidate missing"):
            e20.compare_types(original,original,witnessed,support,provenance)

    def test_unauthenticated_original_type_cannot_be_invented(self):
        graph=fixture()
        witnessed,support,provenance=e20.explicit_rdfs_type_oracle(
            graph,set(),{GENE,TARGET},e20.direct_owner_schema(graph))
        with self.assertRaisesRegex(ValueError,"original owner RDF types disappeared"):
            e20.compare_types({(OTHER,RDF.type,V)},witnessed,witnessed,support,provenance)

    def test_cyclic_source_subclass_ancestry_is_finite(self):
        graph=fixture()
        graph.add((X_PARENT,RDFS.subClassOf,X))
        sch=e20.direct_owner_schema(graph)
        result,_,_=e20.explicit_rdfs_type_oracle(graph,set(),{GENE,TARGET},sch)
        self.assertLess(len(result),20)
        self.assertIn((GENE,RDF.type,X_PARENT),result)

    def test_independent_native_schema_and_sparql_source_inputs_agree(self):
        original=fixture()
        schema=e20.direct_owner_schema(original)
        self.assertEqual(len(schema[str(RDFS.subPropertyOf)]),1)
        self.assertEqual(len(schema[str(RDFS.subClassOf)]),2)
        self.assertEqual(len(schema[str(RDFS.domain)]),1)
        self.assertEqual(len(schema[str(RDFS.range)]),1)


    def test_e21_partition_source_role_and_residual_accounting(self):
        original={(GENE,RDF.type,V)}
        full=original|{(GENE,RDF.type,X),(TARGET,RDF.type,Y),(TARGET,RDF.type,X)}
        oracle=original|{(GENE,RDF.type,X),(TARGET,RDF.type,Y)}
        result=e20.original_role_type_partition(original,full,oracle,{GENE},{TARGET})
        genes=result["role_partition"]["original_gene_role"]
        targets=result["role_partition"]["original_target_role"]
        self.assertEqual((genes["full_profile_inferred_type_statements"],
                          genes["limited_RDFS_supported_inferred"],
                          genes["remaining_not_explained_by_limited_RDFS"]), (1,1,0))
        self.assertEqual((targets["full_profile_inferred_type_statements"],
                          targets["limited_RDFS_supported_inferred"],
                          targets["remaining_not_explained_by_limited_RDFS"]), (2,1,1))
        self.assertFalse(result["new_biological_type_annotations_inferred"])

    def test_e21_rejects_overlapping_roles_and_unmapped_original_node(self):
        original={(GENE,RDF.type,V)}
        with self.assertRaisesRegex(ValueError,"overlap"):
            e20.original_role_type_partition(original,original,original,{GENE},{GENE})
        with self.assertRaisesRegex(ValueError,"unmapped"):
            e20.original_role_type_partition(original|{(OTHER,RDF.type,X)},
                                             original|{(OTHER,RDF.type,X)},
                                             original,{GENE},{TARGET})



    def test_e22_class_type_inventory_partitions_every_residual(self):
        owl=URIRef("http://www.w3.org/2002/07/owl#Thing")
        obo=URIRef("http://purl.obolibrary.org/obo/RO_0000001")
        original={(GENE,RDF.type,V)}
        full=original|{(GENE,RDF.type,owl),(TARGET,RDF.type,owl),
                       (GENE,RDF.type,obo)}
        result=e20.residual_type_class_inventory(original,full,original)
        self.assertEqual(result["original_full_profile_limited_oracle_residual_count"],3)
        self.assertEqual(result["source_class_namespace_counts"]["OWL_vocabulary"],2)
        self.assertEqual(result["source_class_namespace_counts"]["source_OBO_URI"],1)
        self.assertTrue(result["class_namespace_is_not_inference_rule_provenance"])

    def test_e22_missing_independent_source_type_not_reported_as_residual(self):
        with self.assertRaisesRegex(ValueError,"missing"):
            e20.residual_type_class_inventory(
                {(GENE,RDF.type,V)},set(),{(GENE,RDF.type,V)})

if __name__=="__main__":
    unittest.main()
