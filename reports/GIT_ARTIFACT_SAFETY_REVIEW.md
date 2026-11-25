# GIT_ARTIFACT_SAFETY_REVIEW.md — Git State, Tracked Artifacts & Retention Policy (M01.1)

**Date:** 2026-11-25  
**Repository:** `https://github.com/abdurrahmansyah/krkCMd_research_starter_v1.git`  
**Verified HEAD:** `e2cea5d` (`feat: M01-R — New Workstation Migration`, tracking `origin/main`)  
**Policy:** Read-only Git audit; **zero files deleted, untracked, reset, committed, or pushed automatically.**

---

## 1. Current Git State Summary

- **Total tracked files (`git ls-files`):** `112`
- **Recent commits:**
  - `e2cea5d` — `feat: M01-R — New Workstation Migration` (manual researcher upload of M01-R)
  - `201aa50` — `feat: M01`
  - `80279cd` — `feat: manuscript generator & reference`
  - `80f0745` — `feat: run ipynb and result .html`

---

## 2. Sensitive / Large / Non-Source Artifact Audit

| Category | Tracked in Git? | Observed Details | Risk / Action |
|---|---|---|---|
| `.venv/`, `.venv_old_pc_backup/`, `.venv-*/` | **No** (`0` tracked) | Ignored by `.gitignore`. `.venv_old_pc_backup/` remains untracked on disk. | Safe. Propose manual deletion of `.venv_old_pc_backup/` only after researcher approval. |
| `.cache/`, `__pycache__/`, `*.pyc` | **No** (`0` tracked) | Ignored by `.gitignore`. | Safe. Recommend also ignoring `.cache/` explicitly before M02 downloads. |
| `.env` / credentials / tokens | **No** (`0` tracked) | Only `.env.example` is tracked. | Safe. |
| Raw datasets (`krkCMd_table.csv`, `krkCMd_scripts.zip`, `krkCMd_images.zip`) | **No** (`0` tracked) | `data/raw/*` (except `.gitkeep`) is ignored. | Safe. |
| Model binaries (`.joblib`, `.pkl`, `.mat`) | **No** (`0` tracked) | `artifacts/models/*` and `data/interim/*` are ignored. | Safe. |
| `reports/runs/*/isolated_workspace` | **No** (`0` tracked) | Explicitly ignored in `.gitignore`. | Safe. |
| `reports/runs/M01R_.../M01R_review_package.zip` & run outputs | **Yes** (`28` files in `e2cea5d`) | Researcher manually committed the M01-R run directory including `M01R_review_package.zip` (2.29 MB) and `pip_reports/*.json`. | Low risk (lightweight, no raw CSV/PDF/secrets), but `.zip` and large `pip_reports/*.json` bloat Git history over time. |
| `papers/*.pdf` | **Yes** (`20` PDFs tracked) | Committed in starter history before `.gitignore` or via force/initial commit; `31` newer PDFs remain ignored. | Existing starter history — **do NOT rewrite Git history automatically.** |
| Logs containing local paths | **Yes** (inside `reports/runs/M01R_.../*.json`) | Contains workstation hostname `DESKTOP-CQB09OU` and local paths (`C:\PROJECT\...`, `C:\Users\Nur Ridho A\...`). | Acceptable for local academic traceability; avoid tracking future raw `pip_reports/*.json` or `*.zip` in Git. |

---

## 3. Recommended `.gitignore` Improvements (Proposed Only)

To keep future M01.1 and M02 commits lightweight and free of caches, virtual environments, and review archives, we recommend appending the following rules to `.gitignore` (not applied automatically without approval):

```gitignore
# Virtual environments & caches (M02+)
.venv-*/
.cache/
*.lock.tmp

# Run-level large intermediates & review archives
reports/runs/*/*.zip
reports/runs/*/pip_reports/
reports/runs/*/isolated_workspace/
reports/runs/*/*.html
reports/runs/*/*.ipynb
```

---

## 4. Explicit Artifact Retention Policy

1. **Immutable Historical Evidence:** Preserve `reports/tables/*`, `reports/figures/*`, `reports/logs/baseline_run_summary.json`, `reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/`, and `reports/runs/M01_1_*/` as read-only audit evidence.
2. **Legacy Backup Cleanup (Pending Approval):** `.venv_old_pc_backup/` (copied from the old PC) is no longer needed because `.venv` has been cleanly rebuilt and M00 reproduced identically; propose manual removal by the researcher after reviewing M01.1.
3. **Checkpoint Cache Isolation (M02+):** Store `HF_HOME` and `TORCH_HOME` inside `.cache/` (ignored by Git) so gated/open foundation-model weights never enter `git status`.
