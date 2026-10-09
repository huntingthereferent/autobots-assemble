"""One bounded candidate A/B: all available binary-axis finite differences.

This is a native numerical experiment, not a definition of general A/B.
No Eggy imports, layer parameter, supplied next WATCH or second operator.
"""
from copy import deepcopy
from itertools import product
import json

RULE = 'exact integer subtraction along every retained binary axis, oriented 0->1'


def coordinates(axes):
    return [''.join(bits) for bits in product('01', repeat=len(axes))]


def admissible(x):
    if not isinstance(x, dict) or set(x) != {'rule', 'nodes', 'tables', 'history', 'outcome', 'reasons'}:
        raise ValueError('X contract fields missing or unknown')
    if x['rule'] != RULE:
        raise ValueError('unsupported native rule; no substitute inferred')
    checked, active = set(), set()
    def check_node(key):
        if key in checked:
            return
        if key in active:
            raise ValueError('cyclic evidence')
        active.add(key)
        node = x['nodes'][key]
        if type(node['value']) is not int:
            raise ValueError('non-integer native value')
        if node['kind'] == 'source':
            if not node.get('source'):
                raise ValueError('source reference absent')
        elif node['kind'] == 'difference':
            for parent in (node['positive'], node['negative']):
                check_node(parent)
            if node['value'] != x['nodes'][node['positive']]['value'] - x['nodes'][node['negative']]['value']:
                raise ValueError('derived value disagrees with retained support')
        else:
            raise ValueError('unsupported evidence node')
        active.remove(key)
        checked.add(key)
    for key in x['nodes']:
        check_node(key)
    for table in x['tables']:
        axes = table['axes']
        if len(set(axes)) != len(axes):
            raise ValueError('ambiguous duplicate axis')
        if set(table['cells']) - set(coordinates(axes)):
            raise ValueError('cell outside binary domain')
        for key in table['cells'].values():
            check_node(key)
    return True


def ab(x):
    """Same X->X entry point on sources and on evidence-bearing differences."""
    y = deepcopy(x)
    try:
        admissible(x)
    except (ValueError, KeyError, TypeError) as exc:
        y['outcome'] = 'CONTRACT_IMPLEMENTATION_LIMIT'
        y['reasons'] = [str(exc)]
        return y
    y['tables'] = []
    y['reasons'] = []
    missing = []
    for table_index, table in enumerate(x['tables']):
        axes = table['axes']
        if not axes:
            missing.append({'table': table_index, 'reason': 'no remaining native binary axis; no further contrast inferred'})
        for axis_index, axis in enumerate(axes):
            remaining = axes[:axis_index] + axes[axis_index + 1:]
            cells = {}
            for coord in coordinates(remaining):
                lo = coord[:axis_index] + '0' + coord[axis_index:]
                hi = coord[:axis_index] + '1' + coord[axis_index:]
                if lo not in table['cells'] or hi not in table['cells']:
                    missing.append({'axis': axis, 'coordinate': coord, 'reason': 'required corner absent'})
                    continue
                positive, negative = table['cells'][hi], table['cells'][lo]
                key = 'd' + str(len(y['nodes']))
                while key in y['nodes']:
                    key += '_'
                y['nodes'][key] = {'kind': 'difference', 'value': x['nodes'][positive]['value'] - x['nodes'][negative]['value'],
                                   'positive': positive, 'negative': negative,
                                   'axis': axis, 'orientation': '0->1', 'remaining_coordinate': coord}
                cells[coord] = key
            y['tables'].append({'axes': remaining, 'cells': cells, 'route': table['route'] + [axis]})
    values = [y['nodes'][key]['value'] for table in y['tables'] for key in table['cells'].values()]
    if missing:
        y['outcome'] = 'PARTIAL' if values else 'UNKNOWN'
        y['reasons'] = missing
    elif not values:
        y['outcome'] = 'UNKNOWN'
        y['reasons'] = ['no evidenced contrast available; this is not earned zero']
    else:
        y['outcome'] = 'SUPPORTED_MOVEMENT' if any(v != 0 for v in values) else 'EARNED_ZERO'
    y['history'].append({'input_tables': deepcopy(x['tables']), 'input_outcome': x['outcome'],
                         'native_rule': RULE, 'output_outcome': y['outcome']})
    admissible(y)
    return y


def show_tables(x):
    return [{'axes': t['axes'], 'route': t['route'],
             'values': {c: x['nodes'][node]['value'] for c, node in t['cells'].items()}}
            for t in x['tables']]


def witness():
    # The only fixture in this run. Source values and axes are initial choices.
    x0 = {'rule': RULE,
          'nodes': {'s' + c: {'kind': 'source', 'value': value, 'source': 'fixture:binary-square:' + c}
                    for c, value in [('00', 0), ('01', 1), ('10', 1), ('11', 0)]},
          'tables': [{'axes': ['a', 'b'], 'cells': {c: 's' + c for c in ['00','01','10','11']}, 'route': []}],
          'history': [], 'outcome': 'INPUT_EVIDENCE', 'reasons': []}
    report = {'candidate_scope': 'bounded native integer finite differences; not general A/B identification',
              'outside_choices': ['complete binary-square fixture', 'axis names and binary domain',
                                  'orientation 0->1', 'integer subtraction', 'process every remaining axis'],
              'outside_choices_between_calls': [], 'X0': deepcopy(x0)}
    try:
        admissible(x0)
        x1 = ab(x0)
        report['X1'] = deepcopy(x1)
        assert x0 == report['X0'], 'first call mutated source'
        report['X1_directly_admissible'] = admissible(x1)
        # No extraction, reorientation, adapter or new parameters between calls.
        x2 = ab(x1)
        report['X2'] = deepcopy(x2)
        assert x1 == report['X1'], 'second call mutated prior result'
        assert x1['outcome'] == x2['outcome'] == 'SUPPORTED_MOVEMENT'
        assert [t['values'] for t in show_tables(x1)] == [{'0': 1, '1': -1}, {'0': 1, '1': -1}]
        assert [t['values'] for t in show_tables(x2)] == [{'': -2}, {'': -2}]
        assert [t['route'] for t in x2['tables']] == [['a', 'b'], ['b', 'a']]
        for key, node in x0['nodes'].items():
            assert x1['nodes'][key] == node and x2['nodes'][key] == node
        assert len(x1['nodes']) == 8 and len(x2['nodes']) == 10
        report.update(result='SUPPORTED_TWO_STEP_NATIVE_MOVEMENT',
                      first_missing_relation=None, X1_values=show_tables(x1), X2_values=show_tables(x2),
                      evidence_checks='source values, both comparison routes and signed parent references retained; derived values checked',
                      untested=['other fixtures', 'third call', 'unknown/zero/error branches', 'general distinction discovery'])
    except Exception as exc:
        report.update(result='CONTRACT_IMPLEMENTATION_LIMIT', error=repr(exc))
    print(json.dumps(report, indent=2))
    return 0 if report['result'] == 'SUPPORTED_TWO_STEP_NATIVE_MOVEMENT' else 1


if __name__ == '__main__':
    raise SystemExit(witness())
