"""Witness-bound, replayable 19,683-law family-specific Continuity classification.

Does NOT claim to recognize all arbitrary finite A/B actions. An unknown
feature prefix cannot become 'conjugate' from histogram agreement alone.
"""
from hashlib import sha256
from dataclasses import dataclass
import json
from .core import (valid_law, fingerprint, orbit_RS, R, S, A, B,
                  STATE_R, STATE_S, SELECTED_FEATURES)

SCHEMA=1
AREA='finite_action/F3_5_all_fifth_couplings'
RELATION='FULL_LABEL_PRESERVING_AB_CONJUGACY'
UNKNOWN='UNKNOWN_FEATURE_BUDGET'
NEGATIVE='NONCONJUGATE_AB_BY_ORBIT_INCIDENCE'
POSITIVE='CONJUGATE_AB_BY_VERIFIED_R_S'

def _json(x):return json.dumps(x,sort_keys=True,separators=(',',':'))

def _digest(x):return sha256(_json(x).encode()).hexdigest()

def _mapping(q,target):
    cur=q
    for k in range(9):
        for scale in range(2):
            endpoint=cur if scale==0 else S(cur)
            if endpoint==target:
                mapping=list(range(243))
                for _ in range(k):mapping=[STATE_R[x] for x in mapping]
                if scale:mapping=[STATE_S[x] for x in mapping]
                aa=B(q);bb=B(target)
                assert len(set(mapping))==243
                assert all(mapping[A[x]]==A[mapping[x]] and
                           mapping[aa[x]]==bb[mapping[x]] for x in range(243))
                return {'R_power':k,'S_power':scale,'mapping':mapping}
        cur=R(cur)
    return None

@dataclass(frozen=True)
class ResearchRecord:
    record: dict
    @property
    def status(self):return self.record['status']
    @property
    def question_id(self):return self.record['question_id']
    def serialize(self):return _json(self.record)

class ContinuityFifthCouplingClassifier:
    """Exact replayable area adapter; the classified family is an explicit contract."""
    @staticmethod
    def start(source,target,max_features=4):
        q=valid_law(source);p=valid_law(target)
        if type(max_features)!=int or not 1<=max_features<=4:
            raise ValueError('positive feature budget in 1..4 required')
        question={'area':AREA,'relation':RELATION,
            'state_space':'F3^5','source_table':list(q),'target_table':list(p),
            'features':[{'p':a,'q':b,'r':c} for a,b,c in SELECTED_FEATURES]}
        identifier=_digest(question)
        source_fp,target_fp=fingerprint(q),fingerprint(p)
        observations=[];obstruction=None
        for i in range(max_features):
            observations.append({'feature':i+1,
                'source_histogram':[list(x) for x in source_fp[i]],
                'target_histogram':[list(x) for x in target_fp[i]]})
            if source_fp[i]!=target_fp[i]:
                obstruction=i+1;break
        positive=_mapping(q,p) if obstruction is None else None
        if obstruction is not None:status=NEGATIVE
        elif positive is not None:status=POSITIVE
        else:status=UNKNOWN
        if status==UNKNOWN and max_features==4:
            raise AssertionError('complete four-feature class theorem contradicted by input')
        return ResearchRecord({'schema':SCHEMA,'question':question,'question_id':identifier,
            'max_features':max_features,'status':status,
            'observations':observations,'first_obstruction_feature':obstruction,
            'positive_full_AB_witness':positive,
            'scope_note':'ONLY the fixed 243-state, 19683-law F3^5 fifth-coordinate coupling grammar'})

    @staticmethod
    def replay(serialized,*,expected_question_id=None):
        try:
            raw=json.loads(serialized)
            if not isinstance(raw,dict) or set(raw)!={
                'schema','question','question_id','max_features','status',
                'observations','first_obstruction_feature','positive_full_AB_witness','scope_note'}:
                raise ValueError('unknown record fields')
            q=raw['question']
            if raw['schema']!=SCHEMA or q['area']!=AREA or q['relation']!=RELATION or \
               q['state_space']!='F3^5' or q['features']!=[
                {'p':a,'q':b,'r':c} for a,b,c in SELECTED_FEATURES]:
                raise ValueError('question identity/scope changed')
            if (raw['question_id']!=_digest(q) or
                (expected_question_id is not None and expected_question_id!=raw['question_id'])):
                raise ValueError('question anchor changed')
            real=ContinuityFifthCouplingClassifier.start(
                q['source_table'],q['target_table'],raw['max_features'])
            if real.serialize()!=_json(raw):raise ValueError('witness failed mathematical replay')
            return real
        except (json.JSONDecodeError,TypeError,KeyError,IndexError) as exc:
            raise ValueError('invalid saved mathematical record') from exc

    @staticmethod
    def resume(serialized,max_features,*,expected_question_id=None):
        prior=ContinuityFifthCouplingClassifier.replay(serialized,expected_question_id=expected_question_id)
        if type(max_features)!=int or max_features<prior.record['max_features'] or max_features>4:
            raise ValueError('feature budget must not decrease')
        if prior.status!=UNKNOWN:return prior
        q=prior.record['question']
        later=ContinuityFifthCouplingClassifier.start(q['source_table'],q['target_table'],max_features)
        if later.record['observations'][:len(prior.record['observations'])]!=prior.record['observations']:
            raise AssertionError('earlier observation ancestry was lost')
        return later
