# Continuity — ticker movement and source-entry A/B witness
2026-10-08 · research front page · local runtime 127.0.0.1:18540
Parent visual template: continuity_research_index_v1 (candidate)
Parent architecture: continuity_social_hub_v1 (approved)

## Current referent
The research frontage must let a reader move through native feed layers. The same source witnesses survive when crossing an index/ticker, source-specific view, expanded witness list, or external provider page.

## A: observed wall
The previous ticker used native <details> inside a horizontally clipped strip. Opening a layer did not reveal the source witnesses in the visible layout. Source coverage rows were static div elements. Mobile CSS hid the entire sidebar with external feeds. CSS density compressed the vertical tickers but did not create horizontal ticker motion.

## B: observed change
- The marquee is a continuous, source-grounded horizontal index: each button labels a native category/source, its witnessed status, and latest witnessed headline.
- Clicking a ticker opens a bounded-height detail panel OUTSIDE the ticker overflow. Grouped claims remain separate and original source titles link to native external URLs.
- The marquee pauses on hover, focus, or a selected ticker, and does not animate when reduced motion is preferred.
- External-source coverage entries use a native <details>/<summary> for accessible keyboard activation. Each exposes sampled items, native item URLs, feed URL, and provider documentation when those are present. Missing provider links are never fabricated.
- "View in main research feed" enters the source-filtered existing feed and preserves article provenance. "All sources" restores the full view.
- Mobile now has a compact "External feeds / open source index" entrance BEFORE the report stream; each source is expandable there. Desktop sidebar is preserved.
- Source content remains fetched/ephemeral, not durably or artificially merged. No new agent or A/B architecture.

## Native runtime / browser witnesses
Actual Chromium DevTools browser against local Continuity HTTP runtime:
- 42 visible root ticker categories, 28 externally configured native feeds, 185 fetched item witnesses.
- Marquee transform advanced horizontally from x=0px to x=-48.2181px across roughly 0.75 seconds.
- Clicking All feeds: selected witness panel visible with 185 native feed items and aria-expanded=true. Clicking again closed it.
- Clicking Agência Brasil Education: accordion opened with 8 fetched articles and the native RSS URL https://agenciabrasil.ebc.com.br/rss/educacao/feed.xml.
- The source-scoped main feed displayed 8 articles from that same source only; reset restored normal source scope.
- At mobile viewport 390px, document scroll width remained 390px and the mobile source index rendered 28 independently expandable feed entries.
- Prefers-reduced-motion emulation produced animationName=none.
- Browser recorded NO JavaScript exceptions.

## Regression checks
- 4 research interaction structural tests: pass
- 6 frontpage movement priority tests: pass
- 6 frontage projection tests: pass
- 8 external live feed tests: pass
- JavaScript parse validation and git diff --check: pass

## Boundary
Only this local checkout was changed; no GitHub push. Existing Ollama adapter, current agent lineage, saved handoffs, and other dirty worktrees were not altered by this visual pass.
