# ARC3 First-Contact Runbook

This runbook exists to preserve the distinction between:

```text
finding a solution
and
replaying a solution already found
```

The first untouched run is the primary witness for the active referent.

## Setup

Use the official starter:

https://github.com/arcprize/ARC-AGI-3-Kaggle-Starter

On the machine that will run the benchmark:

```bash
git clone https://github.com/arcprize/ARC-AGI-3-Kaggle-Starter.git
cd ARC-AGI-3-Kaggle-Starter
make setup
```

Copy:

`research/dives/ARC3-TRACE-001/direct_agent/my_agent.py`

to a local path and run it with:

`research/dives/ARC3-TRACE-001/direct_agent/run_first_contact.py`

Example:

```bash
python run_first_contact.py \
  --starter-root /path/to/ARC-AGI-3-Kaggle-Starter \
  --agent /path/to/my_agent.py \
  --out first_contact_run.json
```

## First-contact rule

Before this run:

- do not inject public solution sequences;
- do not add per-game ID branches;
- do not tune from the public game's known answer;
- do not replace the agent after seeing a game and continue calling it one run.

The runner hashes the exact agent file and refuses to overwrite the witness by default.

## What counts

Count:

- every exploratory environment action;
- every execution action;
- resets/deaths if the framework counts them in the action budget;
- every level reached during that same untouched run.

Do not replace the count with:

- a minimized path;
- a later successful replay;
- a path generated after reading the solution;
- a post-hoc shortest route through a learned world model.

## After the first run

The first run becomes immutable evidence.

Then improvements are allowed, but they form a new generation:

```text
agent generation 0
→ untouched public run
→ failure analysis
→ generic correction
→ agent generation 1
→ new clean evaluation
```

A generic correction changes the solver's reusable machinery.

A per-game answer patch does not establish first-contact generality and should be kept out of the competition agent.

## Acceptance ladder

### PUBLIC COMPLETION

```text
25/25 games
183/183 levels
```

### PUBLIC FIRST-CONTACT HUMAN-EFFICIENT

Public completion **and** the untouched discovery-inclusive run meets the official human-efficiency threshold on every game.

### PRIVATE 100%

Only an official hidden competition rerun can establish this.

Public success does not silently promote to private success.
