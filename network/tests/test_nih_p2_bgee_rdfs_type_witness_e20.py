"""E20 source RDFS type derivation: independent fixtures and refusal controls."""
from __future__ import annotations

import unittest
from rdflib import Graph,URIRef,RDF,RDFS,BNode
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
        self.assertEqual(result["source_class_term_family_counts"]["OWL_vocabulary"],2)
        self.assertEqual(result["source_class_term_family_counts"]["source_OBO_URI"],1)
        self.assertTrue(result["class_term_counts_are_not_inference_rule_provenance"])

    def test_e22_missing_independent_source_type_not_reported_as_residual(self):
        with self.assertRaisesRegex(ValueError,"missing"):
            e20.residual_type_class_inventory(
                {(GENE,RDF.type,V)},set(),{(GENE,RDF.type,V)})


    def test_e22_anonymous_class_identity_never_exported_as_persistent_URI(self):
        a,b=BNode("first-native-anon"),BNode("second-native-anon")
        other={(GENE,RDF.type,a),(TARGET,RDF.type,a),(GENE,RDF.type,b)}
        r=e20.residual_type_class_inventory(set(),other,set())
        self.assertEqual(r["distinct_anonymous_blank_node_class_terms"],2)
        self.assertEqual(r["anonymous_blank_node_class_statement_counts"],[1,2])
        self.assertEqual(r["source_class_term_family_counts"]
                         ["anonymous_RDF_blank_node_class_term"],3)
        self.assertEqual(r["top_named_class_URI_counts"],[])
        self.assertTrue(r["anonymous_blank_node_labels_not_persistent_identifiers"])


    def test_e23_source_owned_anonymous_class_and_inferred_only_separate(self):
        from rdflib.namespace import OWL
        owned=BNode("original-restriction")
        invented=BNode("inferred-only")
        graph=Graph()
        graph.add((owned,RDF.type,OWL.Restriction))
        graph.add((owned,OWL.onProperty,P))
        residual={(GENE,RDF.type,owned),(TARGET,RDF.type,owned),
                  (GENE,RDF.type,invented)}
        result=e20.original_anonymous_class_premise_census(
            graph,set(),residual,set())
        self.assertEqual(result["anonymous_class_terms_total"],2)
        self.assertEqual(result["anonymous_class_terms_present_in_original_owner_graph"],1)
        self.assertEqual(result["anonymous_class_terms_absent_from_original_owner_graph"],1)
        self.assertEqual(result["direct_source_owl_restriction_class_terms"],1)
        self.assertEqual(result["direct_source_owl_onProperty_class_terms"],1)
        self.assertEqual(sum(x["residual_original_node_type_statements"]
                             for x in result["structural_groups"]),3)
        self.assertFalse(result["blank_node_labels_exported"])

    def test_e23_cannot_promote_missing_restricted_type_witness(self):
        with self.assertRaisesRegex(ValueError,"not contained"):
            e20.original_anonymous_class_premise_census(
                Graph(),set(),set(),{(GENE,RDF.type,V)})


    def test_e24_source_anonymous_restrictions_and_intersections_fingerprinted(self):
        from rdflib.namespace import OWL
        r=BNode("r"),BNode("i")
        # Synthetic fixture only; source-connected CI reauthenticates owners.
        graph=Graph()
        graph.add((r[0],RDF.type,OWL.Restriction))
        graph.add((r[0],OWL.onProperty,P))
        graph.add((r[0],OWL.someValuesFrom,X))
        graph.add((r[1],OWL.intersectionOf,BNode("rdf-list")))
        result=e20.original_anonymous_constructor_fingerprint(
            graph,set(),{(GENE,RDF.type,r[0]),(TARGET,RDF.type,r[0]),
                         (GENE,RDF.type,r[1])},set())
        self.assertEqual(result["original_anonymous_class_term_count"],2)
        self.assertEqual(result["original_anonymous_type_statement_count"],3)
        self.assertEqual(sum(k["anonymous_class_term_count"]
                             for k in result["source_constructor_profiles"]),2)
        self.assertEqual(sum(k["residual_original_node_type_statements"]
                             for k in result["source_constructor_profiles"]),3)
        profiles=result["source_constructor_profiles"]
        self.assertTrue(any("someValuesFrom" in p["original_author_predicate_features"] for p in profiles))
        self.assertTrue(any("intersectionOf" in p["original_author_predicate_features"] for p in profiles))
        self.assertFalse(result["bnode_identifiers_or_raw_owner_triples_exported"])

    def test_e24_rejects_missing_source_oracle_statement(self):
        with self.assertRaisesRegex(ValueError,"boundary changed"):
            e20.original_anonymous_constructor_fingerprint(
                Graph(),set(),set(),{(GENE,RDF.type,V)})

if __name__=="__main__":
    unittest.main()
