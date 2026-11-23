import json
import re
from pathlib import Path
import numpy as np
import pandas as pd
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "raw" / "krkCMd_table.csv"
REPORTS_DIR = ROOT / "reports"
TABLES_DIR = REPORTS_DIR / "tables"
FIGURES_DIR = REPORTS_DIR / "figures"
LOGS_DIR = REPORTS_DIR / "logs"

for d in [TABLES_DIR, FIGURES_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

print("--- 1. AUDITING CSV ---")
df = pd.read_csv(CSV_PATH, low_memory=False)
n_rows, n_cols = df.shape
print(f"Total Rows: {n_rows}")
print(f"Total Columns: {n_cols}")

cols = df.columns.tolist()
meta_cols = [c for c in cols if not re.match(r"^x\d+$", c) and c not in ["MANwidth", "DLMwidth", "AEDwidth"]]
feature_cols = [f"x{i}" for i in range(1, 502)]
target_col = "MANwidth"
baseline_cols = ["DLMwidth", "AEDwidth"]

print(f"Metadata columns detected: {meta_cols}")
print(f"Feature columns (x1..x501) count: {len([c for c in cols if c in feature_cols])}")
print(f"Target column exists: {target_col in cols}")
print(f"Baseline columns: {[c for c in baseline_cols if c in cols]}")

missing_per_col = df.isna().sum()
total_missing = int(missing_per_col.sum())
dup_rows = int(df.duplicated().sum())

print(f"Total missing values across table: {total_missing}")
print(f"Duplicate rows: {dup_rows}")

meta_summary = {}
for col in meta_cols:
    val_counts = df[col].value_counts(dropna=False).head(10).to_dict()
    meta_summary[col] = {
        "unique_count": int(df[col].nunique(dropna=False)),
        "null_count": int(df[col].isna().sum()),
        "top_values": {str(k): int(v) for k, v in val_counts.items()}
    }

# Check grouping: Series + Image + Gridline
group_cols = [c for c in ["Series", "Image", "Gridline"] if c in df.columns]
group_id = df[group_cols].astype(str).agg("_".join, axis=1)
n_groups = int(group_id.nunique())
group_sizes = group_id.value_counts()

# Cross-tabulate with Stage to see if groups repeat across stages
stages_per_group = df.groupby(group_id)["Stage"].nunique()
profiles_per_stage_group = df.groupby([group_id, "Stage"]).size()

group_audit = {
    "group_cols": group_cols,
    "n_unique_groups": n_groups,
    "group_size_min": int(group_sizes.min()),
    "group_size_max": int(group_sizes.max()),
    "group_size_mean": float(group_sizes.mean()),
    "group_size_median": float(group_sizes.median()),
    "stages_per_group_min": int(stages_per_group.min()),
    "stages_per_group_max": int(stages_per_group.max()),
    "stages_per_group_mean": float(stages_per_group.mean()),
    "profiles_per_stage_group_min": int(profiles_per_stage_group.min()),
    "profiles_per_stage_group_max": int(profiles_per_stage_group.max()),
}

# Target and baseline stats
target_stats = df[target_col].describe().to_dict()
baseline_stats = {col: df[col].describe().to_dict() for col in baseline_cols if col in df.columns}

# Features check
x_data = df[feature_cols]
x_min = float(x_data.min().min())
x_max = float(x_data.max().max())
x_nulls = int(x_data.isna().sum().sum())

audit_result = {
    "n_rows": n_rows,
    "n_cols": n_cols,
    "columns": cols[:10] + ["..."] + cols[-5:],
    "total_missing": total_missing,
    "duplicate_rows": dup_rows,
    "meta_summary": meta_summary,
    "group_audit": group_audit,
    "target_stats": target_stats,
    "baseline_stats": baseline_stats,
    "features_audit": {
        "expected_count": 501,
        "actual_count": len(feature_cols),
        "min_intensity": x_min,
        "max_intensity": x_max,
        "missing_values": x_nulls,
    }
}

with open(TABLES_DIR / "comprehensive_audit.json", "w") as f:
    json.dump(audit_result, f, indent=2)

print("\n--- 2. EXTRACTING PAPER DEFINITIONS ---")
papers = list((ROOT / "papers").glob("*.pdf"))
print(f"Total papers in papers/: {len(papers)}")

paper_2024 = ROOT / "papers" / "2024 Deep learning metasensor for crack-width assessment and self-healing evaluation in concrete.pdf"
paper_2025 = ROOT / "papers" / "2025 Dataset for developing deep learning models to assess crack width and self-healing progress in concrete.pdf"

def extract_snippets(pdf_path, keywords):
    if not pdf_path.exists():
        return f"File not found: {pdf_path.name}"
    reader = PdfReader(str(pdf_path))
    snippets = []
    for page_idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        for kw in keywords:
            if re.search(rf"\b{kw}\b", text, re.IGNORECASE):
                for line in text.split("\n"):
                    if re.search(rf"\b{kw}\b", line, re.IGNORECASE):
                        snippets.append(f"[Page {page_idx+1}] {line.strip()}")
    return snippets[:15]

paper_notes = {
    "paper_2025_snippets": extract_snippets(paper_2025, ["Gridline", "Series", "Stage", "brightness profile", "resolution", "MANwidth"]),
    "paper_2024_snippets": extract_snippets(paper_2024, ["metasensor", "DLMwidth", "AEDwidth", "healing", "6400"])
}

with open(TABLES_DIR / "paper_snippets.json", "w") as f:
    json.dump(paper_notes, f, indent=2)

print("Audit script completed successfully.")
