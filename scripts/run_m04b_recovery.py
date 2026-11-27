"""
scripts/run_m04b_recovery.py

Executes exactly one authorized recovery attempt each for SG02 (10,800s),
SG03 (10,800s), and FM04 (7,200s) using exact M04A scientific_v1 configurations.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from evaluation.experiment_runner import ExperimentSpec, execute_experiment  # noqa: E402


RECOVERY_SPECS = {
    "FM04": {
        "env": ROOT / ".venv-foundation" / "Scripts" / "python.exe",
        "timeout_sec": 7200,
        "monitor_gpu": True,
        "decision": "D-010B",
    },
    "SG02": {
        "env": ROOT / ".venv-signal-tf" / "Scripts" / "python.exe",
        "timeout_sec": 10800,
        "monitor_gpu": False,
        "decision": "D-010A",
    },
    "SG03": {
        "env": ROOT / ".venv-signal-tf" / "Scripts" / "python.exe",
        "timeout_sec": 10800,
        "monitor_gpu": False,
        "decision": "D-010A",
    },
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--m04a-dir", required=True)
    parser.add_argument("--models", nargs="+", default=["FM04", "SG02", "SG03"])
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    m04a_dir = Path(args.m04a_dir)
    run_id = run_dir.name
    runs_root = ROOT / "reports" / "runs"
    split_manifest = str(ROOT / "reports" / "tables" / "group_split_manifest.csv")

    cfg_all = yaml.safe_load((m04a_dir / "M04A_SCIENTIFIC_CONFIGURATIONS.yaml").read_text(encoding="utf-8"))
    attempts_log: Dict[str, Any] = {}

    for mid in args.models:
        if mid not in RECOVERY_SPECS:
            raise ValueError(f"Unauthorized recovery model: {mid}")
        rspec = RECOVERY_SPECS[mid]
        mcfg = cfg_all["models"][mid]
        sci_cfg = mcfg["scientific_v1"]

        attempt_id = f"attempts/M04B_{mid}_scientific_v1_s42_recovery1"
        attempt_dir = run_dir / attempt_id
        if attempt_dir.exists():
            raise FileExistsError(f"Recovery attempt already exists (max 1 attempt allowed): {attempt_dir}")
        attempt_dir.mkdir(parents=True, exist_ok=False)

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
            environment_executable=str(rspec["env"]),
            worker_module="src.evaluation.m04a_scientific_worker",
            authorize_real_data_training=True,
            authorized_phase="M04A_PROTOCOL_A_TRAIN_VAL",
            config_json_path=str(cfg_json_path),
            config_hash=cfg_hash,
            timeout_sec=int(rspec["timeout_sec"]),
            cpu_threads=16,
            monitor_gpu=bool(rspec["monitor_gpu"]),
        )

        start_utc = datetime.now(timezone.utc).isoformat()
        print(f"=== RECOVERY START {mid} (timeout={rspec['timeout_sec']}s, decision={rspec['decision']}) ===", flush=True)
        res = execute_experiment(spec, runs_root)
        end_utc = datetime.now(timezone.utc).isoformat()

        worker_ok = (attempt_dir / "worker_result.json").exists()
        status = (
            "PASS"
            if (
                res.get("returncode") == 0
                and worker_ok
                and not res.get("timed_out")
                and not res.get("suspend_detected")
                and res.get("violation_reason") is None
            )
            else "FAILED"
        )
        print(
            f"=== RECOVERY END {mid}: {status} (rc={res.get('returncode')}, wall={res.get('elapsed_sec')}s, "
            f"suspend={res.get('suspend_detected')}, err={res.get('violation_reason')}) ===",
            flush=True,
        )
        attempts_log[mid] = {
            "decision": rspec["decision"],
            "attempt_id": attempt_id,
            "start_utc": start_utc,
            "end_utc": end_utc,
            "timeout_limit_sec": rspec["timeout_sec"],
            "config_sha256": cfg_hash,
            "status": status,
            "runner_summary": {
                "returncode": res.get("returncode"),
                "timed_out": res.get("timed_out"),
                "suspend_detected": res.get("suspend_detected"),
                "max_poll_gap_sec": res.get("max_poll_gap_sec"),
                "violation_reason": res.get("violation_reason"),
                "elapsed_sec": res.get("elapsed_sec"),
                "peak_rss_mb": res.get("peak_rss_mb"),
                "peak_vram_delta_mib": res.get("peak_vram_delta_mib"),
            },
        }
        (run_dir / "M04B_RECOVERY_ATTEMPTS.json").write_text(json.dumps(attempts_log, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
