"""
scripts/resource_policy.py

Provisional dynamic resource safety policy, thread controls, and subprocess
monitoring interfaces for krkCMd compatibility testing (M01.1 Section O).
"""

from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Sequence

import psutil

BYTES_PER_GB = 1_000_000_000
BYTES_PER_GIB = 1024 ** 3


@dataclass(frozen=True)
class ResourceBudget:
    """Computed provisional safety budgets in decimal GB (and GiB reference)."""

    available_ram_gb: float
    available_vram_gb: float
    available_disk_gb: float
    ram_budget_gb: float
    vram_budget_gb: float
    initial_env_cache_budget_gb: float
    max_concurrent_workers: int = 1
    max_gpu_workers: int = 1
    default_cpu_threads: int = 16
    classical_timeout_sec: int = 300
    deep_timeout_sec: int = 900
    unit_basis: str = "GB (decimal 10^9 bytes); GiB = 2^30 bytes"

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def compute_dynamic_budgets(
    available_ram_gb: float,
    available_vram_gb: float,
    available_disk_gb: float,
    logical_cores: Optional[int] = None,
) -> ResourceBudget:
    """
    Compute provisional dynamic safety budgets per M01.1 Section O:
      - Reserve >= 16 GB available host RAM, cap at 64 GB, or 70% of available RAM.
      - Reserve >= 2.5 GB available GPU VRAM, cap at 20 GB, or 85% of available VRAM.
      - Reserve >= 100 GB free disk space, cap initial env+cache budget at 30 GB.
    """
    ram_budget = max(0.0, min(64.0, 0.70 * available_ram_gb, available_ram_gb - 16.0))
    vram_budget = max(0.0, min(20.0, 0.85 * available_vram_gb, available_vram_gb - 2.5))
    disk_budget = max(0.0, min(30.0, available_disk_gb - 100.0))

    cpu_threads = 16
    if logical_cores is not None and logical_cores > 0:
        cpu_threads = max(1, min(16, logical_cores - 4 if logical_cores > 4 else logical_cores))

    return ResourceBudget(
        available_ram_gb=round(available_ram_gb, 3),
        available_vram_gb=round(available_vram_gb, 3),
        available_disk_gb=round(available_disk_gb, 3),
        ram_budget_gb=round(ram_budget, 3),
        vram_budget_gb=round(vram_budget, 3),
        initial_env_cache_budget_gb=round(disk_budget, 3),
        default_cpu_threads=cpu_threads,
    )


def build_thread_env(cpu_threads: int = 16, base_env: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """Return environment dictionary with explicit BLAS/OpenMP thread controls."""
    env = dict(os.environ if base_env is None else base_env)
    val = str(max(1, int(cpu_threads)))
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        env[var] = val
    return env


def query_gpu_vram_usage() -> Optional[Dict[str, float]]:
    """Query current GPU VRAM usage in MiB/GB via nvidia-smi if available."""
    try:
        res = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total,memory.free,memory.used,utilization.gpu", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res.returncode != 0 or not res.stdout.strip():
            return None
        parts = [float(x.strip()) for x in res.stdout.strip().splitlines()[0].split(",")]
        return {
            "vram_total_mib": parts[0],
            "vram_free_mib": parts[1],
            "vram_used_mib": parts[2],
            "gpu_util_percent": parts[3],
            "vram_free_gb": round((parts[1] * 1048576.0) / BYTES_PER_GB, 3),
        }
    except Exception:
        return None


def terminate_process_tree(pid: int) -> None:
    """Terminate a process and all its children safely."""
    try:
        parent = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return
    children = parent.children(recursive=True)
    for child in children:
        try:
            child.terminate()
        except psutil.NoSuchProcess:
            pass
    try:
        parent.terminate()
    except psutil.NoSuchProcess:
        return
    _, alive = psutil.wait_procs(children + [parent], timeout=3)
    for p in alive:
        try:
            p.kill()
        except psutil.NoSuchProcess:
            pass


def run_monitored_subprocess(
    cmd: Sequence[str],
    timeout_sec: int = 300,
    cpu_threads: int = 16,
    poll_interval_sec: float = 0.2,
    cwd: Optional[str] = None,
) -> Dict[str, object]:
    """
    Execute a subprocess with explicit thread controls, wall-clock timeout,
    process-tree termination on timeout, and peak child RSS monitoring.
    """
    env = build_thread_env(cpu_threads=cpu_threads)
    t0 = time.monotonic()
    proc = subprocess.Popen(
        list(cmd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        cwd=cwd,
    )
    peak_rss_bytes = 0
    timed_out = False

    while True:
        ret = proc.poll()
        try:
            p = psutil.Process(proc.pid)
            rss = p.memory_info().rss
            for ch in p.children(recursive=True):
                try:
                    rss += ch.memory_info().rss
                except psutil.NoSuchProcess:
                    pass
            if rss > peak_rss_bytes:
                peak_rss_bytes = rss
        except psutil.NoSuchProcess:
            pass

        if ret is not None:
            break
        if (time.monotonic() - t0) >= timeout_sec:
            timed_out = True
            terminate_process_tree(proc.pid)
            break
        time.sleep(poll_interval_sec)

    stdout, stderr = proc.communicate()
    elapsed = round(time.monotonic() - t0, 3)
    return {
        "returncode": -1 if timed_out else proc.returncode,
        "timed_out": timed_out,
        "elapsed_sec": elapsed,
        "peak_rss_mb": round(peak_rss_bytes / (1024 * 1024), 3),
        "stdout": stdout,
        "stderr": stderr,
    }
