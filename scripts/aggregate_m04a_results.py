"""
scripts/aggregate_m04a_results.py

Aggregates all M04A attempts, computes raw & nonnegative-clipped metrics, tolerances,
subgroups, Stage C historical references (DLMwidth, AEDwidth), resource usage,
artifact inventory, and independent metric recomputation.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from evaluation.m04a_data import load_protocol_a_train_val  # noqa: E402
from evaluation.metrics import (  # noqa: E402
    compute_engineering_tolerances,
    compute_measurement_agreement,
    compute_predictive_accuracy,
)


def _compute_full_metric_row(model_id: str, variant: str, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
    acc = compute_predictive_accuracy(y_true, y_pred)
    agr = compute_measurement_agreement(y_true, y_pred)
    tol = compute_engineering_tolerances(y_true, y_pred)
    row = {
        "model_id": model_id,
        "prediction_variant": variant,
        "n_obs": int(len(y_true)),
    }
    row.update(acc)
    row.update(agr)
    row.update(tol)
    return row


def _safe_subgroup_metrics(df: pd.DataFrame, group_name: str, group_value: str, model_id: str) -> Dict[str, Any]:
    yt = df["y_true_um"].to_numpy(dtype=np.float64)
    yp = df["y_pred_raw_um"].to_numpy(dtype=np.float64)
    ypc = df["y_pred_nonnegative_um"].to_numpy(dtype=np.float64)
    acc = compute_predictive_accuracy(yt, yp)
    acc_c = compute_predictive_accuracy(yt, ypc)
    pos_mask = yt > 0
    pos_mape = float(np.mean(np.abs(yp[pos_mask] - yt[pos_mask]) / yt[pos_mask]) * 100.0) if pos_mask.any() else None
    return {
        "model_id": model_id,
        "subgroup_type": group_name,
        "subgroup_value": group_value,
        "n_obs": int(len(df)),
        "n_gridline_groups": int(df["group_id"].nunique()),
        "n_image_groups": int(df["image_group"].nunique()),
        "raw_mae_um": acc["mae_um"],
        "raw_rmse_um": acc["rmse_um"],
        "raw_bias_um": acc["bias_um"],
        "raw_r2": acc["r2"],
        "clipped_mae_um": acc_c["mae_um"],
        "clipped_rmse_um": acc_c["rmse_um"],
        "positive_width_mape_pct_descriptive": pos_mape,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    run_dir = Path(args.run_dir)
    run_id = run_dir.name

    # Load 32 registry IDs
    reg_df = pd.read_csv(ROOT / "reports" / "runs" / "M03_20261126_132016_DESKTOP-CQB09OU" / "M03_MODEL_ELIGIBILITY.csv")

    # Find latest attempt per model_id (prefer PASS over failed retries)
    attempts_root = run_dir / "attempts"
    model_attempts: Dict[str, List[Path]] = {}
    for p in sorted(attempts_root.iterdir()):
        if not p.is_dir():
            continue
        # Parse M04A_<MID>_...
        parts = p.name.split("_")
        if len(parts) >= 2 and parts[0] == "M04A":
            mid = parts[1]
            model_attempts.setdefault(mid, []).append(p)

    status_rows = []
    pred_frames = []
    raw_metric_rows = []
    clip_metric_rows = []
    tol_rows = []
    subgroup_rows = []
    resource_rows = []
    artifact_rows = []
    recomp_checks = {}

    for _, r in reg_df.iterrows():
        mid = str(r["id"])
        cand_dirs = model_attempts.get(mid, [])
        chosen_dir: Optional[Path] = None
        chosen_worker: Optional[Dict[str, Any]] = None
        chosen_runner: Optional[Dict[str, Any]] = None

        for d in cand_dirs:
            wp = d / "worker_result.json"
            rp = d / "runner_result.json"
            if wp.exists():
                w = json.loads(wp.read_text(encoding="utf-8"))
                if w.get("status") == "PASS":
                    chosen_dir = d
                    chosen_worker = w
                    chosen_runner = json.loads(rp.read_text(encoding="utf-8")) if rp.exists() else {}
                    break
        if chosen_dir is None and cand_dirs:
            chosen_dir = cand_dirs[-1]
            rp = chosen_dir / "runner_result.json"
            chosen_runner = json.loads(rp.read_text(encoding="utf-8")) if rp.exists() else {}

        if chosen_worker is not None:
            m_status = "PASS"
            fail_reason = ""
            pred_df = pd.read_csv(chosen_dir / "predictions.csv")
            pred_frames.append(pred_df)

            yt = pred_df["y_true_um"].to_numpy(dtype=np.float64)
            yp_raw = pred_df["y_pred_raw_um"].to_numpy(dtype=np.float64)
            yp_clip = pred_df["y_pred_nonnegative_um"].to_numpy(dtype=np.float64)

            rm = _compute_full_metric_row(mid, "raw", yt, yp_raw)
            cm = _compute_full_metric_row(mid, "nonnegative_clipped", yt, yp_clip)
            rm["n_negative_raw_predictions"] = chosen_worker["n_negative_raw_predictions"]
            rm["min_raw_prediction_um"] = chosen_worker["min_raw_prediction_um"]
            raw_metric_rows.append(rm)
            clip_metric_rows.append(cm)

            tol_r = {"model_id": mid, "prediction_variant": "raw"}
            tol_r.update(compute_engineering_tolerances(yt, yp_raw))
            tol_c = {"model_id": mid, "prediction_variant": "nonnegative_clipped"}
            tol_c.update(compute_engineering_tolerances(yt, yp_clip))
            tol_rows.extend([tol_r, tol_c])

            # Subgroups: Series, Stage, zero vs positive, crack-width bins
            for s_val, g in pred_df.groupby("Series"):
                subgroup_rows.append(_safe_subgroup_metrics(g, "Series", str(s_val), mid))
            for st_val, g in pred_df.groupby("Stage"):
                subgroup_rows.append(_safe_subgroup_metrics(g, "Stage", str(st_val), mid))
            subgroup_rows.append(_safe_subgroup_metrics(pred_df[pred_df["y_true_um"] == 0.0], "WidthRegime", "zero_width_0", mid))
            subgroup_rows.append(_safe_subgroup_metrics(pred_df[pred_df["y_true_um"] > 0.0], "WidthRegime", "positive_width_gt0", mid))
            subgroup_rows.append(_safe_subgroup_metrics(pred_df[(pred_df["y_true_um"] > 0.0) & (pred_df["y_true_um"] <= 100.0)], "WidthBin", "(0, 100]", mid))
            subgroup_rows.append(_safe_subgroup_metrics(pred_df[(pred_df["y_true_um"] > 100.0) & (pred_df["y_true_um"] <= 300.0)], "WidthBin", "(100, 300]", mid))
            subgroup_rows.append(_safe_subgroup_metrics(pred_df[pred_df["y_true_um"] > 300.0], "WidthBin", ">300", mid))

            resource_rows.append({
                "model_id": mid,
                "name": r["name"],
                "environment": r["environment"],
                "device": chosen_worker["device"],
                "init_sec": chosen_worker["init_sec"],
                "preprocess_fit_sec": chosen_worker["preprocess_fit_sec"],
                "load_sec": chosen_worker["load_sec"],
                "train_or_context_sec": chosen_worker["train_or_context_sec"],
                "predict_sec": chosen_worker["predict_sec"],
                "total_elapsed_sec": chosen_worker["total_elapsed_sec"],
                "subprocess_wall_sec": chosen_runner.get("elapsed_sec"),
                "val_throughput_rows_per_sec": chosen_worker["val_throughput_rows_per_sec"],
                "peak_rss_mb": chosen_runner.get("peak_rss_mb"),
                "peak_cuda_alloc_mb": chosen_worker["peak_cuda_alloc_mb"],
                "peak_cuda_res_mb": chosen_worker["peak_cuda_res_mb"],
                "param_count": chosen_worker["param_count"],
                "actual_epochs": chosen_worker["actual_epochs"],
                "best_epoch": chosen_worker["best_epoch"],
            })

            artifact_rows.append({
                "model_id": mid,
                "attempt_id": chosen_dir.name,
                "artifact_path": chosen_worker["artifact_path"],
                "artifact_size_bytes": chosen_worker["artifact_size_bytes"],
                "artifact_sha256": chosen_worker["artifact_sha256"],
            })

            # Independent recomputation check
            ind_mae = float(np.mean(np.abs(yp_raw - yt)))
            ind_rmse = float(np.sqrt(np.mean((yp_raw - yt) ** 2)))
            recomp_checks[mid] = {
                "reported_mae_um": rm["mae_um"],
                "recomputed_mae_um": ind_mae,
                "mae_diff": abs(rm["mae_um"] - ind_mae),
                "reported_rmse_um": rm["rmse_um"],
                "recomputed_rmse_um": ind_rmse,
                "rmse_diff": abs(rm["rmse_um"] - ind_rmse),
                "n_rows": int(len(pred_df)),
            }
        elif chosen_runner is not None:
            m_status = "FAILED"
            fail_reason = chosen_runner.get("violation_reason") or f"rc={chosen_runner.get('returncode')}"
        else:
            m_status = str(r["m03_readiness_tier"])
            fail_reason = "Not targeted in M04A (D-009E)"

        status_rows.append({
            "model_id": mid,
            "name": r["name"],
            "category": r["category"],
            "environment": r["environment"],
            "m04a_targeted": mid in model_attempts,
            "m04a_status": m_status,
            "chosen_attempt_id": chosen_dir.name if chosen_dir else "",
            "n_attempts": len(cand_dirs),
            "failure_or_exclusion_reason": fail_reason,
        })

    # Rank raw & clipped metrics by MAE (ascending), tie-break RMSE (ascending), Lin's CCC (descending)
    raw_df = pd.DataFrame(raw_metric_rows).sort_values(
        ["mae_um", "rmse_um", "lins_ccc"], ascending=[True, True, False]
    ).reset_index(drop=True)
    raw_df.insert(0, "rank_raw_mae", np.arange(1, len(raw_df) + 1))

    clip_df = pd.DataFrame(clip_metric_rows).sort_values(
        ["mae_um", "rmse_um", "lins_ccc"], ascending=[True, True, False]
    ).reset_index(drop=True)
    clip_df.insert(0, "rank_clipped_mae", np.arange(1, len(clip_df) + 1))

    # Stage C Historical Comparison (DLMwidth & AEDwidth on exact same Protocol A validation rows)
    raw_csv = ROOT / "data" / "raw" / "krkCMd_table.csv"
    manifest_csv = ROOT / "reports" / "tables" / "group_split_manifest.csv"
    df_all = pd.read_csv(raw_csv)
    df_man = pd.read_csv(manifest_csv)
    df_all["source_row_id"] = np.arange(len(df_all), dtype=np.int64)
    df_val = df_all.merge(df_man, on="source_row_id", how="inner")
    df_val = df_val.loc[df_val["split"] == "validation"].sort_values("source_row_id").reset_index(drop=True)

    ref_rows = []
    for ref_col in ["DLMwidth", "AEDwidth"]:
        yt = df_val["MANwidth"].to_numpy(dtype=np.float64)
        yp = df_val[ref_col].to_numpy(dtype=np.float64)
        rr = _compute_full_metric_row(ref_col, "historical_stored_output", yt, yp)
        rr["provenance"] = "HISTORICAL_CSV_STORED_OUTPUT_POTENTIALLY_NON_INDEPENDENT"
        ref_rows.append(rr)

    # Write all CSVs & JSONs
    pd.DataFrame(status_rows).to_csv(run_dir / "M04A_MODEL_STATUS.csv", index=False)
    pd.concat(pred_frames, ignore_index=True).to_csv(run_dir / "M04A_VALIDATION_PREDICTIONS.csv", index=False)
    raw_df.to_csv(run_dir / "M04A_VALIDATION_METRICS_RAW.csv", index=False)
    clip_df.to_csv(run_dir / "M04A_VALIDATION_METRICS_NONNEGATIVE.csv", index=False)
    pd.DataFrame(ref_rows).to_csv(run_dir / "M04A_REFERENCE_VALIDATION_METRICS.csv", index=False)
    pd.DataFrame(tol_rows).to_csv(run_dir / "M04A_TOLERANCE_METRICS.csv", index=False)
    pd.DataFrame(subgroup_rows).to_csv(run_dir / "M04A_SUBGROUP_METRICS.csv", index=False)
    pd.DataFrame(resource_rows).to_csv(run_dir / "M04A_RESOURCE_USAGE.csv", index=False)
    pd.DataFrame(artifact_rows).to_csv(run_dir / "M04A_ARTIFACT_INVENTORY.csv", index=False)

    (run_dir / "M04A_METRIC_RECOMPUTATION.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "n_models_recomputed": len(recomp_checks),
                "max_mae_diff": max(v["mae_diff"] for v in recomp_checks.values()),
                "max_rmse_diff": max(v["rmse_diff"] for v in recomp_checks.values()),
                "per_model": recomp_checks,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    # Consolidate Data Access Audit from one worker + split verification
    sample_audit = next(iter(model_attempts.values()))[-1] / "worker_result.json"
    if sample_audit.exists():
        w = json.loads(sample_audit.read_text(encoding="utf-8"))
        (run_dir / "M04A_DATA_ACCESS_AUDIT.json").write_text(json.dumps(w["data_audit"], indent=2), encoding="utf-8")

    print(f"AGGREGATED_MODELS={len(raw_df)}")
    print(raw_df[["rank_raw_mae", "model_id", "mae_um", "rmse_um", "lins_ccc", "r2"]].to_string(index=False))


if __name__ == "__main__":
    main()
