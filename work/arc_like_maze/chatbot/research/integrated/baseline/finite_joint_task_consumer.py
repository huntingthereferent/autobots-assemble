"""Pure finite-law reference for consuming, not expanding, a witnessed join.

This module does not prove owner provenance, perform HTTP requests, or infer
constraints from ordinary prose. The finite laws are explicitly supplied.
"""
from finite_goal_priority import Law, ROOT
from finite_cross_pin_join import join


def consume(old: Law, new: Law, report, *, goals=(), edges=(), paths=(), destinations=()):
    """Return one Boolean per task obligation after checking the *exact* joint witness.

    A valid edge of the complete underlying finite law is insufficient: the
    edge must be present in the preexisting admitted history.
    """
    if (not isinstance(old, Law) or not isinstance(new, Law) or not
            (goals or edges or paths or destinations)):
        raise ValueError('complete finite laws and a nonempty explicit task required')
    independent = join(old, new, report.words)
    if independent != report:
        raise ValueError('supplied join was not independently replayed')
    if independent.status != 'JOINT_PARTIAL_CORRESPONDENCE_WITNESSED':
        return independent.status, (), independent.contradiction
    fwd = dict(report.state_pairs)
    admitted = {(s, a): (t, ns, nt) for s, a, t, ns, nt in report.admitted_edges}
    checks = []
    for goal in goals:
        checks.append(('GOAL', goal, goal in fwd))
    for source, action in edges:
        checks.append(('EDGE', (source, action), (source, action) in admitted))
    for word, old_end, new_end in paths:
        s, ns, valid = ROOT, ROOT, True
        for a in word:
            edge = admitted.get((s, a))
            if edge is None or edge[1] != ns:
                valid = False
                break
            s, ns = edge[0], edge[2]
        checks.append(('PATH', (word, old_end, new_end),
                       valid and s == old_end and ns == new_end))
    for source, image in destinations:
        checks.append(('DESTINATION', (source, image), fwd.get(source) == image))
    return ('TASK_COMPLETED_ON_JOINT_WITNESS' if all(c[2] for c in checks)
            else 'TASK_REQUIREMENTS_UNPROVED'), tuple(checks), None


if __name__ == '__main__':
    old, new = Law((0, 0, 0)), Law((0, 1, 2))
    joined = join(old, new, ('A', 'BAA'))
    for req in ({'goals':((1,0,0),(2,1,0)), 'edges':((ROOT,'A'),),
                 'paths':(('BAA',(2,1,0),(2,1,0)),),
                 'destinations':(((1,0,0),(1,0,0)),)},
                {'edges':(((1,0,0),'B'),)}):
        print(consume(old,new,joined,**req))
