# darksun-p2fe

Pathfinder 2E Foundry VTT compendia that implement the Dark Sun universe.

## Getting Started

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Pipeline

1. **Extract source PDF**
   ```bash
   python scripts/extract_pdf.py
   ```

2. **Transform into PF2E datasets**
   ```bash
   python scripts/transform_data.py
   ```

3. **Build Foundry compendia**
   ```bash
   python scripts/build_compendia.py
   ```

4. **Run validation**
   ```bash
   python scripts/validate_data.py
   ```

See `docs/pipeline_overview.md` for full details, mapping guidelines, and QA steps.
