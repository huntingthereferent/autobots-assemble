# Source-root live field

This is a **browser-executable page**, not a prerecorded SVG in a GitHub README.

- [Open the HTML source](index.html)
- [Source-root research projector](../../views/traces/research_live.py)
- [Original workstation observer](../../systems/workspace/research_observatory.py)
- [Live program regression tests](../../network/tests/test_live_source_field.py)

## What actually moves

The page obtains recent commits and completed workflow runs from GitHub's public API **when opened and every two minutes while the tab is visible**. The default root is the oldest observed commit in the recent 24-commit sample, not the origin of all work. The viewer can choose another observed root.

Each directed edge is made only from a native relationship:

1. A commit reports the exact parent SHA in GitHub; that parent's node can lead to the child.
2. A completed workflow run has `head_sha` exactly matching one sampled commit. A run attaches to that commit; whether it passed or failed is preserved.

The graph searches outward from the selected observed root, not toward any predetermined destination. Unrelated commits and runs cannot be spliced in just to make a pattern. Counters and graph geometry recalculate from the observed relationships. Edges and numeric displays change when actual source observations change.

Moving particles **replay already-recorded edges**; they do not claim fresh events on every frame. If GitHub cannot be reached, the page reports a source error and does not manufacture a change.

Separately, the [published workstation projection](../../views/traces/research-live.json) includes original structured ARC research, checkpoints and explicit walls. That projection is regenerated only when its originals are changed and verified. This is a **research record index**, not a live-running historical execution journal. Being on the same page does not imply the underlying studies are a single physical phenomenon.

## Publishing

GitHub's plain profile README **cannot execute JavaScript**, and a raw source file is not an interactive website.

The repository currently has GitHub Pages **disabled**. After this is merged to main, a repository admin needs to visit [Settings → Pages](https://github.com/huntingthereferent/autobots-assemble/settings/pages) and select:

- Source: **Deploy from a branch**
- Branch: **main**
- Folder: **/docs**
- Save

Then the intended website route is `https://huntingthereferent.github.io/autobots-assemble/live/` (do not claim it works until a Pages deployment succeeds). [GitHub's publishing-source instructions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) describe this setup.

Public API requests from visitors are rate-limited by GitHub. This first boundary uses a recent 24-commit sample and at most 60 workflow runs, with independent root selection. It is not yet a live joined graph of solar data, earthquakes, markets and other external systems. Those need owner/source-native verification adapters before any directed link is drawn.

## Test

```bash
python -m unittest -v network.tests.test_live_source_field network.tests.test_research_observatory
python -m views.traces.research_live
```

The published JSON and source code are part of the original repository. Only the browser fetches the public API; no API token or client credential is needed.
