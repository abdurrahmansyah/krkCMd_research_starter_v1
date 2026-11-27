"""
src/evaluation/m04a_data.py

Strict Protocol A (train + validation only) data loader and leakage guard for M04A.
Never returns or exposes the sealed historical test partition (3,822 rows).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd


META_COLS = ["No", "Profile", "Series", "Image", "Gridline", "Stage"]
FEATURE_COLS = [f"x{i}" for i in range(1, 502)]
TARGET_COL = "MANwidth"
EXPECTED_TRAIN_ROWS = 12216
EXPECTED_TRAIN_GROUPS = 2036
EXPECTED_VAL_ROWS = 3060
EXPECTED_VAL_GROUPS = 510


@dataclass(frozen=True)
class ProtocolAData:
    X_train: np.ndarray
    y_train: np.ndarray
    train_meta: pd.DataFrame
    train_inner_mask: np.ndarray  # True = inner train (~80% groups), False = inner val (~20% groups)
    X_val: np.ndarray
    y_val: np.ndarray
    val_meta: pd.DataFrame
    audit: Dict[str, object]


def load_protocol_a_train_val(
    raw_csv_path: Path,
    split_manifest_path: Path,
    authorized_phase: str = "M04A_PROTOCOL_A_TRAIN_VAL",
    inner_val_frac: float = 0.20,
    seed: int = 42,
) -> ProtocolAData:
    if authorized_phase != "M04A_PROTOCOL_A_TRAIN_VAL":
        raise PermissionError(
            f"Unauthorized phase '{authorized_phase}'. Only M04A_PROTOCOL_A_TRAIN_VAL is permitted."
        )

    df = pd.read_csv(raw_csv_path)
    if df.shape != (19098, 510):
        raise ValueError(f"Unexpected raw CSV shape {df.shape}; expected (19098, 510).")

    missing_feats = [c for c in FEATURE_COLS if c not in df.columns]
    if missing_feats or TARGET_COL not in df.columns:
        raise ValueError(f"Missing required columns: {missing_feats[:5]} / {TARGET_COL}")

    manifest = pd.read_csv(split_manifest_path)
    if len(manifest) != len(df) or manifest["source_row_id"].nunique() != len(df):
        raise ValueError("Split manifest does not match 19,098 unique source_row_id rows.")

    merged = df.copy()
    merged["source_row_id"] = np.arange(len(merged), dtype=np.int64)
    merged = merged.merge(manifest[["source_row_id", "group_id", "split"]], on="source_row_id", how="inner")
    merged["image_group"] = merged["Series"].astype(str) + "|" + merged["Image"].astype(str)

    # Strict exclusion of sealed test partition
    test_mask = merged["split"] == "test"
    n_test_excluded = int(test_mask.sum())
    if n_test_excluded != 3822:
        raise ValueError(f"Expected 3,822 test rows to exclude, found {n_test_excluded}.")

    train_df = merged.loc[merged["split"] == "train"].sort_values("source_row_id").reset_index(drop=True)
    val_df = merged.loc[merged["split"] == "validation"].sort_values("source_row_id").reset_index(drop=True)

    if len(train_df) != EXPECTED_TRAIN_ROWS or train_df["group_id"].nunique() != EXPECTED_TRAIN_GROUPS:
        raise ValueError(f"Train partition mismatch: {len(train_df)} rows, {train_df['group_id'].nunique()} groups.")
    if len(val_df) != EXPECTED_VAL_ROWS or val_df["group_id"].nunique() != EXPECTED_VAL_GROUPS:
        raise ValueError(f"Validation partition mismatch: {len(val_df)} rows, {val_df['group_id'].nunique()} groups.")

    overlap = set(train_df["group_id"]) & set(val_df["group_id"])
    if overlap:
        raise ValueError(f"Group leakage detected between train and validation: {len(overlap)} shared groups.")

    # Deterministic group-aware inner train/val split inside Protocol A train
    unique_groups = np.sort(train_df["group_id"].unique())
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(unique_groups))
    n_inner_val_groups = max(1, int(round(len(unique_groups) * inner_val_frac)))
    inner_val_groups = set(unique_groups[perm[:n_inner_val_groups]])
    train_inner_mask = ~train_df["group_id"].isin(inner_val_groups).to_numpy()

    meta_cols_keep = ["source_row_id", "Series", "Image", "Gridline", "Stage", "group_id", "image_group", "split"]

    X_train = train_df[FEATURE_COLS].to_numpy(dtype=np.float32)
    y_train = train_df[TARGET_COL].to_numpy(dtype=np.float64)
    X_val = val_df[FEATURE_COLS].to_numpy(dtype=np.float32)
    y_val = val_df[TARGET_COL].to_numpy(dtype=np.float64)

    audit = {
        "authorized_phase": authorized_phase,
        "feature_count": len(FEATURE_COLS),
        "target_col": TARGET_COL,
        "train_rows": int(len(train_df)),
        "train_groups": int(train_df["group_id"].nunique()),
        "inner_train_rows": int(train_inner_mask.sum()),
        "inner_val_rows": int((~train_inner_mask).sum()),
        "inner_val_groups": int(n_inner_val_groups),
        "validation_rows": int(len(val_df)),
        "validation_groups": int(val_df["group_id"].nunique()),
        "test_rows_excluded": n_test_excluded,
        "test_rows_exposed_to_worker": 0,
    }

    return ProtocolAData(
        X_train=X_train,
        y_train=y_train,
        train_meta=train_df[meta_cols_keep].copy(),
        train_inner_mask=train_inner_mask,
        X_val=X_val,
        y_val=y_val,
        val_meta=val_df[meta_cols_keep].copy(),
        audit=audit,
    )
