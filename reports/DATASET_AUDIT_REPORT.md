# krkCMd Dataset Audit & Verification Report

**Date:** 2026-11-23  
**Status:** VALIDATED  
**Dataset Path:** `data/raw/krkCMd_table.csv`  

---

## 1. Executive Summary

The raw dataset `krkCMd_table.csv` was subjected to rigorous validation. All data integrity checks passed with zero errors, zero missing values, and zero duplicate rows.

The critical schema discrepancy where the starter template referenced `Grid` was resolved: the official column name in the dataset is **`Gridline`**.

Furthermore, mathematical and physical validation proved that the grouping key **`Series + Image + Gridline`** defines an invariant physical crack location tracked across all 6 self-healing stages without exception.

---

## 2. Dataset Dimensions & Schema

| Metric | Value |
|---|---|
| Total Rows | 19,098 |
| Total Columns | 510 |
| Missing Cells | 0 |
| Duplicate Rows | 0 |
| Metadata Columns | `No`, `Profile`, `Series`, `Image`, `Gridline`, `Stage` (6 columns) |
| Feature Columns | `x1` through `x501` (501 features, strictly ordered) |
| Target Column | `MANwidth` (Manual crack width in micrometers, $\mu\text{m}$) |
| Baseline Columns | `DLMwidth`, `AEDwidth` |

---

## 3. Strict Group & Stage Validation

- **Group Key:** `Series + Image + Gridline`
- **Total Unique Groups:** 3,183
- **Observations per Group:** Strictly **6 observations** for all 3,183 groups (min=6, max=6).
- **Stage Distribution per Group:** Every single group contains **Stage 1, 2, 3, 4, 5, 6 exactly once** (`tuple(sorted(stages)) == (1, 2, 3, 4, 5, 6)` for 100% of groups).
- **Leakage Prevention Verification:**
  3,183 groups * 6 stages = 19,098 rows.
  Splitting by rows would leak the same crack across different stages into train and test sets. Group-aware splitting (`GroupShuffleSplit` on `Series + Image + Gridline`) is strictly mandatory.

---

## 4. Target & Feature Summary

- **Feature Intensities (`x1`..`x501`):** Range [0.0, 255.0], 0 missing values.
- **`MANwidth` Target ($\mu\text{m}$):**
  - Min: 0.00 $\mu\text{m}$
  - Max: 813.59 $\mu\text{m}$
  - Mean: 148.88 $\mu\text{m}$
  - Median: 119.06 $\mu\text{m}$
  - Std: 141.79 $\mu\text{m}$
- **Baseline Comparisons:**
  - `DLMwidth`: mean 147.72 $\mu\text{m}$ (range [0.00, 651.51])
  - `AEDwidth`: mean 125.63 $\mu\text{m}$ (range [0.00, 992.19])

---

## 5. Decision & Next Step

The schema is now aligned and verified. **No model training has been conducted.** All code and configurations reference `Gridline`. The project is prepared for Ide 1 benchmark modeling once approved.
