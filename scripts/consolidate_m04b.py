"""
scripts/consolidate_m04b.py

Strengthened M04B consolidation, 16-point attempt validation, independent metric
recomputation, subgroup/zero-width/tail-error/fairness audits, and exploratory
paired image-cluster bootstrap (D-010C, D-010E).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from evaluation.m04b_bootstrap import audit_clusters, run_paired_cluster_bootstrap  # noqa: E402
from evaluation.metrics import (  # noqa: E402
    compute_engineering_tolerances,
    compute_measurement_agreement,
    compute_predictive_accuracy,
)


MODEL_FAMILY_MAP = {
    "ML01": "classical_boosting", "ML02": "classical_boosting", "ML03": "classical_boosting",
    "ML04": "classical_boosting", "ML05": "classical_boosting", "ML06": "classical_boosting", "ML07": "classical_boosting",
    "DL01": "tabular_deep_learning", "DL02": "tabular_deep_learning", "DL03": "tabular_deep_learning",
    "DL04": "tabular_deep_learning", "DL05": "tabular_deep_learning",
    "FM01": "tabular_foundation_models", "FM02": "tabular_foundation_models",
    "FM03": "tabular_foundation_models", "FM04": "tabular_foundation_models",
    "SG01": "spatial_signal_regression", "SG02": "spatial_signal_regression", "SG03": "spatial_signal_regression",
    "SG04": "spatial_signal_regression", "SG05": "spatial_signal_regression", "SG06": "spatial_signal_regression",
    "HY01": "custom_hybrid_approaches", "HY02": "custom_hybrid_approaches", "HY03": "custom_hybrid_approaches",
    "HY04": "custom_hybrid_approaches", "HY05": "custom_hybrid_approaches",
    "RF01": "reference_benchmarks", "RF02": "reference_benchmarks", "RF03": "reference_benchmarks",
    "RF04": "reference_benchmarks", "RF05": "reference_benchmarks",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def validate_attempt_dir(
    att_dir: Path,
    expected_model_id: str,
    expected_val_ids: List[int],
    expected_y: np.ndarray,
    expected_config_id: str = "scientific_v1",
) -> Tuple[bool, str, Optional[Dict[str, Any]], Optional[Dict[str, Any]], Optional[pd.DataFrame]]:
    """
    Strengthened 16-point validation contract for a scientific attempt directory.
    Returns (is_valid, reason, worker_json, runner_json, pred_df).
    """
    wp = att_dir / "worker_result.json"
    rp = att_dir / "runner_result.json"
    sp = att_dir / "experiment_spec.json"
    pp = att_dir / "predictions.csv"

    if not rp.exists():
        return False, "Missing runner_result.json", None, None, None
    rr = json.loads(rp.read_text(encoding="utf-8"))
    if rr.get("returncode") != 0:
        return False, f"Nonzero runner exit code: {rr.get('returncode')}", None, rr, None
    if rr.get("timed_out", False):
        return False, "Runner timed_out=True", None, rr, None
    if rr.get("violation_reason") is not None:
        return False, f"Resource violation: {rr.get('violation_reason')}", None, rr, None
    if rr.get("suspend_detected", False):
        return False, "Suspend detected during execution", None, rr, None
    if not wp.exists():
        return False, "Missing worker_result.json", None, rr, None

    wr = json.loads(wp.read_text(encoding="utf-8"))
    if wr.get("status") != "PASS":
        return False, f"Worker status != PASS: {wr.get('status')}", wr, rr, None
    if wr.get("model_id") != expected_model_id:
        return False, f"Model ID mismatch: {wr.get('model_id')} != {expected_model_id}", wr, rr, None
    if Path(wr.get("attempt_id", "")).name != att_dir.name:
        return False, f"Attempt ID mismatch: {wr.get('attempt_id')} != {att_dir.name}", wr, rr, None
    if wr.get("config_id") != expected_config_id:
        return False, f"Config ID mismatch: {wr.get('config_id')} != {expected_config_id}", wr, rr, None
    if sp.exists():
        spec = json.loads(sp.read_text(encoding="utf-8"))
        if spec.get("model_id") != expected_model_id or spec.get("config_id") != expected_config_id:
            return False, "ExperimentSpec identity mismatch", wr, rr, None
    if wr.get("data_audit", {}).get("test_rows_exposed_to_worker") != 0:
        return False, "Unauthorized test data exposure reported", wr, rr, None
    if not pp.exists():
        return False, "Missing predictions.csv", wr, rr, None

    p_df = pd.read_csv(pp)
    if len(p_df) != len(expected_val_ids):
        return False, f"Row count {len(p_df)} != {len(expected_val_ids)}", wr, rr, None
    if p_df["source_row_id"].nunique() != len(expected_val_ids):
        return False, "Duplicate source_row_id detected", wr, rr, None
    p_df = p_df.sort_values("source_row_id").reset_index(drop=True)
    if p_df["source_row_id"].tolist() != expected_val_ids:
        return False, "Validation membership mismatch", wr, rr, None
    if not np.isfinite(p_df["y_pred_raw_um"]).all():
        return False, "Non-finite raw predictions", wr, rr, None
    if not np.allclose(p_df["y_true_um"].to_numpy(dtype=np.float64), expected_y, atol=1e-12):
        return False, "Target values do not match MANwidth", wr, rr, None
    if not np.allclose(p_df["y_pred_nonnegative_um"], np.maximum(0.0, p_df["y_pred_raw_um"]), atol=1e-12):
        return False, "Clipped predictions inconsistent with max(0, y_pred_raw)", wr, rr, None

    return True, "VALID", wr, rr, p_df


def _full_metric_row(model_id: str, variant: str, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
    acc = compute_predictive_accuracy(y_true, y_pred)
    agr = compute_measurement_agreement(y_true, y_pred)
    tol = compute_engineering_tolerances(y_true, y_pred)
    row = {"model_id": model_id, "prediction_variant": variant, "n_obs": int(len(y_true))}
    row.update(acc)
    row.update(agr)
    row.update(tol)
    return row


def _subgroup_row(df: pd.DataFrame, stype: str, sval: str, mid: str) -> Dict[str, Any]:
    yt = df["y_true_um"].to_numpy(dtype=np.float64)
    yp = df["y_pred_raw_um"].to_numpy(dtype=np.float64)
    ypc = df["y_pred_nonnegative_um"].to_numpy(dtype=np.float64)
    acc = compute_predictive_accuracy(yt, yp)
    acc_c = compute_predictive_accuracy(yt, ypc)
    tol = compute_engineering_tolerances(yt, yp)
    return {
        "model_id": mid,
        "subgroup_type": stype,
        "subgroup_value": sval,
        "n_obs": int(len(df)),
        "n_gridline_groups": int(df["group_id"].nunique()),
        "n_image_groups": int(df["image_group"].nunique()),
        "manwidth_min_um": float(yt.min()),
        "manwidth_max_um": float(yt.max()),
        "raw_mae_um": acc["mae_um"],
        "raw_rmse_um": acc["rmse_um"],
        "raw_median_ae_um": acc["median_ae_um"],
        "raw_bias_um": acc["bias_um"],
        "raw_p95_ae_um": acc["p95_ae_um"],
        "within_20um_rate": tol["within_20um_rate"],
        "clipped_mae_um": acc_c["mae_um"],
        "sparse_flag": bool(len(df) < 100 or df["image_group"].nunique() < 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--m04a-dir", required=True)
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    m04a_dir = Path(args.m04a_dir)

    raw_csv = pd.read_csv(ROOT / "data" / "raw" / "krkCMd_table.csv")
    manifest = pd.read_csv(ROOT / "reports" / "tables" / "group_split_manifest.csv")
    raw_csv["source_row_id"] = np.arange(len(raw_csv), dtype=np.int64)
    val_gt = raw_csv.merge(manifest, on="source_row_id", how="inner")
    val_gt = val_gt.loc[val_gt["split"] == "validation"].sort_values("source_row_id").reset_index(drop=True)
    expected_val_ids = val_gt["source_row_id"].tolist()
    expected_y = val_gt["MANwidth"].to_numpy(dtype=np.float64)

    reg_df = pd.read_csv(ROOT / "reports" / "runs" / "M03_20261126_132016_DESKTOP-CQB09OU" / "M03_MODEL_ELIGIBILITY.csv")

    # Collect valid attempts: M04A canonical PASS + M04B recovery attempts
    status_rows = []
    pred_frames = []
    raw_metric_rows = []
    clip_metric_rows = []
    tol_rows = []
    neg_rows = []
    subgroup_rows = []
    zw_rows = []
    resource_rows = []
    fairness_rows = []
    artifact_rows = []
    recomp_checks = {}
    model_preds_for_boot: Dict[str, np.ndarray] = {}

    for _, reg in reg_df.iterrows():
        mid = str(reg["id"])
        # Search M04B recovery first if targeted in M04B, else M04A
        m04b_att = run_dir / "attempts" / f"M04B_{mid}_scientific_v1_s42_recovery1"
        m04a_atts = sorted((m04a_dir / "attempts").glob(f"M04A_{mid}_*"))

        chosen_valid = False
        chosen_run_id = ""
        chosen_att_dir: Optional[Path] = None
        chosen_wr = None
        chosen_rr = None
        chosen_pdf = None
        fail_reason = ""

        if m04b_att.exists():
            ok, reason, wr, rr, pdf = validate_attempt_dir(m04b_att, mid, expected_val_ids, expected_y)
            chosen_run_id = run_dir.name
            chosen_att_dir = m04b_att
            chosen_wr = wr
            chosen_rr = rr
            if ok:
                chosen_valid = True
                chosen_pdf = pdf
            else:
                fail_reason = reason
        elif m04a_atts:
            # Canonical rule: earliest valid attempt consistent with manifest (no MAE cherry-picking)
            for cand in m04a_atts:
                ok, reason, wr, rr, pdf = validate_attempt_dir(cand, mid, expected_val_ids, expected_y)
                if ok:
                    chosen_valid = True
                    chosen_run_id = m04a_dir.name
                    chosen_att_dir = cand
                    chosen_wr = wr
                    chosen_rr = rr
                    chosen_pdf = pdf
                    break
            if not chosen_valid:
                chosen_att_dir = m04a_atts[-1]
                chosen_run_id = m04a_dir.name
                _, fail_reason, chosen_wr, chosen_rr, _ = validate_attempt_dir(chosen_att_dir, mid, expected_val_ids, expected_y)
        else:
            fail_reason = f"Not targeted in M04A/M04B ({reg['m03_readiness_tier']})"

        if chosen_valid and chosen_pdf is not None and chosen_wr is not None:
            cfg_p = chosen_att_dir / "scientific_v1_config.json"
            cfg_sha = sha256_file(cfg_p) if cfg_p.exists() else ""

            cdf = chosen_pdf.copy()
            cdf.insert(0, "config_sha256", cfg_sha)
            cdf.insert(0, "model_family", MODEL_FAMILY_MAP[mid])
            cdf.insert(0, "source_attempt_id", chosen_att_dir.name)
            cdf.insert(0, "source_run_id", chosen_run_id)
            pred_frames.append(cdf)

            yt = cdf["y_true_um"].to_numpy(dtype=np.float64)
            yp_raw = cdf["y_pred_raw_um"].to_numpy(dtype=np.float64)
            yp_clip = cdf["y_pred_nonnegative_um"].to_numpy(dtype=np.float64)
            model_preds_for_boot[mid] = yp_raw

            rm = _full_metric_row(mid, "raw", yt, yp_raw)
            cm = _full_metric_row(mid, "nonnegative_clipped", yt, yp_clip)
            raw_metric_rows.append(rm)
            clip_metric_rows.append(cm)

            neg_mask = yp_raw < 0.0
            neg_rows.append({
                "model_id": mid,
                "n_negative_raw_predictions": int(neg_mask.sum()),
                "pct_negative_raw_predictions": float(neg_mask.mean() * 100.0),
                "mean_negative_magnitude_um": float(np.mean(np.abs(yp_raw[neg_mask]))) if neg_mask.any() else 0.0,
                "min_raw_prediction_um": float(np.min(yp_raw)),
                "raw_mae_um": rm["mae_um"],
                "clipped_mae_um": cm["mae_um"],
                "mae_change_after_clipping_um": cm["mae_um"] - rm["mae_um"],
                "raw_rmse_um": rm["rmse_um"],
                "clipped_rmse_um": cm["rmse_um"],
                "rmse_change_after_clipping_um": cm["rmse_um"] - rm["rmse_um"],
            })

            tr = {"model_id": mid, "prediction_variant": "raw"}
            tr.update(compute_engineering_tolerances(yt, yp_raw))
            tc = {"model_id": mid, "prediction_variant": "nonnegative_clipped"}
            tc.update(compute_engineering_tolerances(yt, yp_clip))
            tol_rows.extend([tr, tc])

            for sval, g in cdf.groupby("Series"):
                subgroup_rows.append(_subgroup_row(g, "Series", str(sval), mid))
            for stval, g in cdf.groupby("Stage"):
                subgroup_rows.append(_subgroup_row(g, "Stage", str(stval), mid))
            for igval, g in cdf.groupby("image_group"):
                subgroup_rows.append(_subgroup_row(g, "ImageGroup", str(igval), mid))
            subgroup_rows.append(_subgroup_row(cdf[cdf["y_true_um"] == 0.0], "WidthRegime", "zero_width_0", mid))
            subgroup_rows.append(_subgroup_row(cdf[cdf["y_true_um"] > 0.0], "WidthRegime", "positive_width_gt0", mid))
            subgroup_rows.append(_subgroup_row(cdf[(cdf["y_true_um"] > 0.0) & (cdf["y_true_um"] <= 100.0)], "WidthBin", "(0, 100]", mid))
            subgroup_rows.append(_subgroup_row(cdf[(cdf["y_true_um"] > 100.0) & (cdf["y_true_um"] <= 300.0)], "WidthBin", "(100, 300]", mid))
            subgroup_rows.append(_subgroup_row(cdf[cdf["y_true_um"] > 300.0], "WidthBin", ">300", mid))

            # Zero-width analysis
            zw_df = cdf[cdf["y_true_um"] == 0.0]
            zw_raw = zw_df["y_pred_raw_um"].to_numpy(dtype=np.float64)
            zw_clip = zw_df["y_pred_nonnegative_um"].to_numpy(dtype=np.float64)
            zw_tol = compute_engineering_tolerances(zw_df["y_true_um"].to_numpy(dtype=np.float64), zw_raw)
            zw_rows.append({
                "model_id": mid,
                "n_zero_width_val": int(len(zw_df)),
                "mean_pred_raw_um": float(np.mean(zw_raw)),
                "median_pred_raw_um": float(np.median(zw_raw)),
                "raw_mae_um": float(np.mean(np.abs(zw_raw))),
                "clipped_mae_um": float(np.mean(zw_clip)),
                "negative_raw_rate_pct": float(np.mean(zw_raw < 0.0) * 100.0),
                "within_5um_rate": zw_tol["within_5um_rate"],
                "within_10um_rate": zw_tol["within_10um_rate"],
                "within_20um_rate": zw_tol["within_20um_rate"],
            })

            resource_rows.append({
                "model_id": mid,
                "source_run_id": chosen_run_id,
                "source_attempt_id": chosen_att_dir.name,
                "status": "PASS",
                "environment": reg["environment"],
                "device": chosen_wr["device"],
                "init_sec": chosen_wr["init_sec"],
                "preprocess_fit_sec": chosen_wr["preprocess_fit_sec"],
                "load_sec": chosen_wr["load_sec"],
                "train_or_context_sec": chosen_wr["train_or_context_sec"],
                "predict_sec": chosen_wr["predict_sec"],
                "total_elapsed_sec": chosen_wr["total_elapsed_sec"],
                "subprocess_wall_sec": chosen_rr.get("elapsed_sec") if chosen_rr else None,
                "peak_rss_mb": chosen_rr.get("peak_rss_mb") if chosen_rr else None,
                "peak_cuda_alloc_mb": chosen_wr["peak_cuda_alloc_mb"],
                "peak_cuda_res_mb": chosen_wr["peak_cuda_res_mb"],
                "param_count": chosen_wr["param_count"],
                "actual_epochs": chosen_wr["actual_epochs"],
                "best_epoch": chosen_wr["best_epoch"],
                "artifact_size_bytes": chosen_wr["artifact_size_bytes"],
                "failure_reason": "",
            })

            uses_inner = mid in {"DL01", "DL02", "DL04", "DL05", "SG01", "RF05"}
            fairness_rows.append({
                "model_id": mid,
                "authorized_train_rows": 12216,
                "actual_optimization_rows": 9774 if uses_inner else 12216,
                "inner_val_rows": 2442 if uses_inner else 0,
                "uses_group_aware_inner_split": uses_inner,
                "final_refit_on_full_train": False,
                "preprocessing_train_only": True,
                "actual_epochs": chosen_wr["actual_epochs"],
                "notes": "Group-aware 80/20 inner split; best inner-val checkpoint" if uses_inner else (
                    "Full 12,216 train database context (zero-shot)" if mid in {"FM03", "FM04"} else "Full 12,216 train rows"
                ),
            })

            artifact_rows.append({
                "model_id": mid,
                "source_run_id": chosen_run_id,
                "artifact_path": chosen_wr["artifact_path"],
                "artifact_size_bytes": chosen_wr["artifact_size_bytes"],
                "artifact_sha256": chosen_wr["artifact_sha256"],
            })

            ind_mae = float(np.mean(np.abs(yp_raw - yt)))
            ind_rmse = float(np.sqrt(np.mean((yp_raw - yt) ** 2)))
            recomp_checks[mid] = {
                "source_run_id": chosen_run_id,
                "reported_mae_um": rm["mae_um"],
                "recomputed_mae_um": ind_mae,
                "mae_diff": abs(rm["mae_um"] - ind_mae),
                "reported_rmse_um": rm["rmse_um"],
                "recomputed_rmse_um": ind_rmse,
                "rmse_diff": abs(rm["rmse_um"] - ind_rmse),
            }

            m_status = "PASS"
        elif chosen_att_dir is not None:
            m_status = "FAILED"
            resource_rows.append({
                "model_id": mid,
                "source_run_id": chosen_run_id,
                "source_attempt_id": chosen_att_dir.name,
                "status": "FAILED",
                "environment": reg["environment"],
                "device": reg["device"],
                "subprocess_wall_sec": chosen_rr.get("elapsed_sec") if chosen_rr else None,
                "peak_rss_mb": chosen_rr.get("peak_rss_mb") if chosen_rr else None,
                "failure_reason": fail_reason,
            })
        else:
            m_status = str(reg["m03_readiness_tier"])

        status_rows.append({
            "model_id": mid,
            "name": reg["name"],
            "category": reg["category"],
            "environment": reg["environment"],
            "source_run_id": chosen_run_id,
            "chosen_attempt_id": chosen_att_dir.name if chosen_att_dir else "",
            "scientific_status": m_status,
            "failure_or_exclusion_reason": "" if chosen_valid else fail_reason,
        })

    # Rank raw & clipped metrics (D-010E)
    raw_df = pd.DataFrame(raw_metric_rows).sort_values(
        ["mae_um", "rmse_um", "lins_ccc"], ascending=[True, True, False]
    ).reset_index(drop=True)
    raw_df.insert(0, "rank_raw_mae", np.arange(1, len(raw_df) + 1))

    clip_df = pd.DataFrame(clip_metric_rows).sort_values(
        ["mae_um", "rmse_um", "lins_ccc"], ascending=[True, True, False]
    ).reset_index(drop=True)
    clip_df.insert(0, "rank_clipped_mae", np.arange(1, len(clip_df) + 1))

    # Historical references (separate dataset)
    ref_pred_frames = []
    ref_metric_rows = []
    for ref_col in ["DLMwidth", "AEDwidth"]:
        yp = val_gt[ref_col].to_numpy(dtype=np.float64)
        model_preds_for_boot[ref_col] = yp
        rdf = pd.DataFrame({
            "reference_id": ref_col,
            "provenance": "HISTORICAL_REFERENCE",
            "source_row_id": val_gt["source_row_id"],
            "Series": val_gt["Series"],
            "Image": val_gt["Image"],
            "Gridline": val_gt["Gridline"],
            "Stage": val_gt["Stage"],
            "group_id": val_gt["group_id"],
            "image_group": val_gt["Series"].astype(str) + "|" + val_gt["Image"].astype(str),
            "y_true_um": expected_y,
            "y_pred_um": yp,
            "signed_error_um": yp - expected_y,
            "absolute_error_um": np.abs(yp - expected_y),
        })
        ref_pred_frames.append(rdf)
        rr = _full_metric_row(ref_col, "HISTORICAL_REFERENCE", expected_y, yp)
        rr["provenance"] = "HISTORICAL_CSV_STORED_OUTPUT_POTENTIALLY_NON_INDEPENDENT"
        ref_metric_rows.append(rr)

    # Add absolute/relative differences vs ML01 and DLMwidth to raw_df
    ml01_mae = float(raw_df.loc[raw_df["model_id"] == "ML01", "mae_um"].iloc[0])
    dlm_mae = float(next(r["mae_um"] for r in ref_metric_rows if r["model_id"] == "DLMwidth"))
    raw_df["abs_mae_diff_vs_ML01_um"] = raw_df["mae_um"] - ml01_mae
    raw_df["rel_mae_diff_vs_ML01_pct"] = (raw_df["mae_um"] - ml01_mae) / ml01_mae * 100.0
    raw_df["abs_mae_diff_vs_DLMwidth_um"] = raw_df["mae_um"] - dlm_mae
    raw_df["rel_mae_diff_vs_DLMwidth_pct"] = (raw_df["mae_um"] - dlm_mae) / dlm_mae * 100.0

    # Tail-error analysis (top 50 hardest observations by mean abs error across top-5 models)
    all_preds_df = pd.concat(pred_frames, ignore_index=True)
    top5_ids = raw_df["model_id"].head(5).tolist()
    tail_pivot = all_preds_df[all_preds_df["model_id"].isin(top5_ids)].pivot(
        index="source_row_id", columns="model_id", values="raw_absolute_error_um"
    )
    tail_meta = val_gt.set_index("source_row_id")[["Series", "Image", "Gridline", "Stage", "MANwidth"]]
    tail_meta["image_group"] = tail_meta["Series"].astype(str) + "|" + tail_meta["Image"].astype(str)
    tail_df = tail_meta.join(tail_pivot)
    tail_df["top5_mean_abs_error_um"] = tail_pivot.mean(axis=1)
    tail_df = tail_df.sort_values("top5_mean_abs_error_um", ascending=False).head(50).reset_index()

    # Exploratory Paired Image-Cluster Bootstrap (D-010C)
    ref_for_cluster = all_preds_df[all_preds_df["model_id"] == raw_df["model_id"].iloc[0]].sort_values("source_row_id")
    cluster_audit_df = audit_clusters(ref_for_cluster)
    cluster_labels = ref_for_cluster["image_group"].to_numpy()
    boot_models_df, boot_paired_df, draws, unique_clusters = run_paired_cluster_bootstrap(
        model_preds=model_preds_for_boot,
        y_true=expected_y,
        cluster_labels=cluster_labels,
        comparators=("ML01", "DLMwidth", "AEDwidth"),
        n_boot=10000,
        seed=42,
        ci_level=0.95,
    )

    np.savez_compressed(run_dir / "M04B_BOOTSTRAP_DRAWS.npz", draws=draws, clusters=np.array(unique_clusters))
    (run_dir / "M04B_BOOTSTRAP_CONFIGURATION.json").write_text(
        json.dumps(
            {
                "decision": "D-010C",
                "cluster_unit": "Series + Image (image_group)",
                "n_clusters_in_validation": int(len(unique_clusters)),
                "n_observations": int(len(expected_y)),
                "n_boot": 10000,
                "seed": 42,
                "confidence_level": 0.95,
                "ci_method": "percentile",
                "mae_estimand": "pooled_observation_weighted_mae",
                "status": "EXPLORATORY_CONDITIONAL_ON_PROTOCOL_A_VALIDATION",
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    # Save all CSVs & JSONs
    pd.DataFrame(status_rows).to_csv(run_dir / "M04B_MODEL_STATUS.csv", index=False)
    all_preds_df.to_csv(run_dir / "M04B_CONSOLIDATED_VALIDATION_PREDICTIONS.csv", index=False)
    raw_df.to_csv(run_dir / "M04B_CONSOLIDATED_METRICS_RAW.csv", index=False)
    clip_df.to_csv(run_dir / "M04B_CONSOLIDATED_METRICS_NONNEGATIVE.csv", index=False)
    pd.concat(ref_pred_frames, ignore_index=True).to_csv(run_dir / "M04B_REFERENCE_VALIDATION_PREDICTIONS.csv", index=False)
    pd.DataFrame(ref_metric_rows).to_csv(run_dir / "M04B_REFERENCE_VALIDATION_METRICS.csv", index=False)
    pd.DataFrame(tol_rows).to_csv(run_dir / "M04B_TOLERANCE_METRICS.csv", index=False)
    pd.DataFrame(neg_rows).to_csv(run_dir / "M04B_NEGATIVE_PREDICTION_ANALYSIS.csv", index=False)
    pd.DataFrame(subgroup_rows).to_csv(run_dir / "M04B_SUBGROUP_METRICS.csv", index=False)
    pd.DataFrame(zw_rows).to_csv(run_dir / "M04B_ZERO_WIDTH_ANALYSIS.csv", index=False)
    tail_df.to_csv(run_dir / "M04B_TAIL_ERROR_ANALYSIS.csv", index=False)
    pd.DataFrame(resource_rows).to_csv(run_dir / "M04B_RESOURCE_USAGE.csv", index=False)
    pd.DataFrame(fairness_rows).to_csv(run_dir / "M04B_TRAINING_DATA_FAIRNESS_AUDIT.csv", index=False)
    pd.DataFrame(artifact_rows).to_csv(run_dir / "M04B_ARTIFACT_INVENTORY.csv", index=False)
    cluster_audit_df.to_csv(run_dir / "M04B_CLUSTER_AUDIT.csv", index=False)
    boot_models_df.to_csv(run_dir / "M04B_BOOTSTRAP_MODEL_INTERVALS.csv", index=False)
    boot_paired_df.to_csv(run_dir / "M04B_BOOTSTRAP_PAIRED_MAE_DIFFERENCES.csv", index=False)

    (run_dir / "M04B_METRIC_RECOMPUTATION.json").write_text(
        json.dumps(
            {
                "run_id": run_dir.name,
                "n_models_recomputed": len(recomp_checks),
                "max_mae_diff": max(v["mae_diff"] for v in recomp_checks.values()),
                "max_rmse_diff": max(v["rmse_diff"] for v in recomp_checks.values()),
                "per_model": recomp_checks,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    # Data access & split verification snapshots
    (run_dir / "M04B_DATA_ACCESS_AUDIT.json").write_text(
        json.dumps(
            {
                "run_id": run_dir.name,
                "authorized_phase": "M04A_PROTOCOL_A_TRAIN_VAL",
                "train_rows": 12216,
                "validation_rows": 3060,
                "test_rows_excluded": 3822,
                "test_rows_exposed_to_workers": 0,
                "successful_models": int(len(raw_df)),
                "consolidated_prediction_rows": int(len(all_preds_df)),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"CONSOLIDATED_PASS_MODELS={len(raw_df)}")
    print(f"CONSOLIDATED_PRED_ROWS={len(all_preds_df)}")
    print(f"CLUSTERS_IN_VAL={len(unique_clusters)}")
    print(raw_df[["rank_raw_mae", "model_id", "mae_um", "rmse_um", "lins_ccc", "r2"]].to_string(index=False))


if __name__ == "__main__":
    main()
