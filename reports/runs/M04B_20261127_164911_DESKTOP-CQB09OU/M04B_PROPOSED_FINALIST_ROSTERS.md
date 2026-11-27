# M04B Proposed Finalist Rosters (Awaiting Researcher Approval)

- **Run ID:** `M04B_20261127_164911_DESKTOP-CQB09OU`
- **Status:** `PROPOSED` (Zero automatic approval; `0` HPO candidates approved yet)

## Three Differentiated Roster Proposals

1. **Compact Roster (5 HPO/inference candidates + 3 fixed anchors = 8 models):**
   - **HPO/Inference:** `ML01` (Extra Trees), `ML04` (XGBoost), `ML06` (CatBoost), `FM03` (TabICLv2, discrete inference only), `DL03` (RealMLP).
   - **Fixed Anchors:** `RF05` (DLM retrained), `RF02` (Linear), `RF01` (Dummy Mean).
   - **Trade-off:** Fastest M05 turnaround (~1.5–2.5 h) while covering Classical, Boosting, Foundation, Tabular DL, and Reference paradigms.

2. **Balanced Roster (9 HPO/inference candidates + 3 fixed anchors = 12 models — Recommended):**
   - **HPO/Inference:** `ML01`, `ML02`, `ML04`, `ML05`, `ML06`, `FM03`, `DL03`, `DL02` (FT-Transformer), `SG06` (MultiROCKET-HYDRA).
   - **Fixed Anchors:** `RF05`, `RF02`, `RF01`.
   - **Trade-off:** Adds `ML02` (Random Forest), `ML05` (LightGBM), `DL02` (attention-based Tabular DL), and `SG06` (Spatial Signal Convolution) (~4–7 h M05 budget).

3. **Expanded Roster (13 HPO/inference candidates + 3 fixed anchors = 16 models):**
   - **Adds to Balanced:** `ML03` (HistGradientBoosting), `DL05` (TabM), `DL04` (TabR), `SG04` (LITETime `n_reg=1`).
   - **Fixed Anchors:** `RF05`, `RF02`, `RF01`.
   - **Note on `FM04`, `SG02`, `SG03`:** All 3 recovered cleanly in M04B (`FM04` `23.90 µm` / `1,863s`, `SG02` `56.42 µm` / `5,082s`, `SG03` `75.03 µm` / `5,891s`), but are excluded from M05 HPO due to high single-run runtime and lower screening accuracy (`SG02`/`SG03` CPU-only TF). They remain preserved in the 32-model registry and may be included as fixed-config comparators in Protocol B if approved.
