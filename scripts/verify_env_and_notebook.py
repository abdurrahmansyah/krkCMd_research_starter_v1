"""
scripts/verify_env_and_notebook.py

Comprehensive verification of Python environment, Jupyter kernelspec,
dependency integrity, and notebook code cell compilation (using compile()).
Produces explicit exit code 0 on success, or exit code 1 with actionable failure messages.
"""

import sys
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
failures = []

print("=" * 65)
print("REPOSITORY, ENVIRONMENT & NOTEBOOK CONSISTENCY VERIFIER")
print("=" * 65)

# 1. Python Executable Check
print("\n--- 1. PYTHON EXECUTABLE ---")
print(f"Executable: {sys.executable}")
print(f"Version: {sys.version.split()[0]}")
if sys.version_info < (3, 11) or sys.version_info >= (3, 12):
    failures.append(f"Python version expected 3.11.x, but running on {sys.version.split()[0]}")
else:
    print("Python 3.11 check: PASS")

# 2. Dependency Check (Imports & Pip Check)
print("\n--- 2. DEPENDENCY & IMPORT INTEGRITY ---")
required_modules = [
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

for mod_name, pkg_name in required_modules:
    try:
        __import__(mod_name)
        print(f"Module '{mod_name}' ({pkg_name}): OK")
    except ImportError as e:
        failures.append(f"Missing required module: {pkg_name} ({e})")
        print(f"Module '{mod_name}' ({pkg_name}): FAIL")

# Run pip check
pip_res = subprocess.run([sys.executable, "-m", "pip", "check"], capture_output=True, text=True)
if pip_res.returncode != 0:
    failures.append(f"pip check reported broken dependencies:\n{pip_res.stdout or pip_res.stderr}")
    print("pip check: FAIL")
else:
    print("pip check: PASS (No broken requirements found)")

# 3. Jupyter Kernelspec Check
print("\n--- 3. JUPYTER KERNELSPEC REGISTRATION ---")
kernel_res = subprocess.run([sys.executable, "-m", "jupyter", "kernelspec", "list", "--json"], capture_output=True, text=True)
if kernel_res.returncode != 0:
    failures.append(f"jupyter kernelspec list command failed: {kernel_res.stderr}")
    print("kernelspec command: FAIL")
else:
    try:
        specs = json.loads(kernel_res.stdout).get("kernelspecs", {})
        registered_kernels = list(specs.keys())
        print(f"Registered kernels: {registered_kernels}")
        if "krkcmd-research" not in specs:
            failures.append("Kernel 'krkcmd-research' is NOT registered in jupyter kernelspec!")
            print("krkcmd-research registration: FAIL")
        else:
            k_spec = specs["krkcmd-research"]["spec"]
            print(f"krkcmd-research display name: '{k_spec.get('display_name')}'")
            print(f"krkcmd-research executable: '{k_spec.get('argv', [''])[0]}'")
            print("krkcmd-research registration: PASS")
    except Exception as e:
        failures.append(f"Failed to parse kernelspec output: {e}")
        print("kernelspec parse: FAIL")

# 4. Notebook Readability & Code Cell Compilation (using compile())
print("\n--- 4. NOTEBOOK CODE CELL COMPILATION (STATIC SYNTAX CHECK) ---")
print("[INFO] Static verification using compile(). Does NOT execute cells or train models at runtime.")

nb_path = ROOT / "notebooks" / "00_baseline_krkCMd.ipynb"
if not nb_path.exists():
    failures.append(f"Notebook file not found at {nb_path}")
    print("Notebook presence: FAIL")
else:
    try:
        with open(nb_path, "r", encoding="utf-8") as f:
            nb = json.load(f)

        code_cells = [c for c in nb.get("cells", []) if c.get("cell_type") == "code"]
        print(f"Found {len(nb.get('cells', []))} total cells ({len(code_cells)} code cells).")

        compile_errors = []
        for idx, cell in enumerate(code_cells):
            source = "".join(cell.get("source", []))
            try:
                # Compile statically in 'exec' mode
                compile(source, filename=f"notebook_cell_{idx}", mode="exec")
            except SyntaxError as e:
                compile_errors.append(f"Cell {idx} SyntaxError: {e}")

        if compile_errors:
            failures.extend(compile_errors)
            print(f"Code cell compilation: FAIL ({len(compile_errors)} errors)")
            for err in compile_errors:
                print(f"  {err}")
        else:
            print(f"Code cell compilation: PASS ({len(code_cells)}/{len(code_cells)} cells compiled cleanly)")

        # Verify schema keywords inside notebook cells
        all_code = "\n".join("".join(c.get("source", [])) for c in code_cells)
        if "Gridline" not in all_code:
            failures.append("Notebook code does not reference 'Gridline' column!")
        if '["Series", "Image", "Grid"]' in all_code or "['Series', 'Image', 'Grid']" in all_code:
            failures.append("Notebook code still contains outdated candidate group key ['Series', 'Image', 'Grid']!")

    except Exception as e:
        failures.append(f"Failed to read or parse notebook JSON: {e}")
        print("Notebook parsing: FAIL")

# 5. Git & Data Safety Check
print("\n--- 5. DATA & PAPERS REPOSITORY SAFETY ---")
gitignore_path = ROOT / ".gitignore"
if gitignore_path.exists():
    gi_content = gitignore_path.read_text(encoding="utf-8")
    if "papers/*.pdf" in gi_content:
        print(".gitignore contains papers/*.pdf: PASS")
    else:
        failures.append(".gitignore is missing rule 'papers/*.pdf'!")
    if "data/raw/*" in gi_content:
        print(".gitignore contains data/raw/*: PASS")
    else:
        failures.append(".gitignore is missing rule 'data/raw/*'!")
else:
    failures.append(".gitignore file does not exist!")

# Summary
print("\n" + "=" * 65)
if failures:
    print(f"VERIFICATION RESULT: FAILED ({len(failures)} issue(s) detected)")
    print("=" * 65)
    for i, f in enumerate(failures, 1):
        print(f"{i}. [FAIL] {f}")
    sys.exit(1)
else:
    print("VERIFICATION RESULT: ALL CHECKS PASSED SUCCESSFULLY")
    print("No model training was performed.")
    print("=" * 65)
    sys.exit(0)
