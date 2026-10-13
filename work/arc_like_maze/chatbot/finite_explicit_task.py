"""Standalone finite counterpart for explicitly supplied task constraints.

No natural-language inference; mathematical A/B operators are scoped to Law.
This does not certify HTTP owner provenance or implement the whole chatbot.
"""
import re
from finite_goal_priority import Law
from finite_required_edge_guard import preflight

STATE = r'\(\s*[012]\s*,\s*[012]\s*,\s*[012]\s*\)'
TASK = re.compile(
    rf'goals\s*:\s*(?P<goals>{STATE}(?:\s*,\s*{STATE})*)'
    rf'(?:\s*;\s*require\s*:\s*edge\s+(?P<source>{STATE})\s+(?P<action>[AB]))?\s*',
    flags=re.IGNORECASE)


def parse_explicit(text):
    if type(text) is not str:
        return None
    match = TASK.fullmatch(text.strip())
    if match is None:
        return None
    extract = lambda s: tuple(int(x) for x in re.findall('[012]', s))
    goals = tuple(extract(x.group()) for x in re.finditer(STATE, match['goals']))
    if len(set(goals)) != len(goals) or not 1 <= len(goals) <= 8:
        return None
    requirement = ((extract(match['source']), match['action'].upper())
                   if match['source'] else None)
    return goals, requirement


def task_candidates(old: Law, new: Law, task: str, candidate_words):
    explicit = parse_explicit(task)
    if explicit is None:
        return 'UNKNOWN_TASK', None
    goals, required_edge = explicit
    if required_edge is None:
        return 'GOALS_ONLY', tuple('NOT_CHECKED' for _ in candidate_words)
    verdicts = tuple(preflight(old, new, words, required_edge) for words in candidate_words)
    return 'REQUIRED_EDGE', verdicts

if __name__ == '__main__':
    old, new = Law((0,0,1)), Law((0,0,0))
    words = (('ABAA','ABBABA'), ('ABAA','AAABB','BAAAB'), ('ABBABA',))
    print(task_candidates(old,new,
          'goals: (0,1,1), (0,2,0); require: edge (0,0,0) B',words))
