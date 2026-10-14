"""Paired-budget comparison of two existing finite chatbot trial policies.

The fixed and guided agents get independent, identical local owners, pinned roots,
path limits, goal sets, candidate pools and *trial budgets*. No evidence from
one agent is shared with the other. Explicitly reports per-law/goal results,
never promoting selected pairing to full conjugacy or general A/B law.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import json

from ab_chatbot_conflict_guided import ConflictGuidedPortfolio
from ab_chatbot_post_extension_portfolio import PostExtensionPortfolio
from ab_chatbot_relation_probe import FiniteSystem
from test_ab_chatbot_path_union import PathUnionTests

# Deliberately declared test cases, not a representative sample of all 27^2
# finite transformation-law pairs or all possible goal combinations.
DEFAULT_CASES = (
    ((0,0,1), (1,0,1), ((0,1,0),(0,1,1))),
    ((0,0,1), (1,0,1), ((0,1,1),(0,2,0))),
    ((0,0,1), (0,0,0), ((0,1,0),(0,1,1))),
    ((0,0,1), (0,0,0), ((0,1,1),(0,2,0))),
    ((0,0,1), (0,1,0), ((0,1,0),(0,1,1))),
    ((0,0,1), (2,1,0), ((1,1,0),(1,1,2))),
)

@dataclass(frozen=True)
class Outcome:
    law_old: tuple
    law_new: tuple
    goals: tuple
    trial_budget: int
    policy: str
    status: str
    completed: int
    admitted: int
    excluded: int
    paired: int
    trials: int
    observed_old: int
    observed_new: int
    candidate_pool_truncated: bool
    selected_words: tuple
    selected_goal_words: tuple
    replay_verified: bool
    witness_guided_attempts: int


def run_once(law_old,law_new,goals, *, budget, guided):
    if type(budget) is not int or not 1 <= budget <= 12:
        raise ValueError('bounded trial count required')
    fixture=PathUnionTests()
    try:
        _,old,new,_,_=fixture.make(law_old,law_new,depth=0,budget=54)
        settings=dict(max_depth=6,variants_per_goal=4,candidate_limit=7)
        if guided:
            agent=ConflictGuidedPortfolio(old,new,goals,trial_budget=budget,
                                          candidate_pool_limit=12,**settings)
        else:
            agent=PostExtensionPortfolio(old,new,goals,max_trials=budget,**settings)
        for _ in range(50):
            report=agent.advance(max_new_edges=108)
            if report.status not in ('SEARCHING','EVALUATING'):
                break
        else:
            raise AssertionError('finite-run continuation limit reached')
        report=report.portfolio if guided else report
        status=report.status
        selected=report.selected
        # Finite independent owner-law replay of reported paths *and every*
        # admitted edge of the selected complete candidate (not its snapshot).
        owner_old,owner_new=FiniteSystem(law_old),FiniteSystem(law_new)
        winner=next((i for i,t in enumerate(agent.finished) if t is selected),None)
        if winner is None or winner >= len(agent._extenders):
            raise AssertionError('selected trial must retain its replayable extender')
        extender=agent._extenders[winner]
        fwd=dict(extender.forward)
        verified=(selected is not None and
            len(fwd)==len(set(fwd.values())) and
            len(extender.edges)==selected.admitted_edges and
            all(owner_old.follow(word)==goal and
                owner_new.follow(word)==image and fwd[goal]==image
                for goal,image,word in selected.carried) and
            all(fwd[s]==ns and fwd[t]==nt and
                owner_old.step(s,a)==t and owner_new.step(ns,a)==nt
                for s,a,t,ns,nt in extender.edges.values()))
        if selected is None or not verified:
            raise AssertionError('controlled benchmark must finish with replayed selected paths')
        return Outcome(law_old,law_new,goals,budget,
            'guided' if guided else 'fixed',status,len(selected.carried),
            selected.admitted_edges,selected.excluded_edges,selected.paired_states,
            len(report.trials),report.observed_old,report.observed_new,
            report.candidate_cap_reached,selected.words,selected.carried,True,
            len(agent.attempts) if guided else 0)
    finally:
        fixture.doCleanups()


def compare(cases=DEFAULT_CASES, budgets=(2,3,4)):
    output=[]
    for old,new,goals in cases:
        for trial_budget in budgets:
            fixed=run_once(old,new,goals,budget=trial_budget,guided=False)
            guided=run_once(old,new,goals,budget=trial_budget,guided=True)
            if fixed.trials!=guided.trials or fixed.trials!=trial_budget:
                raise AssertionError('unequal number of completed trials')
            output.append((fixed,guided))
    return tuple(output)


def summarize(pairs):
    def sign(a,b):
        return 'guided' if a>b else ('fixed' if a<b else 'tie')
    goals=dict(fixed=0,guided=0,tie=0)
    edges=dict(fixed=0,guided=0,tie=0)
    for fixed,guided in pairs:
        goals[sign(guided.completed,fixed.completed)]+=1
        edges[sign(guided.admitted,fixed.admitted)]+=1
    obs=dict(fixed=0,guided=0,tie=0)
    for f,g in pairs:
        # Lower owner-observation cost is preferred.
        obs[sign(f.observed_old+f.observed_new, g.observed_old+g.observed_new)]+=1
    return dict(cases=len(pairs),goal_completions=goals,edge_admissions=edges, observation_cost=obs,
                actual_guidance=sum(bool(g.witness_guided_attempts) for f,g in pairs),
                mean_fixed_edges=sum(f.admitted for f,g in pairs)/len(pairs),
                mean_guided_edges=sum(g.admitted for f,g in pairs)/len(pairs),
                total_owner_observations_fixed=sum(f.observed_old+f.observed_new for f,g in pairs),
                total_owner_observations_guided=sum(g.observed_old+g.observed_new for f,g in pairs))

def adoption_gate(pairs):
    if not pairs: raise ValueError('need paired executed cases')
    summary=summarize(pairs)
    # Even an all-clear would mean only support on the *declared cases*, not
    # a universal theorem or automatic production deployment.
    safe=all(g.completed >= f.completed and g.admitted >= f.admitted and
             g.observed_old+g.observed_new <= f.observed_old+f.observed_new
             for f,g in pairs)
    improved=any(g.completed > f.completed or g.admitted > f.admitted or
                 g.observed_old+g.observed_new < f.observed_old+f.observed_new
                 for f,g in pairs)
    return {'decision':'EVIDENCE_SUPPORTS_GUIDANCE_ON_DECLARED_CASES' if safe and improved
                         else 'KEEP_FIXED_DEFAULT',
            'reason':'Equal-trial comparisons; any observed regression blocks promotion; no claim beyond the tested cases.',
            'summary':summary}

def export_budget(budget):
    if budget not in (2, 3, 4) or type(budget) is not int:
        raise ValueError('benchmark budget must be one of 2, 3, 4')
    pairs=compare(budgets=(budget,))
    records=[{'fixed':asdict(f),'guided':asdict(g)} for f,g in pairs]
    output=f'BENCH_BUDGET_{budget}.json'
    with open(output,'w',encoding='utf-8') as handle:
        json.dump(records,handle,indent=2)
    return output, summarize(pairs)

def aggregate_files():
    rows=[]
    for budget in (2,3,4):
        with open(f'BENCH_BUDGET_{budget}.json',encoding='utf-8') as handle:
            entries=json.load(handle)
        if len(entries)!=len(DEFAULT_CASES):
            raise ValueError('incomplete budget segment')
        for index,entry in enumerate(entries):
            fixed,guided=Outcome(**entry['fixed']),Outcome(**entry['guided'])
            expected=DEFAULT_CASES[index]
            # JSON encodes tuples as lists; compare normalized values.
            for record in (fixed,guided):
                if record.trial_budget!=budget or record.trials!=budget or not record.replay_verified:
                    raise ValueError('incomplete/unverified or wrong-budget record')
                if tuple(record.law_old)!=expected[0] or tuple(record.law_new)!=expected[1] or \
                      tuple(tuple(goal) for goal in record.goals)!=expected[2]:
                    raise ValueError('unexpected finite law/goal combination')
            rows.append((fixed,guided))
    data={'scope':'six declared finite law/goal pairs, three equal trial caps; NOT exhaustive',
          'adoption_gate':adoption_gate(rows),
          'runs':[{'fixed':asdict(f),'guided':asdict(g)} for f,g in rows]}
    with open('POLICY_BENCHMARK_RESULTS.json','w',encoding='utf-8') as handle:
        json.dump(data,handle,indent=2)
    return data

if __name__=='__main__':
    import sys
    if len(sys.argv)==3 and sys.argv[1]=='--budget':
        filename, stats=export_budget(int(sys.argv[2]))
        print(filename, json.dumps(stats,sort_keys=True))
    elif sys.argv[1:]==['--aggregate']:
        data=aggregate_files()
        print(json.dumps(data['adoption_gate'],indent=2))
    else:
        print('Run separately: python ab_chatbot_policy_benchmark.py --budget 2|3|4')
        print('Then run:       python ab_chatbot_policy_benchmark.py --aggregate')
        raise SystemExit(2)
