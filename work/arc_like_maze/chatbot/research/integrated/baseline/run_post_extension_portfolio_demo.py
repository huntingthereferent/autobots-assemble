"""Runnable local controlled post-extension comparison."""
from ab_chatbot_seed_first_extension import SeedFirstGoalExtender
from ab_chatbot_post_extension_portfolio import PostExtensionPortfolio
from test_ab_chatbot_path_union import PathUnionTests

fixture = PathUnionTests()
try:
    _, old, new, *_ = fixture.make((0,0,1),(1,0,1),depth=0,budget=54)
    goals=((0,1,0),(0,1,1))
    seed=SeedFirstGoalExtender(old,new,goals,max_depth=6,
                              variants_per_goal=3,max_candidates=5)
    for _ in range(80):
        earlier=seed.advance(max_new_edges=108)
        if earlier.status not in ('SEARCHING','EXTENDING'): break
    portfolio=PostExtensionPortfolio(old,new,goals,max_depth=6,
                                      variants_per_goal=3,candidate_limit=5,max_trials=6)
    for _ in range(80):
        later=portfolio.advance(max_new_edges=108)
        if later.status not in ('SEARCHING','EVALUATING'): break
    print('Seed-only:', earlier.status, earlier.selected_paths,
          len(earlier.carried_goals),earlier.admitted_edges)
    print('Post-extension:', later.status, later.selected.words,
          len(later.selected.carried),later.selected.admitted_edges)
    for trial in later.trials:
        print('  ',trial.words,'goals',len(trial.carried),'edges',trial.admitted_edges,
              'excluded',trial.excluded_edges)
finally:
    fixture.doCleanups()
