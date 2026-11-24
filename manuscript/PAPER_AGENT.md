# PAPER_AGENT.md | krkCMd living manuscript
Version 0.1 | Status: exploratory draft, not submission-ready

## Scope and authority
Manage only manuscript, figures, references and evidence mappings. Read root AGENT.md, docs/DECISIONS.md, docs/EXPERIMENT_LOG.md, current configs, notebook and run outputs first. Root AGENT.md and approved decisions govern experimental protocol. Never silently change experiments, hyperparameters, dataset or split. Obtain user approval for any protocol change. No training unless explicitly authorized. Do not overwrite historical outputs.

## Files and placement
Place this file and both DOCX drafts in `manuscript/`; figures and editable DOT sources in `manuscript/figures/`; reference register in `references/`. Preserve root AGENT.md; add a reference to this file only with approval. Create `manuscript/CHANGELOG.md` and `manuscript/EVIDENCE_MAP.md` when first updating. Keep English and Indonesian texts synchronized by identical section numbering and shared evidence IDs. Do not publish copyrighted PDFs or raw data; check tracked files and license separately.

## Evidence gate
1. Read exact current commit and record git SHA, notebook path, execution status, Python/library versions, CSV hash, run ID, seeds and configuration. Inspect HTML and matching CSV/JSON outputs. Do not infer outputs from filename, code, old reports or expected counts.
2. Verify `group_split_manifest.csv`: each source_row_id unique, exactly one partition per group, all expected rows covered, all pairwise group intersections empty, and stage coverage per group when joined to CSV. Check Series/Image/Gridline semantics against data descriptor. Never equate zero group overlap with complete absence of leakage.
3. Verify benchmark tables, prediction records, sample alignment, selection by validation MAE, and metrics recomputed from saved predictions. Existing DLM/AED predictions are not retrained. Check original training provenance; note comparability limitations.
4. Verify robustness table and clean reference from the same refitted model. Do not compare perturbed metrics directly against a different training configuration. Record perturbations, seeds, clipping, sample counts. A single selected model is not a multi-model robustness comparison.
5. Per-series errors are screening only. Cross-series drift/adaptation requires a separate approved protocol and fixed disjoint target test. RF retraining is not neural fine-tuning. Never infer drift from unequal MAE alone.

## Manuscript updates
- Normal text: supported narrative. Amber `[VERIFY / UPDATE]` / `[VERIFIKASI / REVISI]`: evidence or wording pending. Red `[RESULT REQUIRED]` / `[BUTUH HASIL]`: result pending. `TBD` is not zero. No lorem ipsum or invented results.
- Update Methods first, then Results, Discussion, Conclusion, Abstract last. Maintain IMRAD; keep figures numbered, tables editable, symbols/units consistent (µm). Prefer direct source citations and measured data to generic claims. Include limitations and declaration fields. Do not claim novelty without screening current literature.
- For every factual claim or numeric table/figure, log evidence ID, path, run ID, source hash, row/column or DOI, manuscript section, status. Mark conceptual/synthetic diagrams as illustrative. Use matching figure labels and result numbers in both languages.
- Maintain versioned copies e.g. `krkCMd_paper_en_v0.2.docx`; never replace the last accepted version silently. Changelog: date, sections changed, evidence, pending items, author/agent, approval if needed.
- Format via python-docx or Word; render both files to PDF/PNG and visually inspect all pages (clipping, tables, fonts, figures, page breaks). Update citations and cross-references, verify language consistency. Remove draft markers only when evidence is confirmed. Adapt to journal template after user selects venue.

## Literature register
`REFERENCE_REGISTER.md` is a candidate queue, not a final bibliography. For each entry verify title, authors, year, venue, DOI/URL, publication type, relevance, access, and whether full text read. Deduplicate by DOI/title. Use backward and forward snowballing from 2024 DLM and 2025 krkCMd; check new krkCMd users. Record claim-to-source mapping and page/table. Do not cite a paper solely to meet a numerical quota. No fabricated DOI, results, author, or quotation. Report verified count separately from candidate count. Only cited and reviewed items enter the final bibliography.

## Self-extension
Propose any new rule in `docs/AGENT_CHANGE_PROPOSALS.md` with evidence, rationale, affected files, impact and acceptance test. Await explicit approval for protocol/governance changes. Then update this file, root decision log if needed, and changelog. Preserve previous decisions. No autonomous changes to the approved methodology.

## Report after each run
Report what was read, exact evidence, actual results, changes to EN/ID, unresolved markers, source count, visual QA, and next approved decision. Stop before any new training or experimental expansion unless the user has authorized it.
