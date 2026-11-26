# DL04_TABR_INTEGRATION_REPORT.md — Official TabR Repository Integration (M02C)

**Candidate:** `DL04` — TabR (`bin.tabr.Model`)  
**Official Repository:** `https://github.com/yandex-research/tabular-dl-tabr`  
**Pinned Commit SHA:** `17baa9082506f8e7a0f8d11bb1e08212926a1507` (MIT License)  
**Local Clone Path:** `data/external/tabular-dl-tabr` (gitignored)  
**Environment:** `.venv-tabr` (`krkcmd-tabr`, Python `3.11.9`, `torch==2.9.1+cu128`, `faiss-cpu==1.16.0`, `delu==0.0.26`, `tomli-w==1.2.0`, `tensorboard==2.21.0`)

---

## Integration & Isolation Summary
1. **Retrieval Backend:** Official `bin.tabr.Model` uses `faiss.IndexFlatL2(d_main)` on **CPU** because `faiss-gpu` is Linux-only (`device_used = "cpu (faiss-cpu IndexFlatL2; faiss-gpu unsupported on Windows)"`).
2. **Strict Context Isolation:** During `fit(X_train, y_train)`, batch indices are masked out from `candidate_x_`/`candidate_y` (with `is_train=True` self-exclusion). During `predict(X_test)`, `is_train=False` and `y=None` ensure evaluation queries never enter the labeled retrieval database.
3. **M02C Results:**
   - **L0:** `PASS` (`86,529` params)
   - **L1 (`100 -> 20`):** `PASS` (`0.1251 s` fit, `0.0018 s` pred, serialization `max_reload_diff = 0.0`, `0` negative predictions)
   - **L2A (`1,000 -> 200`):** `PASS` (`0.9521 s` fit, `0.0141 s` pred)
   - **L2B (`4,096 -> 1,024`):** `PASS` (`6.9425 s` fit, `0.0691 s` pred)
   - **L2C (`12,216 -> 3,822`):** `PASS` (`47.1521 s` fit, `0.8957 s` pred)
4. **Status:** **`SCALE_CHECK_PASS`** (CPU `faiss-cpu`).
