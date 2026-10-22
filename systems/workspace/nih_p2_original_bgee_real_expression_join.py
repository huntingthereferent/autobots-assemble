"""Original Bgee real gene-expression RDF join, independent SQLite and bounded OWL RL.

Two author R2RML mapping rules and both complete pinned RO files are required.
The original archive is read only; data rows never enter the artifact. The
candidate triples arise from actual author source records, not test fixtures.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
import json
import re
import sqlite3

from rdflib import Graph, URIRef, RDFS, OWL
from . import nih_p2_original_bgee_archive_intake as intake
from . import nih_p2_author_genex_bgee_ro_mapping_gate as bridge

SCHEMA="nih-p2-original-bgee-real-gene-expression-inference-v1"
ZIP_BLOB="234c79cc9e1eca2b6493fc6ee34b8270f2508861"
TABLES={
  "gene":("bgeegeneid","geneid"),
  "globalcond":("globalconditionid","anatentityid"),
  "globalexpression":("globalexpressionid","bgeegeneid","globalconditionid","calltype")
}
SAFE_ID=re.compile(r"^[A-Za-z0-9_.:-]+$")
MAX_SELECTED_ROWS=100000
SAMPLE_PER_KIND=24


def id_value(value):
    if value is None or not SAFE_ID.fullmatch(value):
        raise ValueError("source original ID cannot be represented by owner RDF term template")
    return value


def source_tables(archive):
    census=intake.examine_archive(archive,expected_git_blob=ZIP_BLOB)
    tables={name:[] for name in TABLES}
    schemas={}
    with ZipFile(archive) as z:
        for info in z.infolist():
            if info.is_dir():continue
            if info.file_size>intake.MAX_MEMBER_BYTES:
                raise ValueError("original SQL member exceeds accepted compressed-source bound")
            raw=z.read(info)
            if b"COPY " not in raw[:500000]:continue
            selected=None
            for line in raw.decode("utf8","strict").splitlines():
                if selected:
                    if line==chr(92)+".":
                        selected=None
                        continue
                    values=line.split(chr(9))
                    if len(values)!=selected[1]:
                        raise ValueError("source COPY row width disagrees with owner columns")
                    tables[selected[0]].append(tuple(
                        None if values[i]==chr(92)+"N" else values[i]
                        for i in selected[2]))
                    if sum(len(v) for v in tables.values())>MAX_SELECTED_ROWS:
                        raise ValueError("source input row count exceeds bound")
                    continue
                match=intake.TABLE_COPY.match(line)
                if not match:continue
                table=intake.canonical_table(match.group(1))
                if table not in TABLES:continue
                cols=tuple(c.strip().lower().replace('"','')
                           for c in match.group(2).split(","))
                if table in schemas and schemas[table]!=cols:
                    raise ValueError("conflicting author SQL table schema")
                if not set(TABLES[table]).issubset(cols):
                    raise ValueError("original author SQL join column missing from "+table)
                schemas[table]=cols
                selected=(table,len(cols),tuple(cols.index(c) for c in TABLES[table]))
            if selected:
                raise ValueError("source PostgreSQL COPY section truncated")
    if any(not tables[t] for t in TABLES):
        raise ValueError("original archive lacks an author-required source table")
    return tables,census


def construct_edges(gene,cond,anatom):
    """Two exact author R2RML term templates, not renamed raw relation codes."""
    g="http://omabrowser.org/ontology/oma#GENE_"+id_value(gene)
    c="http://bgee.org/#EXPRESSION_CONDITION_"+id_value(cond)
    result={("expression_condition",(g,str(bridge.GENEX.isExpressedIn),c))}
    if anatom is not None:
        a="http://purl.obolibrary.org/obo/"+id_value(anatom).replace(":","_")
        result.add(("anatomy",(g,str(bridge.GENEX.isExpressedIn),a)))
    return result


def keyed_join(rows):
    genes={}
    conds={}
    for internal,gene in rows["gene"]:
        if internal in genes and genes[internal]!=gene:
            raise ValueError("conflicting source owner gene key")
        genes[internal]=gene
    for internal,anat in rows["globalcond"]:
        if internal in conds and conds[internal]!=anat:
            raise ValueError("conflicting source owner condition key")
        conds[internal]=anat
    edges={"anatomy":set(),"expression_condition":set()}
    events=Counter()
    for expression, internal_gene, condition, call in rows["globalexpression"]:
        if call!="EXPRESSED":
            continue
        events["source_positive_expression_rows"]+=1
        if internal_gene not in genes:
            events["unmatched_gene"]+=1
            continue
        if condition not in conds:
            events["unmatched_condition"]+=1
            continue
        for kind,edge in construct_edges(genes[internal_gene],condition,conds[condition]):
            edges[kind].add(edge)
        events["joined_positive_rows"]+=1
    return edges,dict(events)


def independent_sqlite_join(rows):
    """Independent real SQLite relational join with the author-specified keys."""
    con=sqlite3.connect(":memory:")
    try:
        for name,columns in TABLES.items():
            con.execute("CREATE TABLE "+name+" ("+",".join(c+" TEXT" for c in columns)+")")
            con.executemany("INSERT INTO "+name+" VALUES ("+",".join("?" for _ in columns)+")",rows[name])
        found=con.execute("""
           SELECT DISTINCT g.geneid,c.anatentityid,e.globalconditionid
           FROM globalexpression AS e
           JOIN globalcond AS c ON e.globalconditionid=c.globalconditionid
           JOIN gene AS g ON g.bgeegeneid=e.bgeegeneid
           WHERE e.calltype='EXPRESSED'
        """).fetchall()
        out={"anatomy":set(),"expression_condition":set()}
        for gene,anat,condition in found:
            for kind,edge in construct_edges(gene,condition,anat):
                out[kind].add(edge)
        return out,len(found)
    finally:
        con.close()


def bounded_source_owlrl(edges,author_graph,ro_graph):
    """On genuine source-ground edges only; source-owned two axioms required."""
    from owlrl import DeductiveClosure,OWLRL_Semantics
    sub=(bridge.GENEX.isExpressedIn,RDFS.subPropertyOf,bridge.RO_EXPRESSED)
    inverse=(bridge.RO_EXPRESSED,OWL.inverseOf,bridge.RO_EXPRESSES)
    if sub not in author_graph or inverse not in ro_graph:
        raise ValueError("independent original ontology owner semantics missing")
    original=Graph()
    original.add(sub)
    original.add(inverse)
    chosen=[]
    for kind in ("anatomy","expression_condition"):
        ordered=sorted(edges[kind],
            key=lambda t:sha256(("|".join(t)+"|original-Bgee-v1").encode()).hexdigest())
        if len(ordered)<SAMPLE_PER_KIND:
            raise ValueError("insufficient genuine source facts for predetermined bounded test")
        for s,p,o in ordered[:SAMPLE_PER_KIND]:
            original.add((URIRef(s),URIRef(p),URIRef(o)))
            chosen.append((kind,s,p,o))
    expanded=Graph()
    expanded+=original
    DeductiveClosure(OWLRL_Semantics,rdfs_closure=True).expand(expanded)
    proofs=[]
    for kind,s,p,o in chosen:
        forward=(URIRef(s),bridge.RO_EXPRESSED,URIRef(o))
        reverse=(URIRef(o),bridge.RO_EXPRESSES,URIRef(s))
        if forward not in expanded or reverse not in expanded:
            raise ValueError("OWL RL not reproducing genuine Bgee expression inference")
        proofs.append({
          "source_mapping_kind":kind,
          "original_source_relationship_sha256":sha256("|".join((s,p,o)).encode()).hexdigest(),
          "entailed_forward_RO_sha256":sha256("|".join(map(str,forward)).encode()).hexdigest(),
          "entailed_inverse_RO_sha256":sha256("|".join(map(str,reverse)).encode()).hexdigest(),
          "original_source_relationship_not_synthetic":True})
    return proofs,len(expanded)


def evaluate(rows,author_graph,ro_graph):
    joined,events=keyed_join(rows)
    static,n_sql=independent_sqlite_join(rows)
    if joined!=static:
        raise ValueError("independent full original Bgee SQLite SQL join disagrees with direct owner-key join: "+
                         repr({k:(len(joined[k]),len(static[k])) for k in joined}))
    proofs,nmaterialized=bounded_source_owlrl(joined,author_graph,ro_graph)
    return {
      "raw_original_source_join_tables":{k:len(v) for k,v in rows.items()},
      "original_positive_expression_call_rows":events.get("source_positive_expression_rows",0),
      "joined_positive_expression_rows":events.get("joined_positive_rows",0),
      "source_unmatched_gene_rows":events.get("unmatched_gene",0),
      "source_unmatched_condition_rows":events.get("unmatched_condition",0),
      "independent_SQL_distinct_join_tuples":n_sql,
      "source_original_gene_anatomy_RDF_edges":len(joined["anatomy"]),
      "source_original_gene_condition_RDF_edges":len(joined["expression_condition"]),
      "original_complete_source_key_join_matches_independent_SQL":True,
      "real_source_ground_OWL_RL_edges_tested":len(proofs),
      "genuine_source_biomedical_relation_inferences_reproduced":len(proofs),
      "bounded_reasoner_rdf_triples":nmaterialized,
      "bounded_real_source_proof_receipts":proofs,
    }


def execute(archive,author_files,ro_files):
    bridge_proof=bridge.examine(author_files,ro_files)
    rows,census=source_tables(archive)
    genex=Graph().parse(data=Path(author_files["bgee_v14_genex.owl"]).read_bytes(),format="turtle")
    original_ro,_,_=bridge.source.admit_sources(ro_files)
    report=evaluate(rows,genex,original_ro)
    if report["original_positive_expression_call_rows"]!=census["source_measured_expression_rows"]:
        raise ValueError("original archive source positive count differed from frozen intake")
    report.update({
      "schema":SCHEMA,
      "authenticated_original_bgee_zip_blob":census["complete_original_source_git_blob_sha1"],
      "original_author_file_commit":bridge.COMMIT,
      "original_owner_source_mapping_rules":len(bridge_proof["author_R2RML_mappings"]),
      "original_external_RO_commit":bridge.source.COMMIT,
      "actual_source_relationships_not_trial_synthetic":True,
      "Bgee_expression_observations_do_not_prove_treatment_efficacy":True,
      "clinical_valid_at_and_first_public_time":"NOT_MEASURED",
      "complete_dataset_full_OWL_RL_materialization":False,
      "equal_capability_static_SQL_oracle_not_AB_advantage":True,
      "original_patient_level_data_used":False,
      "original_W13_modified":False,
      "official_NIH_benchmark":False})
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True,type=Path)
    for name in ("obda","owl","r2rml","ro-base","core","output"):
        p.add_argument("--"+name,required=True,type=Path)
    a=p.parse_args()
    author={"bgee_v14_genex."+k:getattr(a,k) for k in ("obda","owl","r2rml")}
    result=execute(a.archive,author,{"ro-base.owl":a.ro_base,"core.owl":a.core})
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+chr(10))
    print(json.dumps({k:result[k] for k in (
      "original_positive_expression_call_rows",
      "joined_positive_expression_rows",
      "source_unmatched_gene_rows",
      "source_unmatched_condition_rows",
      "independent_SQL_distinct_join_tuples",
      "source_original_gene_anatomy_RDF_edges",
      "source_original_gene_condition_RDF_edges",
      "real_source_ground_OWL_RL_edges_tested",
      "genuine_source_biomedical_relation_inferences_reproduced",
      "original_complete_source_key_join_matches_independent_SQL")},sort_keys=True))


if __name__=="__main__":
    main()
