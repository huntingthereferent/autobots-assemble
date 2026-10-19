"""Bounded RDF export from the original Phase-1-contained Phase-2 WORLD blueprint.

Reuses the Phase 1 draft's TE namespace and its OWL-Time, PROV-O and Biolink
vocabulary. The RDF *data* is a source-qualified graph, not an OWL temporal
reasoner. A separately implemented parsed-graph oracle checks exact source
facts and deterministic synthetic Q(K,V); it never converts an owner-posted
calendar day into a known-at UTC instant or clinical validity.
"""
from __future__ import annotations
from datetime import date
from hashlib import sha256
import json
from pathlib import Path
from rdflib import Graph,Namespace,RDF,RDFS,OWL,URIRef,Literal
from rdflib.namespace import XSD
from systems.workspace.world_temporal_blueprint import validate,evaluate

TE=Namespace("https://example.org/nih-temporal-evidence/2026-10/")
TIME=Namespace("http://www.w3.org/2006/time#")
PROV=Namespace("http://www.w3.org/ns/prov#")
BIOLINK=Namespace("https://w3id.org/biolink/vocab/")
SCHEMA="world-phase1-phase2-rdf-source-graph/v1"

def assertion_uri(row):
    return TE["world-assertion-"+row["id"]]

def source_uri(row):
    return URIRef(row["source_ref"]) if row["provenance_state"]=="owner-version-day-attested" else TE["world-source-"+row["source_ref"]]

def create_graph(bp,mode):
    validate(bp)
    if mode not in ("synthetic","registry"):raise ValueError("unknown source graph partition")
    graph=Graph()
    for name,ns in (("te",TE),("time",TIME),("prov",PROV),("biolink",BIOLINK),
                    ("rdf",RDF),("rdfs",RDFS),("owl",OWL),("xsd",XSD)):
        graph.bind(name,ns)
    graph.add((TE.TemporalAssertion,RDF.type,OWL.Class))
    graph.add((TE.TemporalAssertion,RDFS.subClassOf,BIOLINK.InformationContentEntity))
    for row in bp["sample_sets"][mode]:
        subject=assertion_uri(row)
        source=source_uri(row)
        graph.add((subject,RDF.type,TE.TemporalAssertion))
        graph.add((subject,RDF.type,
                   TE.AvailabilityWitnessedAssertion if mode=="synthetic" else TE.UnresolvedAvailabilityAssertion))
        graph.add((subject,PROV.wasDerivedFrom,source))
        graph.add((source,RDF.type,PROV.Entity))
        for k,prop in (("subject",TE.subjectToken),("predicate",TE.predicateToken),("object",TE.objectToken)):
            graph.add((subject,prop,Literal(row[k],datatype=XSD.string)))
        if mode=="synthetic":
            interval=TE["world-interval-"+row["id"]]
            begin=TE["world-valid-begin-"+row["id"]]
            end=TE["world-valid-end-"+row["id"]]
            known=TE["world-known-"+row["id"]]
            graph.add((subject,TE.hasEvidenceClass,TE.SyntheticFixture))
            graph.add((subject,TE.validDuring,interval))
            graph.add((subject,TE.knownFrom,known))
            graph.add((interval,RDF.type,TIME.ProperInterval))
            graph.add((interval,TIME.hasBeginning,begin))
            graph.add((interval,TIME.hasEnd,end))
            for t,day in ((begin,row["valid_from"]),(end,row["valid_to"]),(known,row["known_day"])):
                graph.add((t,RDF.type,TIME.Instant))
                graph.add((t,TIME.inXSDDate,Literal(day,datatype=XSD.date)))
        else:
            graph.add((subject,RDF.type,TE.RegistryStatusAssertion))
            graph.add((subject,TE.hasEvidenceClass,TE.OriginalPublicVersion))
            graph.add((subject,TE.statusValue,Literal(row["object"],datatype=XSD.string)))
            graph.add((subject,TE.sourceReportedPostedDay,Literal(row["posted_day"],datatype=XSD.date)))
            graph.add((subject,TE.submittedDay,Literal(row["submitted_day"],datatype=XSD.date)))
            graph.add((subject,TE.observedDay,Literal(row["observed_day"],datatype=XSD.date)))
            graph.add((subject,TE.sourceTextSHA256,Literal(row["source_text_sha256"],datatype=XSD.string)))
            graph.add((source,TE.sourceVersionId,Literal("V94" if row["id"]=="ctgov-v94" else "V105",datatype=XSD.string)))
    return graph

def independently_check_rdf(bp,mode,rdf_text):
    """Parse the exported Turtle anew and reconstruct the answer from RDF,
    without calling create_graph or the Python query projection."""
    validate(bp)
    if type(rdf_text) is not str or len(rdf_text.encode())>500_000:
        raise ValueError("unbounded generated RDF")
    g=Graph()
    g.parse(data=rdf_text,format="turtle")
    if (TE.TemporalAssertion,RDFS.subClassOf,BIOLINK.InformationContentEntity) not in g:
        raise ValueError("Phase 1 Biolink source alignment missing")
    src=bp["sample_sets"][mode]
    ids={assertion_uri(r) for r in src}
    if set(g.subjects(RDF.type,TE.TemporalAssertion))!=ids:
        raise ValueError("extra or missing RDF assertion")
    k=bp["queries"][mode]["knowledge_cutoff"]
    v=bp["queries"][mode]["valid_target"]
    eligible=[];future=[];outside=[];unknown=[]
    for row in src:
        a=assertion_uri(row)
        owner=source_uri(row)
        if (a,PROV.wasDerivedFrom,owner) not in g or (owner,RDF.type,PROV.Entity) not in g:
            raise ValueError("RDF source provenance missing")
        for key,property in (("subject",TE.subjectToken),("predicate",TE.predicateToken),("object",TE.objectToken)):
            if set(g.objects(a,property))!={Literal(row[key],datatype=XSD.string)}:
                raise ValueError("RDF assertion field differs from source")
        if mode=="synthetic":
            if (a,TE.hasEvidenceClass,TE.SyntheticFixture) not in g:
                raise ValueError("synthetic source class missing")
            intervals=list(g.objects(a,TE.validDuring))
            known=list(g.objects(a,TE.knownFrom))
            if len(intervals)!=1 or len(known)!=1:
                raise ValueError("exact modeled time nodes missing")
            i=intervals[0]
            b=list(g.objects(i,TIME.hasBeginning))
            e=list(g.objects(i,TIME.hasEnd))
            if len(b)!=1 or len(e)!=1 or (i,RDF.type,TIME.ProperInterval) not in g:
                raise ValueError("valid interval invalid")
            def day(node):
                if (node,RDF.type,TIME.Instant) not in g:raise ValueError("time instant missing")
                values=list(g.objects(node,TIME.inXSDDate))
                if len(values)!=1 or values[0].datatype!=XSD.date:
                    raise ValueError("date from original assertion missing")
                return str(values[0])
            start,finish,known_at=day(b[0]),day(e[0]),day(known[0])
            if (start,finish,known_at)!=(row["valid_from"],row["valid_to"],row["known_day"]):
                raise ValueError("RDF materializer changed source time fields")
            if not start<=v<finish:outside.append(row["id"])
            elif known_at>k:future.append(row["id"])
            else:eligible.append(row["id"])
        else:
            unknown.append(row["id"])
            if (a,RDF.type,TE.UnresolvedAvailabilityAssertion) not in g or (
                 a,TE.hasEvidenceClass,TE.OriginalPublicVersion) not in g:
                raise ValueError("original source's unresolved public availability not preserved")
            if list(g.objects(a,TE.validDuring)) or list(g.objects(a,TE.knownFrom)):
                raise ValueError("invented real historical valid interval or posting instant")
            if (a,TE.statusValue,Literal("recruiting",datatype=XSD.string)) not in g:
                raise ValueError("historical registry status changed")
            for prop,value,dtype in (
                 (TE.sourceReportedPostedDay,row["posted_day"],XSD.date),
                 (TE.submittedDay,row["submitted_day"],XSD.date),
                 (TE.observedDay,row["observed_day"],XSD.date),
                 (TE.sourceTextSHA256,row["source_text_sha256"],XSD.string),
                 (TE.sourceVersionId,"V94" if row["id"]=="ctgov-v94" else "V105",XSD.string)):
                node=owner if prop==TE.sourceVersionId else a
                if set(g.objects(node,prop))!={Literal(value,datatype=dtype)}:
                    raise ValueError("original registry version owner datum changed")
    # An independently parsed-graph oracle must agree with the deterministic
    # synthetic source model, without using its assertion filtering algorithm.
    expected=evaluate(bp,mode)
    if (eligible!=expected["eligible"] or future!=expected["withheld_future"]
        or outside!=expected["outside_validity"] or unknown!=expected["unresolved_validity"]):
        raise ValueError("RDF observation-level oracle differs from temporal engine")
    return {"schema":SCHEMA,"source_partition":mode,"rdf_triple_count":len(g),
        "source_assertion_count":len(ids),
        "source_derived_provenance_links":len(list(g.triples((None,PROV.wasDerivedFrom,None)))),
        "parsed_graph_query_oracle_agreed":True,
        "eligible":eligible,"withheld_future":future,"outside_validity":outside,
        "unresolved_validity":unknown,
        "original_real_publication_instant_authenticated":False if mode=="registry" else None,
        "owl_reasoning_claimed":False,"clinical_verdict":"NOT_EVALUATED",
        "sha256":sha256(rdf_text.encode()).hexdigest()}

def write_exports(bp,folder):
    validate(bp)
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    reports=[]
    for partition in ("synthetic","registry"):
        ttl=create_graph(bp,partition).serialize(format="turtle")
        evidence=independently_check_rdf(bp,partition,ttl)
        (folder/("world_"+partition+"_temporal_blueprint.ttl")).write_text(ttl)
        reports.append(evidence)
    (folder/"world_temporal_blueprint_rdf_receipt.json").write_text(
        json.dumps({"schema":SCHEMA,"partitions":reports,
                    "original_W13_source_modified":False,"official_NIH_submission":False},
                    indent=2,sort_keys=True)+"\n")
    return reports
