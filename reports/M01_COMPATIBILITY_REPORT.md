# M01 — Comprehensive Model Registry & Compatibility Assessment Report

**Project:** `krkCMd_research_starter`  
**Milestone:** M01 — Feasibility Assessment, Dependency Resolution, Reproducibility Planning, and Synthetic Smoke Testing  
**Date of Assessment:** 2026-11-25  
**Governing Policy:** `AGENT.md` & `MASTER_PROMPT.md`  
**Status Policy:** Exploratory compatibility evaluation; **no candidate model is approved for experimental training in this milestone.**

---

## 1. Executive Summary

This milestone establishes a standardized, reproducible registry and feasibility audit for expanding the research scope of:
> *“Benchmarking and Robustness Analysis of Machine Learning Models for Concrete Crack Width Estimation Using krkCMd Brightness Profiles.”*

A comprehensive registry of **32 candidate models** across six methodological paradigms has been established:
1. Classical Machine Learning & Gradient Boosting (7 candidates)
2. Tabular Deep Learning (5 candidates)
3. Tabular Foundation Models (4 candidates)
4. Spatial Signal Regression (6 candidates)
5. Custom and Domain-Specific Hybrid Approaches (5 candidates)
6. Reference Benchmarks (5 candidates)

### Core Governance Declarations:
- **Zero Real Data Training:** No machine learning model was trained using actual observations from `krkCMd_table.csv`.
- **Zero Hyperparameter Optimization:** No hyperparameter tuning, grid search, or random search was performed.
- **Baseline Preservation:** The verified baseline notebook (`notebooks/00_baseline_krkCMd.ipynb`) and existing baseline artifacts (`artifacts/models/`, `artifacts/results/`) remain strictly unmodified.
- **Environment Integrity:** The primary `.venv` was preserved in its frozen, clean state without installing unvetted packages.
- **Manuscript Integrity:** Manuscript files and experimental result tables were not altered.

---

## 2. Hardware and Environment Audit Findings

A complete system audit was executed using local commands and recorded in `reports/logs/hardware_environment.json`:

| Hardware / System Component | Specification / Audit Result | Operational Implication for Research |
|---|---|---|
| **Operating System** | Windows 11 Enterprise (Build 26300, 64-bit AMD64) | Native Windows support verified for core scientific packages. |
| **CPU Model** | Intel(R) Core(TM) i7 (Family 6 Model 154 Stepping 3, GenuineIntel) | 14 physical cores, 20 logical threads. Highly performant for parallel CPU model fitting (`n_jobs=-1`). |
| **System Memory (RAM)** | **31.70 GB Total** (6.29 GB Available, 25.42 GB Used / 80.2%) | Ample total RAM; however, high background usage requires keeping per-model memory budgets $\le 4.0\text{ GB}$. |
| **Disk Storage (Drive C:)** | **952.51 GB Total** (**37.54 GB Free**, 914.97 GB Used / 96.1%) | **Tight disk constraint (37.5 GB free)**. Environment isolation must be strictly budgeted ($\le 8\text{ GB}$ total). |
| **GPU Model & VRAM** | **NVIDIA GeForce RTX 3050 Laptop GPU** (4096 MiB = 4.0 GB VRAM) | CUDA acceleration available for moderate CNNs; requires batch size capping ($\le 64$) for transformers to prevent CUDA OOM. |
| **GPU Driver & CUDA** | Driver Version: **596.52** \| Supported CUDA: **13.2** | Supports PyTorch with CUDA 12.1 / 12.4 runtime wheels natively on Windows. |
| **Python Executable** | `C:\PROJECT\krkCMd_research_starter\.venv\Scripts\python.exe` | **Python 3.11.9** (64-bit). Fully compliant with project specification. |
| **Virtual Environment** | `.venv` (Frozen baseline scientific stack) | `pip check` confirmed: **No broken requirements found**. |
| **MATLAB Installation** | `C:\Program Files\MATLAB\R2026b\bin\matlab.EXE` | MATLAB R2026b is installed on PATH. |
| **MATLAB Toolboxes** | **Deep Learning Toolbox (`nnet`) is ABSENT** | Cannot execute MATLAB `predict(krknet, X)` directly on host without active toolbox license. |
| **WSL2 Subsystem** | Available (Default Distribution: Ubuntu 2) | Available as an auxiliary fallback if Linux-only dependencies arise. |

---

## 3. Comprehensive Model Compatibility Matrix (All 32 Candidates)

The complete matrix is saved in `reports/tables/model_compatibility_matrix.csv` and registered in `configs/model_registry.yaml`:

| ID | Model Name | Paradigm Family | Primary Estimator Class | Target Package | Status | Primary Reference / DOI | Hardware |
|---|---|---|---|---|---|---|---|
| **ML01** | Extra Trees | Classical ML & Boosting | `sklearn.ensemble.ExtraTreesRegressor` | `scikit-learn` | **`SMOKE_TEST_PASS`** | Geurts et al. (2006) [10.1007/s10994-006-6226-1](https://doi.org/10.1007/s10994-006-6226-1) | CPU |
| **ML02** | Random Forest | Classical ML & Boosting | `sklearn.ensemble.RandomForestRegressor` | `scikit-learn` | **`SMOKE_TEST_PASS`** | Breiman (2001) [10.1023/A:1010933404324](https://doi.org/10.1023/A:1010933404324) | CPU |
| **ML03** | HistGradientBoosting | Classical ML & Boosting | `sklearn.ensemble.HistGradientBoostingRegressor` | `scikit-learn` | **`SMOKE_TEST_PASS`** | Ke et al. (2017) [NeurIPS 2017](https://papers.nips.cc/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html) | CPU |
| **ML04** | XGBoost | Classical ML & Boosting | `xgboost.XGBRegressor` | `xgboost` | `STATIC_REVIEW` | Chen & Guestrin (2016) [10.1145/2939672.2945399](https://doi.org/10.1145/2939672.2945399) | CPU / GPU |
| **ML05** | LightGBM | Classical ML & Boosting | `lightgbm.LGBMRegressor` | `lightgbm` | `STATIC_REVIEW` | Ke et al. (2017) [NeurIPS 2017](https://papers.nips.cc/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html) | CPU / GPU |
| **ML06** | CatBoost | Classical ML & Boosting | `catboost.CatBoostRegressor` | `catboost` | `STATIC_REVIEW` | Prokhorenkova et al. (2018) [NeurIPS 2018](https://papers.nips.cc/paper/2018/hash/14491b756b3a51daac41c24863285549-Abstract.html) | CPU / GPU |
| **ML07** | SVR RBF | Classical ML & Boosting | `sklearn.svm.SVR(kernel='rbf')` | `scikit-learn` | **`SMOKE_TEST_PASS`** | Smola & Schölkopf (2004) [10.1023/B:STCO.0000035301.49549.88](https://doi.org/10.1023/B:STCO.0000035301.49549.88) | CPU |
| **DL01** | MLP | Tabular Deep Learning | `sklearn.neural_network.MLPRegressor` | `scikit-learn` | **`SMOKE_TEST_PASS`** | Rumelhart et al. (1986) [10.1038/323533a0](https://doi.org/10.1038/323533a0) | CPU |
| **DL02** | FT-Transformer | Tabular Deep Learning | `rtdl.FTTransformer` | `rtdl_num_embeddings, torch` | `CONDITIONAL` | Gorishniy et al. (2021) [arXiv:2106.11958](https://arxiv.org/abs/2106.11958) | GPU (4GB) |
| **DL03** | RealMLP | Tabular Deep Learning | `tabbench.RealMLP` | `torch` | `STATIC_REVIEW` | Holzmüller et al. (2024) [arXiv:2407.04491](https://arxiv.org/abs/2407.04491) | GPU / CPU |
| **DL04** | TabR | Tabular Deep Learning | `tabular-dl-tabr` | `torch, faiss-cpu` | `CONDITIONAL` | Gorishniy et al. (2024) [arXiv:2307.14338](https://arxiv.org/abs/2307.14338) | GPU / CPU |
| **DL05** | TabM | Tabular Deep Learning | `tabular-dl-tabm` | `torch` | `STATIC_REVIEW` | Gorishniy et al. (2024) [arXiv:2410.24210](https://arxiv.org/abs/2410.24210) | GPU / CPU |
| **FM01** | TabPFN-3.5 | Tabular Foundation Models | `tabpfn.TabPFNRegressor` | `tabpfn` | `CONDITIONAL` | Hollmann et al. (2025) [10.1038/s41586-024-08328-6](https://doi.org/10.1038/s41586-024-08328-6) | GPU / CPU |
| **FM02** | TabPFN-3.5-Fast | Tabular Foundation Models | `tabpfn.TabPFNRegressor(model='fast')` | `tabpfn` | `CONDITIONAL` | PriorLabs Technical Report (2025) [arXiv:2501.04257](https://arxiv.org/abs/2501.04257) | GPU / CPU |
| **FM03** | TabICLv2 | Tabular Foundation Models | `tabicl` | `torch` | `CONDITIONAL` | In-Context Learning for Tabular Data (2024) | GPU |
| **FM04** | TabDPT | Tabular Foundation Models | `TabDPT` | `torch` | `CONDITIONAL` | Ma et al. (2024) [arXiv:2410.18164](https://arxiv.org/abs/2410.18164) | GPU |
| **SG01** | Vanilla 1D-CNN | Spatial Signal Regression | `torch.nn.Conv1d` Module | `torch` | `STATIC_REVIEW` | LeCun et al. (1989) [10.1162/neco.1989.1.4.541](https://doi.org/10.1162/neco.1989.1.4.541) | CPU / GPU |
| **SG02** | ResNet-1D | Spatial Signal Regression | `aeon.networks.ResNetNetwork` | `aeon, torch` | `STATIC_REVIEW` | Wang et al. (2017) [10.1109/IJCNN.2017.7966039](https://doi.org/10.1109/IJCNN.2017.7966039) | CPU / GPU |
| **SG03** | InceptionTime Regression | Spatial Signal Regression | `aeon.regression.deep_learning.InceptionTimeRegressor` | `aeon, torch` | `STATIC_REVIEW` | Fawaz et al. (2020) [10.1007/s10618-020-00710-y](https://doi.org/10.1007/s10618-020-00710-y) | GPU / CPU |
| **SG04** | LITETime Regression | Spatial Signal Regression | `aeon.regression.deep_learning.LITETimeRegressor` | `aeon, torch` | `STATIC_REVIEW` | Ismail-Fawaz et al. (2023) [arXiv:2309.05566](https://arxiv.org/abs/2309.05566) | CPU / GPU |
| **SG05** | ROCKET Regression | Spatial Signal Regression | `aeon.regression.convolution_based.RocketRegressor` | `aeon, numba` | `STATIC_REVIEW` | Dempster et al. (2020) [10.1007/s10618-020-00701-z](https://doi.org/10.1007/s10618-020-00701-z) | CPU |
| **SG06** | MultiROCKET-HYDRA | Spatial Signal Regression | `aeon.regression.convolution_based.MultiRocketRegressor` | `aeon, numba` | `STATIC_REVIEW` | Tan et al. (2022) [10.1007/s10618-022-00834-3](https://doi.org/10.1007/s10618-022-00834-3) | CPU |
| **HY01** | SNV + CatBoost | Custom & Hybrid | `Pipeline(SNVTransformer, CatBoostRegressor)` | `catboost, numpy` | `DESIGN_REQUIRED` | Barnes et al. (1989) [10.1366/0003702894202201](https://doi.org/10.1366/0003702894202201) | CPU / GPU |
| **HY02** | Derivative + Extra Trees | Custom & Hybrid | `Pipeline(DerivativeTransformer, ExtraTreesRegressor)` | `scikit-learn, scipy` | `DESIGN_REQUIRED` | Savitzky & Golay (1964) [10.1021/ac60214a047](https://doi.org/10.1021/ac60214a047) | CPU |
| **HY03** | Dual-stream Multiscale CNN | Custom & Hybrid | PyTorch DualStreamConv1D | `torch` | `DESIGN_REQUIRED` | Project Custom Architecture | GPU / CPU |
| **HY04** | CNN + CatBoost | Custom & Hybrid | `Pipeline(CNNFeatureExtractor, CatBoostRegressor)` | `torch, catboost` | `DESIGN_REQUIRED` | Hybrid Representation Design | GPU + CPU |
| **HY05** | Robust Stacking Ensemble | Custom & Hybrid | `sklearn.ensemble.StackingRegressor` | `scikit-learn, catboost, aeon` | `DESIGN_REQUIRED` | Wolpert (1992) [10.1016/S0893-6080(05)80023-1](https://doi.org/10.1016/S0893-6080(05)80023-1) | CPU |
| **RF01** | Dummy Mean | Reference Benchmarks | `sklearn.dummy.DummyRegressor` | `scikit-learn` | **`SMOKE_TEST_PASS`** | Empirical Mean Floor | CPU |
| **RF02** | Linear Regression | Reference Benchmarks | `sklearn.linear_model.LinearRegression` | `scikit-learn` | **`SMOKE_TEST_PASS`** | Ordinary Least Squares | CPU |
| **RF03** | AED Original (Python Port) | Reference Benchmarks | `scripts.aed_analytical.AEDRegressor` | `numpy, scipy` | **`SMOKE_TEST_PASS`** | Tomczak et al. (2017) [10.1515/sgem-2017-0017](https://doi.org/10.1515/sgem-2017-0017) | CPU |
| **RF04** | DLM Pretrained | Reference Benchmarks | `krknet.mat` (Author Pretrained) | MATLAB / PyTorch Port | `CONDITIONAL` | Jakubowski & Tomczak (2024) [10.1016/j.conbuildmat.2024.135768](https://doi.org/10.1016/j.conbuildmat.2024.135768) | CPU / GPU |
| **RF05** | DLM Retrained | Reference Benchmarks | 15-layer 1D-CNN Table 3 Architecture | `torch` | `STATIC_REVIEW` | Jakubowski & Tomczak (2024) [10.1016/j.conbuildmat.2024.135768](https://doi.org/10.1016/j.conbuildmat.2024.135768) | GPU / CPU |

---

## 4. Status Breakdown Analysis

```text
======================================================================
Status Distribution Across 32 Candidates:
- STATIC_REVIEW       : 12 models  (37.5%) — Implementation vetted; pending environment install
- SMOKE_TEST_PASS     :  8 models  (25.0%) — Verified in .venv with L0/L1 synthetic test
- CONDITIONAL         :  7 models  (21.9%) — Technical or licensing mitigations required
- DESIGN_REQUIRED     :  5 models  (15.6%) — Custom pipelines/architectures to be formalized
- APPROVED            :  0 models  ( 0.0%) — Strictly zero unapproved training
======================================================================
```

---

## 5. Synthetic Smoke Testing (L0 / L1) Results

Synthetic profiles were generated deterministically (`seed=42`) using $N_{\text{train}} = 100$ and $N_{\text{test}} = 20$ profiles with $D = 501$ continuous features simulating concrete surface brightness with central crack attenuation:

| Model ID | Model Name | L0 Import | L1 Output Shape | Finite Check (`isfinite`) | L1 Wall Time | Status |
|---|---|---|---|---|---|---|
| `ML01` | Extra Trees | PASS | `(20,)` | **PASS (True)** | 0.370 s | `SMOKE_TEST_PASS` |
| `ML02` | Random Forest | PASS | `(20,)` | **PASS (True)** | 0.056 s | `SMOKE_TEST_PASS` |
| `ML03` | HistGradientBoosting | PASS | `(20,)` | **PASS (True)** | 0.117 s | `SMOKE_TEST_PASS` |
| `ML07` | SVR RBF | PASS | `(20,)` | **PASS (True)** | 0.007 s | `SMOKE_TEST_PASS` |
| `DL01` | MLP | PASS | `(20,)` | **PASS (True)** | 0.043 s | `SMOKE_TEST_PASS` |
| `RF01` | Dummy Mean | PASS | `(20,)` | **PASS (True)** | 0.002 s | `SMOKE_TEST_PASS` |
| `RF02` | Linear Regression | PASS | `(20,)` | **PASS (True)** | 0.022 s | `SMOKE_TEST_PASS` |
| `RF03` | AED Original (Python Port) | PASS | `(20,)` | **PASS (True)** | < 0.001 s | `SMOKE_TEST_PASS` |

*No errors, crashes, or non-finite values occurred during any test.*

---

## 6. DLM and AED Reproduction Feasibility Assessment

### 1. AED Original (`RF03`)
- **Inspection of Script:** `CrackWidthAED_VBA.txt` is an analytical rule-based procedure.
- **Port Feasibility:** **100% Feasible**. The algorithm iterates outward from the global minimum brightness pixel, tests brightness inflection thresholds (`step=10`, `accuracy=5`, `brightness_increment=5`), detects crack-closure conditions, and computes width in micrometers via the 6400 dpi optical scaling factor:
  $$\text{Width}_{\mu\text{m}} = (\Delta_{\text{pixels}} + 1) \times \frac{25.4}{6400} \times 1000$$
- **Verification:** The native Python port was executed in our smoke test and passed with finite predictions in sub-millisecond execution time.

### 2. DLM Pretrained (`RF04`)
- **Inspection of File:** `krknet.mat` contains a MATLAB 5.0 MAT-file encapsulating an opaque `SeriesNetwork` object.
- **Host Limitation:** The host machine has MATLAB R2026b installed, but **does not possess the MATLAB Deep Learning Toolbox (`nnet`)**. Calling `predict(krknet, X)` directly in MATLAB fails.
- **Feasibility:** `RF04` is classified as `CONDITIONAL`. To evaluate author weights, the weight tensors must either be extracted via a machine with the MATLAB Deep Learning Toolbox or reconstructed via HDF5/MATLAB conversion tools.

### 3. DLM Retrained (`RF05`)
- **Inspection of 2024 Paper (Table 3):** The exact layer-by-layer specification of the author's 15-layer CNN is published on page 6 of Jakubowski & Tomczak (2024):
  - Input: $501 \times 1 \times 1$
  - Conv1: 64 filters, kernel $4 \times 1$, stride 1, padding 'same' $\to$ BatchNorm $\to$ ReLU $\to$ MaxPool ($4 \times 1$, stride 2)
  - Conv2: 32 filters, kernel $16 \times 1$, stride 1, padding 'same' $\to$ BatchNorm $\to$ ReLU $\to$ MaxPool ($4 \times 1$, stride 2)
  - Conv3: 32 filters, kernel $32 \times 1$, stride 1, padding 'same' $\to$ BatchNorm $\to$ ReLU $\to$ Dropout
  - Dense: 1 output $\to$ Regression loss
- **Feasibility:** **100% Feasible in PyTorch**. Architecture, hyperparameters (Adam, initial LR $10^{-3}$, final LR $10^{-5}$, 50 epochs, batch size 128), and scaling constant are completely documented and ready for exact Python implementation upon environment approval.

---

## 7. Key Critical Bottlenecks, License Restrictions & Missing Evidence

1. **TabPFN Feature Limit (FM01 / FM02):**
   - The TabPFN v2 foundation model imposes a hard ceiling of **500 features**. Passing 501 features triggers an immediate error.
   - *Mitigation Plan:* Drop feature `x1` or `x501` (boundary points representing background matrix) or apply 1-component linear projection.
2. **PriorLabs License Gating (FM01 / FM02):**
   - Model weights require accepting the PriorLabs Non-Commercial / Research license via Hugging Face. Commercial use is restricted.
3. **FT-Transformer Quadratic Complexity (DL02):**
   - Multi-head self-attention over 501 feature tokens requires $501^2 = 251,001$ attention operations per row per layer. On 4GB VRAM, batch size must be restricted to $\le 64$.
4. **FAISS CPU vs GPU (DL04 TabR):**
   - `faiss-gpu` is Linux-only; however, `faiss-cpu` is fully functional on Windows x64. For 12,216 samples and 501 features, CPU retrieval is fast (<15 ms).
5. **Host Disk Storage (37.5 GB Free):**
   - Disk space is limited. Virtual environments must not be created indiscriminately. The proposed 4 isolated environments must be created selectively and sequentially.

---

## 8. Proposed Decision and Experiment Log Entries

### Proposed Decision Log Entry (`docs/DECISIONS.md`):
```markdown
## D-005 — Model Registry and Compatibility Assessment (2026-11-25)
- Status: EXPLORATORY (M01 COMPLETE)
- Context: Evaluated 32 model candidates across 6 paradigms for Idea 1 & 2 expansion.
- Outcome: 8 models passed L0/L1 smoke testing in .venv; 12 static reviews completed; 7 conditional constraints identified; 5 custom designs cataloged.
- Strict Constraint: No model is approved for new training experiments until resource budget and multi-environment architecture are authorized.
```

### Proposed Experiment Log Entry (`docs/EXPERIMENT_LOG.md`):
```markdown
## EXP-002 — Milestone M01: Model Registry and Compatibility Assessment
- Date: 2026-11-25
- Status: COMPLETED (Read-Only Audit & Synthetic Smoke Tests)
- Scope: Hardware audit, dependency resolution checks, 32-candidate registry, synthetic profile L0/L1 smoke testing, DLM/AED reproduction analysis.
- Findings: All 8 installed baseline models passed L0/L1 synthetic testing. 24 remaining models cataloged with exact citations, licenses, and environment plans. Zero actual krkCMd training conducted.
```

---

## 9. Next-Stage Execution Recommendations (Pending User Approval)

1. **Approval Gate 1 (Environment Authorization):**
   User reviews and authorizes the proposed `docs/MODEL_ENVIRONMENT_PLAN.md` to create `.venv-boost` (for XGBoost, LightGBM, CatBoost) and `.venv-signal` (for ROCKET and aeon).
2. **Approval Gate 2 (Model Screening Selection):**
   Select the top candidates from each family for formal Level 2 capacity checking ($N = 12,216$) and initial baseline benchmarking.
3. **Approval Gate 3 (Deep Learning & MATLAB Path):**
   Decide whether to execute DLM Retrained in PyTorch or obtain MATLAB Deep Learning Toolbox license for `krknet.mat`.
