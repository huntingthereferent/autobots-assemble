# Workstation

[Workstation](work.html) · [Source provenance](trace.html) · [Workstation source observer](../../systems/workspace/research_observatory.py) · [Read-only workstation implementation](../../systems/workspace/README.md)

The GitHub Pages entrance under `/live/` now redirects to the **Workstation**, not the source provenance graph.

## Evidence boundaries

The Workstation reads actual **public GitHub Actions workflow runs** on opening and every three minutes while visible. It displays the *latest observed 50* runs, counts queued/running/passed/failed outcomes within that sample, and lets a viewer inspect the real GitHub jobs and ordered steps for one selected workflow. It uses exact GitHub execution IDs and commit hashes. A workflow pass is evidence only for the checks it ran; it is not proof an unrelated research question was solved.

The research section loads `views/traces/research-live.json`, projected from native research checkpoints, ARC experiments, pinned statuses and explicit walls. Original `next` and `boundary` fields are preserved when recorded. These are **historical source states**, not a claim that all their workers are currently executing. Nothing is invented from a file name or decorative animation.

The display makes no artificial relationship between a GitHub Actions workflow and a research record merely because both appear on the page. A future cross-system link needs an independently checkable source relationship.

Source failure is visible and **does not turn missing data into zeros or imply active work has stopped**. Public GitHub API requests can be rate-limited. Browser checks have no credentials or write access.

## Source provenance diagram

The [source provenance view](trace.html) draws a **bounded, schematic** commit ancestry diagram using only public GitHub parent SHA relationships and exact Actions head SHA matches. The surrounding ledger preserves commit messages, dates, author attribution, and links to the original records. Its moving markers replay observed relationships; no animation is a new event, and graphic position is not a measured scientific quantity.

The diagram requests the latest 24 public commits and 60 recent workflow runs, counts only matching records for the selected root, and displays no more than 10 workflow-run symbols to avoid overplotting. Gaps in the public sample are not inferred as negative findings.

## What was borrowed from REA

The [REA reverse-engineering project](https://github.com/morluto/rea) inspired the *investigation format*: preserved source evidence, drill-down by observation, and explicit unresolved questions. No REA source files, tool hooks, or dependency code were copied; this is a small native HTML/JS observer for our own records. REA's internal evidence contracts remain REA's, not an assumed native workstation relation.

## Local workstation

The public GitHub Pages site cannot inspect a private runtime journal. For local process handoffs, workspace return points, editable editions and authorized worker state, use the [existing loopback-only workstation viewer](../../systems/workspace/README.md). Never publish its private runtime data to GitHub Pages without deliberate review.

## Test

```sh
python -m unittest -v network.tests.test_work_activity_ui network.tests.test_live_source_field network.tests.test_research_observatory
python -m views.traces.research_live
```

The site is deployed at [https://huntingthereferent.github.io/autobots-assemble/live/](https://huntingthereferent.github.io/autobots-assemble/live/), subject to a successful GitHub Pages build after each relevant change.
