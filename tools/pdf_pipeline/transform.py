"""High-level transformation pipeline orchestrating raw-to-processed data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .transformers import REGISTRY


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _find_section_file(raw_dir: Path, slug: str) -> Path:
    matches = sorted(raw_dir.glob(f"*-{slug}.json"))
    if not matches:
        raise FileNotFoundError(f"No raw section file found for slug '{slug}' in {raw_dir}")
    return matches[0]


def transform_all(
    *,
    section_profiles: Path,
    raw_sections_dir: Path,
    output_dir: Path,
) -> List[Path]:
    profiles_data = _load_json(section_profiles)
    output_dir.mkdir(parents=True, exist_ok=True)

    written: List[Path] = []

    for profile in profiles_data:
        slug = profile["slug"]
        transformer_key = profile["transformer"]
        transformer = REGISTRY.get(transformer_key)
        if transformer is None:
            raise KeyError(f"Unknown transformer '{transformer_key}' for slug '{slug}'")

        raw_path = _find_section_file(raw_sections_dir, slug)
        section_data = _load_json(raw_path)

        mapping_path = profile.get("mapping")
        mapping_data: Dict | None = None
        if mapping_path:
            mapping_path = Path(mapping_path)
            if not mapping_path.is_absolute():
                mapping_path = section_profiles.parent / mapping_path
            mapping_data = _load_json(mapping_path)

        transformed = transformer(section_data, mapping_data or {})

        output_name = profile.get("output", f"{slug}.json")
        output_path = output_dir / output_name
        payload = {
            "slug": slug,
            "transformer": transformer_key,
            "source_section": section_data.get("title"),
            "data": transformed,
        }
        output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        written.append(output_path)

    return written

