"""Witness-guided alternative exploration over existing finite seed unions.

Uses a replayed excluded edge from one complete extension to prioritize a
*different, already witnessed seed* that admits that particular old edge.
A repair is reported only after the second extension independently replays
and admits the edge. This does not claim the two extensions can be merged.
"""
from __future__ import annotations

from dataclasses import dataclass

from ab_chatbot_post_extension_portfolio import PostExtensionPortfolio
from ab_chatbot_discovered_correspondence import State

INVALID = ('UNKNOWN_VERSION','WALL_OBSERVATION','UNKNOWN_BUDGET')

@dataclass(frozen=True)
class GuidedAttempt:
    prior_words: tuple[str, ...]
    alternative_words: tuple[str, ...]
    old_source: State
    action: str
    old_target: State
    prior_new_source: State
    prior_new_target: State
    prior_assigned_target_image: State | None
    cause: str
    left_word: str
    right_word: str
    # Until independently completed/replayed, this is only a candidate.
    outcome: str  # SEED_ADMITS_EDGE, ALTERNATIVE_REPLAY_ADMITS_EDGE
    alternative_new_source: State | None = None
    alternative_new_target: State | None = None
    alternative_assigned_target_image: State | None = None

@dataclass(frozen=True)
class GuidedReport:
    status: str
    portfolio: object
    attempts: tuple[GuidedAttempt, ...]
    chosen_trials: int
    trial_budget: int
    remaining_candidates_not_tested: bool
    detail: str

class ConflictGuidedPortfolio(PostExtensionPortfolio):
    """Bounded incremental extension selection with concrete conflict witnesses.

    The first candidate is selected by existing seed ranking. Each completed
    candidate may supply excluded edges to prioritize an untried compatible
    seed that has already *admitted* the same old-state A/B edge. Full trials
    are still checked by existing UnionEdgeExtender, with no privileged access
    to internal owner transformations or guessed unobserved edges.
    """
    def __init__(self, old, new, goals, *, trial_budget=3,
                 candidate_pool_limit=12, **kwargs):
        if (type(trial_budget) is not int or not 1 <= trial_budget <= 24 or
                type(candidate_pool_limit) is not int or not 1 <= candidate_pool_limit <= 24 or
                trial_budget > candidate_pool_limit):
            raise ValueError('invalid trial budget or candidate pool limit')
        super().__init__(old, new, goals, max_trials=candidate_pool_limit, **kwargs)
        self.trial_budget = trial_budget
        self.attempts: list[GuidedAttempt] = []
        self._pending: GuidedAttempt | None = None
        self.original_pool_size: int | None = None

    def _seek_alternative(self, report) -> None:
        if self.active_index == len(self.selections) or not report.rejected:
            return
        previous = self.selections[self.active_index-1]
        available = self.selections[self.active_index:]
        targets = {(r.source,r.action):r for r in report.rejected}
        ranked=[]
        for index, candidate in enumerate(available):
            seed_edges = {(s,a):(s,a,t,ns,nt) for s,a,t,ns,nt in candidate.admitted_edges}
            covered=[targets[key] for key in sorted(targets) if key in seed_edges]
            if not covered:
                continue
            # Rejection is witnessed under previous mapping; the candidate seed
            # itself witnesses the same old edge in an alternative partial map.
            ranked.append((len(covered), len(candidate.carried_goals),
                           len(candidate.admitted_edges), -index, candidate, covered[0]))
        if not ranked:
            return  # No admissible repair *seed* in bounded pool: usual ordering.
        _,_,_,_,candidate,rejection = max(ranked,key=lambda x:x[:4])
        at = available.index(candidate)
        self.selections = self.selections[:self.active_index] + (candidate,) + \
                          available[:at]+available[at+1:]
        from_edge = self._extenders[-1]
        if (rejection.source,rejection.action) in from_edge.edges:
            raise AssertionError('selected guidance is not an excluded edge')
        witness = rejection.witness
        self._pending = GuidedAttempt(
            previous.words, candidate.words, rejection.source, rejection.action,
            rejection.old_target, from_edge.forward[rejection.source],
            rejection.new_target, from_edge.forward.get(rejection.old_target), rejection.cause,
            witness.left_word, witness.right_word, 'SEED_ADMITS_EDGE')
        self.attempts.append(self._pending)

    def _verify_followup(self, report):
        pending = self._pending
        if pending is None:
            return
        key=(pending.old_source,pending.action)
        edge=next((e for e in report.admitted_edges if e[:2]==key),None)
        if (edge is not None and edge[2]==pending.old_target and
                report.status.endswith(('WITNESSED','REMOTE_REPORTED'))):
            new=GuidedAttempt(
                pending.prior_words,pending.alternative_words,pending.old_source,
                pending.action,pending.old_target,pending.prior_new_source,
                pending.prior_new_target,pending.prior_assigned_target_image,
                pending.cause,pending.left_word,
                pending.right_word,'ALTERNATIVE_REPLAY_ADMITS_EDGE',edge[3],edge[4],
                self._extenders[-1].forward.get(pending.old_target))
            self.attempts[-1]=new
        self._pending=None

    def advance(self, *, max_new_edges=108) -> GuidedReport:
        before = self.active_index
        r = super().advance(max_new_edges=max_new_edges)
        if self.original_pool_size is None and self.selections is not None:
            self.original_pool_size=len(self.selections)
        if (self.selections is not None and self.active_index > before and
                r.status=='EVALUATING'):
            extension=self._extenders[-1].advance(max_new_edges=0)
            if extension.status in INVALID:
                r = super()._report(extension.status,'Final trial replay rejected before guidance')
            else:
                self._verify_followup(extension)
                if self.active_index >= self.trial_budget:
                    if self.active_index < len(self.selections):
                        self.candidate_cap_reached=True
                        self.selections=self.selections[:self.active_index]
                else:
                    self._seek_alternative(extension)
        if r.status in INVALID:
            return GuidedReport(r.status, r, (), r.evaluated, self.trial_budget,
                                self.candidate_cap_reached,
                                'Pinned replay invalidated the current guidance and completion result')
        return GuidedReport(r.status,r,tuple(self.attempts),r.evaluated,
                            self.trial_budget,self.candidate_cap_reached,
                            'Witnessed edge repair means an alternative pairing admits an edge; '
                            'it does not make both full pairings compatible.')
