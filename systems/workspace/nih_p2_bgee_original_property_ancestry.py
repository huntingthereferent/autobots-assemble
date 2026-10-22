"""Original Bgee relationship -> full original RO named superproperty ancestry.

Source scope: complete author-original Bgee SQL rows and GenEx + whole two-file
RO ontology. An independent iterative URI traversal and RDFLib SPARQL
property path must agree on *all* named parent properties of
genex:isExpressedIn. Every inherited gene-expression triple is a logical
consequence of the attested source predicates, NOT an independent measurement,
biomedical treatment claim, OWL DL proof, or static-baseline improvement.

This is separate from inverse-rule testing and does not manufacture data
when no additional original named ancestor property exists.
"""
from __future__ import annotations

import argparse
from collections import deque
from hashlib import sha256
import json
from pathlib import Path

from rdflib import Graph, URIRef, RDFS
from . import nih_p2_author_genex_bgee_ro_mapping_gate as bridge
from . import nih_p2_original_bgee_real_expression_join as bgee
from . import nih_p2_bgee_exhaustive_sharded_owlrl as former

SCHEMA="nih-p2-bgee-original-inherited-ro-property-hierarchy-v1"
MAX_ANCESTORS=40
MAX_AUTHENTIC_SOURCE_EDGES=30000
MAX_INHERITED_INFERENCES=1100000
SPARQL_ANCESTORS="""PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?ancestor WHERE {
  <http://purl.org/genex#isExpressedIn> rdfs:subPropertyOf+ ?ancestor .
  FILTER(isIRI(?ancestor))
}"""


def named_property_edges(graph):
    return {(s,o) for s,o in graph.subject_objects(RDFS.subPropertyOf)
            if isinstance(s,URIRef) and isinstance(o,URIRef)}


def traverse_source_property_ancestors(ontology):
    """Handwritten BFS with owner-source edge witnesses; never calls SPARQL."""
    root=bridge.GENEX.isExpressedIn
    graph_edges=named_property_edges(ontology)
    adjacency={}
    for child,parent in graph_edges:
        adjacency.setdefault(child,set()).add(parent)
    queue=deque([root])
    visited={root}
    witness={}
    while queue:
        current=queue.popleft()
        for parent in sorted(adjacency.get(current,set()),key=str):
            if parent==root:
                continue
            if parent not in visited:
                if len(visited)>MAX_ANCESTORS:
                    raise ValueError("original named property ancestry exceeds bounded scan")
                witness[parent]=(current,parent)
                visited.add(parent)
                queue.append(parent)
    return visited-{root},witness,graph_edges


def independent_sparql_ancestors(ontology):
    ans={row[0] for row in ontology.query(SPARQL_ANCESTORS)
         if isinstance(row[0],URIRef)}
    ans.discard(bridge.GENEX.isExpressedIn)
    return ans


def chained_witness(ancestor,witness,graph_edges):
    current=ancestor
    chain=[]
    for _ in range(MAX_ANCESTORS+1):
        if current==bridge.GENEX.isExpressedIn:
            chain.reverse()
            return chain
        if current not in witness:
            raise ValueError("original source property source-edge chain missing")
        child,parent=witness[current]
        if (child,parent) not in graph_edges:
            raise ValueError("original source witness edge not asserted")
        chain.append((str(child),str(RDFS.subPropertyOf),str(parent)))
        current=child
    raise ValueError("source property witness exceeds finite chain bound")


def inherited_edges(source_edges,ancestors):
    if len(source_edges)>MAX_AUTHENTIC_SOURCE_EDGES:
        raise ValueError("original mapped relationships over finite size limit")
    if len(ancestors)>MAX_ANCESTORS:
        raise ValueError("independent original graph ancestry over finite size limit")
    if len(source_edges)*len(ancestors)>MAX_INHERITED_INFERENCES:
        raise ValueError("complete inherited result set exceeds finite limit")
    out=set()
    for s,p,o in source_edges:
        if p!=bridge.GENEX.isExpressedIn:
            raise ValueError("original Bgee RDF assertion predicate unexpectedly changed")
        for ancestor in ancestors:
            out.add((s,ancestor,o))
    if len(out)!=len(source_edges)*len(ancestors):
        raise ValueError("source-derived ancestor consequences collide unexpectedly")
    return out


def evaluate(original_edges,original_genex,original_ro):
    merged=Graph()
    merged += original_genex
    merged += original_ro
    bgee_edges=former.original_join_graph(original_edges)
    manual,witness,source_schema_edges=traverse_source_property_ancestors(merged)
    independent=independent_sparql_ancestors(merged)
    if manual!=independent:
        raise ValueError("manual original-source property BFS disagrees with independent RDFLib SPARQL property path: "
                         +repr({"manual_only":len(manual-independent),
                                "sparql_only":len(independent-manual)}))
    if bridge.RO_EXPRESSED not in manual:
        raise ValueError("author-defined source GenEx to RO expressed-in relation absent")
    entailed=inherited_edges(bgee_edges,manual)
    receipts={}
    for property in sorted(manual,key=str):
        chain=chained_witness(property,witness,source_schema_edges)
        receipts[str(property)]={
            "named_superproperty":str(property),
            "original_source_minimal_property_chain":chain,
            "original_source_property_chain_sha256":sha256(
                "\n".join("|".join(t) for t in chain).encode()).hexdigest(),
            "independent_SPARQL_named_ancestor_confirmed":True,
            "inherited_original_Bgee_assertions_for_this_ancestor":len(bgee_edges),
        }
    extra_ancestors=manual-{bridge.RO_EXPRESSED}
    return {
        "schema":SCHEMA,
        "original_mapped_Bgee_expression_assertions":len(bgee_edges),
        "original_named_source_property_subPropertyOf_axioms":len(source_schema_edges),
        "source_owned_named_superproperty_ancestors":len(manual),
        "independent_SPARQL_named_superproperty_ancestors":len(independent),
        "source_owned_named_additional_properties_beyond_expressed_in":len(extra_ancestors),
        "full_named_property_hierarchy_source_declarations":receipts,
        "inherited_Bgee_properties_directly_or_indirectly":len(entailed),
        "original_inherited_RDF_triples_SHA256":former.digest_set(entailed),
        "original_direct_RO_expressed_in_consequences":len(bgee_edges),
        "additional_hierarchy_entailed_statements_beyond_RO_expressed_in":
              len(bgee_edges)*len(extra_ancestors),
        "source_hierarchy_is_not_independently_measured_biomedical_observations":True,
        "entire_original_named_RDFS_property_ancestry_independently_verified":True,
        "full_original_OWL_RL_reasoner_ran":False,
        "source_only_hierarchy_does_not_prove_clinical_efficacy":True,
        "original_patient_level_records_used":False,
        "clinical_valid_at_and_first_public_time":"NOT_MEASURED",
        "official_NIH_benchmark":False,
        "original_W13_modified":False,
    }


def execute(zip_path,author_files,ro_files):
    gate=bridge.examine(author_files,ro_files)
    records,census=bgee.source_tables(zip_path)
    direct,events=bgee.keyed_join(records)
    sql,sql_n=bgee.independent_sqlite_join(records)
    if direct!=sql or sql_n!=19804:
        raise ValueError("actual original Bgee data rows changed or full SQL baseline differs")
    genex=Graph().parse(data=Path(author_files["bgee_v14_genex.owl"]).read_bytes(),format="turtle")
    ro,ro_receipts,_=bridge.source.admit_sources(ro_files)
    results=evaluate(direct,genex,ro)
    if results["original_mapped_Bgee_expression_assertions"]!=25027:
        raise ValueError("frozen whole original Bgee source inference coverage changed")
    results.update({
        "original_Bgee_author_archive_git_blob":census["complete_original_source_git_blob_sha1"],
        "original_Bgee_positive_expression_rows":events.get("source_positive_expression_rows",0),
        "original_Bgee_unmatched_genes":events.get("unmatched_gene",0),
        "original_Bgee_unmatched_conditions":events.get("unmatched_condition",0),
        "original_author_mapping_commit":bridge.COMMIT,
        "original_relation_ontology_source_commit":bridge.source.COMMIT,
        "whole_immutable_original_RO_source_receipts":ro_receipts,
        "original_author_mapping_files_validated":len(gate["author_R2RML_mappings"])==2,
        "all_reported_source_provenance_verified":True,
    })
    return results


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--archive",type=Path,required=True)
    for name in ("obda","owl","r2rml","ro-base","core","output"):
        a.add_argument("--"+name,type=Path,required=True)
    c=a.parse_args()
    authors={"bgee_v14_genex."+k:getattr(c,k) for k in ("obda","owl","r2rml")}
    report=execute(c.archive,authors,{"ro-base.owl":c.ro_base,"core.owl":c.core})
    c.output.parent.mkdir(parents=True,exist_ok=True)
    c.output.write_text(json.dumps(report,indent=2,sort_keys=True)+chr(10))
    print(json.dumps({k:report[k] for k in (
        "original_mapped_Bgee_expression_assertions",
        "original_named_source_property_subPropertyOf_axioms",
        "source_owned_named_superproperty_ancestors",
        "source_owned_named_additional_properties_beyond_expressed_in",
        "inherited_Bgee_properties_directly_or_indirectly",
        "additional_hierarchy_entailed_statements_beyond_RO_expressed_in",
    )},sort_keys=True))


if __name__=="__main__":
    main()
