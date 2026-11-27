# M03 Approved Decision Snapshot (Recorded at M04A Start)

- **M04A Run ID:** `M04A_20261126_145808_DESKTOP-CQB09OU`
- **Approval Date:** 2026-11-26
- **Source:** Researcher Authorization — M03 Methodology Approval & M04A Execution (`docs/DECISIONS.md` `D-009A` through `D-009J`)

## Approved Decisions

| ID | Summary | Status | M04A Scope Impact |
|---|---|---|---|
| `D-009A` | Protocol A: Legacy exploratory benchmark (`train` + `validation` only) | `APPROVED BY RESEARCHER` | M04A trains on `12,216` train rows and screens on `3,060` validation rows; `test` (`3,822`) sealed. |
| `D-009B` | Protocol B: 3-fold `Series + Image` primary stricter internal evaluation | `APPROVED BY RESEARCHER` | Deferred beyond M04A; not executed in M04A. |
| `D-009C` | 5-fold `Series + Image` sensitivity analysis restricted to finalists | `APPROVED BY RESEARCHER` | Deferred beyond M04A; not executed in M04A. |
| `D-009D` | Protocol C: LOSO evaluation for finalists & representative families | `APPROVED BY RESEARCHER` | Deferred beyond M04A; not executed in M04A. |
| `D-009E` | 23 initial screening candidates; preserve all 32 registered IDs | `APPROVED BY RESEARCHER` | Exactly 23 eligible candidates targeted in M04A; `FM01`, `FM02`, `RF03`, `RF04`, `HY01–HY05` retained in registry. |
| `D-009F` | Primary metric: MAE (µm); tie-breakers: RMSE, Lin's CCC | `APPROVED BY RESEARCHER` | Ranking by raw validation MAE (µm), tie-broken by RMSE and Lin's CCC. |
| `D-009G` | HPO deferred to M05 | `APPROVED BY RESEARCHER` | Zero HPO in M04A; prespecified `scientific_v1` configurations only. |
| `D-009H` | Reference Track (`RF03` AED original, `RF04` pretrained DLM) separate | `APPROVED BY RESEARCHER` | Does not block M04A screening. |
| `D-009I` | Preserve raw and nonnegative-clipped (`max(0, y_pred_raw)`) predictions | `APPROVED BY RESEARCHER` | Raw MAE used for primary screening ranking; clipped metrics reported separately. |
| `D-009J` | Full comparative robustness follows screening and tuning | `APPROVED BY RESEARCHER` | Zero actual-data corruption sweeps in M04A. |

**Unapproved / Deferred:** All other M03 proposals (`M04` full outer Protocol B/C, M05 HPO, Idea 2 robustness sweeps, custom `HY01–HY05`) remain unapproved for execution in M04A.
