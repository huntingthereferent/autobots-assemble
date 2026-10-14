"""Reproduce finite mixed-obligation outcomes against independent local owners."""
import json
from dataclasses import asdict
from pathlib import Path

from ab_chatbot_mixed_obligations import MixedTaskSession
from test_ab_chatbot_mixed_obligations import TASK, EDGE_B, completed
from test_ab_chatbot_evidence_prefilter import EvidencePrefilterTests, OPTIONS


def main():
    output=[]
    for name, task in (
        ('all_three_types',TASK),
        ('incompatible_requirements',{**TASK,'required_edges':[EDGE_B]}),
        ('inconsistent_task',{**TASK,'required_destinations':[{'source':[0,1,1],'image':[0,2,0]}]}),
        ('ambiguous_task','keep the paths and destinations')
    ):
        owners=EvidencePrefilterTests()
        old,new=owners.make()
        try:
            session=MixedTaskSession(old,new,task,**OPTIONS)
            outcome=session.advance(max_new_edges=108)
            if session.agent is not None:
                for _ in range(48):
                    if outcome.status not in ('SEARCHING','EVALUATING'):
                        break
                    outcome=session.advance(max_new_edges=108)
            assert outcome.status not in ('SEARCHING','EVALUATING')
            output.append({'case':name,'status':outcome.status,
                'contract_fingerprint':outcome.contract.fingerprint if outcome.contract else None,
                'observed_old':len(old.snapshot.edges),'observed_new':len(new.snapshot.edges),
                'selected_words':list(outcome.report.selected.words) if outcome.report and outcome.report.selected else None,
                'goals_carried':len(outcome.report.selected.carried) if outcome.report and outcome.report.selected else 0,
                'candidate_checks':[
                    {'words':list(words),'checks':[
                        {'type':r.kind,'satisfied':r.satisfied,'detail':r.detail} for r in checks]}
                     for words,checks in outcome.obligations]})
        finally:
            owners.doCleanups()
    dest=Path(__file__).with_name('MIXED_OBLIGATION_RESULTS.json')
    dest.write_text(json.dumps(output,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps([{k:v for k,v in r.items() if k!='candidate_checks'} for r in output],indent=2))
    print('Detailed per-candidate certificates:',dest)

if __name__=='__main__':main()
