"""
src/models/m02a_adapters.py

Lightweight, reusable compatibility adapters for the five M02A candidates:
  - ML04: xgboost.XGBRegressor
  - ML05: lightgbm.LGBMRegressor
  - ML06: catboost.CatBoostRegressor
  - SG05: aeon.regression.convolution_based.RocketRegressor
  - SG06: aeon.regression.convolution_based.MultiRocketHydraRegressor

All configurations are bounded compatibility-test settings, NOT research hyperparameters.
"""

from __future__ import annotations

import importlib
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import joblib
import numpy as np

EXPECTED_FEATURES = 501


def validate_tabular_inputs(X: np.ndarray, y: Optional[np.ndarray] = None) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """Validate canonical (n_samples, 501) input contract and optional 1D target."""
    arr_x = np.asarray(X, dtype=np.float32)
    if arr_x.ndim != 2:
        raise ValueError(f"Expected 2D input X of shape (n_samples, {EXPECTED_FEATURES}), got ndim={arr_x.ndim} shape={arr_x.shape}")
    if arr_x.shape[1] != EXPECTED_FEATURES:
        raise ValueError(f"Expected {EXPECTED_FEATURES} ordered features, got {arr_x.shape[1]}")
    if not np.isfinite(arr_x).all():
        raise ValueError("Input X contains NaN or Inf values.")

    arr_y: Optional[np.ndarray] = None
    if y is not None:
        arr_y = np.asarray(y, dtype=np.float32)
        if arr_y.ndim != 1 or arr_y.shape[0] != arr_x.shape[0]:
            raise ValueError(f"Expected 1D target y of shape ({arr_x.shape[0]},), got {arr_y.shape}")
        if not np.isfinite(arr_y).all():
            raise ValueError("Target y contains NaN or Inf values.")
    return arr_x, arr_y


def adapt_2d_to_3d_signal(X: np.ndarray) -> np.ndarray:
    """
    Adapt canonical (n_samples, 501) array to (n_samples, 1, 501) for aeon
    without reordering features or flattening sample identity.
    """
    arr_x, _ = validate_tabular_inputs(X)
    return np.ascontiguousarray(arr_x[:, np.newaxis, :], dtype=np.float32)


def validate_predictions(y_pred: np.ndarray, expected_n: int) -> np.ndarray:
    """Ensure predictions are 1D, exact length expected_n, and strictly finite."""
    arr = np.asarray(y_pred, dtype=np.float64)
    if arr.ndim != 1 or arr.shape != (expected_n,):
        raise ValueError(f"Invalid prediction shape {arr.shape}; expected ({expected_n},)")
    if not np.isfinite(arr).all():
        raise ValueError("Predictions contain NaN or Inf values.")
    return arr


@dataclass
class BaseM02AAdapter:
    model_id: str
    expected_module: str
    expected_class: str
    input_mode: str  # "2d" or "3d_signal"
    random_state: int = 42
    n_threads: int = 16
    config_label: str = "compatibility_bounded"
    estimator: Any = field(default=None, init=False)
    fit_time_sec: Optional[float] = field(default=None, init=False)
    predict_time_sec: Optional[float] = field(default=None, init=False)

    def _import_class(self) -> Any:
        mod = importlib.import_module(self.expected_module)
        cls = getattr(mod, self.expected_class)
        actual_fqn = f"{cls.__module__}.{cls.__name__}"
        if not actual_fqn.startswith(self.expected_module.split(".")[0]) or cls.__name__ != self.expected_class:
            raise ImportError(f"Estimator identity mismatch: got {actual_fqn}, expected {self.expected_module}.{self.expected_class}")
        return cls

    def build_config(self) -> Dict[str, Any]:
        raise NotImplementedError

    def create_estimator(self) -> Any:
        cls = self._import_class()
        self.estimator = cls(**self.build_config())
        return self.estimator

    def prepare_X(self, X: np.ndarray) -> np.ndarray:
        if self.input_mode == "3d_signal":
            return adapt_2d_to_3d_signal(X)
        arr_x, _ = validate_tabular_inputs(X)
        return arr_x

    def fit(self, X: np.ndarray, y: np.ndarray) -> "BaseM02AAdapter":
        if self.estimator is None:
            self.create_estimator()
        x_in = self.prepare_X(X)
        _, y_in = validate_tabular_inputs(X, y)
        t0 = time.perf_counter()
        self.estimator.fit(x_in, y_in)
        self.fit_time_sec = round(time.perf_counter() - t0, 4)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.estimator is None:
            raise RuntimeError("Estimator has not been created/fitted.")
        x_in = self.prepare_X(X)
        t0 = time.perf_counter()
        raw_pred = self.estimator.predict(x_in)
        self.predict_time_sec = round(time.perf_counter() - t0, 4)
        return validate_predictions(raw_pred, expected_n=X.shape[0])

    def transformed_dimensionality(self) -> Optional[int]:
        return None

    def get_runtime_metadata(self) -> Dict[str, Any]:
        cls = self.estimator.__class__ if self.estimator is not None else None
        mod = importlib.import_module(self.expected_module.split(".")[0])
        return {
            "model_id": self.model_id,
            "python_executable": sys.executable,
            "package": self.expected_module.split(".")[0],
            "package_version": getattr(mod, "__version__", "unknown"),
            "estimator_class": f"{cls.__module__}.{cls.__name__}" if cls else f"{self.expected_module}.{self.expected_class}",
            "input_mode": self.input_mode,
            "config_label": self.config_label,
            "config": self.build_config(),
            "random_state": self.random_state,
            "n_threads": self.n_threads,
            "fit_time_sec": self.fit_time_sec,
            "predict_time_sec": self.predict_time_sec,
            "transformed_dimensionality": self.transformed_dimensionality(),
        }

    def save(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.estimator, path)
        return path

    def load_and_predict(self, path: Path, X: np.ndarray) -> np.ndarray:
        loaded = joblib.load(path)
        x_in = self.prepare_X(X)
        return validate_predictions(loaded.predict(x_in), expected_n=X.shape[0])


class ML04XGBoostAdapter(BaseM02AAdapter):
    def __init__(self, random_state: int = 42, n_threads: int = 16, n_estimators: int = 20) -> None:
        super().__init__("ML04", "xgboost", "XGBRegressor", "2d", random_state, n_threads)
        self.n_estimators = n_estimators

    def build_config(self) -> Dict[str, Any]:
        return {
            "n_estimators": self.n_estimators,
            "max_depth": 4,
            "learning_rate": 0.1,
            "tree_method": "hist",
            "device": "cpu",
            "n_jobs": self.n_threads,
            "random_state": self.random_state,
        }


class ML05LightGBMAdapter(BaseM02AAdapter):
    def __init__(self, random_state: int = 42, n_threads: int = 16, n_estimators: int = 20) -> None:
        super().__init__("ML05", "lightgbm", "LGBMRegressor", "2d", random_state, n_threads)
        self.n_estimators = n_estimators

    def build_config(self) -> Dict[str, Any]:
        return {
            "n_estimators": self.n_estimators,
            "max_depth": 6,
            "learning_rate": 0.1,
            "device": "cpu",
            "n_jobs": self.n_threads,
            "random_state": self.random_state,
            "verbose": -1,
        }


class ML06CatBoostAdapter(BaseM02AAdapter):
    def __init__(self, random_state: int = 42, n_threads: int = 16, iterations: int = 20) -> None:
        super().__init__("ML06", "catboost", "CatBoostRegressor", "2d", random_state, n_threads)
        self.iterations = iterations

    def build_config(self) -> Dict[str, Any]:
        return {
            "iterations": self.iterations,
            "depth": 6,
            "learning_rate": 0.1,
            "task_type": "CPU",
            "thread_count": self.n_threads,
            "random_seed": self.random_state,
            "verbose": 0,
            "allow_writing_files": False,
        }


class SG05RocketAdapter(BaseM02AAdapter):
    def __init__(self, random_state: int = 42, n_threads: int = 16, n_kernels: int = 2000) -> None:
        super().__init__("SG05", "aeon.regression.convolution_based", "RocketRegressor", "3d_signal", random_state, n_threads)
        self.n_kernels = n_kernels

    def build_config(self) -> Dict[str, Any]:
        return {
            "n_kernels": self.n_kernels,
            "n_jobs": self.n_threads,
            "random_state": self.random_state,
        }

    def transformed_dimensionality(self) -> Optional[int]:
        if self.estimator is None:
            return None
        tr = getattr(self.estimator, "_transformer", None)
        if tr is not None and hasattr(tr, "n_kernels"):
            return int(tr.n_kernels) * 2
        est = getattr(self.estimator, "estimator_", None)
        if est is not None and hasattr(est, "n_features_in_"):
            return int(est.n_features_in_)
        return None


class SG06MultiRocketHydraAdapter(BaseM02AAdapter):
    def __init__(self, random_state: int = 42, n_threads: int = 16, n_kernels: int = 8) -> None:
        super().__init__(
            "SG06",
            "aeon.regression.convolution_based",
            "MultiRocketHydraRegressor",
            "3d_signal",
            random_state,
            n_threads,
        )
        self.n_kernels = n_kernels

    def build_config(self) -> Dict[str, Any]:
        return {
            "n_kernels": self.n_kernels,
            "n_jobs": self.n_threads,
            "random_state": self.random_state,
        }

    def transformed_dimensionality(self) -> Optional[int]:
        if self.estimator is None:
            return None
        reg = getattr(self.estimator, "_regressor", None)
        if reg is not None and hasattr(reg, "n_features_in_"):
            return int(reg.n_features_in_)
        # Fallback: inspect pipeline steps if exposed
        pipe = getattr(self.estimator, "_pipeline", None)
        if pipe is not None and hasattr(pipe, "steps"):
            last = pipe.steps[-1][1]
            if hasattr(last, "n_features_in_"):
                return int(last.n_features_in_)
        return None


ADAPTER_REGISTRY = {
    "ML04": ML04XGBoostAdapter,
    "ML05": ML05LightGBMAdapter,
    "ML06": ML06CatBoostAdapter,
    "SG05": SG05RocketAdapter,
    "SG06": SG06MultiRocketHydraAdapter,
}


def get_adapter(model_id: str, **kwargs: Any) -> BaseM02AAdapter:
    if model_id not in ADAPTER_REGISTRY:
        raise KeyError(f"Unknown M02A model_id {model_id!r}. Allowed: {sorted(ADAPTER_REGISTRY)}")
    return ADAPTER_REGISTRY[model_id](**kwargs)
