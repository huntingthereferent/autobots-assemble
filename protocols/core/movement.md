# Core Protocol — Movement

## Input

- current referent
- admissible evidence
- protocol-specific witness conditions

## Witness contract

A movement is admitted only when the protocol's required conditions are supported. Record exactly which evidence satisfied which condition.

## Output

A movement produces:

- result state: \`MOVE\`, \`WALL\`, \`UNKNOWN\`, or \`PARTIAL\`;
- output relation(s), if supported;
- provenance / witness record;
- next referent or explicit continuation;
- no deletion of older evidence.

## Closure

The output must be usable as the next input under the same outer contract. If an output requires a new hidden evidence standard to continue, the movement is not closed and must be marked as a wall or protocol boundary.
