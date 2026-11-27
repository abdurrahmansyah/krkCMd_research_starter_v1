"""
src/evaluation/experiment_runner.py

Reproducible cross-environment experiment runner interface for M04+ (M03 Section 13 / M04A Section 7).
Strictly blocks actual krkCMd data execution unless authorize_real_data_training=True
is explicitly supplied by an approved M04+ milestone, and prevents attempt-directory overwrites.
"""

from __future__ import annotations

import json
import os
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
    authorized_phase: str = "M04A_PROTOCOL_A_TRAIN_VAL"
    config_json_path: Optional[str] = None
    config_hash: Optional[str] = None
    timeout_sec: int = 3600
    cpu_threads: int = 16
    monitor_gpu: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _atomic_write_json(path: Path, payload: Dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def execute_experiment(spec: ExperimentSpec, out_dir: Path) -> Dict[str, Any]:
    """
    Validate authorization, reject attempt-directory overwrite, allocate unique attempt
    directory, enforce resource limits, and record prediction/metric/error metadata.
    """
    if not spec.authorize_real_data_training:
        raise PermissionError(
            f"Real-data training is NOT authorized for {spec.model_id}/{spec.config_id} "
            "(stop gate active)."
        )

    attempt_dir = out_dir / spec.run_id / spec.attempt_id
    if attempt_dir.exists() and (
        (attempt_dir / "runner_result.json").exists()
        or (attempt_dir / "worker_result.json").exists()
    ):
        raise FileExistsError(
            f"Attempt directory already contains completed artifacts: {attempt_dir}. "
            "Retries must allocate a new unique attempt_id."
        )

    attempt_dir.mkdir(parents=True, exist_ok=True)
    _atomic_write_json(attempt_dir / "experiment_spec.json", spec.to_dict())

    cmd = [
        spec.environment_executable,
        "-m",
        spec.worker_module,
        "--model-id",
        spec.model_id,
        "--config-id",
        spec.config_id,
        "--run-id",
        spec.run_id,
        "--attempt-id",
        spec.attempt_id,
        "--split-manifest",
        spec.split_manifest,
        "--seed",
        str(spec.seed),
        "--authorized-phase",
        spec.authorized_phase,
        "--out-dir",
        str(attempt_dir),
    ]
    if spec.config_json_path:
        cmd.extend(["--config-json", spec.config_json_path])

    budget = refresh_available_resources(ROOT)
    res = run_monitored_subprocess(
        cmd,
        timeout_sec=spec.timeout_sec,
        cpu_threads=spec.cpu_threads,
        ram_budget_bytes=budget.ram_budget_bytes,
        vram_budget_bytes=budget.vram_budget_bytes,
        monitor_gpu=spec.monitor_gpu,
        cwd=ROOT,
    )
    _atomic_write_json(attempt_dir / "runner_result.json", res)
    return res