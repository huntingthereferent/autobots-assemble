"""Replay selective audit of two independent owner-pinned route comparisons."""
import json
import unittest
from ab_chatbot_source_change_propagation import SourceChangePropagation
from ab_chatbot_selective_propagation import SelectivePropagationPortfolio
from test_ab_chatbot_two_route_comparison import TwoRouteTests


def main():
    case=unittest.TestCase()
    records={}; fixtures={}
    for i in (0,1):
        cmp,left,right,middle,registry,oldpin,newpin=TwoRouteTests.fixture(case,same_middle=(i==1))
        h=SourceChangePropagation(cmp)
        assert h.advance().status=='BASELINE_WITNESSED'
        name=f'portfolio_{i}'
        records[name]=h;fixtures[name]=(cmp,left,right,middle,registry,oldpin,newpin)
    ledger=SelectivePropagationPortfolio(records)
    no_change=ledger.advance()
    fixtures['portfolio_0'][4].revoke(fixtures['portfolio_0'][6].token)
    changed=ledger.advance()
    forced=ledger.verify_for_use('portfolio_1')
    def show(report):
        return {'audited':list(report.audited),'skipped':list(report.skipped),
                'changed':[[name,scope,list(causes)] for name,scope,causes in report.changed_dependencies],
                'records':[{'name':r.name,'mode':r.mode,'outcome':r.outcome,
                            'fresh_proof':r.proof_fresh} for r in report.records],
                'new_observations':report.owner_observations_before!=report.owner_observations_after}
    return {'stable':show(no_change),'revoked_only_first':show(changed),
            'explicit_proof_for_other':{'name':forced.name,'outcome':forced.outcome,
                                        'mode':forced.mode,'fresh_proof':forced.proof_fresh},
            'number_of_audits':{name:len(h.history) for name,h in records.items()}}


if __name__=='__main__':print(json.dumps(main(),indent=2))
