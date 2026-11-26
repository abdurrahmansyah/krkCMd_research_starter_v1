# FOUNDATION_MODEL_SOURCE_REGISTER.md — Verified Foundation Model Identities (M02C)

**Verification Date:** 2026-11-25  
**Target Models:** `FM01`, `FM02`, `FM03`, `FM04`  
**Policy:** All inferences run locally on `DESKTOP-CQB09OU`; zero `krkCMd` data transmitted to external APIs.

---

| ID | Model | Primary Literature | Official Repo & Package Release | Exact Constructor / API | Checkpoint Repo & File (`HF gated?`) | Code & Weights Licenses |
|---|---|---|---|---|---|---|
| **FM01** | **TabPFN-3.5** | Hollmann et al. (2025) *Nature* 637:345–353 (`10.1038/s41586-024-08328-6`); TabPFN-3.5 report (`arXiv:2609.17895`) | `PriorLabs/TabPFN`; `tabpfn==10.2.0` | `TabPFNRegressor(device="cuda:0", random_state=42)` | `Prior-Labs/tabpfn_3_5` (`06bf2ba3`), `tabpfn-v3.5-20260909.safetensors` (`gated: false`) | Code: Apache-2.0; Weights: PriorLabs Non-Commercial (`HF LICENSE`) |
| **FM02** | **TabPFN-3.5-Fast** | PriorLabs TabPFN-3.5 report (`arXiv:2609.17895`) | `PriorLabs/TabPFN`; `tabpfn==10.2.0` | `TabPFNRegressor.create_default_for_version(ModelVersion.V3_5_FAST, device="cuda:0", random_state=42)` | `Prior-Labs/tabpfn_3_5` (`06bf2ba3`), `tabpfn-v3.5-fast-20260909.safetensors` (`gated: false`) | Code: Apache-2.0; Weights: PriorLabs Non-Commercial (`HF LICENSE`) |
| **FM03** | **TabICLv2** | Qu et al. (2025/2026) *TabICL* (`arXiv:2502.05564`) & *TabICLv2* (`arXiv:2602.11139`) | `soda-inria/tabicl`; `tabicl==2.2.0` | `TabICLRegressor(checkpoint_version="tabicl-regressor-v2-20260212.ckpt", n_estimators=8, batch_size=8, device="cuda:0", use_fa3=False, random_state=42)` | `jingang/TabICL` (`4dcd344e`), `tabicl-regressor-v2-20260212.ckpt` (`gated: false`) | Code & Weights: **BSD-3-Clause** (Open Source) |
| **FM04** | **TabDPT** | Ma et al. (2025) *TabDPT: Scaling Tabular Foundation Models on Real Data* (`arXiv:2410.18164`, NeurIPS 2025) | `layer6ai-labs/TabDPT-inference`; `tabdpt==1.3.2` | `TabDPTRegressor(context_reduction="retrieval", feature_reduction="pca", use_flash=False, compile=False, device="cuda:0")` | `Layer6/TabDPT` (`a5ca6e01`), `tabdpt1_3.safetensors` (`gated: false`) | Code: MIT; Weights: **Apache-2.0** (Open Weights) |

---

## Pretraining Provenance & Potential `krkCMd` Overlap
- **`FM01` / `FM02` (TabPFN-3.5 / Fast):** Pretrained primarily on synthetic structural causal priors (with later real-data extensions in v2.5–3.5). Absence of overlap with public Zenodo `krkCMd` (`10.5281/zenodo.11408398`) cannot be independently proven from model cards alone $\to$ **`UNKNOWN`**.
- **`FM03` (TabICLv2):** Pretrained on synthetic tabular priors (`arXiv:2602.11139`). No evidence of `krkCMd` inclusion, but unverified end-to-end $\to$ **`UNKNOWN`**.
- **`FM04` (TabDPT):** Explicitly pretrained on **real-world public tabular datasets** (`Layer6/TabDPT`). Potential overlap with `krkCMd` cannot be excluded without full pretraining corpus audit $\to$ **`UNKNOWN`**.
