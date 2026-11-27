"""
src/evaluation/metrics.py

Comprehensive reusable scientific evaluation metrics for krkCMd M03+ (Section 8):
  - Predictive accuracy (MAE, RMSE, MSE, MedianAE, R2, Bias, P90/P95/Max AE, WAPE)
  - Measurement agreement (Bland-Altman LoA, Lin's CCC, Pearson, Spearman, calibration)
  - Engineering analytical tolerances (+-5, +-10, +-20, +-50 um, exceedance, severe underestimation)
  - Robustness aggregation (abs/rel degradation, mean/worst corrupted MAE, AUSEC, consistency, tolerance retention)
"""

from __future__ import annotations

from typing import Dict, Iterable, Mapping, Optional, Sequence
import numpy as np
from scipy import stats


def _validate_pair(y_true: np.ndarray, y_pred: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    yt = np.asarray(y_true, dtype=np.float64)
    yp = np.asarray(y_pred, dtype=np.float64)
    if yt.ndim != 1 or yp.ndim != 1 or yt.shape != yp.shape:
        raise ValueError(f"Expected matching 1D arrays, got y_true={yt.shape}, y_pred={yp.shape}")
    if yt.size == 0:
        raise ValueError("Empty target/prediction arrays are not allowed.")
    if not (np.isfinite(yt).all() and np.isfinite(yp).all()):
        raise ValueError("Non-finite values in y_true or y_pred.")
    return yt, yp


def compute_predictive_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Optional[float]]:
    yt, yp = _validate_pair(y_true, y_pred)
    err = yp - yt
    abs_err = np.abs(err)
    mse = float(np.mean(err ** 2))
    rmse = float(np.sqrt(mse))
    mae = float(np.mean(abs_err))
    medae = float(np.median(abs_err))
    ss_res = float(np.sum(err ** 2))
    ss_tot = float(np.sum((yt - np.mean(yt)) ** 2))
    r2 = float(1.0 - ss_res / ss_tot) if ss_tot > 0 else None
    denom_wape = float(np.sum(np.abs(yt)))
    wape = float(np.sum(abs_err) / denom_wape) if denom_wape > 0 else None
    return {
        "mae_um": mae,
        "rmse_um": rmse,
        "mse_um2": mse,
        "median_ae_um": medae,
        "r2": r2,
        "bias_um": float(np.mean(err)),
        "p90_ae_um": float(np.percentile(abs_err, 90)),
        "p95_ae_um": float(np.percentile(abs_err, 95)),
        "max_ae_um": float(np.max(abs_err)),
        "wape": wape,
    }


def compute_measurement_agreement(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Optional[float]]:
    yt, yp = _validate_pair(y_true, y_pred)
    diff = yp - yt
    mean_diff = float(np.mean(diff))
    sd_diff = float(np.std(diff, ddof=1)) if diff.size > 1 else 0.0
    loa_lower = mean_diff - 1.96 * sd_diff
    loa_upper = mean_diff + 1.96 * sd_diff

    var_t = float(np.var(yt, ddof=0))
    var_p = float(np.var(yp, ddof=0))
    cov_tp = float(np.mean((yt - np.mean(yt)) * (yp - np.mean(yp))))
    ccc_denom = var_t + var_p + (float(np.mean(yt) - np.mean(yp)) ** 2)
    ccc = float((2.0 * cov_tp) / ccc_denom) if ccc_denom > 0 else None

    if np.std(yt) > 0 and np.std(yp) > 0:
        pearson_r = float(stats.pearsonr(yt, yp).statistic)
        spearman_rho = float(stats.spearmanr(yt, yp).statistic)
        cal_slope, cal_intercept = np.polyfit(yp, yt, 1)
        cal_slope = float(cal_slope)
        cal_intercept = float(cal_intercept)
    else:
        pearson_r = None
        spearman_rho = None
        cal_slope = None
        cal_intercept = None

    return {
        "bland_altman_mean_diff_um": mean_diff,
        "bland_altman_sd_diff_um": sd_diff,
        "bland_altman_loa_lower_um": float(loa_lower),
        "bland_altman_loa_upper_um": float(loa_upper),
        "lins_ccc": ccc,
        "pearson_r": pearson_r,
        "spearman_rho": spearman_rho,
        "calibration_slope": cal_slope,
        "calibration_intercept_um": cal_intercept,
    }


def compute_engineering_tolerances(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    tolerances_um: Sequence[float] = (5.0, 10.0, 20.0, 50.0),
) -> Dict[str, float]:
    yt, yp = _validate_pair(y_true, y_pred)
    diff = yp - yt
    abs_err = np.abs(diff)
    out: Dict[str, float] = {}
    for tol in tolerances_um:
        t_int = int(tol) if float(tol).is_integer() else tol
        out[f"within_{t_int}um_rate"] = float(np.mean(abs_err <= tol))
        out[f"exceedance_{t_int}um_rate"] = float(np.mean(abs_err > tol))
        out[f"severe_underest_{t_int}um_rate"] = float(np.mean(diff < -tol))
    return out


def compute_robustness_summary(
    y_true: np.ndarray,
    clean_pred: np.ndarray,
    corrupted_preds: Mapping[str, np.ndarray],
    severities: Optional[Sequence[float]] = None,
    tolerance_um: float = 20.0,
) -> Dict[str, Optional[float]]:
    yt, cp = _validate_pair(y_true, clean_pred)
    clean_mae = float(np.mean(np.abs(cp - yt)))
    clean_tol = float(np.mean(np.abs(cp - yt) <= tolerance_um))

    maes = []
    consistencies = []
    tol_retentions = []
    for name, pred in corrupted_preds.items():
        _, yp = _validate_pair(yt, pred)
        c_mae = float(np.mean(np.abs(yp - yt)))
        maes.append(c_mae)
        consistencies.append(float(np.mean(np.abs(yp - cp))))
        if clean_tol > 0:
            tol_retentions.append(float(np.mean(np.abs(yp - yt) <= tolerance_um)) / clean_tol)

    if not corrupted_preds:
        return {
            "n_conditions": 0,
            "clean_mae_um": clean_mae,
            "mean_corrupted_mae_um": None,
            "worst_condition_mae_um": None,
            "abs_degradation_um": None,
            "rel_degradation": None,
            "prediction_consistency_mad_um": None,
            "mean_tolerance_retention": None,
            "area_under_severity_error_curve": None,
        }

    mean_corr_mae = float(np.mean(maes))
    worst_corr_mae = float(np.max(maes))
    abs_deg = mean_corr_mae - clean_mae
    rel_deg = (abs_deg / clean_mae) if clean_mae > 0 else None

    ausec = None
    if severities is not None and len(severities) == len(maes) and len(maes) >= 2:
        order = np.argsort(severities)
        ausec = float(np.trapezoid(np.asarray(maes)[order], np.asarray(severities)[order]))

    return {
        "n_conditions": len(maes),
        "clean_mae_um": clean_mae,
        "mean_corrupted_mae_um": mean_corr_mae,
        "worst_condition_mae_um": worst_corr_mae,
        "abs_degradation_um": abs_deg,
        "rel_degradation": rel_deg,
        "prediction_consistency_mad_um": float(np.mean(consistencies)),
        "mean_tolerance_retention": float(np.mean(tol_retentions)) if tol_retentions else None,
        "area_under_severity_error_curve": ausec,
    }
