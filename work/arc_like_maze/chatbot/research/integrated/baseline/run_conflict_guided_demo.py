"""Run a finite-language-owner comparison; not a physical coupling witness."""
from ab_chatbot_conflict_guided import ConflictGuidedPortfolio
from ab_chatbot_post_extension_portfolio import PostExtensionPortfolio
from test_ab_chatbot_path_union import PathUnionTests

GOALS=((0,1,0),(0,1,1))
for label,guided in [('fixed',False),('rejection-guided',True)]:
    fixture=PathUnionTests()
    try:
        _,old,new,*_=fixture.make((0,0,1),(1,0,1),depth=0,budget=54)
        options=dict(max_depth=6,variants_per_goal=4,candidate_limit=7)
        if guided:
            bot=ConflictGuidedPortfolio(old,new,GOALS,trial_budget=3,
                                          candidate_pool_limit=12,**options)
        else:
            bot=PostExtensionPortfolio(old,new,GOALS,max_trials=3,**options)
        for _ in range(70):
            outcome=bot.advance(max_new_edges=108)
            status=outcome.status
            if status not in ('SEARCHING','EVALUATING'):
                break
        else: raise AssertionError('did not complete finite test')
        r=outcome.portfolio if guided else outcome
        print(label,status,'goals',len(r.selected.carried),
              'admitted',r.selected.admitted_edges,'trials',len(r.trials),
              'owner-observations',(r.observed_old,r.observed_new))
        if guided:
            for a in outcome.attempts:
                print('  rejected then alternate',a.old_source,a.action,
                    'old_target',a.old_target,'reason',a.cause,
                    'prior_assigned_target',a.prior_assigned_target_image,
                    'alternate_target',a.alternative_assigned_target_image,
                    'result',a.outcome)
            print('  bound',outcome.remaining_candidates_not_tested,
                  'pool',bot.original_pool_size)
    finally:
        fixture.doCleanups()
