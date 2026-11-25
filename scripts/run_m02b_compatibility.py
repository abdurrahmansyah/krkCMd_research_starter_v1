"""
scripts/run_m02b_compatibility.py

Authoritative M02B orchestrator:
  1. Verifies PyTorch GPU computation on cuda:0 (Turing sm_75: FP32 + FP16 AMP + SDPA)
  2. Executes isolated L0, L1, and progressive L2 (L2A/L2B/L2C) tests for M02B targets
  3. Records DL04 (TabR) transparently as CONDITIONAL (repo-only, no PyPI package)
  4. Reconciles the 32-candidate effective compatibility matrix without touching M02A/M00
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from build_compatibility_matrix import reconcile_effective_matrix  # noqa: E402
from resource_policy import refresh_available_resources, run_monitored_subprocess  # noqa: E402


def verify_gpu_runtime(deep_py: str, out_json: Path) -> dict:
    gpu_script = """
import json, time, torch
out = {
    "torch_version": torch.__version__,
    "torch_cuda_version": torch.version.cuda,
    "cuda_available": torch.cuda.is_available(),
    "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
    "arch_list": torch.cuda.get_arch_list() if hasattr(torch.cuda, "get_arch_list") else [],
}
if torch.cuda.is_available():
    out["gpu_name"] = torch.cuda.get_device_name(0)
    out["compute_capability"] = list(torch.cuda.get_device_capability(0))
    torch.cuda.reset_peak_memory_stats(0)
    t0 = time.perf_counter()
    # FP32 matmul + Conv1d forward/backward + optimizer update
    x = torch.randn((32, 1, 501), device="cuda:0", dtype=torch.float32)
    y = torch.randn((32, 1), device="cuda:0", dtype=torch.float32)
    conv = torch.nn.Conv1d(1, 16, kernel_size=5, padding=2).to("cuda:0")
    fc = torch.nn.Linear(16 * 501, 1).to("cuda:0")
    opt = torch.optim.AdamW(list(conv.parameters()) + list(fc.parameters()), lr=1e-3)
    h = torch.relu(conv(x)).flatten(1)
    pred = fc(h)
    loss = torch.nn.functional.mse_loss(pred, y)
    loss.backward()
    opt.step()
    torch.cuda.synchronize()
    out["fp32_elapsed_sec"] = round(time.perf_counter() - t0, 4)
    out["fp32_finite"] = bool(torch.isfinite(pred).all() and torch.isfinite(loss))

    # Small FP16 AMP test
    with torch.amp.autocast("cuda", dtype=torch.float16):
        pred_fp16 = fc(torch.relu(conv(x)).flatten(1))
    out["fp16_amp_finite"] = bool(torch.isfinite(pred_fp16).all())

    # Turing SDPA attention path check (math / mem_efficient, NOT flash_attention_2)
    q = torch.randn((4, 4, 32, 16), device="cuda:0", dtype=torch.float16)
    with torch.nn.attention.sdpa_kernel([torch.nn.attention.SDPBackend.MATH, torch.nn.attention.SDPBackend.EFFICIENT_ATTENTION]):
        attn_out = torch.nn.functional.scaled_dot_product_attention(q, q, q)
    out["sdpa_turing_finite"] = bool(torch.isfinite(attn_out).all())
    out["peak_cuda_allocated_mb"] = round(torch.cuda.max_memory_allocated(0) / (1024**2), 3)
    out["peak_cuda_reserved_mb"] = round(torch.cuda.max_memory_reserved(0) / (1024**2), 3)
    out["status"] = "GPU_PASS" if (out["fp32_finite"] and out["fp16_amp_finite"] and out["sdpa_turing_finite"]) else "GPU_FAILED"
else:
    out["status"] = "CPU_ONLY"
print(json.dumps(out))
"""
    res = run_monitored_subprocess([deep_py, "-c", gpu_script], timeout_sec=120, cpu_threads=16, monitor_gpu=True)
    data = json.loads(res["stdout"].strip().splitlines()[-1]) if res["stdout"].strip() else {"status": "FAILED", "stderr": res["stderr"][-800:]}
    data["subprocess_elapsed_sec"] = res["elapsed_sec"]
    data["peak_rss_mb"] = res["peak_rss_mb"]
    out_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def main() -> int:
    run_dir = ROOT / "reports" / "runs" / "M02B_20261125_081433_DESKTOP-CQB09OU"
    deep_py = str(ROOT / ".venv-deep" / "Scripts" / "python.exe")
    tf_py = str(ROOT / ".venv-signal-tf" / "Scripts" / "python.exe")
    hydra_py = str(ROOT / ".venv-signal-hydra" / "Scripts" / "python.exe")
    worker = str(ROOT / "src" / "evaluation" / "m02b_compat_worker.py")

    print("=== 1. GPU Runtime Verification ===", flush=True)
    gpu_res = verify_gpu_runtime(deep_py, run_dir / "gpu_runtime_verification_M02B.json")
    print("GPU_STATUS:", gpu_res.get("status"), gpu_res.get("gpu_name"), "CC:", gpu_res.get("compute_capability"), flush=True)

    targets = [
        ("DL01", deep_py, ".venv-deep", 900, True),
        ("DL02", deep_py, ".venv-deep", 900, True),
        ("DL03", deep_py, ".venv-deep", 900, True),
        ("DL05", deep_py, ".venv-deep", 900, True),
        ("SG01", deep_py, ".venv-deep", 900, True),
        ("RF05", deep_py, ".venv-deep", 900, True),
        ("SG02", tf_py, ".venv-signal-tf", 300, False),
        ("SG03", tf_py, ".venv-signal-tf", 300, False),
        ("SG04", tf_py, ".venv-signal-tf", 300, False),
        ("SG06", hydra_py, ".venv-signal-hydra", 300, False),
    ]

    smoke_results = {}
    capacity_results = {}
    resource_rows = []

    for mid, py_exe, env_name, stage_timeout, mon_gpu in targets:
        print(f"\n=== Testing {mid} ({env_name}) ===", flush=True)
        smoke_results[mid] = {}
        capacity_results[mid] = {}
        progressed = True

        for stage in ("L0", "L1"):
            budget = refresh_available_resources(ROOT)
            res = run_monitored_subprocess(
                [py_exe, worker, "--model-id", mid, "--stage", stage, "--n-threads", "16"],
                timeout_sec=stage_timeout,
                cpu_threads=16,
                ram_budget_bytes=budget.ram_budget_bytes,
                vram_budget_bytes=budget.vram_budget_bytes,
                monitor_gpu=mon_gpu,
            )
            payload = json.loads(res["stdout"].strip().splitlines()[-1]) if res["stdout"].strip() else {"status": "FAILED", "error": res["stderr"][-500:]}
            if res["returncode"] != 0 and payload.get("status") == "PASS":
                payload["status"] = "FAILED"
                payload["error"] = res.get("violation_reason") or f"Non-zero exit {res['returncode']}"
            payload["peak_rss_mb"] = res["peak_rss_mb"]
            payload["subprocess_elapsed_sec"] = res["elapsed_sec"]
            payload["violation_reason"] = res["violation_reason"]
            smoke_results[mid][stage] = payload
            print(f"  {mid} {stage}: {payload['status']} (rss={res['peak_rss_mb']} MiB, wall={res['elapsed_sec']}s)", flush=True)
            resource_rows.append({
                "model_id": mid,
                "env": env_name,
                "stage": stage,
                "status": payload["status"],
                "device_used": payload.get("metadata", {}).get("device_used", "N/A"),
                "fit_time_sec": payload.get("fit_time_sec"),
                "predict_time_sec": payload.get("predict_time_sec"),
                "subprocess_wall_sec": res["elapsed_sec"],
                "peak_rss_mb": res["peak_rss_mb"],
                "peak_cuda_allocated_mb": payload.get("peak_cuda_allocated_mb"),
                "peak_cuda_reserved_mb": payload.get("peak_cuda_reserved_mb"),
                "violation_reason": res["violation_reason"],
            })
            if payload["status"] != "PASS":
                progressed = False
                break

        for stage in ("L2A", "L2B", "L2C"):
            if not progressed:
                capacity_results[mid][stage] = {"status": "NOT_EXECUTED", "reason": "Prior stage failed"}
                continue
            budget = refresh_available_resources(ROOT)
            res = run_monitored_subprocess(
                [py_exe, worker, "--model-id", mid, "--stage", stage, "--n-threads", "16"],
                timeout_sec=stage_timeout,
                cpu_threads=16,
                ram_budget_bytes=budget.ram_budget_bytes,
                vram_budget_bytes=budget.vram_budget_bytes,
                monitor_gpu=mon_gpu,
            )
            payload = json.loads(res["stdout"].strip().splitlines()[-1]) if res["stdout"].strip() else {"status": "FAILED", "error": res["stderr"][-500:]}
            if res["returncode"] != 0 and payload.get("status") == "PASS":
                payload["status"] = "FAILED"
                payload["error"] = res.get("violation_reason") or f"Non-zero exit {res['returncode']}"
            payload["peak_rss_mb"] = res["peak_rss_mb"]
            payload["subprocess_elapsed_sec"] = res["elapsed_sec"]
            payload["violation_reason"] = res["violation_reason"]
            capacity_results[mid][stage] = payload
            print(f"  {mid} {stage}: {payload['status']} (fit={payload.get('fit_time_sec')}s, pred={payload.get('predict_time_sec')}s, rss={res['peak_rss_mb']} MiB, vram={payload.get('peak_cuda_allocated_mb')} MiB)", flush=True)
            resource_rows.append({
                "model_id": mid,
                "env": env_name,
                "stage": stage,
                "status": payload["status"],
                "device_used": payload.get("metadata", {}).get("device_used", "N/A"),
                "fit_time_sec": payload.get("fit_time_sec"),
                "predict_time_sec": payload.get("predict_time_sec"),
                "subprocess_wall_sec": res["elapsed_sec"],
                "peak_rss_mb": res["peak_rss_mb"],
                "peak_cuda_allocated_mb": payload.get("peak_cuda_allocated_mb"),
                "peak_cuda_reserved_mb": payload.get("peak_cuda_reserved_mb"),
                "violation_reason": res["violation_reason"],
            })
            if payload["status"] != "PASS":
                progressed = False

    # Record DL04 (TabR) transparently as CONDITIONAL (repo-only, no PyPI wheel)
    smoke_results["DL04"] = {
        "L0": {
            "model_id": "DL04",
            "stage": "L0",
            "status": "CONDITIONAL",
            "metadata": {
                "model_id": "DL04",
                "environment_name": "N/A (repo-only yandex-research/tabular-dl-tabr @ 17baa908)",
                "package": "tabular-dl-tabr (non-PyPI)",
                "package_version": "commit 17baa9082506f8e7a0f8d11bb1e08212926a1507",
                "estimator_class": "yandex-research/tabular-dl-tabr",
                "device_used": "NOT_EXECUTED",
                "limitation": "Not packaged on PyPI; requires dedicated repo/FAISS integration in .venv-tabr without generic KNN substitution.",
            },
        },
        "L1": {"status": "NOT_EXECUTED"},
    }
    capacity_results["DL04"] = {s: {"status": "NOT_EXECUTED"} for s in ("L2A", "L2B", "L2C")}

    (run_dir / "smoke_test_results_M02B.json").write_text(json.dumps(smoke_results, indent=2), encoding="utf-8")
    (run_dir / "capacity_test_results_M02B.json").write_text(json.dumps(capacity_results, indent=2), encoding="utf-8")

    with (run_dir / "resource_usage_M02B.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(resource_rows[0].keys()))
        w.writeheader()
        w.writerows(resource_rows)

    reconcile_effective_matrix(
        registry_path=ROOT / "configs" / "model_registry.yaml",
        m01_1_matrix_path=ROOT / "reports" / "tables" / "model_compatibility_matrix_M01_1.csv",
        m02a_run_dir=ROOT / "reports" / "runs" / "M02A_20261125_074616_DESKTOP-CQB09OU",
        m02b_run_dir=run_dir,
        out_csv=run_dir / "model_compatibility_matrix_M02B.csv",
    )
    print("M02B_COMPATIBILITY_SUITE_COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
