# ARC3 Public 100% — Prior Art / Claim Boundary

## Verified public result

OpenWorld's current public evidence records a Claude Fable 5 source-free run that completed:

- 25/25 public ARC-AGI-3 games;
- 183/183 public levels;
- with process-isolated game execution so the solving agent did not read game source.

Evidence:

- https://github.com/quome-cloud/openworld/blob/main/experiments/results/arc3_fullgame_sourcefree_fable.json
- https://github.com/quome-cloud/openworld/blob/main/experiments/results/arc3_milestone.json

This establishes that **public ARC3 completion is solved prior art**.

## Important RHAE caveat

OpenWorld also reports mean RHAE 100.0 on the 25 banked public solution paths.

However its own E120/E149 documentation makes the scope explicit:

```text
RHAE
= efficiency of the final banked replay path

RHAE
!= total cost/actions used to discover that path
```

The discovery process included exploration, repeated sessions, model reasoning, code-world-model construction, and search. E149 explicitly calls discovery cost an omitted axis.

Therefore:

```text
public 25/25 + banked-path RHAE 100
!=
first-contact human-efficient 100
```

The latter remains the relevant target for this project.

## Useful prior-art shape

The public perfect-completion system's broad shape is:

```text
observe pixels
→ build/update executable world hypothesis
→ verify predictions against real transitions
→ infer goal
→ plan inside model
→ replay plan on real environment
→ correct on mismatch
```

Use this as prior evidence, not as architecture that must be copied.

## Discovery-cost evidence

OpenWorld E149 reports that its public Fable sweep required substantial discovery effort even though the final banked paths were human-efficient.

That means the main unsolved seam for "solve like a human" is not shortest-path execution after learning.

It is:

```text
learn enough of a novel game
with very few real actions
while simultaneously progressing toward the win
```

## Active claim boundary

We may claim:

- public completion is already demonstrated by prior work;
- final path efficiency can reach/exceed human baselines after discovery.

We may not claim:

- our agent has first-contact 100%;
- discovery-inclusive RHAE 100%;
- private competition 100%;

until an actual first-contact evaluator witnesses those results.
