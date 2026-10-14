"""Compare compatible seed unions AFTER individually witnessed edge extension.

Uses the existing BranchDiscoverer, PathUnionAgent, and UnionEdgeExtender.
Candidate search is bounded; no universal A/B claim and no source identity upgrade.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import combinations

from ab_chatbot_branch_discovery import BranchDiscoverer
from ab_chatbot_path_union import PathUnionAgent, JoinedRestriction
from ab_chatbot_union_extension import UnionEdgeExtender
from ab_chatbot_discovered_correspondence import DOMAIN_SET, State
from ab_chatbot_rule_change import _count, _cached_path
from ab_chatbot_language_bridge import ObservationWall

TERMINAL_EXTENSIONS = (
    'ROOTED_CLOSED_WITNESSED', 'ROOTED_CLOSED_REMOTE_REPORTED',
    'PARTIAL_EXTENSION_WITNESSED', 'PARTIAL_EXTENSION_REMOTE_REPORTED',
)

@dataclass(frozen=True)
class Trial:
    words: tuple[str, ...]
    carried: tuple[tuple[State, State, str], ...]
    paired_states: int
    admitted_edges: int
    excluded_edges: int
    status: str

@dataclass(frozen=True)
class PortfolioReport:
    status: str
    selected: Trial | None
    trials: tuple[Trial, ...]
    evaluated: int
    candidates: int
    candidate_cap_reached: bool
    possible_goal_images: tuple[tuple[State, tuple[State, ...]], ...]
    observed_old: int
    observed_new: int
    detail: str

class _SelectedUnion:
    """Read-only selection over the same replay-audited PathUnionAgent."""
    def __init__(self, source, selected):
        self.source, self.selected = source, selected
        self.discovered = source.discovered

    def run(self):
        evidence = self.source.run()  # zero-read, checks origin, versions, cache
        if evidence.status in ('UNKNOWN_VERSION','WALL_OBSERVATION',
                               'DISCOVERY_INCOMPLETE','GOALS_OUTSIDE_CANDIDATES'):
            return evidence
        if self.selected is None:
            raise ValueError('No selected witnessed paths')
        owned = evidence.status.endswith('_WITNESSED')
        carried = len(self.selected.carried_goals) == len(self.source.goals)
        return replace(evidence,
                       status=('UNION_' if carried else 'PARTIAL_UNION_') +
                              ('WITNESSED' if owned else 'REMOTE_REPORTED'),
                       selected=self.selected)

class PostExtensionPortfolio:
    """Choose among bounded compatible *seed* subsets by downstream results.

    The report is final only after every selected trial's retained edges have
    completed zero-read replay. Invalid/unfinished evidence invalidates the
    current selection rather than retaining earlier success.
    """
    def __init__(self, old, new, goals: tuple[State, ...], *, max_depth=6,
                 variants_per_goal=3, candidate_limit=6, max_trials=12):
        if (type(goals) is not tuple or not goals or len(set(goals)) != len(goals)
                or any(g not in DOMAIN_SET for g in goals)):
            raise ValueError('distinct finite goals required')
        if (type(max_depth) is not int or not 0 <= max_depth <= 8 or
                type(variants_per_goal) is not int or not 1 <= variants_per_goal <= 10 or
                type(candidate_limit) is not int or not 1 <= candidate_limit <= 8 or
                type(max_trials) is not int or not 1 <= max_trials <= 24):
            raise ValueError('invalid bounded search limits')
        self.goals = goals
        self.discovered = BranchDiscoverer(old,new,goals[0],max_depth=max_depth)
        self.union = PathUnionAgent(self.discovered,goals,
                                    variants_per_goal=variants_per_goal,
                                    max_candidates=candidate_limit)
        self.max_trials = max_trials
        self.selections = None
        self.active_index = 0
        self.active_extender = None
        self.finished = []
        self.candidate_cap_reached = False

    def _report(self,status,detail,selected=None):
        trials = tuple(self.finished) if status not in ('UNKNOWN_VERSION','WALL_OBSERVATION','UNKNOWN_BUDGET') else ()
        images = tuple((g,tuple(sorted({image for t in trials for goal,image,_ in t.carried if goal==g})))
                       for g in self.goals) if trials else ()
        return PortfolioReport(status,selected, trials, len(self.finished),
                               len(self.selections) if self.selections is not None else 0,
                               self.candidate_cap_reached, images,
                               _count(self.discovered.old),_count(self.discovered.new),detail)

    def _discover_selections(self):
        audited = self.union.run()
        if audited.status in ('UNKNOWN_VERSION','WALL_OBSERVATION','DISCOVERY_INCOMPLETE'):
            return audited.status
        pool,available,truncated = self.union._select_candidates()
        if not pool:
            self.selections = ()
            return None
        options = []
        for size in range(1,len(pool)+1):
            for group in combinations(pool,size):
                fwd,rev,edges={}, {}, {}
                good=True
                for p in group:
                    op = _cached_path(self.discovered.old,self.discovered.old_root,p.word)
                    np = _cached_path(self.discovered.new,self.discovered.new_root,p.word)
                    if op != p.original_path or np != p.changed_path:
                        raise ObservationWall('candidate failed zero-read replay')
                    for o,n in zip(op.states,np.states):
                        if (o in fwd and fwd[o]!=n) or (n in rev and rev[n]!=o):
                            good=False;break
                        fwd[o]=n;rev[n]=o
                    if not good:break
                    for i,a in enumerate(p.word):
                        e=(op.states[i],a,op.states[i+1],np.states[i],np.states[i+1])
                        key=e[:2]
                        if key in edges and edges[key]!=e:
                            good=False;break
                        edges[key]=e
                    if not good:break
                if not good:continue
                words=tuple(sorted((p.word for p in group),key=lambda w:(len(w),w)))
                carried=tuple((goal,fwd[goal],min((p.word for p in group if p.source_target==goal),
                                                key=lambda w:(len(w),w)))
                              for goal in self.goals if any(p.source_target==goal for p in group))
                selected=JoinedRestriction(words,tuple(sorted(fwd.items())),
                                           tuple(sorted(edges.values())),carried)
                score=(len(carried),len(edges),len(fwd),-len(words))
                options.append((score,selected))
        # Choose promising but distinct seed mappings, including single-path
        # alternatives. All reported results are scoped to these trials.
        options.sort(key=lambda item:(tuple(-x for x in item[0]),item[1].words))
        keep=[];seen=set()
        for _,s in options:
            fingerprint=s.state_pairs
            if fingerprint in seen:continue
            seen.add(fingerprint)
            keep.append(s)
            if len(keep)>=self.max_trials:break
        self.selections=tuple(keep)
        self.candidate_cap_reached=truncated or len(options)>len(keep)
        return None

    def advance(self, *, max_new_edges=108):
        if type(max_new_edges) is not int or not 0 <= max_new_edges <= 108:
            raise ValueError('invalid per-call observation allowance')
        if self.selections is None:
            b=self.discovered.advance(max_new_edges=max_new_edges)
            if b.status in ('UNKNOWN_VERSION','WALL_OBSERVATION','UNKNOWN_BUDGET'):
                return self._report(b.status,'Discovery: '+b.detail)
            if b.status=='CONTINUING':
                return self._report('SEARCHING',b.detail)
            try:
                result=self._discover_selections()
            except (ObservationWall,ValueError,KeyError) as exc:
                return self._report('WALL_OBSERVATION',f'Seed replay: {exc}')
            if result is not None:
                return self._report(result,'Seed discovery not ready')
            if not self.selections:
                return self._report('GOALS_OUTSIDE_SEARCH_BOUND','No witnessed goal seeds under finite bound')
            # no extra observations after discovery in this call; explicit
            # continuation ensures budget is not silently exceeded.
            return self._report('EVALUATING','Seed selections ready; evaluate individually')
        if self.active_index==len(self.selections):
            # Replay entire candidate history on every final read, including
            # the winning candidate, to avoid stale post-selection labels.
            for index,ext in enumerate(self._extenders):
                r=ext.advance(max_new_edges=0)
                if r.status in ('UNKNOWN_VERSION','WALL_OBSERVATION','UNKNOWN_BUDGET'):
                    return self._report(r.status,'Trial replay rejected: '+str(index))
                if r.status not in TERMINAL_EXTENSIONS:
                    return self._report('UNKNOWN_BUDGET','Trial was no longer complete')
            best=max(self.finished,key=lambda t:(len(t.carried),t.admitted_edges,
                                                  t.paired_states,-t.excluded_edges,
                                                  tuple((-len(w),w) for w in t.words)))
            owned=all(x.status.endswith('_WITNESSED') for x in self.finished)
            kind='GOALS_CARRIED_' if len(best.carried)==len(self.goals) else 'PARTIAL_GOALS_'
            return self._report(kind+('WITNESSED' if owned else 'REMOTE_REPORTED'),
                                'Ranked verified downstream results only within bounded candidate pool.',best)
        if not hasattr(self,'_extenders'):
            self._extenders=[]
        if self.active_extender is None:
            try:
                self.active_extender=UnionEdgeExtender(_SelectedUnion(self.union,
                                             self.selections[self.active_index]))
            except (ObservationWall,ValueError,KeyError) as exc:
                return self._report('WALL_OBSERVATION',f'Unable to start candidate: {exc}')
            self._extenders.append(self.active_extender)
        result=self.active_extender.advance(max_new_edges=max_new_edges)
        if result.status in ('UNKNOWN_VERSION','WALL_OBSERVATION','UNKNOWN_BUDGET'):
            return self._report(result.status,f'Trial {self.active_index}: {result.detail}')
        if result.status=='CONTINUING':
            return self._report('EVALUATING',f'Trial {self.active_index}: {result.detail}')
        fwd=dict(result.state_pairs)
        words=self.active_extender.words
        carried=tuple((g,fwd[g],words[g]) for g in self.goals if g in fwd and g in words)
        self.finished.append(Trial(self.selections[self.active_index].words,carried,
                                  len(fwd),len(result.admitted_edges),len(result.rejected),result.status))
        self.active_index+=1
        self.active_extender=None
        return self._report('EVALUATING',f'{self.active_index}/{len(self.selections)} completed trials')
