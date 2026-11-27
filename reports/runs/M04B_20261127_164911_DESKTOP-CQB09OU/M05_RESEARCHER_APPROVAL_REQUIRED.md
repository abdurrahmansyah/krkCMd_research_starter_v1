# M05 Decisions Requiring Explicit Researcher Approval

1. **Finalist Roster Selection:** Approve one of Compact (5 HPO models), Balanced (9 HPO models), or Expanded (13 HPO models) — plus fixed reference anchors (`RF01`, `RF02`, `RF05`).
2. **M05 Inner Validation Split Scheme:** Approve whether M05 HPO tunes on `Series + Image` grouped inner CV inside Protocol A `train` (`12,216` rows) or nested inside `Protocol B` 3-fold outer training folds.
3. **Training Refit Policy After Early Stopping:** Approve retaining the best inner-validation early-stopped checkpoint vs refitting on all authorized training rows for `best_epoch`.
4. **Expensive / Unresolved Models:** Decide whether `SG02`, `SG03`, `FM04` (if still timed out) or `FM01`/`FM02` (if PriorLabs token provided) remain deferred or receive separate compute/implementation authorization.
5. **M05 Compute Budget Scenario:** Approve Compact (~1.5–2.5 h), Balanced (~4–7 h), or Expanded (~8–14 h) wall-clock budget.
