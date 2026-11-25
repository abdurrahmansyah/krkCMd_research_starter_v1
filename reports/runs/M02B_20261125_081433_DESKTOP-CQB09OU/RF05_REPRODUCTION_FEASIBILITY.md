# RF05_REPRODUCTION_FEASIBILITY.md — Architecture-Based DLM Retraining Feasibility (M02B)

**Candidate:** `RF05` — DLM Retrained (Architecture-Based PyTorch Reproduction)  
**Primary Reference:** Jakubowski, J., & Tomczak, K. (2024). *"Deep learning metasensor for crack-width assessment and self-healing evaluation in concrete."* *Construction and Building Materials*, 422, 135768. DOI: `10.1016/j.conbuildmat.2024.135768`.  
**Distinction from `RF04`:** `RF05` is an **architecture-based retraining** feasibility study (starting from random weights on the project's group-aware split), strictly distinct from `RF04` (executing the authors' pretrained MATLAB `krknet.mat` checkpoint, which remains `CONDITIONAL` due to absent MATLAB / Deep Learning Toolbox).

---

## 1. Extracted Specification from 2024 Paper (Section 3.2.3 & Table 3) & `CrackWidthDLM_Matlab.m`

| Item | Verified Specification from Paper / Script | PyTorch Mapping (`src/models/m02b_adapters.py`) | Status |
|---|---|---|---|
| **1. Input representation** | `501 × 1 × 1` brightness profile (`XBet = reshape(XBet', 501, 1, 1, N)`), Table 3 Layer 1: *"501 × 1 × 1 images with normalization"* | `(batch, 1, 501)` float32 tensor | Verified |
| **2. Preprocessing** | MATLAB `imageInputLayer` default (`'zerocenter'` mean subtraction) | Raw `[0, 255]` or train-only mean centering (for synthetic test, raw `[0, 255]` used; train-only normalization recommended for future real runs) | Documented |
| **3–4. Conv Block 1 (Layers 2–4)** | Layer 2: `64` `4 × 1 × 1` convolutions, stride `[1 1]`, padding `'same'`; Layer 3: BatchNorm (`64` ch); Layer 4: `ReLU` | `Conv1d(1, 64, kernel_size=4, stride=1, padding="same") -> BatchNorm1d(64) -> ReLU()` | Exact |
| **5. Pooling 1 (Layer 5)** | `4 × 1` max pooling, stride `[2 2]`, padding `[0 0 0 0]` | `MaxPool1d(kernel_size=4, stride=2, padding=0)` | Exact |
| **6–8. Conv Block 2 (Layers 6–8)** | Layer 6: `32` `16 × 1 × 64` convolutions, stride `[1 1]`, padding `'same'`; Layer 7: BatchNorm (`32` ch); Layer 8: `ReLU` | `Conv1d(64, 32, kernel_size=16, stride=1, padding="same") -> BatchNorm1d(32) -> ReLU()` | Exact |
| **9. Pooling 2 (Layer 9)** | `4 × 1` max pooling, stride `[2 2]`, padding `[0 0 0 0]` | `MaxPool1d(kernel_size=4, stride=2, padding=0)` | Exact |
| **10–12. Conv Block 3 (Layers 10–12)** | Layer 10: `32` `32 × 1 × 32` convolutions, stride `[1 1]`, padding `'same'`; Layer 11: BatchNorm (`32` ch); Layer 12: `ReLU` | `Conv1d(32, 32, kernel_size=32, stride=1, padding="same") -> BatchNorm1d(32) -> ReLU()` | Exact |
| **13. Regularization (Layer 13)** | **20% dropout** | `Dropout(p=0.2)` | Exact |
| **14–15. Regression Head (Layers 14–15)** | Layer 14: `1` fully connected layer; Layer 15: Regression output (`MSE` loss) | `Flatten() -> LazyLinear(1)` with `MSELoss()` | Exact |
| **Training Settings (p. 6)** | **SGDM** (*stochastic gradient descent with momentum*), minibatch `128`, initial LR `10^-3`, final LR `10^-5`, `50` epochs *(Note: earlier M01 docs erroneously wrote Adam; corrected to SGDM)* | `torch.optim.SGD(..., lr=1e-3, momentum=0.9)` | Corrected |
| **Output Unit (`CrackWidthDLM_Matlab.m`)** | `pi2mi = 1000 * 25.4 / 6400 = 3.96875` µm/px; `DLMwidth(DLMwidth < 0) = 0` | Target `MANwidth` is already in µm; `pi2mi` applies only if network predicts in pixels | Documented |

---

## 2. Feasibility Conclusion

All 15 layers, kernel sizes, filter counts, pooling dimensions, dropout rate (`20%`), optimizer (`SGDM`), batch size (`128`), and epoch count (`50`) are **explicitly specified** in the 2024 paper. The PyTorch `RF05DLMRetrainedAdapter` in `src/models/m02b_adapters.py` faithfully implements this 15-layer architecture for bounded synthetic L0/L1/L2 testing on `cuda:0`. **No claim of exact numerical parity with `krknet.mat` (`RF04`) is made.**
