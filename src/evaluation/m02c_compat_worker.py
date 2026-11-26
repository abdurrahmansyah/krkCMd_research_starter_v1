"""
src/evaluation/m02c_compat_worker.py

Isolated compatibility worker for M02C (FM01-FM04, DL04, RF05).
Strictly uses deterministic synthetic 501-feature profiles (NO real krkCMd data).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import warnings
from pathlib import Path
from typing import Any, Dict

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.evaluation.m02a_compat_worker import generate_synthetic_profiles  # noqa: E402
from src.models.m02c_adapters import get_m02c_adapter  # noqa: E402


def run_stage(model_id: str, stage: str, n_threads: int = 16) -> Dict[str, Any]:
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMBA_NUM_THREADS"):
        os.environ[var] = str(n_threads)

    stage_dims = {
        "L0": (0, 0),
        "L1": (100, 20),
        "L2A": (1000, 200),
        "L2B": (4096, 1024),
        "L2C": (12216, 3822),
    }
    if stage not in stage_dims:
        raise ValueError(f"Unsupported stage: {stage}")

    result: Dict[str, Any] = {
        "model_id": model_id,
        "stage": stage,
        "python_executable": sys.executable,
        "n_threads": n_threads,
        "status": "FAILED",
    }

    with warnings.catch_warnings(record=True) as caught_warnings:
        warnings.simplefilter("always")
        try:
            adapter = get_m02c_adapter(model_id, random_state=42, n_threads=n_threads)
            t0 = time.perf_counter()
            adapter.create_estimator()
            init_sec = round(time.perf_counter() - t0, 4)

            if stage == "L0":
                meta = adapter.get_runtime_metadata()
                result.update({
                    "status": "PASS",
                    "init_time_sec": init_sec,
                    "metadata": meta,
                    "warning_count": len(caught_warnings),
                    "warnings_sample": [str(w.message) for w in caught_warnings[:5]],
                })
                return result

            n_train, n_test = stage_dims[stage]
            X_train, y_train, X_test, _ = generate_synthetic_profiles(n_train, n_test, seed=42)

            adapter.fit(X_train, y_train)
            preds = adapter.predict(X_test)

            serialization_info = None
            if stage == "L1":
                serialization_info = adapter.save_and_reload_predict(X_test)

            neg_count = int(np.sum(preds < 0))
            meta = adapter.get_runtime_metadata()
            result.update({
                "status": "PASS",
                "input_shape": [int(X_train.shape[0]), int(X_train.shape[1])],
                "predict_input_shape": [int(X_test.shape[0]), int(X_test.shape[1])],
                "output_shape": [int(preds.shape[0])],
                "all_finite": bool(np.isfinite(preds).all()),
                "negative_prediction_count": neg_count,
                "min_pred": float(np.min(preds)),
                "max_pred": float(np.max(preds)),
                "init_time_sec": init_sec,
                "checkpoint_load_time_sec": adapter.checkpoint_load_time_sec,
                "fit_context_time_sec": adapter.fit_context_time_sec,
                "predict_time_sec": adapter.predict_time_sec,
                "total_wall_sec": round((adapter.fit_context_time_sec or 0.0) + (adapter.predict_time_sec or 0.0), 4),
                "peak_cuda_allocated_mb": adapter.peak_cuda_allocated_mb,
                "peak_cuda_reserved_mb": adapter.peak_cuda_reserved_mb,
                "serialization": serialization_info,
                "metadata": meta,
                "warning_count": len(caught_warnings),
                "warnings_sample": [str(w.message) for w in caught_warnings[:5]],
            })
        except Exception as exc:
            err_msg = f"{type(exc).__name__}: {exc}"
            low = err_msg.lower()
            if "tabpfnlicenseerror" in low or "license acceptance" in low:
                result["status"] = "BLOCKED_LICENSE"
            elif "401" in low or "gated" in low or "unauthorized" in low:
                result["status"] = "BLOCKED_ACCESS"
            else:
                result["status"] = "FAILED"
            result["error"] = err_msg
            result["warning_count"] = len(caught_warnings)
            result["warnings_sample"] = [str(w.message) for w in caught_warnings[:5]]

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="M02C isolated compatibility worker.")
    parser.add_argument("--model-id", required=True, choices=["FM01", "FM02", "FM03", "FM04", "DL04", "RF05"])
    parser.add_argument("--stage", required=True, choices=["L0", "L1", "L2A", "L2B", "L2C"])
    parser.add_argument("--n-threads", type=int, default=16)
    args = parser.parse_args()

    res = run_stage(args.model_id, args.stage, n_threads=args.n_threads)
    print(json.dumps(res))
    return 0 if res["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
