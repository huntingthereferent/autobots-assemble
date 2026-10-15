"""Source-owned isolated synthetic RDF/Turtle constructor; never a clinical agent."""
from __future__ import annotations
import json
import os
import sys
from datetime import date

P='https://example.org/nih-temporal-synthetic/'
T='http://www.w3.org/2006/time#'
R='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
O='http://www.w3.org/2002/07/owl#'
S='http://www.w3.org/2000/01/rdf-schema#'
X='http://www.w3.org/2001/XMLSchema#'
V='http://www.w3.org/ns/prov#'
B='https://w3id.org/biolink/vocab/'

def uri(fragment):return '<'+P+fragment+'>'
def std(prefix,part): return '<'+prefix+part+'>'
def lit(v):return json.dumps(v,ensure_ascii=True)
def day(d):return lit(date.fromisoformat(d).isoformat())+'^^'+std(X,'date')
def boolean(value):return ('"true"' if value else '"false"')+'^^'+std(X,'boolean')

def render(request,scope):
    cutoff,target=scope['query_at'],scope['target_at']
    rows=[]
    def add(a,b,c):rows.append(a+' '+b+' '+c+' .')
    rdftype=std(R,'type')
    ob=uri('TemporalObservation')
    name=uri('mapping-'+request['mapping_id'])
    add(name,rdftype,std(O,'Ontology'))
    add(ob,rdftype,std(O,'Class'))
    add(ob,std(S,'subClassOf'),std(B,'InformationContentEntity'))
    for prop,domain in [('validDuring','Interval'),('knownFrom','Instant')]:
        add(uri(prop),rdftype,std(O,'ObjectProperty'))
        add(uri(prop),std(S,'range'),std(T,domain))
    add(uri('eligibleAtQuery'),rdftype,std(O,'DatatypeProperty'))
    add(uri('eligibleAtQuery'),std(S,'range'),std(X,'boolean'))
    add(name,uri('queryAt'),day(cutoff))
    add(name,uri('targetAt'),day(target))
    visible=[]; withheld=[]
    for obs in sorted(scope['observations'],key=lambda x:x['id']):
        stem=obs['id']
        ident=uri('obs-'+stem)
        period=uri('valid-'+stem)
        begins=uri('start-'+stem)
        ends=uri('end-'+stem)
        knowledge=uri('known-'+stem)
        source=uri('source-'+obs['source_ref'])
        active=obs['valid_from']<=target<obs['valid_to']
        is_visible=active and obs['known_at']<=cutoff
        if is_visible: visible.append(stem)
        if active and obs['known_at']>cutoff: withheld.append(stem)
        add(ident,rdftype,ob)
        add(ident,uri('validDuring'),period)
        add(ident,uri('knownFrom'),knowledge)
        add(ident,std(V,'wasDerivedFrom'),source)
        add(ident,uri('eligibleAtQuery'),boolean(is_visible))
        for key in ('subject','predicate','object'):
            add(ident,uri(key+'Token'),lit(obs[key]))
        add(period,rdftype,std(T,'Interval'))
        add(period,std(T,'hasBeginning'),begins)
        add(period,std(T,'hasEnd'),ends)
        for instant,when in ((begins,obs['valid_from']),(ends,obs['valid_to']),(knowledge,obs['known_at'])):
            add(instant,rdftype,std(T,'Instant'))
            add(instant,std(T,'inXSDDate'),day(when))
        add(source,rdftype,std(V,'Entity'))
    turtle='\n'.join(rows)+'\n'
    return {'turtle':turtle,'triple_count':len(set(rows)),
            'visible_ids':visible,'withheld_future_ids':withheld,
            'claim':'synthetic-ontology-mapping-only'}

if __name__=='__main__':
    obj=json.load(sys.stdin)
    print(json.dumps({'pid':os.getpid(),'report':render(obj['request'],obj['scope'])},sort_keys=True))