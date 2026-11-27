"""
src/evaluation/m04b_bootstrap.py

Exploratory paired Series + Image cluster bootstrap for M04B (D-010C).
All intervals are conditional on saved Protocol A validation predictions.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd


def _lins_ccc(y_true: np.ndarray, y_pred: np.ndarray) -> Optional[float]:
    if y_true.size < 2:
        return None
    vt = float(np.var(y_true, ddof=0))
    vp = float(np.var(y_pred, ddof=0))
    if vt == 0.0 and vp == 0.0:
        return None
    if vt == 0.0 or vp == 0.0:
        return None
    mt = float(np.mean(y_true))
    mp = float(np.mean(y_pred))
    cov = float(np.mean((y_true - mt) * (y_pred - mp)))
    denom = vt + vp + (mt - mp) ** 2
    return float((2.0 * cov) / denom) if denom > 0 else None


def audit_clusters(ref_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for ig, g in ref_df.groupby("image_group", sort=True):
        rows.append({
            "image_group": str(ig),
            "Series": str(g["Series"].iloc[0]),
            "Image": str(g["Image"].iloc[0]),
            "n_obs": int(len(g)),
            "n_gridline_groups": int(g["group_id"].nunique()),
            "n_stages": int(g["Stage"].nunique()),
            "zero_width_obs": int((g["y_true_um"] == 0.0).sum()),
            "mean_manwidth_um": float(g["y_true_um"].mean()),
        })
    return pd.DataFrame(rows).sort_values("image_group").reset_index(drop=True)


def generate_cluster_draws(n_clusters: int, n_boot: int = 10000, seed: int = 42) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.integers(0, n_clusters, size=(n_boot, n_clusters), dtype=np.int32)


def run_paired_cluster_bootstrap(
    model_preds: Dict[str, np.ndarray],
    y_true: np.ndarray,
    cluster_labels: np.ndarray,
    comparators: Sequence[str] = ("ML01", "DLMwidth", "AEDwidth"),
    n_boot: int = 10000,
    seed: int = 42,
    ci_level: float = 0.95,
) -> Tuple[pd.DataFrame, pd.DataFrame, np.ndarray, List[str]]:
    """
    Execute paired cluster bootstrap using a single common draw sequence across all models.
    Pooled observation-weighted MAE = sum(sampled_abs_err) / sum(sampled_n).
    """
    unique_clusters = sorted(np.unique(cluster_labels).tolist())
    n_clusters = len(unique_clusters)
    draws = generate_cluster_draws(n_clusters, n_boot=n_boot, seed=seed)

    cluster_idx_list = [np.where(cluster_labels == c)[0] for c in unique_clusters]
    cluster_n = np.array([len(ix) for ix in cluster_idx_list], dtype=np.float64)

    # Precompute cluster-level sums for fast exact pooled MAE and RMSE
    models = list(model_preds.keys())
    cluster_abs_err = {}
    cluster_sq_err = {}
    for m in models:
        err = model_preds[m] - y_true
        ae = np.abs(err)
        se = err ** 2
        cluster_abs_err[m] = np.array([float(ae[ix].sum()) for ix in cluster_idx_list], dtype=np.float64)
        cluster_sq_err[m] = np.array([float(se[ix].sum()) for ix in cluster_idx_list], dtype=np.float64)

    # Precompute row-level cluster blocks for CCC (exact replicate evaluation)
    sampled_n_per_boot = cluster_n[draws].sum(axis=1)  # shape (n_boot,)

    alpha_low = (1.0 - ci_level) / 2.0 * 100.0
    alpha_high = (1.0 + ci_level) / 2.0 * 100.0

    boot_mae_cache: Dict[str, np.ndarray] = {}
    model_rows = []

    for m in models:
        yp = model_preds[m]
        point_mae = float(np.mean(np.abs(yp - y_true)))
        point_rmse = float(np.sqrt(np.mean((yp - y_true) ** 2)))
        point_ccc = _lins_ccc(y_true, yp)

        b_mae = cluster_abs_err[m][draws].sum(axis=1) / sampled_n_per_boot
        b_rmse = np.sqrt(cluster_sq_err[m][draws].sum(axis=1) / sampled_n_per_boot)
        boot_mae_cache[m] = b_mae

        # Cluster-sufficient statistics for exact pooled Lin's CCC across n_boot
        c_sum_t = np.array([float(y_true[ix].sum()) for ix in cluster_idx_list], dtype=np.float64)
        c_sum_p = np.array([float(yp[ix].sum()) for ix in cluster_idx_list], dtype=np.float64)
        c_sum_t2 = np.array([float((y_true[ix] ** 2).sum()) for ix in cluster_idx_list], dtype=np.float64)
        c_sum_p2 = np.array([float((yp[ix] ** 2).sum()) for ix in cluster_idx_list], dtype=np.float64)
        c_sum_tp = np.array([float((y_true[ix] * yp[ix]).sum()) for ix in cluster_idx_list], dtype=np.float64)

        st = c_sum_t[draws].sum(axis=1) / sampled_n_per_boot
        sp = c_sum_p[draws].sum(axis=1) / sampled_n_per_boot
        st2 = c_sum_t2[draws].sum(axis=1) / sampled_n_per_boot
        sp2 = c_sum_p2[draws].sum(axis=1) / sampled_n_per_boot
        stp = c_sum_tp[draws].sum(axis=1) / sampled_n_per_boot

        vt = np.maximum(0.0, st2 - st ** 2)
        vp = np.maximum(0.0, sp2 - sp ** 2)
        cov = stp - st * sp
        denom = vt + vp + (st - sp) ** 2
        valid_ccc = (vt > 0.0) & (vp > 0.0) & (denom > 0.0)
        b_ccc = np.where(valid_ccc, (2.0 * cov) / np.where(valid_ccc, denom, 1.0), np.nan)
        ccc_valid_vals = b_ccc[np.isfinite(b_ccc)]

        model_rows.append({
            "model_id": m,
            "n_obs": int(len(y_true)),
            "n_clusters": int(n_clusters),
            "n_boot": int(n_boot),
            "mae_point_um": point_mae,
            "mae_ci_low_um": float(np.percentile(b_mae, alpha_low)),
            "mae_ci_high_um": float(np.percentile(b_mae, alpha_high)),
            "rmse_point_um": point_rmse,
            "rmse_ci_low_um": float(np.percentile(b_rmse, alpha_low)),
            "rmse_ci_high_um": float(np.percentile(b_rmse, alpha_high)),
            "ccc_point": point_ccc,
            "ccc_ci_low": float(np.percentile(ccc_valid_vals, alpha_low)) if ccc_valid_vals.size > 0 else None,
            "ccc_ci_high": float(np.percentile(ccc_valid_vals, alpha_high)) if ccc_valid_vals.size > 0 else None,
            "ccc_valid_replicates": int(ccc_valid_vals.size),
        })

    paired_rows = []
    for comp in comparators:
        if comp not in boot_mae_cache:
            continue
        comp_point = float(np.mean(np.abs(model_preds[comp] - y_true)))
        for m in models:
            if m == comp:
                continue
            cand_point = float(np.mean(np.abs(model_preds[m] - y_true)))
            delta_b = boot_mae_cache[m] - boot_mae_cache[comp]
            paired_rows.append({
                "candidate_id": m,
                "comparator_id": comp,
                "delta_mae_point_um": cand_point - comp_point,
                "delta_mae_boot_median_um": float(np.median(delta_b)),
                "delta_mae_ci_low_um": float(np.percentile(delta_b, alpha_low)),
                "delta_mae_ci_high_um": float(np.percentile(delta_b, alpha_high)),
                "valid_replicates": int(len(delta_b)),
                "n_obs": int(len(y_true)),
                "n_clusters": int(n_clusters),
                "interpretation_note": "Exploratory conditional on saved Protocol A validation predictions; negative favors candidate.",
            })

    return pd.DataFrame(model_rows), pd.DataFrame(paired_rows), draws, unique_clusters
