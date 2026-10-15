"""Source-independent W13 composition verifier using preserved W12 native rules.

The worker's new multi-world implementation is NOT imported here. The native
reference is byte-identical to the W12 candidate, pinned by SHA-256.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import json
from . import game_w12_reference as w12

CP_ID='GAME-W13-WORLDS'
VERIFIER='cp-checker:GAME-W13-WORLDS'
WORKER_ROLE='game-build'
CONTRACT='game-w13-multiworld-v1'
W12_SHA256='dcf457efd0bf9bd93823ad862e8f1f315b20f46334dd323a1d467a820c3f5ac1'


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)


def validate_request(obj: object) -> dict:
    if type(obj) is not dict or set(obj) != {'contract','worlds','actions'} or obj.get('contract')!=CONTRACT:
        raise ValueError('W13 exact contract required')
    worlds,actions=obj['worlds'],obj['actions']
    if type(worlds) is not list or not 2<=len(worlds)<=4:
        raise ValueError('W13 requires two to four worlds')
    if type(actions) is not list or not 3<=len(actions)<=150 or any(type(x)is not str or x not in w12.ACTIONS | {'advance'} for x in actions):
        raise ValueError('invalid bounded W13 actions')
    names=set(); canon_worlds=[]
    for item in worlds:
        if type(item) is not dict or set(item) != {'id','spec'}:
            raise ValueError('world requires exact id/spec')
        name=item['id']
        if type(name)is not str or not name.isascii() or not 1<=len(name)<=32 or not all(z.isalnum() or z in '-_' for z in name) or name in names:
            raise ValueError('invalid or duplicate world ID')
        names.add(name)
        s=item['spec']
        if type(s)is not dict or set(s) != {'width','height','start','target'}:
            raise ValueError('invalid world spec fields')
        if any(type(s[k]) is not int for k in ['width','height']):
            raise ValueError('world dimensions must be integer')
        if any(type(s[k]) is not list or len(s[k])!=2 or any(type(z) is not int for z in s[k]) for k in ('start','target')):
            raise ValueError('world coordinates must be integral pairs')
        w12.GameSpec(s['width'],s['height'],tuple(s['start']),tuple(s['target'])).validate()
        canon_worlds.append({'id':name,'spec':dict(s)})
    if len(set(canonical(item['spec']) for item in worlds))<2:
        raise ValueError('W13 must include at least two distinct world specifications')
    return {'contract':CONTRACT,'worlds':canon_worlds,'actions':list(actions)}


def expected_report(request: dict) -> dict:
    """Check sequence and per-world W12 traces independently from new engine.

    Every ADVANCE is an explicit operation that requires a solved prior world.
    Collecting after the last advance is mandatory for successful W13 witness.
    """
    req=validate_request(request)
    worlds,actions=req['worlds'],req['actions']
    segments=[[] for _ in worlds]
    at=0
    for action in actions:
        if action=='advance':
            if at>=len(worlds)-1:
                raise ValueError('W13 cannot advance beyond last world')
            item=worlds[at]['spec']
            local=w12.run_actions(segments[at],w12.GameSpec(item['width'],item['height'],tuple(item['start']),tuple(item['target'])))
            w12.verify_trace(local)
            if not local['solved']:
                raise ValueError('advance before world completion')
            at+=1
        else:
            segments[at].append(action)
    if at!=len(worlds)-1:
        raise ValueError('W13 did not reach every world')
    results=[]
    for item,segment in zip(worlds,segments):
        spec=item['spec']
        trace=w12.run_actions(segment,w12.GameSpec(spec['width'],spec['height'],tuple(spec['start']),tuple(spec['target'])))
        w12.verify_trace(trace)
        if not trace['solved']:
            raise ValueError('W13 unsolved world')
        results.append({'world_id':item['id'],'trace':trace})
    return {'version':CONTRACT,'worlds':results,'worlds_completed':len(results),
            'last_world':worlds[-1]['id'],'solved':True,
            'boundary':'W13 composition over byte-preserved W12 native rules'}


def check_preserved_reference():
    original=Path(w12.__file__).read_bytes()
    if sha256(original).hexdigest()!=W12_SHA256:
        raise ValueError('W12 reference modified from source candidate')
    return True