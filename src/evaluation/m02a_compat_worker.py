"""
src/evaluation/m02a_compat_worker.py

Isolated compatibility worker for M02A L0, L1, and progressive L2 synthetic checks.
Strictly uses deterministic synthetic 501-feature profiles (NO real krkCMd data).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
import warnings
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.models.m02a_adapters import EXPECTED_FEATURES, get_adapter  # noqa: E402


def generate_synthetic_profiles(
    n_train: int,
    n_test: int,
    n_features: int = EXPECTED_FEATURES,
    seed: int = 42,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Generate deterministic synthetic 1D concrete crack brightness profiles."""
    rng = np.random.default_rng(seed)
    x_axis = np.linspace(-10.0, 10.0, n_features)

    def _make(n: int) -> Tuple[np.ndarray, np.ndarray]:
        widths = rng.uniform(30.0, 350.0, size=(n, 1))
        centers = rng.uniform(-2.0, 2.0, size=(n, 1))
        depths = rng.uniform(50.0, 150.0, size=(n, 1))
        noise = rng.normal(0.0, 3.0, size=(n, n_features))
        dip = depths * np.exp(-0.5 * ((x_axis[None, :] - centers) / (widths / 50.0)) ** 2)
        X = np.clip(180.0 - dip + noise, 0.0, 255.0).astype(np.float32)
        y = widths[:, 0].astype(np.float32)
        return X, y

    X_train, y_train = _make(n_train)
    X_test, y_test = _make(n_test)
    return X_train, y_train, X_test, y_test


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
            adapter = get_adapter(model_id, random_state=42, n_threads=n_threads)
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

            # For Numba-based signal estimators, measure second fit/predict on L1 to separate JIT overhead
            second_run = None
            if stage == "L1" and model_id in ("SG05", "SG06"):
                adapter2 = get_adapter(model_id, random_state=42, n_threads=n_threads)
                adapter2.fit(X_train, y_train)
                _ = adapter2.predict(X_test)
                second_run = {
                    "fit_time_sec": adapter2.fit_time_sec,
                    "predict_time_sec": adapter2.predict_time_sec,
                }

            serialization_info = None
            if stage == "L1":
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        model_file = Path(tmpdir) / f"{model_id}.joblib"
                        adapter.save(model_file)
                        reloaded_preds = adapter.load_and_predict(model_file, X_test)
                        max_diff = float(np.max(np.abs(preds - reloaded_preds)))
                        serialization_info = {
                            "supported": True,
                            "artifact_size_bytes": model_file.stat().st_size,
                            "max_reload_diff": max_diff,
                            "consistent": bool(np.allclose(preds, reloaded_preds, atol=1e-6)),
                        }
                except Exception as ser_exc:
                    serialization_info = {"supported": False, "error": str(ser_exc)}

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
                "fit_time_sec": adapter.fit_time_sec,
                "predict_time_sec": adapter.predict_time_sec,
                "total_wall_sec": round((adapter.fit_time_sec or 0.0) + (adapter.predict_time_sec or 0.0), 4),
                "second_run_post_jit": second_run,
                "serialization": serialization_info,
                "metadata": meta,
                "warning_count": len(caught_warnings),
                "warnings_sample": [str(w.message) for w in caught_warnings[:5]],
            })
        except Exception as exc:
            result["status"] = "FAILED"
            result["error"] = f"{type(exc).__name__}: {exc}"
            result["warning_count"] = len(caught_warnings)
            result["warnings_sample"] = [str(w.message) for w in caught_warnings[:5]]

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="M02A isolated compatibility worker.")
    parser.add_argument("--model-id", required=True, choices=["ML04", "ML05", "ML06", "SG05", "SG06"])
    parser.add_argument("--stage", required=True, choices=["L0", "L1", "L2A", "L2B", "L2C"])
    parser.add_argument("--n-threads", type=int, default=16)
    args = parser.parse_args()

    res = run_stage(args.model_id, args.stage, n_threads=args.n_threads)
    print(json.dumps(res))
    return 0 if res["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
