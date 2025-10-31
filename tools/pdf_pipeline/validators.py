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


def validate_journals(processed_dir: Path) -> List[str]:
    """Ensure each processed journal entry has content and a title."""

    issues: List[str] = []
    if not processed_dir.exists():
        issues.append(f"journal directory missing: {processed_dir}")
        return issues

    files = sorted(processed_dir.glob("*.json"))
    if not files:
        issues.append("no journal entries generated")
        return issues

    for journal_file in files:
        payload = _load_json(journal_file)
        data = payload.get("data", {})
        title = data.get("title") or payload.get("slug") or journal_file.stem
        content = data.get("content", "").strip()

        if not title:
            issues.append(f"{journal_file.name}: missing title")
        if len(content) < 40:
            issues.append(f"{journal_file.name}: content too short")

    return issues
