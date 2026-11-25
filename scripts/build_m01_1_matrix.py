"""
scripts/build_m01_1_matrix.py

Builds the separated M01.1 32-candidate compatibility matrix from:
  - configs/model_registry.yaml (corrected M01.1 definitions)
  - reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/smoke_test_results_new_pc.json
  - reports/logs/cuda_dependency_resolution_M01_1.json

Strictly separates static compatibility, package availability, dependency resolution,
installed environment, actual implementation tested, L0/L1/L2 statuses, GPU computation
status, reproduction fidelity, and experimental approval (NOT_APPROVED).
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List
import yaml

ROOT = Path(__file__).resolve().parents[1]


def build_matrix(
    registry_path: Path,
    smoke_path: Path,
    dep_path: Path,
    out_csv: Path,
) -> List[Dict[str, Any]]:
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    smoke_data = json.loads(smoke_path.read_text(encoding="utf-8"))["results"]
    dep_data = json.loads(dep_path.read_text(encoding="utf-8"))["dry_runs"]

    rows: List[Dict[str, Any]] = []
    for category, items in registry["categories"].items():
        for item in items:
            mid = item["id"]
            env = item.get("env", "")
            sm = smoke_data.get(mid)

            # Determine dependency resolution status from M01.1 dry-runs
            if "env-baseline" in env and mid in ("ML01", "ML02", "ML03", "ML07", "DL01", "HY02", "RF01", "RF02", "RF03"):
                dep_status = "INSTALLED_AND_RESOLVED_BASELINE"
                inst_env = ".venv (Python 3.11.9)"
            elif "env-boost" in env:
                dep_status = dep_data.get("env-boost", {}).get("status", "UNKNOWN")
                inst_env = "NOT_INSTALLED (proposed: .venv-boost)"
            elif "env-deep" in env and "env-signal-tf" not in env:
                cuda_ok = dep_data.get("env-deep-cuda-cu128", {}).get("status") == "RESOLVED_TRANSITIVE"
                addons_ok = dep_data.get("env-deep-addons-pypi", {}).get("status") == "RESOLVED_TRANSITIVE"
                dep_status = "RESOLVED_TRANSITIVE_CU128" if (cuda_ok and addons_ok) else "PARTIAL_OR_FAILED"
                inst_env = "NOT_INSTALLED (proposed: .venv-deep)"
            elif "env-signal-tf" in env:
                dep_status = dep_data.get("env-signal-tf", {}).get("status", "UNKNOWN")
                inst_env = "NOT_INSTALLED (proposed: .venv-signal-tf or PyTorch port)"
            elif "env-signal-cpu" in env:
                dep_status = dep_data.get("env-signal-cpu", {}).get("status", "UNKNOWN")
                inst_env = "NOT_INSTALLED (proposed: .venv-signal-cpu)"
            elif "env-foundation" in env:
                cuda_ok = dep_data.get("env-deep-cuda-cu128", {}).get("status") == "RESOLVED_TRANSITIVE"
                fm_ok = dep_data.get("env-foundation-addons-pypi", {}).get("status") == "RESOLVED_TRANSITIVE"
                dep_status = "RESOLVED_TRANSITIVE_CU128" if (cuda_ok and fm_ok) else "PARTIAL_OR_FAILED"
                inst_env = "NOT_INSTALLED (proposed: .venv-foundation, gated)"
            else:
                dep_status = "NOT_APPLICABLE"
                inst_env = "NOT_INSTALLED"

            # Package availability
            if mid == "DL04":
                pkg_avail = "torch+faiss-cpu on PyPI; tabular-dl-tabr repo-only"
            elif mid == "RF04":
                pkg_avail = "MATLAB+nnet NOT installed; PyTorch port required"
            else:
                pkg_avail = "PyPI / PyTorch cu128 wheels verified"

            # Actual implementation tested, L0/L1, reproduction fidelity
            if sm:
                actual_impl = sm["estimator_tested"]
                l0 = "PASS" if sm.get("l0_import") else "FAIL"
                l1 = "PASS" if sm.get("l1_fit_predict") else "FAIL"
                if mid == "DL01":
                    l1 = "PASS_PROTOTYPE (sklearn ConvergenceWarning at max_iter=20; PyTorch MLP NOT_EXECUTED)"
                elif mid == "RF03":
                    l1 = "PASS_PROTOTYPE (analytical init+predict finite; no training)"
            else:
                actual_impl = "NONE (NOT_EXECUTED)"
                l0 = "NOT_EXECUTED"
                l1 = "NOT_EXECUTED"

            if mid == "RF03":
                repro_fid = "CONDITIONAL (simplified prototype tested; faithful CrackWidthAED_VBA.txt parity unvalidated)"
            elif mid == "RF04":
                repro_fid = "CONDITIONAL (krknet.mat requires MATLAB nnet or exact weight extraction)"
            elif mid == "RF05":
                repro_fid = "NOT_EXECUTED (Table 3 15-layer CNN architecture retraining)"
            else:
                repro_fid = "N/A"

            rows.append({
                "id": mid,
                "name": item["name"],
                "category": category,
                "target_estimator": item["estimator"],
                "static_compatibility": item["status"],
                "package_availability": pkg_avail,
                "dependency_resolution": dep_status,
                "installed_environment": inst_env,
                "actual_implementation_tested": actual_impl,
                "l0_status": l0,
                "l1_status": l1,
                "l2_status": "NOT_EXECUTED",
                "gpu_computation_status": "NOT_EXECUTED (PyTorch CUDA not installed in M01.1)",
                "reproduction_fidelity": repro_fid,
                "experimental_approval": "NOT_APPROVED",
            })

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    rows = build_matrix(
        ROOT / "configs" / "model_registry.yaml",
        ROOT / "reports" / "runs" / "M01R_20261125_032229_DESKTOP-CQB09OU" / "smoke_test_results_new_pc.json",
        ROOT / "reports" / "logs" / "cuda_dependency_resolution_M01_1.json",
        ROOT / "reports" / "tables" / "model_compatibility_matrix_M01_1.csv",
    )
    print(f"WROTE {len(rows)} rows to reports/tables/model_compatibility_matrix_M01_1.csv")
