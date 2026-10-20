"""External OBO Relations biomedical RDF graph: genuine structure, declared test clocks.

Actual OWL RDF/XML is fetched from one GitHub commit and whole-file hashed.
Its rdfs:subPropertyOf/rdfs:subClassOf relations are original biomedical
ontology data, NOT authored toy edges. Date stamps are expressly synthetic
test overlays because the source has no historical edge-level validity.
A/B computes finite 2-hop compositions. An independent rdflib SPARQL
property path checks the same graph; a full-graph static *reasoning*
baseline ignores test timestamps. No source content is redistributed.
"""
from __future__ import annotations

from collections import Counter
from datetime import date,timedelta
from hashlib import sha256
from pathlib import Path
import argparse
import json
from rdflib import Graph,URIRef,RDFS,OWL,RDF,Namespace
from rdflib.namespace import XSD
from owlrl import DeductiveClosure,OWLRL_Semantics

SCHEMA="nih-phase2-external-obo-original-rdf-inference-comparison/v1"
OWNER="oborel/obo-relations"
COMMIT="091f4761ec84657cc336d623e02006d6c351722c"
SOURCE_FILES=("ro-base.owl","core.owl")
# Observed exact raw original GitHub commit assets, fixed before benchmark run.
PINNED_WHOLE_SOURCE_SHA256={
    "ro-base.owl":"bdfe8dda3adc4b9cda9d9c843b02e1031772280a92c07003af7c9c22cde027fe",
    "core.owl":"3c8e219fddd6f772c2d5e27cced12a91e8c3d2431b5e02af58e4ec567a4efeb8",
}
VERSION="2026-09-04"
SOURCE_URL="https://raw.githubusercontent.com/"+OWNER+"/"+COMMIT+"/"
CUTOFFS=("2026-01-03","2026-01-12","2026-01-29")
MAX_EDGES=2500
MIN_PROPERTY_EDGES=400
AB=Namespace("https://example.org/ab-nih-external-observation/")


def digest(b):return sha256(b).hexdigest()


def admit_sources(filenames):
    if set(filenames)!=set(SOURCE_FILES):raise ValueError("exact two pinned original ontology files needed")
    combined=Graph()
    src={}
    for name in SOURCE_FILES:
        raw=Path(filenames[name]).read_bytes()
        if digest(raw)!=PINNED_WHOLE_SOURCE_SHA256[name]:
            raise ValueError("original external ontology bytes do not match frozen source hash")
        if not 5000<len(raw)<5_000_000:
            raise ValueError("original ontology missing or unreasonable size")
        g=Graph()
        g.parse(data=raw,format="xml",publicID=SOURCE_URL+name)
        version=set(str(obj) for obj in g.objects(None,OWL.versionInfo))
        if VERSION not in version:
            raise ValueError("original ontology release changed")
        if not any(str(obj).endswith("creativecommons.org/publicdomain/zero/1.0/") for obj in g.objects(None,URIRef("http://purl.org/dc/terms/license"))):
            raise ValueError("external owner's original license attribution unavailable")
        src[name]={"url":SOURCE_URL+name,"sha256":digest(raw),"rdf_triples":len(g),"version":VERSION}
        combined+=g
    edges=set()
    for p,domain in ((RDFS.subPropertyOf,"relation-types"),(RDFS.subClassOf,"biological-classes")):
        for s,o in combined.subject_objects(p):
            if isinstance(s,URIRef) and isinstance(o,URIRef) and s!=o:
                edges.add((str(s),str(p),str(o),domain))
    if len(edges)>MAX_EDGES or sum(e[3]=="relation-types" for e in edges)<MIN_PROPERTY_EDGES:
        raise ValueError("source edge content unlike pinned external ontology")
    ordered=sorted(edges)
    return combined,src,ordered


def overlay(edges):
    """Deterministic declared *hypothetical* clocks; never source publication."""
    rows=[]
    for s,p,o,domain in edges:
        h=bytes.fromhex(digest((s+"|"+p+"|"+o).encode("utf8")))
        known=(date(2026,1,1)+timedelta(days=1+h[0]%22)).isoformat()
        valid=(date(2026,1,1)+timedelta(days=h[1]%9)).isoformat()
        rows.append({"s":s,"p":p,"o":o,"domain":domain,
            "known_at":known,"valid_from":valid,"valid_to":"2026-02-02",
            "source_relation_sha256":digest((s+"|"+p+"|"+o).encode())})
    return rows


def ab_composed_query(rows, *, start, end, predicate, known, valid):
    """Finite actual joined graph relationship; TWO links, not same-subject tags."""
    available={(r["s"],r["o"]) for r in rows
        if r["p"]==predicate and r["known_at"]<=known
        and r["valid_from"]<=valid<r["valid_to"]}
    second={x for x,y in available if y==end}
    middle={y for x,y in available if x==start}
    common=middle & second
    return {"path_exists":bool(common),"middle_nodes":sorted(common),
        "relationship":"source-edge-composition-only","causal_claim":False}


def sparql_oracle(rows, start, end, pred, known, valid, *, ignore_clocks):
    """Independent RDFLib SPARQL *static graph reasoner* / temporal graph oracle."""
    g=Graph()
    for row in rows:
        if row["p"]!=pred:continue
        if ignore_clocks or (row["known_at"]<=known and row["valid_from"]<=valid<row["valid_to"]):
            g.add((URIRef(row["s"]),URIRef(pred),URIRef(row["o"])))
    # Unlike the A/B exact-two-hop operation this asks whether ANY path
    # exists. Disagreement is retained as a measured limitation.
    q=f"ASK WHERE {{ <{start}> <{pred}>+ <{end}> }}"
    return bool(g.query(q))


def exact_two_hop_oracle(rows,start,end,pred,known,valid):
    g=Graph()
    for row in rows:
        if row["p"]==pred and row["known_at"]<=known and row["valid_from"]<=valid<row["valid_to"]:
            g.add((URIRef(row["s"]),URIRef(pred),URIRef(row["o"])))
    # Separately implemented original RDF triples cross-product, not ab_composed_query.
    return sorted({str(b) for a,_,b in g.triples((URIRef(start),URIRef(pred),None))
                   if (b,URIRef(pred),URIRef(end)) in g})


def selected_queries(rows):
    """Preserve exact 2-hop cases AND source-observed >2-hop limitation cases."""
    within={}
    for domain in ("relation-types","biological-classes"):
        subset=[r for r in rows if r["domain"]==domain]
        by_source={}
        for r in subset:
            by_source.setdefault(r["s"],set()).add(r["o"])
        direct={(r["s"],r["o"]) for r in subset}
        pairs2=set()
        for first in subset:
            for final in by_source.get(first["o"],()):
                if first["s"]!=final:
                    pairs2.add((first["s"],final))
        # Use the actual original source edges; don't inject synthetic edges
        # to force the static baseline into better-looking performance.
        pairs3=set()
        for first in subset:
            for middle in by_source.get(first["o"],()):
                for final in by_source.get(middle,()):
                    if (first["s"]!=final and first["s"]!=middle
                            and final!=first["o"]):
                        pair=(first["s"],final)
                        if pair not in pairs2 and pair not in direct:
                            pairs3.add(pair)
        within[domain]={
            "predicate":subset[0]["p"] if subset else None,
            "exact-two-hop":sorted(pairs2),
            "three-hop-without-shorter":sorted(pairs3),
        }
    if not within["relation-types"]["exact-two-hop"] or not within["relation-types"]["three-hop-without-shorter"]:
        raise ValueError("external original ontology has no both two- and three-hop source trials")
    cases=[]
    sizes={}
    for domain,data in within.items():
        sizes[domain]={
            "original_exact_two_hop":len(data["exact-two-hop"]),
            "original_three_hop_without_shorter":len(data["three-hop-without-shorter"]),
        }
        for kind,limit in (("exact-two-hop",96 if domain=="relation-types" else 24),
                           ("three-hop-without-shorter",24 if domain=="relation-types" else 8)):
            for source,target in data[kind][:limit]:
                cases.append((source,target,data["predicate"],domain,kind))
    if len(cases)<40 or not any(case[-1]=="three-hop-without-shorter" for case in cases):
        raise ValueError("insufficient independent actual longer-source-path examples")
    return cases,sizes

def ontology_disjoint_probe(g):
    """Actual external owl:disjointWith premise + injected contradiction CONTROL.

    This checks an OWL RL inconsistency signal. It is not unsatisfiable-class
    enumeration, full OWL DL or a claim original OBO ontology inconsistent.
    """
    pairs=sorted((str(s),str(o)) for s,o in g.subject_objects(OWL.disjointWith)
                 if isinstance(s,URIRef) and isinstance(o,URIRef))
    if not pairs:raise ValueError("no actual external disjointness premise")
    a,b=pairs[0]
    test=Graph()
    sample=AB["synthetic-conflict-individual"]
    test.add((URIRef(a),OWL.disjointWith,URIRef(b)))
    test.add((sample,RDF.type,URIRef(a)))
    test.add((sample,RDF.type,URIRef(b)))
    DeductiveClosure(OWLRL_Semantics).expand(test)
    ERR=URIRef("http://www.daml.org/2002/03/agents/agent-ont#ErrorMessage")
    # owlrl has its own namespace for rule error messages.
    messages=[str(o) for s,p,o in test if "ErrorMessage" in str(p) or "ErrorMessage" in str(o)]
    # OWLRL reports inconsistency through err:ErrorMessage rdf:type.
    actual=[str(s) for s,p,o in test if p==RDF.type and "ErrorMessage" in str(o)]
    return {
        "original_external_disjoint_axiom":[a,b],
        "deliberately_injected_fixture":True,
        "owlrl_error_signal_count":len(set(actual)),
        "owlrl_error_explanations":len(messages),
        "full_unsatisfiable_class_enumeration":False,
        "original_biomedical_ontology_inconsistent":None,
        "full_owl_dl_consistency_verified":False,
    }


def execute(files):
    graph,sources,edges=admit_sources(files)
    rows=overlay(edges)
    picks,candidate_counts=selected_queries(rows)
    cases=[]
    for src,tgt,p,domain,path_type in picks:
        for known in CUTOFFS:
            # target is deliberately held later than all hypothetical starts.
            valid="2026-01-30"
            ab=ab_composed_query(rows,start=src,end=tgt,predicate=p,known=known,valid=valid)
            independent=exact_two_hop_oracle(rows,src,tgt,p,known,valid)
            if ab["middle_nodes"]!=independent:
                raise ValueError("independent RDF exact-two-hop oracle disagrees")
            static=sparql_oracle(rows,src,tgt,p,known,valid,ignore_clocks=True)
            temporal_all_paths=sparql_oracle(rows,src,tgt,p,known,valid,ignore_clocks=False)
            cases.append({
                "source_domain":domain,"source_path_category":path_type,\n                "source_subject":src,"source_object":tgt,
                "source_predicate":p,"test_known_at_synthetic":known,
                "test_target_at_synthetic":valid,
                "AB_two_hop":ab["path_exists"],
                "independent_exact_two_hop":bool(independent),
                "independent_RDF_temporal_property_path_plus":temporal_all_paths,
                "full_external_graph_static_RDF_property_path_plus":static,
                "static_predicted_reachable_before_support":static and not temporal_all_paths,
                "temporal_any_path_unmatched_by_2_hop":temporal_all_paths and not ab["path_exists"],
                "source_path_witness_middle_nodes":ab["middle_nodes"],
            })
    domains={k:sum(c["source_domain"]==k for c in cases) for k in candidate_counts}
    return {
        "schema":SCHEMA,"external_source":"OBO Relation Ontology 2026-09-04",
        "original_source_git_commit":COMMIT,
        "source_files":sources,
        "original_graph_rdf_triples":len(graph),
        "original_source_hierarchy_edges":len(edges),
        "original_hierarchy_relation_domains":Counter(r[3] for r in edges),
        "candidate_two_hop_source_pairs":candidate_counts,
        "synthetic_clock_overlay_only":True,
        "source_original_edge_publication_times_authenticated":False,
        "independent_static_baseline":"rdflib SPARQL property path + over entire original ontology hierarchy graph",
        "independent_temporal_baseline":"rdflib SPARQL property path + on filtered original hierarchy relations",
        "AB_operation":"finite original-source-exact-two-hop chronological-availability-composition",
        "scored_cases":len(cases),"domain_cases":domains,
        "AB_equals_independent_exact_two_hop_cases":len(cases),
        "static_future_leakage_cases":sum(c["static_predicted_reachable_before_support"] for c in cases),
        "full_static_true_cases":sum(c["full_external_graph_static_RDF_property_path_plus"] for c in cases),
        "temporal_any_path_not_supported_by_AB_2_hop":
            sum(c["temporal_any_path_unmatched_by_2_hop"] for c in cases),
        "original_three_hop_only_case_count":
            sum(c["source_path_category"]=="three-hop-without-shorter" for c in cases),
        "static_reasoner_reachable_three_hop_AB_misses":
            sum(c["source_path_category"]=="three-hop-without-shorter"
                and c["full_external_graph_static_RDF_property_path_plus"]
                and not c["AB_two_hop"] for c in cases),
        "actual_original_disjointness_with_synthetic_inconsistent_fixture":
            ontology_disjoint_probe(graph),
        "original_raw_ontology_files_redistributed":False,
        "original_W13_engine_modified":False,
        "World48_required":False,
        "official_NIH_shared_test_data":False,
        "NIH_Phase2_reproduced":False,
        "cases":cases,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ro-base",required=True,type=Path)
    p.add_argument("--core",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    result=execute({"ro-base.owl":a.ro_base,"core.owl":a.core})
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2,default=list)+"\n",encoding="utf8")
    print(json.dumps({
        "external_original_graph_triples":result["original_graph_rdf_triples"],
        "actual_original_hierarchy_edges":result["original_source_hierarchy_edges"],
        "external_reproduction_queries":result["scored_cases"],
        "domain_cases":result["domain_cases"],
        "static_future_leakage_cases":result["static_future_leakage_cases"],
        "two_hop_mismatch_cases":result["scored_cases"]-
            result["AB_equals_independent_exact_two_hop_cases"],
        "static_reaches_three_hop_where_AB_cannot":
            result["static_reasoner_reachable_three_hop_AB_misses"],
        "OWL_RL_deliberate_contradiction_signal":
            result["actual_original_disjointness_with_synthetic_inconsistent_fixture"]
                  ["owlrl_error_signal_count"],
        "NIH_Phase2_reproduced":False,
    },sort_keys=True))


if __name__=="__main__":
    main()
