# ARC A/B Evidence Log

## Scope
Clean ARC-AGI-3 work. The live board and competition goal are the current material.
Old ARC agents and game source are not solve guidance.

## Rule for this log
Record what the board actually supported:
current whole board -> relation present -> movement -> returned whole board -> what survived/changed -> next supported movement.
Do not silently turn an action number into a permanent semantic.
Do not turn a successful witness into a general rule without another witness.

## ar25

### Initial board
- 64x64 live board.
- Goal supplied by environment: 8 levels.
- Whole-board visual relation includes paired L-shaped structures across a central vertical structure.
- Fresh interaction established that actions 1/2 and 3/4 transform the paired structures in opposing directions.
- Action meanings are NOT assumed permanent.

### Level 1 — earned witness
Movement:
- ACTION3 x5
- ACTION2 x10

Result:
- levels_completed: 0 -> 1

Witness:
- The two whole-board L structures reached the correspondence required by the environment.
- This is direct completion evidence, not inferred reward.

Boundary:
- This witnesses that sequence for this board state only.
- It does not establish permanent meanings for ACTION3/ACTION2.

### Returned board after level 1
The whole configuration changed.
After ACTION5, the operative transformation changed:
- same action IDs no longer preserve the earlier displacement relation;
- e.g. ACTION4 produced a different coupled movement, including 6-cell movement of one structure.
Therefore action-label semantics are not the reusable object. The board relation is.

### Current movement
Continue from the returned whole board under the same evidence contract.
