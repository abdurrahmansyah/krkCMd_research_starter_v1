# M02_PROVISIONING_PLAN.md — Phased Environment Provisioning & Verification Plan (Post-M01-R / M01.1)

**Date:** 2026-11-25  
**Workstation:** `DESKTOP-CQB09OU` (i9-10900KF 20T, 127.92 GB RAM, Quadro RTX 6000 24 GB VRAM Turing `sm_75`, Driver 621.24 / CUDA UMD 13.5, ~1.75 TB free disk, Windows Pro 24H2)  
**Policy:** **NO M02 environment has been created or installed in M01.1.** All commands below are **PROPOSED** for researcher approval.

---

## 1. NVIDIA Turing (`sm_75`) Compatibility Analysis

The workstation's **NVIDIA Quadro RTX 6000** (24 GB GDDR6, `compute_capability = 7.5`, `sm_75`) must **not** be confused with Ampere (`RTX A6000`, `sm_86`), Ada (`RTX 6000 Ada`, `sm_89`), or Blackwell (`RTX PRO 6000`, `sm_120`).

| Capability | Turing `sm_75` Support | Research Implication |
|---|---|---|
| **PyTorch Official Windows CUDA Wheels** | Supported (`cu124`, `cu126`, `cu128`, `cu130`) | **Must pass `--index-url https://download.pytorch.org/whl/cu128`** (not `--extra-index-url`, which fell back to PyPI CPU `torch 2.15.0` in M01-R). |
| **FP32 Computation** | **Full native support** | Primary training precision for `DL01–DL05`, `SG01`, `HY03–HY04`, `RF05`. |
| **FP16 & AMP (`torch.amp`)** | **Supported (Turing Tensor Cores)** | Safe for speedup/VRAM reduction in `DL02`, `FM01–FM04`; verify numerical stability vs FP32. |
| **Native BF16 (`bfloat16`)** | **NOT native hardware** (Ampere `sm_80`+) | Avoid `torch.bfloat16` autocast; emulated or unsupported in kernels. Use FP32 or FP16 AMP. |
| **TF32 (`allow_tf32`)** | **NOT supported** (Ampere `sm_80`+) | Standard IEEE FP32 math is used automatically. |
| **Attention Implementations** | PyTorch SDPA (`math` & `mem_efficient` backends) | **FlashAttention-2 (`flash-attn`) requires Ampere `sm_80`+ and is NOT supported on Turing `sm_75`.** Force SDPA `mem_efficient` or `math` backend where needed. |
| **Foundation-Model CUDA Kernels & Quantization** | Standard PyTorch CUDA ops work; `bitsandbytes`/4-bit/8-bit quantization kernels vary on Windows `sm_75` | Test `FM01–FM04` in FP16/FP32 first; do not assume `flash-attn` or Ada/Hopper FP8 kernels work. |
| **CPU Fallback** | Fully viable (`127.92 GB` RAM, 20 threads) | Mandatory fallback for TensorFlow `aeon` (`SG02–SG04`), `ROCKET`/`MultiROCKET` (`SG05–SG06`), and `faiss-cpu` (`DL04`). |

---

## 2. Phased M02 Provisioning Plan

### M02A — Boosting & CPU Signal Environments (`.venv-boost`, `.venv-signal-cpu`)
- **Targets:** `ML04` (XGBoost), `ML05` (LightGBM), `ML06` (CatBoost), `HY01` (SNV+CatBoost), `SG05` (ROCKET), `SG06` (MultiROCKET), `HY05` (Stacking).
- **Proposed Commands (after approval):**
```powershell
py -3.11 -m venv .venv-boost
.\.venv-boost\Scripts\python.exe -m pip install "xgboost>=2.0,<4" "lightgbm>=4.0,<5" "catboost>=1.2,<2" "scikit-learn>=1.4,<2" "numpy>=1.26" "pandas>=2.1" "scipy>=1.11" joblib psutil

py -3.11 -m venv .venv-signal-cpu
.\.venv-signal-cpu\Scripts\python.exe -m pip install "aeon>=1.6" "numba>=0.59" "scikit-learn>=1.4,<2" "scipy>=1.11" psutil
```

### M02B — Deep Learning & Neural Signal Environments (`.venv-deep`, optional `.venv-signal-tf`)
- **Targets:** `DL01` (PyTorch MLP), `DL02` (FT-Transformer via `rtdl-num-embeddings`), `DL03` (RealMLP via `pytabkit`), `DL04` (TabR via `tabular-dl-tabr` + `faiss-cpu`), `DL05` (TabM via `tabm`), `SG01` (Vanilla 1D-CNN), `HY03`–`HY04`, `RF05` (DLM 15-layer PyTorch).
- **Backend Note for `SG02–SG04`:** `aeon.networks.ResNetNetwork`, `InceptionTimeRegressor`, and `LITETimeRegressor` use TensorFlow/Keras (CPU-only on native Windows TF >2.10). Either run them on CPU in `.venv-signal-tf` or implement native PyTorch equivalents in `.venv-deep` for Quadro RTX 6000 GPU training.
- **Proposed Commands (after approval):**
```powershell
py -3.11 -m venv .venv-deep
.\.venv-deep\Scripts\python.exe -m pip install torch==2.9.1+cu128 torchvision==0.24.1+cu128 --index-url https://download.pytorch.org/whl/cu128
.\.venv-deep\Scripts\python.exe -m pip install "faiss-cpu>=1.8" "rtdl-num-embeddings>=0.0.12" "tabm>=0.0.3" "pytabkit>=1.8.0" "scikit-learn>=1.4,<2" "pandas>=2.1" "scipy>=1.11" psutil
# Immediate GPU Turing sm_75 smoke check (proposed):
.\.venv-deep\Scripts\python.exe -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0), torch.cuda.get_device_capability(0))"
```

### M02C — Foundation-Model Environment (`.venv-foundation`)
- **Targets:** `FM01` (`tabpfn.TabPFNRegressor`), `FM02` (`TabPFNRegressor` fast), `FM03` (`tabicl.TabICLRegressor`), `FM04` (`tabdpt.TabDPTRegressor`).
- **License & Feature Notes:**
  - `FM01`/`FM02`: PriorLabs Research/Non-Commercial gated weights on Hugging Face; 500-feature limit (requires approved protocol before dropping 1 feature or projecting 501->500).
  - `FM03`: `tabicl 2.2.0` on PyPI (Apache-2.0 code; verify checkpoint terms).
  - `FM04`: `tabdpt 1.3.2` on PyPI (MIT code, open weights; chunked retrieval for >5,000 rows).
- **Proposed Commands (after researcher accepts gated licenses):**
```powershell
py -3.11 -m venv .venv-foundation
.\.venv-foundation\Scripts\python.exe -m pip install torch==2.9.1+cu128 --index-url https://download.pytorch.org/whl/cu128
.\.venv-foundation\Scripts\python.exe -m pip install "tabpfn>=2.0" "tabicl>=2.0" "tabdpt>=1.0" "huggingface_hub>=0.23" "scikit-learn>=1.4,<2" psutil
```

---

## 3. Reference Reproduction Track (`RF03`, `RF04`, `RF05`)

- **`RF03` (Faithful AED Python Port):** Translate multi-stage `data/interim/krkCMd_scripts/CrackWidthAED_VBA.txt` into `src/` and validate numerical parity against `AEDwidth` in `krkCMd_table.csv` (keeping analytical init+predict interface).
- **`RF04` (Original Pretrained `krknet.mat`):** MATLAB and Deep Learning Toolbox are **not installed** on `DESKTOP-CQB09OU`. Execution requires either exporting layer weights/biases from an external licensed MATLAB+`nnet` installation or reconstructing/loading the exact weights in PyTorch. Remains `CONDITIONAL`.
- **`RF05` (DLM Retrained 15-Layer 1D-CNN):** Implement Table 3 architecture of Jakubowski & Tomczak (2024) in PyTorch inside `.venv-deep` under the strict `Series + Image + Gridline` split (distinct from `RF04` pretrained weights).
