"""
src/features/perturbations.py

Deterministic brightness-profile perturbation library for Idea 2 robustness protocol (M03 Section 9).
All outputs preserve shape (n_samples, 501) and clip intensities to [0.0, 255.0].
"""

from __future__ import annotations

from typing import Dict
import numpy as np
from scipy.ndimage import gaussian_filter1d


def _validate_profiles(X: np.ndarray) -> np.ndarray:
    arr = np.asarray(X, dtype=np.float32)
    if arr.ndim != 2 or arr.shape[1] != 501:
        raise ValueError(f"Expected shape (n_samples, 501), got {arr.shape}")
    return arr


def _clip255(arr: np.ndarray) -> np.ndarray:
    return np.clip(arr, 0.0, 255.0).astype(np.float32)


def apply_brightness_shift(X: np.ndarray, delta: float) -> np.ndarray:
    return _clip255(_validate_profiles(X) + float(delta))


def apply_contrast_scale(X: np.ndarray, scale: float) -> np.ndarray:
    arr = _validate_profiles(X)
    row_mean = np.mean(arr, axis=1, keepdims=True)
    return _clip255(row_mean + float(scale) * (arr - row_mean))


def apply_gaussian_noise(X: np.ndarray, sigma: float, seed: int = 42) -> np.ndarray:
    arr = _validate_profiles(X)
    rng = np.random.default_rng(seed)
    noise = rng.normal(0.0, float(sigma), size=arr.shape).astype(np.float32)
    return _clip255(arr + noise)


def apply_gaussian_smoothing(X: np.ndarray, sigma: float) -> np.ndarray:
    arr = _validate_profiles(X)
    return _clip255(gaussian_filter1d(arr, sigma=float(sigma), axis=1, mode="nearest"))


def apply_gamma(X: np.ndarray, gamma: float) -> np.ndarray:
    arr = _validate_profiles(X) / 255.0
    return _clip255(255.0 * np.power(np.clip(arr, 0.0, 1.0), float(gamma)))


def apply_illumination_gradient(X: np.ndarray, amplitude: float) -> np.ndarray:
    arr = _validate_profiles(X)
    grad = np.linspace(-float(amplitude), float(amplitude), arr.shape[1], dtype=np.float32)[None, :]
    return _clip255(arr + grad)


def apply_impulse_noise(X: np.ndarray, prob: float, seed: int = 42) -> np.ndarray:
    arr = _validate_profiles(X).copy()
    rng = np.random.default_rng(seed)
    mask = rng.random(arr.shape) < float(prob)
    salt = rng.random(arr.shape) < 0.5
    arr[mask & salt] = 255.0
    arr[mask & (~salt)] = 0.0
    return _clip255(arr)


def apply_downsample_interp(X: np.ndarray, factor: int) -> np.ndarray:
    arr = _validate_profiles(X)
    f = max(2, int(factor))
    idx_full = np.arange(501, dtype=np.float32)
    idx_sub = np.arange(0, 501, f, dtype=np.float32)
    out = np.empty_like(arr)
    for i in range(arr.shape[0]):
        out[i] = np.interp(idx_full, idx_sub, arr[i, ::f])
    return _clip255(out)


def apply_combined_corruption(X: np.ndarray, shift: float = -15.0, scale: float = 0.85, sigma: float = 5.0, seed: int = 42) -> np.ndarray:
    x1 = apply_contrast_scale(X, scale)
    x2 = apply_brightness_shift(x1, shift)
    return apply_gaussian_noise(x2, sigma, seed=seed)


PERTURBATION_DISPATCH: Dict[str, object] = {
    "brightness_shift": apply_brightness_shift,
    "contrast_scale": apply_contrast_scale,
    "gaussian_noise": apply_gaussian_noise,
    "gaussian_smoothing": apply_gaussian_smoothing,
    "gamma": apply_gamma,
    "illumination_gradient": apply_illumination_gradient,
    "impulse_noise": apply_impulse_noise,
    "downsample_interp": apply_downsample_interp,
    "combined": apply_combined_corruption,
}
