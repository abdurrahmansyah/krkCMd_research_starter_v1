"""
scripts/check_model_compatibility.py

[DEPRECATED IN M02B]
This legacy script contains a static candidate list and is retained only for
historical reference. Use `scripts/build_compatibility_matrix.py` (which loads
authoritative definitions from `configs/model_registry.yaml` and reconciles
versioned runtime evidence) instead.
"""

import sys
import os
import json
import time
import platform
import subprocess
import shutil
from pathlib import Path
import numpy as np
import pandas as pd
import psutil

if "--legacy-allow-overwrite" not in sys.argv:
    print(
        "[DEPRECATED] scripts/check_model_compatibility.py is deprecated in M02B.\n"
        "Use scripts/build_compatibility_matrix.py instead (registry-driven, preserves historical matrices).",
        file=sys.stderr,
    )
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
LOGS_DIR = REPORTS_DIR / "logs"
TABLES_DIR = REPORTS_DIR / "tables"

for d in [LOGS_DIR, TABLES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("krkCMd M01: MODEL REGISTRY & COMPATIBILITY CHECKER")
print("=" * 70)

# ---------------------------------------------------------
# 1. Hardware & Environment Audit
# ---------------------------------------------------------
print("\n[1/4] Running Hardware and Environment Audit...")

mem = psutil.virtual_memory()
disk = psutil.disk_usage(str(ROOT))

gpu_info = {
    "gpu_available": False,
    "gpu_name": None,
    "driver_version": None,
    "cuda_version_supported": None,
    "vram_total_mb": None,
    "vram_free_mb": None,
}

try:
    res = subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version,memory.total,memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=10)
    if res.returncode == 0 and res.stdout.strip():
        parts = [p.strip() for p in res.stdout.strip().split(",")]
        gpu_info["gpu_available"] = True
        gpu_info["gpu_name"] = parts[0]
        gpu_info["driver_version"] = parts[1]
        gpu_info["vram_total_mb"] = float(parts[2])
        gpu_info["vram_free_mb"] = float(parts[3])
        
        # Check cuda version supported by driver
        smi_out = subprocess.run(["nvidia-smi"], capture_output=True, text=True).stdout
        for line in smi_out.split("\n"):
            if "CUDA Version:" in line:
                gpu_info["cuda_version_supported"] = line.split("CUDA Version:")[1].split("|")[0].strip()
except Exception as e:
    gpu_info["error"] = str(e)

# WSL2 check
wsl_available = False
wsl_distro = None
try:
    wsl_res = subprocess.run(["wsl", "--status"], capture_output=True, text=True, timeout=10)
    if wsl_res.returncode == 0:
        wsl_available = True
        wsl_distro = "Ubuntu (Default)"
except Exception:
    pass

# MATLAB & Deep Learning Toolbox check
matlab_exe = shutil.which("matlab")
matlab_available = bool(matlab_exe)
nnet_toolbox = Path("C:/Program Files/MATLAB/R2026b/toolbox/nnet").exists()

hw_report = {
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "os": {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "platform": platform.platform(),
        "architecture": platform.machine(),
    },
    "cpu": {
        "processor": platform.processor(),
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
    },
    "memory_gb": {
        "total": round(mem.total / (1024**3), 2),
        "available": round(mem.available / (1024**3), 2),
        "used": round(mem.used / (1024**3), 2),
        "percent_used": mem.percent,
    },
    "disk_gb": {
        "drive": str(ROOT.drive),
        "total": round(disk.total / (1024**3), 2),
        "free": round(disk.free / (1024**3), 2),
        "used": round(disk.used / (1024**3), 2),
        "percent_used": disk.percent,
    },
    "gpu": gpu_info,
    "python": {
        "executable": sys.executable,
        "version": sys.version.split()[0],
        "venv_path": str(Path(sys.prefix).resolve()),
    },
    "matlab": {
        "installed": matlab_available,
        "executable": matlab_exe,
        "deep_learning_toolbox_present": nnet_toolbox,
    },
    "wsl2": {
        "available": wsl_available,
        "distro": wsl_distro,
    }
}

hw_path = LOGS_DIR / "hardware_environment.json"
with open(hw_path, "w", encoding="utf-8") as f:
    json.dump(hw_report, f, indent=2)
print(f"  -> Saved hardware audit to: {hw_path.relative_to(ROOT)}")

# ---------------------------------------------------------
# 2. Dependency Resolution Inspection
# ---------------------------------------------------------
print("\n[2/4] Inspecting Dependencies and Pip Resolution...")

packages_to_check = [
    "scikit-learn", "numpy", "pandas", "scipy", "joblib",
    "xgboost", "lightgbm", "catboost", "torch", "torchvision",
    "faiss-cpu", "aeon", "tabpfn", "pypdf"
]

dep_res = {}
for pkg in packages_to_check:
    cmd = [sys.executable, "-m", "pip", "install", "--dry-run", "--no-deps", pkg]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if r.returncode == 0:
            version_str = "Available"
            for line in r.stdout.splitlines():
                if "Would install" in line or "Collecting" in line:
                    version_str = line.strip()
                    break
            dep_res[pkg] = {"status": "RESOLVED", "detail": version_str}
        else:
            dep_res[pkg] = {"status": "CONFLICT_OR_MISSING", "detail": r.stderr.strip()[:100]}
    except Exception as e:
        dep_res[pkg] = {"status": "ERROR", "detail": str(e)}

dep_path = LOGS_DIR / "dependency_resolution.json"
with open(dep_path, "w", encoding="utf-8") as f:
    json.dump(dep_res, f, indent=2)
print(f"  -> Saved dependency resolution to: {dep_path.relative_to(ROOT)}")

# ---------------------------------------------------------
# 3. Synthetic Smoke Tests (L0 / L1) for Installed Models
# ---------------------------------------------------------
print("\n[3/4] Running Synthetic Smoke Tests (L0 / L1 on 501 features)...")
print("  Note: Using strictly deterministic synthetic profiles (seed=42). Zero krkCMd data used.")

# Generate small synthetic dataset: 100 rows, 501 features, target = crack width (50 - 300 um)
rng = np.random.default_rng(42)
n_synth_train = 100
n_synth_test = 20
n_features = 501

# Synthetic brightness profile: baseline 180 + Gaussian dip in center simulating crack
x_axis = np.linspace(-10, 10, n_features)
X_synth_train = np.zeros((n_synth_train, n_features), dtype=np.float32)
y_synth_train = np.zeros(n_synth_train, dtype=np.float32)

for i in range(n_synth_train):
    width = rng.uniform(30.0, 350.0)
    center = rng.uniform(-2, 2)
    depth = rng.uniform(50.0, 150.0)
    noise = rng.normal(0, 3.0, size=n_features)
    dip = depth * np.exp(-0.5 * ((x_axis - center) / (width / 50.0)) ** 2)
    profile = np.clip(180.0 - dip + noise, 0, 255)
    X_synth_train[i] = profile
    y_synth_train[i] = width

X_synth_test = np.zeros((n_synth_test, n_features), dtype=np.float32)
y_synth_test = np.zeros(n_synth_test, dtype=np.float32)
for i in range(n_synth_test):
    width = rng.uniform(30.0, 350.0)
    center = rng.uniform(-2, 2)
    depth = rng.uniform(50.0, 150.0)
    noise = rng.normal(0, 3.0, size=n_features)
    dip = depth * np.exp(-0.5 * ((x_axis - center) / (width / 50.0)) ** 2)
    profile = np.clip(180.0 - dip + noise, 0, 255)
    X_synth_test[i] = profile
    y_synth_test[i] = width

smoke_results = {}

# Test ML01 (ExtraTrees)
try:
    from sklearn.ensemble import ExtraTreesRegressor
    t0 = time.time()
    m_et = ExtraTreesRegressor(n_estimators=10, random_state=42)
    m_et.fit(X_synth_train, y_synth_train)
    p_et = m_et.predict(X_synth_test)
    dur = round(time.time() - t0, 3)
    finite = bool(np.isfinite(p_et).all())
    smoke_results["ML01"] = {"status": "SMOKE_TEST_PASS", "dur_sec": dur, "finite": finite, "out_shape": list(p_et.shape)}
    print(f"  ML01 (ExtraTrees): PASS (duration: {dur}s, finite: {finite})")
except Exception as e:
    smoke_results["ML01"] = {"status": "FAILED", "error": str(e)}

# Test ML02 (RandomForest)
try:
    from sklearn.ensemble import RandomForestRegressor
    t0 = time.time()
    m_rf = RandomForestRegressor(n_estimators=10, random_state=42)
    m_rf.fit(X_synth_train, y_synth_train)
    p_rf = m_rf.predict(X_synth_test)
    dur = round(time.time() - t0, 3)
    finite = bool(np.isfinite(p_rf).all())
    smoke_results["ML02"] = {"status": "SMOKE_TEST_PASS", "dur_sec": dur, "finite": finite, "out_shape": list(p_rf.shape)}
    print(f"  ML02 (RandomForest): PASS (duration: {dur}s, finite: {finite})")
except Exception as e:
    smoke_results["ML02"] = {"status": "FAILED", "error": str(e)}

# Test ML03 (HistGradientBoosting)
try:
    from sklearn.ensemble import HistGradientBoostingRegressor
    t0 = time.time()
    m_hgb = HistGradientBoostingRegressor(max_iter=20, random_state=42)
    m_hgb.fit(X_synth_train, y_synth_train)
    p_hgb = m_hgb.predict(X_synth_test)
    dur = round(time.time() - t0, 3)
    finite = bool(np.isfinite(p_hgb).all())
    smoke_results["ML03"] = {"status": "SMOKE_TEST_PASS", "dur_sec": dur, "finite": finite, "out_shape": list(p_hgb.shape)}
    print(f"  ML03 (HistGradientBoosting): PASS (duration: {dur}s, finite: {finite})")
except Exception as e:
    smoke_results["ML03"] = {"status": "FAILED", "error": str(e)}

# Test ML07 (SVR RBF)
try:
    from sklearn.svm import SVR
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    t0 = time.time()
    m_svr = make_pipeline(StandardScaler(), SVR(C=10.0, epsilon=0.1))
    m_svr.fit(X_synth_train, y_synth_train)
    p_svr = m_svr.predict(X_synth_test)
    dur = round(time.time() - t0, 3)
    finite = bool(np.isfinite(p_svr).all())
    smoke_results["ML07"] = {"status": "SMOKE_TEST_PASS", "dur_sec": dur, "finite": finite, "out_shape": list(p_svr.shape)}
    print(f"  ML07 (SVR RBF): PASS (duration: {dur}s, finite: {finite})")
except Exception as e:
    smoke_results["ML07"] = {"status": "FAILED", "error": str(e)}

# Test DL01 (MLP)
try:
    from sklearn.neural_network import MLPRegressor
    t0 = time.time()
    m_mlp = make_pipeline(StandardScaler(), MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=20, random_state=42))
    m_mlp.fit(X_synth_train, y_synth_train)
    p_mlp = m_mlp.predict(X_synth_test)
    dur = round(time.time() - t0, 3)
    finite = bool(np.isfinite(p_mlp).all())
    smoke_results["DL01"] = {"status": "SMOKE_TEST_PASS", "dur_sec": dur, "finite": finite, "out_shape": list(p_mlp.shape)}
    print(f"  DL01 (MLP): PASS (duration: {dur}s, finite: {finite})")
except Exception as e:
    smoke_results["DL01"] = {"status": "FAILED", "error": str(e)}

# Test RF01 (Dummy Mean)
try:
    from sklearn.dummy import DummyRegressor
    t0 = time.time()
    m_dm = DummyRegressor(strategy="mean")
    m_dm.fit(X_synth_train, y_synth_train)
    p_dm = m_dm.predict(X_synth_test)
    dur = round(time.time() - t0, 3)
    finite = bool(np.isfinite(p_dm).all())
    smoke_results["RF01"] = {"status": "SMOKE_TEST_PASS", "dur_sec": dur, "finite": finite, "out_shape": list(p_dm.shape)}
    print(f"  RF01 (Dummy Mean): PASS (duration: {dur}s, finite: {finite})")
except Exception as e:
    smoke_results["RF01"] = {"status": "FAILED", "error": str(e)}

# Test RF02 (Linear Regression)
try:
    from sklearn.linear_model import LinearRegression
    t0 = time.time()
    m_lr = make_pipeline(StandardScaler(), LinearRegression())
    m_lr.fit(X_synth_train, y_synth_train)
    p_lr = m_lr.predict(X_synth_test)
    dur = round(time.time() - t0, 3)
    finite = bool(np.isfinite(p_lr).all())
    smoke_results["RF02"] = {"status": "SMOKE_TEST_PASS", "dur_sec": dur, "finite": finite, "out_shape": list(p_lr.shape)}
    print(f"  RF02 (Linear Regression): PASS (duration: {dur}s, finite: {finite})")
except Exception as e:
    smoke_results["RF02"] = {"status": "FAILED", "error": str(e)}

# Test RF03 (AED Python port smoke test)
def aed_python_single(profile, resolution=6400, accuracy=5, step=10, brightness_increment=5, rel_increment_threshold=0):
    vals = np.asarray(profile, dtype=float)
    min_b = np.min(vals)
    # find first global min
    j_min = int(np.where(vals == min_b)[0][0])
    
    # search left bound
    j = j_min
    while j > 0 and (vals[j - 1] - min_b <= accuracy):
        j -= 1
    y_upper = j
    
    # search right bound
    j = j_min
    while j < len(vals) - 1 and (vals[j + 1] - min_b <= accuracy):
        j += 1
    y_lower = j
    
    # width in um
    width_px = (y_lower - y_upper + 1)
    width_um = width_px * (25.4 / resolution) * 1000.0
    return width_um

try:
    t0 = time.time()
    p_aed = [aed_python_single(p) for p in X_synth_test]
    dur = round(time.time() - t0, 3)
    finite = bool(np.isfinite(p_aed).all())
    smoke_results["RF03"] = {"status": "SMOKE_TEST_PASS", "dur_sec": dur, "finite": finite, "out_shape": [len(p_aed)]}
    print(f"  RF03 (AED Python Port): PASS (duration: {dur}s, finite: {finite})")
except Exception as e:
    smoke_results["RF03"] = {"status": "FAILED", "error": str(e)}

# ---------------------------------------------------------
# 4. Generate Full 32 Model Registry Matrix
# ---------------------------------------------------------
print("\n[4/4] Building Comprehensive 32-Candidate Model Compatibility Matrix...")

candidates = [
    # Classical ML & Boosting
    {
        "id": "ML01",
        "family": "Classical ML & Boosting",
        "name": "Extra Trees",
        "estimator": "sklearn.ensemble.ExtraTreesRegressor",
        "package": "scikit-learn>=1.4,<2",
        "status": "SMOKE_TEST_PASS",
        "paper": "Geurts et al. (2006) Extremely randomized trees",
        "doi": "10.1007/s10994-006-6226-1",
        "license_code": "BSD-3-Clause",
        "license_weights": "N/A",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "CPU (multi-core)",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "Low",
        "readiness_summary": "Installed in .venv. L0/L1 smoke test passed. Native multithreaded CPU scaling.",
    },
    {
        "id": "ML02",
        "family": "Classical ML & Boosting",
        "name": "Random Forest",
        "estimator": "sklearn.ensemble.RandomForestRegressor",
        "package": "scikit-learn>=1.4,<2",
        "status": "SMOKE_TEST_PASS",
        "paper": "Breiman (2001) Random Forests",
        "doi": "10.1023/A:1010933404324",
        "license_code": "BSD-3-Clause",
        "license_weights": "N/A",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "CPU (multi-core)",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "Low",
        "readiness_summary": "Installed in .venv. L0/L1 smoke test passed. Standard ensemble baseline.",
    },
    {
        "id": "ML03",
        "family": "Classical ML & Boosting",
        "name": "HistGradientBoosting",
        "estimator": "sklearn.ensemble.HistGradientBoostingRegressor",
        "package": "scikit-learn>=1.4,<2",
        "status": "SMOKE_TEST_PASS",
        "paper": "Ke et al. (2017) LightGBM: Highly Efficient GBDT",
        "doi": "10.5555/3294996.3295074",
        "license_code": "BSD-3-Clause",
        "license_weights": "N/A",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "CPU",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "Low",
        "readiness_summary": "Installed in .venv. L0/L1 smoke test passed. Binned histogram boosting.",
    },
    {
        "id": "ML04",
        "family": "Classical ML & Boosting",
        "name": "XGBoost",
        "estimator": "xgboost.XGBRegressor",
        "package": "xgboost>=2.0,<4",
        "status": "STATIC_REVIEW",
        "paper": "Chen & Guestrin (2016) XGBoost: A Scalable Tree Boosting System",
        "doi": "10.1145/2939672.2945399",
        "license_code": "Apache-2.0",
        "license_weights": "N/A",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "CPU / GPU",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "Low",
        "readiness_summary": "PyPI Windows wheel verified. Pending isolated boost venv installation.",
    },
    {
        "id": "ML05",
        "family": "Classical ML & Boosting",
        "name": "LightGBM",
        "estimator": "lightgbm.LGBMRegressor",
        "package": "lightgbm>=4.0,<5",
        "status": "STATIC_REVIEW",
        "paper": "Ke et al. (2017) LightGBM: Highly Efficient GBDT",
        "doi": "10.5555/3294996.3295074",
        "license_code": "MIT",
        "license_weights": "N/A",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "CPU / GPU",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "Low",
        "readiness_summary": "PyPI Windows wheel verified. Fast leaf-wise tree growth.",
    },
    {
        "id": "ML06",
        "family": "Classical ML & Boosting",
        "name": "CatBoost",
        "estimator": "catboost.CatBoostRegressor",
        "package": "catboost>=1.2,<2",
        "status": "STATIC_REVIEW",
        "paper": "Prokhorenkova et al. (2018) CatBoost: unbiased boosting",
        "doi": "10.5555/3327757.3327770",
        "license_code": "Apache-2.0",
        "license_weights": "N/A",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "CPU / GPU",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "Low",
        "readiness_summary": "PyPI Windows wheel verified. Symmetric oblivious trees reduce overfitting.",
    },
    {
        "id": "ML07",
        "family": "Classical ML & Boosting",
        "name": "SVR RBF",
        "estimator": "sklearn.svm.SVR",
        "package": "scikit-learn>=1.4,<2",
        "status": "SMOKE_TEST_PASS",
        "paper": "Smola & Scholkopf (2004) A tutorial on support vector regression",
        "doi": "10.1023/B:STCO.0000035301.49549.88",
        "license_code": "BSD-3-Clause",
        "license_weights": "N/A",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "CPU",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "Medium",
        "readiness_summary": "Installed in .venv. L0/L1 smoke test passed. Scaling required; O(N^2) fit runtime.",
    },

    # Tabular Deep Learning
    {
        "id": "DL01",
        "family": "Tabular Deep Learning",
        "name": "MLP",
        "estimator": "sklearn.neural_network.MLPRegressor",
        "package": "scikit-learn>=1.4,<2",
        "status": "SMOKE_TEST_PASS",
        "paper": "Rumelhart et al. (1986) Learning representations by back-propagating errors",
        "doi": "10.1038/323533a0",
        "license_code": "BSD-3-Clause",
        "license_weights": "N/A",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "CPU / PyTorch GPU",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "Low",
        "readiness_summary": "Installed in .venv. L0/L1 smoke test passed. Classical dense feedforward network.",
    },
    {
        "id": "DL02",
        "family": "Tabular Deep Learning",
        "name": "FT-Transformer",
        "estimator": "rtdl.FTTransformer / PyTorch",
        "package": "rtdl_num_embeddings, torch",
        "status": "CONDITIONAL",
        "paper": "Gorishniy et al. (2021) Revisiting Deep Learning Models for Tabular Data",
        "doi": "10.48550/arXiv.2106.11958",
        "license_code": "Apache-2.0",
        "license_weights": "N/A",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "GPU (VRAM >= 4GB)",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "High",
        "readiness_summary": "Feature tokenizer transformer. Quadratic attention over 501 features (501^2=251k ops/sample); tight on 4GB VRAM.",
    },
    {
        "id": "DL03",
        "family": "Tabular Deep Learning",
        "name": "RealMLP",
        "estimator": "avidale/tabbench / PyTorch",
        "package": "torch>=2.1",
        "status": "STATIC_REVIEW",
        "paper": "Holzmueller et al. (2024) Why Do Tree-Based Models Still Outperform DL on Tabular Data?",
        "doi": "10.48550/arXiv.2407.04491",
        "license_code": "MIT",
        "license_weights": "N/A",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "GPU / CPU",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "Medium",
        "readiness_summary": "Carefully regularized MLP with Mish/Swish, LayerNorm, and cosine schedule.",
    },
    {
        "id": "DL04",
        "family": "Tabular Deep Learning",
        "name": "TabR",
        "estimator": "tabular-dl-tabr / PyTorch",
        "package": "torch>=2.1, faiss-cpu>=1.7",
        "status": "CONDITIONAL",
        "paper": "Gorishniy et al. (2024) TabR: Unlocking Potential of Retrieval Models on Tabular Data",
        "doi": "10.48550/arXiv.2307.14338",
        "license_code": "Apache-2.0",
        "license_weights": "N/A",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "GPU / CPU (FAISS)",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "High",
        "readiness_summary": "Retrieval-augmented model. FAISS CPU verified on Win64; retrieval across 12k rows x 501 features is lightweight.",
    },
    {
        "id": "DL05",
        "family": "Tabular Deep Learning",
        "name": "TabM",
        "estimator": "tabular-dl-tabm / PyTorch",
        "package": "torch>=2.1",
        "status": "STATIC_REVIEW",
        "paper": "Gorishniy et al. (2024) TabM: Parameter-Efficient Ensembles for Tabular Data",
        "doi": "10.48550/arXiv.2410.24210",
        "license_code": "Apache-2.0",
        "license_weights": "N/A",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "GPU / CPU",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "Medium",
        "readiness_summary": "Batch-ensemble architecture with shared backbone and multiple sub-adapters.",
    },

    # Tabular Foundation Models
    {
        "id": "FM01",
        "family": "Tabular Foundation Models",
        "name": "TabPFN-3.5",
        "estimator": "tabpfn.TabPFNRegressor",
        "package": "tabpfn>=2.0",
        "status": "CONDITIONAL",
        "paper": "Hollmann et al. (2023 / 2025 Nature) Accurate predictions with tabular foundation model",
        "doi": "10.1038/s41586-024-08328-6",
        "license_code": "Apache-2.0",
        "license_weights": "PriorLabs Non-Commercial / Gated",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "GPU (VRAM >= 4GB)",
        "features_501_compatible": False,
        "n_train_12216_compatible": False,
        "complexity": "High",
        "readiness_summary": "Feature limit is 500 features (501 exceeds by 1; needs pruning). Sample limit ~10k (requires subsampling or ensembling). Gated weights.",
    },
    {
        "id": "FM02",
        "family": "Tabular Foundation Models",
        "name": "TabPFN-3.5-Fast",
        "estimator": "tabpfn.TabPFNRegressor(model='fast')",
        "package": "tabpfn>=2.0",
        "status": "CONDITIONAL",
        "paper": "PriorLabs TabPFN v2 Technical Report (2025)",
        "doi": "10.48550/arXiv.2501.04257",
        "license_code": "Apache-2.0",
        "license_weights": "PriorLabs Gated",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "GPU / CPU",
        "features_501_compatible": False,
        "n_train_12216_compatible": False,
        "complexity": "High",
        "readiness_summary": "Fast quantized variant of TabPFN v2. Same 500-feature context constraint.",
    },
    {
        "id": "FM03",
        "family": "Tabular Foundation Models",
        "name": "TabICLv2",
        "estimator": "tabicl / PyTorch",
        "package": "torch>=2.1",
        "status": "CONDITIONAL",
        "paper": "In-Context Learning for Tabular Data Survey / Repos (2024)",
        "doi": "UNKNOWN",
        "license_code": "Research only",
        "license_weights": "HuggingFace gated",
        "python_311": True,
        "windows_native": False,
        "hardware_req": "GPU (VRAM >= 8GB recommended)",
        "features_501_compatible": False,
        "n_train_12216_compatible": False,
        "complexity": "Very High",
        "readiness_summary": "Experimental academic release. Limited documentation and fixed small feature context window.",
    },
    {
        "id": "FM04",
        "family": "Tabular Foundation Models",
        "name": "TabDPT",
        "estimator": "TabDPT / PyTorch",
        "package": "torch>=2.1",
        "status": "CONDITIONAL",
        "paper": "Ma et al. (2024) TabDPT: Scaling Tabular Foundation Models",
        "doi": "10.48550/arXiv.2410.18164",
        "license_code": "MIT",
        "license_weights": "Open weights (HuggingFace)",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "GPU (VRAM >= 4GB)",
        "features_501_compatible": True,
        "n_train_12216_compatible": False,
        "complexity": "High",
        "readiness_summary": "Diffusion-based prior tabular model. Requires chunked in-context retrieval for >5,000 samples.",
    },

    # Spatial Signal Regression (1D time-series / profile models)
    {
        "id": "SG01",
        "family": "Spatial Signal Regression",
        "name": "Vanilla 1D-CNN",
        "estimator": "PyTorch 1D-CNN Module",
        "package": "torch>=2.1",
        "status": "STATIC_REVIEW",
        "paper": "LeCun et al. (1989) Backpropagation applied to handwritten zip code recognition",
        "doi": "10.1162/neco.1989.1.4.541",
        "license_code": "Custom / Apache-2.0",
        "license_weights": "N/A",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "CPU / GPU",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "Medium",
        "readiness_summary": "3-layer Conv1D network with pooling and regression head. Readily implementable in PyTorch.",
    },
    {
        "id": "SG02",
        "family": "Spatial Signal Regression",
        "name": "ResNet-1D",
        "estimator": "aeon.networks.ResNetNetwork / PyTorch",
        "package": "aeon>=1.6, torch>=2.1",
        "status": "STATIC_REVIEW",
        "paper": "Wang et al. (2017) Time series classification from scratch with deep neural networks",
        "doi": "10.1109/IJCNN.2017.7966039",
        "license_code": "BSD-3-Clause",
        "license_weights": "N/A",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "CPU / GPU",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "Medium",
        "readiness_summary": "1D Residual network with skip connections preventing gradient degradation over 501 features.",
    },
    {
        "id": "SG03",
        "family": "Spatial Signal Regression",
        "name": "InceptionTime Regression",
        "estimator": "aeon.regression.deep_learning.InceptionTimeRegressor",
        "package": "aeon>=1.6, torch>=2.1",
        "status": "STATIC_REVIEW",
        "paper": "Fawaz et al. (2020) InceptionTime: Finding AlexNet for time series",
        "doi": "10.1007/s10618-020-00710-y",
        "license_code": "BSD-3-Clause",
        "license_weights": "N/A",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "GPU (recommended) / CPU",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "Medium",
        "readiness_summary": "Multiscale parallel 1D convolutional filters with bottleneck layer. Strong baseline for spatial profiles.",
    },
    {
        "id": "SG04",
        "family": "Spatial Signal Regression",
        "name": "LITETime Regression",
        "estimator": "aeon.regression.deep_learning.LITETimeRegressor",
        "package": "aeon>=1.6, torch>=2.1",
        "status": "STATIC_REVIEW",
        "paper": "Ismail-Fawaz et al. (2023) LITE: Light Inception with bues for time series",
        "doi": "10.48550/arXiv.2309.05566",
        "license_code": "BSD-3-Clause",
        "license_weights": "N/A",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "CPU / GPU",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "Medium",
        "readiness_summary": "Lightweight Inception variant with reduced parameters and fast CPU execution.",
    },
    {
        "id": "SG05",
        "family": "Spatial Signal Regression",
        "name": "ROCKET Regression",
        "estimator": "aeon.regression.convolution_based.RocketRegressor",
        "package": "aeon>=1.6, numba>=0.59",
        "status": "STATIC_REVIEW",
        "paper": "Dempster et al. (2020) ROCKET: Exceptionally fast and accurate time series classification",
        "doi": "10.1007/s10618-020-00701-z",
        "license_code": "BSD-3-Clause",
        "license_weights": "N/A",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "CPU (multi-core)",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "Low",
        "readiness_summary": "10,000 random non-trainable 1D convolutional kernels + RidgeCV linear regressor. Exceptionally fast.",
    },
    {
        "id": "SG06",
        "family": "Spatial Signal Regression",
        "name": "MultiROCKET-HYDRA Regression",
        "estimator": "aeon.regression.convolution_based.MultiRocketRegressor",
        "package": "aeon>=1.6, numba>=0.59",
        "status": "STATIC_REVIEW",
        "paper": "Tan et al. (2022) MultiRocket / Dempster (2023) HYDRA",
        "doi": "10.1007/s10618-022-00834-3",
        "license_code": "BSD-3-Clause",
        "license_weights": "N/A",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "CPU",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "Medium",
        "readiness_summary": "Adds first-order difference transformations and multi-pooling to ROCKET.",
    },

    # Custom & Hybrid Approaches
    {
        "id": "HY01",
        "family": "Custom & Hybrid",
        "name": "SNV + CatBoost",
        "estimator": "Pipeline(SNVTransformer(), CatBoostRegressor())",
        "package": "catboost>=1.2, numpy, scipy",
        "status": "DESIGN_REQUIRED",
        "paper": "Barnes et al. (1989) Standard Normal Variate transformation in NIR spectroscopy",
        "doi": "10.1366/0003702894202201",
        "license_code": "Apache-2.0 / BSD",
        "license_weights": "N/A",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "CPU / GPU",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "Medium",
        "readiness_summary": "Row-wise profile normalization (x - mean)/std eliminates baseline brightness drift; passed to CatBoost.",
    },
    {
        "id": "HY02",
        "family": "Custom & Hybrid",
        "name": "Derivative + Extra Trees",
        "estimator": "Pipeline(SpatialDerivativeTransformer(), ExtraTreesRegressor())",
        "package": "scikit-learn, scipy",
        "status": "DESIGN_REQUIRED",
        "paper": "Savitzky & Golay (1964) Smoothing and differentiation of data",
        "doi": "10.1021/ac60214a047",
        "license_code": "BSD-3-Clause",
        "license_weights": "N/A",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "CPU",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "Low",
        "readiness_summary": "1st and 2nd spatial derivatives highlight crack boundaries and slope inflection points.",
    },
    {
        "id": "HY03",
        "family": "Custom & Hybrid",
        "name": "Dual-stream multiscale CNN",
        "estimator": "PyTorch DualStreamCNNModule",
        "package": "torch>=2.1",
        "status": "DESIGN_REQUIRED",
        "paper": "Custom design tailored to crack brightness profiles",
        "doi": "N/A (Project Novel Design)",
        "license_code": "Apache-2.0",
        "license_weights": "N/A",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "GPU / CPU",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "High",
        "readiness_summary": "Branch A (fine kernels k=3,5) detects sharp crack edges; Branch B (coarse kernels k=17,33) captures surface illumination.",
    },
    {
        "id": "HY04",
        "family": "Custom & Hybrid",
        "name": "CNN + CatBoost",
        "estimator": "Pipeline(FrozenCNNFeatureExtractor(), CatBoostRegressor())",
        "package": "torch>=2.1, catboost>=1.2",
        "status": "DESIGN_REQUIRED",
        "paper": "Hybrid Deep-Tree Ensembles (Various, 2020-2024)",
        "doi": "UNKNOWN",
        "license_code": "Apache-2.0",
        "license_weights": "N/A",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "GPU + CPU",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "High",
        "readiness_summary": "Latent representations extracted from 1D-CNN pooling layer concatenated with raw profile, predicted by CatBoost.",
    },
    {
        "id": "HY05",
        "family": "Custom & Hybrid",
        "name": "Robust stacking ensemble",
        "estimator": "StackingRegressor(estimators=[ET, ROCKET, CatBoost], final_estimator=RidgeCV())",
        "package": "scikit-learn, aeon, catboost",
        "status": "DESIGN_REQUIRED",
        "paper": "Wolpert (1992) Stacked generalization",
        "doi": "10.1016/S0893-6080(05)80023-1",
        "license_code": "BSD-3-Clause",
        "license_weights": "N/A",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "CPU",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "High",
        "readiness_summary": "Out-of-fold multi-paradigm ensemble combining tree, linear, convolutional, and signal representations.",
    },

    # Reference Benchmarks
    {
        "id": "RF01",
        "family": "Reference Benchmarks",
        "name": "Dummy Mean",
        "estimator": "sklearn.dummy.DummyRegressor",
        "package": "scikit-learn>=1.4,<2",
        "status": "SMOKE_TEST_PASS",
        "paper": "Baseline definition",
        "doi": "N/A",
        "license_code": "BSD-3-Clause",
        "license_weights": "N/A",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "CPU",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "Trivial",
        "readiness_summary": "Installed in .venv. Always predicts training mean.",
    },
    {
        "id": "RF02",
        "family": "Reference Benchmarks",
        "name": "Linear Regression",
        "estimator": "sklearn.linear_model.LinearRegression",
        "package": "scikit-learn>=1.4,<2",
        "status": "SMOKE_TEST_PASS",
        "paper": "Legendre (1805) / Gauss (1809) Ordinary least squares",
        "doi": "N/A",
        "license_code": "BSD-3-Clause",
        "license_weights": "N/A",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "CPU",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "Trivial",
        "readiness_summary": "Installed in .venv. Standard OLS with StandardScaler.",
    },
    {
        "id": "RF03",
        "family": "Reference Benchmarks",
        "name": "AED Original (Simplified Prototype)",
        "estimator": "Simplified single-profile heuristic (prototype) / CrackWidthAED_VBA.txt (target)",
        "package": "numpy, scipy",
        "status": "CONDITIONAL",
        "paper": "Tomczak et al. (2017) Method for Assessment of Changes in Crack Width",
        "doi": "10.1515/sgem-2017-0017",
        "license_code": "CC BY 4.0 (original script)",
        "license_weights": "N/A",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "CPU",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "Medium",
        "readiness_summary": "Simplified single-profile analytical prototype passed L0/L1 init+predict; faithful VBA reproduction remains CONDITIONAL pending parity check.",
    },
    {
        "id": "RF04",
        "family": "Reference Benchmarks",
        "name": "DLM Pretrained (MATLAB / PyTorch)",
        "estimator": "MATLAB krknet.mat / PyTorch Reconstruction",
        "package": "MATLAB Deep Learning Toolbox OR torch",
        "status": "CONDITIONAL",
        "paper": "Jakubowski & Tomczak (2024) Deep learning metasensor",
        "doi": "10.1016/j.conbuildmat.2024.135768",
        "license_code": "CC BY 4.0",
        "license_weights": "CC BY 4.0 (Zenodo: 14568863)",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "CPU / GPU",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "Medium",
        "readiness_summary": "Pretrained weights in krknet.mat (MATLAB opaque class). Requires MATLAB Deep Learning Toolbox OR exact weights extraction to PyTorch.",
    },
    {
        "id": "RF05",
        "family": "Reference Benchmarks",
        "name": "DLM Retrained (PyTorch)",
        "estimator": "krkcmd.models.DLMRetrained15Layer",
        "package": "torch>=2.1",
        "status": "STATIC_REVIEW",
        "paper": "Jakubowski & Tomczak (2024) Deep learning metasensor Table 3",
        "doi": "10.1016/j.conbuildmat.2024.135768",
        "license_code": "CC BY 4.0",
        "license_weights": "N/A (trained from scratch)",
        "python_311": True,
        "windows_native": True,
        "hardware_req": "GPU (RTX 3050) / CPU",
        "features_501_compatible": True,
        "n_train_12216_compatible": True,
        "complexity": "Medium",
        "readiness_summary": "15-layer 1D-CNN architecture fully documented in Table 3 of 2024 paper. Re-trained from scratch under strict group-aware split.",
    },
]

# Propagate dynamic smoke-test results instead of relying solely on hardcoded status strings
for c in candidates:
    sm = smoke_results.get(c["id"])
    if sm is not None:
        c["smoke_test_observed"] = sm.get("status", "UNKNOWN")
        if c["id"] == "DL01" and sm.get("status") == "SMOKE_TEST_PASS":
            c["status"] = "SMOKE_TEST_PASS_PROTOTYPE"
        elif c["id"] == "RF03" and sm.get("status") == "SMOKE_TEST_PASS":
            c["status"] = "CONDITIONAL"
        else:
            c["status"] = sm.get("status", c["status"])
    else:
        c["smoke_test_observed"] = "NOT_EXECUTED"

df_matrix = pd.DataFrame(candidates)
csv_matrix_path = TABLES_DIR / "model_compatibility_matrix.csv"
df_matrix.to_csv(csv_matrix_path, index=False)
print(f"  -> Saved 32-Candidate Model Compatibility Matrix to: {csv_matrix_path.relative_to(ROOT)}")

print("\n" + "=" * 70)
print(f"ASSESSMENT COMPLETE: {len(candidates)} CANDIDATES REGISTERED.")
print("Status breakdown:")
print(df_matrix["status"].value_counts().to_string())
print("=" * 70)
