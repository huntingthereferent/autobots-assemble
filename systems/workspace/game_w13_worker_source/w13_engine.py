"""W13 multi-world game composition over byte-preserved original W12 rules.

Adds a world-sequence contract and one explicit ADVANCE operation. Never
changes native W12 movement, interaction, blocked move, or receipt verification.
"""
from __future__ import annotations
from game_w12_reference import GameSpec, run_actions

VERSION = 'game-w13-multiworld-v1'


def play(worlds: list[dict], actions: list[str]) -> dict:
    # Validate inter-world traversal independently of native W12 actions.
    if len(worlds) < 2 or len(worlds) > 4:
        raise ValueError('W13 requires two to four worlds')
    current = 0
    segments = [[] for _ in worlds]
    for action in actions:
        if action == 'advance':
            if current >= len(worlds)-1:
                raise ValueError('cannot advance past last world')
            old = worlds[current]['spec']
            trace = run_actions(segments[current], GameSpec(
                old['width'], old['height'],tuple(old['start']),tuple(old['target'])))
            if not trace['solved']:
                raise ValueError('cannot advance from unsolved world')
            current += 1
        else:
            if action not in {'up','down','left','right','interact'}:
                raise ValueError('unknown native game action')
            segments[current].append(action)
    if current != len(worlds)-1:
        raise ValueError('world sequence never reached final world')
    collected = []
    for item, segment in zip(worlds,segments):
        spec=item['spec']
        trace=run_actions(segment,GameSpec(spec['width'],spec['height'],tuple(spec['start']),tuple(spec['target'])))
        if not trace['solved']:
            raise ValueError('every W13 world must complete')
        collected.append({'world_id':item['id'],'trace':trace})
    return {'version':VERSION,'worlds':collected,'worlds_completed':len(collected),
            'last_world':worlds[-1]['id'],'solved':True,
            'boundary':'W13 composition over byte-preserved W12 native rules'}