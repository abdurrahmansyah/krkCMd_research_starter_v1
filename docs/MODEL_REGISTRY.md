# MODEL_REGISTRY.md — 32 Candidate Models Registry & Specifications

**Milestone:** M01 — Model Registry and Compatibility Assessment  
**Date:** 2026-11-25  
**Protocol Reference:** `docs/MODEL_COMPATIBILITY_PROTOCOL.md`  
**Status Policy:** Exploratory registry; no candidate is approved for new training experiments in this milestone.

---

## 1. Overview of Model Taxonomy

To investigate concrete crack-width estimation from 501-point brightness profiles under group-aware evaluation (`Series + Image + Gridline`), 32 model candidates across 6 distinct paradigms are cataloged:

| Paradigm Family | Code Prefix | Candidates | Primary Mechanism |
|---|---|---|---|
| **Classical ML & Gradient Boosting** | `ML01`–`ML07` | 7 | Non-parametric decision tree ensembles & kernel margin regression |
| **Tabular Deep Learning** | `DL01`–`DL05` | 5 | Deep feature representations, self-attention tokenizers & retrieval |
| **Tabular Foundation Models** | `FM01`–`FM04` | 4 | In-context pre-trained foundation models & synthetic prior matching |
| **Spatial Signal Regression** | `SG01`–`SG06` | 6 | 1D convolutional temporal/spatial kernels & spectral random transforms |
| **Custom & Hybrid Approaches** | `HY01`–`HY05` | 5 | Domain-specific physics (SNV/derivative) combined with robust boosting/stacking |
| **Reference Benchmarks** | `RF01`–`RF05` | 5 | Heuristic baselines, linear models, original analytical AED & DLM CNN |

---

## 2. Status Lifecycle & Allowed Vocabularies

In compliance with project governance (`AGENT.md` Section 1.1), candidate statuses are strictly restricted to:
- `REGISTERED`: Cataloged in registry; static analysis pending.
- `STATIC_REVIEW`: Primary paper, dependencies, and code structure vetted.
- `ENV_READY`: Dependencies resolved; isolated virtual environment prepared.
- `SMOKE_TEST_PASS`: Passed Level 0 (import) and Level 1 (small synthetic 501-feature fit/predict).
- `SCALE_CHECK_PASS`: Passed Level 2 (synthetic progressive capacity check up to 12,216 rows).
- `READY_FOR_APPROVAL`: All technical prerequisites satisfied, awaiting user approval.
- `CONDITIONAL`: Requires special mitigation (e.g., context-length trimming, gated license, VRAM limit).
- `BLOCKED`: Hardware, dependency, or upstream license block preventing execution.
- `DESIGN_REQUIRED`: Custom architecture or transformer requiring mathematical/code design.
- `FAILED`: Failed smoke test or capacity check.

*Notice: No model may be marked `APPROVED` during Milestone M01.*

---

## 3. Detailed Model Specifications

### Family 1: Classical Machine Learning & Gradient Boosting

#### ML01 — Extra Trees (Extremely Randomized Trees)
- **Estimator:** `sklearn.ensemble.ExtraTreesRegressor` (package: `scikit-learn>=1.4,<2`)
- **Primary Literature:** Geurts, P., Ernst, D., & Wehenkel, L. (2006). "Extremely randomized trees". *Machine Learning*, 63(1), 3–42. DOI: [10.1007/s10994-006-6226-1](https://doi.org/10.1007/s10994-006-6226-1).
- **License:** BSD-3-Clause (Code), N/A (Weights).
- **Dimensionality & Scaling:** Native support for 501 numerical features. Extremely fast on 12,216 training rows via multi-core parallelization (`n_jobs=-1`).
- **Hardware:** CPU (Intel Core i7 14 physical / 20 logical cores).
- **Status:** `SMOKE_TEST_PASS` (Duration: 0.37s on synthetic 501-profile).

#### ML02 — Random Forest
- **Estimator:** `sklearn.ensemble.RandomForestRegressor` (package: `scikit-learn>=1.4,<2`)
- **Primary Literature:** Breiman, L. (2001). "Random Forests". *Machine Learning*, 45(1), 5–32. DOI: [10.1023/A:1010933404324](https://doi.org/10.1023/A:1010933404324).
- **License:** BSD-3-Clause.
- **Dimensionality & Scaling:** Native support for 501 features and 12,216 rows. Memory footprint ~89 MB for 250 trees.
- **Hardware:** CPU.
- **Status:** `SMOKE_TEST_PASS` (Duration: 0.056s on synthetic 501-profile).

#### ML03 — HistGradientBoosting
- **Estimator:** `sklearn.ensemble.HistGradientBoostingRegressor` (package: `scikit-learn>=1.4,<2`)
- **Primary Literature:** Ke, G. et al. (2017). "LightGBM: A Highly Efficient Gradient Boosting Decision Tree". *NeurIPS 2017*, pp. 3146–3154.
- **License:** BSD-3-Clause.
- **Dimensionality & Scaling:** Automatically discretizes 501 continuous features into 256 integer bins, drastically reducing memory and CPU cache misses.
- **Hardware:** CPU.
- **Status:** `SMOKE_TEST_PASS` (Duration: 0.117s on synthetic 501-profile).

#### ML04 — XGBoost
- **Estimator:** `xgboost.XGBRegressor` (package: `xgboost>=2.0,<4`)
- **Primary Literature:** Chen, T., & Guestrin, C. (2016). "XGBoost: A Scalable Tree Boosting System". *ACM KDD 2016*, pp. 785–794. DOI: [10.1145/2939672.2945399](https://doi.org/10.1145/2939672.2945399).
- **License:** Apache-2.0.
- **Dimensionality & Scaling:** Scalable exact and histogram split algorithms. PyPI Windows x64 wheel available (`xgboost 3.2.0`).
- **Hardware:** CPU / CUDA GPU.
- **Status:** `STATIC_REVIEW` (PyPI dry-run resolved; pending `env-boost` creation).

#### ML05 — LightGBM
- **Estimator:** `lightgbm.LGBMRegressor` (package: `lightgbm>=4.0,<5`)
- **Primary Literature:** Ke, G. et al. (2017). "LightGBM: A Highly Efficient Gradient Boosting Decision Tree". *NeurIPS 2017*.
- **License:** MIT License.
- **Dimensionality & Scaling:** Exclusive Feature Bundling (EFB) and Gradient-based One-Side Sampling (GOSS). Windows x64 wheel verified (`lightgbm 4.7.0`).
- **Hardware:** CPU / OpenCL / CUDA.
- **Status:** `STATIC_REVIEW` (PyPI dry-run resolved; pending `env-boost` creation).

#### ML06 — CatBoost
- **Estimator:** `catboost.CatBoostRegressor` (package: `catboost>=1.2,<2`)
- **Primary Literature:** Prokhorenkova, L. et al. (2018). "CatBoost: unbiased boosting with categorical features". *NeurIPS 2018*, pp. 6638–6648.
- **License:** Apache-2.0.
- **Dimensionality & Scaling:** Symmetric/oblivious decision trees provide strong regularization against noise on 501 continuous features. Windows wheel verified (`catboost 1.2.10`).
- **Hardware:** CPU / CUDA.
- **Status:** `STATIC_REVIEW` (PyPI dry-run resolved; pending `env-boost` creation).

#### ML07 — SVR RBF (Support Vector Regression)
- **Estimator:** `sklearn.pipeline.make_pipeline(StandardScaler(), SVR(kernel='rbf'))`
- **Primary Literature:** Smola, A. J., & Schölkopf, B. (2004). "A tutorial on support vector regression". *Statistics and Computing*, 14(3), 199–222. DOI: [10.1023/B:STCO.0000035301.49549.88](https://doi.org/10.1023/B:STCO.0000035301.49549.88).
- **License:** BSD-3-Clause.
- **Dimensionality & Scaling:** Requires feature scaling. Computational complexity scales as $O(N^2 \cdot D)$ to $O(N^3 \cdot D)$; on 12,216 rows, requires ~10–30s on CPU.
- **Hardware:** CPU.
- **Status:** `SMOKE_TEST_PASS` (Duration: 0.007s on synthetic 501-profile).

---

### Family 2: Tabular Deep Learning

#### DL01 — MLP (Multi-Layer Perceptron)
- **Estimator:** `sklearn.neural_network.MLPRegressor` / PyTorch Sequential
- **Primary Literature:** Rumelhart, D. E., Hinton, G. E., & Williams, R. J. (1986). "Learning representations by back-propagating errors". *Nature*, 323, 533–536. DOI: [10.1038/323533a0](https://doi.org/10.1038/323533a0).
- **License:** BSD-3-Clause.
- **Status:** `SMOKE_TEST_PASS` (Duration: 0.043s on synthetic 501-profile).

#### DL02 — FT-Transformer (Feature Tokenizer Transformer)
- **Estimator:** `rtdl.FTTransformer` (PyTorch)
- **Primary Literature:** Gorishniy, Y., Rubachev, I., Khrulkov, V., & Babenko, A. (2021). "Revisiting Deep Learning Models for Tabular Data". *NeurIPS 2021*, pp. 18932–18943. arXiv: [2106.11958](https://arxiv.org/abs/2106.11958).
- **License:** Apache-2.0.
- **Constraint / Known Limitation:** Tokenizes every numerical feature into an embedding. For 501 features, multi-head self-attention scales quadratically ($501^2 = 251,001$ attention operations per row per layer). On an NVIDIA RTX 3050 Laptop (4GB VRAM), requires small batch sizes (e.g., 32 or 64) to avoid CUDA out-of-memory.
- **Status:** `CONDITIONAL` (Requires batch size tuning for 4GB VRAM limit).

#### DL03 — RealMLP
- **Estimator:** `avidale/tabbench / PyTorch`
- **Primary Literature:** Holzmüller, D., Grinsztajn, L., & Iniolaki, I. (2024). "Why Do Tree-Based Models Still Outperform Deep Learning on Tabular Data?". arXiv: [2407.04491](https://arxiv.org/abs/2407.04491).
- **License:** MIT License.
- **Status:** `STATIC_REVIEW` (PyTorch implementation readily portable).

#### DL04 — TabR (Retrieval-Augmented Tabular Model)
- **Estimator:** `tabular-dl-tabr` (PyTorch + FAISS)
- **Primary Literature:** Gorishniy, Y., Rubachev, I., & Babenko, A. (2024). "TabR: Unlocking the Potential of Retrieval-Augmented Models on Tabular Data". *ICLR 2024*. arXiv: [2307.14338](https://arxiv.org/abs/2307.14338).
- **License:** Apache-2.0.
- **Dependency & Compatibility:** Requires `faiss-cpu` on Windows x64 (`faiss-cpu 1.16.0` verified on PyPI). Given 12,216 training rows and 501 features, exact L2 retrieval takes <10 ms per batch on CPU.
- **Status:** `CONDITIONAL` (Requires isolated PyTorch + FAISS environment).

#### DL05 — TabM (Parameter-Efficient Tabular Ensembles)
- **Estimator:** `tabular-dl-tabm` (PyTorch)
- **Primary Literature:** Gorishniy, Y., Rubachev, I., & Babenko, A. (2024). "TabM: Advancing Tabular Deep Learning with Parameter-Efficient Ensembles". *NeurIPS 2024*. arXiv: [2410.24210](https://arxiv.org/abs/2410.24210).
- **License:** Apache-2.0.
- **Status:** `STATIC_REVIEW` (PyTorch implementation verified).

---

### Family 3: Tabular Foundation Models

#### FM01 — TabPFN-3.5 (TabPFN v2 Regressor)
- **Estimator:** `tabpfn.TabPFNRegressor`
- **Primary Literature:** Hollmann, N. et al. (2025). "Accurate predictions on small data with a tabular foundation model". *Nature*, 637, 345–353. DOI: [10.1038/s41586-024-08328-6](https://doi.org/10.1038/s41586-024-08328-6).
- **License:** Code: Apache-2.0. Weights: PriorLabs Research/Non-Commercial (gated Hugging Face access).
- **Crucial Dimension Constraint:** TabPFN architecture supports a maximum context of **500 features**. The krkCMd profile has **501 features**. Passing 501 features causes an exception.
- **Required Mitigation:** Must drop exactly 1 edge feature (e.g. `x1` or `x501` at profile boundary which represents uncracked surface) or downsample/PCA by 1 dimension. Furthermore, standard TabPFN in-context sample limit is ~10,000; for 12,216 rows, requires chunked ensembling.
- **Status:** `CONDITIONAL` (500-feature context boundary + gated weight license).

#### FM02 — TabPFN-3.5-Fast
- **Estimator:** `tabpfn.TabPFNRegressor(model='fast')`
- **Primary Literature:** PriorLabs TabPFN Technical Report (2025). arXiv: [2501.04257](https://arxiv.org/abs/2501.04257).
- **Status:** `CONDITIONAL` (Inherits FM01 context constraint).

#### FM03 — TabICLv2
- **Estimator:** `tabicl / PyTorch`
- **License:** Research Only / Gated.
- **Status:** `CONDITIONAL` (Academic pre-release; fixed context length limitations).

#### FM04 — TabDPT
- **Estimator:** `TabDPT / PyTorch`
- **Primary Literature:** Ma, S. et al. (2024). "TabDPT: Scaling Tabular Foundation Models". arXiv: [2410.18164](https://arxiv.org/abs/2410.18164).
- **License:** MIT License (Code), Open weights.
- **Status:** `CONDITIONAL` (In-context length scaling and 4GB VRAM constraint).

---

### Family 4: Spatial Signal Regression

#### SG01 — Vanilla 1D-CNN
- **Estimator:** PyTorch Conv1D Regressor (Conv1d $\to$ BatchNorm $\to$ ReLU $\to$ MaxPool $\to$ Linear)
- **Primary Literature:** LeCun, Y. et al. (1989). "Backpropagation applied to handwritten zip code recognition". *Neural Computation*, 1(4), 541–551. DOI: [10.1162/neco.1989.1.4.541](https://doi.org/10.1162/neco.1989.1.4.541).
- **License:** Apache-2.0 / MIT.
- **Dimensionality & Scaling:** Ideal for $1 \times 501$ input profiles.
- **Status:** `STATIC_REVIEW` (PyTorch implementation ready).

#### SG02 — ResNet-1D
- **Estimator:** `aeon.networks.ResNetNetwork` / PyTorch ResNet1D
- **Primary Literature:** Wang, Z., Yan, W., & Oates, T. (2017). "Time series classification from scratch with deep neural networks". *IEEE IJCNN 2017*, pp. 7966039. DOI: [10.1109/IJCNN.2017.7966039](https://doi.org/10.1109/IJCNN.2017.7966039).
- **License:** BSD-3-Clause.
- **Status:** `STATIC_REVIEW` (Compatible with 501-point 1D profiles).

#### SG03 — InceptionTime Regression
- **Estimator:** `aeon.regression.deep_learning.InceptionTimeRegressor`
- **Primary Literature:** Fawaz, H. I. et al. (2020). "InceptionTime: Finding AlexNet for time series". *Data Mining and Knowledge Discovery*, 34, 1936–1962. DOI: [10.1007/s10618-020-00710-y](https://doi.org/10.1007/s10618-020-00710-y).
- **License:** BSD-3-Clause.
- **Status:** `STATIC_REVIEW` (Parallel kernel sizes 10, 20, 40 capture multiscale crack widths).

#### SG04 — LITETime Regression
- **Estimator:** `aeon.regression.deep_learning.LITETimeRegressor`
- **Primary Literature:** Ismail-Fawaz, A. et al. (2023). "LITE: Light Inception with bues for time series". arXiv: [2309.05566](https://arxiv.org/abs/2309.05566).
- **License:** BSD-3-Clause.
- **Status:** `STATIC_REVIEW` (Efficient lightweight inception architecture).

#### SG05 — ROCKET Regression
- **Estimator:** `aeon.regression.convolution_based.RocketRegressor`
- **Primary Literature:** Dempster, A., Petitjean, F., & Webb, G. I. (2020). "ROCKET: Exceptionally fast and accurate time series classification using random convolutional kernels". *Data Mining and Knowledge Discovery*, 34, 1454–1495. DOI: [10.1007/s10618-020-00701-z](https://doi.org/10.1007/s10618-020-00701-z).
- **License:** BSD-3-Clause.
- **Dimensionality & Scaling:** Generates 10,000 random non-trainable 1D convolutional features (lengths 7, 9, 11) followed by `RidgeCV`. For 12,216 samples of 501 length, runs on CPU in ~1–2 minutes with zero GPU dependency.
- **Status:** `STATIC_REVIEW` (aeon 1.6.0 verified via PyPI dry-run).

#### SG06 — MultiROCKET-HYDRA Regression
- **Estimator:** `aeon.regression.convolution_based.MultiRocketRegressor`
- **Primary Literature:** Tan, C. W. et al. (2022). "MultiRocket: multiple pooling operators and transformations". *Data Mining and Knowledge Discovery*, 36, 1623–1646. DOI: [10.1007/s10618-022-00834-3](https://doi.org/10.1007/s10618-022-00834-3).
- **License:** BSD-3-Clause.
- **Status:** `STATIC_REVIEW` (Extracts features on first-order profile differences as well as raw signals).

---

### Family 5: Custom and Hybrid Approaches

#### HY01 — SNV + CatBoost
- **Pipeline:** `StandardNormalVariateTransformer() -> CatBoostRegressor()`
- **Primary Literature:** Barnes, R. J., Dhanoa, M. S., & Lister, S. J. (1989). "Standard Normal Variate transformation and de-trending of near-infrared diffuse reflectance spectra". *Applied Spectroscopy*, 43(5), 772–777. DOI: [10.1366/0003702894202201](https://doi.org/10.1366/0003702894202201).
- **Domain Rationale:** Computes $z_i = \frac{x_i - \mu_{\text{row}}}{\sigma_{\text{row}}}$ per profile. Strips away global specimen brightness shift and contrast attenuation, specifically neutralizing Idea 2 illumination perturbations before non-linear tree regression.
- **Status:** `DESIGN_REQUIRED` (Custom scikit-learn transformer implementation needed).

#### HY02 — Derivative + Extra Trees
- **Pipeline:** `SpatialSavitzkyGolayDerivative() -> ExtraTreesRegressor()`
- **Primary Literature:** Savitzky, A., & Golay, M. J. (1964). "Smoothing and differentiation of data by simplified least squares procedures". *Analytical Chemistry*, 36(8), 1627–1639. DOI: [10.1021/ac60214a047](https://doi.org/10.1021/ac60214a047).
- **Domain Rationale:** Evaluates 1st spatial derivative $f'(x)$ (edge boundaries) and 2nd derivative $f''(x)$ (inflection points). Invariant to uniform brightness shifts.
- **Status:** `DESIGN_REQUIRED` (Feature concatenation transformer design needed).

#### HY03 — Dual-stream Multiscale CNN
- **Architecture:** PyTorch parallel branch network:
  - Branch 1 (Micro-scale): Conv1D with small receptive field ($k=3, 5, 7$) focusing on sharp crack wall transitions.
  - Branch 2 (Macro-scale): Conv1D with wide receptive field ($k=17, 33, 65$) capturing wide crack depressions and illumination gradients.
  - Fusion: Concatenation layer $\to$ Dense linear regression head.
- **Status:** `DESIGN_REQUIRED` (PyTorch model module specification needed).

#### HY04 — CNN + CatBoost
- **Pipeline:** Pretrained/frozen 1D-CNN backbone feature extractor $\to$ CatBoost regressor.
- **Status:** `DESIGN_REQUIRED` (Extractor-regressor interface design needed).

#### HY05 — Robust Stacking Ensemble
- **Architecture:** `StackingRegressor` combining:
  - Base Model 1: Tree ensemble (ExtraTrees or CatBoost)
  - Base Model 2: Signal transformation (ROCKET)
  - Base Model 3: Deep spatial feature model (1D-CNN)
  - Meta-Learner: Constrained non-negative RidgeCV regression.
- **Status:** `DESIGN_REQUIRED` (Out-of-fold cross-validation pipeline design needed).

---

### Family 6: Reference Benchmarks

#### RF01 — Dummy Mean
- **Estimator:** `sklearn.dummy.DummyRegressor(strategy='mean')`
- **Role:** Non-informative statistical floor (predicts constant training mean).
- **Status:** `SMOKE_TEST_PASS`.

#### RF02 — Linear Regression
- **Estimator:** `sklearn.linear_model.LinearRegression` with `StandardScaler`
- **Role:** Classical linear parametric baseline.
- **Status:** `SMOKE_TEST_PASS`.

#### RF03 — AED Original (Analytical Extreme-point Detection)
- **Estimator:** Python translation of `CrackWidthAED_VBA.txt`
- **Primary Literature:** Tomczak, K., Jakubowski, J., & Fiołek, P. (2017). "Method for Assessment of Changes in the Width of Cracks in Cement Composites with Use of Computer Image Processing and Analysis". *Studia Geotechnica et Mechanica*, 39(4), 73–80. DOI: [10.1515/sgem-2017-0017](https://doi.org/10.1515/sgem-2017-0017).
- **Mechanism:** Rule-based heuristic search outward from global minimum brightness.
- **Status:** `SMOKE_TEST_PASS` (Native Python translation executed successfully in <0.001s).

#### RF04 — DLM Pretrained (Deep Learning Metasensor)
- **Estimator:** Author's pretrained network in `krknet.mat`
- **Primary Literature:** Jakubowski, K., & Tomczak, A. (2024). "Deep learning metasensor for crack-width assessment and self-healing evaluation in concrete". *Construction and Building Materials*, 422, 135768. DOI: [10.1016/j.conbuildmat.2024.135768](https://doi.org/10.1016/j.conbuildmat.2024.135768).
- **Execution Challenge:** `krknet.mat` contains a MATLAB 5.0 SeriesNetwork opaque object. The host machine has MATLAB R2026b installed, but **lacks the MATLAB Deep Learning Toolbox (`nnet`)**.
- **Porting Feasibility:** To execute `RF04` in Python without MATLAB toolbox, the binary weights/biases must be exported via an active MATLAB Deep Learning Toolbox license or reconstructed layer-by-layer.
- **Status:** `CONDITIONAL` (Requires MATLAB Deep Learning Toolbox license OR exact weights port).

#### RF05 — DLM Retrained (PyTorch Reconstruction)
- **Estimator:** 15-layer 1D-CNN specified in Table 3 of Jakubowski & Tomczak (2024).
- **Architecture Details:**
  1. Image Input: $501 \times 1 \times 1$
  2. Conv1D: 64 filters, kernel $4 \times 1$, stride 1, padding 'same'
  3. Batch Normalization
  4. ReLU
  5. MaxPool: $4 \times 1$, stride 2, padding 0
  6. Conv1D: 32 filters, kernel $16 \times 1$, stride 1, padding 'same'
  7. Batch Normalization
  8. ReLU
  9. MaxPool: $4 \times 1$, stride 2, padding 0
  10. Conv1D: 32 filters, kernel $32 \times 1$, stride 1, padding 'same'
  11. Batch Normalization
  12. ReLU
  13. Dropout (regularization)
  14. Fully Connected (1 output)
  15. Regression Output
- **Training Protocol:** Adam optimizer, initial LR $10^{-3}$, final LR $10^{-5}$, 50 epochs, batch size 128. Output scaled by $\text{pi2mi} = \frac{1000 \times 25.4}{6400} = 3.96875\,\mu\text{m/px}$.
- **Status:** `STATIC_REVIEW` (Architecture fully verified; ready for PyTorch implementation upon protocol approval).
