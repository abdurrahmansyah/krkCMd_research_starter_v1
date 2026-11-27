# M04B Exploratory Statistical Analysis (`D-010C`)

- **Run ID:** `M04B_20261127_164911_DESKTOP-CQB09OU`
- **Status:** **EXPLORATORY ONLY** (Conditional on saved `Protocol A` validation predictions; NOT confirmatory)

## 1. Cluster Audit (`M04B_CLUSTER_AUDIT.csv`)
- **Validation Observations:** `3,060` (`510` gridline groups).
- **Image Clusters (`Series + Image`) Represented in Validation:** **`35`** out of `36` dataset image groups (one dataset image group has zero rows in Protocol A validation).
- **Resampling Estimand:** Pooled observation-weighted MAE (`sum(sampled_abs_err) / sum(sampled_n)`), `B = 10,000`, `seed = 42`, `95%` percentile CIs, identical cluster draw sequence across all `23` models and `2` historical references (`M04B_BOOTSTRAP_DRAWS.npz`).

## 2. Key Exploratory 95% Image-Cluster Bootstrap CIs

| Model | Raw MAE (µm) | 95% Bootstrap CI (µm) | Paired ΔMAE vs `ML01` (µm) | Paired 95% CI vs `ML01` | Paired ΔMAE vs `DLMwidth` (µm) | Paired 95% CI vs `DLMwidth` |
|---|---:|---|---:|---|---:|---|
| `ML01` Extra Trees | 14.25 | `[10.95, 18.32]` | — | — | `-0.34` | `[-0.97, +0.30]` |
| `FM03` TabICLv2 | 14.39 | `[10.63, 19.08]` | `+0.14` | `[-0.48, +0.88]` | `-0.20` | `[-0.96, +0.62]` |
| `ML02` Random Forest | 14.56 | `[11.17, 18.81]` | `+0.30` | `[+0.04, +0.62]` | `-0.03` | `[-0.62, +0.63]` |
| `ML04` XGBoost | 14.74 | `[11.49, 18.81]` | `+0.49` | `[+0.11, +0.88]` | `+0.15` | `[-0.53, +0.91]` |
| `ML06` CatBoost | 14.98 | `[11.50, 19.36]` | `+0.73` | `[+0.28, +1.25]` | `+0.39` | `[-0.41, +1.23]` |
| `ML05` LightGBM | 15.00 | `[11.66, 19.19]` | `+0.74` | `[+0.32, +1.15]` | `+0.41` | `[-0.26, +1.14]` |
| `DL03` RealMLP | 16.66 | `[13.10, 21.05]` | `+2.41` | `[+1.75, +3.12]` | `+2.07` | `[+0.91, +3.31]` |
| `DL02` FT-Transformer | 16.73 | `[13.19, 21.36]` | `+2.47` | `[+1.52, +3.53]` | `+2.13` | `[+0.89, +3.55]` |
| `RF05` DLM retrained | 17.49 | `[13.84, 22.15]` | `+3.24` | `[+1.99, +4.57]` | `+2.90` | `[+1.53, +4.53]` |
| `SG06` MultiROCKET-HYDRA | 22.33 | `[19.66, 25.65]` | `+8.08` | `[+6.87, +9.21]` | `+7.74` | `[+5.63, +9.85]` |
| `FM04` TabDPT | 23.90 | `[19.95, 28.29]` | `+9.65` | `[+8.13, +11.29]` | `+9.31` | `[+6.89, +11.79]` |

## 3. Interpretation Restrictions
- These CIs are **conditional on the single-seed (`seed=42`) Protocol A validation predictions** and do not capture training-seed variance, HPO variance, or cross-image generalization (`Protocol B`).
- No confirmatory hypothesis tests or p-values were executed; confirmatory testing is reserved for M08.
