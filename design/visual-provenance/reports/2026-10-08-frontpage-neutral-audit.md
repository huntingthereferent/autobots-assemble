# Continuity front page — neutral A/B audit and repair
**Date:** 2026-10-08
**Runtime:** `http://127.0.0.1:18540/` (local only)
**Checkout:** `C:\Users\teepa\continuity-live`
**Parent references:** `continuity_social_hub_v1` (approved); `continuity_research_index_v1` (candidate visual lens)

## Current referent
Continuity should currently read as a research site, carrying actual A/B movement between witnessed native sources, related systems, and returning observations. A control must not imply an action or reachability that its implementation does not have. Preserve agent lineage, ephemeral source ownership, established ticker/source expansion, and visual provenance.

## A — independent cold findings (before latest edits)
1. **Broken apparent navigation:** 13 School/Calendar/Personal/Research/Jobs/Factory/Work controls were literal `<button data-source>` but had no JavaScript listeners. Clicking them did not enter the named system or an area.
2. **External navigation blocked by evidence write:** Clicking the headline first opened `about:blank`; the real destination was assigned only in the asynchronous `/api/traces` completion handler. A slow trace could leave a blank page.
3. **Source state was unnecessarily discarded:** Clicking a role filter re-created the ticker strip and source accordions despite unchanged native sources. It reset ticker motion and focus/expanded DOM.
4. **Mixed source filter:** When an already-filtered Social view entered a News publisher, the category filter could hide that publisher's real items.
5. **Unsafe source-to-markup construction:** local `item(title, meta, extra)` used HTML-string interpolation for task IDs, dynamic status/source strings and movement labels. User content could enter HTML parsing.
6. **False action label:** the top-right “Your Continuity” button actually POSTed to the James daily-operations activation endpoint; its consequence was not apparent from the label.
7. **Visual regression:** after native `<summary>` source expansion, provider metadata was larger than the compact research-reference scale.

## B — smallest evidenced corrections
- Changed those 13 dead buttons into real `href="#area-..."` links mapped to currently existing area IDs. The matching native area index auto-expands and the navigation state follows the selected section. The UI now explicitly calls these **related area entrances**, not separate native system apps.
- Converted external article titles from blank-tab buttons into native HTTPS/HTTP anchors (`target="_blank"`, `rel="noopener noreferrer"`). A provenance trace runs asynchronously. The trace says **navigation requested**, never claims the external destination was loaded.
- Renders untrusted local row content with DOM element construction and `textContent` instead of interpolated markup. Preserves existing acknowledgement/admit buttons and status markers.
- Only rebuilds source/ticker DOM after the native feed snapshot changes; role/source-view toggles preserve existing ticker and opened source nodes. Ticker repaint preserves animation position and keyboard focus when possible.
- Source-only entrance switches to the `Latest` tab so the publisher's sampled items are not accidentally excluded by the previous role filter. Visible active-tab state tracks the movement.
- Made the top-right action label “Start daily ops,” with an explicit accessible name for James daily operations, retaining the existing explicit click protocol.
- Restored compact native source metadata, measured at **9.44px** in desktop Chromium.

## Direct browser observations
Rendered and interacted with local Continuity using headless Chromium DevTools; no mock data was substituted:
- 42 root ticker categories and 28 source providers; source sample held 185 items.
- Ticker transform advanced about 47 px horizontally during a 0.75-second observation.
- Opening All feeds exposed 185 native witnesses in its separate expansion; second activation closes it.
- Agência Brasil Education opened with 8 native links, documented provider RSS feed; entering the main stream retained 8 publisher-owned items.
- Role change retained the same ticker DOM and open source accordion (`ticker=true,source=true`).
- From Social → publisher-only stream, the active tab switched to Latest and exposed the publisher's source witnesses.
- Clicking School area entrance changed URL hash to `#area-learn`, opened native area details and marked Learn as active navigation.
- Article headline is a real external `<a>` with HTTPS href and no-opener/new-tab constraints; no blank-tab dependency.
- Injecting literal IMG/SVG/SCRIPT-looking text into a local row created **0** image, SVG or script nodes.
- At 390 px mobile viewport, document scroll width remained 390 px, with mobile external source index accessible.
- Reduced motion set ticker animation to none; browser recorded no JS exceptions.

## Tests
- 4 research navigation tests passed
- 4 research ticker/source tests passed
- 6 front-page movement priority tests passed
- 6 frontage projection tests passed
- 8 external live-feed tests passed
- Node.js syntax check and `git diff --check` passed

**Total: 28 focused Python tests passed**, plus live Chromium interaction checks.

## What survives unchanged
A/B model, agent pool/orchestration, recorded user tasks, task ownership, live source adapter data, current/source trail semantics, original source witnesses, ticker customization, and previously approved template. No new second agent architecture was introduced.

## Gaps, explicitly not promoted to completion
- Actual native School, Factory, Jobs, Research, etc. application pages are not published by this site's current HTTP server. Those controls reach **real related area indexes**, not standalone system workspaces.
- An external link click is a requested traversal witness, not proof that its remote page loaded, responded, or was visited successfully.
- Provider availability varies; feed sample contents are ephemeral. No content or source count was fabricated.
- Existing CSS has several historical presentation overlays; a careful cascade consolidation remains a maintenance opportunity, not a prerequisite for the observed corrections.
- This audit ran the focused 28-test frontage suite, not every unrelated Online School test.
- Edits reside in the current **local** checkout. No GitHub push/commit. Existing Ollama changes and other worktrees remain preserved.

## Native evidence files
- `D:\continuity-visual-audit\audit-final-desktop.png` — local headless desktop capture during audit, before final source typography correction
- `D:\continuity-visual-audit\test-ticker-source.cjs` — direct browser interaction replay
- `network/tests/test_research_frontpage_navigation.py`
- `network/tests/test_research_frontpage_interactions.py`
- `runtime/http/index.html`, `runtime/http/styles.css`, `runtime/http/app.js`
