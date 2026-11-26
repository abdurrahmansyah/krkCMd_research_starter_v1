# M03_SPLIT_PROTOCOL.md — Scientific Dataset & Split Governance (M03)

**Dataset Contract (Verified):** `19,098` rows × `510` raw columns (`x1..x501`, target `MANwidth` in µm, `4,900` zero-width rows, `DLMwidth` & `AEDwidth` comparison-only, `3,183` `Series + Image + Gridline` groups × `6` stages).

## 1. Protocol A — Legacy Exploratory Benchmark (Historical Split Preserved)
- Manifest: `reports/tables/group_split_manifest.csv` (`12,216` train / `2,036` groups; `3,060` val / `510` groups; `3,822` test / `637` groups; zero gridline-group overlap).
- **Governance Rule:** Historical test results have already influenced project decisions (`M00`–`M02`). Use Protocol A for M00 comparability and `DLMwidth`/`AEDwidth` comparison; **do NOT perform iterative HPO or finalist selection on the historical test set.**

## 2. Protocol B — Stricter `Series + Image` Grouped Internal Evaluation
- **Audit (`M03_SPLIT_AUDIT.json`):** `36` distinct `Series + Image` groups (`CMd_0.23_20mths`: `8`, `CMd_0.23_2mths`: `8`, `CMd_0.28_20mths`: `4`, `CMd_0.28_2mths`: `16`; group sizes `60..924`, median `513.0`).
- **3-Fold vs. 5-Fold Trade-off:**
  - `3-Fold` (`protocol_b_series_image_3fold.csv`, fold sizes `6,246 / 6,444 / 6,408`): guarantees every fold can represent all 4 `Series` (since `CMd_0.28_20mths` has `4` images), at the cost of smaller training sets (`~67%`).
  - `5-Fold` (`protocol_b_series_image_5fold.csv`, fold sizes `3,834 / 3,828 / 3,816 / 3,786 / 3,834`): gives `~80%` training per fold and balanced row counts, but `CMd_0.28_20mths` (`4` images) is absent from 1 fold.
- **Caveat:** Internal splits of the same `19,098`-row dataset are **not** independent external validation.

## 3. Protocol C — Generalization Diagnostics
- Subgroup breakdowns by `Series`, `Stage` (`1..6`), crack-width bin, zero-width (`MANwidth == 0`, `n=4,900`), `Image` held-out, and Leave-One-Series-Out (`protocol_c_leave_one_series_out.csv`). Full Idea 4 domain adaptation remains deferred.
