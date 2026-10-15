"""Host-owned CP-specific temporal reasoning verifier for bounded synthetic RDF evidence.

This is a closed-world, explicitly functional-predicate test, NOT clinical
reasoning, OWL entailment, disease prediction, or a general KG reasoner.
"""
from __future__ import annotations
from datetime import date
import re

from .nih_scope_native import validate_scope
from .nih_ontology_native import verify_report

CP_ID = 'NIH-P1-REASONING'
WORKER_ROLE = 'temporal-witness'
VERIFIER = 'cp-checker:NIH-P1-REASONING'
_ID = re.compile(r'[a-z][a-z0-9_-]{1,47}\Z')
_DATE = re.compile(r'\d{4}-\d{2}-\d{2}\Z')


def _date(value):
    if type(value) is not str or not _DATE.fullmatch(value):
        raise ValueError('expected canonical date')
    try:
        if date.fromisoformat(value).isoformat() != value:
            raise ValueError('noncanonical day')
    except ValueError as exc:
        raise ValueError('invalid calendar day') from exc
    return value


def _id(value):
    if type(value) is not str or not _ID.fullmatch(value):
        raise ValueError('invalid bounded identifier')
    return value


def validate_request(value):
    if type(value) is not dict or set(value) != {'kind','synthetic','ontology_job_id','cases','functional_predicates'}:
        raise ValueError('exact temporal reasoning request fields required')
    if value['kind'] != 'synthetic-temporal-reasoning/v1' or value['synthetic'] is not True:
        raise ValueError('synthetic reasoning contract only')
    parent = _id(value['ontology_job_id'])
    cases = value['cases']
    if type(cases) is not list or not (2 <= len(cases) <= 8):
        raise ValueError('two to eight temporal queries required')
    result = []
    used = set()
    for item in cases:
        if type(item) is not dict or set(item) != {'id','known_at','target_at'}:
            raise ValueError('each case requires id, known_at, target_at')
        key = _id(item['id'])
        if key in used: raise ValueError('duplicate temporal case')
        used.add(key)
        result.append({'id':key,'known_at':_date(item['known_at']),'target_at':_date(item['target_at'])})
    preds = value['functional_predicates']
    if type(preds) is not list or not (1 <= len(preds) <= 8):
        raise ValueError('explicit functional-predicate declarations required')
    funcs = sorted({_id(v) for v in preds})
    if len(funcs) != len(preds): raise ValueError('duplicate functional predicate')
    return {'kind':'synthetic-temporal-reasoning/v1','synthetic':True,
            'ontology_job_id':parent,'cases':sorted(result,key=lambda v:v['id']),
            'functional_predicates':funcs}


def expected_reasoning_report(request, scope):
    """Independent host evaluation from *native validated scope*, not child's RDF algorithm."""
    req = validate_request(request)
    obs = validate_scope(scope)['observations']
    out = []
    for case in req['cases']:
        cutoff, target = case['known_at'],case['target_at']
        present = [o for o in obs if o['valid_from'] <= target < o['valid_to']]
        active = [o for o in present if o['known_at'] <= cutoff]
        unavailable = [o for o in present if o['known_at'] > cutoff]
        # Predicate-specific exclusivity is EXPLICITLY declared; no inference
        # that generic biomedical predicates are functional.
        conflicts = []
        for pred in req['functional_predicates']:
            for i,a in enumerate(active):
                if a['predicate'] != pred:continue
                for b in active[i+1:]:
                    if b['subject']==a['subject'] and b['predicate']==pred and b['object']!=a['object']:
                        conflicts.append([min(a['id'],b['id']),max(a['id'],b['id'])])
        out.append({'id':case['id'],'known_at':cutoff,'target_at':target,
                    'admissible':sorted(o['id'] for o in active),
                    'withheld_future':sorted(o['id'] for o in unavailable),
                    'not_applicable':sorted(o['id'] for o in obs if o not in present),
                    'declared_conflicts':sorted(conflicts)})
    return {'kind':'synthetic-as-known-at-reasoning/v1','cases':out,
            'functional_predicates':req['functional_predicates'],
            'conclusion':'synthetic-temporal-logic-only'}


def verify_reasoning_report(report, *, request, scope, ontology_report, mapping_id):
    if type(report) is not dict or set(report) != {'kind','cases','functional_predicates','conclusion'}:
        raise ValueError('temporal reasoning report shape mismatch')
    # The parent RDF is independently re-parsed and checked before any child
    # temporal claim can be attributed to it.
    verify_report(ontology_report,scope=scope,mapping_id=mapping_id)
    expected=expected_reasoning_report(request,scope)
    if report != expected:
        raise ValueError('host temporal reasoning witness rejected result')
    return {'case_count':len(expected['cases']),'declared_conflict_cases':sum(bool(c['declared_conflicts']) for c in expected['cases']),
            'verdict':'PASS'}