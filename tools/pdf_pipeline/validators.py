"""Validation helpers for processed conversion datasets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List


class ValidationError(Exception):
    """Raised when a dataset fails validation rules."""


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_ancestries(processed_path: Path) -> List[str]:
    """Run sanity checks on the processed ancestry dataset."""

    data = _load_json(processed_path)
    entities = data.get("data", {}).get("entities", [])
    issues: List[str] = []

    if not entities:
        issues.append("no ancestry entities found")
        return issues

    for entity in entities:
        name = entity.get("name", "<unknown>")
        description = entity.get("description", "").strip()
        pf2e = entity.get("pf2e", {})

        if len(description) < 40:
            issues.append(f"{name}: description too short")
        boosts = pf2e.get("boosts", [])
        if not boosts or "free" not in boosts:
            issues.append(f"{name}: missing free ability boost")
        if pf2e.get("hit_points", 0) <= 0:
            issues.append(f"{name}: invalid hit point value")
        languages = pf2e.get("languages", [])
        if not languages:
            issues.append(f"{name}: no languages mapped")

    return issues
