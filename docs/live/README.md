# Workstation

[Workstation](work.html) · [Meow Lab 2](cat-keyboard.html) · [Audio intake](suno-intake.html) · [Referent audit](work.html#audit) · [Source provenance](trace.html) · [Workstation source observer](../../systems/workspace/research_observatory.py) · [Read-only workstation implementation](../../systems/workspace/README.md)

The GitHub Pages entrance under `/live/` now redirects to the **Workstation**, not the source provenance graph.

## Meow Lab 2 — Swallow Sounds keyboard

[Meow Lab 2](cat-keyboard.html) is a visibly redesigned playable instrument with four locally synthesized cat calls, four replaceable sound slots, source-file import (browser-decodable WAV/MP3 and other supported formats), waveform display, 13-note sampled keyboard, and the original recorder/sequencer. User audio files remain in browser memory. Import records a source label and SHA-256 digest where WebCrypto is available; **it does not mean the native workstation ran**.

The native path is `systems.workspace.audio_sound_bank`, which accepts up to four named, selected PCM16 WAVs (`miso.wav`, `mochi.wav`, `nori.wav`, `bean.wav`), copies an exact source edition, admits separate jobs in the existing runtime journal, executes the reviewed source worker, independently replays each result, writes original lineage and movement events to the existing workspace journal, and exports verified WAVs plus a manifest. A newly imported sound is never implicitly treated as native-verified. The browser WAV-and-JSON handoff export can be fed into the real local worker.

These creative audio operations are not Suno model copies or ARC/NIH/WORLD evidence. The GitHub Pages site is read-only; the native Python runner is opt-in. [Project instructions](../../work/projects/cat-keyboard/README.md).

## Native audio intake (Suno export compatibility)

[Audio intake](suno-intake.html) is an **independent local, source-first instrument** for user-supplied WAV/MP3 and MIDI files, including files exported through Suno's documented workflows. It provides bounded waveform observation, SHA-256 content identities where supported, audio slicing, playback-rate pitch mapping, PCM16 WAV export, MIDI note/timing inspection, and a provenance manifest. It does **not** connect to Suno accounts, scrape Suno, use private APIs, copy Suno software, or create new generated music. [Scope and evidence](../../work/projects/suno-export-intake/README.md).

## Evidence boundaries

The Workstation reads actual **public GitHub Actions workflow runs** on opening and every three minutes while visible. It displays the *latest observed 50* runs, counts queued/running/passed/failed outcomes within that sample, and lets a viewer inspect the real GitHub jobs and ordered steps for one selected workflow. It uses exact GitHub execution IDs and commit hashes. A workflow pass is evidence only for the checks it ran; it is not proof an unrelated research question was solved.

The research section loads `views/traces/research-live.json`, projected from native research checkpoints, ARC experiments, pinned statuses and explicit walls. Original `next` and `boundary` fields are preserved when recorded. These are **historical source states**, not a claim that all their workers are currently executing. Nothing is invented from a file name or decorative animation.

The display makes no artificial relationship between a GitHub Actions workflow and a research record merely because both appear on the page. A future cross-system link needs an independently checkable source relationship.

Source failure is visible and **does not turn missing data into zeros or imply active work has stopped**. Public GitHub API requests can be rate-limited. Browser checks have no credentials or write access.

## Data audit in the Workstation

The public /live/ entrance still opens the Workstation. The embedded [Referent audit](work.html#audit) is **not** the executions panel and does **not** show run counts, poll GitHub Actions, or use a tickserver. The audit reads a source-pinned Git tree only when opened or manually reloaded.

Choose a project such as ARC, WORLD, World48, NIH, A/B, W13 or Workstation. An explicit file-path classifier collects tracked Python test-like files and recorded JSON data files; unmatched sources remain **Unassigned** and the full index is available. Test mode opens the original source at the pinned commit and walks individual `test_*` methods/functions, showing source lines, recognized assertions and the complete test block. Data mode opens an original JSON record and walks its top-level fields and individual array entries, without treating successful JSON parsing as evidence that the recorded measurements are correct. Previous/next navigation advances through entries and then files.

An audit assessment is made by the **human reviewer**, not by this source browser. Assessments and notes can be exported as JSON with the source commit, file's Git blob identity, and test name/line or data-record key. They are not silently saved, treated as passed tests, or submitted to GitHub. A declared assertion is not an observed execution result. Dynamically generated, parametrized and differently named tests may require manually opening original code; the index is not proof that a project's entire test coverage has been discovered.

The existing periodically committed research projection appears as a **separate** data source, with its original recorded movements, boundaries and paths. An apparent match between a test path and research source is organizational, not proof one executed the other. Actual job and step outcomes remain in the Workstation's **Executions** section rather than being misrepresented as data audit results.

## Source provenance diagram

The [source provenance view](trace.html) draws a **bounded, schematic** commit ancestry diagram using only public GitHub parent SHA relationships and exact Actions head SHA matches. The surrounding ledger preserves commit messages, dates, author attribution, and links to the original records. Its moving markers replay observed relationships; no animation is a new event, and graphic position is not a measured scientific quantity.

The diagram requests the latest 24 public commits and 60 recent workflow runs, counts only matching records for the selected root, and displays no more than 10 workflow-run symbols to avoid overplotting. Gaps in the public sample are not inferred as negative findings.

## What was borrowed from REA

The [REA reverse-engineering project](https://github.com/morluto/rea) inspired the *investigation format*: preserved source evidence, drill-down by observation, and explicit unresolved questions. No REA source files, tool hooks, or dependency code were copied; this is a small native HTML/JS observer for our own records. REA's internal evidence contracts remain REA's, not an assumed native workstation relation.

## Local workstation

The public GitHub Pages site cannot inspect a private runtime journal. For local process handoffs, workspace return points, editable editions and authorized worker state, use the [existing loopback-only workstation viewer](../../systems/workspace/README.md). Never publish its private runtime data to GitHub Pages without deliberate review.

## Test

```sh
python -m unittest -v network.tests.test_referent_audit_ui network.tests.test_work_activity_ui network.tests.test_live_source_field network.tests.test_research_observatory
python -m views.traces.research_live
```

The site is deployed at [https://huntingthereferent.github.io/autobots-assemble/live/](https://huntingthereferent.github.io/autobots-assemble/live/), subject to a successful GitHub Pages build after each relevant change.
