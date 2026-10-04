"""Transition memory and lightweight planning for generic ARC3 first-contact play."""
from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from typing import Hashable, Iterable

from state import StateView, infer_directional_translation


ActionToken = tuple[int, ...]


@dataclass(frozen=True)
class Edge:
    next_key: Hashable
    level_delta: int
    changed: bool
    terminal_bad: bool
    support: int = 1


class TransitionModel:
    def __init__(self) -> None:
        self.exact: dict[tuple[bytes, ActionToken], Edge] = {}
        self.object_votes: defaultdict[
            tuple[Hashable, ActionToken], Counter[tuple[Hashable, int, bool, bool]]
        ] = defaultdict(Counter)
        self.object_conflicts: Counter[tuple[Hashable, ActionToken]] = Counter()
        self.action_stats: defaultdict[int, Counter[str]] = defaultdict(Counter)
        self.motion_rules: defaultdict[
            int, Counter[tuple[tuple[int, int, int, int], int, int]]
        ] = defaultdict(Counter)
        self.known_states: set[Hashable] = set()

    def update(
        self,
        before: StateView,
        action: ActionToken,
        after: StateView,
        *,
        level_delta: int,
        terminal_bad: bool,
    ) -> None:
        changed = before.exact_key != after.exact_key
        self.exact[(before.exact_key, action)] = Edge(
            after.exact_key, level_delta, changed, terminal_bad, 1
        )

        ob_key = (before.object_key, action)
        outcome = (after.object_key, level_delta, changed, terminal_bad)
        votes = self.object_votes[ob_key]
        if votes and outcome not in votes:
            self.object_conflicts[ob_key] += 1
        votes[outcome] += 1

        self.known_states.add(before.object_key)
        self.known_states.add(after.object_key)

        aid = action[0]
        if level_delta > 0:
            self.action_stats[aid]["progress"] += 1
        if terminal_bad:
            self.action_stats[aid]["death"] += 1
        if changed:
            self.action_stats[aid]["changed"] += 1
        else:
            self.action_stats[aid]["noop"] += 1

        if aid in (1, 2, 3, 4):
            moved = infer_directional_translation(before, after, aid)
            if moved is not None:
                self.motion_rules[aid][moved] += 1

    def exact_edge(self, state: StateView, action: ActionToken) -> Edge | None:
        return self.exact.get((state.exact_key, action))

    def object_edge(self, state: StateView, action: ActionToken) -> Edge | None:
        votes = self.object_votes.get((state.object_key, action))
        if not votes:
            return None
        ranked = votes.most_common(2)
        outcome, support = ranked[0]
        if len(ranked) > 1 and ranked[1][1] >= support:
            return None
        nxt, dl, changed, bad = outcome
        return Edge(nxt, dl, changed, bad, support)

    def confidence(self, state: StateView, action: ActionToken) -> float:
        if self.exact_edge(state, action) is not None:
            return 1.0
        votes = self.object_votes.get((state.object_key, action))
        if not votes:
            return 0.0
        total = sum(votes.values())
        best = votes.most_common(1)[0][1]
        return best / total if total else 0.0

    def best_motion_rule(self, action_id: int):
        votes = self.motion_rules.get(action_id)
        if not votes:
            return None
        rule, support = votes.most_common(1)[0]
        return rule, support

    def plan_to_known_progress(
        self,
        start: StateView,
        legal_tokens: Iterable[ActionToken],
        *,
        max_depth: int = 16,
    ) -> list[ActionToken]:
        legal_ids = {a[0] for a in legal_tokens}
        root = start.object_key
        q = deque([(root, [])])
        seen = {root}

        while q:
            key, path = q.popleft()
            if len(path) >= max_depth:
                continue

            for (src, action), votes in list(self.object_votes.items()):
                if src != key or action[0] not in legal_ids or not votes:
                    continue
                ranked = votes.most_common(2)
                outcome, support = ranked[0]
                if len(ranked) > 1 and ranked[1][1] >= support:
                    continue
                nxt, dl, changed, bad = outcome
                if bad and dl <= 0:
                    continue
                candidate = path + [action]
                if dl > 0:
                    return candidate
                if nxt not in seen:
                    seen.add(nxt)
                    q.append((nxt, candidate))
        return []

    def score_action(self, state: StateView, token: ActionToken) -> float:
        aid = token[0]
        stats = self.action_stats[aid]
        score = 0.0
        score += 36.0 * stats["progress"]
        score += 1.5 * stats["changed"]
        score -= 5.0 * stats["noop"]
        score -= 28.0 * stats["death"]

        ex = self.exact_edge(state, token)
        if ex is not None:
            if ex.level_delta > 0:
                score += 250.0
            elif ex.terminal_bad:
                score -= 100.0
            elif not ex.changed:
                score -= 30.0
            else:
                score += 4.0
        else:
            score += 14.0

        ob = self.object_edge(state, token)
        if ob is not None:
            if ob.level_delta > 0:
                score += 80.0
            if ob.terminal_bad and ob.level_delta <= 0:
                score -= 30.0
            score += 6.0 * self.confidence(state, token)
        else:
            score += 5.0

        if aid in (1, 2, 3, 4):
            score += 3.0
        elif aid == 5:
            score += 1.0
        return score
