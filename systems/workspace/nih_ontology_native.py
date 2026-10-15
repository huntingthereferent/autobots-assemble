"""Host-owned RDF verifier for ONE synthetic Phase-1 ontology-mapping CP.

This tests explicit RDF vocabulary mapping, not OWL entailment or clinical reasoning.
The copied worker's implementation is never imported here.
"""
from __future__ import annotations

from datetime import date
import re
from rdflib import Graph, Namespace, RDF, RDFS, OWL, Literal
from rdflib.namespace import XSD
from .nih_scope_native import validate_scope, expected_scope_report

CP_ID = 'NIH-P1-ONTOLOGY'
WORKER_ROLE = 'ontology-builder'
VERIFIER = 'cp-checker:NIH-P1-ONTOLOGY'
EX = Namespace('https://example.org/nih-temporal-synthetic/')
TIME = Namespace('http://www.w3.org/2006/time#')
PROV = Namespace('http://www.w3.org/ns/prov#')
BIOLINK = Namespace('https://w3id.org/biolink/vocab/')
_ID = re.compile(r'[a-z][a-z0-9_-]{1,47}\Z')


def validate_request(data: object) -> dict:
    required = {'kind','synthetic','mapping_id','scope_job_id','format'}
    if type(data) is not dict or set(data) != required:
        raise ValueError('ontology job requires exact request fields')
    if data['kind'] != 'synthetic-temporal-ontology/v1' or data['synthetic'] is not True or data['format'] != 'turtle':
        raise ValueError('only synthetic RDF/Turtle ontology mapping is supported')
    for key in ('mapping_id','scope_job_id'):
        if type(data[key]) is not str or not _ID.fullmatch(data[key]):
            raise ValueError(f'unsafe {key}')
    return {key:data[key] for key in ('kind','synthetic','mapping_id','scope_job_id','format')}


def _d(day: str) -> Literal:
    return Literal(date.fromisoformat(day).isoformat(), datatype=XSD.date)


def expected_graph(scope: dict, mapping_id: str) -> Graph:
    """Independently build EXACT expected RDF graph from verified parent input."""
    scope = validate_scope(scope)
    if type(mapping_id) is not str or not _ID.fullmatch(mapping_id):
        raise ValueError('unsafe mapping id')
    g = Graph()
    for pref, ns in [('ex',EX),('time',TIME),('prov',PROV),('biolink',BIOLINK),('owl',OWL),('rdfs',RDFS),('xsd',XSD)]:
        g.bind(pref, ns)
    mapping = EX['mapping-'+mapping_id]
    g.add((mapping, RDF.type, OWL.Ontology))
    g.add((EX.TemporalObservation, RDF.type, OWL.Class))
    g.add((EX.TemporalObservation, RDFS.subClassOf, BIOLINK.InformationContentEntity))
    for rel, cls in ((EX.validDuring, TIME.Interval),(EX.knownFrom, TIME.Instant)):
        g.add((rel, RDF.type, OWL.ObjectProperty))
        g.add((rel, RDFS.range, cls))
    g.add((EX.eligibleAtQuery, RDF.type, OWL.DatatypeProperty))
    g.add((EX.eligibleAtQuery, RDFS.range, XSD.boolean))
    g.add((mapping, EX.queryAt, _d(scope['query_at'])))
    g.add((mapping, EX.targetAt, _d(scope['target_at'])))
    report = expected_scope_report(scope)
    for o in scope['observations']:
        stem=o['id']
        obs=EX['obs-'+stem]
        span=EX['valid-'+stem]
        start=EX['start-'+stem]
        end=EX['end-'+stem]
        known=EX['known-'+stem]
        source=EX['source-'+o['source_ref']]
        visible=stem in report['visible_ids']
        g.add((obs,RDF.type,EX.TemporalObservation))
        g.add((obs,EX.validDuring,span))
        g.add((obs,EX.knownFrom,known))
        g.add((obs,PROV.wasDerivedFrom,source))
        g.add((obs,EX.eligibleAtQuery,Literal(visible,datatype=XSD.boolean)))
        for field in ('subject','predicate','object'):
            g.add((obs,EX[field+'Token'],Literal(o[field])))
        g.add((span,RDF.type,TIME.Interval))
        g.add((span,TIME.hasBeginning,start))
        g.add((span,TIME.hasEnd,end))
        for instant, day in ((start,o['valid_from']),(end,o['valid_to']),(known,o['known_at'])):
            g.add((instant,RDF.type,TIME.Instant))
            g.add((instant,TIME.inXSDDate,_d(day)))
        g.add((source,RDF.type,PROV.Entity))
    return g


def verify_report(payload: object, *, scope: dict, mapping_id: str):
    if type(payload) is not dict or set(payload) != {'turtle','triple_count','visible_ids','withheld_future_ids','claim'}:
        raise ValueError('ontology report shape mismatch')
    text=payload['turtle']
    if type(text) is not str or not text or len(text.encode('utf-8')) > 60000:
        raise ValueError('missing or oversized Turtle')
    actual=Graph()
    try:
        actual.parse(data=text,format='turtle')
    except Exception as exc:
        raise ValueError('worker did not produce parsable RDF Turtle') from exc
    expected=expected_graph(scope,mapping_id)
    if set(actual) != set(expected) or type(payload['triple_count']) is not int or payload['triple_count'] != len(expected):
        raise ValueError('host independent RDF graph comparison rejected worker output')
    witness=expected_scope_report(scope)
    if (payload['visible_ids'] != witness['visible_ids']
            or payload['withheld_future_ids'] != witness['withheld_future_ids']
            or payload['claim'] != 'synthetic-ontology-mapping-only'):
        raise ValueError('ontology availability claim disagrees with verified scope')
    return {'triple_count':len(expected),'mapping_id':mapping_id,
            'visible_ids':witness['visible_ids'],'withheld_future_ids':witness['withheld_future_ids']}