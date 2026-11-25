"""
scripts/resource_policy.py

Provisional dynamic resource safety policy, thread controls, and subprocess
watchdog with active RAM/VRAM/timeout enforcement (M01.1 Section O & M02B Section 2).

Internal units: bytes (with MiB/GiB helpers for reporting).
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Dict, Optional, Sequence

import psutil

BYTES_PER_MIB = 1024 ** 2
BYTES_PER_GIB = 1024 ** 3
BYTES_PER_GB = 1_000_000_000


@dataclass(frozen=True)
class ResourceBudget:
    """Computed provisional safety budgets (bytes internal, GiB/GB reported)."""

    available_ram_bytes: int
    available_vram_bytes: int
    available_disk_bytes: int
    ram_budget_bytes: int
    vram_budget_bytes: int
    env_cache_budget_bytes: int
    ram_reserve_bytes: int = 16 * BYTES_PER_GIB
    vram_reserve_bytes: int = int(2.5 * BYTES_PER_GIB)
    disk_reserve_bytes: int = 100 * BYTES_PER_GIB
    max_concurrent_workers: int = 1
    max_gpu_workers: int = 1
    default_cpu_threads: int = 16
    classical_timeout_sec: int = 300
    deep_timeout_sec: int = 900

    # GiB reporting properties
    @property
    def ram_budget_gib(self) -> float:
        return round(self.ram_budget_bytes / BYTES_PER_GIB, 3)

    @property
    def vram_budget_gib(self) -> float:
        return round(self.vram_budget_bytes / BYTES_PER_GIB, 3)

    @property
    def env_cache_budget_gib(self) -> float:
        return round(self.env_cache_budget_bytes / BYTES_PER_GIB, 3)

    # Backward-compatible GB-named attributes for existing callers/tests
    @property
    def ram_budget_gb(self) -> float:
        return self.ram_budget_gib

    @property
    def vram_budget_gb(self) -> float:
        return self.vram_budget_gib

    @property
    def initial_env_cache_budget_gb(self) -> float:
        return self.env_cache_budget_gib

    def to_dict(self) -> Dict[str, object]:
        d = asdict(self)
        d["ram_budget_gib"] = self.ram_budget_gib
        d["vram_budget_gib"] = self.vram_budget_gib
        d["env_cache_budget_gib"] = self.env_cache_budget_gib
        return d


def compute_dynamic_budgets(
    available_ram_gb: float,
    available_vram_gb: float,
    available_disk_gb: float,
    logical_cores: Optional[int] = None,
) -> ResourceBudget:
    """
    Compute provisional dynamic safety budgets using consistent GiB (2^30 bytes):
      - Reserve >= 16 GiB available host RAM, cap at 64 GiB, or 70% of available RAM.
      - Reserve >= 2.5 GiB available GPU VRAM, cap at 20 GiB, or 85% of available VRAM.
      - Reserve >= 100 GiB free disk space, cap env+cache budget at 30 GiB.
    """
    ram_budget_gib = max(0.0, min(64.0, 0.70 * available_ram_gb, available_ram_gb - 16.0))
    vram_budget_gib = max(0.0, min(20.0, 0.85 * available_vram_gb, available_vram_gb - 2.5))
    disk_budget_gib = max(0.0, min(30.0, available_disk_gb - 100.0))

    cpu_threads = 16
    if logical_cores is not None and logical_cores > 0:
        cpu_threads = max(1, min(16, logical_cores - 4 if logical_cores > 4 else logical_cores))

    return ResourceBudget(
        available_ram_bytes=int(max(0.0, available_ram_gb) * BYTES_PER_GIB),
        available_vram_bytes=int(max(0.0, available_vram_gb) * BYTES_PER_GIB),
        available_disk_bytes=int(max(0.0, available_disk_gb) * BYTES_PER_GIB),
        ram_budget_bytes=int(ram_budget_gib * BYTES_PER_GIB),
        vram_budget_bytes=int(vram_budget_gib * BYTES_PER_GIB),
        env_cache_budget_bytes=int(disk_budget_gib * BYTES_PER_GIB),
        default_cpu_threads=cpu_threads,
    )


def build_thread_env(cpu_threads: int = 16, base_env: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """Return environment dictionary with explicit BLAS/OpenMP/Numba thread controls."""
    env = dict(os.environ if base_env is None else base_env)
    val = str(max(1, int(cpu_threads)))
    for var in (
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
        "NUMBA_NUM_THREADS",
    ):
        env[var] = val
    return env


def query_gpu_vram_usage() -> Optional[Dict[str, float]]:
    """Query current GPU VRAM usage in bytes/MiB/GiB via nvidia-smi if available."""
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
            "vram_free_bytes": int(parts[1] * BYTES_PER_MIB),
            "vram_used_bytes": int(parts[2] * BYTES_PER_MIB),
            "vram_free_gib": round(parts[1] / 1024.0, 3),
        }
    except Exception:
        return None


def refresh_available_resources(root: Optional[Path] = None) -> ResourceBudget:
    """Measure live RAM, VRAM, and disk and return current ResourceBudget."""
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage(str((root or Path(".")).resolve()))
    gpu = query_gpu_vram_usage()
    avail_vram_gib = (gpu["vram_free_bytes"] / BYTES_PER_GIB) if gpu else 0.0
    return compute_dynamic_budgets(
        available_ram_gb=mem.available / BYTES_PER_GIB,
        available_vram_gb=avail_vram_gib,
        available_disk_gb=disk.free / BYTES_PER_GIB,
        logical_cores=psutil.cpu_count(logical=True),
    )


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


def check_resource_limits(
    proc_rss_bytes: int,
    sys_avail_ram_bytes: int,
    ram_budget_bytes: int,
    ram_reserve_bytes: int,
    gpu_used_delta_bytes: int = 0,
    sys_free_vram_bytes: Optional[int] = None,
    vram_budget_bytes: Optional[int] = None,
    vram_reserve_bytes: int = int(2.5 * BYTES_PER_GIB),
) -> Optional[str]:
    """Return explicit violation reason string if any safety limit is breached, else None."""
    if ram_budget_bytes > 0 and proc_rss_bytes > ram_budget_bytes:
        return f"PROCESS_RAM_BUDGET_EXCEEDED ({proc_rss_bytes / BYTES_PER_MIB:.1f} MiB > {ram_budget_bytes / BYTES_PER_MIB:.1f} MiB)"
    if sys_avail_ram_bytes < ram_reserve_bytes:
        return f"SYSTEM_RAM_RESERVE_BREACHED ({sys_avail_ram_bytes / BYTES_PER_GIB:.2f} GiB < {ram_reserve_bytes / BYTES_PER_GIB:.2f} GiB)"
    if vram_budget_bytes is not None and vram_budget_bytes > 0 and gpu_used_delta_bytes > vram_budget_bytes:
        return f"GPU_VRAM_BUDGET_EXCEEDED ({gpu_used_delta_bytes / BYTES_PER_MIB:.1f} MiB > {vram_budget_bytes / BYTES_PER_MIB:.1f} MiB)"
    if sys_free_vram_bytes is not None and sys_free_vram_bytes < vram_reserve_bytes:
        return f"GPU_VRAM_RESERVE_BREACHED ({sys_free_vram_bytes / BYTES_PER_GIB:.2f} GiB < {vram_reserve_bytes / BYTES_PER_GIB:.2f} GiB)"
    return None


def run_monitored_subprocess(
    cmd: Sequence[str],
    timeout_sec: int = 300,
    cpu_threads: int = 16,
    poll_interval_sec: float = 0.2,
    cwd: Optional[str] = None,
    ram_budget_bytes: Optional[int] = None,
    ram_reserve_bytes: int = 16 * BYTES_PER_GIB,
    vram_budget_bytes: Optional[int] = None,
    vram_reserve_bytes: int = int(2.5 * BYTES_PER_GIB),
    monitor_gpu: bool = False,
    ram_probe: Optional[Callable[[], int]] = None,
) -> Dict[str, object]:
    """
    Execute a subprocess with:
      - explicit BLAS/OpenMP/Numba thread controls before framework import
      - log files (not PIPE) to prevent stdout/stderr pipe deadlock
      - wall-clock timeout enforcement
      - active process-tree RAM and system RAM/VRAM reserve enforcement
      - process-tree termination on timeout or resource limit violation
    """
    env = build_thread_env(cpu_threads=cpu_threads)
    if ram_budget_bytes is None:
        live = refresh_available_resources()
        ram_budget_bytes = live.ram_budget_bytes
        if vram_budget_bytes is None:
            vram_budget_bytes = live.vram_budget_bytes

    baseline_gpu = query_gpu_vram_usage() if monitor_gpu else None
    baseline_vram_used = baseline_gpu["vram_used_bytes"] if baseline_gpu else 0

    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "stdout.log"
        err_path = Path(tmpdir) / "stderr.log"
        with out_path.open("w+", encoding="utf-8") as fout, err_path.open("w+", encoding="utf-8") as ferr:
            t0 = time.monotonic()
            proc = subprocess.Popen(
                list(cmd),
                stdout=fout,
                stderr=ferr,
                text=True,
                env=env,
                cwd=cwd,
            )
            peak_rss_bytes = 0
            peak_vram_delta_bytes = 0
            timed_out = False
            violation_reason: Optional[str] = None

            while True:
                ret = proc.poll()
                rss = 0
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

                sys_avail_ram = ram_probe() if ram_probe is not None else psutil.virtual_memory().available
                sys_free_vram = None
                vram_delta = 0
                if monitor_gpu:
                    g = query_gpu_vram_usage()
                    if g:
                        sys_free_vram = int(g["vram_free_bytes"])
                        vram_delta = max(0, int(g["vram_used_bytes"]) - int(baseline_vram_used))
                        if vram_delta > peak_vram_delta_bytes:
                            peak_vram_delta_bytes = vram_delta

                if ret is not None:
                    break

                violation_reason = check_resource_limits(
                    proc_rss_bytes=rss,
                    sys_avail_ram_bytes=sys_avail_ram,
                    ram_budget_bytes=ram_budget_bytes,
                    ram_reserve_bytes=ram_reserve_bytes,
                    gpu_used_delta_bytes=vram_delta,
                    sys_free_vram_bytes=sys_free_vram,
                    vram_budget_bytes=vram_budget_bytes,
                    vram_reserve_bytes=vram_reserve_bytes,
                )
                if violation_reason is not None:
                    terminate_process_tree(proc.pid)
                    break

                if (time.monotonic() - t0) >= timeout_sec:
                    timed_out = True
                    violation_reason = f"WALL_CLOCK_TIMEOUT ({timeout_sec}s)"
                    terminate_process_tree(proc.pid)
                    break

                time.sleep(poll_interval_sec)

            proc.wait()
            elapsed = round(time.monotonic() - t0, 3)
            fout.seek(0)
            ferr.seek(0)
            stdout_txt = fout.read()
            stderr_txt = ferr.read()

    return {
        "returncode": -1 if (timed_out or violation_reason is not None) else proc.returncode,
        "timed_out": timed_out,
        "violation_reason": violation_reason,
        "elapsed_sec": elapsed,
        "peak_rss_bytes": peak_rss_bytes,
        "peak_rss_mb": round(peak_rss_bytes / BYTES_PER_MIB, 3),
        "peak_vram_delta_bytes": peak_vram_delta_bytes,
        "peak_vram_delta_mib": round(peak_vram_delta_bytes / BYTES_PER_MIB, 3),
        "stdout": stdout_txt,
        "stderr": stderr_txt,
    }
