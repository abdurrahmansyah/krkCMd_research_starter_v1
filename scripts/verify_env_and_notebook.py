"""
scripts/verify_env_and_notebook.py

Portable verification of Python environment, Jupyter kernelspec discovery,
interpreter argv validation, dependency integrity, static notebook cell
compilation (compile()), optional lightweight kernel runtime check, and
Git/data safety rules.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_MODULES = [
    ("numpy", "numpy"),
    ("pandas", "pandas"),
    ("scipy", "scipy"),
    ("sklearn", "scikit-learn"),
    ("matplotlib", "matplotlib"),
    ("seaborn", "seaborn"),
    ("ipykernel", "ipykernel"),
    ("yaml", "pyyaml"),
    ("joblib", "joblib"),
    ("openpyxl", "openpyxl"),
    ("pypdf", "pypdf"),
]


def _safe_resolve(path_str: str) -> Optional[Path]:
    if not path_str:
        return None
    try:
        return Path(path_str).expanduser().resolve()
    except OSError:
        return None


def inspect_kernelspecs(
    specs: Dict[str, Any],
    requested_kernel: Optional[str] = None,
    expected_python: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Validate Jupyter kernelspecs without hardcoding workstation/user paths
    or a single kernel name.

    Returns a structured dict with:
      - status: "PASS" | "FAIL"
      - selected_kernel: Optional[str]
      - discovered_kernels: list of per-kernel inspection dicts
      - failures: list of actionable error strings
      - warnings: list of warning strings
    """
    exp_py = (expected_python or Path(sys.executable)).resolve()
    discovered: List[Dict[str, Any]] = []
    failures: List[str] = []
    warnings: List[str] = []

    for name, entry in sorted(specs.items()):
        spec = entry.get("spec", {}) if isinstance(entry, dict) else {}
        argv = spec.get("argv") or []
        argv0 = str(argv[0]) if argv else ""
        argv0_path = Path(argv0) if argv0 else None
        exists_on_disk = bool(argv0_path and argv0_path.exists())
        resolved_argv0 = _safe_resolve(argv0) if exists_on_disk else None
        matches_expected = bool(resolved_argv0 and resolved_argv0 == exp_py)
        is_stale = bool(argv0) and not exists_on_disk

        discovered.append({
            "name": name,
            "display_name": spec.get("display_name", ""),
            "resource_dir": entry.get("resource_dir", "") if isinstance(entry, dict) else "",
            "argv0": argv0,
            "interpreter_exists": exists_on_disk,
            "stale_interpreter": is_stale,
            "matches_expected_python": matches_expected,
        })
        if is_stale and name.startswith("krkcmd"):
            warnings.append(
                f"Project kernel '{name}' has a stale/missing interpreter path: '{argv0}'."
            )

    selected_kernel: Optional[str] = None

    if requested_kernel:
        match = next((k for k in discovered if k["name"] == requested_kernel), None)
        if match is None:
            avail = [k["name"] for k in discovered]
            failures.append(
                f"Requested kernel '{requested_kernel}' is not registered. "
                f"Discovered kernels: {avail}. Register it with: "
                f"\"{exp_py}\" -m ipykernel install --user --name {requested_kernel} "
                f"--display-name \"Python ({requested_kernel})\""
            )
        else:
            selected_kernel = match["name"]
            if match["stale_interpreter"]:
                failures.append(
                    f"Kernel '{requested_kernel}' points to a missing/stale interpreter: '{match['argv0']}'."
                )
            elif not match["matches_expected_python"]:
                failures.append(
                    f"Kernel '{requested_kernel}' points to '{match['argv0']}', "
                    f"which does not match expected Python '{exp_py}'."
                )
    else:
        # Portable auto-discovery: prefer krkcmd* kernels matching expected Python, then any matching kernel
        matching = [k for k in discovered if k["matches_expected_python"] and not k["stale_interpreter"]]
        krk_matching = [k for k in matching if k["name"].startswith("krkcmd")]
        if krk_matching:
            selected_kernel = krk_matching[0]["name"]
        elif matching:
            selected_kernel = matching[0]["name"]
        else:
            avail = [f"{k['name']} -> {k['argv0']} (exists={k['interpreter_exists']})" for k in discovered]
            failures.append(
                f"No registered Jupyter kernel points to expected Python '{exp_py}'. "
                f"Discovered kernels: {avail}. Register one with: "
                f"\"{exp_py}\" -m ipykernel install --user --name krkcmd-research-newpc "
                f"--display-name \"Python (krkCMd Research)\""
            )

    return {
        "status": "PASS" if not failures else "FAIL",
        "expected_python": str(exp_py),
        "requested_kernel": requested_kernel,
        "selected_kernel": selected_kernel,
        "discovered_kernels": discovered,
        "warnings": warnings,
        "failures": failures,
    }


def run_lightweight_kernel_smoke(kernel_name: str, timeout_sec: int = 45) -> Dict[str, Any]:
    """Execute a tiny synthetic 1-cell notebook on the target kernel (no research training)."""
    try:
        import nbformat
        from nbclient import NotebookClient
    except ImportError as exc:
        return {"status": "FAIL", "error": f"nbformat/nbclient not available: {exc}"}

    nb = nbformat.v4.new_notebook(
        cells=[
            nbformat.v4.new_code_cell(
                "import sys, numpy, pandas, sklearn\n"
                "print('KERNEL_SMOKE_OK', sys.executable, sys.version.split()[0], "
                "numpy.__version__, pandas.__version__, sklearn.__version__)"
            )
        ]
    )
    try:
        client = NotebookClient(nb, kernel_name=kernel_name, timeout=timeout_sec)
        client.execute()
        outputs = []
        for out in nb.cells[0].get("outputs", []):
            if out.get("output_type") == "stream":
                outputs.append(out.get("text", "").strip())
        return {"status": "PASS", "kernel_name": kernel_name, "output": "\n".join(outputs)}
    except Exception as exc:
        return {"status": "FAIL", "kernel_name": kernel_name, "error": str(exc)}


def verify_notebook_static(nb_path: Path) -> Dict[str, Any]:
    """Statically compile all code cells in the notebook without executing them."""
    if not nb_path.exists():
        return {"status": "FAIL", "failures": [f"Notebook file not found at {nb_path}"]}

    failures: List[str] = []
    with nb_path.open("r", encoding="utf-8") as f:
        nb = json.load(f)

    cells = nb.get("cells", [])
    code_cells = [c for c in cells if c.get("cell_type") == "code"]
    compile_errors: List[str] = []
    for idx, cell in enumerate(code_cells):
        source = "".join(cell.get("source", []))
        try:
            compile(source, filename=f"notebook_cell_{idx}", mode="exec")
        except SyntaxError as exc:
            compile_errors.append(f"Cell {idx} SyntaxError: {exc}")

    failures.extend(compile_errors)
    all_code = "\n".join("".join(c.get("source", [])) for c in code_cells)
    has_gridline = "Gridline" in all_code
    has_stale_grid = '["Series", "Image", "Grid"]' in all_code or "['Series', 'Image', 'Grid']" in all_code
    if not has_gridline:
        failures.append("Notebook code does not reference 'Gridline' column!")
    if has_stale_grid:
        failures.append("Notebook code still contains outdated group key ['Series', 'Image', 'Grid']!")

    return {
        "status": "PASS" if not failures else "FAIL",
        "notebook_path": str(nb_path),
        "total_cells": len(cells),
        "code_cells": len(code_cells),
        "compiled_cleanly": len(code_cells) - len(compile_errors),
        "has_gridline": has_gridline,
        "has_stale_grid": has_stale_grid,
        "failures": failures,
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Portable environment, kernel, and notebook verifier.")
    parser.add_argument("--kernel", "--kernel-name", dest="kernel_name", default=None, help="Explicit Jupyter kernel name to verify (auto-discovers matching kernel if omitted).")
    parser.add_argument("--expected-python", default=None, help="Expected Python executable path (defaults to sys.executable).")
    parser.add_argument("--notebook", default=str(ROOT / "notebooks" / "00_baseline_krkCMd.ipynb"), help="Path to baseline notebook for static compile check.")
    parser.add_argument("--verify-kernel-runtime", action="store_true", help="Run a lightweight 1-cell synthetic smoke test on the selected kernel.")
    parser.add_argument("--json-out", default=None, help="Optional path to write structured JSON verification report.")
    args = parser.parse_args(argv)

    failures: List[str] = []
    report: Dict[str, Any] = {
        "python": {"executable": sys.executable, "version": sys.version.split()[0]},
        "imports": {},
        "pip_check": {},
        "kernels": {},
        "kernel_runtime_smoke": None,
        "notebook_static": {},
        "gitignore": {},
    }

    print("=" * 65)
    print("PORTABLE REPOSITORY, ENVIRONMENT & NOTEBOOK VERIFIER")
    print("=" * 65)

    # 1. Python version check
    print(f"\n--- 1. PYTHON EXECUTABLE ---\nExecutable: {sys.executable}\nVersion: {sys.version.split()[0]}")
    if sys.version_info < (3, 11) or sys.version_info >= (3, 12):
        failures.append(f"Python version expected 3.11.x, but running on {sys.version.split()[0]}")
    else:
        print("Python 3.11 check: PASS")

    # 2. Imports & pip check
    print("\n--- 2. DEPENDENCY & IMPORT INTEGRITY ---")
    for mod_name, pkg_name in REQUIRED_MODULES:
        try:
            __import__(mod_name)
            report["imports"][pkg_name] = "OK"
            print(f"Module '{mod_name}' ({pkg_name}): OK")
        except ImportError as exc:
            report["imports"][pkg_name] = f"FAIL: {exc}"
            failures.append(f"Missing required module: {pkg_name} ({exc})")

    pip_res = subprocess.run([sys.executable, "-m", "pip", "check"], capture_output=True, text=True)
    report["pip_check"] = {"returncode": pip_res.returncode, "output": (pip_res.stdout or pip_res.stderr).strip()}
    if pip_res.returncode != 0:
        failures.append(f"pip check reported broken dependencies:\n{pip_res.stdout or pip_res.stderr}")
        print("pip check: FAIL")
    else:
        print("pip check: PASS (No broken requirements found)")

    # 3. Jupyter kernelspec discovery & verification
    print("\n--- 3. JUPYTER KERNELSPEC DISCOVERY & ARGV VERIFICATION ---")
    kernel_res = subprocess.run([sys.executable, "-m", "jupyter", "kernelspec", "list", "--json"], capture_output=True, text=True)
    if kernel_res.returncode != 0:
        failures.append(f"jupyter kernelspec list command failed: {kernel_res.stderr}")
        report["kernels"] = {"status": "FAIL", "error": kernel_res.stderr}
    else:
        specs = json.loads(kernel_res.stdout).get("kernelspecs", {})
        exp_py = Path(args.expected_python) if args.expected_python else Path(sys.executable)
        k_report = inspect_kernelspecs(specs, requested_kernel=args.kernel_name, expected_python=exp_py)
        report["kernels"] = k_report
        print(f"Discovered kernels: {[k['name'] for k in k_report['discovered_kernels']]}")
        print(f"Selected kernel: {k_report['selected_kernel']}")
        for w in k_report["warnings"]:
            print(f"[WARN] {w}")
        failures.extend(k_report["failures"])

        if args.verify_kernel_runtime and k_report["selected_kernel"] and not k_report["failures"]:
            print(f"Running lightweight runtime smoke on kernel '{k_report['selected_kernel']}'...")
            smoke = run_lightweight_kernel_smoke(k_report["selected_kernel"])
            report["kernel_runtime_smoke"] = smoke
            print(f"Kernel runtime smoke: {smoke['status']} | {smoke.get('output') or smoke.get('error')}")
            if smoke["status"] != "PASS":
                failures.append(f"Kernel runtime smoke failed: {smoke.get('error')}")

    # 4. Static notebook compilation
    print("\n--- 4. NOTEBOOK STATIC COMPILATION ---")
    nb_rep = verify_notebook_static(Path(args.notebook))
    report["notebook_static"] = nb_rep
    if nb_rep["status"] == "PASS":
        print(f"Code cell compilation: PASS ({nb_rep['compiled_cleanly']}/{nb_rep['code_cells']} cells compiled cleanly)")
    else:
        failures.extend(nb_rep["failures"])

    # 5. .gitignore safety check
    print("\n--- 5. DATA & PAPERS REPOSITORY SAFETY ---")
    gi_path = ROOT / ".gitignore"
    if gi_path.exists():
        gi = gi_path.read_text(encoding="utf-8")
        has_papers = "papers/*.pdf" in gi
        has_raw = "data/raw/*" in gi
        report["gitignore"] = {"exists": True, "papers_pdf_rule": has_papers, "data_raw_rule": has_raw}
        if not has_papers:
            failures.append(".gitignore is missing rule 'papers/*.pdf'!")
        if not has_raw:
            failures.append(".gitignore is missing rule 'data/raw/*'!")
        print(f".gitignore rules: papers/*.pdf={has_papers}, data/raw/*={has_raw}")
    else:
        report["gitignore"] = {"exists": False}
        failures.append(".gitignore file does not exist!")

    report["overall_status"] = "PASS" if not failures else "FAIL"
    report["failures"] = failures

    if args.json_out:
        out_p = Path(args.json_out)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nSaved structured verification report to: {out_p}")

    print("\n" + "=" * 65)
    if failures:
        print(f"VERIFICATION RESULT: FAILED ({len(failures)} issue(s) detected)")
        for i, f in enumerate(failures, 1):
            print(f"{i}. [FAIL] {f}")
        print("=" * 65)
        return 1

    print("VERIFICATION RESULT: ALL CHECKS PASSED SUCCESSFULLY (No model training performed)")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
