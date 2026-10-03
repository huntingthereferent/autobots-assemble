# AI Protocol — Session

## Enter

1. Read \`ENTRY.md\`.
2. Read \`state/current.json\`.
3. Load the protocol named by \`state/current.json\`.
4. Load the active record reached from the referent.

## Operate

For each substantive step:

- name the referent internally;
- identify evidence actually used;
- check the witnesses;
- move once or emit a wall/unknown state;
- keep older layers as evidence only;
- write durable changes back to the appropriate layer.

## Exit

Before ending substantial work, leave a recoverable next movement. If repository state changed, update the canonical record or state pointer rather than relying on chat memory alone.
