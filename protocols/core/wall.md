# Core Protocol — Wall

A wall is a valid result, not a failure to reason.

## Emit a wall when

- required evidence is unavailable;
- an external permission/account/file is required;
- a correspondence rule is missing;
- the available tool cannot perform the required action;
- two layers use incompatible witness contracts;
- continuing would require inventing data or authority.

## Wall record

Record:

- current referent;
- exact missing condition;
- evidence already available;
- what would dissolve the wall;
- next admissible action, if one exists.

Do not route around a wall by silently changing the referent.

## Swallow-first when a search/agent runtime is available

For A/B-enabled execution, UNKNOWN/WALL is a missing-world-reference candidate
before it is a human task:

```text
preserve exact wall
-> outward traversal of native source/system/tool/workflow/reference
-> bounded locator + provenance (do not copy or replace its native state)
-> compare candidate against the same wall through A/B admission
-> admit evidence-valid reference -> resume original work
-> no MOVE: retain exact wall and appended search/attempt history
-> remaining reground agents
-> only then consider human escalation through an explicit guard
```

No outward search recorded is not the same as a failed search. Neither permits
an automatic human escalation. A new reference is admitted only through a
separately verified comparison; resemblance alone is not closure.

The runtime adapter and its limitations are documented in
`runtime/README.md`. This is a contract, not proof that every configured
agent already uses the adapter.
