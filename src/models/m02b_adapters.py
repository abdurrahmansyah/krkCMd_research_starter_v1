"""
src/models/m02b_adapters.py

Lightweight, reusable compatibility adapters for M02B deep-learning, GPU,
neural-signal, SG06-retry, and RF05 architecture-based candidates.

All configurations are bounded synthetic compatibility-test settings,
NOT research hyperparameters.
"""

from __future__ import annotations

import importlib
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


@dataclass
class BaseM02BAdapter:
    model_id: str
    environment_name: str
    expected_module: str
    expected_class: str
    input_mode: str  # "2d" or "3d_signal"
    random_state: int = 42
    n_threads: int = 16
    device_requested: str = "cpu"
    config_label: str = "compatibility_bounded"
    estimator: Any = field(default=None, init=False)
    device_used: str = field(default="cpu", init=False)
    fit_time_sec: Optional[float] = field(default=None, init=False)
    predict_time_sec: Optional[float] = field(default=None, init=False)
    param_count: Optional[int] = field(default=None, init=False)
    last_loss_finite: Optional[bool] = field(default=None, init=False)
    last_grad_finite: Optional[bool] = field(default=None, init=False)
    peak_cuda_allocated_mb: Optional[float] = field(default=None, init=False)
    peak_cuda_reserved_mb: Optional[float] = field(default=None, init=False)
    extra_metadata: Dict[str, Any] = field(default_factory=dict, init=False)

    def build_config(self) -> Dict[str, Any]:
        raise NotImplementedError

    def create_estimator(self) -> Any:
        raise NotImplementedError

    def fit(self, X: np.ndarray, y: np.ndarray) -> "BaseM02BAdapter":
        raise NotImplementedError

    def predict(self, X: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    def save_and_reload_predict(self, X: np.ndarray) -> Dict[str, Any]:
        raise NotImplementedError

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
            "input_mode": self.input_mode,
            "config_label": self.config_label,
            "config": self.build_config(),
            "random_state": self.random_state,
            "n_threads": self.n_threads,
            "device_requested": self.device_requested,
            "device_used": self.device_used,
            "param_count": self.param_count,
            "last_loss_finite": self.last_loss_finite,
            "last_grad_finite": self.last_grad_finite,
            "peak_cuda_allocated_mb": self.peak_cuda_allocated_mb,
            "peak_cuda_reserved_mb": self.peak_cuda_reserved_mb,
            "fit_time_sec": self.fit_time_sec,
            "predict_time_sec": self.predict_time_sec,
            **self.extra_metadata,
        }


# ---------------------------------------------------------------------------
# PyTorch-based Adapters (.venv-deep)
# ---------------------------------------------------------------------------

class _PyTorchBaseAdapter(BaseM02BAdapter):
    def _setup_torch(self) -> Any:
        import torch
        torch.manual_seed(self.random_state)
        if torch.cuda.is_available() and self.device_requested.startswith("cuda"):
            torch.cuda.init()
            torch.cuda.manual_seed_all(self.random_state)
            self.device_used = "cuda:0"
            torch.cuda.reset_peak_memory_stats(0)
        else:
            self.device_used = "cpu"
        return torch

    def _record_cuda_mem(self, torch: Any) -> None:
        if self.device_used.startswith("cuda"):
            torch.cuda.synchronize()
            self.peak_cuda_allocated_mb = round(torch.cuda.max_memory_allocated(0) / (1024 ** 2), 3)
            self.peak_cuda_reserved_mb = round(torch.cuda.max_memory_reserved(0) / (1024 ** 2), 3)

    def _train_torch_loop(
        self,
        torch: Any,
        model: Any,
        X_tensor: Any,
        y_tensor: Any,
        epochs: int,
        batch_size: int,
        lr: float,
        optimizer_name: str = "adam",
    ) -> None:
        from torch.utils.data import DataLoader, TensorDataset

        model.to(self.device_used)
        self.param_count = sum(p.numel() for p in model.parameters())
        if optimizer_name == "sgd_momentum":
            opt = torch.optim.SGD(model.parameters(), lr=lr, momentum=0.9)
        else:
            opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
        loss_fn = torch.nn.MSELoss()
        ds = TensorDataset(X_tensor, y_tensor)
        gen = torch.Generator().manual_seed(self.random_state)
        dl = DataLoader(ds, batch_size=batch_size, shuffle=True, generator=gen)

        model.train()
        loss_finite = True
        grad_finite = True
        for _ in range(epochs):
            for xb, yb in dl:
                xb = xb.to(self.device_used)
                yb = yb.to(self.device_used)
                opt.zero_grad(set_to_none=True)
                out = self._forward_for_loss(model, xb)
                loss = loss_fn(out, yb)
                if not torch.isfinite(loss):
                    loss_finite = False
                    raise FloatingPointError("Non-finite training loss encountered.")
                loss.backward()
                for p in model.parameters():
                    if p.grad is not None and not torch.isfinite(p.grad).all():
                        grad_finite = False
                        raise FloatingPointError("Non-finite gradient encountered.")
                opt.step()
        self.last_loss_finite = loss_finite
        self.last_grad_finite = grad_finite

    def _forward_for_loss(self, model: Any, xb: Any) -> Any:
        return model(xb).squeeze(-1)

    def _predict_torch(self, torch: Any, model: Any, X_tensor: Any, batch_size: int) -> np.ndarray:
        model.eval()
        preds = []
        with torch.no_grad():
            for i in range(0, X_tensor.shape[0], batch_size):
                xb = X_tensor[i : i + batch_size].to(self.device_used)
                out = self._forward_for_loss(model, xb)
                preds.append(out.detach().cpu().numpy())
        return np.concatenate(preds, axis=0)

    def save_and_reload_predict(self, X: np.ndarray) -> Dict[str, Any]:
        import torch
        arr_x, _ = validate_tabular_inputs(X)
        preds_before = self.predict(arr_x)
        with tempfile.TemporaryDirectory() as tmpdir:
            ckpt = Path(tmpdir) / f"{self.model_id}.pt"
            torch.save(self.estimator.state_dict(), ckpt)
            reloaded = self._build_model()
            reloaded.load_state_dict(torch.load(ckpt, map_location=self.device_used, weights_only=True))
            reloaded.to(self.device_used)
            X_t = self._make_tensor(torch, arr_x)
            preds_after = validate_predictions(self._predict_torch(torch, reloaded, X_t, self.batch_size), arr_x.shape[0])
            return {
                "supported": True,
                "format": "pytorch_state_dict",
                "artifact_size_bytes": ckpt.stat().st_size,
                "max_reload_diff": float(np.max(np.abs(preds_before - preds_after))),
                "consistent": bool(np.allclose(preds_before, preds_after, atol=1e-5)),
            }

    def _build_model(self) -> Any:
        raise NotImplementedError

    def _make_tensor(self, torch: Any, arr_x: np.ndarray) -> Any:
        return torch.from_numpy(arr_x)


class DL01PyTorchMLPAdapter(_PyTorchBaseAdapter):
    def __init__(self, random_state: int = 42, n_threads: int = 16, epochs: int = 5, batch_size: int = 64) -> None:
        super().__init__("DL01", ".venv-deep", "torch.nn", "Sequential_MLP", "2d", random_state, n_threads, "cuda:0")
        self.epochs = epochs
        self.batch_size = batch_size

    def build_config(self) -> Dict[str, Any]:
        return {"hidden_dims": [128, 64], "epochs": self.epochs, "batch_size": self.batch_size, "lr": 1e-3}

    def _build_model(self) -> Any:
        import torch.nn as nn
        return nn.Sequential(
            nn.Linear(EXPECTED_FEATURES, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )

    def create_estimator(self) -> Any:
        self._setup_torch()
        self.estimator = self._build_model().to(self.device_used)
        self.param_count = sum(p.numel() for p in self.estimator.parameters())
        return self.estimator

    def fit(self, X: np.ndarray, y: np.ndarray) -> "DL01PyTorchMLPAdapter":
        torch = self._setup_torch()
        arr_x, arr_y = validate_tabular_inputs(X, y)
        if self.estimator is None:
            self.estimator = self._build_model()
        t0 = time.perf_counter()
        self._train_torch_loop(torch, self.estimator, torch.from_numpy(arr_x), torch.from_numpy(arr_y), self.epochs, self.batch_size, 1e-3)
        self._record_cuda_mem(torch)
        self.fit_time_sec = round(time.perf_counter() - t0, 4)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        import torch
        arr_x, _ = validate_tabular_inputs(X)
        t0 = time.perf_counter()
        raw = self._predict_torch(torch, self.estimator, torch.from_numpy(arr_x), self.batch_size)
        self._record_cuda_mem(torch)
        self.predict_time_sec = round(time.perf_counter() - t0, 4)
        return validate_predictions(raw, arr_x.shape[0])


class DL02FTTransformerAdapter(_PyTorchBaseAdapter):
    def __init__(self, random_state: int = 42, n_threads: int = 16, epochs: int = 3, batch_size: int = 32) -> None:
        super().__init__("DL02", ".venv-deep", "rtdl_revisiting_models", "FTTransformer", "2d", random_state, n_threads, "cuda:0")
        self.epochs = epochs
        self.batch_size = batch_size

    def build_config(self) -> Dict[str, Any]:
        return {
            "n_cont_features": EXPECTED_FEATURES,
            "cat_cardinalities": [],
            "d_out": 1,
            "n_blocks": 2,
            "d_block": 64,
            "attention_n_heads": 4,
            "ffn_d_hidden_multiplier": 1.333,
            "attention_dropout": 0.1,
            "ffn_dropout": 0.1,
            "residual_dropout": 0.0,
            "epochs": self.epochs,
            "batch_size": self.batch_size,
            "token_count": EXPECTED_FEATURES + 1,
            "attention_backend": "torch.nn.functional.scaled_dot_product_attention (Turing math/mem_efficient)",
        }

    def _build_model(self) -> Any:
        from rtdl_revisiting_models import FTTransformer
        return FTTransformer(
            n_cont_features=EXPECTED_FEATURES,
            cat_cardinalities=[],
            d_out=1,
            n_blocks=2,
            d_block=64,
            attention_n_heads=4,
            ffn_d_hidden_multiplier=4 / 3,
            attention_dropout=0.1,
            ffn_dropout=0.1,
            residual_dropout=0.0,
        )

    def _forward_for_loss(self, model: Any, xb: Any) -> Any:
        return model(xb, None).squeeze(-1)

    def create_estimator(self) -> Any:
        self._setup_torch()
        self.estimator = self._build_model().to(self.device_used)
        self.param_count = sum(p.numel() for p in self.estimator.parameters())
        self.extra_metadata["token_count"] = EXPECTED_FEATURES + 1
        return self.estimator

    def fit(self, X: np.ndarray, y: np.ndarray) -> "DL02FTTransformerAdapter":
        torch = self._setup_torch()
        arr_x, arr_y = validate_tabular_inputs(X, y)
        if self.estimator is None:
            self.estimator = self._build_model()
        t0 = time.perf_counter()
        self._train_torch_loop(torch, self.estimator, torch.from_numpy(arr_x), torch.from_numpy(arr_y), self.epochs, self.batch_size, 1e-3)
        self._record_cuda_mem(torch)
        self.fit_time_sec = round(time.perf_counter() - t0, 4)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        import torch
        arr_x, _ = validate_tabular_inputs(X)
        t0 = time.perf_counter()
        raw = self._predict_torch(torch, self.estimator, torch.from_numpy(arr_x), self.batch_size)
        self._record_cuda_mem(torch)
        self.predict_time_sec = round(time.perf_counter() - t0, 4)
        return validate_predictions(raw, arr_x.shape[0])


class DL03RealMLPAdapter(BaseM02BAdapter):
    def __init__(self, random_state: int = 42, n_threads: int = 16, n_epochs: int = 5, batch_size: int = 64) -> None:
        super().__init__("DL03", ".venv-deep", "pytabkit", "RealMLP_TD_Regressor", "2d", random_state, n_threads, "cuda:0")
        self.n_epochs = n_epochs
        self.batch_size = batch_size

    def build_config(self) -> Dict[str, Any]:
        return {"n_epochs": self.n_epochs, "batch_size": self.batch_size, "device": "cuda:0", "random_state": self.random_state}

    def create_estimator(self) -> Any:
        import torch
        from pytabkit import RealMLP_TD_Regressor
        self.device_used = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.estimator = RealMLP_TD_Regressor(
            n_epochs=self.n_epochs,
            batch_size=self.batch_size,
            device=self.device_used,
            random_state=self.random_state,
            n_threads=self.n_threads,
            verbosity=0,
        )
        return self.estimator

    def fit(self, X: np.ndarray, y: np.ndarray) -> "DL03RealMLPAdapter":
        import torch
        arr_x, arr_y = validate_tabular_inputs(X, y)
        if self.estimator is None:
            self.create_estimator()
        if self.device_used.startswith("cuda"):
            torch.cuda.init()
            torch.cuda.reset_peak_memory_stats(0)
        t0 = time.perf_counter()
        self.estimator.fit(arr_x, arr_y)
        if self.device_used.startswith("cuda"):
            torch.cuda.synchronize()
            self.peak_cuda_allocated_mb = round(torch.cuda.max_memory_allocated(0) / (1024 ** 2), 3)
            self.peak_cuda_reserved_mb = round(torch.cuda.max_memory_reserved(0) / (1024 ** 2), 3)
        self.fit_time_sec = round(time.perf_counter() - t0, 4)
        self.last_loss_finite = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        arr_x, _ = validate_tabular_inputs(X)
        t0 = time.perf_counter()
        raw = self.estimator.predict(arr_x)
        self.predict_time_sec = round(time.perf_counter() - t0, 4)
        return validate_predictions(raw, arr_x.shape[0])

    def save_and_reload_predict(self, X: np.ndarray) -> Dict[str, Any]:
        arr_x, _ = validate_tabular_inputs(X)
        before = self.predict(arr_x)
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "DL03.joblib"
            joblib.dump(self.estimator, p)
            loaded = joblib.load(p)
            after = validate_predictions(loaded.predict(arr_x), arr_x.shape[0])
            return {
                "supported": True,
                "format": "joblib",
                "artifact_size_bytes": p.stat().st_size,
                "max_reload_diff": float(np.max(np.abs(before - after))),
                "consistent": bool(np.allclose(before, after, atol=1e-5)),
            }


class DL05TabMAdapter(_PyTorchBaseAdapter):
    def __init__(self, random_state: int = 42, n_threads: int = 16, epochs: int = 5, batch_size: int = 64, k: int = 8) -> None:
        super().__init__("DL05", ".venv-deep", "tabm", "TabM", "2d", random_state, n_threads, "cuda:0")
        self.epochs = epochs
        self.batch_size = batch_size
        self.k = k

    def build_config(self) -> Dict[str, Any]:
        return {
            "n_num_features": EXPECTED_FEATURES,
            "k_ensemble_size": self.k,
            "aggregation": "mean_over_k_ensemble_predictions",
            "d_out": 1,
            "epochs": self.epochs,
            "batch_size": self.batch_size,
        }

    def _build_model(self) -> Any:
        import tabm
        return tabm.TabM.make(
            n_num_features=EXPECTED_FEATURES,
            k=self.k,
            d_out=1,
            n_blocks=2,
            d_block=128,
        )

    def _forward_for_loss(self, model: Any, xb: Any) -> Any:
        # TabM outputs (batch, k, d_out); aggregate via mean across ensemble k
        out = model(xb, None)
        return out.mean(dim=1).squeeze(-1)

    def create_estimator(self) -> Any:
        self._setup_torch()
        self.estimator = self._build_model().to(self.device_used)
        self.param_count = sum(p.numel() for p in self.estimator.parameters())
        self.extra_metadata["ensemble_size_k"] = self.k
        return self.estimator

    def fit(self, X: np.ndarray, y: np.ndarray) -> "DL05TabMAdapter":
        torch = self._setup_torch()
        arr_x, arr_y = validate_tabular_inputs(X, y)
        if self.estimator is None:
            self.estimator = self._build_model()
        t0 = time.perf_counter()
        self._train_torch_loop(torch, self.estimator, torch.from_numpy(arr_x), torch.from_numpy(arr_y), self.epochs, self.batch_size, 1e-3)
        self._record_cuda_mem(torch)
        self.fit_time_sec = round(time.perf_counter() - t0, 4)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        import torch
        arr_x, _ = validate_tabular_inputs(X)
        t0 = time.perf_counter()
        raw = self._predict_torch(torch, self.estimator, torch.from_numpy(arr_x), self.batch_size)
        self._record_cuda_mem(torch)
        self.predict_time_sec = round(time.perf_counter() - t0, 4)
        return validate_predictions(raw, arr_x.shape[0])


class SG01Vanilla1DCNNAdapter(_PyTorchBaseAdapter):
    def __init__(self, random_state: int = 42, n_threads: int = 16, epochs: int = 5, batch_size: int = 64) -> None:
        super().__init__("SG01", ".venv-deep", "torch.nn", "VanillaConv1DRegressor", "3d_signal", random_state, n_threads, "cuda:0")
        self.epochs = epochs
        self.batch_size = batch_size

    def build_config(self) -> Dict[str, Any]:
        return {"channels": [32, 64], "kernel_sizes": [5, 5], "epochs": self.epochs, "batch_size": self.batch_size}

    def _build_model(self) -> Any:
        import torch.nn as nn
        return nn.Sequential(
            nn.Conv1d(1, 32, kernel_size=5, padding=2),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(32, 64, kernel_size=5, padding=2),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1),
            nn.Flatten(),
            nn.Linear(64, 1),
        )

    def _make_tensor(self, torch: Any, arr_x: np.ndarray) -> Any:
        return torch.from_numpy(adapt_2d_to_3d_signal(arr_x))

    def create_estimator(self) -> Any:
        self._setup_torch()
        self.estimator = self._build_model().to(self.device_used)
        self.param_count = sum(p.numel() for p in self.estimator.parameters())
        return self.estimator

    def fit(self, X: np.ndarray, y: np.ndarray) -> "SG01Vanilla1DCNNAdapter":
        torch = self._setup_torch()
        arr_x, arr_y = validate_tabular_inputs(X, y)
        if self.estimator is None:
            self.estimator = self._build_model()
        t0 = time.perf_counter()
        self._train_torch_loop(torch, self.estimator, self._make_tensor(torch, arr_x), torch.from_numpy(arr_y), self.epochs, self.batch_size, 1e-3)
        self._record_cuda_mem(torch)
        self.fit_time_sec = round(time.perf_counter() - t0, 4)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        import torch
        arr_x, _ = validate_tabular_inputs(X)
        t0 = time.perf_counter()
        raw = self._predict_torch(torch, self.estimator, self._make_tensor(torch, arr_x), self.batch_size)
        self._record_cuda_mem(torch)
        self.predict_time_sec = round(time.perf_counter() - t0, 4)
        return validate_predictions(raw, arr_x.shape[0])


class RF05DLMRetrainedAdapter(_PyTorchBaseAdapter):
    """
    Architecture-based PyTorch reproduction of the 15-layer 1D-CNN from
    Jakubowski & Tomczak (2024) Table 3 (for synthetic testing only; distinct from RF04 krknet.mat).
    """

    PI2MI = (1000.0 * 25.4) / 6400.0  # 3.96875 um/px

    def __init__(self, random_state: int = 42, n_threads: int = 16, epochs: int = 5, batch_size: int = 128) -> None:
        super().__init__("RF05", ".venv-deep", "torch.nn", "DLM15LayerCNN_Table3", "3d_signal", random_state, n_threads, "cuda:0")
        self.epochs = epochs
        self.batch_size = batch_size

    def build_config(self) -> Dict[str, Any]:
        return {
            "table3_layers": 15,
            "conv_filters": [64, 32, 32],
            "conv_kernels": [4, 16, 32],
            "optimizer": "SGD(momentum=0.9)",
            "lr": 1e-3,
            "epochs": self.epochs,
            "batch_size": self.batch_size,
            "output_scale_pi2mi": self.PI2MI,
        }

    def _build_model(self) -> Any:
        import torch.nn as nn
        # Conv1d with padding='same' requires odd kernel or PyTorch >=1.10 padding='same'
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

    def _make_tensor(self, torch: Any, arr_x: np.ndarray) -> Any:
        return torch.from_numpy(adapt_2d_to_3d_signal(arr_x))

    def create_estimator(self) -> Any:
        import torch
        self._setup_torch()
        self.estimator = self._build_model().to(self.device_used)
        # Initialize LazyLinear with dummy forward pass so param_count is known
        with torch.no_grad():
            dummy = torch.zeros((2, 1, EXPECTED_FEATURES), device=self.device_used)
            _ = self.estimator(dummy)
        self.param_count = sum(p.numel() for p in self.estimator.parameters())
        return self.estimator

    def fit(self, X: np.ndarray, y: np.ndarray) -> "RF05DLMRetrainedAdapter":
        torch = self._setup_torch()
        arr_x, arr_y = validate_tabular_inputs(X, y)
        if self.estimator is None:
            self.create_estimator()
        t0 = time.perf_counter()
        self._train_torch_loop(
            torch,
            self.estimator,
            self._make_tensor(torch, arr_x),
            torch.from_numpy(arr_y),
            self.epochs,
            self.batch_size,
            1e-3,
            optimizer_name="sgd_momentum",
        )
        self._record_cuda_mem(torch)
        self.fit_time_sec = round(time.perf_counter() - t0, 4)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        import torch
        arr_x, _ = validate_tabular_inputs(X)
        t0 = time.perf_counter()
        raw = self._predict_torch(torch, self.estimator, self._make_tensor(torch, arr_x), self.batch_size)
        self._record_cuda_mem(torch)
        self.predict_time_sec = round(time.perf_counter() - t0, 4)
        return validate_predictions(raw, arr_x.shape[0])

    def save_and_reload_predict(self, X: np.ndarray) -> Dict[str, Any]:
        import torch
        arr_x, _ = validate_tabular_inputs(X)
        preds_before = self.predict(arr_x)
        with tempfile.TemporaryDirectory() as tmpdir:
            ckpt = Path(tmpdir) / "RF05.pt"
            torch.save(self.estimator.state_dict(), ckpt)
            reloaded = self._build_model().to(self.device_used)
            with torch.no_grad():
                _ = reloaded(torch.zeros((2, 1, EXPECTED_FEATURES), device=self.device_used))
            reloaded.load_state_dict(torch.load(ckpt, map_location=self.device_used, weights_only=True))
            preds_after = validate_predictions(self._predict_torch(torch, reloaded, self._make_tensor(torch, arr_x), self.batch_size), arr_x.shape[0])
            return {
                "supported": True,
                "format": "pytorch_state_dict",
                "artifact_size_bytes": ckpt.stat().st_size,
                "max_reload_diff": float(np.max(np.abs(preds_before - preds_after))),
                "consistent": bool(np.allclose(preds_before, preds_after, atol=1e-5)),
            }


# ---------------------------------------------------------------------------
# aeon TensorFlow/Keras Adapters (.venv-signal-tf) & MultiRocketHydra (.venv-signal-hydra)
# ---------------------------------------------------------------------------

class _AeonTFAdapter(BaseM02BAdapter):
    def __init__(self, model_id: str, expected_class: str, n_epochs: int = 2, batch_size: int = 32, random_state: int = 42, n_threads: int = 16) -> None:
        super().__init__(model_id, ".venv-signal-tf", "aeon.regression.deep_learning", expected_class, "3d_signal", random_state, n_threads, "cpu")
        self.n_epochs = n_epochs
        self.batch_size = batch_size

    def create_estimator(self) -> Any:
        import tensorflow as tf
        tf.config.threading.set_intra_op_parallelism_threads(self.n_threads)
        tf.config.threading.set_inter_op_parallelism_threads(max(1, self.n_threads // 4))
        mod = importlib.import_module(self.expected_module)
        cls = getattr(mod, self.expected_class)
        self.device_used = "CPU_ONLY (native Windows TF >2.10)"
        self.estimator = cls(**self.build_config())
        return self.estimator

    def fit(self, X: np.ndarray, y: np.ndarray) -> "_AeonTFAdapter":
        arr_x, arr_y = validate_tabular_inputs(X, y)
        if self.estimator is None:
            self.create_estimator()
        x_3d = adapt_2d_to_3d_signal(arr_x)
        t0 = time.perf_counter()
        self.estimator.fit(x_3d, arr_y)
        self.fit_time_sec = round(time.perf_counter() - t0, 4)
        self.last_loss_finite = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        arr_x, _ = validate_tabular_inputs(X)
        x_3d = adapt_2d_to_3d_signal(arr_x)
        t0 = time.perf_counter()
        raw = self.estimator.predict(x_3d)
        self.predict_time_sec = round(time.perf_counter() - t0, 4)
        return validate_predictions(raw, arr_x.shape[0])

    def save_and_reload_predict(self, X: np.ndarray) -> Dict[str, Any]:
        # Keras/aeon estimators may not support naive joblib; test cleanly and report limitation if unsupported
        arr_x, _ = validate_tabular_inputs(X)
        before = self.predict(arr_x)
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                p = Path(tmpdir) / f"{self.model_id}.joblib"
                joblib.dump(self.estimator, p)
                loaded = joblib.load(p)
                after = validate_predictions(loaded.predict(adapt_2d_to_3d_signal(arr_x)), arr_x.shape[0])
                return {
                    "supported": True,
                    "format": "joblib",
                    "artifact_size_bytes": p.stat().st_size,
                    "max_reload_diff": float(np.max(np.abs(before - after))),
                    "consistent": bool(np.allclose(before, after, atol=1e-5)),
                }
        except Exception as exc:
            return {"supported": False, "error": f"{type(exc).__name__}: {exc}"}


class SG02ResNet1DAdapter(_AeonTFAdapter):
    def __init__(self, random_state: int = 42, n_threads: int = 16, n_epochs: int = 2, batch_size: int = 32) -> None:
        super().__init__("SG02", "ResNetRegressor", n_epochs, batch_size, random_state, n_threads)

    def build_config(self) -> Dict[str, Any]:
        return {"n_epochs": self.n_epochs, "batch_size": self.batch_size, "random_state": self.random_state, "verbose": False}


class SG03InceptionTimeAdapter(_AeonTFAdapter):
    def __init__(self, random_state: int = 42, n_threads: int = 16, n_epochs: int = 2, batch_size: int = 32) -> None:
        super().__init__("SG03", "InceptionTimeRegressor", n_epochs, batch_size, random_state, n_threads)

    def build_config(self) -> Dict[str, Any]:
        return {"n_regressors": 1, "n_epochs": self.n_epochs, "batch_size": self.batch_size, "random_state": self.random_state, "verbose": False}


class SG04LITETimeAdapter(_AeonTFAdapter):
    def __init__(self, random_state: int = 42, n_threads: int = 16, n_epochs: int = 2, batch_size: int = 32) -> None:
        super().__init__("SG04", "LITETimeRegressor", n_epochs, batch_size, random_state, n_threads)

    def build_config(self) -> Dict[str, Any]:
        return {"n_regressors": 1, "n_epochs": self.n_epochs, "batch_size": self.batch_size, "random_state": self.random_state, "verbose": False}


class SG06MultiRocketHydraAdapter(BaseM02BAdapter):
    def __init__(self, random_state: int = 42, n_threads: int = 16, n_kernels: int = 8, n_groups: int = 64) -> None:
        super().__init__(
            "SG06",
            ".venv-signal-hydra",
            "aeon.regression.convolution_based",
            "MultiRocketHydraRegressor",
            "3d_signal",
            random_state,
            n_threads,
            "cpu",
        )
        self.n_kernels = n_kernels
        self.n_groups = n_groups

    def build_config(self) -> Dict[str, Any]:
        return {"n_kernels": self.n_kernels, "n_groups": self.n_groups, "n_jobs": self.n_threads, "random_state": self.random_state}

    def create_estimator(self) -> Any:
        from aeon.regression.convolution_based import MultiRocketHydraRegressor
        self.device_used = "CPU (aeon MultiRocketHydraRegressor runs on CPU even with torch installed)"
        self.estimator = MultiRocketHydraRegressor(**self.build_config())
        return self.estimator

    def fit(self, X: np.ndarray, y: np.ndarray) -> "SG06MultiRocketHydraAdapter":
        arr_x, arr_y = validate_tabular_inputs(X, y)
        if self.estimator is None:
            self.create_estimator()
        x_3d = adapt_2d_to_3d_signal(arr_x)
        t0 = time.perf_counter()
        self.estimator.fit(x_3d, arr_y)
        self.fit_time_sec = round(time.perf_counter() - t0, 4)
        self.last_loss_finite = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        arr_x, _ = validate_tabular_inputs(X)
        x_3d = adapt_2d_to_3d_signal(arr_x)
        t0 = time.perf_counter()
        raw = self.estimator.predict(x_3d)
        self.predict_time_sec = round(time.perf_counter() - t0, 4)
        return validate_predictions(raw, arr_x.shape[0])

    def save_and_reload_predict(self, X: np.ndarray) -> Dict[str, Any]:
        arr_x, _ = validate_tabular_inputs(X)
        before = self.predict(arr_x)
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "SG06.joblib"
            joblib.dump(self.estimator, p)
            loaded = joblib.load(p)
            after = validate_predictions(loaded.predict(adapt_2d_to_3d_signal(arr_x)), arr_x.shape[0])
            return {
                "supported": True,
                "format": "joblib",
                "artifact_size_bytes": p.stat().st_size,
                "max_reload_diff": float(np.max(np.abs(before - after))),
                "consistent": bool(np.allclose(before, after, atol=1e-5)),
            }


ADAPTER_REGISTRY_M02B = {
    "DL01": DL01PyTorchMLPAdapter,
    "DL02": DL02FTTransformerAdapter,
    "DL03": DL03RealMLPAdapter,
    "DL05": DL05TabMAdapter,
    "SG01": SG01Vanilla1DCNNAdapter,
    "SG02": SG02ResNet1DAdapter,
    "SG03": SG03InceptionTimeAdapter,
    "SG04": SG04LITETimeAdapter,
    "SG06": SG06MultiRocketHydraAdapter,
    "RF05": RF05DLMRetrainedAdapter,
}


def get_m02b_adapter(model_id: str, **kwargs: Any) -> BaseM02BAdapter:
    if model_id not in ADAPTER_REGISTRY_M02B:
        raise KeyError(f"Unknown M02B model_id {model_id!r}. Allowed: {sorted(ADAPTER_REGISTRY_M02B)}")
    return ADAPTER_REGISTRY_M02B[model_id](**kwargs)
