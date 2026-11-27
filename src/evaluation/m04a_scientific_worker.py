"""
src/evaluation/m04a_scientific_worker.py

Isolated scientific training & validation worker for M04A (Protocol A train + validation only).
Must be invoked inside the target model's validated .venv* environment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pickle
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from evaluation.m04a_data import EXPECTED_VAL_ROWS, load_protocol_a_train_val  # noqa: E402


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def _atomic_write_json(path: Path, payload: Dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def _gpu_sync_and_stats() -> Tuple[Optional[float], Optional[float]]:
    try:
        import torch

        if torch.cuda.is_available():
            torch.cuda.synchronize()
            alloc = round(torch.cuda.max_memory_allocated(0) / (1024 ** 2), 3)
            res = round(torch.cuda.max_memory_reserved(0) / (1024 ** 2), 3)
            return alloc, res
    except Exception:
        pass
    return None, None


def _run_pytorch_early_stop(
    model_builder,
    X_tr: np.ndarray,
    y_tr: np.ndarray,
    X_iv: np.ndarray,
    y_iv: np.ndarray,
    X_val: np.ndarray,
    *,
    is_3d: bool,
    zero_center_only: bool,
    pi2mi_scale: Optional[float],
    optimizer_name: str,
    lr: float,
    momentum: float,
    weight_decay: float,
    batch_size: int,
    max_epochs: int,
    patience: int,
    seed: int,
    forward_fn,
    artifact_path: Path,
) -> Dict[str, Any]:
    import copy
    import torch
    from torch.utils.data import DataLoader, TensorDataset

    torch.manual_seed(seed)
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    if device == "cuda:0":
        torch.cuda.init()
        torch.cuda.manual_seed_all(seed)
        torch.cuda.reset_peak_memory_stats(0)

    t_prep0 = time.perf_counter()
    if zero_center_only:
        x_mean = float(X_tr.mean())
        x_std = 1.0
        X_tr_n = (X_tr - x_mean).astype(np.float32)
        X_iv_n = (X_iv - x_mean).astype(np.float32)
        X_val_n = (X_val - x_mean).astype(np.float32)
    else:
        x_mean = X_tr.mean(axis=0, keepdims=True)
        x_std = X_tr.std(axis=0, keepdims=True) + 1e-6
        X_tr_n = ((X_tr - x_mean) / x_std).astype(np.float32)
        X_iv_n = ((X_iv - x_mean) / x_std).astype(np.float32)
        X_val_n = ((X_val - x_mean) / x_std).astype(np.float32)

    if is_3d:
        X_tr_n = X_tr_n[:, None, :]
        X_iv_n = X_iv_n[:, None, :]
        X_val_n = X_val_n[:, None, :]

    if pi2mi_scale is not None:
        y_mean = 0.0
        y_std = float(pi2mi_scale)
    else:
        y_mean = float(y_tr.mean())
        y_std = float(y_tr.std()) + 1e-6

    y_tr_n = ((y_tr - y_mean) / y_std).astype(np.float32)
    y_iv_n = ((y_iv - y_mean) / y_std).astype(np.float32)
    preprocess_fit_sec = time.perf_counter() - t_prep0

    t_init0 = time.perf_counter()
    model = model_builder().to(device)
    with torch.no_grad():
        sample = torch.from_numpy(X_tr_n[:2]).to(device)
        _ = forward_fn(model, sample)
    param_count = int(sum(p.numel() for p in model.parameters()))
    init_sec = time.perf_counter() - t_init0

    if optimizer_name == "SGD":
        opt = torch.optim.SGD(model.parameters(), lr=lr, momentum=momentum)
    else:
        opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    loss_fn = torch.nn.MSELoss()

    dl_tr = DataLoader(
        TensorDataset(torch.from_numpy(X_tr_n), torch.from_numpy(y_tr_n)),
        batch_size=batch_size,
        shuffle=True,
        generator=torch.Generator().manual_seed(seed),
    )
    dl_iv = DataLoader(
        TensorDataset(torch.from_numpy(X_iv_n), torch.from_numpy(y_iv_n)),
        batch_size=max(128, batch_size),
        shuffle=False,
    )

    history: List[Dict[str, float]] = []
    best_iv_loss = float("inf")
    best_epoch = 0
    best_state = None
    no_improve = 0

    t_train0 = time.perf_counter()
    for epoch in range(1, max_epochs + 1):
        model.train()
        tr_loss_sum = 0.0
        tr_n = 0
        for xb, yb in dl_tr:
            xb = xb.to(device)
            yb = yb.to(device)
            opt.zero_grad(set_to_none=True)
            pred = forward_fn(model, xb)
            loss = loss_fn(pred, yb)
            if not torch.isfinite(loss):
                raise FloatingPointError(f"Non-finite training loss at epoch {epoch}.")
            loss.backward()
            opt.step()
            tr_loss_sum += float(loss.item()) * xb.shape[0]
            tr_n += xb.shape[0]

        model.eval()
        iv_loss_sum = 0.0
        iv_n = 0
        with torch.no_grad():
            for xb, yb in dl_iv:
                xb = xb.to(device)
                yb = yb.to(device)
                pred = forward_fn(model, xb)
                loss = loss_fn(pred, yb)
                iv_loss_sum += float(loss.item()) * xb.shape[0]
                iv_n += xb.shape[0]

        tr_mse = tr_loss_sum / max(1, tr_n)
        iv_mse = iv_loss_sum / max(1, iv_n)
        history.append({"epoch": epoch, "inner_train_mse": tr_mse, "inner_val_mse": iv_mse})
        if iv_mse < best_iv_loss - 1e-6:
            best_iv_loss = iv_mse
            best_epoch = epoch
            best_state = copy.deepcopy(model.state_dict())
            no_improve = 0
        else:
            no_improve += 1
            if no_improve >= patience:
                break

    if device == "cuda:0":
        torch.cuda.synchronize()
    train_sec = time.perf_counter() - t_train0

    if best_state is not None:
        model.load_state_dict(best_state)

    t_pred0 = time.perf_counter()
    model.eval()
    preds = []
    with torch.no_grad():
        for i in range(0, X_val_n.shape[0], 256):
            xb = torch.from_numpy(X_val_n[i : i + 256]).to(device)
            out = forward_fn(model, xb).detach().cpu().numpy()
            preds.append(out)
    if device == "cuda:0":
        torch.cuda.synchronize()
    predict_sec = time.perf_counter() - t_pred0

    y_pred_raw = np.concatenate(preds, axis=0).astype(np.float64) * y_std + y_mean
    torch.save(
        {
            "state_dict": model.state_dict(),
            "x_mean": x_mean,
            "x_std": x_std,
            "y_mean": y_mean,
            "y_std": y_std,
            "best_epoch": best_epoch,
        },
        artifact_path,
    )
    peak_alloc, peak_res = _gpu_sync_and_stats()
    return {
        "y_pred_raw": y_pred_raw,
        "init_sec": init_sec,
        "preprocess_fit_sec": preprocess_fit_sec,
        "load_sec": 0.0,
        "train_or_context_sec": train_sec,
        "predict_sec": predict_sec,
        "param_count": param_count,
        "actual_epochs": len(history),
        "best_epoch": best_epoch,
        "history": history,
        "device": device,
        "peak_cuda_alloc_mb": peak_alloc,
        "peak_cuda_res_mb": peak_res,
    }


def run_model(
    model_id: str,
    cfg: Dict[str, Any],
    data,
    seed: int,
    artifact_dir: Path,
    attempt_id: str,
) -> Dict[str, Any]:
    X_tr_full = data.X_train
    y_tr_full = data.y_train
    X_val = data.X_val

    inner_mask = data.train_inner_mask
    X_tr_in = X_tr_full[inner_mask]
    y_tr_in = y_tr_full[inner_mask]
    X_iv_in = X_tr_full[~inner_mask]
    y_iv_in = y_tr_full[~inner_mask]

    # 1. Classical & Sklearn references
    if model_id in {"RF01", "RF02", "ML01", "ML02", "ML03", "ML07"}:
        from sklearn.dummy import DummyRegressor
        from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor, RandomForestRegressor
        from sklearn.linear_model import LinearRegression
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        from sklearn.svm import SVR

        t0 = time.perf_counter()
        if model_id == "RF01":
            est = DummyRegressor(**cfg)
        elif model_id == "RF02":
            est = make_pipeline(StandardScaler(), LinearRegression(**cfg))
        elif model_id == "ML01":
            est = ExtraTreesRegressor(**cfg)
        elif model_id == "ML02":
            est = RandomForestRegressor(**cfg)
        elif model_id == "ML03":
            est = HistGradientBoostingRegressor(**cfg)
        else:
            est = make_pipeline(StandardScaler(), SVR(**cfg))
        init_sec = time.perf_counter() - t0

        t1 = time.perf_counter()
        est.fit(X_tr_full, y_tr_full)
        train_sec = time.perf_counter() - t1

        t2 = time.perf_counter()
        y_pred_raw = est.predict(X_val).astype(np.float64)
        predict_sec = time.perf_counter() - t2

        art_path = artifact_dir / f"{model_id}_{attempt_id}.pkl"
        with art_path.open("wb") as f:
            pickle.dump(est, f)

        return {
            "y_pred_raw": y_pred_raw,
            "init_sec": init_sec,
            "preprocess_fit_sec": 0.0,
            "load_sec": 0.0,
            "train_or_context_sec": train_sec,
            "predict_sec": predict_sec,
            "param_count": None,
            "actual_epochs": None,
            "best_epoch": None,
            "history": None,
            "device": "cpu",
            "peak_cuda_alloc_mb": None,
            "peak_cuda_res_mb": None,
            "artifact_path": art_path,
        }

    # 2. Boosting (.venv-boost)
    if model_id in {"ML04", "ML05", "ML06"}:
        t0 = time.perf_counter()
        if model_id == "ML04":
            import xgboost as xgb
            est = xgb.XGBRegressor(**cfg)
        elif model_id == "ML05":
            import lightgbm as lgb
            est = lgb.LGBMRegressor(**cfg)
        else:
            from catboost import CatBoostRegressor
            est = CatBoostRegressor(**cfg)
        init_sec = time.perf_counter() - t0

        t1 = time.perf_counter()
        est.fit(X_tr_full, y_tr_full)
        train_sec = time.perf_counter() - t1

        t2 = time.perf_counter()
        y_pred_raw = est.predict(X_val).astype(np.float64)
        predict_sec = time.perf_counter() - t2

        art_path = artifact_dir / f"{model_id}_{attempt_id}.pkl"
        with art_path.open("wb") as f:
            pickle.dump(est, f)

        return {
            "y_pred_raw": y_pred_raw,
            "init_sec": init_sec,
            "preprocess_fit_sec": 0.0,
            "load_sec": 0.0,
            "train_or_context_sec": train_sec,
            "predict_sec": predict_sec,
            "param_count": None,
            "actual_epochs": None,
            "best_epoch": None,
            "history": None,
            "device": "cpu",
            "peak_cuda_alloc_mb": None,
            "peak_cuda_res_mb": None,
            "artifact_path": art_path,
        }

    # 3. PyTorch tabular & spatial (.venv-deep)
    if model_id == "DL01":
        import torch.nn as nn

        dims = cfg.get("hidden_dims", [256, 128, 64])
        drop = float(cfg.get("dropout", 0.1))

        def build_mlp():
            layers = []
            in_d = 501
            for h in dims:
                layers.extend([nn.Linear(in_d, h), nn.ReLU(), nn.Dropout(drop)])
                in_d = h
            layers.append(nn.Linear(in_d, 1))
            return nn.Sequential(*layers)

        art_path = artifact_dir / f"{model_id}_{attempt_id}.pt"
        res = _run_pytorch_early_stop(
            build_mlp, X_tr_in, y_tr_in, X_iv_in, y_iv_in, X_val,
            is_3d=False, zero_center_only=False, pi2mi_scale=None,
            optimizer_name="AdamW", lr=float(cfg.get("lr", 1e-3)), momentum=0.0, weight_decay=1e-4,
            batch_size=int(cfg.get("batch_size", 128)), max_epochs=int(cfg.get("max_epochs", 100)),
            patience=int(cfg.get("early_stopping_patience", 15)), seed=seed,
            forward_fn=lambda m, xb: m(xb).squeeze(-1), artifact_path=art_path,
        )
        res["artifact_path"] = art_path
        return res

    if model_id == "DL02":
        from rtdl_revisiting_models import FTTransformer

        def build_ftt():
            return FTTransformer(
                n_cont_features=int(cfg.get("n_cont_features", 501)),
                cat_cardinalities=[],
                d_out=int(cfg.get("d_out", 1)),
                n_blocks=int(cfg.get("n_blocks", 3)),
                d_block=int(cfg.get("d_block", 64)),
                attention_n_heads=int(cfg.get("attention_n_heads", 4)),
                ffn_d_hidden_multiplier=float(cfg.get("ffn_d_hidden_multiplier", 4 / 3)),
                attention_dropout=float(cfg.get("attention_dropout", 0.1)),
                ffn_dropout=float(cfg.get("ffn_dropout", 0.1)),
                residual_dropout=float(cfg.get("residual_dropout", 0.0)),
            )

        art_path = artifact_dir / f"{model_id}_{attempt_id}.pt"
        res = _run_pytorch_early_stop(
            build_ftt, X_tr_in, y_tr_in, X_iv_in, y_iv_in, X_val,
            is_3d=False, zero_center_only=False, pi2mi_scale=None,
            optimizer_name="AdamW", lr=float(cfg.get("lr", 5e-4)), momentum=0.0, weight_decay=1e-5,
            batch_size=int(cfg.get("batch_size", 64)), max_epochs=int(cfg.get("max_epochs", 80)),
            patience=int(cfg.get("early_stopping_patience", 12)), seed=seed,
            forward_fn=lambda m, xb: m(xb, None).squeeze(-1), artifact_path=art_path,
        )
        res["artifact_path"] = art_path
        return res

    if model_id == "DL03":
        import torch
        from pytabkit import RealMLP_TD_Regressor

        if torch.cuda.is_available():
            torch.cuda.init()
            torch.cuda.reset_peak_memory_stats(0)

        t0 = time.perf_counter()
        est = RealMLP_TD_Regressor(
            n_epochs=int(cfg.get("n_epochs", 100)),
            batch_size=int(cfg.get("batch_size", 128)),
            device=str(cfg.get("device", "cuda:0")),
            random_state=int(cfg.get("random_state", seed)),
            use_early_stopping=bool(cfg.get("use_early_stopping", False)),
            val_fraction=float(cfg.get("val_fraction", 0.0)),
        )
        init_sec = time.perf_counter() - t0

        t1 = time.perf_counter()
        est.fit(X_tr_full, y_tr_full)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        train_sec = time.perf_counter() - t1

        t2 = time.perf_counter()
        y_pred_raw = np.asarray(est.predict(X_val), dtype=np.float64).reshape(-1)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        predict_sec = time.perf_counter() - t2

        art_path = artifact_dir / f"{model_id}_{attempt_id}.pkl"
        with art_path.open("wb") as f:
            pickle.dump(est, f)
        peak_alloc, peak_res = _gpu_sync_and_stats()
        return {
            "y_pred_raw": y_pred_raw,
            "init_sec": init_sec,
            "preprocess_fit_sec": 0.0,
            "load_sec": 0.0,
            "train_or_context_sec": train_sec,
            "predict_sec": predict_sec,
            "param_count": None,
            "actual_epochs": int(cfg.get("n_epochs", 100)),
            "best_epoch": None,
            "history": None,
            "device": str(cfg.get("device", "cuda:0")),
            "peak_cuda_alloc_mb": peak_alloc,
            "peak_cuda_res_mb": peak_res,
            "artifact_path": art_path,
        }

    if model_id == "DL05":
        import tabm

        k_ens = int(cfg.get("k_ensemble_size", 8))

        def build_tabm():
            return tabm.TabM.make(
                n_num_features=int(cfg.get("n_num_features", 501)),
                k=k_ens,
                d_out=int(cfg.get("d_out", 1)),
                n_blocks=2,
                d_block=128,
            )

        art_path = artifact_dir / f"{model_id}_{attempt_id}.pt"
        res = _run_pytorch_early_stop(
            build_tabm, X_tr_in, y_tr_in, X_iv_in, y_iv_in, X_val,
            is_3d=False, zero_center_only=False, pi2mi_scale=None,
            optimizer_name="AdamW", lr=float(cfg.get("lr", 1e-3)), momentum=0.0, weight_decay=1e-4,
            batch_size=int(cfg.get("batch_size", 128)), max_epochs=int(cfg.get("max_epochs", 100)),
            patience=int(cfg.get("early_stopping_patience", 15)), seed=seed,
            forward_fn=lambda m, xb: m(xb, None).mean(dim=1).squeeze(-1), artifact_path=art_path,
        )
        res["artifact_path"] = art_path
        return res

    if model_id == "SG01":
        import torch.nn as nn

        ch = cfg.get("channels", [32, 64])
        ks = cfg.get("kernel_sizes", [5, 5])

        def build_cnn():
            return nn.Sequential(
                nn.Conv1d(1, ch[0], kernel_size=ks[0], padding=ks[0] // 2),
                nn.ReLU(),
                nn.MaxPool1d(2),
                nn.Conv1d(ch[0], ch[1], kernel_size=ks[1], padding=ks[1] // 2),
                nn.ReLU(),
                nn.AdaptiveAvgPool1d(1),
                nn.Flatten(),
                nn.Linear(ch[1], 1),
            )

        art_path = artifact_dir / f"{model_id}_{attempt_id}.pt"
        res = _run_pytorch_early_stop(
            build_cnn, X_tr_in, y_tr_in, X_iv_in, y_iv_in, X_val,
            is_3d=True, zero_center_only=False, pi2mi_scale=None,
            optimizer_name="AdamW", lr=float(cfg.get("lr", 1e-3)), momentum=0.0, weight_decay=1e-4,
            batch_size=int(cfg.get("batch_size", 128)), max_epochs=int(cfg.get("max_epochs", 100)),
            patience=int(cfg.get("early_stopping_patience", 15)), seed=seed,
            forward_fn=lambda m, xb: m(xb).squeeze(-1), artifact_path=art_path,
        )
        res["artifact_path"] = art_path
        return res

    if model_id == "RF05":
        import torch.nn as nn

        def build_dlm():
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

        art_path = artifact_dir / f"{model_id}_{attempt_id}.pt"
        res = _run_pytorch_early_stop(
            build_dlm, X_tr_in, y_tr_in, X_iv_in, y_iv_in, X_val,
            is_3d=True, zero_center_only=True,
            pi2mi_scale=float(cfg.get("target_scale_pi2mi", 3.96875)),
            optimizer_name="SGD", lr=float(cfg.get("lr", 1e-3)), momentum=float(cfg.get("momentum", 0.9)),
            weight_decay=0.0, batch_size=int(cfg.get("batch_size", 128)),
            max_epochs=int(cfg.get("max_epochs", 50)),
            patience=int(cfg.get("early_stopping_patience", 15)), seed=seed,
            forward_fn=lambda m, xb: m(xb).squeeze(-1), artifact_path=art_path,
        )
        res["artifact_path"] = art_path
        return res

    # 4. TabR (.venv-tabr)
    if model_id == "DL04":
        import copy
        import torch

        tabr_root = ROOT / "data" / "external" / "tabular-dl-tabr"
        os.environ.setdefault("PROJECT_DIR", str(tabr_root))
        if str(tabr_root) not in sys.path:
            sys.path.insert(0, str(tabr_root))
        from bin.tabr import Model  # type: ignore

        torch.manual_seed(seed)
        t_prep0 = time.perf_counter()
        x_mean = X_tr_in.mean(axis=0, keepdims=True)
        x_std = X_tr_in.std(axis=0, keepdims=True) + 1e-6
        y_mean = float(y_tr_in.mean())
        y_std = float(y_tr_in.std()) + 1e-6

        xt_n = torch.from_numpy(((X_tr_in - x_mean) / x_std).astype(np.float32))
        yt_n = torch.from_numpy(((y_tr_in - y_mean) / y_std).astype(np.float32))
        xiv_n = torch.from_numpy(((X_iv_in - x_mean) / x_std).astype(np.float32))
        yiv_n = torch.from_numpy(((y_iv_in - y_mean) / y_std).astype(np.float32))
        xval_n = torch.from_numpy(((X_val - x_mean) / x_std).astype(np.float32))
        preprocess_fit_sec = time.perf_counter() - t_prep0

        t_init0 = time.perf_counter()
        model = Model(
            n_num_features=501,
            n_bin_features=0,
            cat_cardinalities=[],
            n_classes=None,
            num_embeddings=None,
            d_main=int(cfg.get("d_main", 64)),
            d_multiplier=float(cfg.get("d_multiplier", 2.0)),
            encoder_n_blocks=int(cfg.get("encoder_n_blocks", 1)),
            predictor_n_blocks=int(cfg.get("predictor_n_blocks", 1)),
            mixer_normalization="auto",
            context_dropout=0.1,
            dropout0=0.1,
            dropout1="dropout0",
            normalization="LayerNorm",
            activation="ReLU",
        ).to("cpu")
        param_count = int(sum(p.numel() for p in model.parameters()))
        init_sec = time.perf_counter() - t_init0

        opt = torch.optim.AdamW(model.parameters(), lr=float(cfg.get("lr", 1e-3)), weight_decay=1e-4)
        loss_fn = torch.nn.MSELoss()
        bs = int(cfg.get("batch_size", 64))
        ctx = int(cfg.get("context_size", 32))
        max_ep = int(cfg.get("max_epochs", 80))
        pat = int(cfg.get("early_stopping_patience", 12))
        n_tr = xt_n.shape[0]
        gen = torch.Generator().manual_seed(seed)

        history = []
        best_iv_loss = float("inf")
        best_epoch = 0
        best_state = None
        no_imp = 0

        t_train0 = time.perf_counter()
        for ep in range(1, max_ep + 1):
            model.train()
            perm = torch.randperm(n_tr, generator=gen)
            tr_sum = 0.0
            for i in range(0, n_tr, bs):
                b_idx = perm[i : i + bs]
                mask = torch.ones(n_tr, dtype=torch.bool)
                mask[b_idx] = False
                cand_x = xt_n[mask]
                cand_y = yt_n[mask]
                opt.zero_grad(set_to_none=True)
                out = model(
                    x_={"num": xt_n[b_idx]},
                    y=yt_n[b_idx],
                    candidate_x_={"num": cand_x},
                    candidate_y=cand_y,
                    context_size=min(ctx, cand_x.shape[0]),
                    is_train=True,
                ).squeeze(-1)
                loss = loss_fn(out, yt_n[b_idx])
                if not torch.isfinite(loss):
                    raise FloatingPointError(f"Non-finite TabR loss at epoch {ep}.")
                loss.backward()
                opt.step()
                tr_sum += float(loss.item()) * len(b_idx)

            model.eval()
            iv_sum = 0.0
            with torch.no_grad():
                for i in range(0, xiv_n.shape[0], bs):
                    xb = xiv_n[i : i + bs]
                    yb = yiv_n[i : i + bs]
                    out = model(
                        x_={"num": xb},
                        y=None,
                        candidate_x_={"num": xt_n},
                        candidate_y=yt_n,
                        context_size=ctx,
                        is_train=False,
                    ).squeeze(-1)
                    iv_sum += float(loss_fn(out, yb).item()) * xb.shape[0]

            tr_mse = tr_sum / n_tr
            iv_mse = iv_sum / xiv_n.shape[0]
            history.append({"epoch": ep, "inner_train_mse": tr_mse, "inner_val_mse": iv_mse})
            if iv_mse < best_iv_loss - 1e-6:
                best_iv_loss = iv_mse
                best_epoch = ep
                best_state = copy.deepcopy(model.state_dict())
                no_imp = 0
            else:
                no_imp += 1
                if no_imp >= pat:
                    break
        train_sec = time.perf_counter() - t_train0

        if best_state is not None:
            model.load_state_dict(best_state)

        t_pred0 = time.perf_counter()
        model.eval()
        preds = []
        with torch.no_grad():
            for i in range(0, xval_n.shape[0], bs):
                xb = xval_n[i : i + bs]
                out = model(
                    x_={"num": xb},
                    y=None,
                    candidate_x_={"num": xt_n},
                    candidate_y=yt_n,
                    context_size=ctx,
                    is_train=False,
                ).squeeze(-1)
                preds.append(out.numpy())
        predict_sec = time.perf_counter() - t_pred0
        y_pred_raw = np.concatenate(preds, axis=0).astype(np.float64) * y_std + y_mean
        art_path = artifact_dir / f"{model_id}_{attempt_id}.pt"
        torch.save({"state_dict": model.state_dict(), "x_mean": x_mean, "x_std": x_std, "y_mean": y_mean, "y_std": y_std}, art_path)
        return {
            "y_pred_raw": y_pred_raw,
            "init_sec": init_sec,
            "preprocess_fit_sec": preprocess_fit_sec,
            "load_sec": 0.0,
            "train_or_context_sec": train_sec,
            "predict_sec": predict_sec,
            "param_count": param_count,
            "actual_epochs": len(history),
            "best_epoch": best_epoch,
            "history": history,
            "device": "cpu (faiss-cpu)",
            "peak_cuda_alloc_mb": None,
            "peak_cuda_res_mb": None,
            "artifact_path": art_path,
        }

    # 5. Aeon Signal Models (.venv-signal-tf, .venv-signal-cpu, .venv-signal-hydra)
    if model_id in {"SG02", "SG03", "SG04", "SG05", "SG06"}:
        X_tr_3d = X_tr_full[:, None, :]
        X_val_3d = X_val[:, None, :]
        t0 = time.perf_counter()
        if model_id == "SG02":
            from aeon.regression.deep_learning import ResNetRegressor
            est = ResNetRegressor(**cfg)
            dev = "cpu (native Windows TF)"
        elif model_id == "SG03":
            from aeon.regression.deep_learning import InceptionTimeRegressor
            est = InceptionTimeRegressor(**cfg)
            dev = "cpu (native Windows TF)"
        elif model_id == "SG04":
            from aeon.regression.deep_learning import LITETimeRegressor
            est = LITETimeRegressor(**cfg)
            dev = "cpu (native Windows TF)"
        elif model_id == "SG05":
            from aeon.regression.convolution_based import RocketRegressor
            est = RocketRegressor(**cfg)
            dev = "cpu"
        else:
            from aeon.regression.convolution_based import MultiRocketHydraRegressor
            est = MultiRocketHydraRegressor(**cfg)
            dev = "cpu"
        init_sec = time.perf_counter() - t0

        t1 = time.perf_counter()
        est.fit(X_tr_3d, y_tr_full)
        train_sec = time.perf_counter() - t1

        t2 = time.perf_counter()
        y_pred_raw = np.asarray(est.predict(X_val_3d), dtype=np.float64).reshape(-1)
        predict_sec = time.perf_counter() - t2

        art_path = artifact_dir / f"{model_id}_{attempt_id}.pkl"
        with art_path.open("wb") as f:
            pickle.dump(est, f)

        return {
            "y_pred_raw": y_pred_raw,
            "init_sec": init_sec,
            "preprocess_fit_sec": 0.0,
            "load_sec": 0.0,
            "train_or_context_sec": train_sec,
            "predict_sec": predict_sec,
            "param_count": None,
            "actual_epochs": cfg.get("n_epochs"),
            "best_epoch": None,
            "history": None,
            "device": dev,
            "peak_cuda_alloc_mb": None,
            "peak_cuda_res_mb": None,
            "artifact_path": art_path,
        }

    # 6. Foundation Models (.venv-foundation)
    if model_id in {"FM03", "FM04"}:
        import torch

        if torch.cuda.is_available():
            torch.cuda.init()
            torch.cuda.reset_peak_memory_stats(0)

        t_load0 = time.perf_counter()
        if model_id == "FM03":
            from tabicl import TabICLRegressor
            est = TabICLRegressor(**cfg)
            load_sec = time.perf_counter() - t_load0
            t_ctx0 = time.perf_counter()
            est.fit(X_tr_full, y_tr_full)
            if torch.cuda.is_available():
                torch.cuda.synchronize()
            ctx_sec = time.perf_counter() - t_ctx0
            t_pred0 = time.perf_counter()
            y_pred_raw = np.asarray(est.predict(X_val), dtype=np.float64).reshape(-1)
            if torch.cuda.is_available():
                torch.cuda.synchronize()
            predict_sec = time.perf_counter() - t_pred0
            meta_art = {"model_id": "FM03", "class": "TabICLRegressor", "config": cfg, "context_rows": int(X_tr_full.shape[0])}
        else:
            from tabdpt import TabDPTRegressor
            est = TabDPTRegressor(
                normalizer=cfg.get("normalizer", "standard"),
                feature_reduction=cfg.get("feature_reduction", "pca"),
                context_reduction=cfg.get("context_reduction", "retrieval"),
                use_flash=bool(cfg.get("use_flash", False)),
                compile=bool(cfg.get("compile", False)),
                verbose=False,
            )
            load_sec = time.perf_counter() - t_load0
            t_ctx0 = time.perf_counter()
            est.fit(X_tr_full, y_tr_full)
            if torch.cuda.is_available():
                torch.cuda.synchronize()
            ctx_sec = time.perf_counter() - t_ctx0
            t_pred0 = time.perf_counter()
            y_pred_raw = np.asarray(
                est.predict(
                    X_val,
                    n_ensembles=int(cfg.get("n_ensembles", 8)),
                    context_size=int(cfg.get("context_size", 2048)),
                    batch_size=int(cfg.get("batch_size", 128)),
                    seed=int(cfg.get("seed", seed)),
                ),
                dtype=np.float64,
            ).reshape(-1)
            if torch.cuda.is_available():
                torch.cuda.synchronize()
            predict_sec = time.perf_counter() - t_pred0
            meta_art = {
                "model_id": "FM04",
                "class": "TabDPTRegressor",
                "config": cfg,
                "context_rows": int(X_tr_full.shape[0]),
                "native_max_features": 128,
                "native_pca_compression_applied": True,
            }

        art_path = artifact_dir / f"{model_id}_{attempt_id}_context_meta.json"
        _atomic_write_json(art_path, meta_art)
        peak_alloc, peak_res = _gpu_sync_and_stats()
        return {
            "y_pred_raw": y_pred_raw,
            "init_sec": 0.0,
            "preprocess_fit_sec": 0.0,
            "load_sec": load_sec,
            "train_or_context_sec": ctx_sec,
            "predict_sec": predict_sec,
            "param_count": None,
            "actual_epochs": None,
            "best_epoch": None,
            "history": None,
            "device": "cuda:0" if torch.cuda.is_available() else "cpu",
            "peak_cuda_alloc_mb": peak_alloc,
            "peak_cuda_res_mb": peak_res,
            "artifact_path": art_path,
        }

    raise ValueError(f"Unsupported model_id for M04A: {model_id}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--config-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--split-manifest", required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--authorized-phase", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--config-json", required=True)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    artifact_dir = ROOT / "reports" / "runs" / args.run_id / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    cfg = json.loads(Path(args.config_json).read_text(encoding="utf-8"))
    raw_csv = ROOT / "data" / "raw" / "krkCMd_table.csv"
    data = load_protocol_a_train_val(
        raw_csv_path=raw_csv,
        split_manifest_path=Path(args.split_manifest),
        authorized_phase=args.authorized_phase,
        seed=args.seed,
    )

    t_total0 = time.perf_counter()
    safe_attempt = Path(args.attempt_id).name
    res = run_model(args.model_id, cfg, data, args.seed, artifact_dir, safe_attempt)
    total_elapsed = time.perf_counter() - t_total0

    y_pred_raw = np.asarray(res["y_pred_raw"], dtype=np.float64)
    if y_pred_raw.shape != (EXPECTED_VAL_ROWS,) or not np.isfinite(y_pred_raw).all():
        raise ValueError(f"Invalid validation prediction shape {y_pred_raw.shape} or non-finite values.")

    y_pred_clip = np.maximum(0.0, y_pred_raw)
    signed_err = y_pred_raw - data.y_val
    abs_err = np.abs(signed_err)

    pred_df = data.val_meta.copy()
    pred_df.insert(0, "seed", args.seed)
    pred_df.insert(0, "config_id", args.config_id)
    pred_df.insert(0, "model_id", args.model_id)
    pred_df.insert(0, "attempt_id", args.attempt_id)
    pred_df.insert(0, "run_id", args.run_id)
    pred_df["y_true_um"] = data.y_val
    pred_df["y_pred_raw_um"] = y_pred_raw
    pred_df["y_pred_nonnegative_um"] = y_pred_clip
    pred_df["raw_signed_error_um"] = signed_err
    pred_df["raw_absolute_error_um"] = abs_err

    pred_path = out_dir / "predictions.csv"
    pred_df.to_csv(pred_path, index=False)

    if res.get("history") is not None:
        _atomic_write_json(out_dir / f"M04A_TRAINING_HISTORY_{args.model_id}.json", {"model_id": args.model_id, "history": res["history"]})

    art_path = Path(res["artifact_path"])
    worker_summary = {
        "status": "PASS",
        "model_id": args.model_id,
        "config_id": args.config_id,
        "run_id": args.run_id,
        "attempt_id": args.attempt_id,
        "seed": args.seed,
        "n_val_predictions": int(len(pred_df)),
        "n_negative_raw_predictions": int((y_pred_raw < 0).sum()),
        "min_raw_prediction_um": float(np.min(y_pred_raw)),
        "init_sec": round(res["init_sec"], 4),
        "preprocess_fit_sec": round(res["preprocess_fit_sec"], 4),
        "load_sec": round(res["load_sec"], 4),
        "train_or_context_sec": round(res["train_or_context_sec"], 4),
        "predict_sec": round(res["predict_sec"], 4),
        "total_elapsed_sec": round(total_elapsed, 4),
        "val_throughput_rows_per_sec": round(EXPECTED_VAL_ROWS / max(res["predict_sec"], 1e-6), 2),
        "param_count": res["param_count"],
        "actual_epochs": res["actual_epochs"],
        "best_epoch": res["best_epoch"],
        "device": res["device"],
        "peak_cuda_alloc_mb": res["peak_cuda_alloc_mb"],
        "peak_cuda_res_mb": res["peak_cuda_res_mb"],
        "artifact_path": str(art_path),
        "artifact_size_bytes": int(art_path.stat().st_size),
        "artifact_sha256": _sha256_file(art_path),
        "data_audit": data.audit,
    }
    _atomic_write_json(out_dir / "worker_result.json", worker_summary)
    print(f"WORKER_PASS {args.model_id} raw_mae={float(abs_err.mean()):.4f} wall={total_elapsed:.2f}s")


if __name__ == "__main__":
    main()
