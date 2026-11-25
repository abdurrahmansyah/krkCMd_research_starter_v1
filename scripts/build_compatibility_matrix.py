"""
scripts/build_compatibility_matrix.py

Authoritative registry-driven compatibility matrix builder (M02B Section 2).
Loads static model definitions from configs/model_registry.yaml and reconciles
versioned runtime evidence from M01-R / M02A / M02B run directories without
mutating historical matrices or marking any model APPROVED.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_registry_candidates(registry_path: Path) -> List[Dict[str, Any]]:
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    out: List[Dict[str, Any]] = []
    for category, items in data["categories"].items():
        for item in items:
            row = dict(item)
            row["category"] = category
            out.append(row)
    return out


def reconcile_effective_matrix(
    registry_path: Path,
    m01_1_matrix_path: Optional[Path] = None,
    m02a_run_dir: Optional[Path] = None,
    m02b_run_dir: Optional[Path] = None,
    out_csv: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    candidates = load_registry_candidates(registry_path)

    base_map: Dict[str, Dict[str, Any]] = {}
    if m01_1_matrix_path and m01_1_matrix_path.exists():
        with m01_1_matrix_path.open("r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                base_map[r["id"]] = r

    m02a_smoke = {}
    m02a_cap = {}
    if m02a_run_dir and (m02a_run_dir / "smoke_test_results_M02A.json").exists():
        m02a_smoke = json.loads((m02a_run_dir / "smoke_test_results_M02A.json").read_text(encoding="utf-8"))
        m02a_cap = json.loads((m02a_run_dir / "capacity_test_results_M02A.json").read_text(encoding="utf-8"))

    m02b_smoke = {}
    m02b_cap = {}
    if m02b_run_dir and (m02b_run_dir / "smoke_test_results_M02B.json").exists():
        m02b_smoke = json.loads((m02b_run_dir / "smoke_test_results_M02B.json").read_text(encoding="utf-8"))
        m02b_cap = json.loads((m02b_run_dir / "capacity_test_results_M02B.json").read_text(encoding="utf-8"))

    rows: List[Dict[str, Any]] = []
    for item in candidates:
        mid = item["id"]
        prev = base_map.get(mid, {})
        effective_status = item.get("status", "STATIC_REVIEW")

        row: Dict[str, Any] = {
            "id": mid,
            "name": item["name"],
            "category": item["category"],
            "registry_static_status": item.get("status", "STATIC_REVIEW"),
            "effective_runtime_status": effective_status,
            "target_estimator": item.get("estimator", ""),
            "actual_implementation_tested": prev.get("actual_implementation_tested", "NONE (NOT_EXECUTED)"),
            "package_and_version": prev.get("package_availability", item.get("package", "")),
            "environment": prev.get("installed_environment", item.get("env", "")),
            "device": item.get("hardware", "CPU"),
            "l0_status": prev.get("l0_status", "NOT_EXECUTED"),
            "l1_status": prev.get("l1_status", "NOT_EXECUTED"),
            "l2a_status": "NOT_EXECUTED",
            "l2b_status": "NOT_EXECUTED",
            "l2c_status": "NOT_EXECUTED",
            "tested_configuration": "N/A",
            "max_tested_shape": "N/A",
            "memory_usage_summary": "N/A",
            "serialization_result": "N/A",
            "source_evidence": prev.get("evidence_paths", "configs/model_registry.yaml"),
            "remaining_limitations": item.get("notes", "None recorded"),
            "experimental_approval": "NOT_APPROVED",
        }

        # Reconcile M02A evidence
        if mid in m02a_smoke:
            l0 = m02a_smoke[mid].get("L0", {})
            l1 = m02a_smoke[mid].get("L1", {})
            cap = m02a_cap.get(mid, {})
            l2a, l2b, l2c = cap.get("L2A", {}), cap.get("L2B", {}), cap.get("L2C", {})
            meta = l1.get("metadata", l0.get("metadata", {}))
            if all(x.get("status") == "PASS" for x in (l0, l1, l2a, l2b, l2c)):
                row["effective_runtime_status"] = "SCALE_CHECK_PASS"
            elif l1.get("status") == "PASS":
                row["effective_runtime_status"] = "SMOKE_TEST_PASS"
            elif l0.get("status") == "FAILED":
                row["effective_runtime_status"] = "BLOCKED"
            row["actual_implementation_tested"] = meta.get("estimator_class", row["target_estimator"])
            row["package_and_version"] = f"{meta.get('package', '')}=={meta.get('package_version', '')}"
            row["environment"] = ".venv-boost" if mid.startswith("ML") else ".venv-signal-cpu"
            row["device"] = "CPU"
            row["l0_status"] = l0.get("status", "NOT_EXECUTED")
            row["l1_status"] = l1.get("status", "NOT_EXECUTED")
            row["l2a_status"] = l2a.get("status", "NOT_EXECUTED")
            row["l2b_status"] = l2b.get("status", "NOT_EXECUTED")
            row["l2c_status"] = l2c.get("status", "NOT_EXECUTED")
            row["tested_configuration"] = json.dumps(meta.get("config", {}))
            row["max_tested_shape"] = "(12216, 501) -> (3822,)" if l2c.get("status") == "PASS" else "NONE"
            row["memory_usage_summary"] = f"L2C peak_rss={l2c.get('peak_rss_mb', 'N/A')} MiB"
            ser = l1.get("serialization") or {}
            row["serialization_result"] = f"supported={ser.get('supported')}, diff={ser.get('max_reload_diff')}" if ser else "N/A"
            row["source_evidence"] = f"reports/runs/{m02a_run_dir.name}"

        # Reconcile M02B evidence (takes precedence for M02B targets including SG06 retry)
        if mid in m02b_smoke:
            l0 = m02b_smoke[mid].get("L0", {})
            l1 = m02b_smoke[mid].get("L1", {})
            cap = m02b_cap.get(mid, {})
            l2a, l2b, l2c = cap.get("L2A", {}), cap.get("L2B", {}), cap.get("L2C", {})
            meta = l1.get("metadata", l0.get("metadata", {}))
            if all(x.get("status") == "PASS" for x in (l0, l1, l2a, l2b, l2c)):
                row["effective_runtime_status"] = "SCALE_CHECK_PASS"
            elif l1.get("status") == "PASS":
                row["effective_runtime_status"] = "SMOKE_TEST_PASS"
            elif l0.get("status") == "FAILED" or l1.get("status") == "FAILED":
                row["effective_runtime_status"] = "FAILED"
            elif l0.get("status") == "BLOCKED" or meta.get("blocked"):
                row["effective_runtime_status"] = "BLOCKED"
            elif l0.get("status") == "CONDITIONAL":
                row["effective_runtime_status"] = "CONDITIONAL"

            row["actual_implementation_tested"] = meta.get("estimator_class", row["target_estimator"])
            row["package_and_version"] = f"{meta.get('package', '')}=={meta.get('package_version', '')}"
            row["environment"] = meta.get("environment_name", row["environment"])
            row["device"] = meta.get("device_used", row["device"])
            row["l0_status"] = l0.get("status", "NOT_EXECUTED")
            row["l1_status"] = l1.get("status", "NOT_EXECUTED")
            row["l2a_status"] = l2a.get("status", "NOT_EXECUTED")
            row["l2b_status"] = l2b.get("status", "NOT_EXECUTED")
            row["l2c_status"] = l2c.get("status", "NOT_EXECUTED")
            row["tested_configuration"] = json.dumps(meta.get("config", {}))
            if l2c.get("status") == "PASS":
                row["max_tested_shape"] = "(12216, 501) -> (3822,)"
            elif l2b.get("status") == "PASS":
                row["max_tested_shape"] = "(4096, 501) -> (1024,)"
            elif l2a.get("status") == "PASS":
                row["max_tested_shape"] = "(1000, 501) -> (200,)"
            elif l1.get("status") == "PASS":
                row["max_tested_shape"] = "(100, 501) -> (20,)"
            else:
                row["max_tested_shape"] = "NONE"

            rss_val = l2c.get("peak_rss_mb") or l1.get("peak_rss_mb") or l0.get("peak_rss_mb") or "N/A"
            vram_val = l2c.get("peak_cuda_allocated_mb") or l1.get("peak_cuda_allocated_mb") or "N/A"
            row["memory_usage_summary"] = f"peak_rss={rss_val} MiB; peak_cuda_alloc={vram_val} MiB"
            ser = l1.get("serialization") or {}
            row["serialization_result"] = f"supported={ser.get('supported')}, diff={ser.get('max_reload_diff')}" if ser else "N/A"
            row["source_evidence"] = f"reports/runs/{m02b_run_dir.name}"
            if meta.get("limitation"):
                row["remaining_limitations"] = meta["limitation"]

        # Never allow APPROVED in compatibility matrix
        row["experimental_approval"] = "NOT_APPROVED"
        rows.append(row)

    if out_csv:
        out_csv.parent.mkdir(parents=True, exist_ok=True)
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    return rows
