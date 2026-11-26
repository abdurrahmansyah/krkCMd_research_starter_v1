# M03_REFERENCE_REPRODUCTION_PROTOCOL.md — RF03, RF04 & RF05 Reproduction Protocol

1. **`RF03` — Faithful AED Original (`data/interim/krkCMd_scripts/CrackWidthAED_VBA.txt`):**
   - **Critical Finding:** AED is a **group-sequential (`k=6`)** algorithm, NOT a single-row independent estimator!
   - **Stage 1 (`(row_idx) % 6 == 0`):** Locate first global minimum `min_brightness` across `x1..x501`; expand `y_upper` left and `y_lower` right while `|b - min_brightness| <= accuracy (5)`; locate outer local maxima `j_upper`, `j_lower` using `step=10`, `brightness_increment=5`, and `rel_increment_threshold=0`; width = `(y_lower - y_upper + 1) * 25.4 / 6400 * 1000`.
   - **Stages 2–6 (`(row_idx) % 6 != 0`):** Reuse `j_upper`, `j_lower` **inherited from Stage 1 of the same crack location**; count local extreme points `lpe` using `0.5 * step = 5`; evaluate the 5 `CrackWidth0 = True` healing/closure rules comparing against Stage 1 boundary brightness (`max1_upper`, `max1_lower`); if not closed, find inner minimum in `[j_upper, j_lower]` and expand with `accuracy=5`.
   - **Parity Validation Design:** Compare exact Python port predictions against `AEDwidth` in `krkCMd_table.csv` (not executed in M03).
2. **`RF04` — DLM Pretrained (`data/interim/krkCMd_scripts/krknet.mat`):**
   - MATLAB 5.0 MAT-file containing an opaque `SeriesNetwork`. MATLAB & Deep Learning Toolbox (`nnet`) are **not installed** on `DESKTOP-CQB09OU`. Remains `CONDITIONAL` pending external MATLAB export of exact layer weights/biases and `'zerocenter'` input mean vector.
3. **`RF05` — DLM Retrained (Table 3 15-Layer 1D-CNN):**
   - Verified 15 layers, `Dropout(0.2)`, `SGDM` (`lr=1e-3` -> `1e-5`, batch `128`, `50` epochs), `pi2mi = 3.96875`.
   - Unverified details explicitly marked as assumptions: scalar vs per-feature `'zerocenter'` normalization and exact LR decay schedule (piecewise vs cosine).
