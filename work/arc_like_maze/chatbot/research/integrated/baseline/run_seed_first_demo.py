"""Demonstration of combining seeds before extending one rooted relation."""
from ab_chatbot_seed_first_extension import SeedFirstGoalExtender
from ab_chatbot_backtracked_extension import BacktrackedGoalExtender
from ab_chatbot_extension_portfolio import CompletedExtensionPortfolio
from test_ab_chatbot_path_union import PathUnionTests

GOALS = ((0, 1, 0), (0, 1, 1))

for changed in ((0,0,0), (1,0,1), (0,0,1)):
    fixture = PathUnionTests()
    try:
        _, old, new, *_ = fixture.make((0,0,1), changed, depth=0, budget=54)
        candidates = []
        for goal in GOALS:
            agent = BacktrackedGoalExtender(old, new, goal, max_depth=6)
            for _ in range(100):
                result = agent.advance(max_new_edges=108)
                if result.status not in ('SEARCHING', 'EXTENDING'):
                    break
            candidates.append(agent)
        portfolio = CompletedExtensionPortfolio(tuple(candidates), GOALS).run()
        seed_first = SeedFirstGoalExtender(old, new, GOALS, max_depth=6)
        for _ in range(100):
            result = seed_first.advance(max_new_edges=108)
            if result.status not in ('SEARCHING', 'EXTENDING'):
                break
        print('changed-law', changed)
        print('  completed-first:', portfolio.status,
              'goals', len(portfolio.selected.carried_goals) if portfolio.selected else 0)
        print('  seed-first:     ', result.status, 'goals', len(result.carried_goals),
              'paths', result.selected_paths, 'states', result.paired_states,
              'edges', result.admitted_edges, 'excluded', result.excluded_edges)
    finally:
        fixture.doCleanups()
