import sys
import json
import ast
import subprocess
from pathlib import Path

print("=== 1. PYTHON EXECUTABLE ===")
print("Executable:", sys.executable)
print("Python Version:", sys.version)

print("\n=== 2. IPYKERNEL CHECK ===")
try:
    import ipykernel
    print("ipykernel version:", ipykernel.__version__)
    print("ipykernel installed: YES")
except ImportError as e:
    print("ipykernel installed: NO, error:", e)

print("\n=== 3. JUPYTER KERNELSPEC CHECK ===")
res = subprocess.run([sys.executable, "-m", "jupyter", "kernelspec", "list", "--json"], capture_output=True, text=True)
try:
    specs = json.loads(res.stdout)
    kernels = specs.get("kernelspecs", {})
    print("Registered kernels:", list(kernels.keys()))
    if "krkcmd-research" in kernels:
        print("krkcmd-research details:", json.dumps(kernels["krkcmd-research"], indent=2))
    else:
        print("krkcmd-research is NOT registered!")
except Exception as e:
    print("Failed to parse kernelspec:", e, res.stdout, res.stderr)

print("\n=== 4. NOTEBOOK READABILITY & CELL COMPILATION ===")
nb_path = Path("notebooks/00_baseline_krkCMd.ipynb")
print("Notebook exists:", nb_path.exists())
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

print("Total cells in notebook:", len(nb["cells"]))

code_cells = 0
compiled_cells = 0
syntax_errors = []

for idx, cell in enumerate(nb["cells"]):
    if cell.get("cell_type") == "code":
        code_cells += 1
        source = "".join(cell.get("source", []))
        try:
            ast.parse(source, filename=f"cell_{idx}")
            compiled_cells += 1
        except SyntaxError as e:
            syntax_errors.append((idx, str(e)))

print(f"Total code cells: {code_cells}")
print(f"Successfully compiled code cells: {compiled_cells}/{code_cells}")
if syntax_errors:
    for idx, err in syntax_errors:
        print(f"Syntax error in cell {idx}: {err}")
else:
    print("All code cells parsed and compiled without syntax errors: PASS")

# Verify schema alignment in cell sources
all_code = "\n".join("".join(c.get("source", [])) for c in nb["cells"] if c.get("cell_type") == "code")
print("Uses Gridline in code:", "Gridline" in all_code)
print("Uses raw 'Grid' in metadata_candidates:", '"Grid"' in all_code)
print("Uses raw 'Grid' in group_cols:", '["Series", "Image", "Grid"]' in all_code)
