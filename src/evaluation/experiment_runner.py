"""
src/evaluation/experiment_runner.py

Reproducible cross-environment experiment runner interface for M04+ (M03 Section 13).
Strictly blocks actual krkCMd data execution unless authorize_real_data_training=True
is explicitly supplied by an approved M04+ milestone.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from resource_policy import refresh_available_resources, run_monitored_subprocess  # noqa: E402


@dataclass(frozen=True)
class ExperimentSpec:
    model_id: str
    config_id: str
    run_id: str
    attempt_id: str
    split_manifest: str
    seed: int
    environment_executable: str
    worker_module: str
    authorize_real_data_training: bool = False
    timeout_sec: int = 900
    cpu_threads: int = 16
    monitor_gpu: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def execute_experiment(spec: ExperimentSpec, out_dir: Path) -> Dict[str, Any]:
    """
    Validate authorization, allocate unique attempt directory, enforce resource
    limits, and record prediction/metric/error metadata.
    """
    if not spec.authorize_real_data_training:
        raise PermissionError(
            f"Real-data training is NOT authorized for {spec.model_id}/{spec.config_id} "
            "(M03 stop gate active)."
        )

    attempt_dir = out_dir / spec.run_id / spec.attempt_id
    attempt_dir.mkdir(parents=True, exist_ok=True)
    (attempt_dir / "experiment_spec.json").write_text(json.dumps(spec.to_dict(), indent=2), encoding="utf-8")

    budget = refresh_available_resources(ROOT)
    res = run_monitored_subprocess(
        [
            spec.environment_executable,
            "-m",
            spec.worker_module,
            "--model-id",
            spec.model_id,
            "--config-id",
            spec.config_id,
            "--split-manifest",
            spec.split_manifest,
            "--seed",
            str(spec.seed),
            "--out-dir",
            str(attempt_dir),
        ],
        timeout_sec=spec.timeout_sec,
        cpu_threads=spec.cpu_threads,
        ram_budget_bytes=budget.ram_budget_bytes,
        vram_budget_bytes=budget.vram_budget_bytes,
        monitor_gpu=spec.monitor_gpu,
    )
    (attempt_dir / "runner_result.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    return res
