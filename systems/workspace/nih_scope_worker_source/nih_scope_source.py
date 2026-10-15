"""Standalone bounded source edition: synthetic as-known-at query, never clinical inference."""
import json
import os
import re
import sys
from datetime import date


def run(value):
    required = {'kind','synthetic','case_id','application','question','query_at','target_at','observations'}
    if not isinstance(value,dict) or set(value)!=required or value['kind']!='temporal-scope/v1' or value['synthetic'] is not True:
        raise ValueError('unsupported scope')
    def is_day(x):
        if type(x) is not str or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',x) or date.fromisoformat(x).isoformat()!=x:
            raise ValueError('noncanonical date')
        return x
    query,target=is_day(value['query_at']),is_day(value['target_at'])
    seen,visible,hidden=set(),[],[]
    for row in value['observations']:
        if set(row) != {'id','subject','predicate','object','source_ref','known_at','valid_from','valid_to'}:
            raise ValueError('invalid observation')
        oid=row['id']
        if oid in seen: raise ValueError('repeated observation')
        seen.add(oid)
        start,end,known=map(is_day,(row['valid_from'],row['valid_to'],row['known_at']))
        if not start < end: raise ValueError('invalid validity')
        if start <= target < end:
            (visible if known <= query else hidden).append(oid)
    if not visible or not hidden: raise ValueError('not a temporal leakage fixture')
    return {'case_id':value['case_id'],'query_at':query,'target_at':target,
            'visible_ids':sorted(visible),'withheld_future_ids':sorted(hidden),
            'synthetic':True,'interpretation':'scope-only-as-known-at',
            'clinical_verdict':'NOT_EVALUATED'}


if __name__ == '__main__':
    try:
        data=json.load(sys.stdin)
        print(json.dumps({'report':run(data),'pid':os.getpid()},sort_keys=True))
    except (ValueError,TypeError,KeyError) as exc:
        print(str(exc),file=sys.stderr)
        sys.exit(1)