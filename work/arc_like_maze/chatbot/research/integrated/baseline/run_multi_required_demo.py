"""Reproduce explicit finite multi-edge scenarios with two separately pinned owners."""
import json
import test_ab_chatbot_evidence_prefilter as evidence
from ab_chatbot_multi_required import MultiTaskSession

GOALS=[[0,1,1],[0,2,0]]
CASES=(
 ('two_compatible_edges',[{'state':[0,0,0],'action':'B'},
                          {'state':[0,1,0],'action':'B'}]),
 ('distinct_conflicts',[{'state':[0,0,0],'action':'B'},
                        {'state':[1,2,0],'action':'B'}]),
 ('conjunction_unproved',[{'state':[0,0,0],'action':'B'},
                          {'state':[0,0,1],'action':'A'}]),
)

def run():
    out=[]
    for name,edges in CASES:
        helper=evidence.EvidencePrefilterTests()
        old,new=helper.make()
        try:
            session=MultiTaskSession(old,new,{'goals':GOALS,'required_edges':edges},
                                     **evidence.OPTIONS)
            for _ in range(45):
                report=session.advance(max_new_edges=108)
                if report.status not in ('SEARCHING','EVALUATING'):break
            else:raise RuntimeError('bounded run incomplete')
            agent=session.agent
            out.append({'case':name,'task_status':report.status,
                        'goals_carried':len(report.report.selected.carried)
                            if report.report.selected else None,
                        'selected_words':list(report.report.selected.words)
                            if report.report.selected else None,
                        'candidates_before':agent.before_filter,
                        'candidates_after':len(agent.selections),
                        'rejected_seed_certificates':len(agent.exclusions),
                        'certificate_actions':[
                            {'words':list(w),'required_state':list(e[0]),'required_action':e[1],
                             'cause':cert.cause,'observed_old_target':list(cert.observed_old_target),
                             'observed_new_target':list(cert.observed_new_target)}
                            for w,e,cert in agent.exclusions],
                        'unproved_by_candidate':[
                            {'words':list(w),'missing':[[list(s),a] for s,a in missing]}
                            for w,missing in agent.missing_by_trial],
                        'observed_old':report.report.observed_old,
                        'observed_new':report.report.observed_new,
                        'fingerprint':report.contract.fingerprint})
        finally:
            helper.doCleanups()
    return out

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
