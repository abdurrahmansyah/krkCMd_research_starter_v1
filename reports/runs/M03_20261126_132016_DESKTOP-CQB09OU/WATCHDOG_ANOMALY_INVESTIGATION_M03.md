# WATCHDOG_ANOMALY_INVESTIGATION_M03.md — FM04 L2C Timing Anomaly & Repair (M03)

## 1. Observed Anomaly (M02C `task-581`)
- In M02C, `FM04` (`TabDPTRegressor`) L2C reported `subprocess_elapsed_sec = 48477.078` (~13.5 hours) despite `timeout_sec = 900`.
- **Root Cause:** On Windows, `time.monotonic()` (`QueryPerformanceCounter` / `GetTickCount64`) advances across OS sleep/hibernation. The host workstation suspended overnight between two `0.2 s` watchdog poll ticks, causing `now - t0` to jump past `900 s` in a single poll step (`max_poll_gap > 30 s`). This is **not** valid completed runtime.

## 2. Implemented Repairs (`scripts/resource_policy.py`)
1. **Suspend/Resume Jump Detection:** `run_monitored_subprocess()` now tracks `max_poll_gap_sec` and sets `suspend_detected = True` whenever any single poll interval exceeds `suspend_gap_threshold_sec` (`30.0 s`), appending `[SUSPEND_DETECTED]` to `violation_reason`.
2. **Bounded Monitoring Timeouts:** `query_gpu_vram_usage()` enforces `timeout_sec=3`, and `proc.wait(timeout=5)` prevents indefinite post-termination hangs.
3. **Unique Attempt Isolation:** Every retry writes its own immutable `attempts/<attempt_id>.json` before any subsequent attempt begins (`tests/test_m03_metrics_perturbations_watchdog.py::test_watchdog_detects_simulated_suspend_clock_jump` PASS).
