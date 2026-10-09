# Continuity front page — visual provenance / research lens
Date: 2026-10-08
Repository: `C:\Users\teepa\continuity-live`
Scope: presentation only; existing social-hub template remains approved.

## Current referent
The homepage should **currently read as an active research index**, without converting Continuity into a research-only app. Preserve source identities, live feed, tickers, area entrances, local system ownership, and A/B state.

## A / B observation
A — Current portal-first rendering: a tall personal-attention masthead, identity and day context, vertical ticker stack. Primary source excerpts did not enter the first 950 px screenshot.

B — New research edition: "Start anywhere. Follow the work.", current source observations, compact contextual masthead, small functional text entrances, horizontal inspectable ticker index, archival editoral serif headings, quiet color, flat source panels and visible native excerpts. Current tasks are still readable within a scrollable native panel.

### What survives
- Main feed before area directory; actual source/article lines remain source-owned.
- Same filter controls, expandable ticker witnesses, source groupings, current trail, reset, active work, and side access to local systems.
- Agent monitor and identity actions; runtime activation diagnostic retained behind "Agent note".
- Source snippets and claims are not invented, merged, or relabeled as validated research findings.
- Current `continuity_social_hub_v1` is still an approved provenance parent; the new lens is a **candidate presentation**.

### What changed
- First-viewport hierarchy: source observations visible beneath a compact research masthead.
- Flat archival reference tone replaces oversized rounded consumer cards.
- Ticker index becomes a horizontally scrollable strip; its nested source witnesses are preserved.
- Attention list height constrained to prevent a large blank masthead; day context remains in the side of that masthead.
- Research-index nav anchors and monitor/system entrances are working links.

## Native rendered witnesses (local only)
- Original desktop: `D:\continuity-visual-audit\research-desktop.png`
- Revised desktop: `D:\continuity-visual-audit\research-desktop-after.png`
- True 390 px mobile: `D:\continuity-visual-audit\research-mobile-true.png`
- Mobile DevTools: `innerWidth=390`, `document.documentElement.scrollWidth=390`, main source panel width 374 px. Ticker content scrolls internally, not as page overflow.

## Verification
- 6/6 frontpage movement priority tests
- 6/6 frontage projection tests
- 8/8 external live feed tests
- `node --check runtime/http/app.js` passed
- Visual registry and template JSON read successfully; candidate registered
- `git diff --check` passed (CRLF conversion advisory only)
- HTTP root at `127.0.0.1:18540` served revised research markup

## Boundaries / next movement
- This is visual evidence and a local research-first presentation lens, **not** a research content generator or new A/B architecture.
- This does not assert all external providers are available; providers own the statuses they actually return.
- Not committed or pushed. Other local work (including Ollama A/B integration) is preserved separately.
