"""
scripts/run_m04a_screening.py

Orchestrates M04A staged screening (Stage A Pilot -> Stage B Remaining -> Stage C Historical Refs).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from evaluation.experiment_runner import ExperimentSpec, execute_experiment  # noqa: E402


ENV_EXECS = {
    ".venv": ROOT / ".venv" / "Scripts" / "python.exe",
    ".venv-boost": ROOT / ".venv-boost" / "Scripts" / "python.exe",
    ".venv-deep": ROOT / ".venv-deep" / "Scripts" / "python.exe",
    ".venv-tabr": ROOT / ".venv-tabr" / "Scripts" / "python.exe",
    ".venv-signal-cpu": ROOT / ".venv-signal-cpu" / "Scripts" / "python.exe",
    ".venv-signal-tf": ROOT / ".venv-signal-tf" / "Scripts" / "python.exe",
    ".venv-signal-hydra": ROOT / ".venv-signal-hydra" / "Scripts" / "python.exe",
    ".venv-foundation": ROOT / ".venv-foundation" / "Scripts" / "python.exe",
}

STAGE_A = ["RF01", "ML01", "DL01", "SG01", "FM03"]
STAGE_B = [
    "RF02", "ML02", "ML03", "ML04", "ML05", "ML06", "ML07",
    "DL02", "DL03", "DL04", "DL05",
    "SG02", "SG03", "SG04", "SG05", "SG06",
    "RF05", "FM04",
]


def run_models(run_dir: Path, models: List[str], timeout_sec: int = 3600) -> List[Dict[str, Any]]:
    cfg_all = yaml.safe_load((run_dir / "M04A_SCIENTIFIC_CONFIGURATIONS.yaml").read_text(encoding="utf-8"))
    run_id = run_dir.name
    split_manifest = str(ROOT / "reports" / "tables" / "group_split_manifest.csv")
    runs_root = ROOT / "reports" / "runs"

    results = []
    for mid in models:
        mcfg = cfg_all["models"][mid]
        sci_cfg = mcfg["scientific_v1"]
        env_key = mcfg["environment"]
        py_exec = str(ENV_EXECS[env_key])
        base_attempt = f"attempts/M04A_{mid}_scientific_v1_s42"
        attempt_id = base_attempt
        attempt_dir = run_dir / attempt_id
        idx = 2
        while attempt_dir.exists():
            attempt_id = f"{base_attempt}_r{idx}"
            attempt_dir = run_dir / attempt_id
            idx += 1
        attempt_dir.mkdir(parents=True, exist_ok=True)

        cfg_json_path = attempt_dir / "scientific_v1_config.json"
        cfg_bytes = json.dumps(sci_cfg, sort_keys=True, indent=2).encode("utf-8")
        cfg_json_path.write_bytes(cfg_bytes)
        cfg_hash = hashlib.sha256(cfg_bytes).hexdigest().upper()

        spec = ExperimentSpec(
            model_id=mid,
            config_id="scientific_v1",
            run_id=run_id,
            attempt_id=attempt_id,
            split_manifest=split_manifest,
            seed=42,
            environment_executable=py_exec,
            worker_module="src.evaluation.m04a_scientific_worker",
            authorize_real_data_training=True,
            authorized_phase="M04A_PROTOCOL_A_TRAIN_VAL",
            config_json_path=str(cfg_json_path),
            config_hash=cfg_hash,
            timeout_sec=timeout_sec,
            cpu_threads=16,
            monitor_gpu=(mcfg["device"] == "cuda:0"),
        )
        print(f"=== STARTING {mid} ({env_key}, device={mcfg['device']}) ===", flush=True)
        res = execute_experiment(spec, runs_root)
        worker_ok = (attempt_dir / "worker_result.json").exists()
        status = "PASS" if (res.get("returncode") == 0 and worker_ok and not res.get("violation_reason")) else "FAILED"
        print(f"=== FINISHED {mid}: {status} (rc={res.get('returncode')}, wall={res.get('elapsed_sec')}s, err={res.get('violation_reason')}) ===", flush=True)
        results.append({"model_id": mid, "status": status, "runner_result": res})
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--stage", choices=["A", "B", "ALL"], required=True)
    parser.add_argument("--models", nargs="*", default=None)
    parser.add_argument("--timeout-sec", type=int, default=3600)
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    if args.models:
        targets = args.models
    elif args.stage == "A":
        targets = STAGE_A
    elif args.stage == "B":
        targets = STAGE_B
    else:
        targets = STAGE_A + STAGE_B

    out = run_models(run_dir, targets, timeout_sec=args.timeout_sec)
    summary_path = run_dir / f"stage_{args.stage}_summary.json"
    summary_path.write_text(json.dumps(out, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
