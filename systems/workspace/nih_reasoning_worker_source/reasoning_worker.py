"""Isolated CP-native RDF temporal query worker; **synthetic evidence only**.

Child computes from parsed RDF graph, not from the parent's scope records.
The host verifier independently computes from original parent scope records.
"""
from __future__ import annotations
import json, os, sys
from collections import defaultdict
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, XSD

EX=Namespace('https://example.org/nih-temporal-synthetic/')
TIME=Namespace('http://www.w3.org/2006/time#')


def _day(g, instant):
    values=list(g.objects(instant,TIME.inXSDDate))
    if len(values)!=1:return None
    v=values[0]
    return str(v) if isinstance(v,Literal) and v.datatype==XSD.date else None


def rdf_observations(turtle):
    g=Graph()
    g.parse(data=turtle,format='turtle')
    items=[]
    for uri in g.subjects(RDF.type,EX.TemporalObservation):
        get=lambda predicate:list(g.objects(uri,predicate))
        ids=str(uri).removeprefix(str(EX)+'obs-')
        for key in ('subject','predicate','object'):
            if len(get(EX[key+'Token']))!=1:raise ValueError('RDF statement token absent')
        source=get(EX.validDuring)
        known=get(EX.knownFrom)
        if len(source)!=1 or len(known)!=1: raise ValueError('invalid RDF temporal relation')
        starts=list(g.objects(source[0],TIME.hasBeginning))
        ends=list(g.objects(source[0],TIME.hasEnd))
        if len(starts)!=1 or len(ends)!=1: raise ValueError('invalid RDF interval')
        valid_from,valid_to,available=_day(g,starts[0]),_day(g,ends[0]),_day(g,known[0])
        if None in (valid_from,valid_to,available): raise ValueError('RDF temporal value missing')
        items.append({'id':ids,'subject':str(get(EX.subjectToken)[0]),
                      'predicate':str(get(EX.predicateToken)[0]),'object':str(get(EX.objectToken)[0]),
                      'valid_from':valid_from,'valid_to':valid_to,'known_at':available})
    if not items: raise ValueError('no RDF observations')
    return items


def compute(request, turtle):
    observations = rdf_observations(turtle)
    cases=[]
    for query in request['cases']:
        current, target=query['known_at'],query['target_at']
        present=[o for o in observations if o['valid_from']<=target<o['valid_to']]
        usable=[o for o in present if o['known_at']<=current]
        hidden=[o for o in present if o['known_at']>current]
        collisions=set()
        by_key=defaultdict(list)
        for o in usable:
            if o['predicate'] in request['functional_predicates']:
                by_key[o['subject'],o['predicate']].append(o)
        for group in by_key.values():
            for i,left in enumerate(group):
                for right in group[i+1:]:
                    if left['object']!=right['object']:
                        collisions.add(tuple(sorted((left['id'],right['id']))))
        cases.append({'id':query['id'],'known_at':current,'target_at':target,
                      'admissible':sorted(x['id'] for x in usable),
                      'withheld_future':sorted(x['id'] for x in hidden),
                      'not_applicable':sorted(x['id'] for x in observations if x not in present),
                      'declared_conflicts':[list(p) for p in sorted(collisions)]})
    return {'kind':'synthetic-as-known-at-reasoning/v1','cases':sorted(cases,key=lambda x:x['id']),
            'functional_predicates':request['functional_predicates'],
            'conclusion':'synthetic-temporal-logic-only'}

if __name__=='__main__':
    payload=json.load(sys.stdin)
    result=compute(payload['request'],payload['ontology_turtle'])
    print(json.dumps({'pid':os.getpid(),'report':result},sort_keys=True))