"""Host-owned, deliberately limited as-known-at research scope verifier.

This validates a *synthetic* metadata timeline. It is not a clinical ontology,
medical inference, or a replacement for OWL-Time/PROV-O/Biolink.
"""
from __future__ import annotations

from datetime import date
import re

_ID = re.compile(r'[a-z][a-z0-9_-]{1,47}\Z')
_DAY = re.compile(r'\d{4}-\d{2}-\d{2}\Z')
APPLICATIONS = {'clinical-sequence', 'research-evidence', 'public-health'}
CP_ID = 'NIH-P1-SCOPE'
VERIFIER = 'cp-checker:NIH-P1-SCOPE'
WORKER_ROLE = 'research-scoper'


def _day(value: object) -> str:
    if type(value) is not str or not _DAY.fullmatch(value):
        raise ValueError('date must be YYYY-MM-DD')
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError('invalid calendar day') from exc
    if parsed.isoformat() != value:
        raise ValueError('noncanonical day')
    return value


def _id(value: object) -> str:
    if type(value) is not str or not _ID.fullmatch(value):
        raise ValueError('identifier must be a bounded lowercase token')
    return value


def validate_scope(data: object) -> dict:
    """Strictly synthetic scope, exact fields, no patient identifiers/free data."""
    keys = {'kind','synthetic','case_id','application','question','query_at','target_at','observations'}
    if type(data) is not dict or set(data) != keys:
        raise ValueError('scope requires exact declared fields')
    if data['kind'] != 'temporal-scope/v1' or data['synthetic'] is not True:
        raise ValueError('only explicit synthetic temporal scope is supported')
    case = _id(data['case_id'])
    if data['application'] not in APPLICATIONS:
        raise ValueError('unrecognized biomedical application category')
    question = data['question']
    if type(question) is not str or not 12 <= len(question) <= 220 or '\n' in question:
        raise ValueError('bounded one-line research question required')
    known = _day(data['query_at'])
    target = _day(data['target_at'])
    observations = data['observations']
    if type(observations) is not list or not 2 <= len(observations) <= 16:
        raise ValueError('2..16 bounded synthetic observations required')
    normalized, identifiers = [], set()
    for obs in observations:
        expected = {'id','subject','predicate','object','valid_from','valid_to','known_at','source_ref'}
        if type(obs) is not dict or set(obs) != expected:
            raise ValueError('observation must declare exact fields')
        oid = _id(obs['id'])
        if oid in identifiers:
            raise ValueError('duplicate observation id')
        identifiers.add(oid)
        fields = {name:_id(obs[name]) for name in ('subject','predicate','object','source_ref')}
        start,end,available = (_day(obs[k]) for k in ('valid_from','valid_to','known_at'))
        if not start < end:
            raise ValueError('validity end must follow start; half-open interval')
        normalized.append({'id':oid, **fields, 'valid_from':start,'valid_to':end,'known_at':available})
    normalized.sort(key=lambda row:row['id'])
    visible = [row['id'] for row in normalized
               if row['valid_from'] <= target < row['valid_to'] and row['known_at'] <= known]
    withheld = [row['id'] for row in normalized
                if row['valid_from'] <= target < row['valid_to'] and row['known_at'] > known]
    if not visible or not withheld:
        raise ValueError('test scope must expose both available and future-hidden facts')
    return {'kind':'temporal-scope/v1','synthetic':True,'case_id':case,
            'application':data['application'],'question':question,
            'query_at':known,'target_at':target,'observations':normalized}


def expected_scope_report(data: dict) -> dict:
    scope = validate_scope(data)
    target,cutoff = scope['target_at'],scope['query_at']
    eligible = [o['id'] for o in scope['observations']
                if o['valid_from'] <= target < o['valid_to'] and o['known_at'] <= cutoff]
    hidden = [o['id'] for o in scope['observations']
              if o['valid_from'] <= target < o['valid_to'] and o['known_at'] > cutoff]
    return {'case_id':scope['case_id'], 'query_at':cutoff, 'target_at':target,
            'visible_ids':eligible, 'withheld_future_ids':hidden,
            'synthetic':True, 'interpretation':'scope-only-as-known-at',
            'clinical_verdict':'NOT_EVALUATED'}