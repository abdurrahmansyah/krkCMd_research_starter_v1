# M04A Proposed Finalist Shortlist (Awaiting Researcher Approval)

- **Run ID:** `M04A_20261126_145808_DESKTOP-CQB09OU`
- **Status:** `PROPOSED` (Zero automatic approval; single-seed `seed=42` Protocol A exploratory screening only)
- **Primary Ranking Rule:** Raw Validation `MAE (µm)` -> `RMSE (µm)` -> `Lin's CCC` (`D-009F`, `D-009I`).

---

## Proposed Multi-Paradigm Shortlist for M04B / Protocol B & M05

To preserve multi-paradigm scientific diversity across Idea 1 and Idea 2 without prematurely eliminating slower or tunable architectures:

| Paradigm | Proposed Finalists | M04A Raw MAE (µm) | M04A Raw RMSE (µm) | Lin's CCC | Rationale |
|---|---|---:|---:|---:|---|
| **Classical / Bagging** | `ML01` (Extra Trees), `ML02` (Random Forest) | `14.25` / `14.56` | `28.94` / `29.87` | `0.9796` / `0.9783` | Overall #1 and #3; zero negative raw predictions; strong baseline |
| **Gradient Boosting** | `ML04` (XGBoost), `ML06` (CatBoost), `ML05` (LightGBM) | `14.74` / `14.98` / `15.00` | `29.68` / `29.05` / `29.65` | `0.9786` / `0.9796` / `0.9787` | Tight cluster (`14.74–15.00 µm`); `ML06` has #2 lowest RMSE (`29.05 µm`) |
| **Tabular Foundation** | `FM03` (TabICLv2) | `14.39` | `29.17` | `0.9794` | #2 overall zero-shot (`83.25s` total); strongest non-tree model |
| **Tabular Deep Learning** | `DL03` (RealMLP), `DL02` (FT-Transformer) | `16.66` / `16.73` | `31.41` / `31.36` | `0.9762` / `0.9768` | Leading neural tabular architectures; strong candidates for M05 tuning |
| **Spatial / Signal** | `SG06` (MultiROCKET-HYDRA) | `22.33` (`20.61` clipped) | `33.46` (`32.75` clipped) | `0.9730` | Best spatial convolution representation (`SG06`); `SG04` (`27.72`) as lightweight TF baseline |
| **Reference Anchors** | `RF05` (DLM retrained), `RF02` (Linear), `RF01` (Dummy Mean) | `17.49` / `52.45` / `120.27` | `33.68` / `70.37` / `145.79` | `0.9728` / `0.8722` / `~0` | Domain CNN, linear, and sanity reference anchors |

## Notes on Failed / Deferred Candidates
- `FM04` (`TabDPT`), `SG02` (`ResNet-1D`), `SG03` (`InceptionTime`): Hit the provisional `3,600s` worker timeout (`SG02`/`SG03` on CPU-only native Windows TF; `FM04` with `SUSPEND_DETECTED` at `3,601.5s`). Not eliminated on accuracy; require explicit researcher budget approval (higher timeout or PyTorch GPU re-implementation for `SG02`/`SG03`) if included in M04B.
- `FM01`, `FM02`: `BLOCKED_LICENSE` pending personal researcher PriorLabs acceptance.
- `RF03`, `RF04`: Separate Reference Track (`D-009H`).
- `HY01–HY05`: Deferred custom designs.
