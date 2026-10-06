# Migration Map — v0.17 Sports Betting

| Old element | New layer |
|---|---|
| search/find odds or public info | `research.source` |
| relation source/timestamp | `core.provenance` |
| missing/partial evidence rules | `core.evidence` |
| generic snapshot | `network/` |
| `pessimistic_probability` | sports-betting domain calculation |
| `safe_ev` | sports-betting domain calculation |
| `quarter_kelly` | sports-betting domain calculation |
| `exposure_used` | sports-betting domain calculation |
| `decide` | `domain.sports-betting.decision` |
| `record_decision` | `core.movement` + provenance |
| sports output mode | output lens over pure domain assessment |
| hidden default caps | replace with explicit policy evidence |
| missing uncertainty → 0 | remove; preserve WALL/UNKNOWN |
| missing day P/L → 0 | remove unless explicitly supplied by policy |

The frozen v0.17 `sports_loss_policy.py` remains evidence of the earlier implementation. It should not be copied verbatim into the active architecture because some of its fallback assumptions conflict with the current evidence contract.
