"""
scripts/run_m02c_compatibility.py

Configurable M02C orchestrator:
  1. Verifies GPU matmul + Conv1d + finite gradients & parameters after optimizer update
  2. Runs Track A (FM01-FM04) and Track B (DL04, RF05, SG06 L2C 1800s retry)
  3. Validates exit code, timeout, resource violations, and JSON integrity
  4. Records downloaded local checkpoint SHA-256 inventory & reconciles 32-candidate matrix
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from build_compatibility_matrix import reconcile_effective_matrix  # noqa: E402
from resource_policy import refresh_available_resources, run_monitored_subprocess  # noqa: E402


def parse_worker_result(res: Dict[str, Any]) -> Dict[str, Any]:
    """Strictly validate subprocess exit code, timeout, resource violations, and JSON output."""
    stdout = str(res.get("stdout", "") or "").strip()
    payload: Dict[str, Any] = {"status": "FAILED", "error": "Empty worker output"}
    if stdout:
        try:
            payload = json.loads(stdout.splitlines()[-1])
        except Exception as exc:
            payload = {"status": "FAILED", "error": f"Malformed worker JSON: {exc}"}

    # A worker that emits PASS JSON but subsequently fails, times out, or breaches limits CANNOT pass!
    if res.get("timed_out") or res.get("violation_reason") or res.get("returncode", 1) != 0:
        if payload.get("status") == "PASS":
            payload["status"] = "FAILED"
            payload["error"] = res.get("violation_reason") or f"Subprocess failed with rc={res.get('returncode')}"
        elif not payload.get("error"):
            payload["error"] = res.get("violation_reason") or str(res.get("stderr", ""))[-400:]

    payload["peak_rss_mb"] = res.get("peak_rss_mb")
    payload["subprocess_elapsed_sec"] = res.get("elapsed_sec")
    payload["violation_reason"] = res.get("violation_reason")
    return payload


def verify_gpu_runtime_m02c(py_exe: str, out_json: Path) -> Dict[str, Any]:
    budget = refresh_available_resources(ROOT)
    if budget.vram_budget_bytes <= 0:
        data = {"status": "BLOCKED_INSUFFICIENT_VRAM_BUDGET", "vram_budget_gib": budget.vram_budget_gib}
        out_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data

    script = """
import json, time, torch
out = {
    "torch_version": torch.__version__,
    "torch_cuda_version": torch.version.cuda,
    "cuda_available": torch.cuda.is_available(),
}
if torch.cuda.is_available():
    out["gpu_name"] = torch.cuda.get_device_name(0)
    out["compute_capability"] = list(torch.cuda.get_device_capability(0))
    torch.cuda.reset_peak_memory_stats(0)
    t0 = time.perf_counter()
    # Explicit CUDA matrix multiplication
    a = torch.randn((256, 256), device="cuda:0", dtype=torch.float32)
    b = torch.randn((256, 256), device="cuda:0", dtype=torch.float32)
    c = a @ b
    # Conv1d forward + backward + optimizer update + explicit finite grad & param check
    x = torch.randn((32, 1, 501), device="cuda:0", dtype=torch.float32)
    y = torch.randn((32, 1), device="cuda:0", dtype=torch.float32)
    conv = torch.nn.Conv1d(1, 16, kernel_size=5, padding=2).to("cuda:0")
    fc = torch.nn.Linear(16 * 501, 1).to("cuda:0")
    opt = torch.optim.AdamW(list(conv.parameters()) + list(fc.parameters()), lr=1e-3)
    pred = fc(torch.relu(conv(x)).flatten(1))
    loss = torch.nn.functional.mse_loss(pred, y)
    loss.backward()
    grads_finite = all(p.grad is not None and torch.isfinite(p.grad).all().item() for p in list(conv.parameters()) + list(fc.parameters()))
    opt.step()
    params_finite = all(torch.isfinite(p).all().item() for p in list(conv.parameters()) + list(fc.parameters()))
    torch.cuda.synchronize()
    out["matmul_finite"] = bool(torch.isfinite(c).all().item())
    out["fp32_finite"] = bool(torch.isfinite(pred).all().item() and torch.isfinite(loss).item())
    out["grads_finite_post_backward"] = grads_finite
    out["params_finite_post_step"] = params_finite
    out["device_placed"] = str(pred.device)
    out["elapsed_sec"] = round(time.perf_counter() - t0, 4)
    out["peak_cuda_allocated_mb"] = round(torch.cuda.max_memory_allocated(0) / (1024**2), 3)
    out["status"] = "GPU_PASS" if (out["matmul_finite"] and out["fp32_finite"] and grads_finite and params_finite) else "GPU_FAILED"
else:
    out["status"] = "CPU_ONLY"
print(json.dumps(out))
"""
    res = run_monitored_subprocess([py_exe, "-c", script], timeout_sec=120, cpu_threads=16, monitor_gpu=True)
    data = parse_worker_result(res)
    out_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def inventory_local_checkpoints(out_json: Path) -> List[Dict[str, Any]]:
    cache_dir = ROOT / ".cache" / "hf"
    rows: List[Dict[str, Any]] = []
    if cache_dir.exists():
        for ext in ("*.safetensors", "*.ckpt", "*.bin", "*.pt"):
            for p in sorted(cache_dir.rglob(ext)):
                if p.is_file():
                    h = hashlib.sha256()
                    with p.open("rb") as f:
                        for chunk in iter(lambda: f.read(1024 * 1024), b""):
                            h.update(chunk)
                    rows.append({
                        "filename": p.name,
                        "relative_cache_path": p.relative_to(ROOT).as_posix(),
                        "size_bytes": p.stat().st_size,
                        "size_mb": round(p.stat().st_size / (1024 ** 2), 2),
                        "sha256": h.hexdigest().upper(),
                    })
    out_json.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return rows


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="M02C configurable compatibility orchestrator.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--candidates", nargs="*", default=None, help="Optional subset of candidate IDs.")
    args = parser.parse_args(argv)

    run_dir = ROOT / "reports" / "runs" / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    found_py = str(ROOT / ".venv-foundation" / "Scripts" / "python.exe")
    tabr_py = str(ROOT / ".venv-tabr" / "Scripts" / "python.exe")
    deep_py = str(ROOT / ".venv-deep" / "Scripts" / "python.exe")
    hydra_py = str(ROOT / ".venv-signal-hydra" / "Scripts" / "python.exe")
    worker_c = str(ROOT / "src" / "evaluation" / "m02c_compat_worker.py")
    worker_b = str(ROOT / "src" / "evaluation" / "m02b_compat_worker.py")

    print("=== 1. M02C GPU Verification (.venv-foundation) ===", flush=True)
    gpu_res = verify_gpu_runtime_m02c(found_py, run_dir / "gpu_runtime_verification_M02C.json")
    print("GPU_VERIFICATION:", gpu_res.get("status"), gpu_res.get("gpu_name"), "matmul:", gpu_res.get("matmul_finite"), "params_finite:", gpu_res.get("params_finite_post_step"), flush=True)

    plan = [
        ("FM01", found_py, ".venv-foundation", worker_c, ("L0", "L1", "L2A", "L2B", "L2C"), 900, True),
        ("FM02", found_py, ".venv-foundation", worker_c, ("L0", "L1", "L2A", "L2B", "L2C"), 900, True),
        ("FM03", found_py, ".venv-foundation", worker_c, ("L0", "L1", "L2A", "L2B", "L2C"), 900, True),
        ("FM04", found_py, ".venv-foundation", worker_c, ("L0", "L1", "L2A", "L2B", "L2C"), 900, True),
        ("DL04", tabr_py, ".venv-tabr", worker_c, ("L0", "L1", "L2A", "L2B", "L2C"), 900, False),
        ("RF05", deep_py, ".venv-deep", worker_c, ("L0", "L1", "L2A", "L2B", "L2C"), 900, True),
        ("SG06", hydra_py, ".venv-signal-hydra", worker_b, ("L2C",), 1800, False),
    ]
    if args.candidates:
        wanted = set(args.candidates)
        plan = [p for p in plan if p[0] in wanted]

    smk_path = run_dir / "smoke_test_results_M02C.json"
    cap_path = run_dir / "capacity_test_results_M02C.json"
    smoke_results: Dict[str, Any] = json.loads(smk_path.read_text(encoding="utf-8")) if (args.candidates and smk_path.exists()) else {}
    capacity_results: Dict[str, Any] = json.loads(cap_path.read_text(encoding="utf-8")) if (args.candidates and cap_path.exists()) else {}
    resource_rows: List[Dict[str, Any]] = []

    for mid, py_exe, env_name, wrk, stages, timeout_s, mon_gpu in plan:
        print(f"\n=== Testing {mid} ({env_name}) ===", flush=True)
        if mid == "SG06":
            # Preserve M02B L0..L2B for SG06 and run controlled L2C 1800s retry!
            m02b_dir = ROOT / "reports/runs/M02B_20261125_081433_DESKTOP-CQB09OU"
            m02b_smk = json.loads((m02b_dir / "smoke_test_results_M02B.json").read_text(encoding="utf-8"))
            m02b_cap = json.loads((m02b_dir / "capacity_test_results_M02B.json").read_text(encoding="utf-8"))
            smoke_results[mid] = m02b_smk[mid]
            capacity_results[mid] = dict(m02b_cap[mid])
        else:
            smoke_results[mid] = {}
            capacity_results[mid] = {}

        progressed = True
        for st in stages:
            if not progressed:
                capacity_results[mid][st] = {"status": "NOT_EXECUTED", "reason": "Prior stage failed"}
                continue
            budget = refresh_available_resources(ROOT)
            if mon_gpu and budget.vram_budget_bytes <= 0:
                payload = {"status": "BLOCKED", "error": "Insufficient GPU VRAM budget"}
            else:
                res = run_monitored_subprocess(
                    [py_exe, wrk, "--model-id", mid, "--stage", st, "--n-threads", "16"],
                    timeout_sec=timeout_s,
                    cpu_threads=16,
                    ram_budget_bytes=budget.ram_budget_bytes,
                    vram_budget_bytes=budget.vram_budget_bytes,
                    monitor_gpu=mon_gpu,
                )
                payload = parse_worker_result(res)

            if st in ("L0", "L1"):
                smoke_results[mid][st] = payload
            else:
                capacity_results[mid][st] = payload

            print(f"  {mid} {st}: {payload['status']} (rss={payload.get('peak_rss_mb')} MiB, vram={payload.get('peak_cuda_allocated_mb')} MiB, wall={payload.get('subprocess_elapsed_sec')}s)", flush=True)
            if payload["status"] != "PASS":
                print(f"    -> Detail: {payload.get('error')}", flush=True)
                progressed = False

            resource_rows.append({
                "model_id": mid,
                "env": env_name,
                "stage": st,
                "status": payload["status"],
                "device_used": payload.get("metadata", {}).get("device_used", "N/A"),
                "checkpoint_load_time_sec": payload.get("checkpoint_load_time_sec"),
                "fit_context_time_sec": payload.get("fit_context_time_sec", payload.get("fit_time_sec")),
                "predict_time_sec": payload.get("predict_time_sec"),
                "subprocess_wall_sec": payload.get("subprocess_elapsed_sec"),
                "peak_rss_mb": payload.get("peak_rss_mb"),
                "peak_cuda_allocated_mb": payload.get("peak_cuda_allocated_mb"),
                "peak_cuda_reserved_mb": payload.get("peak_cuda_reserved_mb"),
                "violation_reason": payload.get("violation_reason"),
            })

    (run_dir / "smoke_test_results_M02C.json").write_text(json.dumps(smoke_results, indent=2), encoding="utf-8")
    (run_dir / "capacity_test_results_M02C.json").write_text(json.dumps(capacity_results, indent=2), encoding="utf-8")
    with (run_dir / "resource_usage_M02C.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(resource_rows[0].keys()))
        w.writeheader()
        w.writerows(resource_rows)

    ckpts = inventory_local_checkpoints(run_dir / "checkpoint_inventory_M02C.json")
    print(f"CHECKPOINT_INVENTORY: {len(ckpts)} local checkpoint files hashed", flush=True)

    # Record foundation context contracts
    ctx_contracts = {}
    for mid in ("FM01", "FM02", "FM03", "FM04"):
        st_l2c = capacity_results.get(mid, {}).get("L2C", {})
        st_l1 = smoke_results.get(mid, {}).get("L1", {})
        meta = st_l2c.get("metadata") or st_l1.get("metadata") or {}
        ctx_contracts[mid] = {
            "status_l1": st_l1.get("status"),
            "status_l2c": st_l2c.get("status"),
            "available_training_rows_tested": meta.get("available_training_rows"),
            "context_rows_per_query": meta.get("context_rows_per_query", "all_or_internal"),
            "internally_dropped_features": meta.get("internally_dropped_features", 0),
            "native_feature_reduction": meta.get("native_feature_reduction", "none"),
            "config": meta.get("config"),
        }
    (run_dir / "foundation_context_contracts.json").write_text(json.dumps(ctx_contracts, indent=2), encoding="utf-8")

    # Reconcile 32-candidate matrix (preserving M02A and M02B for other 25 candidates!)
    # Temporarily feed M02C results by merging into an effective matrix
    m02b_dir = ROOT / "reports/runs/M02B_20261125_081433_DESKTOP-CQB09OU"
    m02b_matrix = m02b_dir / "model_compatibility_matrix_M02B.csv"
    with m02b_matrix.open("r", encoding="utf-8") as f:
        base_rows = list(csv.DictReader(f))

    out_rows = []
    for row in base_rows:
        mid = row["id"]
        r = dict(row)
        if mid in smoke_results:
            l0 = smoke_results[mid].get("L0", {})
            l1 = smoke_results[mid].get("L1", {})
            cap = capacity_results.get(mid, {})
            l2a, l2b, l2c = cap.get("L2A", {}), cap.get("L2B", {}), cap.get("L2C", {})
            meta = l2c.get("metadata") or l1.get("metadata") or l0.get("metadata") or {}
            if all(x.get("status") == "PASS" for x in (l0, l1, l2a, l2b, l2c)):
                r["effective_runtime_status"] = "SCALE_CHECK_PASS"
            elif l1.get("status") == "PASS":
                r["effective_runtime_status"] = "SMOKE_TEST_PASS"
            elif l0.get("status") in ("BLOCKED_ACCESS", "BLOCKED_LICENSE") or l1.get("status") in ("BLOCKED_ACCESS", "BLOCKED_LICENSE"):
                r["effective_runtime_status"] = l1.get("status") if l1.get("status") in ("BLOCKED_ACCESS", "BLOCKED_LICENSE") else l0.get("status")
            else:
                r["effective_runtime_status"] = "FAILED"
            r["actual_implementation_tested"] = meta.get("estimator_class", r["target_estimator"])
            r["package_and_version"] = f"{meta.get('package', '')}=={meta.get('package_version', '')}"
            r["environment"] = meta.get("environment_name", r["environment"])
            r["device"] = meta.get("device_used", r["device"])
            r["l0_status"] = l0.get("status", "NOT_EXECUTED")
            r["l1_status"] = l1.get("status", "NOT_EXECUTED")
            r["l2a_status"] = l2a.get("status", "NOT_EXECUTED")
            r["l2b_status"] = l2b.get("status", "NOT_EXECUTED")
            r["l2c_status"] = l2c.get("status", "NOT_EXECUTED")
            r["tested_configuration"] = json.dumps(meta.get("config", {}))
            if l2c.get("status") == "PASS":
                r["max_tested_shape"] = "(12216, 501) -> (3822,)"
            elif l2b.get("status") == "PASS":
                r["max_tested_shape"] = "(4096, 501) -> (1024,)"
            elif l2a.get("status") == "PASS":
                r["max_tested_shape"] = "(1000, 501) -> (200,)"
            elif l1.get("status") == "PASS":
                r["max_tested_shape"] = "(100, 501) -> (20,)"
            else:
                r["max_tested_shape"] = "NONE"
            rss_v = l2c.get("peak_rss_mb") or l2b.get("peak_rss_mb") or l1.get("peak_rss_mb") or l0.get("peak_rss_mb")
            vram_v = l2c.get("peak_cuda_allocated_mb") or l1.get("peak_cuda_allocated_mb")
            r["memory_usage_summary"] = f"peak_rss={rss_v} MiB; peak_cuda_alloc={vram_v} MiB"
            ser = l1.get("serialization") or {}
            r["serialization_result"] = f"supported={ser.get('supported')}, diff={ser.get('max_reload_diff')}" if ser else "N/A"
            r["source_evidence"] = f"reports/runs/{args.run_id}"
            r["experimental_approval"] = "NOT_APPROVED"
        out_rows.append(r)

    with (run_dir / "model_compatibility_matrix_M02C.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    print("M02C_COMPATIBILITY_SUITE_COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
