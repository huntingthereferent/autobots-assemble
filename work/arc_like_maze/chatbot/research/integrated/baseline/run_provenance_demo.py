"""Bounded local vs remote provenance demonstration, preserving owner evidence."""
import json
from pathlib import Path
from test_ab_chatbot_mixed_obligations import TASK
from ab_chatbot_provenance_contract import ProvenanceTaskSession,LOCAL
import test_ab_chatbot_evidence_prefilter as fixture


def run_case(label, task, remote_new=False, remove_owner=False):
    helper=fixture.EvidencePrefilterTests()
    old,new=helper.make(remote_new=remote_new)
    try:
        session=ProvenanceTaskSession(old,new,task,**fixture.OPTIONS)
        result=None
        for _ in range(50):
            result=session.advance(max_new_edges=108)
            if result.status not in ('SEARCHING','EVALUATING'):
                break
        assert result.status not in ('SEARCHING','EVALUATING'), label
        first={'label':label,'status':result.status,
            'declared_proofs':[(p.side,p.required,p.observed,p.satisfied)
                               for p in result.source_proofs],
            'observed_old':len(old.snapshot.edges), 'observed_new':len(new.snapshot.edges),
            'goals': (len(result.base_outcome.report.selected.carried) if
                      result.base_outcome is not None and getattr(result.base_outcome,'report',None) is not None and
                      result.base_outcome.report.selected is not None else 0)}
        if remove_owner:
            new.owner=None
            reread=session.advance(max_new_edges=0)
            first['after_owner_removed']=reread.status
        return first
    finally:
        helper.doCleanups()


def main():
    cases=[run_case('both_local', {**TASK,'required_provenance':{'old':LOCAL,'new':LOCAL}}),
           run_case('new_unverified', {**TASK,'required_provenance':{'old':LOCAL,'new':LOCAL}},remote_new=True),
           run_case('old_only_remote_new', {**TASK,'required_provenance':{'old':LOCAL}},remote_new=True),
           run_case('binding_revocation', {**TASK,'required_provenance':{'old':LOCAL}},remove_owner=True),
           run_case('unrecognized_words','please use verified sources')]
    dest=Path(__file__).with_name('PROVENANCE_CONTRACT_RESULTS.json')
    dest.write_text(json.dumps(cases,indent=2,sort_keys=True)+'\n')
    print(json.dumps(cases,indent=2))

if __name__=='__main__':main()
