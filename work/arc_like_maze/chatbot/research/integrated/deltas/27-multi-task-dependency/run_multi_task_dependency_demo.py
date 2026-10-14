"""Reproduce a three-task/shared-source selective replay against real local pins."""
import json
import unittest
from ab_chatbot_multi_task_dependency import MultiRouteTaskDependencies
from test_ab_chatbot_route_bound_task import RouteBoundTaskTests


def main():
    case=unittest.TestCase()
    refresh,comparison,left,right,middle,registry,pold,pnew=RouteBoundTaskTests.fixture(case)
    mk=RouteBoundTaskTests.task
    tasks={
        'left_a':mk(case,refresh,'left',required_edges=[{'state':[1,0,0],'action':'B'}]),
        'left_b':mk(case,refresh,'left',required_edges=[{'state':[1,1,2],'action':'A'}]),
        'right_a':mk(case,refresh,'right',required_edges=[{'state':[0,1,2],'action':'B'}]),
    }
    ledger=MultiRouteTaskDependencies(tasks)
    def show(r):
        return {'status':r.status,'epoch':r.epoch,'changed_sources':r.changed_sources,
          'audited':r.audited,'cached':r.cached,
          'tasks':{e.name:{'status':e.status,'mode':e.mode,
                    'fresh':e.fresh,'proof_for_use':e.proof_for_use,
                    'sources':e.source_ids} for e in r.entries},
          'observations_before':r.observations_before,
          'observations_after':r.observations_after}
    baseline=show(ledger.history[0])
    idle=show(ledger.advance())
    registry.revoke(pnew.token)
    after_right=show(ledger.advance())
    left_still_usable=ledger.verify_for_use('left_a')
    left_use={'status':left_still_usable.status,'proof_for_use':left_still_usable.proof_for_use}
    left.final.old.snapshot.revision+=1
    after_shared=show(ledger.advance())
    output={'experiment':'Multi-route task dependency propagation','date':'2026-10-13',
      'method':'on-demand real owner/snapshot audits; no background polling',
      'dependencies':ledger.dependencies(),
      'baseline':baseline,'no_change':idle,'right_middle_revocation':after_right,
      'left_task_explicit_use':left_use,'shared_final_revision_change':after_shared,
      'task_results_are_not_merged':True}
    if not (after_right['audited']==('right_a',) and
            after_shared['audited']==('left_a','left_b','right_a') and
            left_use['proof_for_use'] and
            after_right['observations_before']==after_right['observations_after']):
        raise AssertionError('demo results do not satisfy expected selective propagation')
    print(json.dumps(output,indent=2))

if __name__=='__main__':main()
