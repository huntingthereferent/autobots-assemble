"""Reproduce explicit-vs-absent required-edge behavior using local owner fixtures."""
import json
from ab_chatbot_task_contract import TaskContractSession
from test_ab_chatbot_evidence_prefilter import EvidencePrefilterTests, GOALS, OPTIONS


def scenario(task):
    helper = EvidencePrefilterTests()
    try:
        old,new = helper.make()
        session = TaskContractSession(old,new,task,**OPTIONS)
        for _ in range(40):
            result = session.advance(max_new_edges=108)
            if result.status not in ('SEARCHING','EVALUATING'):
                break
        return {'status': result.status,
                'required_edge': session.intake.contract.required_edge if session.intake.contract else None,
                'goal_count': len(result.report.selected.carried) if result.report and result.report.selected else 0,
                'candidate_evaluations': len(session.agent.finished) if session.agent else 0,
                'owner_observations': [result.report.observed_old, result.report.observed_new] if result.report else [0,0],
                'task_hash': session.intake.contract.fingerprint if session.intake.contract else None}
    finally:
        helper.doCleanups()


def main():
    goals_only = {'goals': [[0,1,1],[0,2,0]]}
    explicit_edge = {'goals': [[0,1,1],[0,2,0]],
                     'required_edge': {'state': [0,0,0], 'action':'B'}}
    report = {'goals_only':scenario(goals_only),
              'explicit_edge':scenario(explicit_edge),
              'ambiguous':scenario('keep B while solving the goals')}
    print(json.dumps(report, indent=2))

if __name__=='__main__':main()
