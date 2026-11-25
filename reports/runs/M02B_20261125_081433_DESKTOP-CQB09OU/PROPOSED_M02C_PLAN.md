# PROPOSED_M02C_PLAN.md — Proposed Foundation-Model Environment & Checkpoint Plan

**Prepared at:** End of M02B (`M02B_20261125_081433_DESKTOP-CQB09OU`)  
**Status:** **PROPOSED ONLY — NOT INSTALLED OR EXECUTED IN M02B**

1. **Isolated Environment (`.venv-foundation`, kernel `krkcmd-foundation`):**
   - Python `3.11.9` + `torch==2.9.1+cu128` (`--index-url https://download.pytorch.org/whl/cu128`)
   - `tabpfn==10.2.0`, `tabicl==2.2.0`, `tabdpt==1.3.2`, `huggingface_hub`, `scikit-learn==1.9.1`, `psutil`
   - Must pin `torch==2.9.1+cu128` + `--extra-index-url https://download.pytorch.org/whl/cu128` so `tabpfn`/`tabicl`/`tabdpt` do not pull PyPI CPU `torch 2.15.0`.
   - Must stay separate from `.venv-deep` because `tabdpt 1.3.2` constrains `faiss-cpu` to `1.12.0` vs `1.16.0` in `.venv-deep`.
2. **Checkpoint & License Gates:**
   - `FM01`/`FM02` (`TabPFN`): PriorLabs gated license acceptance required by researcher (`HF_HOME` inside `.cache/`, ignored by Git); 500-feature limit requires approved feature protocol.
   - `FM03` (`TabICLv2` / `tabicl 2.2.0`): Verify checkpoint terms before download.
   - `FM04` (`TabDPT` / `tabdpt 1.3.2`): Open weights (MIT code); requires chunked context for `N=12,216`.
3. **Turing `sm_75` Note:** Force PyTorch SDPA `mem_efficient`/`math` backend (no FlashAttention-2) and FP32/FP16 AMP (no native BF16/TF32).
