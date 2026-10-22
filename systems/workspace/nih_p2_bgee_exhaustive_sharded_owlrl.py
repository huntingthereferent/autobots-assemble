"""Exhaustive original Bgee GenEx -> RO rule verification in finite OWL RL shards.

Read-only authentic sources:
 * Git-blob-pinned Bgee tutorial SQL archive and three author mapping files;
 * whole-SHA-256-pinned independent Relations Ontology original release.

All distinct author-generated Bgee gene/anatomy and gene/condition RDF edges
are compared to two independent full-source baselines: SQLite joined records
and RDFLib SPARQL CONSTRUCT of the exact original source-owned schema rules.
Every original edge is then exercised once in OWL RL over a bounded *minimal
source-owned rule subgraph*. This proves exhaustive per-edge consequences
under those two rules, NOT a monolithic/full RO+GenEx+data OWL RL closure,
OWL DL consistency, independent medical truth or superiority to static SQL.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from rdflib import Graph, URIRef, RDFS, OWL
from . import nih_p2_original_bgee_real_expression_join as earlier
from . import nih_p2_author_genex_bgee_ro_mapping_gate as bridge

SCHEMA="nih-p2-original-bgee-exhaustive-sharded-owlrl-v1"
CHUNK_SIZE=2048
SOURCE_EDGE_LIMIT=30000
FIXED_SOURCE_ANATOMY=5223
FIXED_SOURCE_CONDITION=19804
PREVIEW=12
CONSTRUCT_QUERY="""PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
CONSTRUCT {
 ?gene <http://purl.obolibrary.org/obo/RO_0002206> ?place .
 ?place <http://purl.obolibrary.org/obo/RO_0002292> ?gene .
}
WHERE {
  <http://purl.org/genex#isExpressedIn>
    rdfs:subPropertyOf <http://purl.obolibrary.org/obo/RO_0002206> .
  <http://purl.obolibrary.org/obo/RO_0002206>
    owl:inverseOf <http://purl.obolibrary.org/obo/RO_0002292> .
  ?gene <http://purl.org/genex#isExpressedIn> ?place .
  FILTER(isIRI(?gene) && isIRI(?place))
}"""


def source_axioms(author,ro):
    sub=(bridge.GENEX.isExpressedIn,RDFS.subPropertyOf,bridge.RO_EXPRESSED)
    inverse=(bridge.RO_EXPRESSED,OWL.inverseOf,bridge.RO_EXPRESSES)
    if sub not in author or inverse not in ro:
        raise ValueError("exact original owner source-only schema axioms unavailable")
    return sub,inverse


def original_join_graph(by_kind):
    if set(by_kind)!={"anatomy","expression_condition"}:
        raise ValueError("both independent Bgee original source mapping branches required")
    tuples=by_kind["anatomy"] | by_kind["expression_condition"]
    if not tuples or len(tuples)>SOURCE_EDGE_LIMIT:
        raise ValueError("empty source rows or source-owned finite bound exceeded")
    if sum(len(v) for v in by_kind.values())!=len(tuples):
        raise ValueError("one original RDF triple has overlapping mapping categories")
    triples=set()
    for s,p,o in tuples:
        if not isinstance(s,str) or not isinstance(p,str) or not isinstance(o,str):
            raise ValueError("typed original source RDF term missing")
        if p!=str(bridge.GENEX.isExpressedIn) or not s.startswith(
            "http://omabrowser.org/ontology/oma#GENE_"):
            raise ValueError("unapproved foreign predicate or original gene node")
        if not (o.startswith("http://purl.obolibrary.org/obo/") or
                o.startswith("http://bgee.org/#EXPRESSION_CONDITION_")):
            raise ValueError("unapproved original object template")
        triples.add((URIRef(s),URIRef(p),URIRef(o)))
    return triples


def direct_entailed(original):
    """A two-rule oracle written without SPARQL, SQL or OWL RL."""
    expected=set()
    for s,p,o in original:
        if p!=bridge.GENEX.isExpressedIn:
            raise ValueError("raw original foreign predicate")
        expected.add((s,bridge.RO_EXPRESSED,o))
        expected.add((o,bridge.RO_EXPRESSES,s))
    if len(expected)!=2*len(original):
        raise ValueError("original RDF edges collide under reverse/forward rule")
    return expected


def static_sparql_oracle(original,sub,inverse):
    graph=Graph()
    graph.add(sub)
    graph.add(inverse)
    for t in original:
        graph.add(t)
    return set(graph.query(CONSTRUCT_QUERY).graph)


def source_sort_key(t):
    return (sha256(("|".join(map(str,t))+"|original-Bgee-exhaustive-v1").encode()).hexdigest(),
            tuple(map(str,t)))


def digest_set(triples):
    ordered=sorted("|".join(map(str,t)) for t in triples)
    return sha256(("\n".join(ordered)+"\n").encode()).hexdigest()


def sharded_owlrl_all(original,independent,sub,inverse,*,chunk_size=CHUNK_SIZE):
    from owlrl import DeductiveClosure,OWLRL_Semantics
    if not 1<=chunk_size<=CHUNK_SIZE:
        raise ValueError("OWLRL finite shard bound exceeded")
    rows=sorted(original,key=source_sort_key)
    verified=set()
    partitions=[]
    for off in range(0,len(rows),chunk_size):
        batch=rows[off:off+chunk_size]
        g=Graph()
        g.add(sub)
        g.add(inverse)
        for triple in batch:
            g.add(triple)
        DeductiveClosure(OWLRL_Semantics,rdfs_closure=True).expand(g)
        required=direct_entailed(batch)
        missing=required-set(g)
        if missing:
            raise ValueError("OWL RL missing original source-ground inference at shard "+str(off//chunk_size)
                             +": "+repr([list(map(str,t)) for t in sorted(missing,
                                              key=lambda t:tuple(map(str,t)))[:3]]))
        if not required.issubset(independent):
            raise ValueError("independent static whole-source oracle disagrees with this shard")
        if required & verified:
            raise ValueError("overlapping inference proof across frozen shards")
        verified.update(required)
        partitions.append({
            "shard_index":len(partitions),
            "source_edge_count":len(batch),
            "source_row_sha256":digest_set(batch),
            "forward_and_inverse_entailed":len(required),
            "reasoner_finite_materialized_triples":len(g),
            "missing_owlrl_consequences":0,
            "source_minimal_ontology_axioms":2,
        })
    if verified!=independent:
        raise ValueError("sharded OWL RL source coverage does not equal full independent static oracle")
    return verified,partitions


def evaluate(rows,author,ro,*,chunk_size=CHUNK_SIZE):
    sub,inverse=source_axioms(author,ro)
    direct,events=earlier.keyed_join(rows)
    static_sql,sql_rows=earlier.independent_sqlite_join(rows)
    if direct!=static_sql:
        raise ValueError("full original source direct join disagrees with independent SQLite")
    raw=original_join_graph(direct)
    expected=direct_entailed(raw)
    static_rdf=static_sparql_oracle(raw,sub,inverse)
    if expected!=static_rdf:
        raise ValueError("full original Bgee RDFLib static source-owned SPARQL differs: "+
                         repr({"direct":len(expected),"static":len(static_rdf),
                               "only_direct":len(expected-static_rdf),
                               "only_static":len(static_rdf-expected)}))
    found,shards=sharded_owlrl_all(raw,static_rdf,sub,inverse,chunk_size=chunk_size)
    return {
        "schema":SCHEMA,
        "original_source_positive_expression_rows":events.get("source_positive_expression_rows",0),
        "original_joined_positive_expression_rows":events.get("joined_positive_rows",0),
        "source_missing_genes":events.get("unmatched_gene",0),
        "source_missing_conditions":events.get("unmatched_condition",0),
        "independent_sql_distinct_source_join_rows":sql_rows,
        "original_source_anatomy_relationships":len(direct["anatomy"]),
        "original_source_expression_condition_relationships":len(direct["expression_condition"]),
        "all_source_original_author_mapped_triples":len(raw),
        "independent_full_SQL_source_mapping_agrees":True,
        "independent_static_full_RDFLib_SPARQL_agrees":True,
        "static_direct_forward_inverse_consequences":len(expected),
        "independent_static_SPARQL_consequences":len(static_rdf),
        "exhaustive_sharded_OWL_RL_consequences_verified":len(found),
        "missing_OWL_RL_consequences":len(expected-found),
        "source_raw_edges_SHA256":digest_set(raw),
        "all_rule_consequences_SHA256":digest_set(expected),
        "shard_limit":chunk_size,
        "actual_shard_count":len(shards),
        "shards":shards,
        "source_ground_samples_are_not_synthetic":True,
        "all_mapped_edges_covered_by_partitioned_reasoning":True,
        "full_unpartitioned_RO_OWL_RL_closure_measured":False,
        "full_unpartitioned_Bgee_plus_RO_OWL_RL_closure_measured":False,
        "no_unmeasured_OWL_axioms_claimed":True,
        "clinical_valid_time_or_first_public_witness_authenticated":False,
        "patient_level_or_treatment_inference":False,
        "equal_capacity_SQL_static_reasoning_is_comparator_not_lift":True,
        "official_NIH_benchmark":False,
        "original_W13_modified":False,
    }


def execute(archive,author_files,ro_files):
    # Authenticates whole author R2RML, Ontop, GenEx, RO source files.
    gate=bridge.examine(author_files,ro_files)
    rows,census=earlier.source_tables(archive)
    author=Graph().parse(data=Path(author_files["bgee_v14_genex.owl"]).read_bytes(),format="turtle")
    original_ro,_,_=bridge.source.admit_sources(ro_files)
    result=evaluate(rows,author,original_ro)
    if result["original_source_positive_expression_rows"]!=census["source_measured_expression_rows"]:
        raise ValueError("whole-blob-pinned archive expression count changed")
    if len(gate["author_R2RML_mappings"])!=2:
        raise ValueError("authentic original author model count differs")
    if (result["original_source_anatomy_relationships"]!=FIXED_SOURCE_ANATOMY or
        result["original_source_expression_condition_relationships"]!=FIXED_SOURCE_CONDITION):
        raise ValueError("source original verified discovery baseline changed")
    result.update({
        "original_Bgee_zip_Git_blob_sha1":census["complete_original_source_git_blob_sha1"],
        "original_author_commit":bridge.COMMIT,
        "original_RO_source_commit":bridge.source.COMMIT,
        "original_author_mapping_rules":len(gate["author_R2RML_mappings"]),
        "original_source_file_sha256":{name:receipt["sha256"]
                   for name,receipt in gate["independent_original_RO_whole_file_receipts"].items()},
    })
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--archive",type=Path,required=True)
    for name in ("obda","owl","r2rml","ro-base","core","output"):
        ap.add_argument("--"+name,type=Path,required=True)
    a=ap.parse_args()
    author={"bgee_v14_genex."+k:getattr(a,k) for k in ("obda","owl","r2rml")}
    result=execute(a.archive,author,{"ro-base.owl":a.ro_base,"core.owl":a.core})
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+chr(10))
    print(json.dumps({
        "source_edges":result["all_source_original_author_mapped_triples"],
        "static_rules":result["independent_static_SPARQL_consequences"],
        "verified_owlrl":result["exhaustive_sharded_OWL_RL_consequences_verified"],
        "shards":result["actual_shard_count"],
        "missing_owlrl":result["missing_OWL_RL_consequences"],
        "NIH_completed":False},sort_keys=True))


if __name__=="__main__":
    main()
