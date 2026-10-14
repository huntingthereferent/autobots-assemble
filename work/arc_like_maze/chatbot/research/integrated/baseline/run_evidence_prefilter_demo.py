"""Reproduce the scoped required-edge task with independent pinned owners."""
from ab_chatbot_post_extension_portfolio import PostExtensionPortfolio
from ab_chatbot_evidence_prefilter import RequiredEdgePortfolio
from test_ab_chatbot_path_union import PathUnionTests

GOALS=((0,1,1),(0,2,0))
OPTIONS=dict(max_depth=6,variants_per_goal=4,candidate_limit=7,max_trials=12)


def run(cls):
    fixture=PathUnionTests()
    try:
        _,old,new,_,_=fixture.make((0,0,1),(0,0,0),depth=0,budget=54)
        kw=dict(OPTIONS)
        if cls is RequiredEdgePortfolio:
            kw['required_edge']=((0,0,0),'B')
        agent=cls(old,new,GOALS,**kw)
        for _ in range(40):
            report=agent.advance(max_new_edges=108)
            if report.status not in ('SEARCHING','EVALUATING'):
                break
        else:
            raise RuntimeError('bounded experiment did not terminate')
        eligible=[(trial,ext) for trial,ext in zip(agent.finished,agent._extenders)
                  if ((0,0,0),'B') in ext.edges]
        chosen=max((t for t,_ in eligible),key=lambda t:(len(t.carried),
                   t.admitted_edges,t.paired_states,-t.excluded_edges,
                   tuple((-len(w),w) for w in t.words)))
        return dict(trials=len(agent.finished),selected=chosen.words,
                    eligible_goals=len(chosen.carried),observed=report.observed_old+report.observed_new,
                    exclusions=len(getattr(agent,'certificates',())))
    finally:
        fixture.doCleanups()


if __name__=='__main__':
    baseline=run(PostExtensionPortfolio)
    constrained=run(RequiredEdgePortfolio)
    assert baseline['selected']==constrained['selected']
    print('Full evaluation then required-edge selection:',baseline)
    print('Witnessed-edge prefilter before evaluation:',constrained)
