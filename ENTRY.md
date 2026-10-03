# AI Entry Protocol

When an AI uses this repository as an extension of the user, do **not** begin by scanning everything and choosing the most interesting layer.

## Entry sequence

1. Read `AB_CONTRACT.md`.
2. Read `state/current.json`.
3. Recover the **preferred current referent**.
4. Read only the protocol(s) reached by that referent.
5. Read the active work/domain record.
6. Pull older evidence only when the active relation requires it.
7. Perform one bounded movement at a time.
8. Record the result, provenance, wall/uncertainty state, and next referent.

## Default output contract

An AI response or repo mutation should make these recoverable:

- current referent
- goal / definition of solved
- evidence actually used
- witness conditions checked
- movement made, if any
- wall / unknown / partial state, if any
- artifacts or changes produced
- next referent / next movement

## Do not

- turn A/B into the implementation layer;
- infer a missing relation because an older layer looks similar;
- upgrade `tested` to `submitted`, `submitted` to `accepted`, or `accepted` to `paid`;
- collapse evidence, interpretation, and action into one undocumented step;
- broaden scope merely because more data exists.

If the user gives a new explicit referent, that becomes primary unless it conflicts with an explicit safety or authority boundary.
