# M03_STATISTICAL_ANALYSIS_PLAN.md — Cluster-Aware Statistical Inference (M03)

1. **Statistical Unit:** Repeated observations across `Stage 1..6` within a `Gridline` (`3,183` groups) and adjacent gridlines within an `Image` (`36` images) are **not** independent.
2. **Uncertainty & Hypothesis Testing:**
   - **Paired Cluster Bootstrap** (`B = 2,000` resamples at `Series + Image + Gridline` or `Series + Image` cluster level) for 95% CIs on `MAE`, `RMSE`, and `Lin's CCC`.
   - **Cluster-Aware Paired Permutation Test** (`2,000` sign-flips of cluster-level paired error differences) for pairwise model comparisons.
   - **Multiple-Comparison Control:** **Holm's step-down** adjustment across candidate comparisons against the primary baseline (`ExtraTrees` / `DLMwidth`).
   - **Repeated Seeds:** Minimum `3`–`5` seeds for stochastic neural/tree models under Protocol B.
   - **Equivalence Testing (TOST):** Only permitted with a prespecified engineering margin (e.g., `±3.97` µm = 1 pixel at 6400 dpi) declared before evaluation.
