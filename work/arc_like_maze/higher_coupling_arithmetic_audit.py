"""Independent graph-based audit of the second nonconstant coupling.

No imports from construction or classifier modules. For each of the two
admitted representative lower rules, independently solves the correction
equation for ALL 3^9 upper coupling tables and checks full F3^4 action
commutation and exact cyclic return on every admitted upper table.

Run:
  python -m work.arc_like_maze.higher_coupling_arithmetic_audit
"""
from collections import Counter, deque
from itertools import product

F3 = (0, 1, 2)
LOWERS = {
    1: (0, 1, 2, 0, 2, 1, 1, 1, 1),
    2: (0, 1, 2, 1, 0, 2, 1, 1, 1),
}


def graph_potential(q0, q1, gain):
    adj = [[] for _ in range(9)]
    for u, v, z in product(F3, repeat=3):
        start = 3*v + z
        nv = (v + gain*(u+1)) % 3
        nz = (z + q0[3*u+v]) % 3
        end = 3*nv+nz
        voltage = (q1[3*v+(z+1)%3]-q1[3*v+z]) % 3
        adj[start].append((end, voltage))
        adj[end].append((start, (-voltage) % 3))
    values = [-1]*9
    for root in range(9):
        if values[root] >= 0:
            continue
        values[root] = 0
        todo = deque([root])
        while todo:
            here = todo.popleft()
            for target, voltage in adj[here]:
                requirement = (values[here]+voltage) % 3
                if values[target] < 0:
                    values[target] = requirement
                    todo.append(target)
                elif values[target] != requirement:
                    return None
    return tuple(values)


def update(state, q0, q1, gain, action):
    result = list(state)
    u, v, z = state[:3]
    if action == 'A':
        result[0] = (u+1) % 3
    else:
        result[1] = (v+gain*(u+1)) % 3
        result[2] = (z+q0[3*u+v]) % 3
        if len(state) > 3:
            result[3] = (state[3]+q1[3*v+z]) % 3
    return tuple(result)


def lift(state, potential):
    result = list(state)
    result[2] = (state[2]+1) % 3
    if len(state) > 3:
        result[3] = (state[3]+potential[3*state[1]+state[2]]) % 3
    return tuple(result)


def audit():
    results = {}
    commutations = iterations = 0
    for gain, q0 in LOWERS.items():
        tally = Counter()
        for q1 in product(F3, repeat=9):
            potential = graph_potential(q0, q1, gain)
            if potential is None:
                tally['obstructed'] += 1
                continue
            trace = sum(potential[:3]) % 3
            order = 3 if trace == 0 else 9
            tally['order3' if order == 3 else 'order9'] += 1
            for state in product(F3, repeat=4):
                for action in 'AB':
                    if (update(lift(state, potential), q0, q1, gain, action) !=
                            lift(update(state, q0, q1, gain, action), potential)):
                        raise AssertionError(('commutation', gain, q1, state, action))
                    commutations += 1
                after = state
                for _ in range(order):
                    after = lift(after, potential)
                if after != state:
                    raise AssertionError(('cyclic order', gain, q1, state, order))
                iterations += 1
        results[gain] = dict(tally)
        if tally != Counter({'obstructed': 19440, 'order3': 81, 'order9': 162}):
            raise AssertionError(('classification', gain, tally))
    return {
        'status': 'INDEPENDENT_GRAPH_AND_ACTION_AUDIT_PASSED',
        'results_by_gain': results,
        'state_level_generator_commutations': commutations,
        'full_cyclic_orbits': iterations,
    }


if __name__ == '__main__':
    print(audit())
