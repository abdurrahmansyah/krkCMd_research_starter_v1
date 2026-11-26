# RF05_STABILITY_AND_REPRODUCTION_REPORT.md — DLM 15-Layer Architecture Recovery (M02C)

**Candidate:** `RF05` — DLM Retrained (`DLM15LayerCNN_Table3_Normalized`)  
**Sources:** Jakubowski & Tomczak (2024) Table 3 & Section 3.2.3; `data/interim/krkCMd_scripts/CrackWidthDLM_Matlab.m`  
**Environment:** `.venv-deep` (unchanged: `torch==2.9.1+cu128`, `cuda:0`)

---

## 1. Root-Cause Diagnostic (Synthetic `N=1,000, D=501, seed=42`)

| Mode | Normalization | Target Unit | Steps Completed | First Loss | Last Loss | Max Grad Norm | Outcome |
|---|---|---|---|---:|---:|---:|---|
| `raw_um` (M02B) | None (`[0, 255]`) | µm (`[30, 350]`) | 8 / 24 | `48,364.68` | **`nan`** | `2.89e13` | `FAILED` (exploding SGDM gradient) |
| `zerocenter_px` (M02C) | **Train-only** `X - mean(X_train)` | **Pixels** (`y_um / 3.96875`) | **24 / 24** | `3,083.37` | **`210.28`** | `25,765.32` | **`STABLE`** (no gradient clipping, faithful SGDM `lr=1e-3, momentum=0.9`) |

## 2. Verified Facts vs. Implementation Notes
- **Verified from 2024 Paper & MATLAB script:** 15-layer Table 3 architecture (`Conv1d(64,k=4)->BN->ReLU->MaxPool(4,s=2)->Conv1d(32,k=16)->BN->ReLU->MaxPool(4,s=2)->Conv1d(32,k=32)->BN->ReLU->Dropout(0.2)->Flatten->FC(1)`), `SGD` with momentum (`lr=1e-3` to `1e-5`, batch `128`), `pi2mi = 1000 * 25.4 / 6400 = 3.96875` µm/px, and Layer 1 `"501 × 1 × 1 images with normalization"` (MATLAB `imageInputLayer` defaults to `'zerocenter'`).
- **Preprocessing & Serialization:** `RF05DLMNormalizedAdapter` stores `train_input_mean` and `pi2mi` inside the saved checkpoint (`pytorch_state_dict+preprocessing_state`, reload max diff `0.0`).
- **M02C L0/L1/L2A/L2B/L2C Outcome:** **ALL `PASS`** on `cuda:0` (`1,131.49 MiB` RSS, `111.15 MiB` CUDA allocated, `9.594 s` wall at L2C). Distinction from `RF04` (`krknet.mat` pretrained weights) is strictly preserved.
