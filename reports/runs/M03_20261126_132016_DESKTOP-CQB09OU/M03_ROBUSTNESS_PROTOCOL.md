# M03_ROBUSTNESS_PROTOCOL.md — Idea 2 Comparative Robustness Protocol (M03)

1. **Scope:** Deterministic synthetic corruptions (`P01..P16` in `M03_PERTURBATION_REGISTER.yaml`) applied exclusively to held-out validation/test copies (`[0, 255]` clipped), preserving `MANwidth` labels.
2. **Distinction:** Clearly labeled as **synthetic brightness-profile stress tests**, not physical camera/illumination acquisition experiments. Spatial shifts that remove crack boundaries are excluded.
3. **Experimental Separation:**
   - **Track 2A:** Standard training on clean folds + corrupted evaluation.
   - **Track 2B:** Profile preprocessing enhancement (e.g., SNV, Savitzky-Golay derivatives — `HY01`/`HY02` designs).
   - **Track 2C:** Training-fold-only augmentation (strictly no validation/test augmentation).
   - **Track 2D:** Unseen severity/corruption generalization (`P08..P16`).
4. **Selection Guard:** Never rank models solely by relative degradation (`(corr - clean)/clean`), because a weak baseline with high clean MAE can appear artificially "stable."
