"""
src/models/m02c_adapters.py

Modular compatibility adapters for M02C:
  Track A: FM01 (TabPFN-3.5), FM02 (TabPFN-3.5-Fast), FM03 (TabICLv2), FM04 (TabDPT)
  Track B: DL04 (TabR official repo @ 17baa908), RF05 (DLM Table 3 with train-only zero-center + pi2mi)

All foundation checkpoints are cached locally under .cache/hf (gitignored).
Zero real krkCMd data is used; zero external API inference is performed.
"""

from __future__ import annotations

import importlib
import os
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import joblib
import numpy as np

from src.models.m02a_adapters import (
    EXPECTED_FEATURES,
    adapt_2d_to_3d_signal,
    validate_predictions,
    validate_tabular_inputs,
)

ROOT = Path(__file__).resolve().parents[2]
LOCAL_HF_CACHE = ROOT / ".cache" / "hf"


def configure_local_hf_cache() -> Path:
    LOCAL_HF_CACHE.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("HF_HOME", str(LOCAL_HF_CACHE))
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    return LOCAL_HF_CACHE


@dataclass
class BaseM02CAdapter:
    model_id: str
    environment_name: str
    expected_module: str
    expected_class: str
    random_state: int = 42
    n_threads: int = 16
    device_requested: str = "cuda:0"
    estimator: Any = field(default=None, init=False)
    device_used: str = field(default="cpu", init=False)
    checkpoint_load_time_sec: Optional[float] = field(default=None, init=False)
    fit_context_time_sec: Optional[float] = field(default=None, init=False)
    predict_time_sec: Optional[float] = field(default=None, init=False)
    peak_cuda_allocated_mb: Optional[float] = field(default=None, init=False)
    peak_cuda_reserved_mb: Optional[float] = field(default=None, init=False)
    extra_metadata: Dict[str, Any] = field(default_factory=dict, init=False)

    def build_config(self) -> Dict[str, Any]:
        raise NotImplementedError

    def create_estimator(self) -> Any:
        raise NotImplementedError

    def fit(self, X: np.ndarray, y: np.ndarray) -> "BaseM02CAdapter":
        raise NotImplementedError

    def predict(self, X: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    def save_and_reload_predict(self, X: np.ndarray) -> Dict[str, Any]:
        return {"supported": False, "reason": "Not implemented for this adapter"}

    def _record_cuda_mem(self) -> None:
        try:
            import torch
            if self.device_used.startswith("cuda") and torch.cuda.is_available():
                torch.cuda.synchronize()
                self.peak_cuda_allocated_mb = round(torch.cuda.max_memory_allocated(0) / (1024 ** 2), 3)
                self.peak_cuda_reserved_mb = round(torch.cuda.max_memory_reserved(0) / (1024 ** 2), 3)
        except Exception:
            pass

    def get_runtime_metadata(self) -> Dict[str, Any]:
        pkg_root = self.expected_module.split(".")[0]
        try:
            mod = importlib.import_module(pkg_root)
            pkg_ver = getattr(mod, "__version__", "unknown")
        except Exception:
            pkg_ver = "unknown"
        return {
            "model_id": self.model_id,
            "environment_name": self.environment_name,
            "python_executable": sys.executable,
            "package": pkg_root,
            "package_version": pkg_ver,
            "estimator_class": f"{self.expected_module}.{self.expected_class}",
            "config": self.build_config(),
            "device_requested": self.device_requested,
            "device_used": self.device_used,
            "checkpoint_load_time_sec": self.checkpoint_load_time_sec,
            "fit_context_time_sec": self.fit_context_time_sec,
            "predict_time_sec": self.predict_time_sec,
            "peak_cuda_allocated_mb": self.peak_cuda_allocated_mb,
            "peak_cuda_reserved_mb": self.peak_cuda_reserved_mb,
            **self.extra_metadata,
        }


# ---------------------------------------------------------------------------
# Track A: Foundation Models (.venv-foundation)
# ---------------------------------------------------------------------------

class FM01TabPFN35Adapter(BaseM02CAdapter):
    def __init__(self, random_state: int = 42, n_threads: int = 16, batch_size: Optional[int] = None) -> None:
        super().__init__("FM01", ".venv-foundation", "tabpfn", "TabPFNRegressor", random_state, n_threads, "cuda:0")
        self.batch_size = batch_size

    def build_config(self) -> Dict[str, Any]:
        return {
            "model_version": "v3.5 (default TabPFNRegressor)",
            "checkpoint": "Prior-Labs/tabpfn_3_5/tabpfn-v3.5-20260909.safetensors",
            "n_estimators": "auto",
            "inference_precision": "auto",
            "memory_saving_mode": "auto",
            "random_state": self.random_state,
            "n_preprocessing_jobs": 1,
        }

    def create_estimator(self) -> Any:
        configure_local_hf_cache()
        import torch
        from tabpfn import TabPFNRegressor
        if torch.cuda.is_available():
            torch.cuda.init()
            torch.cuda.reset_peak_memory_stats(0)
            self.device_used = "cuda:0"
        else:
            self.device_used = "cpu"
        t0 = time.perf_counter()
        self.estimator = TabPFNRegressor(
            device=self.device_used,
            random_state=self.random_state,
            inference_precision="auto",
            memory_saving_mode="auto",
            n_preprocessing_jobs=1,
            show_progress_bar=False,
        )
        self.checkpoint_load_time_sec = round(time.perf_counter() - t0, 4)
        self.extra_metadata.update({
            "checkpoint_repo": "Prior-Labs/tabpfn_3_5",
            "checkpoint_file": "tabpfn-v3.5-20260909.safetensors",
            "native_preprocessing": "TabPFN internal FeatureTransformer & quantile/power transforms",
            "internally_dropped_features": 0,
            "attention_backend": "PyTorch SDPA (Turing sm_75)",
        })
        return self.estimator

    def fit(self, X: np.ndarray, y: np.ndarray) -> "FM01TabPFN35Adapter":
        arr_x, arr_y = validate_tabular_inputs(X, y)
        if self.estimator is None:
            self.create_estimator()
        t0 = time.perf_counter()
        self.estimator.fit(arr_x, arr_y)
        self.fit_context_time_sec = round(time.perf_counter() - t0, 4)
        self.extra_metadata["available_training_rows"] = int(arr_x.shape[0])
        self._record_cuda_mem()
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        arr_x, _ = validate_tabular_inputs(X)
        t0 = time.perf_counter()
        raw = self.estimator.predict(arr_x)
        self.predict_time_sec = round(time.perf_counter() - t0, 4)
        self._record_cuda_mem()
        return validate_predictions(raw, arr_x.shape[0])

    def save_and_reload_predict(self, X: np.ndarray) -> Dict[str, Any]:
        arr_x, _ = validate_tabular_inputs(X)
        before = self.predict(arr_x)
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                p = Path(tmpdir) / "FM01.joblib"
                joblib.dump(self.estimator, p)
                loaded = joblib.load(p)
                after = validate_predictions(loaded.predict(arr_x), arr_x.shape[0])
                return {
                    "supported": True,
                    "format": "joblib",
                    "artifact_size_bytes": p.stat().st_size,
                    "max_reload_diff": float(np.max(np.abs(before - after))),
                    "consistent": bool(np.allclose(before, after, atol=1e-4)),
                }
        except Exception as exc:
            return {"supported": False, "error": f"{type(exc).__name__}: {exc}"}


class FM02TabPFN35FastAdapter(FM01TabPFN35Adapter):
    def __init__(self, random_state: int = 42, n_threads: int = 16) -> None:
        super().__init__(random_state, n_threads)
        self.model_id = "FM02"

    def build_config(self) -> Dict[str, Any]:
        return {
            "model_version": "ModelVersion.V3_5_FAST",
            "checkpoint": "Prior-Labs/tabpfn_3_5/tabpfn-v3.5-fast-20260909.safetensors",
            "random_state": self.random_state,
        }

    def create_estimator(self) -> Any:
        configure_local_hf_cache()
        import torch
        from tabpfn import TabPFNRegressor
        from tabpfn.constants import ModelVersion
        if torch.cuda.is_available():
            torch.cuda.init()
            torch.cuda.reset_peak_memory_stats(0)
            self.device_used = "cuda:0"
        else:
            self.device_used = "cpu"
        t0 = time.perf_counter()
        self.estimator = TabPFNRegressor.create_default_for_version(
            ModelVersion.V3_5_FAST,
            device=self.device_used,
            random_state=self.random_state,
            show_progress_bar=False,
        )
        self.checkpoint_load_time_sec = round(time.perf_counter() - t0, 4)
        self.extra_metadata.update({
            "checkpoint_repo": "Prior-Labs/tabpfn_3_5",
            "checkpoint_file": "tabpfn-v3.5-fast-20260909.safetensors",
            "native_preprocessing": "TabPFN-3.5-Fast internal preprocessing",
            "internally_dropped_features": 0,
            "attention_backend": "PyTorch SDPA (Turing sm_75)",
        })
        return self.estimator


class FM03TabICLv2Adapter(BaseM02CAdapter):
    def __init__(self, random_state: int = 42, n_threads: int = 16) -> None:
        super().__init__("FM03", ".venv-foundation", "tabicl", "TabICLRegressor", random_state, n_threads, "cuda:0")

    def build_config(self) -> Dict[str, Any]:
        return {
            "checkpoint_version": "tabicl-regressor-v2-20260212.ckpt",
            "n_estimators": 8,
            "batch_size": 1,
            "use_amp": "auto",
            "use_fa3": False,
            "random_state": self.random_state,
        }

    def create_estimator(self) -> Any:
        configure_local_hf_cache()
        import torch
        from tabicl import TabICLRegressor
        if torch.cuda.is_available():
            torch.cuda.init()
            torch.cuda.reset_peak_memory_stats(0)
            self.device_used = "cuda:0"
        else:
            self.device_used = "cpu"
        t0 = time.perf_counter()
        self.estimator = TabICLRegressor(
            n_estimators=8,
            batch_size=1,
            checkpoint_version="tabicl-regressor-v2-20260212.ckpt",
            device=self.device_used,
            use_amp="auto",
            use_fa3=False,
            random_state=self.random_state,
            n_jobs=self.n_threads,
            verbose=False,
        )
        self.checkpoint_load_time_sec = round(time.perf_counter() - t0, 4)
        self.extra_metadata.update({
            "checkpoint_repo": "jingang/TabICL",
            "checkpoint_file": "tabicl-regressor-v2-20260212.ckpt",
            "ensemble_size": 8,
            "attention_backend": "PyTorch SDPA (use_fa3=False for Turing sm_75)",
        })
        return self.estimator

    def fit(self, X: np.ndarray, y: np.ndarray) -> "FM03TabICLv2Adapter":
        arr_x, arr_y = validate_tabular_inputs(X, y)
        if self.estimator is None:
            self.create_estimator()
        t0 = time.perf_counter()
        self.estimator.fit(arr_x, arr_y)
        self.fit_context_time_sec = round(time.perf_counter() - t0, 4)
        self.extra_metadata["available_training_rows"] = int(arr_x.shape[0])
        self._record_cuda_mem()
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        arr_x, _ = validate_tabular_inputs(X)
        t0 = time.perf_counter()
        raw = self.estimator.predict(arr_x)
        self.predict_time_sec = round(time.perf_counter() - t0, 4)
        self._record_cuda_mem()
        return validate_predictions(raw, arr_x.shape[0])

    def save_and_reload_predict(self, X: np.ndarray) -> Dict[str, Any]:
        arr_x, _ = validate_tabular_inputs(X)
        before = self.predict(arr_x)
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                p = Path(tmpdir) / "FM03_tabicl.pkl"
                self.estimator.save(str(p))
                from tabicl import TabICLRegressor
                loaded = TabICLRegressor.load(str(p))
                after = validate_predictions(loaded.predict(arr_x), arr_x.shape[0])
                return {
                    "supported": True,
                    "format": "tabicl.save/load",
                    "artifact_size_bytes": p.stat().st_size,
                    "max_reload_diff": float(np.max(np.abs(before - after))),
                    "consistent": bool(np.allclose(before, after, atol=1e-4)),
                }
        except Exception as exc:
            return {"supported": False, "error": f"{type(exc).__name__}: {exc}"}


class FM04TabDPTAdapter(BaseM02CAdapter):
    def __init__(self, random_state: int = 42, n_threads: int = 16, context_size: int = 2048, n_ensembles: int = 8) -> None:
        super().__init__("FM04", ".venv-foundation", "tabdpt", "TabDPTRegressor", random_state, n_threads, "cuda:0")
        self.context_size = context_size
        self.n_ensembles = n_ensembles

    def build_config(self) -> Dict[str, Any]:
        return {
            "normalizer": "standard",
            "feature_reduction": "pca (native TabDPT compression if > max_features)",
            "context_reduction": "retrieval",
            "n_ensembles": self.n_ensembles,
            "context_size": self.context_size,
            "use_flash": False,
            "compile": False,
            "seed": self.random_state,
        }

    def create_estimator(self) -> Any:
        configure_local_hf_cache()
        import torch
        from tabdpt import TabDPTRegressor
        if torch.cuda.is_available():
            torch.cuda.init()
            torch.cuda.reset_peak_memory_stats(0)
            self.device_used = "cuda:0"
        else:
            self.device_used = "cpu"
        t0 = time.perf_counter()
        self.estimator = TabDPTRegressor(
            normalizer="standard",
            feature_reduction="pca",
            context_reduction="retrieval",
            faiss_metric="l2",
            device=self.device_used,
            use_flash=False,
            compile=False,
            verbose=False,
        )
        self.checkpoint_load_time_sec = round(time.perf_counter() - t0, 4)
        self.extra_metadata.update({
            "checkpoint_repo": "Layer6/TabDPT",
            "max_features_native": getattr(self.estimator, "max_features", "unknown"),
            "native_feature_reduction": "pca",
            "context_mechanism": "FAISS L2 retrieval (context_size per query)",
            "ensemble_size": self.n_ensembles,
            "attention_backend": "PyTorch SDPA (use_flash=False for Turing sm_75)",
        })
        return self.estimator

    def fit(self, X: np.ndarray, y: np.ndarray) -> "FM04TabDPTAdapter":
        arr_x, arr_y = validate_tabular_inputs(X, y)
        if self.estimator is None:
            self.create_estimator()
        t0 = time.perf_counter()
        self.estimator.fit(arr_x, arr_y)
        self.fit_context_time_sec = round(time.perf_counter() - t0, 4)
        self.extra_metadata["available_training_rows"] = int(arr_x.shape[0])
        self.extra_metadata["context_rows_per_query"] = min(self.context_size, int(arr_x.shape[0]))
        self._record_cuda_mem()
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        arr_x, _ = validate_tabular_inputs(X)
        t0 = time.perf_counter()
        ctx = min(self.context_size, self.extra_metadata.get("available_training_rows", self.context_size))
        raw = self.estimator.predict(arr_x, n_ensembles=self.n_ensembles, context_size=ctx, batch_size=128, seed=self.random_state)
        self.predict_time_sec = round(time.perf_counter() - t0, 4)
        self._record_cuda_mem()
        return validate_predictions(raw, arr_x.shape[0])

    def save_and_reload_predict(self, X: np.ndarray) -> Dict[str, Any]:
        arr_x, _ = validate_tabular_inputs(X)
        before = self.predict(arr_x)
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                p = Path(tmpdir) / "FM04_tabdpt.joblib"
                joblib.dump(self.estimator, p)
                loaded = joblib.load(p)
                ctx = min(self.context_size, self.extra_metadata.get("available_training_rows", self.context_size))
                after = validate_predictions(loaded.predict(arr_x, n_ensembles=self.n_ensembles, context_size=ctx, seed=self.random_state), arr_x.shape[0])
                return {
                    "supported": True,
                    "format": "joblib",
                    "artifact_size_bytes": p.stat().st_size,
                    "max_reload_diff": float(np.max(np.abs(before - after))),
                    "consistent": bool(np.allclose(before, after, atol=1e-4)),
                }
        except Exception as exc:
            return {"supported": False, "error": f"{type(exc).__name__}: {exc}"}


# ---------------------------------------------------------------------------
# Track B: DL04 Official TabR (.venv-tabr) & RF05 Normalized DLM (.venv-deep)
# ---------------------------------------------------------------------------

class DL04TabRAdapter(BaseM02CAdapter):
    """
    Faithful adapter around yandex-research/tabular-dl-tabr (pinned commit 17baa908).
    Runs on CPU with faiss-cpu IndexFlatL2 on Windows because faiss-gpu is Linux-only.
    Strictly isolates X_train/y_train candidate retrieval bank from evaluation queries.
    """

    def __init__(self, random_state: int = 42, n_threads: int = 16, epochs: int = 3, batch_size: int = 64, context_size: int = 32) -> None:
        super().__init__("DL04", ".venv-tabr", "bin.tabr", "Model", random_state, n_threads, "cpu")
        self.epochs = epochs
        self.batch_size = batch_size
        self.context_size = context_size
        self._train_x: Optional[Any] = None
        self._train_y: Optional[Any] = None
        self._x_mean: float = 0.0
        self._x_std: float = 1.0
        self._y_mean: float = 0.0
        self._y_std: float = 1.0

    def build_config(self) -> Dict[str, Any]:
        return {
            "repo_commit": "17baa9082506f8e7a0f8d11bb1e08212926a1507",
            "d_main": 64,
            "d_multiplier": 2.0,
            "encoder_n_blocks": 1,
            "predictor_n_blocks": 1,
            "context_size": self.context_size,
            "epochs": self.epochs,
            "batch_size": self.batch_size,
            "faiss_backend": "faiss.IndexFlatL2 (CPU on Windows)",
        }

    def _import_tabr_model(self) -> Any:
        tabr_root = ROOT / "data" / "external" / "tabular-dl-tabr"
        if not tabr_root.exists():
            raise FileNotFoundError(f"TabR repo not found at {tabr_root}")
        os.environ.setdefault("PROJECT_DIR", str(tabr_root))
        if str(tabr_root) not in sys.path:
            sys.path.insert(0, str(tabr_root))
        from bin.tabr import Model  # type: ignore
        return Model

    def _build_model(self) -> Any:
        Model = self._import_tabr_model()
        return Model(
            n_num_features=EXPECTED_FEATURES,
            n_bin_features=0,
            cat_cardinalities=[],
            n_classes=None,
            num_embeddings=None,
            d_main=64,
            d_multiplier=2.0,
            encoder_n_blocks=1,
            predictor_n_blocks=1,
            mixer_normalization="auto",
            context_dropout=0.1,
            dropout0=0.1,
            dropout1="dropout0",
            normalization="LayerNorm",
            activation="ReLU",
        )

    def create_estimator(self) -> Any:
        import torch
        torch.manual_seed(self.random_state)
        self.device_used = "cpu (faiss-cpu IndexFlatL2; faiss-gpu unsupported on Windows)"
        t0 = time.perf_counter()
        self.estimator = self._build_model().to("cpu")
        self.checkpoint_load_time_sec = round(time.perf_counter() - t0, 4)
        self.extra_metadata["param_count"] = sum(p.numel() for p in self.estimator.parameters())
        self.extra_metadata["repo_commit"] = "17baa9082506f8e7a0f8d11bb1e08212926a1507"
        return self.estimator

    def fit(self, X: np.ndarray, y: np.ndarray) -> "DL04TabRAdapter":
        import torch
        arr_x, arr_y = validate_tabular_inputs(X, y)
        if self.estimator is None:
            self.create_estimator()
        self._x_mean = float(arr_x.mean())
        self._x_std = float(arr_x.std()) + 1e-6
        self._y_mean = float(arr_y.mean())
        self._y_std = float(arr_y.std()) + 1e-6

        x_norm = torch.from_numpy(((arr_x - self._x_mean) / self._x_std).astype(np.float32))
        y_norm = torch.from_numpy(((arr_y - self._y_mean) / self._y_std).astype(np.float32))
        self._train_x = x_norm
        self._train_y = y_norm

        opt = torch.optim.AdamW(self.estimator.parameters(), lr=1e-3, weight_decay=1e-4)
        loss_fn = torch.nn.MSELoss()
        n = x_norm.shape[0]
        ctx = min(self.context_size, max(1, n - self.batch_size))
        gen = torch.Generator().manual_seed(self.random_state)

        t0 = time.perf_counter()
        self.estimator.train()
        for _ in range(self.epochs):
            perm = torch.randperm(n, generator=gen)
            for i in range(0, n, self.batch_size):
                b_idx = perm[i : i + self.batch_size]
                mask = torch.ones(n, dtype=torch.bool)
                mask[b_idx] = False
                cand_x = x_norm[mask]
                cand_y = y_norm[mask]
                if cand_x.shape[0] < 2:
                    continue
                cur_ctx = min(ctx, cand_x.shape[0])
                opt.zero_grad(set_to_none=True)
                out = self.estimator(
                    x_={"num": x_norm[b_idx]},
                    y=y_norm[b_idx],
                    candidate_x_={"num": cand_x},
                    candidate_y=cand_y,
                    context_size=cur_ctx,
                    is_train=True,
                ).squeeze(-1)
                loss = loss_fn(out, y_norm[b_idx])
                if not torch.isfinite(loss):
                    raise FloatingPointError("Non-finite TabR training loss.")
                loss.backward()
                opt.step()
        self.fit_context_time_sec = round(time.perf_counter() - t0, 4)
        self.extra_metadata["available_training_rows"] = int(n)
        self.extra_metadata["context_rows_per_query"] = min(self.context_size, int(n))
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        import torch
        arr_x, _ = validate_tabular_inputs(X)
        x_norm = torch.from_numpy(((arr_x - self._x_mean) / self._x_std).astype(np.float32))
        ctx = min(self.context_size, int(self._train_x.shape[0]))
        t0 = time.perf_counter()
        self.estimator.eval()
        preds = []
        with torch.no_grad():
            for i in range(0, x_norm.shape[0], self.batch_size):
                xb = x_norm[i : i + self.batch_size]
                out = self.estimator(
                    x_={"num": xb},
                    y=None,
                    candidate_x_={"num": self._train_x},
                    candidate_y=self._train_y,
                    context_size=ctx,
                    is_train=False,
                ).squeeze(-1)
                preds.append((out.numpy() * self._y_std) + self._y_mean)
        self.predict_time_sec = round(time.perf_counter() - t0, 4)
        return validate_predictions(np.concatenate(preds, axis=0), arr_x.shape[0])

    def save_and_reload_predict(self, X: np.ndarray) -> Dict[str, Any]:
        import torch
        arr_x, _ = validate_tabular_inputs(X)
        before = self.predict(arr_x)
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "DL04_tabr.pt"
            torch.save({
                "state_dict": self.estimator.state_dict(),
                "train_x": self._train_x,
                "train_y": self._train_y,
                "x_mean": self._x_mean,
                "x_std": self._x_std,
                "y_mean": self._y_mean,
                "y_std": self._y_std,
            }, p)
            ckpt = torch.load(p, map_location="cpu", weights_only=False)
            reloaded = DL04TabRAdapter(self.random_state, self.n_threads, self.epochs, self.batch_size, self.context_size)
            reloaded.create_estimator()
            reloaded.estimator.load_state_dict(ckpt["state_dict"])
            reloaded._train_x = ckpt["train_x"]
            reloaded._train_y = ckpt["train_y"]
            reloaded._x_mean = ckpt["x_mean"]
            reloaded._x_std = ckpt["x_std"]
            reloaded._y_mean = ckpt["y_mean"]
            reloaded._y_std = ckpt["y_std"]
            after = reloaded.predict(arr_x)
            return {
                "supported": True,
                "format": "pytorch_state_dict+retrieval_bank",
                "artifact_size_bytes": p.stat().st_size,
                "max_reload_diff": float(np.max(np.abs(before - after))),
                "consistent": bool(np.allclose(before, after, atol=1e-5)),
            }


class RF05DLMNormalizedAdapter(BaseM02CAdapter):
    """
    Corrected RF05 Table 3 15-layer 1D-CNN with training-only zero-center
    input normalization and pi2mi=3.96875 pixel target scaling, per
    Jakubowski & Tomczak (2024) & CrackWidthDLM_Matlab.m.
    """

    PI2MI = (1000.0 * 25.4) / 6400.0  # 3.96875 um/px

    def __init__(self, random_state: int = 42, n_threads: int = 16, epochs: int = 5, batch_size: int = 128) -> None:
        super().__init__("RF05", ".venv-deep", "torch.nn", "DLM15LayerCNN_Table3_Normalized", random_state, n_threads, "cuda:0")
        self.epochs = epochs
        self.batch_size = batch_size
        self.train_input_mean: float = 0.0

    def build_config(self) -> Dict[str, Any]:
        return {
            "table3_layers": 15,
            "input_normalization": "train-only global zero-center (X - mean_train)",
            "target_unit_during_training": "pixels (y_um / 3.96875); predictions scaled by pi2mi=3.96875 -> um",
            "optimizer": "SGD(lr=1e-3, momentum=0.9)",
            "epochs": self.epochs,
            "batch_size": self.batch_size,
        }

    def _build_model(self) -> Any:
        import torch.nn as nn
        return nn.Sequential(
            nn.Conv1d(1, 64, kernel_size=4, stride=1, padding="same"),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=4, stride=2, padding=0),
            nn.Conv1d(64, 32, kernel_size=16, stride=1, padding="same"),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=4, stride=2, padding=0),
            nn.Conv1d(32, 32, kernel_size=32, stride=1, padding="same"),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(p=0.2),
            nn.Flatten(),
            nn.LazyLinear(1),
        )

    def create_estimator(self) -> Any:
        import torch
        torch.manual_seed(self.random_state)
        if torch.cuda.is_available():
            torch.cuda.init()
            torch.cuda.manual_seed_all(self.random_state)
            torch.cuda.reset_peak_memory_stats(0)
            self.device_used = "cuda:0"
        else:
            self.device_used = "cpu"
        t0 = time.perf_counter()
        self.estimator = self._build_model().to(self.device_used)
        with torch.no_grad():
            _ = self.estimator(torch.zeros((2, 1, EXPECTED_FEATURES), device=self.device_used))
        self.checkpoint_load_time_sec = round(time.perf_counter() - t0, 4)
        self.extra_metadata["param_count"] = sum(p.numel() for p in self.estimator.parameters())
        return self.estimator

    def fit(self, X: np.ndarray, y: np.ndarray) -> "RF05DLMNormalizedAdapter":
        import torch
        from torch.utils.data import DataLoader, TensorDataset
        arr_x, arr_y = validate_tabular_inputs(X, y)
        if self.estimator is None:
            self.create_estimator()

        self.train_input_mean = float(arr_x.mean())
        x_zc = adapt_2d_to_3d_signal((arr_x - self.train_input_mean).astype(np.float32))
        y_px = (arr_y / self.PI2MI).astype(np.float32)

        dl = DataLoader(
            TensorDataset(torch.from_numpy(x_zc), torch.from_numpy(y_px)),
            batch_size=self.batch_size,
            shuffle=True,
            generator=torch.Generator().manual_seed(self.random_state),
        )
        opt = torch.optim.SGD(self.estimator.parameters(), lr=1e-3, momentum=0.9)
        loss_fn = torch.nn.MSELoss()

        t0 = time.perf_counter()
        self.estimator.train()
        for _ in range(self.epochs):
            for xb, yb in dl:
                xb, yb = xb.to(self.device_used), yb.to(self.device_used)
                opt.zero_grad(set_to_none=True)
                loss = loss_fn(self.estimator(xb).squeeze(-1), yb)
                if not torch.isfinite(loss):
                    raise FloatingPointError("Non-finite RF05 training loss.")
                loss.backward()
                for p in self.estimator.parameters():
                    if p.grad is not None and not torch.isfinite(p.grad).all():
                        raise FloatingPointError("Non-finite RF05 gradient.")
                opt.step()
        self.fit_context_time_sec = round(time.perf_counter() - t0, 4)
        self._record_cuda_mem()
        self.extra_metadata["train_input_mean"] = self.train_input_mean
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        import torch
        arr_x, _ = validate_tabular_inputs(X)
        x_zc = adapt_2d_to_3d_signal((arr_x - self.train_input_mean).astype(np.float32))
        x_t = torch.from_numpy(x_zc)
        t0 = time.perf_counter()
        self.estimator.eval()
        preds = []
        with torch.no_grad():
            for i in range(0, x_t.shape[0], self.batch_size):
                out_px = self.estimator(x_t[i : i + self.batch_size].to(self.device_used)).squeeze(-1)
                preds.append(out_px.detach().cpu().numpy() * self.PI2MI)
        self.predict_time_sec = round(time.perf_counter() - t0, 4)
        self._record_cuda_mem()
        return validate_predictions(np.concatenate(preds, axis=0), arr_x.shape[0])

    def save_and_reload_predict(self, X: np.ndarray) -> Dict[str, Any]:
        import torch
        arr_x, _ = validate_tabular_inputs(X)
        before = self.predict(arr_x)
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "RF05_norm.pt"
            torch.save({
                "state_dict": self.estimator.state_dict(),
                "train_input_mean": self.train_input_mean,
                "pi2mi": self.PI2MI,
            }, p)
            ckpt = torch.load(p, map_location=self.device_used, weights_only=False)
            reloaded = RF05DLMNormalizedAdapter(self.random_state, self.n_threads, self.epochs, self.batch_size)
            reloaded.create_estimator()
            reloaded.estimator.load_state_dict(ckpt["state_dict"])
            reloaded.train_input_mean = float(ckpt["train_input_mean"])
            after = reloaded.predict(arr_x)
            return {
                "supported": True,
                "format": "pytorch_state_dict+preprocessing_state",
                "artifact_size_bytes": p.stat().st_size,
                "max_reload_diff": float(np.max(np.abs(before - after))),
                "consistent": bool(np.allclose(before, after, atol=1e-5)),
            }


ADAPTER_REGISTRY_M02C = {
    "FM01": FM01TabPFN35Adapter,
    "FM02": FM02TabPFN35FastAdapter,
    "FM03": FM03TabICLv2Adapter,
    "FM04": FM04TabDPTAdapter,
    "DL04": DL04TabRAdapter,
    "RF05": RF05DLMNormalizedAdapter,
}


def get_m02c_adapter(model_id: str, **kwargs: Any) -> BaseM02CAdapter:
    if model_id not in ADAPTER_REGISTRY_M02C:
        raise KeyError(f"Unknown M02C model_id {model_id!r}. Allowed: {sorted(ADAPTER_REGISTRY_M02C)}")
    return ADAPTER_REGISTRY_M02C[model_id](**kwargs)
