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
        transformer_key = profile["transformer"]
        transformer = REGISTRY.get(transformer_key)
        if transformer is None:
            raise KeyError(f"Unknown transformer '{transformer_key}'")

        mapping_path = profile.get("mapping")
        mapping_data: Dict | None = None
        if mapping_path:
            mapping_path = Path(mapping_path)
            if not mapping_path.is_absolute():
                mapping_path = section_profiles.parent / mapping_path
            mapping_data = _load_json(mapping_path)

        base_target_dir = output_dir
        if subdir := profile.get("output_dir"):
            base_target_dir = output_dir / subdir
            base_target_dir.mkdir(parents=True, exist_ok=True)

        skip_slugs = set(profile.get("skip_slugs", []))
        additional_config = profile.get("config", {})

        def process_section(section_data: dict, *, explicit_slug: str | None = None) -> None:
            slug_value = explicit_slug or section_data.get("slug")
            if not slug_value:
                raise ValueError("Section data missing slug")
            if slug_value in skip_slugs:
                return

            config = {}
            if mapping_data:
                config.update(mapping_data)
            if additional_config:
                config.update(additional_config)

            transformed = transformer(section_data, config)

            if template := profile.get("output_template"):
                output_name = template.format(slug=slug_value)
            elif "output" in profile and explicit_slug is not None:
                output_name = profile["output"]
            else:
                output_name = f"{slug_value}.json"

            target_dir = base_target_dir
            target_dir.mkdir(parents=True, exist_ok=True)
            output_path = target_dir / output_name
            payload = {
                "slug": slug_value,
                "transformer": transformer_key,
                "source_section": section_data.get("title"),
                "data": transformed,
            }
            output_path.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            written.append(output_path)

        if "slug" in profile:
            slug = profile["slug"]
            raw_path = _find_section_file(raw_sections_dir, slug)
            section_data = _load_json(raw_path)
            process_section(section_data, explicit_slug=slug)
        elif "glob" in profile:
            pattern = profile["glob"]
            for raw_path in sorted(raw_sections_dir.glob(pattern)):
                section_data = _load_json(raw_path)
                process_section(section_data)
        else:
            raise ValueError("Profile must specify either 'slug' or 'glob'")

    return written

