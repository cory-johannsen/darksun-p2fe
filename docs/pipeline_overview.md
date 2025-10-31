# Dark Sun Conversion Pipeline

This repository now contains an end-to-end pipeline that ingests the original Dark Sun boxed set PDF and emits Foundry VTT-ready Pathfinder 2E compendia.

## Directory Layout
- `tools/pdf_pipeline/` – Python helpers for manifest generation, extraction, transformation, validation, and compendium build steps.
- `data/raw/` – Machine-extracted text blocks and section manifests straight from the PDF.
- `data/processed/` – Domain-normalised JSON used as a staging area for PF2E conversions.
- `data/mappings/` – Authoritative mapping metadata (e.g., ability adjustments, headings) that guides conversions.
- `packs/` – Generated Foundry compendium packs (`*.db`).

## Workflow
1. **Extract the PDF**
   ```bash
   source .venv/bin/activate
   python scripts/extract_pdf.py
   ```
   - Produces `data/raw/pdf_manifest.json` and one JSON file per chapter under `data/raw/sections/`.

2. **Transform to PF2E-friendly JSON**
   ```bash
   python scripts/transform_data.py
   ```
   - Applies mapping rules from `data/mappings/` and emits datasets into `data/processed/`.

3. **Build Foundry Compendia**
   ```bash
   python scripts/build_compendia.py
   ```
   - Generates `packs/dark-sun-ancestries.db` (PF2E ancestry items) and `packs/dark-sun-rules.db` (journal entries that mirror the source text).

4. **Run QA Checks**
   ```bash
   python scripts/validate_data.py
   ```
   - Executes structural sanity checks on processed data (description length, boosts/flaws, languages, etc.).

## Extending the Pipeline
- Add new entries to `data/mappings/section_profiles.json` to register additional chapters (equipment, spells, monsters, lore, etc.).
- Provide transformer-specific mapping files (see `data/mappings/ancestries.json` for an example) and implement a transformer module under `tools/pdf_pipeline/transformers/`.
- Update `tools/pdf_pipeline/transformers/__init__.py` to expose the new transformer key.
- Extend `tools/pdf_pipeline/compendium.py` with builders for other PF2E entity types (items, spells, bestiary).

## Manual Review Guidelines
- Spot-check extracted `data/raw/sections/*.json` to ensure headings and tables have clean text (adjust `pdf_pipeline/manifest.py` if any sections are mis-segmented).
- Review `data/processed/*.json` for anomalies such as truncated descriptions, missing traits, or misaligned ability conversions.
- Import `packs/dark-sun-ancestries.db` into a Foundry sandbox world and verify:
  - Ability boosts/flaws, HP, size, speeds, and traits align with Dark Sun lore.
  - Descriptions render correctly and do not include table artefacts that should be templated elsewhere.
- Import `packs/dark-sun-rules.db` and review a sample of journal pages to confirm formatting and coverage match the source chapters.
- Re-run `scripts/validate_data.py`