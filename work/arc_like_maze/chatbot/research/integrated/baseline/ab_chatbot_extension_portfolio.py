"""Select compatible *completed* rooted extension witnesses for requested goals.

This module does not invent coordinates, merge contradictory full pairings,
or generalize beyond pinned finite A/B-labeled laws. Candidate extensions
are made by the existing BacktrackedGoalExtender, not recomputed here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ab_chatbot_backtracked_extension import BacktrackedGoalExtender
from ab_chatbot_discovered_correspondence import DOMAIN_SET, State
from ab_chatbot_rule_change import WordRelation, _cached_path, _count

PortfolioStatus = Literal[
    'GOALS_CARRIED_WITNESSED', 'GOALS_CARRIED_REMOTE_REPORTED',
    'PARTIAL_GOALS_WITNESSED', 'PARTIAL_GOALS_REMOTE_REPORTED',
    'NO_GOALS_CARRIED', 'UNKNOWN_INCOMPLETE', 'UNKNOWN_VERSION', 'WALL_OBSERVATION',
]

@dataclass(frozen=True)
class PortfolioConflict:
    first: int
    second: int
    cause: str
    # A different equality result under the source and target laws.
    witness: WordRelation

@dataclass(frozen=True)
class PortfolioSelection:
    candidate_indices: tuple[int, ...]
    paired_states: tuple[tuple[State, State], ...]
    admitted_edges: tuple[tuple[State, str, State, State, State], ...]
    carried_goals: tuple[tuple[State, State, str], ...]

@dataclass(frozen=True)
class PortfolioReport:
    status: PortfolioStatus
    requested_goals: tuple[State, ...]
    selected: PortfolioSelection | None
    conflicts: tuple[PortfolioConflict, ...]
    available_candidates: int
    compatible_subsets: int
    possible_goal_images: tuple[tuple[State, tuple[State, ...]], ...]
    old_observed_edges: int
    new_observed_edges: int
    detail: str

class CompletedExtensionPortfolio:
    """Exact subset comparison over at most eight *supplied verified* extensions.

    Completed extensions must use the very same pinned source objects and roots.
    On each comparison, their entire histories, edges and rejected witnesses are
    audited by each source extender with a zero-observation call. Candidate
    compatibility is not presumed from individually correct action words.
    """

    def __init__(self, candidates: tuple[BacktrackedGoalExtender, ...],
                 goals: tuple[State, ...]):
        if (type(candidates) is not tuple or not 1 <= len(candidates) <= 8 or
                any(not isinstance(x, BacktrackedGoalExtender) for x in candidates) or
                len(set(map(id, candidates))) != len(candidates)):
            raise ValueError('1..8 distinct completed goal extenders required')
        if (type(goals) is not tuple or not goals or len(set(goals)) != len(goals) or
                any(x not in DOMAIN_SET for x in goals)):
            raise ValueError('distinct finite goals required')
        self.candidates, self.goals = candidates, goals
        one = candidates[0].branch
        self.old, self.new = one.old, one.new
        self.old_root, self.new_root = one.old_root, one.new_root
        if any(x.branch.old is not self.old or x.branch.new is not self.new or
               x.branch.old_root != self.old_root or x.branch.new_root != self.new_root
               for x in candidates):
            raise ValueError('extensions must share pinned source objects and roots')

    def _report(self, status, detail, *, selected=None, conflicts=(),
                compatible=0, images=()):
        return PortfolioReport(status, self.goals, selected, tuple(conflicts),
                               len(self.candidates), compatible, tuple(images),
                               _count(self.old), _count(self.new), detail)

    def run(self) -> PortfolioReport:
        """Replay prior observations, then compare; never make new observations."""
        reports = []
        for idx, candidate in enumerate(self.candidates):
            report = candidate.advance(max_new_edges=0)
            if report.status == 'UNKNOWN_VERSION':
                return self._report('UNKNOWN_VERSION', f'Candidate {idx} source version changed')
            if report.status == 'WALL_OBSERVATION':
                return self._report('WALL_OBSERVATION', f'Candidate {idx} failed replay: {report.detail}')
            if report.status not in ('GOAL_CARRIED_WITNESSED', 'GOAL_CARRIED_REMOTE_REPORTED'):
                return self._report('UNKNOWN_INCOMPLETE',
                                    f'Candidate {idx} not complete: {report.status}')
            extension = candidate.extender
            r = candidate.last_extension
            if extension is None or r is None:
                return self._report('WALL_OBSERVATION','Missing completed extension evidence')
            if (len(dict(r.state_pairs)) != len(r.state_pairs) or
                    len(set(n for _, n in r.state_pairs)) != len(r.state_pairs) or
                    set(extension.words) != set(dict(r.state_pairs)) or
                    len({(s,a) for s,a,*_ in r.admitted_edges}) != len(r.admitted_edges)):
                return self._report('WALL_OBSERVATION', 'Candidate pairing, words or edges inconsistent')
            reports.append((r, extension.words))

        def join(indices):
            fwd, rev, edges = {}, {}, {}
            for i in indices:
                r, _ = reports[i]
                for old, new in r.state_pairs:
                    if (old in fwd and fwd[old] != new) or (new in rev and rev[new] != old):
                        return None
                    fwd[old], rev[new] = new, old
                for edge in r.admitted_edges:
                    key = edge[:2]
                    if key in edges and edges[key] != edge:
                        return None
                    edges[key] = edge
            if any(fwd.get(s) != ns or fwd.get(t) != nt for s,a,t,ns,nt in edges.values()):
                return None
            return fwd, edges

        # A conflicting candidate pair carries a *word-equality* witness,
        # not just a count or a coordinate mismatch.
        conflicts = []
        for i in range(len(reports)):
            fi, wi = dict(reports[i][0].state_pairs), reports[i][1]
            ri = {v:k for k,v in fi.items()}
            for j in range(i+1, len(reports)):
                fj, wj = dict(reports[j][0].state_pairs), reports[j][1]
                shared = sorted((s for s in fi if s in fj and fi[s] != fj[s]))
                if shared:
                    s=shared[0]; word_i=wi[s]; word_j=wj[s]; cause='SOURCE_COLLISION'
                else:
                    shared_image = sorted(set(ri).intersection(fj.values()))
                    mismatch = next((n for n in shared_image if ri[n] != next(s for s,v in fj.items() if v==n)), None)
                    if mismatch is None:
                        continue
                    word_i=wi[ri[mismatch]]
                    word_j=wj[next(s for s,v in fj.items() if v==mismatch)]
                    cause='TARGET_COLLISION'
                oi,oj=(_cached_path(self.old,self.old_root,w) for w in (word_i,word_j))
                ni,nj=(_cached_path(self.new,self.new_root,w) for w in (word_i,word_j))
                old_eq=oi.states[-1] == oj.states[-1]
                new_eq=ni.states[-1] == nj.states[-1]
                if old_eq == new_eq:
                    return self._report('WALL_OBSERVATION','Candidate conflict has no valid equality witness')
                conflicts.append(PortfolioConflict(i,j,cause,
                    WordRelation(word_i,word_j,oi,oj,ni,nj,old_eq,new_eq)))

        scored = []
        for mask in range(1,1 << len(reports)):
            indices = tuple(i for i in range(len(reports)) if mask & (1 << i))
            joined=join(indices)
            if joined is None:
                continue
            mapping, edges=joined
            carried=[]
            for goal in self.goals:
                if goal in mapping:
                    word=min((words[goal] for r,words in (reports[i] for i in indices) if goal in words),
                             key=lambda w:(len(w),w))
                    carried.append((goal,mapping[goal],word))
            score=(len(carried),len(edges),len(mapping),-len(indices))
            selection=PortfolioSelection(indices,tuple(sorted(mapping.items())),
                                         tuple(sorted(edges.values())),tuple(carried))
            scored.append((score,selection))
        if not scored:
            return self._report('WALL_OBSERVATION','No compatible nonempty subset')
        best_score=max(score for score, _ in scored)
        best=min((selection for score,selection in scored if score==best_score),
                 key=lambda x:x.candidate_indices)
        peak=max(score[0] for score,_ in scored)
        options=tuple((g,tuple(sorted({image for score,s in scored if score[0]==peak
                                      for goal,image,word in s.carried_goals if goal==g})))
                      for g in self.goals)
        locally_owned=all(x.branch.old.origin_scope=='LOCAL_OWNER_VERIFIED' and
                          x.branch.new.origin_scope=='LOCAL_OWNER_VERIFIED'
                          for x in self.candidates)
        complete=len(best.carried_goals)==len(self.goals)
        status=(('GOALS_CARRIED_' if complete else 'PARTIAL_GOALS_') +
                ('WITNESSED' if locally_owned else 'REMOTE_REPORTED'))
        if not best.carried_goals:
            status='NO_GOALS_CARRIED'
        return self._report(status, 'Compared complete extensions; selected goal coverage first, '
                            'then admitted edges and paired states, without merging conflicting '
                            'pairings. Exact only over the supplied candidate pool; distinct '
                            'goal images remain possible.',selected=best,
                            conflicts=conflicts,compatible=len(scored),images=options)
