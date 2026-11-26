# M03_NOVELTY_GAP_ANALYSIS.md — Evidence-Based Gap Analysis (M03)

1. **Verified Prior Findings:**
   - Jakubowski & Tomczak (2024) demonstrated 15-layer 1D-CNN (`DLM`) outperforms threshold-based `AED` on `krkCMd` brightness profiles.
   - Recent tabular & time-series literature shows GBDTs (`XGBoost`, `LightGBM`, `CatBoost`), `ROCKET`/`MultiRocket`, `TabR`/`TabM`, and foundation models (`TabPFN-3.5`, `TabICLv2`, `TabDPT`) are competitive on tabular/1D signals.
2. **Proposed Contributions (Targeted Gaps):**
   - **Gap 1 (Leakage-Free Multi-Paradigm Comparison):** Systematic evaluation across 6 paradigms under both `Gridline`-grouped (Protocol A) and stricter `Series + Image`-grouped (Protocol B) splits, addressing the in-sample limitation of `DLMwidth`.
   - **Gap 2 (Illumination & Sensor Robustness):** Quantitative comparison of clean vs. 16 synthetic brightness-profile corruptions (`Idea 2`) and profile-invariant preprocessing (`HY01`/`HY02`) — which existing `krkCMd` benchmarks do not systematically evaluate.
3. **Unresolved Novelty Questions (Do Not Overclaim):**
   - Do not claim *"first of its kind"* without full-text screening of `PMC13611813` (2026 calibrated post-processing paper, not locally present) and all 50 register entries in `references/REFERENCE_REGISTER.md`.
