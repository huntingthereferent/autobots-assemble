"""One bounded relation-carried witness; no future-axis schedule."""
from copy import deepcopy
from itertools import permutations
import json


def relations(x, left, right):
    """Evidence of a directed relation, including same-sign parent lifting."""
    a, b = x['nodes'][left], x['nodes'][right]
    found = [{'kind': e['kind'], 'source_edge': key}
             for key, e in x['source_relations'].items()
             if e['negative'] == left and e['positive'] == right]
    if a['type'] == b['type'] == 'difference':
        positive = relations(x, a['positive'], b['positive'])
        negative = relations(x, a['negative'], b['negative'])
        for p in positive:
            for n in negative:
                if p['kind'] == n['kind']:
                    found.append({'kind': p['kind'], 'positive_support': p,
                                  'negative_support': n,
                                  'positive_pair': [a['positive'], b['positive']],
                                  'negative_pair': [a['negative'], b['negative']]})
    return found


def admissible(x):
    assert set(x) == {'nodes', 'source_relations', 'current', 'history', 'outcome'}
    active, done = set(), set()
    def check(key):
        if key in done:
            return
        assert key not in active, 'cyclic parent evidence'
        active.add(key)
        n = x['nodes'][key]
        assert type(n['value']) is int
        if n['type'] == 'source':
            assert n['source']
        else:
            assert n['type'] == 'difference'
            check(n['positive'])
            check(n['negative'])
            assert n['value'] == x['nodes'][n['positive']]['value'] - x['nodes'][n['negative']]['value']
            assert n['support'] in relations(x, n['negative'], n['positive'])
        active.remove(key)
        done.add(key)
    # Detect cycles before traversing relational proofs.
    def acyclic(key, path):
        assert key not in path, 'cyclic parent evidence'
        n = x['nodes'][key]
        if n['type'] == 'difference':
            for parent in ('positive', 'negative'):
                acyclic(n[parent], path | {key})
    for key in x['nodes']:
        acyclic(key, set())
    for e in x['source_relations'].values():
        assert e['kind'] and e['orientation'] == '0->1'
        assert all(x['nodes'][e[s]]['type'] == 'source' for s in ('positive', 'negative'))
    for key in x['nodes']:
        check(key)
    assert len(set(x['current'])) == len(x['current'])
    assert all(key in x['nodes'] for key in x['current'])
    return True


def ab(x):
    admissible(x)
    y = deepcopy(x)
    y['current'] = []
    inspected = []
    for left, right in permutations(x['current'], 2):
        proofs = relations(x, left, right)
        inspected.append({'negative': left, 'positive': right, 'support': proofs,
                          'decision': 'admitted' if proofs else 'no supported directed relation'})
        for proof in proofs:
            key = 'd' + str(len(y['nodes']))
            assert key not in y['nodes']
            y['nodes'][key] = {
                'type': 'difference',
                'value': x['nodes'][right]['value'] - x['nodes'][left]['value'],
                'positive': right, 'negative': left, 'support': proof}
            y['current'].append(key)
    values = [y['nodes'][key]['value'] for key in y['current']]
    y['outcome'] = ('UNKNOWN' if not values else
                    'SUPPORTED_MOVEMENT' if any(values) else 'EARNED_ZERO')
    y['history'].append({'input_current': list(x['current']), 'inspected': inspected})
    admissible(y)
    return y


def witness():
    x0 = {
        'nodes': {s: {'type': 'source', 'value': v, 'source': 'fixture:binary-square:' + s}
                  for s, v in [('00', 0), ('01', 1), ('10', 1), ('11', 0)]},
        'source_relations': {
            'b0': {'negative': '00', 'positive': '01', 'kind': 'b', 'orientation': '0->1'},
            'b1': {'negative': '10', 'positive': '11', 'kind': 'b', 'orientation': '0->1'},
            'a0': {'negative': '00', 'positive': '10', 'kind': 'a', 'orientation': '0->1'},
            'a1': {'negative': '01', 'positive': '11', 'kind': 'a', 'orientation': '0->1'}},
        'current': ['00', '01', '10', '11'], 'history': [], 'outcome': 'INPUT_EVIDENCE'}
    report = {'experiment': 2, 'X0': deepcopy(x0), 'outside_choices_between_calls': [],
              'outside_initial_choices': ['same square values', 'four directed native source edges',
                                          'integer subtraction', 'same-sign parent relation lifting',
                                          'inspect all ordered pairs of current nodes'],
              'future_schedule': None}
    try:
        x1 = ab(x0)
        report['X1'] = deepcopy(x1)
        report['X1_directly_admissible'] = admissible(x1)
        x2 = ab(x1)
        report['X2'] = deepcopy(x2)
        assert x0 == report['X0'] and x1 == report['X1'], 'input mutation'
        assert x1['source_relations'] == x2['source_relations'] == x0['source_relations']
        assert all(x2['nodes'][k] == n for k, n in x1['nodes'].items())
        assert all(x1['nodes'][k] == n for k, n in x0['nodes'].items())
        report['X1_values'] = [x1['nodes'][k]['value'] for k in x1['current']]
        report['X2_values'] = [x2['nodes'][k]['value'] for k in x2['current']]
        report['result'] = ('SUPPORTED_RELATION_CARRIED_RECURSION'
                            if x2['outcome'] == 'SUPPORTED_MOVEMENT' else x2['outcome'])
        report['first_unsupported_relation'] = (None if x2['current'] else
            'No current-node pair has a supported directed relation; see inspected pairs.')
        report['checks'] = 'arithmetic, signed relational proofs, source retention, unchanged inputs'
    except Exception as exc:
        report.update(result='CONTRACT_IMPLEMENTATION_LIMIT', error=repr(exc))
    report['untested'] = ['other fixtures', 'third call', 'missing/partial support', 'earned zero', 'malformed inputs']
    print(json.dumps(report, indent=2))
    return 1 if report['result'] == 'CONTRACT_IMPLEMENTATION_LIMIT' else 0


if __name__ == '__main__':
    raise SystemExit(witness())
