"""
scripts/audit_dataset.py

Reproducible dataset audit and validation script for krkCMd research.
Enforces schema validation, feature count calculation, strict group key checks,
and 6-stage completeness checks per physical crack location.
"""

import json
import re
from pathlib import Path
import numpy as np
import pandas as pd
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "raw" / "krkCMd_table.csv"
REPORTS_DIR = ROOT / "reports"
TABLES_DIR = REPORTS_DIR / "tables"
FIGURES_DIR = REPORTS_DIR / "figures"
LOGS_DIR = REPORTS_DIR / "logs"

for d in [TABLES_DIR, FIGURES_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("krkCMd DATASET AUDIT & SCHEMA VALIDATION")
print("=" * 60)

if not CSV_PATH.exists():
    raise FileNotFoundError(f"Raw CSV not found at {CSV_PATH}")

# Read CSV (read-only mode)
df = pd.read_csv(CSV_PATH, low_memory=False)
n_rows, n_cols = df.shape
print(f"Loaded CSV: {CSV_PATH.name}")
print(f"Total Rows: {n_rows}")
print(f"Total Columns: {n_cols}")

# 1. Column definitions
REQUIRED_METADATA = ["No", "Profile", "Series", "Image", "Gridline", "Stage"]
EXPECTED_FEATURES = [f"x{i}" for i in range(1, 502)]
REQUIRED_TARGET = "MANwidth"
BASELINE_COLS = ["DLMwidth", "AEDwidth"]
EXPECTED_TOTAL_COLUMNS = len(REQUIRED_METADATA) + len(EXPECTED_FEATURES) + 1 + len(BASELINE_COLS)  # 510

cols = df.columns.tolist()

# 2. Schema Validation
missing_metadata = [c for c in REQUIRED_METADATA if c not in cols]
if missing_metadata:
    raise ValueError(f"CRITICAL: Missing mandatory metadata columns: {missing_metadata}")

# Feature count calculation based strictly on columns present in df
actual_feature_cols = [c for c in cols if c in set(EXPECTED_FEATURES)]
actual_feature_count = len(actual_feature_cols)

if actual_feature_count != len(EXPECTED_FEATURES):
    missing_feats = [c for c in EXPECTED_FEATURES if c not in cols]
    raise ValueError(f"CRITICAL: Expected 501 features, found {actual_feature_count}. Missing: {missing_feats[:10]}")

# Validate feature ordering
feature_slice = cols[len(REQUIRED_METADATA): len(REQUIRED_METADATA) + len(EXPECTED_FEATURES)]
feature_order_correct = (feature_slice == EXPECTED_FEATURES)
if not feature_order_correct:
    raise ValueError("CRITICAL: Feature columns are not in strict consecutive order x1..x501!")

if REQUIRED_TARGET not in cols:
    raise ValueError(f"CRITICAL: Target column '{REQUIRED_TARGET}' not found in CSV!")

missing_baselines = [c for c in BASELINE_COLS if c not in cols]
if missing_baselines:
    raise ValueError(f"CRITICAL: Missing comparison baseline columns: {missing_baselines}")

if n_cols != EXPECTED_TOTAL_COLUMNS:
    raise ValueError(f"CRITICAL: Expected {EXPECTED_TOTAL_COLUMNS} columns, but found {n_cols}")

print("Schema Validation: PASS (Metadata, 501 Features, Target, Baselines)")

# 3. Missing values & duplicate rows
total_missing = int(df.isna().sum().sum())
duplicate_rows = int(df.duplicated().sum())
print(f"Missing Values Across Entire Dataset: {total_missing}")
print(f"Duplicate Rows Across Entire Dataset: {duplicate_rows}")

if total_missing != 0:
    raise ValueError(f"CRITICAL: Dataset contains {total_missing} missing cells!")
if duplicate_rows != 0:
    raise ValueError(f"CRITICAL: Dataset contains {duplicate_rows} duplicate rows!")

# 4. Strict Group Key Validation: Series + Image + Gridline
REQUIRED_GROUP_COLS = ["Series", "Image", "Gridline"]
for gc in REQUIRED_GROUP_COLS:
    if gc not in df.columns:
        raise ValueError(f"CRITICAL: Group column '{gc}' not present in dataframe!")

group_id = df["Series"].astype(str) + "||" + df["Image"].astype(str) + "||" + df["Gridline"].astype(str)
n_unique_groups = int(group_id.nunique())
print(f"Unique Physical Groups (Series + Image + Gridline): {n_unique_groups}")

# Group observations count validation: every group MUST have exactly 6 rows
group_sizes = df.groupby(group_id).size()
min_group_size = int(group_sizes.min())
max_group_size = int(group_sizes.max())
all_groups_have_6_obs = (min_group_size == 6 and max_group_size == 6)

if not all_groups_have_6_obs:
    bad_groups = group_sizes[group_sizes != 6]
    raise ValueError(f"CRITICAL: Found groups with size != 6:\n{bad_groups.head()}")

print(f"Group Size Validation: PASS (Every group has strictly 6 rows; min={min_group_size}, max={max_group_size})")

# Stage completeness validation: each group MUST contain Stage 1, 2, 3, 4, 5, 6 exactly once
expected_stages = (1, 2, 3, 4, 5, 6)
stages_by_group = df.groupby(group_id)["Stage"].apply(lambda s: tuple(sorted(s)))
stage_match_mask = (stages_by_group == expected_stages)
all_stages_complete = bool(stage_match_mask.all())

if not all_stages_complete:
    bad_stage_groups = stages_by_group[~stage_match_mask]
    raise ValueError(f"CRITICAL: Found groups without strict Stage (1,2,3,4,5,6):\n{bad_stage_groups.head()}")

print("Stage Completeness Validation: PASS (Every group has Stages 1..6 exactly once)")

# 5. Numerical features and target audit
x_data = df[EXPECTED_FEATURES]
x_min = float(x_data.min().min())
x_max = float(x_data.max().max())

target_series = pd.to_numeric(df[REQUIRED_TARGET], errors="coerce")
target_min = float(target_series.min())
target_max = float(target_series.max())
target_mean = float(target_series.mean())
target_median = float(target_series.median())
target_std = float(target_series.std())

meta_summary = {}
for col in REQUIRED_METADATA:
    val_counts = df[col].value_counts(dropna=False).head(10).to_dict()
    meta_summary[col] = {
        "unique_count": int(df[col].nunique(dropna=False)),
        "null_count": int(df[col].isna().sum()),
        "top_values": {str(k): int(v) for k, v in val_counts.items()}
    }

baseline_summary = {}
for col in BASELINE_COLS:
    b_series = pd.to_numeric(df[col], errors="coerce")
    baseline_summary[col] = {
        "count": int(b_series.notna().sum()),
        "min": float(b_series.min()),
        "max": float(b_series.max()),
        "mean": float(b_series.mean()),
        "std": float(b_series.std()),
    }

# Save structured audit results
comprehensive_audit = {
    "dataset_path": str(CSV_PATH.relative_to(ROOT)),
    "n_rows": n_rows,
    "n_cols": n_cols,
    "expected_cols": EXPECTED_TOTAL_COLUMNS,
    "total_missing_cells": total_missing,
    "duplicate_rows": duplicate_rows,
    "schema": {
        "required_metadata": REQUIRED_METADATA,
        "metadata_found": True,
        "actual_feature_count": actual_feature_count,
        "expected_feature_count": len(EXPECTED_FEATURES),
        "features_in_order": feature_order_correct,
        "target_column": REQUIRED_TARGET,
        "baseline_columns": BASELINE_COLS,
    },
    "group_validation": {
        "group_key": REQUIRED_GROUP_COLS,
        "n_unique_groups": n_unique_groups,
        "min_group_size": min_group_size,
        "max_group_size": max_group_size,
        "all_groups_have_6_observations": all_groups_have_6_obs,
        "all_groups_have_stages_1_to_6": all_stages_complete,
        "expected_rows_check": n_unique_groups * 6 == n_rows
    },
    "target_stats": {
        "name": REQUIRED_TARGET,
        "count": len(target_series),
        "min": target_min,
        "max": target_max,
        "mean": target_mean,
        "median": target_median,
        "std": target_std,
    },
    "baseline_stats": baseline_summary,
    "features_stats": {
        "min_intensity": x_min,
        "max_intensity": x_max,
        "missing_values": int(x_data.isna().sum().sum()),
    },
    "metadata_summary": meta_summary,
}

audit_json_path = TABLES_DIR / "comprehensive_audit.json"
with open(audit_json_path, "w", encoding="utf-8") as f:
    json.dump(comprehensive_audit, f, indent=2)

print(f"Saved audit JSON to: {audit_json_path.relative_to(ROOT)}")

# 6. Extract Paper Citations / Definitions
paper_2024 = ROOT / "papers" / "2024 Deep learning metasensor for crack-width assessment and self-healing evaluation in concrete.pdf"
paper_2025 = ROOT / "papers" / "2025 Dataset for developing deep learning models to assess crack width and self-healing progress in concrete.pdf"

def extract_snippets(pdf_path, keywords):
    if not pdf_path.exists():
        return [f"File not found: {pdf_path.name}"]
    reader = PdfReader(str(pdf_path))
    snippets = []
    for page_idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        for line in text.split("\n"):
            line_clean = line.strip()
            if any(re.search(rf"\b{kw}\b", line_clean, re.IGNORECASE) for kw in keywords):
                if len(line_clean) > 20:
                    snippets.append(f"[Page {page_idx+1}] {line_clean}")
    return snippets[:12]

paper_notes = {
    "paper_2025_snippets": extract_snippets(paper_2025, ["Gridline", "Series", "Stage", "brightness profile", "6400", "MANwidth"]),
    "paper_2024_snippets": extract_snippets(paper_2024, ["metasensor", "DLMwidth", "AEDwidth", "6400", "pi2mi"])
}

snippets_path = TABLES_DIR / "paper_snippets.json"
with open(snippets_path, "w", encoding="utf-8") as f:
    json.dump(paper_notes, f, indent=2)
print(f"Saved paper snippets to: {snippets_path.relative_to(ROOT)}")

# 7. Write Markdown Audit Report
report_md = f"""# krkCMd Dataset Audit & Verification Report

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
| Total Rows | {n_rows:,} |
| Total Columns | {n_cols} |
| Missing Cells | {total_missing} |
| Duplicate Rows | {duplicate_rows} |
| Metadata Columns | `No`, `Profile`, `Series`, `Image`, `Gridline`, `Stage` (6 columns) |
| Feature Columns | `x1` through `x501` ({actual_feature_count} features, strictly ordered) |
| Target Column | `MANwidth` (Manual crack width in micrometers, $\\mu\\text{{m}}$) |
| Baseline Columns | `DLMwidth`, `AEDwidth` |

---

## 3. Strict Group & Stage Validation

- **Group Key:** `Series + Image + Gridline`
- **Total Unique Groups:** {n_unique_groups:,}
- **Observations per Group:** Strictly **6 observations** for all {n_unique_groups:,} groups (min=6, max=6).
- **Stage Distribution per Group:** Every single group contains **Stage 1, 2, 3, 4, 5, 6 exactly once** (`tuple(sorted(stages)) == (1, 2, 3, 4, 5, 6)` for 100% of groups).
- **Leakage Prevention Verification:**
  3,183 groups * 6 stages = 19,098 rows.
  Splitting by rows would leak the same crack across different stages into train and test sets. Group-aware splitting (`GroupShuffleSplit` on `Series + Image + Gridline`) is strictly mandatory.

---

## 4. Target & Feature Summary

- **Feature Intensities (`x1`..`x501`):** Range [{x_min:.1f}, {x_max:.1f}], 0 missing values.
- **`MANwidth` Target ($\\mu\\text{{m}}$):**
  - Min: {target_min:.2f} $\\mu\\text{{m}}$
  - Max: {target_max:.2f} $\\mu\\text{{m}}$
  - Mean: {target_mean:.2f} $\\mu\\text{{m}}$
  - Median: {target_median:.2f} $\\mu\\text{{m}}$
  - Std: {target_std:.2f} $\\mu\\text{{m}}$
- **Baseline Comparisons:**
  - `DLMwidth`: mean {baseline_summary['DLMwidth']['mean']:.2f} $\\mu\\text{{m}}$ (range [{baseline_summary['DLMwidth']['min']:.2f}, {baseline_summary['DLMwidth']['max']:.2f}])
  - `AEDwidth`: mean {baseline_summary['AEDwidth']['mean']:.2f} $\\mu\\text{{m}}$ (range [{baseline_summary['AEDwidth']['min']:.2f}, {baseline_summary['AEDwidth']['max']:.2f}])

---

## 5. Decision & Next Step

The schema is now aligned and verified. **No model training has been conducted.** All code and configurations reference `Gridline`. The project is prepared for Ide 1 benchmark modeling once approved.
"""

report_md_path = REPORTS_DIR / "DATASET_AUDIT_REPORT.md"
with open(report_md_path, "w", encoding="utf-8") as f:
    f.write(report_md)

print(f"Saved Markdown report to: {report_md_path.relative_to(ROOT)}")
print("=" * 60)
print("ALL AUDIT AND GROUP VALIDATION CHECKS PASSED.")
print("=" * 60)
