# SG06_RETRY_REPORT.md — MultiROCKET-HYDRA Controlled L2C Recovery (M02C)

**Candidate:** `SG06` — `aeon.regression.convolution_based.MultiRocketHydraRegressor`  
**Environment:** `.venv-signal-hydra` (unchanged from M02B: `aeon==1.6.0`, `torch==2.9.1+cu128`, `numba==0.63.1`, `numpy==2.3.5`)  
**Configuration:** `n_kernels=8`, `n_groups=64`, `n_jobs=16`, `random_state=42`, input `(12216, 1, 501)` -> `(3822,)`

## Outcome
- **M02B Attempt:** L0, L1, L2A (`3,528.6 MiB` RSS), L2B (`15,732.3 MiB` RSS, `39.99 s`) passed; L2C terminated by watchdog at `300 s` (`WALL_CLOCK_TIMEOUT`, `26,348.3 MiB` RSS).
- **M02C Controlled Retry (1,800s timeout, identical configuration & 16-thread budget):**
  - **L2C Status:** **`PASS`**
  - **Wall-clock duration:** **`344.859 s`** (under `1,800 s` ceiling)
  - **Peak sampled process-tree RSS:** **`26,234.871 MiB`** (`~25.62 GiB`, well within the `64 GiB` cap and preserving `> 16 GiB` host RAM reserve)
  - **Device:** `CPU`
- **Conclusion:** `SG06` is upgraded to **`SCALE_CHECK_PASS`** for `(12216, 501) -> (3822,)` without reducing kernels/groups or substituting estimators.
