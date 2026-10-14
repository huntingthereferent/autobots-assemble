"""CP-28 owner-backed demonstration: share one route audit in one invocation."""
import json
from ab_chatbot_shared_route_certificate import SharedRouteTaskPortfolio
from test_ab_chatbot_route_bound_task import RouteBoundTaskTests


def main():
    self=RouteBoundTaskTests('runTest')
    refresh,_,left,right,_,reg,_,pin=self.fixture()
    t=self.task
    tasks={
        'left_a':t(refresh,'left',required_edges=[{'state':[1,0,0],'action':'B'}]),
        'left_b':t(refresh,'left',required_edges=[{'state':[1,1,2],'action':'A'}]),
        'right_a':t(refresh,'right',required_edges=[{'state':[0,1,2],'action':'B'}]),
        'left_unproved':t(refresh,'left',required_edges=[{'state':[0,1,2],'action':'B'}])}
    portfolio=SharedRouteTaskPortfolio(tasks)
    count={'left':0,'right':0}
    for name,route in [('left',left),('right',right)]:
        old=route.advance
        def wrap(_old=old,_name=name):
            count[_name]+=1
            return _old()
        route.advance=wrap
    record=portfolio.advance(force_tasks=tuple(tasks))
    assert count=={'left':2,'right':2}
    assert portfolio.last_route_audits==2
    assert [e.status for e in record.entries]==[
        'TASK_COMPLETED_ON_SELECTED_ROUTE','TASK_COMPLETED_ON_SELECTED_ROUTE',
        'TASK_COMPLETED_ON_SELECTED_ROUTE','ROUTE_TASK_REQUIREMENTS_UNPROVED']
    assert record.observations_before==record.observations_after
    assert record.entries[0].result.route_certificate is record.entries[1].result.route_certificate
    outputs={'stage':28,'experiment':'shared fresh route certificate across independent tasks',
        'local_integrated':True,'invocation':'explicit on-demand',
        'source_observations_added':0,'route_replay_calls':count,
        'unique_route_audits':portfolio.last_route_audits,
        'task_status':{e.name:e.status for e in record.entries},
        'shared_left_certificate':True,'separate_task_fingerprints':
            record.entries[0].result.task_fingerprint!=record.entries[1].result.task_fingerprint,
        'observations_unchanged':record.observations_before==record.observations_after}
    print(json.dumps(outputs,indent=2,sort_keys=True))

if __name__=='__main__':main()
