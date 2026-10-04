# ARC3 Operator Surface

This is the bridge between ChatGPT reasoning and the live ARC game once a computer is available.

File:

research/dives/ARC3-TRACE-001/direct_agent/operator_shell.py

It is deliberately not an autonomous solver. It exposes a compact, auditable action loop:

1. current state metadata;
2. available actions;
3. frame hash;
4. exact changed-cell count and bounding box after each action;
5. connected-component summary;
6. cropped ASCII rendering of the active board region;
7. append-only JSONL action transcript.

The operator can issue one move at a time, inspect the result, or hand control to an autonomous generation.

This lets the same live environment support two tests:

- HUMAN-LIKE CHATGPT RUN: ChatGPT observes and chooses actions directly.
- AUTONOMOUS AGENT RUN: Gen-0/Gen-1 chooses actions without intervention.

Keep the run types separate. A manually assisted run cannot be relabeled autonomous.

## Start

After the official ARC starter/runtime is installed:

    python operator_shell.py --game ls20 --log runs/ls20.jsonl

Then use commands such as:

    show
    act 3
    act 6 22 41
    reset
    quit

The log is evidence. Do not delete exploratory actions from it when evaluating first-contact performance.
