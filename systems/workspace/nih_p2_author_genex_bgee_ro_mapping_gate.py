"""Author-owned Bgee/GenEx -> RO schema bridge: conditional original-source gate.

This gate verifies three distinct WHOLE original source bodies:
  1. Ontop tutorial authors' exact Ontop and R2RML mapping files;
  2. tutorial authors' GenEx ontology TTL file;
  3. independently pinned Relations Ontology original OWL/RDF release.
It proves a typed *source-author mapping path*, not that SQL result rows were
materialized, observed, historically valid, or clinically tested.
The original Bgee SQL dump is deliberately NOT admitted by this script.
No manual relation-code renaming, test-driven ontology alignment or fiction.
"""
from __future__ import annotations
import argparse
from hashlib import sha1,sha256
from pathlib import Path
import json

from rdflib import Graph,URIRef,RDFS,OWL,Namespace
from . import nih_phase2_external_obo_graph_trial as source

SCHEMA="nih-p2-authored-genex-bgee-ro-predicate-bridge-v1"
OWNER="ontop/ontop-patterns-tutorial"
COMMIT="08820b5589e52b9af846bc7e142e78c99e03d614"
FILES={
    "bgee_v14_genex.obda":"56782ed05ff7b16e07ee5bbc6873f77dbf308c38",
    "bgee_v14_genex.owl":"52c2f36d49fcceede657000d3b74edc3479dc429",
    "bgee_v14_genex.r2rml":"e2c3b329d8e96ffd06768fd1eafe2790429516d4",
}
GENEX=Namespace("http://purl.org/genex#")
OBO=Namespace("http://purl.obolibrary.org/obo/")
RR=Namespace("http://www.w3.org/ns/r2rml#")
MAPS=(
    URIRef("urn:Gene_IsExpressedIn_anatEntity"),
    URIRef("urn:Gene_IsExpressedIn_expressionCondition"),
)
RO_EXPRESSED=OBO["RO_0002206"]
RO_EXPRESSES=OBO["RO_0002292"]


def git_blob(raw):
    return sha1(b"blob "+str(len(raw)).encode()+b"\\0"+raw).hexdigest()


def validate_exact_owner(files):
    if set(files)!=set(FILES):
        raise ValueError("three exact independent source-author mapping files required")
    decoded={}
    receipts={}
    for name,pin in FILES.items():
        raw=Path(files[name]).read_bytes()
        actual=git_blob(raw)
        if actual!=pin:
            raise ValueError("original tutorial source blob changed: "+name)
        decoded[name]=raw.decode("utf8")
        receipts[name]={
            "original_owner":OWNER, "immutable_commit":COMMIT,
            "blob_sha1":actual,"content_sha256":sha256(raw).hexdigest(),
            "byte_count":len(raw),
            "original_path":"obda/"+name,
        }
    return decoded,receipts


def map_statement(g,identifier):
    if (identifier,None,None) not in g:
        raise ValueError("author R2RML map identity missing: "+str(identifier))
    logical=list(g.objects(identifier,RR.logicalTable))
    if len(logical)!=1:raise ValueError("one source query required per author mapping")
    sql=list(g.objects(logical[0],RR.sqlQuery))
    if len(sql)!=1:raise ValueError("one original author SQL query expected")
    predicate_maps=list(g.objects(identifier,RR.predicateObjectMap))
    relevant=[n for n in predicate_maps if (n,RR.predicate,GENEX.isExpressedIn) in g]
    if len(relevant)!=1:raise ValueError("exact original author GenEx predicate required")
    subject_maps=list(g.objects(identifier,RR.subjectMap))
    if len(subject_maps)!=1:raise ValueError("one author subject term map required")
    sub_templates=list(g.objects(subject_maps[0],RR.template))
    object_maps=list(g.objects(relevant[0],RR.objectMap))
    if len(sub_templates)!=1 or len(object_maps)!=1:
        raise ValueError("original author R2RML subject/object templates missing")
    obj_templates=list(g.objects(object_maps[0],RR.template))
    if len(obj_templates)!=1:raise ValueError("author source object template unavailable")
    q=str(sql[0])
    normalized=" ".join(q.lower().split())
    for expected in ("globalexpression","globalcond","gene","jointype_placeholder"):
        if expected=="jointype_placeholder":continue
        if expected not in normalized:
            raise ValueError("source SQL graph role unavailable: "+expected)
    if "calLType='EXPRESSED'".lower() not in normalized.replace(" ",""):
        raise ValueError("source SQL does not select positive EXPRESSED measurements")
    st,ot=str(sub_templates[0]),str(obj_templates[0])
    if st!="http://omabrowser.org/ontology/oma#GENE_{geneid}":
        raise ValueError("original author gene URI construction unexpectedly changed")
    if identifier==MAPS[0]:
        expected="http://purl.obolibrary.org/obo/{anatentityidsparql}"
    else:
        expected="http://bgee.org/#EXPRESSION_CONDITION_{globalconditionid}"
    if ot!=expected:raise ValueError("original author target resource template changed")
    return {
        "original_mapping_id":str(identifier),
        "predicate":str(GENEX.isExpressedIn),
        "original_SQL_text_SHA256":sha256(q.encode()).hexdigest(),
        "original_sql_selects_expressed_call_type":True,
        "author_subject_URI_template":st,
        "author_object_URI_template":ot,
        "original_table_role_names_verified":True,
        "SQL_executed_on_original_Bgee":False,
    }


def examine(ontop_files,ro_files):
    decoded,receipts=validate_exact_owner(ontop_files)
    genex=Graph().parse(data=decoded["bgee_v14_genex.owl"],format="turtle")
    r2=Graph().parse(data=decoded["bgee_v14_genex.r2rml"],format="turtle")
    obda=decoded["bgee_v14_genex.obda"]
    for mapping in ("Gene_IsExpressedIn_anatEntity","Gene_IsExpressedIn_expressionCondition"):
        if obda.count("mappingId\\t"+mapping+"\\n")!=1:
            raise ValueError("original Ontop mapping ID not authenticated "+mapping)
    rows=[map_statement(r2,mapping) for mapping in MAPS]
    if (GENEX.isExpressedIn,RDFS.subPropertyOf,RO_EXPRESSED) not in genex:
        raise ValueError("source author GenEx ontology omits required subPropertyOf rule")
    if (RO_EXPRESSED,OWL.inverseOf,RO_EXPRESSES) not in genex:
        raise ValueError("original tutorial does not attest required inverseOf direction")
    ro,ro_receipts,_=source.admit_sources(ro_files)
    if (RO_EXPRESSED,OWL.inverseOf,RO_EXPRESSES) not in ro:
        raise ValueError("independent RO whole-source inverse declaration not supported")
    if GENEX.isExpressedIn in set(ro.subjects()) and (
         GENEX.isExpressedIn,RDFS.subPropertyOf,RO_EXPRESSED) in ro:
        raise ValueError("unexpected assertion in original RO claimed as cross-source mapping")
    # Independent source chaining by SPARQL property edges, with no inferred
    # individual claims, rather than recognizing similar labels or code patterns.
    combined=Graph()
    combined += genex
    combined += ro
    q="""PREFIX owl: <http://www.w3.org/2002/07/owl#>
         PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
         ASK WHERE {
           <http://purl.org/genex#isExpressedIn> rdfs:subPropertyOf
             <http://purl.obolibrary.org/obo/RO_0002206> .
           <http://purl.obolibrary.org/obo/RO_0002206> owl:inverseOf
             <http://purl.obolibrary.org/obo/RO_0002292> .
         }"""
    if not bool(combined.query(q)):
        raise ValueError("independent SPARQL author-to-RO path did not verify")
    return {
       "schema":SCHEMA,
       "mapping_author_owner":OWNER,"mapping_author_commit":COMMIT,
       "source_author_whole_file_receipts":receipts,
       "source_author_ontology_triples":len(genex),
       "source_author_R2RML_triples":len(r2),
       "independent_original_RO_source_commit":source.COMMIT,
       "independent_original_RO_whole_file_receipts":ro_receipts,
       "independent_original_RO_graph_triples":len(ro),
       "author_R2RML_mappings":rows,
       "author_original_ontop_map_IDs_present":True,
       "source_author_genex_subproperty_to_RO_0002206":True,
       "source_owner_original_RO_0002206_inverseOf_RO_0002292":True,
       "author_file_and_independent_RO_inverse_agree":True,
       "independent_original_graph_SPARQL_path_agrees":True,
       "author_positive_expression_measurement_selection_is_declared":True,
       "original_Bgee_SQL_rows_measured":False,
       "source_ground_biomedical_relationships_materialized":0,
       "source_ground_biomedical_relationships_materialized_measured":False,
       "author_cross_version_biological_semantics_compatible":"NOT_MEASURED",
       "additional_patient_or_disease_treatment_claim":False,
       "genuine_original_expression_direction_claim":"CONDITIONAL_ON_AUTHOR_SQL_DATA",
       "original_W13_modified":False,
       "official_NIH_phase2_benchmark":False,
    }


def main():
    parser=argparse.ArgumentParser()
    for name in FILES:
        parser.add_argument("--"+name.split(".")[1],required=True,type=Path)
    parser.add_argument("--ro-base",required=True,type=Path)
    parser.add_argument("--core",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    files={name:getattr(args,name.split(".")[1]) for name in FILES}
    x=examine(files,{"ro-base.owl":args.ro_base,"core.owl":args.core})
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(x,sort_keys=True,indent=2)+"\\n")
    print(json.dumps({
       "author_source_mappings":len(x["author_R2RML_mappings"]),
       "original_RO_inverse_pair":x["source_owner_original_RO_0002206_inverseOf_RO_0002292"],
       "independent_cross_source_path":x["independent_original_graph_SPARQL_path_agrees"],
       "original_sql_rows_measured":x["original_Bgee_SQL_rows_measured"],
       "NIH_completed":False},sort_keys=True))


if __name__=="__main__":
    main()
