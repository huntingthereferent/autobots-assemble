# Continuity native A/B — first real Qwen inference witness

**Date:** 2026-10-08
**Status:** Actual model-selected read observed, not autonomous build completion.

## Referent and implementation
The existing Continuity A/B agent lineage/evaluator was connected to a local Qwen model via `runtime/ollama_ab.py`, without creating a replacement agent or requiring Codex.

Because model storage on `E:` stalled, a separate Ollama instance was started on `D:`, preserving all incomplete `E:` download files. No original agent journal or task status was changed.

- Local model: `qwen3:4b-instruct`, Q4_K_M, 2.5 GB
- Ollama server: `127.0.0.1:11435`; model storage `D:\Ollama\models`
- Canary Continuity service: `127.0.0.1:18541`, isolated `D:\Ollama\continuity-canary-state`
- Original Continuity agent server: `127.0.0.1:18540`, unchanged.
- Reusable startup scripts: `D:\Ollama\start-ollama-d.ps1` and `D:\Ollama\start-continuity-local-ai.ps1`
- Source: `runtime/http/index.html`
- SHA-256: `1755cc2e0613381a3f004ca46595aa13b12962ddd15e39499823b7d8af4caf9f`

## Witnessed movement
1. Official Ollama registry download and SHA-256 verification completed; model installed (`ollama list` and API tags confirmed).
2. Separate local inference produced valid JSON `{"state":"MOVE","source":"runtime/http/index.html","direction":"inspect source","next_edge":"compare evidence"}`.
3. Raw local inference: wall time 8.87 sec, model duration 8.84 sec, 82 prompt tokens, 24 generated tokens, approximately 9.86 generated tokens/sec.
4. The existing `AgentLineage.evaluate` callback invoked Qwen with the actual task relations; it proposed `MOVE` and selected `runtime/http/index.html`.
5. The bounded repository-reading tool actually read that source and recorded SHA-256 `1755cc2e0613381a3f004ca46595aa13b12962ddd15e39499823b7d8af4caf9f`. An independent `Get-FileHash` matched.
6. Agent-pool API reported `evaluator_registered=true`, `model_actor=qwen3:4b-instruct`, `generative_ab_movement.state=MOVE`, `tool=read_native_source`, `elapsed_ms=54453`.
7. Canary's original three task states remained `READY,READY,READY`. `autonomous_site_build_complete=false`. Original live agent server's `model_actor=NOT_REGISTERED`, three tasks `READY`. No claimed build completion.

## Boundaries
The observed AI movement is **one source-select/read/evidence step**. It has not demonstrated autonomous coding or an indefinite self-directed generative loop. CPU-only inference is measured; NVIDIA GPU discovery previously hung. Model was deliberately not wired into original live agent service pending promotion. To reproduce, start the Ollama server on D: before starting the canary; retain isolated data paths to avoid overwriting native agent history.
