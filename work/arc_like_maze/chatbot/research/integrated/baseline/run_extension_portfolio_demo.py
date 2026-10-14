"""Local deterministic demonstration; the integrated chatbot uses pinned owners."""
from ab_chatbot_backtracked_extension import BacktrackedGoalExtender
from ab_chatbot_extension_portfolio import CompletedExtensionPortfolio
from ab_chatbot_relation_probe import FiniteSystem
from test_ab_chatbot_path_union import PathUnionTests

if __name__ == '__main__':
    fixture=PathUnionTests()
    _,old,new,*_=fixture.make((0,0,1),(0,0,0),depth=0,budget=54)
    goals=((0,1,0),(0,1,1))
    candidates=[]
    try:
        for goal in goals:
            agent=BacktrackedGoalExtender(old,new,goal,max_depth=6)
            for _ in range(100):
                report=agent.advance(max_new_edges=108)
                if report.status not in ('SEARCHING','EXTENDING'):
                    break
            print('individual:',goal,report.status,report.goal_word,
                  'states:',report.paired_states,'edges:',report.admitted_edges)
            candidates.append(agent)
        combined=CompletedExtensionPortfolio(tuple(candidates),goals).run()
        print('joint:',combined.status,'chosen:',combined.selected.candidate_indices,
              'carried:',combined.selected.carried_goals,
              'compatible subsets:',combined.compatible_subsets)
        for conflict in combined.conflicts:
            print('collision:',conflict.cause,conflict.witness.left_word,
                  conflict.witness.right_word,'old_equal:',conflict.witness.old_equal,
                  'new_equal:',conflict.witness.new_equal)
    finally:
        fixture.doCleanups()
